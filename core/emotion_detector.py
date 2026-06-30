"""情绪检测器 — 从用户文本中提取情绪标签

用于：
1. 聊天时实时标注用户情绪
2. 树洞释放时记录情绪统计
3. 联邦学习聚合的本地特征

track-2 升级：
- 加了 `_negate_scores()` helper：扫一遍"否定词 + 情绪关键词"组合
  （如"不难过"、"不想念"、"没哭"、"无意义"），把那些情绪词的原始分降权 80%
- 这样 "我不想念他" 不会误判为 "悲伤"，"我不累" 不会误判为 "疲惫"
- detect_emotion / detect_emotions_multi 在算完原始分后调用一次 _negate_scores
"""

import re

# 否定词集合（覆盖中文里 90% 的否定场景）
_NEGATION_WORDS = ("不", "别", "没", "无", "非", "未", "未尝", "没怎么", "不怎么", "不太")
_NEGATION_RE = re.compile(
    "(" + "|".join(re.escape(w) for w in _NEGATION_WORDS) + r")",
    re.UNICODE,
)
# 否定词与情绪关键词之间允许的"填充词"（不破坏否定关系的虚词/副词）
# 例： "我不再焦虑" 中"再"是 filler；"我不知道" 中"知道"不是 filler → 不断
_NEGATION_FILLER = ("再", "会", "想", "太", "就", "也", "都", "又", "并", "再", "也")
# 主语代词：在否定词之前是合法的（如"我不想念"中"我"在"不"前）
_NEGATION_PRONOUNS = ("我", "你", "他", "她", "它", "们", "自己", "咱们", "我们", "你们", "他们", "她们")
# 双否定（"不是不难过"）保持情绪为正向（"是"后面是"不难过" → 悲伤仍存在）
_DOUBLE_NEG_RE = re.compile(
    r"(不是|并非|并非不|不是不)\s*(不|别|没|无|非|未)\s*",
    re.UNICODE,
)
# 子句边界字符（否定词若在这些位置之后，算"真正"的否定前缀）
_CLAUSE_BOUNDARY = ("，", "。", "！", "？", "；", "、", " ", "\n", "\t", "(", "（", ".", ",", "!", "?", ";")
# 降权系数：被否定的情绪词得分 × 0.2 （即降 80%）
_NEGATION_PENALTY = 0.2

