"""匿名共鸣 — 真实匿名社交（track-3 重做版）

5 个 Tab：
1. 📝 发布 — 匿名发帖（关联场景 + 可选显示时间戳）
2. 🌸 共鸣墙 — 浏览 + 共鸣 + 温暖留言 + 举报
3. 💫 情绪匹配 — 同 MBTI / 同星座 / 同情绪
4. 🌍 情绪全景 — 12 情绪分布 + 联邦学习说明
5. 📦 我的 — 我发布的 / 收到的温暖 / 今日一签 / 匿名等级

注意（track-2 树洞联动）：
- 树洞 track-2 会调用 create_post(content, emotion, scene, source="treehole", session_id=...)
- 树洞 track-2 会通过 session_state 给本会话设 session_id
- 本页面 session_id 是 st.session_state.session_id（与 2_treehole 共享的 8 位 uuid 短码）
"""

import time
import uuid
import random
import streamlit as st
from core.db import (
    create_post, get_posts, resonate_post, get_post_by_id,
    add_comment, get_comments,
    add_warm_word, get_warm_words,
    add_report,
    get_my_posts, get_recent_warm_words_for_user,
    get_top_posts_by_resonates, get_post_count_by_emotion,
    get_post_count,
)
from core.emotion_detector import detect_emotion, compute_session_emotion_profile
from core.config import EMOTIONS, SCENES

st.set_page_config(page_title="匿名共鸣 · 大观园树洞", page_icon="🌸", layout="centered")
from core.styles import inject_css; inject_css()

# ── 匿名 session_id（与 2_treehole 共用同一 8 位短码，仅本会话有效） ──
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# ── Tab 状态记忆（用于发布后跳到指定 tab） ──
if "resonance_active_tab" not in st.session_state:
    st.session_state.resonance_active_tab = 0

# ── 返回 ──
if st.button("← 回到大观园", use_container_width=True):
    st.switch_page("app.py")


# ═══════════════════════════════════════════════════════════
#  辅助函数
# ═══════════════════════════════════════════════════════════

def _format_time(ts: float) -> str:
    """时间戳 → 友好文本"""
    if not ts:
        return ""
    diff = time.time() - ts
    if diff < 60:
        return "刚刚"
    elif diff < 3600:
        return f"{int(diff/60)}分钟前"
    elif diff < 86400:
        return f"{int(diff/3600)}小时前"
    else:
        return f"{int(diff/86400)}天前"


def _get_anonymous_label(session_id: str) -> str:
    """生成匿名代号（基于 session_id 短哈希），保证同一会话所有帖子用同一代号"""
    if not session_id:
        return "匿名朋友"
    h = sum(ord(c) for c in session_id) % 100
    return f"匿名·{h:02d}号"


