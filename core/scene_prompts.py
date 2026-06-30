"""dgy-treehole 6 大场景精确提示词 (来自《树洞疗愈音乐提示词指南》)

每个场景包含:
- place: 场景名 (9 大观园之一)
- therapy: 心理疗法锚定 (独家差异化)
- core_emotion: 核心情绪
- emotion_dimensions: 6 维情绪标签
- scene_image: 抽象场景意象
- style: 曲风 (新世纪亚洲融合)
- mode: 五声调式 + 西方调式融合
- bpm: 节拍速度
- instruments: 乐器分层 (主奏/和声/低频/点缀)
- env_sounds: 自然环境音叠加
- base_prompt: 300+ 字精确提示词模板
- variants: 4 种风格变体 (纯器乐/深度冥想/情绪疏导/静谧沉思)

9 大观园: 潇湘馆 / 蘅芜苑 / 怡红院 / 稻香村 / 藕香榭 / 秋爽斋
         缀锦楼 / 紫菱洲 / 栊翠庵
"""

# 9 大观园场景名 (跟现有 config.MUSIC_PLACES 对齐)
ALL_PLACES = [
    "潇湘馆", "蘅芜苑", "怡红院", "稻香村", "藕香榭", "秋爽斋",
    "缀锦楼", "紫菱洲", "栊翠庵",
]

# 6 维情绪 (跟现有 config.MUSIC_MOODS 对齐)
ALL_MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]