# 情绪关键词映射（优先级从高到低）
EMOTION_PATTERNS = {
    "悲伤": re.compile(
        r"难过|伤心|哭|悲伤|心痛|难受|不开心|低落|抑郁|绝望|"
        r"流泪|想哭|痛|失去|离开|分手|去世|走了|不在了|再也|"
        r"遗憾|后悔|自责|内疚|想念|思念|怀念|舍不得|心碎|泪|"
        r"想死|不想活|活着没意思|自杀|自残|割腕|跳楼|结束生命|"
        r"死了算了|活不下去|生不如死|解脱"
    ),
    "焦虑": re.compile(
        r"焦虑|紧张|害怕|恐惧|担心|不安|压力|崩溃|扛不住|喘不过|"
        r"失眠|睡不着|心慌|心跳|发抖|慌|万一|怎么办|考试|面试|"
        r"deadline|截止|来不及|赶不上|怕|慌张|忐忑"
    ),
    "愤怒": re.compile(
        r"生气|愤怒|讨厌|恨|不公平|凭什么|烦|恶心|混蛋|气死|"
        r"无语|忍不了|受够了|欺负|利用|背叛|骗|撒谎|虚伪|"
        r"不公|怒|火大|暴躁|烦死"
    ),
    "迷茫": re.compile(
        r"迷茫|不知道|方向|意义|活着|为什么|空虚|无聊|没意思|"
        r"目标|未来|选择|纠结|犹豫|到底|应该|该不该|值不值得|"
        r"困惑|不知所措|何去何从"
    ),
    "疲惫": re.compile(
        r"累|疲惫|倦怠|撑不住|撑不下去|好累|太累|筋疲力|透支|"
        r"加班|熬夜|起不来|没精神|不想动|摆烂|躺平|倦了|麻木|"
        r"耗尽|心力交瘁|精疲力竭"
    ),
    "孤独": re.compile(
        r"孤独|一个人|没人|寂寞|被抛弃|不被理解|没人在乎|孤单|"
        r"没朋友|合不来|融入不了|被排挤|被忽视|透明|没人理|"
        r"独处|形单影只"
    ),
    "平静": re.compile(
        r"还好|没事|平静|淡然|释怀|放下|算了|无所谓|习惯了|"
        r"接受|坦然|安宁|安静|还好吧|一般般|凑合"
    ),
    "感恩": re.compile(
        r"感谢|谢谢|感恩|幸运|珍惜|幸福|满足|温暖|感动|"
        r"好人|善良|帮助|支持|陪伴|在乎|关心|爱"
    ),
    "期待": re.compile(
        r"期待|希望|加油|努力|向前|未来可期|相信|机会|"
        r"尝试|改变|进步|成长|学习|新|开始|出发"
    ),
    # ── 新增三院（执念/委屈/自卑）──
    "执念": re.compile(
        r"执念|放不下|过不去|走不出来|忘不掉|纠缠|纠结于|"
        r"一直想|总是想|反复想|困扰|魔怔|钻牛角尖|死结|"
        r"放不开|舍不下|不能原谅|无法释怀|心结|意难平"
    ),
    "委屈": re.compile(
        r"委屈|被忽视|被忽略|被冷落|不被看见|不被在乎|"
        r"吃力不讨好|付出了却|没人感谢|心酸|不值|"
        r"为什么没人|没人问|没人理我|我做得够好了|不被珍惜|"
        r"没人看见|不被看见|却没人|没人在意|"
        r"我付出了|付出那么多|对我不好|真心被"
    ),
    "自卑": re.compile(
        r"自卑|不够好|比不上|不如别人|没用|废物|失败者|"
        r"我不行|我不够|配不上|低人一等|没价值|没意思|"
        r"没人会喜欢|不被爱|不值得|糟糕透了|我很差"
    ),
}

# 情绪强度权重（用于联邦学习聚合）
EMOTION_WEIGHTS = {
    "悲伤": 1.5, "焦虑": 1.3, "愤怒": 1.4,
    "迷茫": 1.0, "疲惫": 1.2, "孤独": 1.3,
    "平静": 0.5, "感恩": 0.3, "期待": 0.4,
    "执念": 1.3, "委屈": 1.3, "自卑": 1.4,
}


def detect_emotion(text: str) -> str:
    """从文本中检测主要情绪，返回情绪标签

    track-2：在算完原始分后调用 _negate_scores，对被否定的情绪词降权 80%。
    特殊处理：若唯一的情绪关键词被否定（其它情绪分都远低于它）→ 返回"平静"，
    避免"我不想念"被误判为"悲伤"。
    """
    if not text or not text.strip():
        return "平静"

    scores = {}
    for emotion, pattern in EMOTION_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            scores[emotion] = len(matches) * EMOTION_WEIGHTS.get(emotion, 1.0)

    if not scores:
        return "平静"

    # 否定词降权（如 "我不想念" → 悲伤分 ×0.2）
    scores, negated = _negate_scores(text, scores)

    if not scores:
        return "平静"

    # 特殊处理：所有匹配的情绪都被否定 → 平静
    # 例 "我不再焦虑，也不想念" → 焦虑 1.3→0.26, 悲伤 1.5→0.3 → 平静
    # 例 "我不想念" → 悲伤 1.5→0.3 → 平静
    if negated and all(emo in negated for emo in scores):
        return "平静"

    return max(scores, key=scores.get)


