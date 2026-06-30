"""疗愈音乐 — 大观园树洞

音乐文件通过 GitHub Release 直接托管（Range 请求友好），
由 Streamlit Cloud 代为请求后以本地临时文件方式播放。

智能推荐逻辑：
- 优先读取 session_state.personality_params（MBTI/星座结果）
- 结合 session_state.emotion_profile（当前对话情绪）
- 为用户推荐最契合当前状态的曲目
"""
import streamlit as st
import requests
from core.config import (
    MUSIC_PLACES, MUSIC_MOODS, MBTI_PARAMS, ELEM_PARAMS,
    EMOTION_MUSIC_MAP, MUSIC_MOOD_MUSIC_MAP,
)
from core.emotion_detector import compute_session_emotion_profile

st.set_page_config(page_title="疗愈音乐 · 大观园树洞", page_icon="🎵", layout="centered")
from core.styles import inject_css; inject_css()

# GitHub Release v1.0-music — ASCII 资产名 (从 release API 抓的)
# 例: hengwuyuan_chensi.mp3, daoxiangcun_chensi.mp3, ouxiangxie_chensi.mp3
RELEASE_BASE = "https://github.com/dechang64/dgy-treehole/releases/download/v1.0-music"

# v2 fallback — raw GitHub (mp3 直接 commit 进 repo, 10 段 v1 太短/缺失的备选)
# 命名规则: {scene_ascii}_{mood_ascii}_v2.mp3 (ouxiangxie 1 x, 跟 git + v1 release 一致)
RAW_V2_BASE = "https://raw.githubusercontent.com/dechang64/dgy-treehole/main/data/mp3_v2"

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


# ═══════════════════════════════════════════════════════════
#  智能推荐引擎
# ═══════════════════════════════════════════════════════════

def get_smart_recommendation():
    """
    综合 personality_params + emotion_profile 生成个性化推荐。

    Returns:
        (scene, mood, reason): 推荐场景、情绪、推荐理由
    """
    params = st.session_state.get("personality_params", {})
    personality_source = st.session_state.get("personality_source", "")
    current_scene = st.session_state.get("current_scene", "")
    chat_history = st.session_state.get("chat_history", [])

    reason_parts = []

    # 1. 人格偏好 → music_mood
    personality_mood = params.get("music_mood", "")
    if personality_mood and personality_mood in MUSIC_MOOD_MUSIC_MAP:
        music_mood = MUSIC_MOOD_MUSIC_MAP[personality_mood]
        if personality_source == "mbti":
            mbti_type = st.session_state.get("personality_type", "")
            reason_parts.append(f"你的{mbti_type}人格偏好「{personality_mood}」风格的音乐")
        elif personality_source in ("zodiac", "zodiac_chart"):
            reason_parts.append(f"你的性格特质更适合「{personality_mood}」氛围")
    else:
        music_mood = "宁静"  # 默认

    # 2. 情绪画像 → 调整音乐情绪
    emotion_profile = compute_session_emotion_profile(chat_history) if chat_history else {}
    if emotion_profile:
        top_emotion = max(emotion_profile, key=emotion_profile.get)
        if top_emotion in EMOTION_MUSIC_MAP:
            # 情绪对音乐的影响：人格偏好为主，情绪为辅
            emotion_music = EMOTION_MUSIC_MAP[top_emotion]["primary"]
            if music_mood == "宁静":
                # 焦虑时宁静优先，不覆盖
                reason_parts.append(f"你当前感到「{top_emotion}」，适合平静的音乐来舒缓")
            elif music_mood in ("uplifting", "reflective") and top_emotion in ("悲伤", "孤独"):
                # 悲伤/孤独 时需要温暖
                music_mood = "疗愈"
                reason_parts.append(f"你感到「{top_emotion}」，这首曲子能温柔地陪伴你")
            elif music_mood == "uplifting" and top_emotion in ("愤怒", "迷茫"):
                reason_parts.append(f"你感到「{top_emotion}」，音乐帮你找到力量")
            else:
                reason_parts.append(f"你感到「{top_emotion}」，{emotion_music}的音乐更适合你")
        emotion_profile.pop(top_emotion, None)
    else:
        reason_parts.append("今天适合用音乐陪伴自己")

    # 3. 场景匹配
    if current_scene and current_scene in MUSIC_PLACES:
        scene = current_scene
    elif personality_mood == "reflective":
        scene = "潇湘馆"
    elif personality_mood == "meditative":
        scene = "稻香村"
    elif personality_mood == "warm":
        scene = "怡红院"
    else:
        scene = MUSIC_PLACES[0]

    reason = " · ".join(reason_parts) if reason_parts else "为你量身推荐"
    return scene, music_mood, reason


# ═══════════════════════════════════════════════════════════
#  音频下载（复用之前逻辑）
# ═══════════════════════════════════════════════════════════

