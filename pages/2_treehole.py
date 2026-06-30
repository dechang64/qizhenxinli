"""匿名树洞 — 释放心事，不留痕迹

设计原则：
- 释放即消失，内容不持久化
- 4种释放方式（风/湖/花/烟）
- 仅统计聚合数据用于联邦学习
- 与倾诉旅程串联：感知情绪上下文，给出个性化疗愈回复

track-1 升级：
- 疗愈回复由 GLM + 角色 system_prompt 实时生成
- 含 1-5 星反馈闭环（低分触发补充疗愈，高分引导去共鸣墙）
- hero 顶部显示当前场景/角色/疗法上下文
- 读取 personality_params["reply_length"] 控制回复长度

track-2 升级：
- 首屏引导：3x4 情绪按钮 + 9 场景 grid，让用户先点选再写（降低倾诉门槛）
- 文本框可选：用户即使没写字也可以直接释放
- 释放后"沉淀到共鸣"：3 个按钮（发布到共鸣墙 / 再来一次 / 回到大观园）
- 文本框 placeholder 随所选情绪变化
"""

import random
import uuid
import requests
import tempfile
import streamlit as st

# ── DIAG: 包 import 块抓任何错，streamlit 报 ImportError 时把 traceback 显示出来 ──
try:
    from core.config import (
        RELEASE_METHODS, EMOTION_MUSIC_MAP, MUSIC_PLACES, MUSIC_MOODS,
        EMOTION_ICONS, EMOTION_PLACEHOLDERS, SCENE_FIT_HINTS, SCENES, SCENE_MAP,
    )
    from core.emotion_detector import detect_emotion, compute_session_emotion_profile
    from core.fl_engine import submit_local_stats
    from core.db import (
        record_treehole, get_treehole_stats, record_treehole_feedback, create_post,
    )
    from core.minimax_chat import chat
    from core.characters import get_character
except Exception as _diag_err:
    import traceback as _diag_tb
    _tb_text = _diag_tb.format_exc()
    # 写到 stderr 让 Cloud logs 抓得到
    import sys as _diag_sys
    print("=== DIAG: 2_treehole.py import error ===", file=_diag_sys.stderr)
    print(_tb_text, file=_diag_sys.stderr)
    # 显示在屏幕
    st.error("❌ 2_treehole.py 加载失败 (DIAG mode)\n\n```\n" + _tb_text + "\n```")
    st.stop()

st.set_page_config(page_title="匿名树洞 · 大观园树洞", page_icon="🌳", layout="centered")
from core.styles import inject_css; inject_css()
# Layer 1: 树皮纹理背景
st.markdown('<div class="treehole-body">', unsafe_allow_html=True)

# GitHub Release — 音乐文件（同 music.py）
# GitHub Release — 音乐文件（同 music.py）
RELEASE_BASE = "https://github.com/dechang64/dgy-treehole/releases/download/v1.0-music"
# GitHub Release — ambient音效（同 Release）
RELEASE_AMBIENT_BASE = "https://github.com/dechang64/dgy-treehole/releases/download/v1.0-music"
FILENAME_MAP = {
    "潇湘馆_宁静.mp3": "xiaoxiangguan_ningjing.mp3",
    "潇湘馆_思念.mp3": "xiaoxiangguan_sinian.mp3",
    "潇湘馆_欢愉.mp3": "xiaoxiangguan_huanyu.mp3",
    "潇湘馆_沉思.mp3": "xiaoxiangguan_chensi.mp3",
    "潇湘馆_疗愈.mp3": "xiaoxiangguan_liaoyu.mp3",
    "潇湘馆_释然.mp3": "xiaoxiangguan_shiran.mp3",
    "蘅芜苑_宁静.mp3": "hengwuyuan_ningjing.mp3",
    "蘅芜苑_思念.mp3": "hengwuyuan_sinian.mp3",
    "蘅芜苑_欢愉.mp3": "hengwuyuan_huanyu.mp3",
    "蘅芜苑_沉思.mp3": "hengwuyuan_chensi.mp3",
    "蘅芜苑_疗愈.mp3": "hengwuyuan_liaoyu.mp3",
    "蘅芜苑_释然.mp3": "hengwuyuan_shiran.mp3",
    "怡红院_宁静.mp3": "yihongyuan_ningjing.mp3",
    "怡红院_思念.mp3": "yihongyuan_sinian.mp3",
    "怡红院_欢愉.mp3": "yihongyuan_huanyu.mp3",
    "怡红院_沉思.mp3": "yihongyuan_chensi.mp3",
    "怡红院_疗愈.mp3": "yihongyuan_liaoyu.mp3",
    "怡红院_释然.mp3": "yihongyuan_shiran.mp3",
    "稻香村_宁静.mp3": "daoxiangcun_ningjing.mp3",
    "稻香村_思念.mp3": "daoxiangcun_sinian.mp3",
    "稻香村_欢愉.mp3": "daoxiangcun_huanyu.mp3",
    "稻香村_沉思.mp3": "daoxiangcun_chensi.mp3",
    "稻香村_疗愈.mp3": "daoxiangcun_liaoyu.mp3",
    "稻香村_释然.mp3": "daoxiangcun_shiran.mp3",
    "藕香榭_宁静.mp3": "ouxiangxie_ningjing.mp3",
    "藕香榭_思念.mp3": "ouxiangxie_sinian.mp3",
    "藕香榭_欢愉.mp3": "ouxiangxie_huanyu.mp3",
    "藕香榭_沉思.mp3": "ouxiangxie_chensi.mp3",
    "藕香榭_疗愈.mp3": "ouxiangxie_liaoyu.mp3",
    "藕香榭_释然.mp3": "ouxiangxie_shiran.mp3",
    "秋爽斋_宁静.mp3": "qiushuangzhai_ningjing.mp3",
    "秋爽斋_思念.mp3": "qiushuangzhai_sinian.mp3",
    "秋爽斋_欢愉.mp3": "qiushuangzhai_huanyu.mp3",
    "秋爽斋_沉思.mp3": "qiushuangzhai_chensi.mp3",
    "秋爽斋_疗愈.mp3": "qiushuangzhai_liaoyu.mp3",
    "秋爽斋_释然.mp3": "qiushuangzhai_shiran.mp3",
    # ── 新增三院 ──
    "栊翠庵_宁静.mp3": "longcuian_ningjing.mp3",
    "栊翠庵_思念.mp3": "longcuian_sinian.mp3",
    "栊翠庵_欢愉.mp3": "longcuian_huanyu.mp3",
    "栊翠庵_沉思.mp3": "longcuian_chensi.mp3",
    "栊翠庵_疗愈.mp3": "longcuian_liaoyu.mp3",
    "栊翠庵_释然.mp3": "longcuian_shiran.mp3",
    "缀锦楼_宁静.mp3": "zhuilou_ningjing.mp3",
    "缀锦楼_思念.mp3": "zhuilou_sinian.mp3",
    "缀锦楼_欢愉.mp3": "zhuilou_huanyu.mp3",
    "缀锦楼_沉思.mp3": "zhuilou_chensi.mp3",
    "缀锦楼_疗愈.mp3": "zhuilou_liaoyu.mp3",
    "缀锦楼_释然.mp3": "zhuilou_shiran.mp3",
    "紫菱洲_宁静.mp3": "zilingzhou_ningjing.mp3",
    "紫菱洲_思念.mp3": "zilingzhou_sinian.mp3",
    "紫菱洲_欢愉.mp3": "zilingzhou_huanyu.mp3",
    "紫菱洲_沉思.mp3": "zilingzhou_chensi.mp3",
    "紫菱洲_疗愈.mp3": "zilingzhou_liaoyu.mp3",
    "紫菱洲_释然.mp3": "zilingzhou_shiran.mp3",
}


