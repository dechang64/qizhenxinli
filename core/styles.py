"""共享 CSS — 所有页面通过 inject_css() 注入"""

CSS = """<style>
/* 隐藏 Streamlit 默认元素 */
#MainMenu, footer, header {visibility: hidden}
.block-container {padding-top: 0.5rem; padding-bottom: 2rem; max-width: 520px}

/* 全局字体 */
.stApp {font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', serif}

/* 卡片样式 */
.card {
    background: #f5f0e8;
    color: #2c1810;  /* 深棕文字, 配米色背景 (之前漏设, 默认米白色看不见) */
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    border: 1px solid #e8dfd0;
}
.card h3, .card h1, .card h2, .card p {
    color: #2c1810 !important;  /* 卡片内文字强制深色 */
}
.card-dark {
    background: #2c1810;
    color: #f5f0e8;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
}

/* 场景卡片 */
.scene-card {
    background: linear-gradient(135deg, #f5f0e8, #e8dfd0);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    border: 1px solid #d4c5a9;
    cursor: pointer;
    transition: all 0.3s;
}
.scene-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(44,24,16,0.12);
    border-color: #b8860b;
}

/* 聊天气泡 */
.chat-ai {
    background: #e8dfd0;
    border-radius: 16px 16px 16px 4px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    max-width: 85%;
}
.chat-user {
    background: #2c1810;
    color: #f5f0e8;
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    max-width: 85%;
    margin-left: auto;
}

/* 标签 */
.tag {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    background: rgba(184,134,11,0.1);
    color: #b8860b;
    border-radius: 99px;
    font-size: 0.8rem;
    margin: 0.15rem;
}

/* 模式指示器（已停用 — 演示模式不再展示给用户） */
/* .mock-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    background: rgba(192,57,43,0.1);
    color: #c0392b;
    border-radius: 99px;
    font-size: 0.7rem;
} */

/* Hero 头部 */
.hero {
    background: linear-gradient(135deg, #2c1810, #4a2c1a 50%, #3d1f0e);
    padding: 2.5rem 1.5rem 2rem;
    color: #f5f0e8;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 16px 16px;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(184,134,11,0.12), transparent 60%);
    pointer-events: none;
}
.hero h1 {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: 0.4rem;
    position: relative;
}
.hero .sub {
    opacity: 0.7;
    font-size: 0.85rem;
    margin: 0.4rem 0 0.8rem;
    position: relative;
}
.hero .motto {
    font-size: 0.8rem;
    opacity: 0.5;
    font-style: italic;
    position: relative;
}

/* 安全徽章 */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.8rem;
    background: rgba(45,106,79,0.1);
    color: #2d6a4f;
    border-radius: 99px;
    font-size: 0.75rem;
}

/* 结果卡片 */
.result-type {
    font-size: 2.5rem;
    font-weight: 800;
    color: #c0392b;
    text-align: center;
    letter-spacing: 0.3rem;
    margin: 0.5rem 0;
}
.result-desc {
    text-align: center;
    font-size: 0.9rem;
    color: #8b7355;
    margin-bottom: 0.8rem;
}
.result-scene {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e8dfd0;
    margin-bottom: 0.8rem;
}
.result-scene .icon {
    font-size: 2rem;
    width: 48px;
    text-align: center;
}
.result-scene .name {
    font-weight: 600;
    font-size: 0.95rem;
    color: #2c1810;
}
.result-scene .info {
    font-size: 0.8rem;
    color: #8b7355;
    margin-top: 0.1rem;
}
.result-reason {
    background: #f5f0e8;
    border-radius: 12px;
    padding: 0.8rem;
    margin: 0.8rem 0;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #2c1810;
}
.result-quote {
    text-align: center;
    font-style: italic;
    color: #8b7355;
    font-size: 0.85rem;
    padding: 0.8rem;
    border-left: 3px solid #b8860b;
    margin: 0.8rem 0;
}

/* 星座按钮 */
.zodiac-btn {
    background: #fff;
    border: 1px solid #e8dfd0;
    border-radius: 12px;
    padding: 0.6rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.zodiac-btn:hover {
    border-color: #b8860b;
    box-shadow: 0 4px 12px rgba(44,24,16,0.08);
}

/* 星盘卡片 */
.chart-planet {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.5rem 0.7rem;
    background: #fff;
    border-radius: 10px;
    margin: 0.3rem 0;
    border: 1px solid #e8dfd0;
}
.chart-planet .p-icon {
    font-size: 1.3rem;
    width: 32px;
    text-align: center;
    flex-shrink: 0;
}
.chart-planet .p-info { flex: 1; }
.chart-planet .p-name { font-size: 0.78rem; font-weight: 600; }
.chart-planet .p-sign { font-size: 0.7rem; color: #8b7355; }
.chart-planet .p-desc { font-size: 0.72rem; color: #2c1810; margin-top: 0.1rem; line-height: 1.5; }

/* 星盘总结 */
.chart-summary {
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    color: #f5f0e8;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.8rem 0;
    text-align: center;
}

/* 元素标签 */
.elem-label {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.3rem 0;
    margin-top: 0.5rem;
}

/* 动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.5s ease-out; }

/* ── 树洞页面树皮纹理背景 ── */
.treehole-body {
    position: relative;
}
/* 用伪元素叠加树皮纹理 */
.treehole-body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        /* 树皮竖纹 */
        repeating-linear-gradient(
            87deg,
            transparent 0px,
            transparent 18px,
            rgba(44,24,16,0.04) 18px,
            rgba(44,24,16,0.04) 20px,
            transparent 20px,
            transparent 48px
        ),
        /* 横向年轮纹理 */
        repeating-linear-gradient(
            0deg,
            transparent 0px,
            transparent 12px,
            rgba(44,24,16,0.025) 12px,
            rgba(44,24,16,0.025) 14px,
            transparent 14px,
            transparent 36px
        ),
        /* 整体暗角，让边缘更像树洞入口 */
        radial-gradient(
            ellipse at 50% 30%,
            transparent 20%,
            rgba(44,24,16,0.08) 100%
        );
    pointer-events: none;
    z-index: 0;
}
/* 确保内容在纹理之上 */
.treehole-body > * {
    position: relative;
    z-index: 1;
}

/* ── 静默释放模式动画 ── */
@keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(184,134,11,0.4); }
    70%  { box-shadow: 0 0 0 16px rgba(184,134,11,0); }
    100% { box-shadow: 0 0 0 0 rgba(184,134,11,0); }
}
.pulse-ring {
    animation: pulseRing 2s ease-out infinite;
    border-radius: 50%;
}
@keyframes gentleFloat {
    0%,100% { transform: translateY(0px); }
    50%       { transform: translateY(-8px); }
}
.gentle-float { animation: gentleFloat 3s ease-in-out infinite; }
@keyframes floatUp {
    0%,100% { transform: translateY(0px); }
    50%       { transform: translateY(-12px); }
}
.float { animation: floatUp 3s ease-in-out infinite; }

/* ── 树洞 Hero：古树内腔，从洞里看出去 ── */
.treehole-hero {
    position: relative;
    background:
        /* 顶部一道冷月白光（穿过树缝） */
        radial-gradient(
            ellipse 80% 30% at 50% 0%,
            rgba(255,245,220,0.18) 0%,
            rgba(255,245,220,0.05) 40%,
            transparent 70%
        ),
        /* 底部苔痕幽绿 */
        radial-gradient(
            ellipse 100% 50% at 50% 100%,
            rgba(45,106,79,0.25) 0%,
            transparent 60%
        ),
        /* 主体：深棕木心 */
        linear-gradient(180deg, #2c1810 0%, #1a0e08 50%, #0f0805 100%);
    color: #f5f0e8;
    padding: 2.5rem 1.5rem 2rem;
    text-align: center;
    border-radius: 0 0 24px 24px;
    margin-bottom: 1.2rem;
    overflow: hidden;
    box-shadow: inset 0 0 80px rgba(0,0,0,0.6);
}
/* 树洞内壁竖纹：模拟年轮+木纹 */
.treehole-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        repeating-linear-gradient(
            85deg,
            transparent 0px,
            transparent 14px,
            rgba(245,240,232,0.04) 14px,
            rgba(245,240,232,0.04) 16px
        ),
        radial-gradient(
            ellipse at 50% 50%,
            transparent 30%,
            rgba(0,0,0,0.4) 100%
        );
    pointer-events: none;
    z-index: 0;
}
.treehole-hero > * { position: relative; z-index: 1; }

.treehole-hero .moon {
    font-size: 2.8rem;
    filter: drop-shadow(0 0 18px rgba(255,235,180,0.6));
    display: block;
    margin-bottom: 0.4rem;
    animation: gentleFloat 4s ease-in-out infinite;
}

.treehole-hero h2 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.4rem;
    margin: 0.3rem 0 0.5rem;
    color: #f5f0e8;
}

.treehole-hero .sub {
    font-size: 0.88rem;
    color: #d4c5a9;
    letter-spacing: 0.1rem;
    margin: 0;
}

.treehole-hero .quote {
    margin-top: 1rem;
    font-size: 0.78rem;
    color: #8b7355;
    font-style: italic;
    letter-spacing: 0.05rem;
    opacity: 0.85;
}

/* 落叶飘入动画 */
@keyframes fallIn {
    0%   { transform: translateY(-30px) rotate(0deg); opacity: 0; }
    20%  { opacity: 1; }
    100% { transform: translateY(40px) rotate(180deg); opacity: 0; }
}
.falling-leaf {
    display: inline-block;
    animation: fallIn 5s ease-in-out infinite;
}
.falling-leaf:nth-child(2) { animation-delay: 1.5s; }
.falling-leaf:nth-child(3) { animation-delay: 3s; }

/* ── 场景卡片网格 ── */
.scene-card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin: 0.6rem 0;
}
@media (max-width: 768px) {
    .scene-card-grid {
        grid-template-columns: 1fr;
    }
}

/* 卡片可点视觉提示 */
.scene-card-clickable {
    cursor: pointer;
    transition: all 0.3s;
    margin-bottom: 0.3rem !important;
}
.scene-card-clickable:hover {
    border-color: #b8860b !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(44,24,16,0.12);
}

/* 场景卡片 + 按钮合并 — 按钮撑成完整卡片样式 */
.scene-card-grid [data-testid="stButton"] button {
    background: linear-gradient(135deg, #b8860b, #d4a574) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 0 16px 16px !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    margin-top: 0.4rem !important;
    box-shadow: 0 4px 12px rgba(184,134,11,0.2) !important;
    transition: all 0.2s !important;
}
.scene-card-grid [data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #d4a574, #e8b86b) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(184,134,11,0.3) !important;
}

/* 卡片 HTML 部分 */
.scene-card-inner {
    background: linear-gradient(135deg, #f5f0e8, #e8dfd0);
    border: 1px solid #d4c5a9;
    border-bottom: none;
    border-radius: 16px 16px 0 0;
    padding: 1.2rem 1rem;
    text-align: left;
}

/* ── 导航：flex-wrap 自动换行 ── */
.nav-flex-wrap {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 0.4rem !important;
    margin: 0.4rem 0 !important;
    justify-content: flex-start;
    width: 100% !important;
}
.nav-flex-wrap > * {
    flex: 0 1 auto !important;
    margin: 0 !important;
}
.nav-flex-wrap a,
.nav-flex-wrap [data-testid="stPageLink-NavLink"],
.nav-flex-wrap a[data-testid="stPageLink-NavLink"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
    display: inline-block !important;
    box-sizing: border-box !important;
}
/* 移动端：每个按钮 30% (一行 3 个) */
@media (max-width: 768px) {
    .nav-flex-wrap a,
    .nav-flex-wrap [data-testid="stPageLink-NavLink"] {
        flex: 0 1 calc(33.33% - 0.3rem) !important;
        text-align: center !important;
        font-size: 0.78rem !important;
        padding: 0.4rem 0.2rem !important;
        max-width: calc(33.33% - 0.3rem) !important;
    }
}
/* 桌面端 (>= 769px)：每个按钮均分 7 等分 (大约 14% 一行 7 个) */
@media (min-width: 769px) {
    .nav-flex-wrap a,
    .nav-flex-wrap [data-testid="stPageLink-NavLink"] {
        flex: 0 1 calc(14.28% - 0.4rem) !important;
        max-width: calc(14.28% - 0.4rem) !important;
        text-align: center !important;
        min-width: 90px !important;
    }
}

/* ── 移动端适配 (max-width: 768px) ── */
@media (max-width: 768px) {
    /* 整体容器窄一点 */
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    /* 场景卡片和按钮更紧凑 */
    .scene-card {
        padding: 1rem !important;
    }
}

/* 全局：section-title 加点呼吸感 */
.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0.8rem 0 0.4rem;
    color: #2c1810;
}

/* ── track-3：共鸣页 post-card / warm-word / emotion-bar ── */
.post-card {
    background: #f5f0e8;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin: 0.6rem 0;
    border: 1px solid #e8dfd0;
    border-left: 3px solid #b8860b;
    position: relative;
}
.post-card .post-content {
    line-height: 1.8;
    color: #2c1810;
    font-size: 0.95rem;
    white-space: pre-wrap;
    word-break: break-word;
}
.post-card .post-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    align-items: center;
    margin-top: 0.6rem;
    font-size: 0.72rem;
    color: #8b7355;
}
.post-card .post-meta .src-tag {
    background: rgba(45,106,79,0.12);
    color: #2d6a4f;
    padding: 0.1rem 0.45rem;
    border-radius: 99px;
}
.post-card .post-actions {
    display: flex;
    gap: 0.4rem;
    align-items: center;
    margin-top: 0.6rem;
    flex-wrap: wrap;
}
.post-card .resonate-count {
    color: #c0392b;
    font-weight: 600;
    font-size: 0.85rem;
    margin-right: 0.3rem;
}

/* 温暖留言行 */
.warm-word {
    background: rgba(184,134,11,0.06);
    border-left: 2px solid #b8860b;
    padding: 0.4rem 0.7rem;
    margin: 0.3rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #2c1810;
    line-height: 1.6;
}
.warm-word .warm-time {
    font-size: 0.68rem;
    color: #8b7355;
    margin-top: 0.15rem;
}
.warm-word-empty {
    text-align: center;
    color: #8b7355;
    font-size: 0.78rem;
    padding: 0.5rem;
    font-style: italic;
}

/* 情绪分布条 */
.emotion-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.3rem 0;
    font-size: 0.78rem;
}
.emotion-bar .bar-label {
    width: 3.2em;
    color: #2c1810;
    font-weight: 500;
    text-align: right;
    flex-shrink: 0;
}
.emotion-bar .bar-track {
    flex: 1;
    background: #e8dfd0;
    border-radius: 99px;
    height: 14px;
    overflow: hidden;
    position: relative;
}
.emotion-bar .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #b8860b, #d4a574);
    border-radius: 99px;
    transition: width 0.6s ease-out;
}
.emotion-bar .bar-count {
    width: 2.5em;
    color: #8b7355;
    font-size: 0.72rem;
    flex-shrink: 0;
    text-align: right;
}

/* 今日一签卡 */
.daily-sign {
    background: linear-gradient(135deg, #2c1810, #4a2c1a);
    color: #f5f0e8;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin: 0.6rem 0;
    border: 1px solid #b8860b;
    position: relative;
    overflow: hidden;
}
.daily-sign::before {
    content: '🌸';
    position: absolute;
    top: -10px;
    right: -8px;
    font-size: 4rem;
    opacity: 0.15;
}
.daily-sign .sign-label {
    font-size: 0.7rem;
    color: #d4a574;
    letter-spacing: 0.2rem;
    margin-bottom: 0.4rem;
}
.daily-sign .sign-content {
    line-height: 1.7;
    font-size: 0.92rem;
    position: relative;
}
.daily-sign .sign-footer {
    font-size: 0.7rem;
    color: #d4c5a9;
    margin-top: 0.5rem;
    text-align: right;
}

/* 匿名等级徽章 */
.anon-tier {
    display: inline-block;
    padding: 0.4rem 0.9rem;
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.3rem 0;
}
.anon-tier.tier-1 { background: rgba(45,106,79,0.12); color: #2d6a4f; }
.anon-tier.tier-2 { background: rgba(184,134,11,0.12); color: #b8860b; }
.anon-tier.tier-3 { background: rgba(192,57,43,0.12); color: #c0392b; }

/* 匹配分组小标题 */
.match-section-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #2c1810;
    margin: 0.8rem 0 0.3rem;
    padding-left: 0.4rem;
    border-left: 3px solid #b8860b;
}

/* 顶部画像卡 */
.emotion-profile {
    background: linear-gradient(135deg, #f5f0e8, #e8dfd0);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin: 0.6rem 0;
    border: 1px solid #d4c5a9;
}
.emotion-profile .profile-title {
    font-size: 0.78rem;
    color: #8b7355;
    margin-bottom: 0.4rem;
}
.emotion-profile .profile-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
}

/* 报告模态（用 st 组件不需要；保留为将来参考） */
.report-form {
    background: #fff;
    border: 1px solid #e8dfd0;
    border-radius: 8px;
    padding: 0.6rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
}

/* 紧凑按钮组（共鸣页用，避免按钮撑满整行） */
.action-row {
    display: flex;
    gap: 0.3rem;
    flex-wrap: wrap;
    margin-top: 0.4rem;
}
.action-row [data-testid="stButton"] button {
    padding: 0.25rem 0.7rem !important;
    font-size: 0.8rem !important;
    border-radius: 99px !important;
    min-height: 0 !important;
    height: auto !important;
}

/* ── 首页 v2 重排：区块 + 区块标题 + 卡片统一 ── */

/* 区块：垂直间距统一 */
.home-section {
    margin: 1.2rem 0 0.4rem;
}
.home-section + .home-section {
    margin-top: 1.6rem;
}

/* 区块标题：图标 + 主标 + 副标 */
.section-header {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin: 0.6rem 0 0.6rem;
    padding-left: 0.2rem;
    border-left: 3px solid #b8860b;
    line-height: 1.2;
}
.section-header .section-icon { font-size: 1.2rem; }
.section-header .section-title-main {
    font-size: 1rem;
    font-weight: 700;
    color: #2c1810;
    letter-spacing: 0.05rem;
}
.section-header .section-title-sub {
    font-size: 0.75rem;
    color: #8b7355;
    margin-left: 0.2rem;
}

/* 7 个 nav：用 CSS Grid 强制多列（不依赖 st.columns，mobile/desktop 都干净） */
.home-nav-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    margin: 0.4rem 0 0.6rem;
}
@media (max-width: 480px) {
    .home-nav-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 0.4rem;
    }
}
@media (min-width: 769px) {
    .home-nav-grid {
        grid-template-columns: repeat(7, 1fr);
        gap: 0.4rem;
    }
}
.home-nav-grid [data-testid="stPageLink-NavLink"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.25rem !important;
    background: #fff !important;
    color: #2c1810 !important;
    border: 1px solid #e8dfd0 !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.3rem !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: all 0.2s !important;
    min-height: 72px !important;
    box-shadow: 0 1px 3px rgba(44,24,16,0.04) !important;
}
.home-nav-grid [data-testid="stPageLink-NavLink"]:hover {
    background: linear-gradient(135deg, #f5f0e8, #e8dfd0) !important;
    border-color: #b8860b !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(184,134,11,0.15) !important;
}
.home-nav-grid [data-testid="stPageLink-NavLink"] span {
    font-size: 1.4rem !important;
    line-height: 1 !important;
}

/* 9 场景按钮：CSS Grid 2 列，mobile 1 列 */
.home-scene-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
    margin: 0.4rem 0 0.4rem;
}
@media (max-width: 480px) {
    .home-scene-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.4rem;
    }
}
.home-scene-grid [data-testid="stButton"] button {
    background: linear-gradient(135deg, #f5f0e8, #e8dfd0) !important;
    color: #2c1810 !important;
    border: 1px solid #d4c5a9 !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.5rem !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    min-height: 56px !important;
    height: auto !important;
    white-space: pre-line !important;
    line-height: 1.4 !important;
    transition: all 0.2s !important;
}
.home-scene-grid [data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #d4a574, #b8860b) !important;
    color: #fff !important;
    border-color: #b8860b !important;
    transform: translateY(-1px) !important;
}

/* 12 情绪按钮：CSS Grid 4×3（mobile 也保持 4 列） */
.home-emotion-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.4rem;
    margin: 0.4rem 0 0.4rem;
}
@media (max-width: 380px) {
    .home-emotion-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 0.3rem;
    }
}
.home-emotion-grid [data-testid="stButton"] button {
    background: #fff !important;
    color: #2c1810 !important;
    border: 1px solid #e8dfd0 !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.2rem !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    min-height: 48px !important;
    height: auto !important;
    transition: all 0.2s !important;
    white-space: pre-line !important;
    line-height: 1.3 !important;
}
.home-emotion-grid [data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #b8860b, #d4a574) !important;
    color: #fff !important;
    border-color: #b8860b !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(184,134,11,0.2) !important;
}

/* hero 大区块 */
.home-hero {
    background: linear-gradient(135deg, #2c1810 0%, #4a2c1a 50%, #3d1f0e 100%);
    color: #f5f0e8;
    padding: 1.6rem 1.2rem 1.4rem;
    text-align: center;
    border-radius: 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 6px 20px rgba(44,24,16,0.18);
}
.home-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 40% at 30% 30%, rgba(184,134,11,0.18), transparent 60%),
        radial-gradient(ellipse 50% 30% at 70% 80%, rgba(192,57,43,0.12), transparent 60%);
    pointer-events: none;
}
.home-hero > * { position: relative; }
.home-hero .hero-eyebrow {
    font-size: 0.7rem;
    color: #d4a574;
    letter-spacing: 0.3rem;
    margin-bottom: 0.4rem;
    opacity: 0.85;
}
.home-hero .hero-title {
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: 0.5rem;
    margin: 0.2rem 0 0.4rem;
    color: #f5f0e8;
}
.home-hero .hero-sub {
    font-size: 0.85rem;
    color: #d4c5a9;
    opacity: 0.85;
    margin: 0 0 0.8rem;
    letter-spacing: 0.05rem;
}
.home-hero .hero-motto {
    font-size: 0.78rem;
    color: #b8860b;
    font-style: italic;
    opacity: 0.75;
    margin: 0.6rem 0 0;
    letter-spacing: 0.08rem;
}

/* CTA 主按钮：st.button primary */
.home-hero [data-testid="baseButton-primary"],
.home-hero button[kind="primary"] {
    background: linear-gradient(135deg, #b8860b, #d4a574) !important;
    color: #fff !important;
    border: none !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.7rem 1.2rem !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(184,134,11,0.35) !important;
}

/* 底部信息 */
.home-footer {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    color: #8b7355;
    font-size: 0.75rem;
    line-height: 1.8;
}
.home-footer .footer-tag {
    color: #b8860b;
    font-size: 0.7rem;
    letter-spacing: 0.05rem;
}
</style>"""

import streamlit as st

def inject_css():
    """在任意页面注入全局 CSS"""
    st.markdown(CSS, unsafe_allow_html=True)