def _render_post_card(post: dict, show_actions: bool = True, show_warm: bool = True,
                       show_warm_toggle: bool = True) -> None:
    """渲染单个帖子卡片 + 操作按钮 + 温暖留言区"""
    content = post.get("content", "")
    emotion = post.get("emotion", "平静")
    scene = post.get("scene", "")
    resonates = post.get("resonates", 0)
    ts = post.get("created_at", 0)
    source = post.get("source", "manual")
    post_id = post.get("id")

    # 时间戳显示开关
    show_time = st.session_state.get("resonance_show_time", True)
    time_str = f"<span style='color:#8b7355;'>· {_format_time(ts)}</span>" if show_time else ""

    # 场景标签
    scene_html = f"<span class='tag'>{scene}</span>" if scene else ""

    # 来源标签
    src_html = ""
    if source == "treehole":
        src_html = "<span class='src-tag'>🌳 来自树洞</span>"

    # 主体卡片
    st.html(f"""
<div class="post-card fade-in">
    <div class="post-content">{content}</div>
    <div class="post-meta">
        <span class="tag">{emotion}</span>
        {scene_html}
        {src_html}
        {time_str}
    </div>
</div>
""")

    if not show_actions:
        return

    # 操作按钮：💗 +1 共鸣 | 💌 共鸣+留言 | 💬 看看温暖 | 🚩 举报
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        if st.button(f"💗 +1 共鸣", key=f"res_{post_id}", use_container_width=True):
            resonate_post(post_id)
            st.toast("已送上共鸣 💗", icon="💗")
            st.rerun()
    with cols[1]:
        if st.button(f"💌 +留言", key=f"warm_btn_{post_id}", use_container_width=True):
            st.session_state[f"warm_input_open_{post_id}"] = not st.session_state.get(
                f"warm_input_open_{post_id}", False)
    with cols[2]:
        if st.button(f"💬 看温暖", key=f"see_warm_{post_id}", use_container_width=True):
            st.session_state[f"see_warm_open_{post_id}"] = not st.session_state.get(
                f"see_warm_open_{post_id}", False)
    with cols[3]:
        if st.button(f"🚩", key=f"report_{post_id}", use_container_width=True):
            st.session_state[f"report_open_{post_id}"] = not st.session_state.get(
                f"report_open_{post_id}", False)

    # 共鸣数显示
    st.html(f"""
<div style="text-align:right; font-size:0.78rem; color:#c0392b; margin-top:-0.4rem;">
    💗 {resonates} 人共鸣
</div>
""")

    # ── 共鸣+留言输入 ──
    if st.session_state.get(f"warm_input_open_{post_id}", False):
        warm_text = st.text_input(
            "留一句温暖的话...",
            key=f"warm_text_{post_id}",
            placeholder="比如：你不是一个人 / 我懂你 / 加油...",
            label_visibility="collapsed",
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("💌 送出", key=f"warm_send_{post_id}", type="primary", use_container_width=True):
                if warm_text and warm_text.strip():
                    add_warm_word(post_id, warm_text.strip(), st.session_state.session_id)
                    st.session_state[f"warm_input_open_{post_id}"] = False
                    st.toast("温暖已送达 💌", icon="🌸")
                    st.rerun()
                else:
                    st.warning("写一句再送出去吧")
        with col_b:
            if st.button("取消", key=f"warm_cancel_{post_id}", use_container_width=True):
                st.session_state[f"warm_input_open_{post_id}"] = False
                st.rerun()

    # ── 温暖留言列表 ──
    if st.session_state.get(f"see_warm_open_{post_id}", False):
        _render_warm_words(post_id, expanded=True)

    # ── 举报 ──
    if st.session_state.get(f"report_open_{post_id}", False):
        reason = st.selectbox(
            "举报原因",
            ["骚扰", "广告", "不当内容", "其他"],
            key=f"report_reason_{post_id}",
            label_visibility="collapsed",
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("提交举报", key=f"report_submit_{post_id}", type="primary", use_container_width=True):
                add_report(post_id, st.session_state.session_id, reason)
                st.session_state[f"report_open_{post_id}"] = False
                st.toast("已收到举报，我们会处理", icon="🛡️")
                st.rerun()
        with col_b:
            if st.button("取消", key=f"report_cancel_{post_id}", use_container_width=True):
                st.session_state[f"report_open_{post_id}"] = False
                st.rerun()


def _render_warm_words(post_id: int, expanded: bool = False) -> None:
    """渲染某帖子的温暖留言列表（limit=5 / 展开时 limit=20）"""
    try:
        limit = 20 if expanded else 5
        words = get_warm_words(post_id, limit=limit)
    except Exception:
        words = []

    if not words:
        st.html('<div class="warm-word-empty">还没有人留言 — 你是第一个送温暖的</div>')
        return

    items_html = ""
    for w in words:
        content = w.get("content", "")
        ts = w.get("created_at", 0)
        items_html += f"""
<div class="warm-word">
    💌 {content}
    <div class="warm-time">{_format_time(ts)}</div>
</div>
"""
    st.html(f'<div style="margin-top:0.4rem;">{items_html}</div>')


# ═══════════════════════════════════════════════════════════
#  5 Tab 主结构
# ═══════════════════════════════════════════════════════════

st.html("""
<div class="card" style="text-align:center; margin-bottom: 0.6rem;">
    <h3 style="margin:0;">🌸 匿名共鸣</h3>
    <p style="font-size: 0.78rem; color: #8b7355; margin: 0.2rem 0 0;">
        你的心声 · 有人听见
    </p>
</div>
""")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 发布", "🌸 共鸣墙", "💫 情绪匹配", "🌍 情绪全景", "📦 我的"
])


