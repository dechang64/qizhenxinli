"""祺臻心理 — 咨询师后台 hub (v0.1 demo)

最简 1 周实现:
- 列出待处理案例 (mock 3 条)
- 排班状态 (mock)
- 跨社区预约 (单一社区 mock)
- 危机预警列表 (mock)

复用 dgy-treehole 的 session_state + styles + db
"""
import streamlit as st
from datetime import datetime, timedelta
from core.styles import inject_css

st.set_page_config(
    page_title="咨询师后台 · 祺臻心理",
    page_icon="🧑‍⚕️",
    layout="wide",
)
inject_css()

# ── 顶部返回 ──
if st.button("← 回到祺臻心理", use_container_width=True):
    st.switch_page("app.py")

st.markdown("""
<div class="card-dark" style="text-align:center; padding: 1.5rem;">
    <div style="font-size: 2.5rem;">🧑‍⚕️</div>
    <h2 style="margin: 0.5rem 0;">咨询师后台</h2>
    <p style="font-size: 0.85rem; color: #d4c5a9;">v0.1 demo · 多社区协同</p>
</div>
""", unsafe_allow_html=True)

# ── 顶部 3 个 KPI 卡片 ──
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("今日案例", "12", delta="+3 较昨日")
with col2:
    st.metric("跨社区预约", "4", delta="+1")
with col3:
    st.metric("待处理危机", "1", delta="🚨")

st.markdown("---")

# ── 当前咨询师身份 (v0.1 mock) ──
if "counselor" not in st.session_state:
    st.session_state.counselor = {
        "name": "X 老师",
        "id": "DR-001",
        "community": "社区A · 苏州工业园",
        "today_slots": ["09:00", "11:00", "14:00", "16:00"],
    }

counselor = st.session_state.counselor

# ── 左: 今日待办 ──
st.markdown("### 📋 今日待办")

todos = [
    {"time": "10:00", "community": "A", "type": "现场", "user": "张*", "summary": "情绪低落 3 个月, 首次评估"},
    {"time": "14:30", "community": "B", "type": "视频", "user": "李*", "summary": "工作压力, 跨社区预约"},
    {"time": "16:00", "community": "A", "type": "现场", "user": "王**", "summary": "评估问卷得分高, 跟进"},
]

for t in todos:
    badge_color = {"A": "#d4a574", "B": "#9bbf65"}.get(t["community"], "#888")
    st.markdown(f"""
<div class="card" style="margin-bottom: 0.6rem; border-left: 3px solid {badge_color};">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <span style="font-size:1rem;">⏰ {t['time']}</span>
            <span style="margin-left:0.5rem;font-size:0.8rem;color:#8b7355;">社区 {t['community']} · {t['type']}</span>
        </div>
        <div style="font-size:0.85rem;color:#666;">{t['user']}</div>
    </div>
    <div style="margin-top:0.5rem;font-size:0.95rem;">{t['summary']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 中: 危机预警 (mock) ──
st.markdown("### 🚨 危机预警 (实时)")

if st.session_state.get("crisis_pending", False):
    st.error("""
    **🚨 紧急 — 社区 C 设备检测到危机关键词**

    时间: 刚刚
    检测词: "我不想活了"
    设备: 社区 C 大屏 #03

    **推荐动作**: 1) 主动远程接管  2) 转介热线 12320-5  3) 联系家属
    """)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📞 远程接管", use_container_width=True):
            st.success("正在接通...")
    with c2:
        if st.button("☎️ 转介热线", use_container_width=True):
            st.info("12320-5 已发送")
    with c3:
        if st.button("✋ 联系家属", use_container_width=True):
            st.warning("需用户已授权家属联系方式")
else:
    st.success("✅ 当前无活跃危机事件")

# ── 右: 多社区数据 ──
st.markdown("### 📊 多社区实时数据")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
<div class="card">
    <h4 style="color:#d4a574;margin:0 0 0.5rem 0;">📍 社区 A · 苏州工业园</h4>
    <div style="display:flex;gap:1rem;font-size:0.85rem;">
        <div>👥 活跃 3</div>
        <div>📅 今日预约 8</div>
        <div>📊 利用率 67%</div>
    </div>
    <div style="font-size:0.75rem;color:#8b7355;margin-top:0.5rem;">心跳: 12s 前</div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="card">
    <h4 style="color:#9bbf65;margin:0 0 0.5rem 0;">📍 社区 B · 姑苏区</h4>
    <div style="display:flex;gap:1rem;font-size:0.85rem;">
        <div>👥 活跃 2</div>
        <div>📅 今日预约 5</div>
        <div>📊 利用率 42%</div>
    </div>
    <div style="font-size:0.75rem;color:#8b7355;margin-top:0.5rem;">心跳: 8s 前</div>
</div>
""", unsafe_allow_html=True)

# ── 测试按钮 (demo 触发危机) ──
st.markdown("---")
st.caption("demo 功能 · 仅测试用")
if st.button("🧪 模拟接收危机广播 (测试)", use_container_width=False):
    st.session_state.crisis_pending = True
    st.rerun()

if st.button("🧹 清除危机状态", use_container_width=False):
    st.session_state.crisis_pending = False
    st.rerun()