def get_audio_file(place: str, mood: str) -> str | None:
    """下载音乐文件并返回本地路径。

    注意：不能用 @st.cache_data —— 临时文件路径在 Streamlit Cloud
    多 worker 环境下无法跨用户共享，且文件随时会被 GC 清理。
    改为每次重新下载，mp3 普遍 < 1MB，用户冷流 < 5s。
    """
    chinese_name = f"{place}_{mood}.mp3"
    asset_name = FILENAME_MAP.get(chinese_name, chinese_name)
    url = f"{RELEASE_BASE}/{asset_name}"
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(
            suffix=".mp3", prefix=f"treehole_{place}_{mood}_", delete=False
        )
        for chunk in resp.iter_content(chunk_size=65536):
            tmp.write(chunk)
        tmp.close()
        return tmp.name
    except Exception as e:
        # 暴露真正错误而不是 swallow 掉
        print(f"[get_audio_file] 下载失败: {url} | {type(e).__name__}: {e}")
        return None


def get_ambient_file(method: str) -> str | None:
    """下载 ambient音效文件用于释放动画。详见 get_audio_file 的注释。"""
    url = f"{RELEASE_AMBIENT_BASE}/{method}.mp3"
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(
            suffix=".mp3", prefix=f"ambient_{method}_", delete=False
        )
        for chunk in resp.iter_content(chunk_size=32768):
            tmp.write(chunk)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"[get_ambient_file] 下载失败: {url} | {type(e).__name__}: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#  个性化疗愈回复引擎（track-1：GLM 角色化生成 + 降级到硬编码）
# ═══════════════════════════════════════════════════════════

# 回复长度指令（per personality_params.reply_length）— 轻量追加到 user message
REPLY_LENGTH_HINTS = {
    "short":       "回复控制在60-100字，简短有力。",
    "medium":      "回复控制在100-180字，中等长度。",
    "medium_long": "回复控制在150-250字，可以稍展开一些。",
}

# 兜底用的硬编码回复（GLM 不可用时降级到这套）
def _legacy_healing_reply(emotion: str, personality_tone: str, word_count: int) -> str:
    """GLM 不可用时的降级回复 — 保留旧的硬编码模板"""

    tone_replies = {
        "gentle_listening": [
            "你愿意把这些话说出来，本身就是很勇敢的事。",
            "说出来就够了。你不需要解释，不需要辩护，只需要被听见。",
            "这些话藏在心里很久了吧。今天你说出来了，这就够了。",
        ],
        "warm": [
            "你已经很棒了。能承认自己的感受，本身就是一种力量。",
            "有些话不需要被理解，只需要被说出来。你做到了。",
            "你已经撑了很久了。今天，就让这些话有个出口吧。",
        ],
        "light": [
            "好，说出来了就好了。",
            "有些事情，说出来就不一样了。",
            "行了，剩下的交给风和湖水吧。",
        ],
        "guiding": [
            "你能识别自己的情绪，这很重要。你已经迈出了第一步。",
            "愿意面对自己的感受，本身就是成熟的标志。",
            "你不需要一个人扛。但今天，你选择了说出来——这很了不起。",
        ],
    }

    emotion_addons = {
        "悲伤": "悲伤不是软弱，它是爱过的证据。",
        "焦虑": "不安的时候，允许自己不安，就已经是在照顾自己了。",
        "愤怒": "有情绪是正常的。你的感受是真实的，不需要被评判。",
        "迷茫": "不知道方向也没关系。有时候，走着走着，路就出现了。",
        "疲惫": "你已经很努力了。今天，就让自己停一停吧。",
        "孤独": "孤独是一种感受，不是事实。你并不孤单。",
        "平静": "平静也是一种力量——它意味着你不需要依赖外界的回应。",
        "感恩": "能感受到感恩的人，内心一定是柔软的。",
        "期待": "有期待的人，说明还没有放弃。",
    }

    tone_key = personality_tone if personality_tone in tone_replies else "warm"
    base = random.choice(tone_replies.get(tone_key, tone_replies["warm"]))

    addon = ""
    priority_emotions = ["悲伤", "焦虑", "疲惫", "愤怒"]
    if emotion in priority_emotions:
        addon = " " + random.choice([emotion_addons.get(e, "") for e in [emotion]])
    elif emotion in emotion_addons and random.random() > 0.4:
        addon = " " + random.choice([emotion_addons[emotion]])

    return (base + addon).strip()