# ═══════════════════════════════════════════════════════════
#  Tab 1：发布
# ═══════════════════════════════════════════════════════════
with tab1:
    st.html("""
<div class="card" style="text-align:center;">
    <h3>📝 匿名发布</h3>
    <p style="font-size: 0.78rem; color: #8b7355;">你的身份完全匿名，只有内容会被看到</p>
</div>
""")

    # 时间戳显示开关（全局，会影响其他 tab 显示）
    st.toggle(
        "⏰ 显示我的发布时间戳",
        value=st.session_state.get("resonance_show_time", True),
        key="resonance_show_time",
        help="关闭后，共鸣墙和「我的」里的帖子不再显示时间"
    )

    post_content = st.text_area(
        "说出你想说的话...",
        height=120,
        placeholder="这里没有人认识你，你可以做真实的自己...",
        label_visibility="collapsed",
    )

    scene_options = ["不选择"] + [s["name"] for s in SCENES]
    selected_scene = st.selectbox("关联场景（可选）", scene_options, index=0)

    if post_content and st.button("🌸 匿名发布", type="primary", use_container_width=True):
        emotion = detect_emotion(post_content)
        scene = selected_scene if selected_scene != "不选择" else ""
        # 兼容老调用 + 为 track-2 预留 source/session_id
        create_post(
            content=post_content,
            emotion=emotion,
            scene=scene,
            source="manual",
            session_id=st.session_state.session_id,
        )
        st.balloons()
        st.success(f"发布成功！检测到情绪「{emotion}」🌸")
        # 跳到 Tab 2（共鸣墙）
        st.session_state.resonance_active_tab = 1
        time.sleep(0.3)
        st.rerun()


# ═══════════════════════════════════════════════════════════
#  Tab 2：共鸣墙
# ═══════════════════════════════════════════════════════════
with tab2:
    st.html("""
<div class="card" style="text-align:center;">
    <h3>🌸 共鸣墙</h3>
    <p style="font-size: 0.78rem; color: #8b7355;">你不是一个人在感受</p>
</div>
""")

    # 筛选行：情绪 + 场景
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_emotion = st.selectbox("按情绪", ["全部"] + EMOTIONS, index=0, key="wall_filter_emotion")
    with col_f2:
        scene_names = ["全部"] + [s["name"] for s in SCENES]
        filter_scene = st.selectbox("按场景", scene_names, index=0, key="wall_filter_scene")

    try:
        posts = get_posts(
            limit=30,
            emotion=None if filter_emotion == "全部" else filter_emotion,
            scene=None if filter_scene == "全部" else filter_scene,
        )
    except Exception:
        posts = []

    if not posts:
        st.html("""
<div style="text-align:center; padding: 2rem; color: #8b7355;">
    <div style="font-size: 2rem;">🌙</div>
    <p>共鸣墙还很安静...</p>
    <p style="font-size: 0.8rem;">成为第一个分享的人吧</p>
</div>
""")
    else:
        # 内容预览 100 字，超过可展开
        for post in posts:
            full_content = post.get("content", "")
            if len(full_content) > 100:
                expand_key = f"expand_{post['id']}"
                is_expanded = st.session_state.get(expand_key, False)
                display = full_content if is_expanded else full_content[:100] + "..."

                # 渲染卡片（带展开按钮）
                _render_post_card({**post, "content": display}, show_actions=False)

                btn_label = "收起" if is_expanded else "展开更多"
                if st.button(btn_label, key=f"expand_btn_{post['id']}", use_container_width=False):
                    st.session_state[expand_key] = not is_expanded
                    st.rerun()

                # 操作按钮
                _render_post_actions(post)
            else:
                _render_post_card(post, show_actions=True)