def detect_emotions_multi(text: str) -> dict[str, float]:
    """检测文本中的多种情绪，返回 {情绪: 得分} 字典

    track-2：同样在算完原始分后应用 _negate_scores。
    若所有情绪都被否定 → 返回 {"平静": 1.0}。
    """
    if not text or not text.strip():
        return {"平静": 1.0}

    scores = {}
    for emotion, pattern in EMOTION_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            scores[emotion] = len(matches) * EMOTION_WEIGHTS.get(emotion, 1.0)

    if not scores:
        return {"平静": 1.0}

    # 否定词降权
    scores, negated = _negate_scores(text, scores)

    if not scores:
        return {"平静": 1.0}

    # 所有情绪都被否定 → 平静
    if negated and all(emo in negated for emo in scores):
        return {"平静": 1.0}

    # 归一化
    total = sum(scores.values())
    return {k: round(v / total, 3) for k, v in scores.items()}


def _is_filler_only(s: str) -> bool:
    """检查字符串是否只由"否定词填充词"组成（0-2 字符）。

    用于判断否定词与情绪关键词之间的内容是否为合法 filler
    （如"我不再焦虑"中"再"是 filler，"不知道"中"知道"不是）。

    允许 0-2 个字符的 filler（再/会/想/太/就/也/都/又/并）+ 任意标点/空白。
    """
    if not s:
        return True
    # 最多 2 个 filler 字符
    filler_count = 0
    for ch in s:
        if ch in _NEGATION_FILLER:
            filler_count += 1
            if filler_count > 2:
                return False
        elif ch in _CLAUSE_BOUNDARY:
            continue
        else:
            return False
    return True


def _is_negation_prefix(s: str) -> bool:
    """检查字符串是否可作为"否定词前缀"（出现在否定词之前）。

    合法前缀组合：
    - 0-1 个主语代词 (我/你/他/她/它/们) + 0-1 个填充词 (再/会/...) + 任意标点
    - 例: "我" (pronoun) → ✓  (出现在"不想念"前)
    - 例: "我再" (pronoun + filler) → ✓
    - 例: "下" (real word) → ✗
    """
    if not s:
        return True
    pronoun_count = 0
    filler_count = 0
    for ch in s:
        if ch in _NEGATION_PRONOUNS:
            pronoun_count += 1
            if pronoun_count > 1:
                return False
        elif ch in _NEGATION_FILLER:
            filler_count += 1
            if filler_count > 1:
                return False
        elif ch in _CLAUSE_BOUNDARY:
            continue
        else:
            return False
    return True