def _is_chat_error(reply: str) -> bool:
    """检测 chat() 是否返回了错误占位（以"（"开头的中文括号提示）"""
    if not reply:
        return True
    return reply.lstrip().startswith("（")


def _resolve_chat_context() -> tuple[str, dict]:
    """从 session_state 解析 (character, personality_params)。
    树洞页允许在没经过倾诉旅程时直接使用，因此 chat_character 缺失时
    fallback 到"贾宝玉"，personality_params 缺失时给空 dict。
    """
    character = st.session_state.get("chat_character", "") or "贾宝玉"
    params = st.session_state.get("personality_params", {}) or {}
    return character, params


def get_healing_reply(
    treehole_text: str,
    emotion: str,
    character: str | None = None,
    personality_params: dict | None = None,
    followup_hint: str | None = None,
    fallback_tone: str = "warm",
) -> str:
    """调用 GLM 角色化疗愈回复。

    行为：
    - character 缺省 → 从 session_state 取，再 fallback 贾宝玉
    - personality_params 缺省 → 从 session_state 取
    - reply_length 在 personality_params 中 → 在 user message 追加长度指令
    - followup_hint 非空 → 用于"补充疗愈"（低分反馈触发），前缀追加
    - chat() 失败/超时/网络错误 → 降级到 _legacy_healing_reply
    - MOCK_MODE（无 GLM_API_KEY）→ 直接走 _mock_response，不降级
    """
    # ── TRACK-1-HEALING-CORE: GLM character-based healing reply ──
    if character is None:
        character, params = _resolve_chat_context()
    else:
        params = personality_params if personality_params is not None else (
            st.session_state.get("personality_params", {}) or {}
        )

    # chat() 内部会调 build_system_prompt(character, personality_params)，
    # 这就是 spec 要求的"传入当前角色 system_prompt"。
    # MOCK_MODE 下 chat() 返回 _mock_response(character, messages, params)，
    # 无 key 不崩。
    length_hint = REPLY_LENGTH_HINTS.get(params.get("reply_length", ""), "")

    # 组合 user content
    user_parts = []
    if followup_hint:
        user_parts.append(followup_hint)
    user_parts.append("用户刚在树洞里写下的心事：")
    user_parts.append(treehole_text.strip())
    if emotion:
        user_parts.append(f"\n（情绪标签：{emotion}）")
    if length_hint:
        # 轻量改：只在 user message 追加一句长度指令，不污染 system_prompt
        user_parts.append(f"\n（{length_hint}）")
    user_content = "\n".join(user_parts)

    # 至少 1 条历史 — 留 user/assistant 交错以便 LLM 看到上下文
    # 旧版有 chat_history 也可一并塞入（避免完全空 messages）
    history = st.session_state.get("chat_history", []) or []
    messages: list[dict] = []
    # 最多取最近 2 条 user/assistant 交替（满足"至少 1 条历史"）
    for m in history[-2:]:
        if m.get("role") in ("user", "assistant"):
            content = m.get("content", m.get("text", ""))
            if content:
                messages.append({"role": m["role"], "content": content})
    messages.append({"role": "user", "content": user_content})

    reply = chat(
        messages=messages,
        character=character,
        personality_params=params,
        temperature=0.7,
        max_tokens=400,
    )

    # 降级：MOCK_MODE 走的是 _mock_response 不会出错；真实 API 失败时
    # _is_chat_error 检测到 "（" 开头的占位文本就降级到 _legacy_healing_reply
    if _is_chat_error(reply):
        tone = params.get("tone", fallback_tone)
        return _legacy_healing_reply(emotion, tone, len(treehole_text))
    return reply


# 当前回复的反馈 token — session_state 跟踪以防重复评分
# ── TRACK-1-HEALING-CORE: feedback loop token ──
# 用 dict-style 访问，避开 __setattr__ 路径（更兼容 streamlit 1.40+ 在 module 顶层的初始化）
if "treehole_feedback_token" not in st.session_state:
    st.session_state["treehole_feedback_token"] = 0


