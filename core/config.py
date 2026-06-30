"""全局配置：API密钥、常量、环境检测"""

# 2026-06-09: bump config.py to force Streamlit Cloud to re-pull this file
# (Cloud was running a stale core/config.py without EMOTION_ICONS/EMOTION_PLACEHOLDERS/SCENE_FIT_HINTS
# added by track-2 commit 9c288cd, causing ImportError on 2_treehole.py import)

import os

# ── GLM API（智谱AI，OpenAI 兼容格式）──
GLM_API_KEY = os.environ.get("GLM_API_KEY", "")
GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# ── MiniMax API（Token Plan 全功能：一个 key 可同时用于 chat + music）──
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
# 独立 music key（如果 chat key 没 music 权限，配此 fallback）—— 2026-06-09
MINIMAX_MUSIC_API_KEY = os.environ.get("MINIMAX_MUSIC_API_KEY", "") or MINIMAX_API_KEY
MINIMAX_BASE_URL = "https://api.minimaxi.com"

# ── AMAX Token Router（OpenAI 兼容，单 key 调度 50+ LLM）──
# 2026-06-10: 切到 AMAX 路由（用户已有 key，MiniMax key 全失效）
# 官方域名: https://ai.amaxsmp.com (用户提供)
AMAX_API_KEY = os.environ.get("AMAX_API_KEY", "")
AMAX_BASE_URL = "https://ai.amaxsmp.com"
AMAX_CHAT_MODEL = os.environ.get("AMAX_CHAT_MODEL", "deepseek-v3")  # 便宜、中文好

# ── 模型 ──
CHAT_MODEL = "glm-4-flash"          # GLM 免费模型，速度快，适合对话
# MUSIC_MODEL 已移除，请在 minimax_music.py 中使用 "music-2.6"（Token Plan 用户）

# ── 数据库（Streamlit Cloud 无持久文件系统，用内存数据库）──
DB_PATH = os.environ.get("TREEHOLE_DB_PATH", ":memory:")

# ── 模式检测 ──
# 2026-06-10: 切到 AMAX 路由；MOCK_MODE 由 chat 模块本地定义
# 保留 GLM/MiniMax 常量以备回退（暂未使用）
MOCK_MODE = not (GLM_API_KEY or MINIMAX_API_KEY or AMAX_API_KEY)

# ── 设计令牌 ──
INK = "#2c1810"
PAPER = "#f5f0e8"
PAPER2 = "#e8dfd0"
RED = "#c0392b"
GOLD = "#b8860b"
JADE = "#2d6a4f"
MUTED = "#8b7355"

# ── 9大场景（6 经典 + 3 新增：栊翠庵/缀锦楼/紫菱洲）──
SCENES = [
    {"name": "潇湘馆", "icon": "🎋", "desc": "竹林深处，月影斑驳",
     "mood": "孤独、思念", "char": "林黛玉", "theory": "叙事疗法",
     "style": "倾听你的心事", "color": "#2d6a4f"},
    {"name": "蘅芜苑", "icon": "🌿", "desc": "幽香弥漫，清冷如月",
     "mood": "迷茫、压抑", "char": "薛宝钗", "theory": "认知行为疗法",
     "style": "理性帮你理清", "color": "#5a7d6b"},
    {"name": "怡红院", "icon": "🌸", "desc": "花团锦簇，温暖如春",
     "mood": "焦虑、不安", "char": "贾宝玉", "theory": "人本主义",
     "style": "温柔化解不安", "color": "#c0392b"},
    {"name": "稻香村", "icon": "🌾", "desc": "田园宁静，炊烟袅袅",
     "mood": "疲惫、倦怠", "char": "李纨", "theory": "正念+ACT",
     "style": "安静的陪伴", "color": "#8b7355"},
    {"name": "藕香榭", "icon": "🪷", "desc": "碧水清波，荷香四溢",
     "mood": "纠结、犹豫", "char": "史湘云", "theory": "积极心理学",
     "style": "大大方方翻篇", "color": "#d4a574"},
    {"name": "秋爽斋", "icon": "📜", "desc": "窗明几净，笔墨书香",
     "mood": "愤怒、不满", "char": "探春", "theory": "赋权+SFBT",
     "style": "陪你把话说清楚", "color": "#a0522d"},
    # ── 新增三院 ──
    {"name": "栊翠庵", "icon": "🪷", "desc": "古柏青灯，禅房清寂",
     "mood": "执念、完美", "char": "妙玉", "theory": "正念禅修",
     "style": "教你放下", "color": "#7d6b5d"},
    {"name": "缀锦楼", "icon": "🎨", "desc": "绣帘半卷，针线生辉",
     "mood": "内耗、委屈", "char": "惜春", "theory": "艺术疗法+边界",
     "style": "把话绣出来", "color": "#b87a8a"},
    {"name": "紫菱洲", "icon": "🫧", "desc": "菱花照水，波光柔软",
     "mood": "自卑、隐忍", "char": "迎春", "theory": "自我悲悯+ACT",
     "style": "温柔地抱住你", "color": "#a8c4d4"},
]