def get_audio_url(place: str, mood: str) -> str | None:
    """返回 mp3 的可访问 URL (浏览器直下, 跳过 streamlit cloud 代理).

    v6.4.9 策略: 不用 tempfile 也不用 streamlit media proxy, 直接返回 URL.
    - 优先 v1 release (GitHub Releases CDN, 36 段全有) 但仅当 ≥ 120s
    - v1 < 120s (太短) 时, fallback raw v2 (新生成, 9/10 段 ≥ 2:00)
    - 浏览器直接 GET, 不走 streamlit cloud 代理 (避免 ERR_CONNECTION_RESET)
    """
    chinese_name = f"{place}_{mood}.mp3"
    asset_name = FILENAME_MAP.get(chinese_name, chinese_name)

    # 1. v1 release (ASCII 直拼) - 短 < 120s 视为不可用
    url_v1 = f"{RELEASE_BASE}/{asset_name}"
    if _url_long_enough(url_v1, min_seconds=120):
        return url_v1
    # 2. v2 raw (ASCII + _v2)
    v2_name = asset_name.replace(".mp3", "_v2.mp3")
    url_v2 = f"{RAW_V2_BASE}/{v2_name}"
    if _url_long_enough(url_v2, min_seconds=0):  # v2 存在就用
        return url_v2
    return None


def _url_long_enough(url: str, min_seconds: int) -> bool:
    """HEAD + Content-Length 估算时长 (mp3 bitrate ~128kbps).

    实测 v1 release size 分布:
    - < 1.7 MB: 2 段太短 (longcuian_liaoyu / _.mp3, < 90s)
    - 1.7-2.5 MB: 3 段偏短 (90-130s)
    - >= 2.5 MB: 54 段正常 (>= 130s)

    阈值 2.5 MB ≈ 130s, 把 5 段短 mp3 排除, 走 v2 fallback
    """
    try:
        r = requests.head(url, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return False
        if min_seconds == 0:
            return True
        size = int(r.headers.get("Content-Length", 0))
        return size >= 2_500_000
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════
#  页面渲染
# ═══════════════════════════════════════════════════════════

if st.button("← 回到大观园", use_container_width=True):
    st.switch_page("app.py")

st.markdown("""
<div class="card-dark" style="text-align:center; padding: 1.5rem;">
    <div style="font-size: 2.5rem;">🎵</div>
    <h2 style="margin: 0.5rem 0;">疗愈音乐</h2>
    <p style="font-size: 0.85rem; color: #d4c5a9;">AI 为你生成专属疗愈音乐</p>
</div>
""", unsafe_allow_html=True)

# ── 智能推荐入口 ──
has_personality = "personality_params" in st.session_state
has_chat = bool(st.session_state.get("chat_history", []))
has_context = has_personality or has_chat

if has_context:
    rec_scene, rec_mood, rec_reason = get_smart_recommendation()
    rec_place_idx = MUSIC_PLACES.index(rec_scene) if rec_scene in MUSIC_PLACES else 0
    rec_mood_idx = MUSIC_MOODS.index(rec_mood) if rec_mood in MUSIC_MOODS else 0

    st.markdown(f"""
<div class="card" style="border-left: 3px solid #2d6a4f;">
    <div style="display:flex;align-items:center;gap:0.6rem;">
        <div style="font-size:1.5rem;">✨</div>
        <div>
            <div style="font-size:0.85rem;font-weight:600;color:#2d6a4f;">今日推荐</div>
            <div style="font-size:0.78rem;color:#8b7355;">{rec_reason}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # 直接播放推荐音乐
    rec_url = get_audio_url(rec_scene, rec_mood)
    if rec_url:
        st.markdown(f"""
<div class="card" style="text-align:center;">
    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎶</div>
    <h3>{rec_scene} · {rec_mood}</h3>
    <p style="font-size: 0.8rem; color: #8b7355;">AI 专属生成</p>
</div>
""", unsafe_allow_html=True)
        st.audio(rec_url, format="audio/mp3")
        st.markdown(f"[📥 下载推荐音乐]({rec_url})")

    st.markdown("""
<div style="text-align:center; margin: 0.8rem 0;">
    <span style="font-size: 0.85rem; color: #8b7355;">— 或者，自选音乐 —</span>
</div>
""", unsafe_allow_html=True)

# ── 自选参数 ──
col1, col2 = st.columns(2)
with col1:
    place = st.selectbox(
        "场景", MUSIC_PLACES,
        index=rec_place_idx if has_context else 0,
    )
with col2:
    mood = st.selectbox(
        "情绪", MUSIC_MOODS,
        index=rec_mood_idx if has_context else 0,
    )

# ── 播放 ──
audio_url = get_audio_url(place, mood)
chinese_name = f"{place}_{mood}.mp3"

st.markdown(f"""
<div class="card" style="text-align:center;">
    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎶</div>
    <h3>{place} · {mood}</h3>
    <p style="font-size: 0.8rem; color: #8b7355;">v6.4 精确提示词 (300+ 字 9 要素)</p>
</div>
""", unsafe_allow_html=True)

if audio_url:
    st.audio(audio_url, format="audio/mp3")
    st.markdown(f"[📥 下载音乐]({audio_url})")
else:
    st.warning("音乐加载失败，请检查网络后重试。")

# ── 所有音乐列表 ──
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding: 1rem;">
    <p style="font-size: 0.9rem; color: #d4c5a9;">🎼 所有音乐</p>
</div>
""", unsafe_allow_html=True)

for scene in MUSIC_PLACES:
    with st.expander(f"🎋 {scene}", expanded=False):
        for emotion in MUSIC_MOODS:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"  {emotion}")
            with col2:
                url = get_audio_url(scene, emotion)
                if url:
                    st.audio(url, format="audio/mp3")