def _render_healing_and_feedback(
    treehole_text: str,
    emotion: str,
    method: str,
    character: str,
    personality_params: dict,
) -> None:
    """渲染疗愈回复卡片 + 1-5 星反馈闭环。

    行为：
    - 用 st.html() 渲染 reply 卡片（避免 f-string markdown 解析问题）
    - 5 颗星 button → 点击存 db + rerun
    - 1-2 星 → 自动触发"补充疗愈"（再调一次 get_healing_reply，附 followup_hint）
    - 4-5 星 → 显示一句暖话 + "去共鸣墙"按钮
    - 已经评过分的回复不再显示反馈 UI（用 treehole_feedback_token 跟踪）

    ── TRACK-1-HEALING-CORE: healing reply + 1-5 star feedback UI ──
    """
    # 当前回复 token（每个 selected_method 触发一次新回复 → 新 token）
    # token 在外面 caller 已递增；这里只读
    current_token = st.session_state.get("treehole_feedback_token", 0)
    rated_token = st.session_state.get("treehole_feedback_rated_token", -1)
    already_rated = current_token == rated_token and rated_token >= 0

    # ── 角色化疗愈回复（GLM 实时生成）──
    with st.spinner(f"正在让{character}陪你..."):
        reply = get_healing_reply(
            treehole_text=treehole_text,
            emotion=emotion,
            character=character,
            personality_params=personality_params,
            fallback_tone=personality_params.get("tone", "warm"),
        )

    char_info = get_character(character)
    st.html(f"""
<div class="card" style="text-align:center; margin-top: 0.5rem;">
    <div style="font-size:0.72rem;color:#b8860b;letter-spacing:0.1rem;margin-bottom:0.3rem;">
        {char_info.get('icon', '🌸')} {character} · {char_info.get('theory', '')}
    </div>
    <p style="font-style:italic; color: #2c1810; line-height: 1.8; font-size:0.95rem;">
        "{reply}"
    </p>
</div>
""")

    # ── 反馈 UI ──
    if not already_rated:
        st.markdown(
            '<div style="text-align:center;font-size:0.75rem;color:#8b7355;margin-top:0.4rem;">'
            "这条回复陪到你了么？"
            "</div>",
            unsafe_allow_html=True,
        )
        # 5 颗星：5 个 button 横排（Streamlit 1.40+ 的 st.feedback 也支持 stars）
        star_cols = st.columns(5)
        for star in range(1, 6):
            with star_cols[star - 1]:
                if st.button(
                    "★" * star + "☆" * (5 - star),
                    key=f"fb_star_{current_token}_{star}",
                    use_container_width=True,
                ):
                    _handle_feedback(star, treehole_text, emotion, method, character, personality_params)
    else:
        # 已评分：根据分数显示不同反馈
        last_score = st.session_state.get("treehole_feedback_last_score", 0)
        if last_score >= 4:
            st.html(f"""
<div class="card" style="text-align:center; margin-top: 0.5rem; background:#f0f7f2; border-color:#2d6a4f;">
    <p style="color:#2d6a4f; font-size:0.92rem; margin:0;">
        🌿 很高兴陪到了你。
    </p>
    <p style="color:#8b7355; font-size:0.78rem; margin:0.3rem 0 0 0;">
        愿你带着这份温暖继续走。
    </p>
</div>
""")
            if st.button("🌸 去共鸣墙看看和你一样心情的人", key=f"goto_resonance_{current_token}"):
                st.switch_page("pages/3_resonance.py")
        else:
            # 低分（1-2 星）已被 _handle_feedback 处理为"补充疗愈"
            st.html(f"""
<div class="card" style="text-align:center; margin-top: 0.5rem; background:#fdf6e3; border-color:#b8860b;">
    <p style="color:#8b7355; font-size:0.85rem; margin:0;">
        谢谢你诚实地说出来。下面是另一位伙伴换一种角度的回应。
    </p>
</div>
""")


def _handle_feedback(
    score: int,
    treehole_text: str,
    emotion: str,
    method: str,
    character: str,
    personality_params: dict,
) -> None:
    """处理用户点击星星：
    - 存 db
    - 标记已评分（用 token 防重）
    - 低分（1-2）→ 触发"补充疗愈"：再调一次 get_healing_reply，附 followup_hint

    ── TRACK-1-HEALING-CORE: feedback handler (1-5 star → db + rerun) ──
    """
    try:
        record_treehole_feedback(
            session_id=st.session_state.get("session_id", ""),
            score=score,
            emotion=emotion,
            method=method,
        )
    except Exception as e:
        # 评分落库失败不能阻塞 UI
        print(f"[treehole_feedback] 写入失败: {type(e).__name__}: {e}")

    st.session_state.treehole_feedback_last_score = score
    st.session_state.treehole_feedback_rated_token = st.session_state.treehole_feedback_token
    st.session_state.treehole_feedback_need_followup = (score <= 2)

    # rerun 让 UI 刷新（避免连续点击 + 显示"补充疗愈"）
    st.rerun()


def _maybe_render_followup(
    treehole_text: str,
    emotion: str,
    character: str,
    personality_params: dict,
) -> None:
    """如果刚被打低分，渲染一次"补充疗愈"回复。

    只触发一次：用 treehole_feedback_followup_done 标记。
    补充疗愈也用 GLM（带 followup_hint），失败则降级到 _legacy_healing_reply（get_healing_reply 内部已处理）。

    ── TRACK-1-HEALING-CORE: follow-up healing for low scores (1-2 stars) ──
    """
    need = st.session_state.pop("treehole_feedback_need_followup", False)
    done = st.session_state.get("treehole_feedback_followup_done", False)
    if not need or done:
        return
    st.session_state.treehole_feedback_followup_done = True
    last_score = st.session_state.get("treehole_feedback_last_score", 1)

    followup_hint = (
        f"用户对上一条疗愈回复打了 {last_score} 星（1-5），觉得不够有共鸣。"
        "请换一种角度再回应这次心事：可能是更温柔的、更直接的、"
        "或更具体地接住用户原文中的某个细节。不要重复上一条的开头。"
    )
    with st.spinner(f"正在让{character}换一种方式再回应..."):
        followup = get_healing_reply(
            treehole_text=treehole_text,
            emotion=emotion,
            character=character,
            personality_params=personality_params,
            followup_hint=followup_hint,
            fallback_tone=personality_params.get("tone", "warm"),
        )
    char_info = get_character(character)
    st.html(f"""
<div class="card" style="text-align:left; margin-top: 0.5rem; background:#fff8e7; border-color:#d4a574;">
    <div style="font-size:0.72rem;color:#b8860b;letter-spacing:0.1rem;margin-bottom:0.3rem;">
        {char_info.get('icon', '🌸')} {character} · 再试一次
    </div>
    <p style="font-style:italic; color: #2c1810; line-height: 1.8; font-size:0.92rem;">
        "{followup}"
    </p>
</div>
""")