def _negate_scores(text: str, raw_scores: dict[str, float]) -> tuple[dict[str, float], set[str]]:
    """否定词降权：扫一遍"否定词 + 情绪关键词"组合，把对应情绪分降权。

    工作机制：
    1. 先把双否定片段（"不是不"/"并非不"）替换成占位符（双否定=肯定，不降权）
    2. 对每个情绪的每个关键词，看它的前面 ~3 字符窗口：
       - 窗口内必须有否定词（不/别/没/无/非/未 等）
       - 否定词与关键词之间只允许"再/会/想/太..."等填充词，不允许实词
       - 否定词必须出现在子句边界后（标点/句首）才算"真否定"
         —— 这条避免 "不知道" 里的"不"被误判
    3. 满足以上所有条件即认为该情绪被否定

    Args:
        text: 用户原始文本
        raw_scores: {emotion: raw_score} 计算出的原始分

    Returns:
        (adjusted_scores, negated_emotions)：
        - adjusted_scores: 应用否定词后的分（被否定的 ×0.2）
        - negated_emotions: 哪些情绪被否定

    Examples:
        >>> _negate_scores("我不想念他", {"悲伤": 1.5})
        ({"悲伤": 0.3}, {"悲伤"})        # "不" 直接接 "想念"
        >>> _negate_scores("我不再焦虑了", {"焦虑": 1.3})
        ({"焦虑": 0.26}, {"焦虑"})       # "不" + filler "再" + "焦虑"
        >>> _negate_scores("我不知道未来", {"迷茫": 1.0})
        ({"迷茫": 1.0}, set())           # "不知道" 是一个词，"不"不算否定前缀
        >>> _negate_scores("我不是不难过", {"悲伤": 1.5})
        ({"悲伤": 1.5}, set())           # 双否定=肯定
    """
    if not text or not raw_scores:
        return raw_scores, set()

    # 1. 双否定：先把 "不是不X" / "并非不X" 里的内层否定词替换成空格
    placeholder = "\x00" * 4
    processed = _DOUBLE_NEG_RE.sub(
        lambda m: m.group(0).replace(m.group(2), placeholder), text
    )

    # 2. 对每个情绪，看哪些关键词前 ~3 字符窗口内是"真否定"
    negated_emotions: set[str] = set()
    NEG_WINDOW = 3  # 否定词与关键词之间最多 3 个字符

    for emotion, pattern in EMOTION_PATTERNS.items():
        for kw_match in pattern.finditer(processed):
            kw_start = kw_match.start()
            # 取关键词前的窗口
            window_start = max(0, kw_start - NEG_WINDOW)
            window = processed[window_start:kw_start]

            # 找窗口里的否定词
            neg_match = _NEGATION_RE.search(window)
            if not neg_match:
                continue

            # 条件 1：否定词必须"在子句边界后"或"是窗口的第 0 个字符"
            # 即：否定词前面是 标点/句首/主语代词
            neg_pos = neg_match.start()
            chars_before_neg = window[:neg_pos]
            if chars_before_neg:
                # 否定词前面必须是 标点/句首/0-1 个填充词/主语代词
                # 不允许出现实词（如"我不知道"中"我"是主语代词 OK，
                # "再不知道"中"再"是 filler OK，但"下不知道"中"下"是实词 → 不算真否定）
                allowed = all(c in _CLAUSE_BOUNDARY for c in chars_before_neg)
                if not allowed:
                    # 不是纯标点：拆成"代词"+"填充词"+"标点" 来看
                    # 简化：chars_before_neg 必须只由 [主语代词][填充词][标点] 构成
                    # 这里用 _is_negation_prefix 函数判断
                    if not _is_negation_prefix(chars_before_neg):
                        continue

            # 条件 2：否定词与关键词之间只允许填充词
            chars_after_neg = window[neg_match.end():]
            if chars_after_neg and not _is_filler_only(chars_after_neg):
                # 后面有实词 → 否定词可能不是针对这个关键词
                continue

            negated_emotions.add(emotion)
            break  # 一个情绪有一个关键词被否定就够了

    if not negated_emotions:
        return raw_scores, set()

    # 3. 应用降权
    adjusted = dict(raw_scores)
    for emotion in negated_emotions:
        if emotion in adjusted:
            adjusted[emotion] = round(adjusted[emotion] * _NEGATION_PENALTY, 4)

    return adjusted, negated_emotions


def compute_session_emotion_profile(messages: list[dict]) -> dict[str, float]:
    """
    计算一次会话的情绪画像（用于联邦学习本地统计）

    Args:
        messages: [{"role": "user", "text": "..."}, ...]

    Returns:
        {"悲伤": 0.3, "焦虑": 0.2, ...} 归一化后的情绪分布
    """
    user_messages = [m.get("text") or m.get("content", "") for m in messages if m.get("role") == "user"]
    if not user_messages:
        return {}

    aggregated = {}
    for msg in user_messages:
        emotions = detect_emotions_multi(msg)
        for emotion, score in emotions.items():
            aggregated[emotion] = aggregated.get(emotion, 0) + score

    # 归一化
    total = sum(aggregated.values())
    if total == 0:
        return {}
    return {k: round(v / total, 3) for k, v in aggregated.items()}