# 6 大场景的精确元数据
SCENE_META = {
    "潇湘馆": {
        "listener": "林黛玉",
        "therapy": "叙事疗法",
        "core_emotion": "孤独、思念",
        "emotion_dimensions": ["思念", "沉思", "宁静", "疗愈"],
        "scene_image": "幽林深境, 月影漫洒, 清寂流动的诗意空间",
        "style": "新世纪亚洲融合 · 叙事氛围乐",
        "mode": "五声羽调式 + 和声小调融合",
        "bpm": 52,
        "tempo": "慢板",
        "instruments": {
            "主奏": ["南箫", "小提琴"],
            "和声": ["原声钢琴"],
            "低频": ["手碟"],
            "点缀": ["古琴泛音"],
        },
        "env_sounds": ["林间晚风", "枝叶轻簌", "月影流动微弱氛围音"],
        "tone": "冷柔",
        "core_keywords": ["空灵悠远", "婉转起伏", "娓娓道来", "空灵辽阔", "孤寂温婉"],
    },
    "蘅芜苑": {
        "listener": "薛宝钗",
        "therapy": "认知行为疗法 (CBT)",
        "core_emotion": "迷茫、压抑",
        "emotion_dimensions": ["沉思", "宁静", "疗愈", "释然"],
        "scene_image": "清宁静域, 幽芳暗涌, 如月辉笼罩的理性沉静空间",
        "style": "新世纪亚洲融合 · 极简理性氛围乐",
        "mode": "五声商调式 + 自然小调融合",
        "bpm": 55,
        "tempo": "慢板",
        "instruments": {
            "主奏": ["洞箫", "立式钢琴"],
            "和声": ["古典吉他 (分解和弦)"],
            "低频": ["手碟"],
            "点缀": ["弱音小提琴"],
        },
        "env_sounds": ["静室微风", "朦胧暗香氛围音", "轻柔气流底噪"],
        "tone": "清冷",
        "core_keywords": ["规整冷静", "层次通透", "线条克制内敛", "室内浅混响", "淡然理智"],
    },
    "怡红院": {
        "listener": "贾宝玉",
        "therapy": "人本主义",
        "core_emotion": "焦虑、不安",
        "emotion_dimensions": ["疗愈", "欢愉", "宁静", "释然"],
        "scene_image": "暖煦庭域, 繁花环绕, 暖意包裹的包容松弛空间",
        "style": "新世纪亚洲融合 · 暖心治愈乐",
        "mode": "五声宫调式 + 自然大调融合",
        "bpm": 78,
        "tempo": "中速",
        "instruments": {
            "主奏": ["曲笛", "柔音钢琴"],
            "和声": ["民谣吉他 (分解和弦)"],
            "低频": ["抒情小提琴"],
            "点缀": ["软音琵琶"],
        },
        "env_sounds": ["和煦清风", "花瓣轻落", "柔和空间回响"],
        "tone": "温暖",
        "core_keywords": ["明媚温柔", "包容松弛", "舒展圆润", "编曲饱满温润", "温情自在"],
    },
    "稻香村": {
        "listener": "李纨",
        "therapy": "正念 + ACT接纳承诺疗法",
        "core_emotion": "疲惫、倦怠",
        "emotion_dimensions": ["宁静", "疗愈", "释然", "沉思"],
        "scene_image": "旷野田园, 暮烟悠然, 松弛平和的原野栖息空间",
        "style": "新世纪亚洲融合 · 正念世界音乐",
        "mode": "五声徵调式 + 和声大调融合",
        "bpm": 45,
        "tempo": "极慢板",
        "instruments": {
            "主奏": ["陶埙", "手碟"],
            "和声": ["木吉他 (极简单和弦)"],
            "低频": ["哑光钢琴", "低音小提琴"],
            "点缀": ["静心木鱼"],
        },
        "env_sounds": ["原野长风", "浅溪流水", "田野自然底噪"],
        "tone": "恬淡",
        "core_keywords": ["质朴恬淡", "大量留白", "极简编曲", "安然恬淡", "深度疗愈"],
    },
    "藕香榭": {
        "listener": "史湘云",
        "therapy": "积极心理学",
        "core_emotion": "纠结、犹豫",
        "emotion_dimensions": ["欢愉", "释然", "疗愈", "宁静"],
        "scene_image": "临水清境, 碧波荡漾, 清风拂面的开阔自在空间",
        "style": "新世纪亚洲融合 · 灵动民谣风",
        "mode": "五声角调式 + 多利亚调式融合",
        "bpm": 90,
        "tempo": "中快板",
        "instruments": {
            "主奏": ["凯尔特风笛", "中音阮"],
            "和声": ["原声吉他 (律动)"],
            "低频": ["明亮钢琴", "高音小提琴"],
            "点缀": ["笙"],
        },
        "env_sounds": ["流水涟漪", "湖面清风", "水波轻响"],
        "tone": "清亮",
        "core_keywords": ["开朗洒脱", "鲜活明快", "舒展奔放", "灵动色彩", "豁达欢快"],
    },
    "秋爽斋": {
        "listener": "探春",
        "therapy": "赋权疗法 + SFBT焦点解决短期疗法",
        "core_emotion": "愤怒、不满",
        "emotion_dimensions": ["沉思", "释然", "疗愈", "宁静"],
        "scene_image": "明朗书境, 思绪畅达, 通透有力的知性表达空间",
        "style": "新世纪亚洲融合 · 力量型跨界古典",
        "mode": "五声清商调式 + 混合利底亚调式融合",
        "bpm": 75,
        "tempo": "中速",
        "instruments": {
            "主奏": ["古筝", "立式钢琴"],
            "和声": ["电箱吉他 (节奏)"],
            "低频": ["张力小提琴"],
            "点缀": ["轻音唢呐", "小堂板鼓"],
        },
        "env_sounds": ["书斋清风", "通透空间底噪", "轻缓气流声"],
        "tone": "刚柔并济",
        "core_keywords": ["清朗利落", "刚柔并济", "知性力量感", "理智正气", "中西融合高级"],
    },
    # 3 个新增场景 (指南里没, 我们自己补, 跟潇湘馆同模板)
    "缀锦楼": {
        "listener": "贾迎春",
        "therapy": "接纳疗法",
        "core_emotion": "委屈、退让",
        "emotion_dimensions": ["疗愈", "宁静", "沉思", "释然"],
        "scene_image": "低回幽室, 暖灯残照, 默默承受的温存空间",
        "style": "新世纪亚洲融合 · 温存疗愈乐",
        "mode": "五声羽调式 + 自然小调融合",
        "bpm": 50,
        "tempo": "慢板",
        "instruments": {
            "主奏": ["二胡", "原声钢琴"],
            "和声": ["木吉他 (分解和弦)"],
            "低频": ["低音大提琴"],
            "点缀": ["古筝泛音"],
        },
        "env_sounds": ["室内暖风", "烛火轻摇", "远处静谧氛围"],
        "tone": "温润",
        "core_keywords": ["低回温存", "柔和内敛", "默默承受", "细腻深情", "接纳释怀"],
    },
    "紫菱洲": {
        "listener": "贾迎春/邢岫烟",
        "therapy": "哀伤辅导",
        "core_emotion": "哀伤、忧郁",
        "emotion_dimensions": ["思念", "沉思", "疗愈", "宁静"],
        "scene_image": "水洲暮霭, 残荷秋水, 沉静低回的哀思空间",
        "style": "新世纪亚洲融合 · 沉静民谣",
        "mode": "五声商调式 + 自然小调融合",
        "bpm": 48,
        "tempo": "慢板",
        "instruments": {
            "主奏": ["中胡", "立式钢琴"],
            "和声": ["木吉他 (分解和弦)"],
            "低频": ["低音小提琴"],
            "点缀": ["竹笛"],
        },
        "env_sounds": ["湖畔晚风", "残荷轻触水面", "远处蛙鸣"],
        "tone": "沉静",
        "core_keywords": ["沉静低回", "哀而不伤", "婉转深长", "秋水长天", "哀思疗愈"],
    },
    "栊翠庵": {
        "listener": "妙玉",
        "therapy": "禅修/正念冥想",
        "core_emotion": "清净、超然",
        "emotion_dimensions": ["宁静", "沉思", "疗愈", "释然"],
        "scene_image": "禅林空境, 檀烟袅袅, 静谧超然的禅意空间",
        "style": "新世纪亚洲融合 · 禅意世界音乐",
        "mode": "五声宫调式 + 利底亚调式融合",
        "bpm": 42,
        "tempo": "极慢板",
        "instruments": {
            "主奏": ["古琴", "木鱼"],
            "和声": ["禅钵 (颂钵)"],
            "低频": ["手碟"],
            "点缀": ["风铃"],
        },
        "env_sounds": ["山寺钟声", "松林风过", "禅院静谧"],
        "tone": "空灵",
        "core_keywords": ["空灵超然", "禅意深远", "静谧冥想", "东方意境", "心灵归处"],
    },
}