SCENE_MAP = {s["name"]: s for s in SCENES}

# ── 树洞释放方式 ──
RELEASE_METHODS = {
    "wind":  {"icon": "🍃", "title": "已随风飘散", "sub": "风会带走它"},
    "lake":  {"icon": "💧", "title": "已沉入湖底", "sub": "湖水会记住它"},
    "petal": {"icon": "🌸", "title": "已化为花瓣", "sub": "花瓣会替你开"},
    "smoke": {"icon": "🕯️", "title": "已燃为青烟", "sub": "烟会替你说"},
    "silent":{"icon": "🎧", "title": "静静聆听",     "sub": "什么都不做，只是听"},
}

# ── 情绪分类 ──
EMOTIONS = ["悲伤", "焦虑", "愤怒", "迷茫", "疲惫", "孤独", "平静",
            "感恩", "期待", "执念", "委屈", "自卑"]

# ── 情绪 icon 映射（track-2 首屏引导用）──
EMOTION_ICONS = {
    "悲伤": "💧", "焦虑": "🌊", "愤怒": "🔥", "迷茫": "🌫️",
    "疲惫": "🍂", "孤独": "🌙", "平静": "🍃", "感恩": "🌸",
    "期待": "🌅", "执念": "⛓️", "委屈": "🌧️", "自卑": "🥀",
}

# ── 情绪 → 文本框 placeholder（track-2 首屏引导用）──
EMOTION_PLACEHOLDERS = {
    "悲伤": "想哭就哭出来...",
    "焦虑": "把心里压着的那些写下来...",
    "愤怒": "把火气先卸掉一些...",
    "迷茫": "不知道方向也没关系...",
    "疲惫": "你已经很努力了...",
    "孤独": "想说点什么就写下来...",
    "平静": "今天风很轻，你想说点什么...",
    "感恩": "想感谢谁？写下来吧...",
    "期待": "你在期待什么...",
    "执念": "放不下的事，先写下来...",
    "委屈": "把说不出口的话写下来...",
    "自卑": "先把自己抱住...",
}

# ── 场景 → "适合" 短句（track-2 首屏引导用，1 行 12-20 字）──
# 复用 scene['desc'] + 自定义一句推荐语
SCENE_FIT_HINTS = {
    "潇湘馆": "适合一个人慢慢说",
    "蘅芜苑": "适合把心绪理一理",
    "怡红院": "适合被温柔接住",
    "稻香村": "适合安静地待一会儿",
    "藕香榭": "适合把纠结说出来",
    "秋爽斋": "适合把话说清楚",
    "栊翠庵": "适合放下放不下的",
    "缀锦楼": "适合把委屈绣出来",
    "紫菱洲": "适合把自己抱住",
}

# ── 音乐场景 ──
MUSIC_PLACES = ["潇湘馆", "蘅芜苑", "怡红院", "稻香村", "藕香榭", "秋爽斋",
                "栊翠庵", "缀锦楼", "紫菱洲"]
MUSIC_MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]

# v6.4: 4 风格变体 (《树洞疗愈音乐提示词指南》第 3 节)
# - base: 基础版 (指南 9 要素完整 prompt)
# - 纯器乐: 删环境音段, 突出主奏独奏
# - 深度冥想: BPM -5~-8, 删减节奏型乐器
# - 情绪疏导: BPM +3~+5, 强化主奏旋律
# - 静谧沉思: 降高频, 突出古琴/陶埙/手碟
MUSIC_VARIANTS = ["base", "纯器乐", "深度冥想", "情绪疏导", "静谧沉思"]

# ═══════════════════════════════════════════════════════════
#  MBTI → 疗愈偏好参数（贯穿整个旅程）
# ═══════════════════════════════════════════════════════════
MBTI_PARAMS = {
    # I — 内向 / 深度，N — 直觉 / 意义
    "INFP": {"tone": "gentle_listening", "reply_length": "medium_long",
             "music_mood": "reflective", "approach": "narrative"},
    "INFJ": {"tone": "guiding", "reply_length": "medium",
             "music_mood": "serene", "approach": "cbt"},
    # E — 外向 / 能量
    "ENFP": {"tone": "light", "reply_length": "medium",
             "music_mood": "uplifting", "approach": "positive"},
    "ENFJ": {"tone": "warm", "reply_length": "medium",
             "music_mood": "warm", "approach": "humanistic"},
    # 理性分析型
    "INTJ": {"tone": "guiding", "reply_length": "medium",
             "music_mood": "meditative", "approach": "cbt"},
    "INTP": {"tone": "guiding", "reply_length": "medium_long",
             "music_mood": "meditative", "approach": "cbt"},
    "ENTJ": {"tone": "guiding", "reply_length": "short",
             "music_mood": "uplifting", "approach": "empowering"},
    "ENTP": {"tone": "light", "reply_length": "short",
             "music_mood": "uplifting", "approach": "positive"},
    # 实际感受型
    "ISFP": {"tone": "gentle_listening", "reply_length": "medium_long",
             "music_mood": "reflective", "approach": "narrative"},
    "ISFJ": {"tone": "warm", "reply_length": "medium_long",
             "music_mood": "warm", "approach": "mindfulness"},
    "ESFP": {"tone": "light", "reply_length": "short",
             "music_mood": "uplifting", "approach": "positive"},
    "ESFJ": {"tone": "warm", "reply_length": "medium",
             "music_mood": "warm", "approach": "humanistic"},
    "ISTP": {"tone": "guiding", "reply_length": "short",
             "music_mood": "serene", "approach": "empowering"},
    "ISTJ": {"tone": "guiding", "reply_length": "medium",
             "music_mood": "serene", "approach": "cbt"},
    "ESTP": {"tone": "light", "reply_length": "short",
             "music_mood": "uplifting", "approach": "positive"},
    "ESTJ": {"tone": "guiding", "reply_length": "short",
             "music_mood": "serene", "approach": "empowering"},
}