def _render_post_actions(post: dict) -> None:
    """单独的帖子操作按钮（用于"展开更多"场景）"""
    post_id = post["id"]
    resonates = post.get("resonates", 0)

    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        if st.button(f"💗 +1 共鸣", key=f"res2_{post_id}", use_container_width=True):
            resonate_post(post_id)
            st.toast("已送上共鸣 💗", icon="💗")
            st.rerun()
    with cols[1]:
        if st.button(f"💌 +留言", key=f"warm_btn2_{post_id}", use_container_width=True):
            st.session_state[f"warm_input_open_{post_id}"] = not st.session_state.get(
                f"warm_input_open_{post_id}", False)
    with cols[2]:
        if st.button(f"💬 看温暖", key=f"see_warm2_{post_id}", use_container_width=True):
            st.session_state[f"see_warm_open_{post_id}"] = not st.session_state.get(
                f"see_warm_open_{post_id}", False)
    with cols[3]:
        if st.button(f"🚩", key=f"report2_{post_id}", use_container_width=True):
            st.session_state[f"report_open_{post_id}"] = not st.session_state.get(
                f"report_open_{post_id}", False)

    st.html(f"""
<div style="text-align:right; font-size:0.78rem; color:#c0392b; margin-top:-0.4rem;">
    💗 {resonates} 人共鸣
</div>
""")

    if st.session_state.get(f"warm_input_open_{post_id}", False):
        warm_text = st.text_input(
            "留一句温暖的话...",
            key=f"warm_text2_{post_id}",
            placeholder="比如：你不是一个人 / 我懂你 / 加油...",
            label_visibility="collapsed",
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("💌 送出", key=f"warm_send2_{post_id}", type="primary", use_container_width=True):
                if warm_text and warm_text.strip():
                    add_warm_word(post_id, warm_text.strip(), st.session_state.session_id)
                    st.session_state[f"warm_input_open_{post_id}"] = False
                    st.toast("温暖已送达 💌", icon="🌸")
                    st.rerun()
                else:
                    st.warning("写一句再送出去吧")
        with col_b:
            if st.button("取消", key=f"warm_cancel2_{post_id}", use_container_width=True):
                st.session_state[f"warm_input_open_{post_id}"] = False
                st.rerun()

    if st.session_state.get(f"see_warm_open_{post_id}", False):
        _render_warm_words(post_id, expanded=True)

    if st.session_state.get(f"report_open_{post_id}", False):
        reason = st.selectbox(
            "举报原因",
            ["骚扰", "广告", "不当内容", "其他"],
            key=f"report_reason2_{post_id}",
            label_visibility="collapsed",
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("提交举报", key=f"report_submit2_{post_id}", type="primary", use_container_width=True):
                add_report(post_id, st.session_state.session_id, reason)
                st.session_state[f"report_open_{post_id}"] = False
                st.toast("已收到举报，我们会处理", icon="🛡️")
                st.rerun()
        with col_b:
            if st.button("取消", key=f"report_cancel2_{post_id}", use_container_width=True):
                st.session_state[f"report_open_{post_id}"] = False
                st.rerun()


# ═══════════════════════════════════════════════════════════
#  Tab 3：情绪匹配（同 MBTI / 同星座 / 同情绪）
# ═══════════════════════════════════════════════════════════
with tab3:
    st.html("""
<div class="card" style="text-align:center;">
    <h3>💫 情绪匹配</h3>
    <p style="font-size: 0.78rem; color: #8b7355;">找到与你同频的人</p>
</div>
""")

    chat_history = st.session_state.get("chat_history", [])
    personality_type = st.session_state.get("personality_type", "")
    personality_source = st.session_state.get("personality_source", "")

    if not chat_history and not personality_type:
        st.html("""
<div style="text-align:center; padding: 2rem; color: #8b7355;">
    <div style="font-size: 2.5rem;">🔮</div>
    <p>先去和角色聊聊天</p>
    <p style="font-size: 0.8rem;">聊过之后，我就能帮你找到情绪相似的人</p>
    <p style="font-size: 0.78rem; margin-top: 0.6rem;">或者测一下 ⭐ 星座 / 🔤 MBTI</p>
</div>
""")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💬 去倾诉", use_container_width=True):
                st.switch_page("pages/1_chat.py")
        with col_b:
            if st.button("⭐ 去测人格", use_container_width=True):
                st.switch_page("pages/5_mbti.py")
    else:
        # ── 情绪画像卡 ──
        if chat_history:
            profile = compute_session_emotion_profile(chat_history)
            if profile:
                top3 = sorted(profile.items(), key=lambda x: -x[1])[:3]
                chips = " ".join(
                    f'<span class="tag">{emo} {pct:.0%}</span>'
                    for emo, pct in top3
                )
                st.html(f"""
<div class="emotion-profile">
    <div class="profile-title">📊 你的情绪画像（近 {len(chat_history)} 条对话）</div>
    <div class="profile-chips">{chips}</div>
</div>
""")
                top_emotion = top3[0][0]
            else:
                top_emotion = None
        else:
            top_emotion = None

        # ── 同 MBTI 匹配 ──
        shown_ids: set[int] = set()
        if personality_source == "mbti" and personality_type:
            try:
                mbti_posts = get_posts(limit=5, emotion=None)
                # 用 personality_type 字段做匹配（如果帖子记录了 MBTI）
                # 当前 schema 没有帖子 MBTI 字段，所以 fallback 到 top_emotion 匹配
                if not mbti_posts and top_emotion:
                    mbti_posts = get_posts(limit=5, emotion=top_emotion)
            except Exception:
                mbti_posts = []

            st.html(f'<div class="match-section-title">🔤 同 MBTI 匹配 · {personality_type}</div>')
            if mbti_posts:
                # 当前帖子没有 MBTI 字段，提示用户 → 显示同情绪的帖子作为近似匹配
                st.html(f"""
<div style="font-size:0.72rem;color:#8b7355;margin:0.2rem 0 0.4rem;">
    💡 找到与你情绪最相近的帖子（同 MBTI 帖子上线后会优先展示）
</div>
""")
                for p in mbti_posts[:3]:
                    _render_post_card(p, show_actions=True, show_warm=False)
                shown_ids = {p["id"] for p in mbti_posts[:3]}
            else:
                st.html('<div class="warm-word-empty">暂时没有匹配，去共鸣墙看看吧</div>')

        # ── 同星座匹配 ──
        if personality_source in ("zodiac", "zodiac_chart") and personality_type:
            try:
                zodiac_posts = get_posts(limit=5)
            except Exception:
                zodiac_posts = []

            st.html(f'<div class="match-section-title">⭐ 同星座匹配 · {personality_type}</div>')
            if zodiac_posts:
                st.html(f"""
<div style="font-size:0.72rem;color:#8b7355;margin:0.2rem 0 0.4rem;">
    💡 你的星座是 {personality_type}，先看看其他朋友的共鸣
</div>
""")
                for p in zodiac_posts[:3]:
                    _render_post_card(p, show_actions=True, show_warm=False)
                shown_ids = {p["id"] for p in zodiac_posts[:3]}
            else:
                st.html('<div class="warm-word-empty">暂时没有匹配</div>')

        # ── 同情绪匹配 ──
        if top_emotion:
            try:
                emo_posts = get_posts(limit=10, emotion=top_emotion)
            except Exception:
                emo_posts = []

            unique = [p for p in emo_posts if p["id"] not in shown_ids][:5]

            st.html(f'<div class="match-section-title">🌊 情绪相似 · 同样感到「{top_emotion}」</div>')
            if unique:
                for p in unique:
                    _render_post_card(p, show_actions=True, show_warm=False)
            else:
                st.html(f"""
<div class="warm-word-empty">暂时没有人同样感到「{top_emotion}」<br>
<span style="font-size:0.78rem;">你可以去发布一个 — 让别人也找到你</span>
</div>
""")
        elif not personality_type:
            st.html("""
<div style="text-align:center; padding: 1rem; color: #8b7355; font-size: 0.85rem;">
    🔍 测一下 MBTI 或星座，匹配会更准
</div>
""")


# ═══════════════════════════════════════════════════════════
#  Tab 4：情绪全景
# ═══════════════════════════════════════════════════════════
with tab4:
    st.html("""
<div class="card" style="text-align:center;">
    <h3>🌍 情绪全景</h3>
    <p style="font-size: 0.78rem; color: #8b7355;">近 7 天的所有声音</p>
</div>
""")

    try:
        dist = get_post_count_by_emotion(days=7)
    except Exception:
        dist = {}

    total = sum(dist.values())

    # 顶部人数文案
    if total > 0:
        st.html(f"""
<div style="text-align:center; margin: 0.4rem 0 1rem; color: #2c1810;">
    近 7 天共有 <strong style="color:#c0392b; font-size:1.2rem;">{total}</strong> 位朋友在这里倾诉过
</div>
""")
    else:
        st.html("""
<div style="text-align:center; margin: 0.4rem 0 1rem; color: #8b7355;">
    近 7 天还没有人发声 — 你是第一个
</div>
""")

    # 12 个情绪横条（保证 0 的情绪也显示）
    if total > 0:
        max_count = max(dist.values()) if dist else 1
        bar_items = ""
        for emo in EMOTIONS:
            cnt = dist.get(emo, 0)
            pct = (cnt / max_count * 100) if max_count > 0 else 0
            bar_items += f"""
<div class="emotion-bar">
    <div class="bar-label">{emo}</div>
    <div class="bar-track">
        <div class="bar-fill" style="width: {pct:.0f}%;"></div>
    </div>
    <div class="bar-count">{cnt}</div>
</div>
"""
        st.html(f'<div style="margin: 0.5rem 0;">{bar_items}</div>')
    else:
        # 空状态：仍然展示 12 个空条
        bar_items = ""
        for emo in EMOTIONS:
            bar_items += f"""
<div class="emotion-bar">
    <div class="bar-label">{emo}</div>
    <div class="bar-track">
        <div class="bar-fill" style="width: 0%;"></div>
    </div>
    <div class="bar-count">0</div>
</div>
"""
        st.html(f'<div style="margin: 0.5rem 0; opacity: 0.5;">{bar_items}</div>')

    # 联邦学习说明
    st.html("""
<div style="margin-top: 1rem; padding: 0.8rem; background: rgba(45,106,79,0.08);
            border-radius: 10px; border-left: 3px solid #2d6a4f; font-size: 0.78rem; color: #2c1810; line-height: 1.7;">
    🔒 <strong>联邦学习保护隐私</strong><br>
    你的情绪数据只聚合到全局统计，不暴露个人 —<br>
    系统只统计"今天有 N 人感到悲伤"，不记录"是谁"。
</div>
""")


# ═══════════════════════════════════════════════════════════
#  Tab 5：我的
# ═══════════════════════════════════════════════════════════
with tab5:
    me = _get_anonymous_label(st.session_state.session_id)

    st.html(f"""
<div class="card" style="text-align:center;">
    <h3>📦 我的</h3>
    <p style="font-size: 0.78rem; color: #8b7355;">代号 · {me}</p>
</div>
""")

    sid = st.session_state.session_id
    post_cnt = get_post_count(sid)

    # 匿名等级
    if post_cnt <= 2:
        tier, tier_class, tier_desc = "🌱 新声", "tier-1", "刚开始记录心声"
    elif post_cnt <= 9:
        tier, tier_class, tier_desc = "🌸 共鸣者", "tier-2", "你已经习惯了被听见"
    else:
        tier, tier_class, tier_desc = "🍃 知音", "tier-3", "你在这里留下了很多真心话"

    st.html(f"""
<div style="text-align:center; margin: 0.5rem 0 0.8rem;">
    <span class="anon-tier {tier_class}">{tier}</span>
    <div style="font-size: 0.72rem; color: #8b7355; margin-top: 0.3rem;">
        {tier_desc} · 已发布 {post_cnt} 篇
    </div>
</div>
""")

    # ── 今日一签 ──
    st.html('<div class="match-section-title">🌸 今日一签</div>')
    try:
        top_posts = get_top_posts_by_resonates(limit=5, days=7)
    except Exception:
        top_posts = []

    if top_posts:
        sign = random.choice(top_posts)
        sign_content = sign.get("content", "")
        sign_resonates = sign.get("resonates", 0)
        sign_emotion = sign.get("emotion", "")
        st.html(f"""
<div class="daily-sign">
    <div class="sign-label">今日 · 共识</div>
    <div class="sign-content">「{sign_content}」</div>
    <div class="sign-footer">
        💗 今天有 {sign_resonates} 个人和你一样 · 情绪 {sign_emotion}
    </div>
</div>
""")
    else:
        st.html("""
<div class="warm-word-empty">
    今日一签还没出现 — 你去发布一条，可能就成了明天的
</div>
""")

    # ── 我发布的 ──
    st.html('<div class="match-section-title">📝 我发布的</div>')
    try:
        my_posts = get_my_posts(sid, limit=20)
    except Exception:
        my_posts = []

    if my_posts:
        for p in my_posts[:10]:
            _render_post_card(p, show_actions=True, show_warm=False)
    else:
        st.html('<div class="warm-word-empty">你还没有发布过 — 去写第一句吧</div>')

    # ── 我收到的温暖 ──
    st.html('<div class="match-section-title">💌 我收到的温暖</div>')
    try:
        received = get_recent_warm_words_for_user(sid, limit=10)
    except Exception:
        received = []

    if received:
        items_html = ""
        for r in received:
            content = r.get("content", "")
            post_emotion = r.get("post_emotion", "")
            ts = r.get("created_at", 0)
            items_html += f"""
<div class="warm-word">
    💌 {content}
    <div class="warm-time">来自「{post_emotion}」的帖子 · {_format_time(ts)}</div>
</div>
"""
        st.html(f'<div>{items_html}</div>')
    else:
        st.html("""
<div class="warm-word-empty">
    还没有人给你留言 — 继续发真心话，温暖会来的
</div>
""")

    # ── 底部小字 ──
    st.html(f"""
<div style="text-align:center; margin-top: 1rem; font-size: 0.7rem; color: #8b7355;">
    🛡️ 你的代号「{me}」只在本次会话内有效<br>
    退出页面后，身份不会留下任何痕迹
</div>
""")