# 完整 Minimax 提示词模板 (300+ 字, 来自指南)
def build_full_prompt(place: str, mood: str) -> str:
    """生成 300+ 字精确提示词 (指南 9 要素)"""
    meta = SCENE_META.get(place, SCENE_META["潇湘馆"])  # fallback

    inst = meta["instruments"]
    env = meta["env_sounds"]
    keywords = "、".join(meta["core_keywords"])

    # 情绪词映射 (mood 是 dgy-treehole 的 6 维)
    mood_cn_map = {
        "宁静": "宁静", "释然": "释然", "思念": "思念",
        "疗愈": "疗愈", "欢愉": "欢愉", "沉思": "沉思",
    }
    mood_cn = mood_cn_map.get(mood, mood)

    # 按场景定制提示词
    template = f"""新世纪亚洲融合{meta['style'].split('·')[-1].strip()}，{meta['mode']}，
曲风{meta['core_keywords'][0]}，{meta['core_keywords'][1]}，兼具东方诗意与国际听觉美感。
{meta['tempo']}，BPM {meta['bpm']}，节奏{meta['core_keywords'][2]}，
旋律{meta['core_keywords'][3]}，空间{meta['core_keywords'][4]}。
乐器编制层次丰富：主奏为{'/'.join(inst['主奏'])}，
和声铺垫使用{'/'.join(inst['和声'])}，
低频氛围基底搭配{'/'.join(inst['低频'])}，
点缀{'/'.join(inst['点缀'])}强化东方{meta['tone']}质感；
音色整体偏{meta['tone']}，无尖锐音效。
叠加泛亚洲自然环境音：{'/'.join(env)}。
整体氛围围绕{place}的抽象意象（{meta['scene_image']}），
引导{meta['listener']}听众深度{mood_cn}，
实现身心疗愈，东方融合风格鲜明，适配全球聆听。"""
    return template


# 4 种风格变体 (指南第 3 节)
VARIANT_MODS = {
    "纯器乐": "纯器乐版本: 不需要人声, 直接删除叠加环境音整段, 主奏乐器独奏为主",
    "深度冥想": "深度冥想/助眠版: 整体下调 5~8 BPM (BPM {bpm} → {bpm_lower}), 删减吉他扫弦/板鼓等节奏型乐器, 突出低频氛围",
    "情绪疏导": "情绪疏导版 (动态更强): 上调 3~5 BPM (BPM {bpm} → {bpm_higher}), 强化主奏乐器旋律线条, 节奏更明显",
    "静谧沉思": "静谧沉思版: 降低高频乐器 (唢呐/高音笛) 音量, 突出古琴/陶埙/手碟, BPM 不变, 整体更内省",
}


def get_variant_prompt(place: str, mood: str, variant: str = "base") -> str:
    """获取变体提示词 (base / 纯器乐 / 深度冥想 / 情绪疏导 / 静谧沉思)"""
    if variant == "base":
        return build_full_prompt(place, mood)

    base = build_full_prompt(place, mood)
    meta = SCENE_META.get(place, SCENE_META["潇湘馆"])
    bpm = meta["bpm"]

    if variant == "纯器乐":
        # 删环境音段
        return base.replace("叠加泛亚洲自然环境音", "(纯器乐, 无环境音)")
    elif variant == "深度冥想":
        mod = VARIANT_MODS["深度冥想"].format(bpm=bpm, bpm_lower=bpm - 6)
        return base + f"\n\n[变体] {mod}"
    elif variant == "情绪疏导":
        mod = VARIANT_MODS["情绪疏导"].format(bpm=bpm, bpm_higher=bpm + 4)
        return base + f"\n\n[变体] {mod}"
    elif variant == "静谧沉思":
        mod = VARIANT_MODS["静谧沉思"]
        return base + f"\n\n[变体] {mod}"
    else:
        return base