def get_music_recommendation(emotion: str) -> tuple[str, str]:
    """根据情绪推荐音乐场景+情绪"""
    if emotion in EMOTION_MUSIC_MAP:
        mood = EMOTION_MUSIC_MAP[emotion]["primary"]
    else:
        mood = "疗愈"

    # 悲伤/孤独 → 怡红院（温暖），焦虑/疲惫 → 稻香村（宁静）
    # 执念 → 栊翠庵（放下），委屈 → 缀锦楼（边界），自卑 → 紫菱洲（自我悲悯）
    scene_map = {
        "悲伤": "怡红院",
        "孤独": "怡红院",
        "焦虑": "稻香村",
        "疲惫": "稻香村",
        "迷茫": "潇湘馆",
        "愤怒": "藕香榭",
        "平静": "稻香村",
        "感恩": "怡红院",
        "期待": "藕香榭",
        # ── 新增三院 ──
        "执念": "栊翠庵",
        "委屈": "缀锦楼",
        "自卑": "紫菱洲",
    }
    scene = scene_map.get(emotion, "稻香村")
    return scene, mood


# ═══════════════════════════════════════════════════════════
#  track-2：首屏引导 + 释放后"沉淀到共鸣"
# ═══════════════════════════════════════════════════════════

def _init_treehole_state() -> None:
    """初始化首屏引导 + 释放后流程的 session_state 字段。

    ── TRACK-2-TREEHOLE-FLOW: state init for first-screen guide + release sediment ──
    """
    if "treehole_emotion" not in st.session_state:
        # 用户在首屏 3x4 网格点选的情绪（默认 None = 还没选）
        st.session_state.treehole_emotion = None
    if "treehole_scene" not in st.session_state:
        # 用户在 9 场景 grid 点选的场景（默认 None = 还没选）
        st.session_state.treehole_scene = None
    if "treehole_release_done" not in st.session_state:
        # 当前是否已释放过（释放后展示"沉淀到共鸣"按钮组）
        st.session_state.treehole_release_done = False
    if "treehole_post_confirm_open" not in st.session_state:
        # "发布到共鸣墙"二次确认是否展开
        st.session_state.treehole_post_confirm_open = False
    if "treehole_last_text" not in st.session_state:
        # 暂存当次释放的文本（供发布到共鸣时用）
        st.session_state.treehole_last_text = ""


