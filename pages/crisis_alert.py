"""祺臻心理 — 危机检测 + 处置 (v0.1 demo)

模拟设备侧"危机关键词触发"流程:
- 关键词检测 (mock)
- 转人工 (mock 远程接管)
- 24h 心理热线卡片
- 危机日志

复用 dgy-treehole 的 styles
"""
import streamlit as st
from core.styles import inject_css

st.set_page_config(
    page_title="危机处置 · 祺臻心理",
    page_icon="🚨",
    layout="centered",
)
inject_css()

# ── 顶部返回 ──
if st.button("← 回到祺臻心理", use_container_width=True):
    st.switch_page("app.py")

st.markdown("""
<div class="card-dark" style="text-align:center; padding: 1.5rem; border-left: 4px solid #dc3545;">
    <div style="font-size: 2.5rem;">🚨</div>
    <h2 style="margin: 0.5rem 0;">危机干预</h2>
    <p style="font-size: 0.85rem; color: #d4c5a9;">祺臻心理 v0.1 demo</p>
</div>
""", unsafe_allow_html=True)

# ── 演示场景 ──
st.markdown("## 📋 v0.1 demo · 危机关键词检测")

st.markdown("""
<div class="card" style="border-left:3px solid #dc3545;">
    <h4>🔍 系统检测到危机关键词</h4>
    <p style="color:#666;font-size:0.85rem;">检测位置: 社区 C 大屏 #03<br>
       检测词: <code>"我不想活了"</code> + <code>"太累了"</code> + <code>"没意义"</code><br>
       时间: 刚刚 (3 词命中 / 5 秒窗口)<br>
       置信度: <strong>0.92</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🎯 设备侧自动动作 (mock)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
<div class="card" style="text-align:center;">
    <div style="font-size:2rem;">⏸️</div>
    <h4 style="color:#d4a574;">暂停 AI</h4>
    <p style="font-size:0.8rem;color:#666;">暂停自由对话<br>切换到预设危机话术</p>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="card" style="text-align:center;">
    <div style="font-size:2rem;">📡</div>
    <h4 style="color:#d4a574;">广播云端</h4>
    <p style="font-size:0.8rem;color:#666;">全网络咨询师推送<br>督导专家推送</p>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="card" style="text-align:center;">
    <div style="font-size:2rem;">☎️</div>
    <h4 style="color:#d4a574;">转介热线</h4>
    <p style="font-size:0.8rem;color:#666;">12320-5 北京心理援助<br>一键直拨</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 📞 24h 心理援助热线 (mock)")

hotlines = [
    {"name": "12320-5", "desc": "北京心理援助热线", "color": "#dc3545"},
    {"name": "400-161-9995", "desc": "全国心理援助", "color": "#d4a574"},
    {"name": "010-82951332", "desc": "北京安定医院", "color": "#9bbf65"},
    {"name": "999", "desc": "医疗急救 (紧急)", "color": "#dc3545"},
]

for h in hotlines:
    st.markdown(f"""
<div class="card" style="border-left:3px solid {h['color']}; margin-bottom:0.5rem;">
    <div style="display:flex;justify-content:space-between;">
        <div>
            <strong style="font-size:1.1rem;">{h['name']}</strong>
            <span style="margin-left:0.5rem;color:#666;font-size:0.85rem;">{h['desc']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 🔬 危机关键词检测 (mock 输入测试)")

test_input = st.text_area(
    "输入测试文本 (demo 不会真上报):",
    value="我已经两周没睡觉了, 累得像行尸走肉, 真的不想活了",
    height=80,
)
if st.button("🔬 检测关键词", use_container_width=True):
    danger_words = ["不想活", "自杀", "了结", "没意义"]
    hits = [w for w in danger_words if w in test_input]
    if hits:
        st.error(f"🚨 命中关键词: {', '.join(hits)} · 置信度 0.92 → 触发危机流程")
    else:
        st.success("✅ 未检测到危机关键词")

st.caption("""
**MVP 实施提示**: 真实产品里
- 关键词 + 自研分类模型双触发
- 危机日志自动上传督导 + 区域经理
- 转介热线需法律 / 伦理委员会批准后才挂出
""")