# ═══════════════════════════════════════════════════════════
#  星座元素 → 疗愈偏好参数
# ═══════════════════════════════════════════════════════════
ELEM_PARAMS = {
    "火": {"tone": "light", "reply_length": "short",
           "music_mood": "uplifting", "approach": "positive"},
    "土": {"tone": "warm", "reply_length": "medium_long",
           "music_mood": "warm", "approach": "mindfulness"},
    "风": {"tone": "light", "reply_length": "short",
           "music_mood": "uplifting", "approach": "positive"},
    "水": {"tone": "gentle_listening", "reply_length": "medium_long",
           "music_mood": "reflective", "approach": "narrative"},
}

# ═══════════════════════════════════════════════════════════
#  情绪 → 场景推荐（首页入口用）
# ═══════════════════════════════════════════════════════════
EMOTION_SCENE_MAP = {
    "悲伤":  {"scene": "潇湘馆", "icon": "🎋", "msg": "有些话，潇湘馆的竹叶愿意听"},
    "焦虑":  {"scene": "稻香村", "icon": "🌾", "msg": "稻香村很安静，适合你降降速"},
    "愤怒":  {"scene": "藕香榭", "icon": "🪷", "msg": "藕香榭的水波，能帮你把火气散开"},
    "迷茫":  {"scene": "秋爽斋", "icon": "📜", "msg": "秋爽斋的探春，擅长帮人理清方向"},
    "疲惫":  {"scene": "稻香村", "icon": "🌾", "msg": "你累了。稻香村适合安静地待一会儿"},
    "孤独":  {"scene": "怡红院", "icon": "🌸", "msg": "怡红院很暖，有人愿意陪你坐坐"},
    "平静":  {"scene": "稻香村", "icon": "🌾", "msg": "平静也是一种力量。稻香村适合你"},
    "感恩":  {"scene": "怡红院", "icon": "🌸", "msg": "怡红院很适合这份温暖"},
    "期待":  {"scene": "藕香榭", "icon": "🪷", "msg": "藕香榭的阳光，和你的期待很配"},
    # ── 新增三院 ──
    "执念":  {"scene": "栊翠庵", "icon": "🪷", "msg": "栊翠庵的青灯下，没有放不下的事"},
    "委屈":  {"scene": "缀锦楼", "icon": "🎨", "msg": "缀锦楼很安静，可以把说不出口的话绣出来"},
    "自卑":  {"scene": "紫菱洲", "icon": "🫧", "msg": "紫菱洲的水很温柔，先把自己抱住"},
}

# ═══════════════════════════════════════════════════════════
#  情绪 → 音乐情绪推荐（主情绪优先，次情绪辅助）
# ═══════════════════════════════════════════════════════════
EMOTION_MUSIC_MAP = {
    "悲伤":   {"primary": "疗愈", "secondary": "沉思"},
    "焦虑":   {"primary": "宁静", "secondary": "沉思"},
    "愤怒":   {"primary": "释然", "secondary": "欢愉"},
    "迷茫":   {"primary": "沉思", "secondary": "宁静"},
    "疲惫":   {"primary": "疗愈", "secondary": "宁静"},
    "孤独":   {"primary": "疗愈", "secondary": "宁静"},
    "平静":   {"primary": "宁静", "secondary": "沉思"},
    "感恩":   {"primary": "欢愉", "secondary": "疗愈"},
    "期待":   {"primary": "欢愉", "secondary": "释然"},
    # ── 新增三院 ──
    "执念":   {"primary": "沉思", "secondary": "释然"},
    "委屈":   {"primary": "疗愈", "secondary": "思念"},
    "自卑":   {"primary": "思念", "secondary": "疗愈"},
}

# ═══════════════════════════════════════════════════════════
#  疗愈偏好 → 音乐氛围推荐（personality params 的 music_mood）
# ═══════════════════════════════════════════════════════════
MUSIC_MOOD_MUSIC_MAP = {
    "serene":     "宁静",
    "warm":       "疗愈",
    "meditative": "沉思",
    "uplifting":  "欢愉",
    "reflective": "思念",
}
