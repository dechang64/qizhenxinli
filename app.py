"""祺臻心理 v0.1 — 主入口

社区心理咨询前台网络 (多社区协同版, 由 dgy-treehole v6.4 复用)
基于 Streamlit + AMAX AI + Flask
"""

import streamlit as st
from core.config import SCENES, EMOTION_SCENE_MAP, SCENE_MAP
from core.db import init_db
from core.styles import inject_css

# ── 初始化数据库（建表，幂等）──
init_db()

# ── 页面配置（必须是第一个 st 命令）──
st.set_page_config(
    page_title="祺臻心理",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── 注入全局 CSS（在 set_page_config 之后）──
inject_css()

# ── 中文 sidebar nav (覆盖 streamlit 默认英文文件名) ──
with st.sidebar:
    st.markdown("### 💎 祺臻心理")
    st.page_link("app.py", label="🏠 主页")
    st.page_link("pages/community_hub.py", label="🧑‍⚕️ 咨询师后台")
    st.page_link("pages/crisis_alert.py", label="🚨 危机处置")
    st.markdown("---")
    st.caption("v0.1 demo · 多社区协同")

    # ── (旧) dgy-treehole pages 暂时保留代码, 但不进 sidebar ──
    with st.expander("🧪 实验功能 (复用 dgy-treehole)", expanded=False):
        st.caption("以下功能由 dgy-treehole 复用, v0.1 不进主流程")
        st.page_link("pages/1_chat.py", label="💬 实验聊天")
        st.page_link("pages/2_treehole.py", label="🌳 实验树洞")
        st.page_link("pages/3_resonance.py", label="🌸 实验共鸣")
        st.page_link("pages/4_music.py", label="🎵 实验音乐")

# ═══════════════════════════════════════════════════════════
#  🎬 区块 1：Hero（沉浸式开场 + 1 个核心 CTA）
# ═══════════════════════════════════════════════════════════
st.html("""
<div class="home-hero fade-in">
    <div class="hero-eyebrow">QIZHEN · WELLNESS · NETWORK</div>
    <div class="hero-title">祺臻心理</div>
    <div class="hero-sub">在这里，你可以放下所有防备</div>
    <div class="hero-motto">"祺心相伴，臻于至善。"</div>
</div>
""")

# 主 CTA：进入树洞（这是新用户最高频动作）
if st.button("🌳  进入树洞，写下心事", key="hero_cta_treehole", type="primary", use_container_width=True):
    st.session_state.current_scene = "潇湘馆"
    st.session_state.chat_character = "林黛玉"
    st.session_state.chat_history = []
    st.switch_page("pages/2_treehole.py")

st.html("""
<div style="text-align:center; margin: 0.4rem 0 0.2rem;">
    <span class="badge">🔒 匿名安全 · 不留痕迹 · 随时离开</span>
</div>
""")

# ═══════════════════════════════════════════════════════════
#  🧭 区块 2：7 个功能导航 — 用 st.pills（mobile-native，inline 元素）
# ═══════════════════════════════════════════════════════════
st.html("""
<div class="home-section">
    <div class="section-header">
        <span class="section-icon">🧭</span>
        <span class="section-title-main">去任何地方</span>
        <span class="section-title-sub">7 个功能区，随点随到</span>
    </div>
</div>
""")

# 用 st.pills 渲染 — Streamlit 1.40+ 重新 expose，自带响应式
# 选中后存到 st.session_state，模块末尾统一 switch_page
nav_items = [
    ("💬 倾诉", "1_chat"),
    ("🌳 树洞", "2_treehole"),
    ("🌸 共鸣", "3_resonance"),
    ("🎵 音乐", "4_music"),
    ("🔮 MBTI 人格", "5_mbti"),
    ("⭐ 星图", "7_zodiac"),
    ("📊 洞察", "6_insight"),
]
nav_labels = [f"{l}" for l, _ in nav_items]
nav_target = st.pills(
    label=" ",
    options=nav_labels,
    key="nav_pills",
    label_visibility="collapsed",
)

# ═══════════════════════════════════════════════════════════
#  💭 区块 3：12 情绪快速入口 — st.pills multi
# ═══════════════════════════════════════════════════════════
st.html("""
<div class="home-section">
    <div class="section-header">
        <span class="section-icon">💭</span>
        <span class="section-title-main">心里装着什么？</span>
        <span class="section-title-sub">点一下，自动去对应的院落</span>
    </div>
</div>
""")

EMOTION_EMOJI = {
    "悲伤": "💧", "焦虑": "🌊", "愤怒": "🔥", "迷茫": "🌫️",
    "疲惫": "🍂", "孤独": "🌙", "平静": "🍃", "感恩": "🌸",
    "期待": "🌅", "执念": "⛓️", "委屈": "🌧️", "自卑": "🥀",
}
emotion_labels = [f"{EMOTION_EMOJI[k]} {k}" for k in EMOTION_EMOJI.keys()]
selected_emotion_label = st.pills(
    label=" ",
    options=emotion_labels,
    key="emotion_pills",
    label_visibility="collapsed",
)

# ═══════════════════════════════════════════════════════════
#  处理 nav / emotion 选中：跳转到对应 page
# ═══════════════════════════════════════════════════════════
if nav_target:
    # 找到对应 page
    for label, page in nav_items:
        if label == nav_target:
            # 树洞/共鸣等页有自己的初始化逻辑，这里只切页面
            if page == "2_树洞":
                st.session_state.current_scene = "潇湘馆"
                st.session_state.chat_character = "林黛玉"
                st.session_state.chat_history = []
            elif page == "1_chat":
                st.session_state.current_scene = "怡红院"
                st.session_state.chat_character = "贾宝玉"
                st.session_state.chat_history = []
            st.switch_page(f"pages/{page}.py")
            break

if selected_emotion_label:
    # 解析出情绪中文名（去掉 emoji 前缀）
    emo = selected_emotion_label.split(" ", 1)[1] if " " in selected_emotion_label else selected_emotion_label
    st.session_state.selected_emotion = emo
    if emo in EMOTION_SCENE_MAP:
        rec = EMOTION_SCENE_MAP[emo]
        st.session_state.current_scene = rec["scene"]
        scene_info = SCENE_MAP.get(rec["scene"], {})
        st.session_state.chat_character = scene_info.get("char", "贾宝玉")
    st.session_state.chat_history = []
    st.switch_page("pages/1_chat.py")

# ═══════════════════════════════════════════════════════════
#  🏯 区块 4：9 大院落 — st.pills（mobile-native，inline 元素）
# ═══════════════════════════════════════════════════════════
st.html("""
<div class="home-section">
    <div class="section-header">
        <span class="section-icon">🏯</span>
        <span class="section-title-main">9 大院落，等你入住</span>
        <span class="section-title-sub">6 处经典 + 栊翠庵/缀锦楼/紫菱洲</span>
    </div>
</div>
""")

scene_labels = [f"{s['icon']} {s['name']}" for s in SCENES]
selected_scene_label = st.pills(
    label=" ",
    options=scene_labels,
    key="scene_pills",
    label_visibility="collapsed",
)

if selected_scene_label:
    # 匹配选中的场景
    for s in SCENES:
        if selected_scene_label == f"{s['icon']} {s['name']}":
            st.session_state.current_scene = s["name"]
            st.session_state.chat_character = s["char"]
            st.session_state.chat_history = []
            st.switch_page("pages/1_chat.py")
            break

# ═══════════════════════════════════════════════════════════
#  🌸 区块 5：今日一签（AI 个性化 + 10 张固定兜底）
# ═══════════════════════════════════════════════════════════
import random
import hashlib
import datetime

# 10 张固定签（兜底用，质量有保证）
_FALLBACK_SIGNS = [
    ("黛玉", "花谢花飞花满天，红消香断有谁怜？", "把无法言说的哀愁，写成诗就轻了。"),
    ("宝玉", "任凭弱水三千，我只取一瓢饮。", "世间繁华三千，你只需守住心里那一瓢。"),
    ("宝钗", "好风凭借力，送我上青云。", "聪明不是算计，是顺势而为的从容。"),
    ("湘云", "幸生来，英豪阔大宽宏量。", "大大方方地活，纠结就少了大半。"),
    ("探春", "我但凡是个男人，可以出得去，我必早走了。", "清醒不是冷漠，是知道什么值得做。"),
    ("妙玉", "过洁世同嫌，至洁亦世所罕。", "放下执念不是妥协，是放过自己。"),
    ("惜春", "独卧青灯古佛旁，心如止水念无常。", "安静不是没有情绪，是懂得照顾自己。"),
    ("迎春", "金闺花柳质，一载赴黄粱。", "先抱住自己，世界才会温柔待你。"),
    ("李纨", "如冰水好空相妒，枉与他人作笑谈。", "生活的担子，放一放，没人怪你。"),
    ("凤姐", "凡事自有定数，何必空忙一场。", "精明之外，留一点温柔给自己。"),
]

def _pick_fallback_today() -> tuple[str, str, str, str]:
    """从 10 张固定签里按今天日期 hash 选一张（每天固定）"""
    today = datetime.date.today().isoformat()
    seed = hashlib.md5(today.encode()).hexdigest()
    return _FALLBACK_SIGNS[int(seed, 16) % len(_FALLBACK_SIGNS)] + ("fixed",)


def _generate_ai_sign(recent_emotion_dist: dict | None) -> tuple | None:
    """用 AMAX 生成一张个性化签。失败返回 None。"""
    try:
        from core.minimax_chat import chat as amax_chat
    except Exception:
        return None

    # 把情绪分布拼成自然语言
    if recent_emotion_dist:
        total = sum(recent_emotion_dist.values()) or 1
        top3 = sorted(recent_emotion_dist.items(), key=lambda x: -x[1])[:3]
        emo_desc = "、".join(f"{e} {round(c/total*100)}%" for e, c in top3)
        user_ctx = f"用户最近7天的情绪分布：{emo_desc}"
    else:
        user_ctx = "用户最近没有记录情绪，给一张通用安慰签"

    system_prompt = """你是红楼梦大观园中的一位人物。给今天写一张「今日一签」。

要求：
1. 先选一个最适合当下用户状态的红楼梦角色（黛玉/宝玉/宝钗/湘云/探春/妙玉/惜春/迎春/李纨/凤姐）
2. 写一句古风引言（5-15 字，可化用原书诗句，或自己写古风短句）
3. 写一句现代人解读（1 句话，把古意连接到当代人的情绪，给出温柔的洞察）
4. 严格按以下格式输出，3 行，不要任何其他文字：

角色名
古风引言
现代人解读"""

    user_prompt = f"今天是 {datetime.date.today().strftime('%Y年%m月%d日')}，{user_ctx}。请生成今日一签。"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        reply = amax_chat(
            messages=messages,
            character="林黛玉",
            personality_params=None,
            temperature=0.85,
            max_tokens=200,
        )

        if not reply or "AI 暂未连接" in reply or "服务暂不可用" in reply or "出了点小问题" in reply:
            return None

        lines = [ln.strip() for ln in reply.strip().split("\n") if ln.strip()]
        if len(lines) < 3:
            return None
        char, quote, remark = lines[0], lines[1], lines[2]
        valid_chars = {"黛玉", "宝玉", "宝钗", "湘云", "探春", "妙玉", "惜春", "迎春", "李纨", "凤姐"}
        if char not in valid_chars:
            for c in valid_chars:
                if c in char:
                    char = c
                    break
            else:
                return None
        return (char, quote, remark, "ai")
    except Exception as e:
        print(f"AI sign generation failed: {e}")
        return None


# === 每日一签主逻辑：AI 优先 + 固定兜底 + 缓存 ===
_today = datetime.date.today().isoformat()
if "daily_sign_cache_date" not in st.session_state or st.session_state.daily_sign_cache_date != _today:
    # 新的一天：尝试 AI 生成，失败兜底
    try:
        from core.db import get_emotion_distribution
        emo_dist = get_emotion_distribution(days=7)
    except Exception:
        emo_dist = None

    ai_sign = _generate_ai_sign(emo_dist)
    if ai_sign:
        _char, _quote, _remark, _source = ai_sign
    else:
        _char, _quote, _remark, _source = _pick_fallback_today()

    st.session_state.daily_sign_cache_date = _today
    st.session_state.daily_sign_data = (_char, _quote, _remark, _source)
else:
    _char, _quote, _remark, _source = st.session_state.daily_sign_data

_footer = "每天换一张 · 来自《红楼梦》" if _source == "fixed" else "今日专属 · AI 懂你"

st.html(f"""
<div class="home-section">
    <div class="daily-sign">
        <div class="sign-label">今 日 一 签</div>
        <div class="sign-content">
            <div style="font-size:0.78rem;color:#d4a574;margin-bottom:0.3rem;">— {_char} —</div>
            <div style="font-style:italic;margin-bottom:0.4rem;">「{_quote}」</div>
            <div style="color:#d4c5a9;font-size:0.82rem;">{_remark}</div>
        </div>
        <div class="sign-footer">{_footer}</div>
    </div>
</div>
""")

# ═══════════════════════════════════════════════════════════
#  📊 区块 6：底部信息
# ═══════════════════════════════════════════════════════════
st.html("""
<div class="home-footer">
    🌸 在这里，你不需要假装坚强 🌸<br>
    <span class="footer-tag">联邦学习保护你的隐私 · 你的话只属于你</span>
</div>
""")
