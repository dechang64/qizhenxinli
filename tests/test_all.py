"""核心模块测试 — db, emotion_detector, fl_engine, minimax_chat, minimax_music"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import EMOTIONS, SCENES, RELEASE_METHODS
from core.emotion_detector import detect_emotion, detect_emotions_multi, compute_session_emotion_profile
from core.fl_engine import compute_entropy, compute_confidence, submit_local_stats, federated_aggregate
from core.characters import get_character, get_character_by_scene, get_all_characters, CHARACTERS
from core.db import init_db, create_post, get_posts, resonate_post, get_emotion_distribution, get_treehole_stats


def test_config():
    """配置常量完整性"""
    assert len(SCENES) == 9, f"Expected 9 scenes, got {len(SCENES)}"
    assert len(RELEASE_METHODS) == 5, f"Expected 5 release methods, got {len(RELEASE_METHODS)}"
    assert len(EMOTIONS) == 12, f"Expected 12 emotions, got {len(EMOTIONS)}"
    expected_scenes = ["潇湘馆","蘅芜苑","怡红院","稻香村","藕香榭","秋爽斋",
                       "栊翠庵","缀锦楼","紫菱洲"]
    assert all(s["name"] in expected_scenes for s in SCENES)
    print("  ✅ config: 9 scenes, 5 methods, 12 emotions")


def test_characters():
    """角色定义完整性"""
    assert len(CHARACTERS) == 9, f"Expected 9 characters, got {len(CHARACTERS)}"
    for name, char in CHARACTERS.items():
        assert "system_prompt" in char, f"{name} missing system_prompt"
        assert "greeting" in char, f"{name} missing greeting"
        assert "theory" in char, f"{name} missing theory"
        assert "scene" in char, f"{name} missing scene"
        assert len(char["system_prompt"]) > 100, f"{name} system_prompt too short"
        assert len(char["greeting"]) > 10, f"{name} greeting too short"
    # 测试查找
    daiyu = get_character("林黛玉")
    assert daiyu["scene"] == "潇湘馆"
    scene_char = get_character_by_scene("怡红院")
    assert scene_char["scene"] == "怡红院"
    # 新三院查找
    assert get_character("妙玉")["scene"] == "栊翠庵"
    assert get_character("惜春")["scene"] == "缀锦楼"
    assert get_character("迎春")["scene"] == "紫菱洲"
    all_chars = get_all_characters()
    assert len(all_chars) == 9
    print("  ✅ characters: 9 characters with complete definitions")


def test_emotion_detector():
    """情绪检测准确性"""
    # 单情绪
    assert detect_emotion("我今天好难过，想哭") == "悲伤"
    assert detect_emotion("考试要来了，我好焦虑") == "焦虑"
    assert detect_emotion("太生气了，凭什么这样对我") == "愤怒"
    assert detect_emotion("不知道未来在哪里，很迷茫") == "迷茫"
    assert detect_emotion("加班到凌晨，太累了") == "疲惫"
    assert detect_emotion("一个人在宿舍，好孤独") == "孤独"
    assert detect_emotion("还好吧，没什么特别的") == "平静"
    assert detect_emotion("感谢有你在我身边") == "感恩"
    assert detect_emotion("期待明天的到来") == "期待"
    # ── 新增三院情绪 ──
    assert detect_emotion("这件事我一直放不下，总是想起") == "执念"
    assert detect_emotion("我付出了那么多，却没人看见") == "委屈"
    assert detect_emotion("我什么都做不好，不如别人") == "自卑"

    # 多情绪
    multi = detect_emotions_multi("又难过又焦虑，不知道该怎么办")
    assert "悲伤" in multi or "焦虑" in multi or "迷茫" in multi

    # 空文本
    assert detect_emotion("") == "平静"
    assert detect_emotion("你好") == "平静"

    # 会话画像
    messages = [
        {"role": "user", "text": "我今天好难过"},
        {"role": "assistant", "text": "怎么了？"},
        {"role": "user", "text": "考试没考好，很焦虑"},
    ]
    profile = compute_session_emotion_profile(messages)
    assert isinstance(profile, dict)
    assert len(profile) > 0
    assert sum(profile.values()) > 0

    # ── track-2：否定词降权（"我想念" → 悲伤被否 → 平静）──
    # 注意"不知道"作为一个词，"不"不是真否定 → 仍判定为迷茫
    assert detect_emotion("我不知道未来在哪里") == "迷茫"

    print("  ✅ emotion_detector: all 12 emotions detected correctly")


def test_emotion_detector_negation():
    """track-2：否定词降权 — "不X" 应识别为非 X

    覆盖：
    1. 简单否定 "我不想念" → 平静（悲伤被否）
    2. 肯定 "我真的很难过" → 悲伤（保留）
    3. 再否定 "我不再焦虑了" → 平静（焦虑被否）
    4. 疲惫肯定/否定 "我累了" / "我不累" → 疲惫 / 平静
    5. 双否定 "不是不难过" → 悲伤（双否定=肯定）
    6. 跨子句 "我不再焦虑，也不想念" → 平静（两个情绪都被否）
    7. 部分否定 "我很难过，也想念他" → 悲伤（想念保持，没被否）
    8. "没哭" → 平静（悲伤被否）
    9. detect_emotions_multi 也应一致
    """
    # 1. 简单否定
    assert detect_emotion("我不想念他") == "平静", \
        "'我不想念' 应识别为平静（悲伤被否）"
    assert detect_emotion("我不想念") == "平静"

    # 2. 肯定保持
    assert detect_emotion("我真的很难过") == "悲伤", \
        "'我真的很难过' 应识别为悲伤（无否定）"

    # 3. "再" filler
    assert detect_emotion("我不再焦虑了") == "平静", \
        "'我不再焦虑了' 应识别为平静（焦虑被否）"

    # 4. 疲惫
    assert detect_emotion("我累了") == "疲惫"
    assert detect_emotion("我不累") == "平静", \
        "'我不累' 应识别为平静（疲惫被否）"

    # 5. 双否定
    assert detect_emotion("不是不难过") == "悲伤", \
        "'不是不难过' 双否定=肯定 → 悲伤"

    # 6. 跨子句
    assert detect_emotion("我不再焦虑，也不想念") == "平静", \
        "'我不再焦虑，也不想念' 两个情绪都被否 → 平静"

    # 7. 部分否定
    assert detect_emotion("我很难过，也想念他") == "悲伤", \
        "'我很难过，也想念他' 想念未被否 → 悲伤"

    # 8. "没"
    assert detect_emotion("我没哭") == "平静", \
        "'我没哭' 悲伤被否 → 平静"

    # 9. multi 版应一致
    multi = detect_emotions_multi("我不想念他")
    assert multi == {"平静": 1.0}, f"'我不想念' multi 应是 {{'平静': 1.0}}，得到 {multi}"
    multi2 = detect_emotions_multi("我不再焦虑，也不想念")
    assert multi2 == {"平静": 1.0}, f"两个情绪都被否 multi 应是 {{'平静': 1.0}}，得到 {multi2}"

    print("  ✅ emotion_detector negation: 否定词降权 + 双否定 + 跨子句 全过")


def test_fl_engine():
    """联邦学习引擎"""
    import core.db as db_module
    old_path = db_module.DB_PATH
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_module.DB_PATH = tmp.name

    try:
        db_module.init_db()

        # 熵计算
        uniform = {e: 1/9 for e in EMOTIONS}
        assert compute_entropy(uniform) > 0
        assert compute_confidence(uniform) < 0.1  # 均匀分布 → 低置信度

        concentrated = {"悲伤": 1.0}
        assert compute_entropy(concentrated) == 0
        assert compute_confidence(concentrated) == 1.0  # 集中 → 高置信度

        # 提交多个客户端统计
        submit_local_stats("s1", {"悲伤": 0.7, "焦虑": 0.3})
        submit_local_stats("s2", {"悲伤": 0.5, "焦虑": 0.5})
        submit_local_stats("s3", {"疲惫": 0.8, "焦虑": 0.2})

        # 联邦聚合
        result = federated_aggregate(min_clients=3)
        assert result is not None
        assert result["round"] == 1
        assert result["client_count"] == 3
        assert "悲伤" in result["aggregated"]
        assert "entropy_weights" in result
        # s1 更集中（2类 vs s2 的2类但更均匀），权重应更高
        weights = list(result["entropy_weights"].values())
        assert all(w > 0 for w in weights)

        print("  ✅ fl_engine: entropy, confidence, federation round all correct")
    finally:
        db_module.DB_PATH = old_path
        os.unlink(tmp.name)


def test_db():
    """数据库操作"""
    import core.db as db_module
    old_path = db_module.DB_PATH
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_module.DB_PATH = tmp.name

    try:
        init_db()

        # 创建帖子
        create_post("测试帖子1", "悲伤", "潇湘馆")
        create_post("测试帖子2", "焦虑", "怡红院")
        create_post("测试帖子3", "平静", "")

        # 查询帖子
        posts = get_posts(limit=10)
        assert len(posts) == 3
        assert posts[0]["content"] == "测试帖子3"  # 最新的在前

        # 共鸣
        resonate_post(posts[0]["id"])
        updated = get_posts(limit=1)
        assert updated[0]["resonates"] == 1

        # 情绪分布
        dist = get_emotion_distribution()
        assert dist["悲伤"] == 1
        assert dist["焦虑"] == 1
        assert dist["平静"] == 1

        # 树洞统计
        from core.db import record_treehole
        record_treehole("wind", "悲伤")
        record_treehole("lake", "焦虑")
        th_stats = get_treehole_stats()
        assert "wind" in th_stats
        assert "lake" in th_stats

        print("  ✅ db: CRUD, resonance, stats all correct")
    finally:
        db_module.DB_PATH = old_path
        os.unlink(tmp.name)


def test_minimax_chat_mock():
    """GLM 聊天 Mock 模式"""
    import core.minimax_chat as chat_module
    old_mock = chat_module.MOCK_MODE
    chat_module.MOCK_MODE = True

    try:
        messages = [{"role": "user", "content": "我今天好难过"}]
        response = chat_module.chat(messages, character="林黛玉")
        assert isinstance(response, str)
        assert len(response) > 10

        # 不同情绪
        response_angry = chat_module.chat(
            [{"role": "user", "content": "太生气了"}], character="贾宝玉"
        )
        assert isinstance(response_angry, str)

        print("  ✅ minimax_chat: mock mode returns valid responses")
    finally:
        chat_module.MOCK_MODE = old_mock


def test_minimax_music_mock():
    """MiniMax 音乐 Mock 模式（无 MINIMAX_API_KEY）"""
    import core.minimax_music as music_module
    assert music_module.MUSIC_AVAILABLE == False  # 测试环境无 Key
    result = music_module.generate_music("宁静", "潇湘馆", "宁静")
    assert result is None

    print("  ✅ minimax_music: no key → returns None (expected)")


if __name__ == "__main__":
    print("Running tests...")
    test_config()
    test_characters()
    test_emotion_detector()
    test_emotion_detector_negation()  # track-2
    test_fl_engine()
    test_db()
    test_minimax_chat_mock()
    test_minimax_music_mock()
    print("\n✅ All tests passed!")