def _render_emotion_grid() -> None:
    """首屏 3x4 情绪按钮网格。

    12 个情绪，按 4 列 × 3 行排列：
    - 每个按钮显示 icon + 中文名
    - 点选后该按钮高亮，存到 st.session_state.treehole_emotion
    """
    st.html("""
<div style="text-align:center; margin: 0.6rem 0 0.3rem;">
    <div style="font-size:0.95rem; color:#2c1810; font-weight:600;">今天，你心里装着什么？</div>
    <div style="font-size:0.72rem; color:#8b7355; margin-top:0.2rem;">
        点一下就好，不一定要写得很完整
    </div>
</div>
""")

    # 4 列 × 3 行 = 12 个情绪
    cols_per_row = 4
    for row_start in range(0, len(EMOTION_ICONS), cols_per_row):
        row_emotions = list(EMOTION_ICONS.keys())[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, emo in enumerate(row_emotions):
            icon = EMOTION_ICONS[emo]
            is_selected = (st.session_state.treehole_emotion == emo)
            # 选中时显示勾选
            label = f"{'✅ ' if is_selected else ''}{icon} {emo}"
            btn_type = "primary" if is_selected else "secondary"
            with cols[i]:
                if st.button(
                    label,
                    key=f"emo_grid_{emo}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    # 切换：再点同一项 = 取消选择
                    if st.session_state.treehole_emotion == emo:
                        st.session_state.treehole_emotion = None
                    else:
                        st.session_state.treehole_emotion = emo
                        # 选情绪后，自动推荐一个场景（但不强制）
                        rec_scene, _ = get_music_recommendation(emo)
                        if not st.session_state.treehole_scene:
                            st.session_state.treehole_scene = rec_scene
                    st.rerun()


def _render_scene_grid() -> None:
    """9 场景 grid，每个场景显示 icon + name + "适合" 短句。

    全部 9 场景都展示，可点选 1 个；点中后存到 st.session_state.treehole_scene。
    未选情绪时也可点（独立选择）。
    """
    if not st.session_state.treehole_emotion:
        st.html("""
<div style="text-align:center; margin: 0.6rem 0 0.2rem; font-size:0.78rem; color:#8b7355;">
    👆 先选一个情绪，下面会自动给你推荐一个场景
</div>
""")
    else:
        st.html(f"""
<div style="text-align:center; margin: 0.6rem 0 0.2rem; font-size:0.78rem; color:#8b7355;">
    现在的情绪：<strong style="color:#b8860b;">{st.session_state.treehole_emotion}</strong>
    · 选一个最像你今天心情的场景（也可以不选）
</div>
""")

    # 3 列 × 3 行 = 9 场景
    cols_per_row = 3
    for row_start in range(0, len(SCENES), cols_per_row):
        row_scenes = SCENES[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, scene in enumerate(row_scenes):
            sname = scene["name"]
            icon = scene["icon"]
            fit = SCENE_FIT_HINTS.get(sname, scene.get("desc", ""))
            is_selected = (st.session_state.treehole_scene == sname)
            # 选中标记
            label = f"{'✅ ' if is_selected else ''}{icon} {sname}\n{fit}"
            btn_type = "primary" if is_selected else "secondary"
            with cols[i]:
                if st.button(
                    label,
                    key=f"scene_grid_{sname}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    if st.session_state.treehole_scene == sname:
                        st.session_state.treehole_scene = None
                    else:
                        st.session_state.treehole_scene = sname
                    st.rerun()


def _render_post_release_actions() -> None:
    """释放完成后底部 3 个按钮：发布到共鸣墙 / 再来一次 / 回到大观园。

    行为：
    - "发布到共鸣墙" → 二次确认后调 create_post(source="treehole") + 跳共鸣页
    - "再来一次" → 清状态 + rerun（用户回到首屏）
    - "回到大观园" → 跳 app.py

    ── TRACK-2-TREEHOLE-FLOW: post-release sediment to resonance ──
    """
    treehole_text = st.session_state.get("treehole_last_text", "")
    emotion = st.session_state.get("treehole_last_emotion", "平静")
    selected_scene = st.session_state.get("treehole_scene", "") or \
        st.session_state.get("treehole_recommend_scene", "") or ""

    st.html("""
<div style="
    margin-top: 1.2rem;
    padding: 0.8rem 0.6rem;
    background: rgba(184,134,11,0.06);
    border-radius: 12px;
    border: 1px dashed #d4c5a9;
    text-align:center;
">
    <div style="font-size:0.85rem; color:#2c1810; font-weight:600; margin-bottom:0.3rem;">
        🌸 想让这段话被听见吗？
    </div>
    <div style="font-size:0.72rem; color:#8b7355;">
        发布到共鸣墙，会有人和你一起分担这份心情
    </div>
</div>
""")

    cols = st.columns(3)
    with cols[0]:
        # 发布按钮：treehole_text 为空时禁用
        can_post = bool(treehole_text and treehole_text.strip())
        if st.button(
            "🌸 发布到共鸣墙",
            key="post_to_resonance",
            use_container_width=True,
            disabled=not can_post,
            help="把刚才写的话匿名发布到共鸣墙" if can_post else "需要先写点内容才能发布",
        ):
            if can_post:
                st.session_state.treehole_post_confirm_open = True
                st.rerun()
    with cols[1]:
        if st.button("🔁 再来一次", key="treehole_again", use_container_width=True):
            # 清空所有暂存状态 + rerun
            for k in [
                "treehole_emotion", "treehole_scene", "treehole_release_done",
                "treehole_post_confirm_open", "treehole_last_text", "treehole_last_emotion",
                "treehole_last_character", "treehole_last_personality_params",
                "treehole_recommend_scene", "treehole_selected_method",
                "treehole_feedback_token", "treehole_feedback_followup_done",
            ]:
                st.session_state[k] = (
                    None if k in ("treehole_emotion", "treehole_scene",
                                  "treehole_release_done", "treehole_post_confirm_open",
                                  "treehole_recommend_scene", "treehole_selected_method")
                    else ("" if "text" in k or "emotion" in k or "character" in k
                          else ({} if "params" in k else False))
                )
            st.rerun()
    with cols[2]:
        if st.button("🏠 回到大观园", key="treehole_home", use_container_width=True):
            st.switch_page("app.py")

    # ── 二次确认：发布到共鸣墙 ──
    if st.session_state.get("treehole_post_confirm_open"):
        st.html("""
<div style="
    margin-top: 0.8rem;
    padding: 0.8rem;
    background: #fff8e7;
    border: 1px solid #d4a574;
    border-radius: 8px;
    text-align:center;
">
    <div style="font-size:0.82rem; color:#2c1810; margin-bottom:0.6rem;">
        你确定要把这段话发布到共鸣墙吗？<br>
        <span style="font-size:0.72rem; color:#8b7355;">
            发布后其他人可以看到你的内容（不含身份）
        </span>
    </div>
</div>
""")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 确认发布", key="post_confirm_yes", type="primary", use_container_width=True):
                try:
                    post_id = create_post(
                        content=treehole_text,
                        emotion=emotion,
                        scene=selected_scene,
                        source="treehole",
                        session_id=st.session_state.get("session_id", ""),
                    )
                    st.session_state.treehole_post_confirm_open = False
                    st.success(f"🌸 已发布到共鸣墙（id={post_id}）")
                    st.balloons()
                    # 跳到共鸣页
                    st.switch_page("pages/3_resonance.py")
                except Exception as e:
                    st.error(f"发布失败：{type(e).__name__}: {e}")
        with c2:
            if st.button("取消", key="post_confirm_no", use_container_width=True):
                st.session_state.treehole_post_confirm_open = False
                st.rerun()

# ── 初始化 session ──
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]
_init_treehole_state()

# ── 返回 ──
if st.button("← 回到大观园", use_container_width=True):
    st.switch_page("app.py")

# ── 场景/角色/疗法上下文条（track-1）──
# ── TRACK-1-HEALING-CORE: hero context bar (scene / character / therapy) ──
# 显示当前疗愈旅程来自哪里；缺省回落"林黛玉 · 叙事疗法"
_ctx_character = st.session_state.get("chat_character", "") or "林黛玉"
_ctx_scene = st.session_state.get("current_scene", "") or "潇湘馆"
_ctx_char_info = get_character(_ctx_character)
_ctx_theory = _ctx_char_info.get("theory", "叙事疗法")
_ctx_icon = _ctx_char_info.get("icon", "🎋")
_ctx_bar = f"{_ctx_icon} {_ctx_scene} · {_ctx_character}陪你 · {_ctx_theory}"
st.html(f"""
<div style="
    margin: 0 0 0.6rem 0;
    padding: 0.5rem 0.9rem;
    background: rgba(245,240,232,0.85);
    border: 1px solid #d4c5a9;
    border-radius: 99px;
    text-align: center;
    font-size: 0.78rem;
    color: #2c1810;
    letter-spacing: 0.03rem;
">
    {_ctx_bar}
</div>
""")

# ── 树洞 Hero：古槐内腔，月光从树缝漏下 ──
# 用 st.html 避免 markdown 解析器在嵌套 div + 中文 + emoji 时的兼容 bug
st.html("""
<div class="treehole-hero">
    <div class="moon">🌕</div>
    <h2>古 · 树 · 洞</h2>
    <p class="sub">把心事说给这棵千年老槐，让它替你记得</p>
    <div class="quote">
        <span class="falling-leaf">🍃</span>
        <span class="falling-leaf">🍂</span>
        <span class="falling-leaf">🍃</span>
        &nbsp;说出即放下，落地即归尘
    </div>
    <p style="font-size: 0.72rem; color: #8b7355; margin-top: 1rem;">
        🔒 你的话不会被存储 · 释放即消失
    </p>
    <p style="font-size: 0.68rem; color: #b8860b; margin-top: 0.3rem;">
        💡 想留下共鸣？去「🌸 匿名共鸣」发布
    </p>
</div>
""")

# ── 情绪上下文（来自倾诉旅程）──
chat_history = st.session_state.get("chat_history", [])
personality_source = st.session_state.get("personality_source", "")
current_scene = st.session_state.get("current_scene", "")
personality_tag = ""
if personality_source == "mbti":
    personality_tag = st.session_state.get("personality_type", "")

# 如果有对话历史，显示情绪上下文
if chat_history:
    profile = compute_session_emotion_profile(chat_history)
    if profile:
        top_emotion = max(profile, key=profile.get)
        top_score = profile[top_emotion]
        msg_count = len([m for m in chat_history if m.get("role") == "user"])

        context_lines = [f"你在{current_scene or '这里'}倾诉了 {msg_count} 句话"]
        if top_score > 0.3:
            context_lines.append(f"主要感到「{top_emotion}」（{top_score:.0%}）")

        context_text = "，".join(context_lines)

        if personality_tag:
            personality_tag_html = f'<span class="tag">{personality_tag}</span>'
        else:
            personality_tag_html = ""

        st.markdown(f"""
<div class="card" style="border-left: 3px solid #2d6a4f; padding: 0.8rem;">
    <div style="font-size: 0.78rem; color: #8b7355;">{context_text}{personality_tag_html}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  track-2：首屏引导（情绪 → 场景 → 文本 → 释放）
# ═══════════════════════════════════════════════════════════

# ── 1. 情绪网格（3x4 = 12 个情绪）──
_render_emotion_grid()

# ── 2. 场景网格（3x3 = 9 个场景，情绪选完后展开）──
_render_scene_grid()

# ── 3. 文本输入（情绪选完后才展开；文本可选）──
if st.session_state.treehole_emotion:
    _selected_emo = st.session_state.treehole_emotion
    _placeholder = EMOTION_PLACEHOLDERS.get(
        _selected_emo, "把你想说的话写下来..."
    )
    # 在输入框上方显示当前选中的情绪
    st.html(f"""
<div style="margin-top: 0.8rem; margin-bottom: 0.3rem; font-size:0.78rem; color:#8b7355;">
    选好了 · 现在写不写都行，不写也可以直接点释放 ↓
</div>
""")
    treehole_text = st.text_area(
        "把你想说的话写在这里...",
        height=120,
        placeholder=_placeholder,
        label_visibility="collapsed",
        key="treehole_text_input",
    )
else:
    treehole_text = ""
    # 提示用户先选情绪
    st.html("""
<div style="margin-top: 0.8rem; padding: 0.6rem; background: rgba(184,134,11,0.06);
            border-radius: 8px; text-align:center; font-size:0.8rem; color:#8b7355;">
    👆 先在上面点一个情绪，我们陪你慢慢来
</div>
""")

# ── 4. 释放方式（情绪选完后一直可见，文本可选）──
if st.session_state.treehole_emotion:
    st.html("<div style='margin-top: 0.6rem;'></div>")
    st.markdown("### 选择释放方式")
    cols = st.columns(5)
    selected_method = None

    for i, (key, info) in enumerate(RELEASE_METHODS.items()):
        with cols[i]:
            if st.button(
                f"{info['icon']}\n{key}",
                key=f"release_{key}",
                use_container_width=True,
            ):
                selected_method = key
                st.session_state.treehole_selected_method = key

    # ── 释放动画 ──
    if selected_method:
        method_info = RELEASE_METHODS[selected_method]
        # 优先用用户在首屏选的情绪；若文本有内容，再让 detect_emotion 覆盖
        user_emo = st.session_state.treehole_emotion
        if treehole_text and treehole_text.strip():
            detected = detect_emotion(treehole_text)
            # 检测结果与用户选择不一致时，优先用检测结果（数据驱动）
            # 但若检测为"平静"且用户明确选了情绪，保留用户选择
            if detected == "平静":
                emotion = user_emo
            else:
                emotion = detected
        else:
            # 无文本 → 用用户手动选择的情绪
            emotion = user_emo

        # 记录树洞统计
        try:
            record_treehole(selected_method, emotion, len(treehole_text))
        except Exception:
            pass

        # 提交联邦学习统计（只提交情绪标签，不提交内容）
        try:
            submit_local_stats(
                st.session_state.session_id,
                {emotion: 1.0}
            )
        except Exception:
            pass

        # ── track-1：每个新的释放 → 递增 feedback token，让评分 UI 重新出现
        st.session_state.treehole_feedback_token = st.session_state.get("treehole_feedback_token", 0) + 1
        st.session_state.treehole_feedback_followup_done = False

        # ── 解析角色/人格上下文（GLM 调用需要）──
        _character, _personality_params = _resolve_chat_context()

        # 暂存当次上下文（rerun 后 _maybe_render_followup 仍能取到）
        st.session_state.treehole_last_text = treehole_text
        st.session_state.treehole_last_emotion = emotion
        st.session_state.treehole_last_character = _character
        st.session_state.treehole_last_personality_params = _personality_params
        # 标记释放已完成（用于底部 3 按钮显示）
        st.session_state.treehole_release_done = True
        # 暂存推荐场景（供发布到共鸣时用）
        _rec_scene, _ = get_music_recommendation(emotion)
        st.session_state.treehole_recommend_scene = _rec_scene

        # ── Layer 3: 静默模式 ──
        if selected_method == "silent":
            music_scene, music_mood = get_music_recommendation(emotion)

            st.markdown("""
<div style="text-align:center; padding: 2rem;" class="fade-in">
    <div style="font-size: 3.5rem;" class="gentle-float">🎧</div>
    <h3 style="color: #b8860b; margin-top: 1rem;">静静聆听</h3>
    <p style="color: #8b7355;">什么都不做，只是听</p>
</div>""", unsafe_allow_html=True)

            with st.spinner(f"正在为你加载 {music_scene} · {music_mood} ..."):
                audio_path = get_audio_file(music_scene, music_mood)

            if audio_path:
                st.audio(audio_path, format="audio/mp3", autoplay=True)
            else:
                st.error(
                    f"音乐加载失败（{music_scene} · {music_mood}）。"
                    "请刷新页面重试，或换个释放方式。"
                )

            # 个性化疗愈回复 + 反馈闭环（仅在用户写了文字时调用）
            if treehole_text and treehole_text.strip():
                _render_healing_and_feedback(
                    treehole_text=treehole_text,
                    emotion=emotion,
                    method=selected_method,
                    character=_character,
                    personality_params=_personality_params,
                )

            st.html(f"""
<div style="text-align:center; margin-top: 0.5rem;">
    <span style="font-size: 0.8rem; color: #8b7355;">为你推荐 · </span>
    <a href="/pages/4_music.py" target="_self">
        <button style="background-color: #2d6a4f; color: white; padding: 0.4rem 0.8rem; border: none; border-radius: 0.5rem; cursor: pointer; font-size: 0.8rem;">
            🎵 {music_scene} · {music_mood}
        </button>
    </a>
</div>
""")

        else:
            # ── 普通释放动画 ──
            animations = {
                "wind": """
<div style="text-align:center; padding: 2rem;" class="fade-in">
    <div style="font-size: 4rem;" class="float">🍃</div>
    <h3 style="color: #2d6a4f; margin-top: 1rem;">已随风飘散</h3>
    <p style="color: #8b7355;">风会带走它</p>
</div>""",
                "lake": """
<div style="text-align:center; padding: 2rem;" class="fade-in">
    <div style="font-size: 4rem;" class="float">💧</div>
    <h3 style="color: #2d6a4f; margin-top: 1rem;">已沉入湖底</h3>
    <p style="color: #8b7355;">湖水会记住它</p>
</div>""",
                "petal": """
<div style="text-align:center; padding: 2rem;" class="fade-in">
    <div style="font-size: 4rem;" class="float">🌸</div>
    <h3 style="color: #c0392b; margin-top: 1rem;">已化为花瓣</h3>
    <p style="color: #8b7355;">花瓣会替你开</p>
</div>""",
                "smoke": """
<div style="text-align:center; padding: 2rem;" class="fade-in">
    <div style="font-size: 4rem;" class="float">🕯️</div>
    <h3 style="color: #8b7355; margin-top: 1rem;">已燃为青烟</h3>
    <p style="color: #8b7355;">烟会替你说</p>
</div>""",
            }

            st.markdown(animations[selected_method], unsafe_allow_html=True)

            # ── Layer 2: ambient音效（静默模式除外）──
            with st.spinner(f"正在加载 {selected_method} 音效 ..."):
                ambient_path = get_ambient_file(selected_method)
            if ambient_path:
                st.audio(ambient_path, format="audio/mp3", autoplay=True)

            # 个性化疗愈回复 + 反馈闭环（仅在用户写了文字时调用）
            if treehole_text and treehole_text.strip():
                _render_healing_and_feedback(
                    treehole_text=treehole_text,
                    emotion=emotion,
                    method=selected_method,
                    character=_character,
                    personality_params=_personality_params,
                )

            # 音乐推荐
            music_scene, music_mood = get_music_recommendation(emotion)
            st.html(f"""
<div style="text-align:center; margin-top: 0.8rem;">
    <span style="font-size: 0.8rem; color: #8b7355;">为你推荐 · </span>
    <a href="/pages/4_music.py" target="_self">
        <button style="background-color: #2d6a4f; color: white; padding: 0.4rem 0.8rem; border: none; border-radius: 0.5rem; cursor: pointer; font-size: 0.8rem;">
            🎵 {music_scene} · {music_mood}
        </button>
    </a>
</div>
""")

        # ── track-2：释放后"沉淀到共鸣"3 按钮（在所有释放方式下都显示）──
        _render_post_release_actions()

# ── track-2：star feedback rerun 后也显示"沉淀到共鸣"3 按钮 ──
# 当 selected_method (local) 为 None 但 session_state 里记着上次的释放方式时，
# 说明是评分/star 触发的 rerun —— 这种情况下也要让用户能继续操作
if (
    st.session_state.treehole_release_done
    and not selected_method
    and st.session_state.get("treehole_selected_method")
):
    _render_post_release_actions()

# ── track-1：低分反馈的"补充疗愈"必须在 rerun 后仍能渲染 ──
# 单独拎到这里，不依赖 if selected_method: 分支（rating star 点击会触发 rerun）
_last = st.session_state.get("treehole_last_text")
if _last:
    _maybe_render_followup(
        treehole_text=st.session_state.get("treehole_last_text", ""),
        emotion=st.session_state.get("treehole_last_emotion", "平静"),
        character=st.session_state.get("treehole_last_character", "贾宝玉"),
        personality_params=st.session_state.get("treehole_last_personality_params", {}) or {},
    )

# ── 树洞统计 ──
try:
    stats = get_treehole_stats()
except Exception:
    stats = {}
total_count = sum(v["count"] for v in stats.values()) if stats else 0
if total_count > 0:
    st.markdown("---")
    st.markdown(f"""
<div style="text-align:center; color: #8b7355; font-size: 0.8rem;">
    已有 <strong>{total_count}</strong> 位朋友在这里释放了心事<br>
    <span style="color: #b8860b;">联邦学习保护了每一位朋友的隐私</span>
</div>
""", unsafe_allow_html=True)

# 关闭树皮纹理 wrapper
st.markdown("</div>", unsafe_allow_html=True)
