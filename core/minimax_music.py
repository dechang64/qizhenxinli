"""MiniMax 音乐生成客户端（Token Plan 用户专用）

API: POST https://api.minimaxi.com/v1/music_generation
Model: music-2.6（Token Plan 用户用完整版，RPM更高）

v6.4 改进 (2026-06-15): 改用《树洞疗愈音乐提示词指南》精确模板
- 9 大观园 6 情绪 = 54 段, 各 300+ 字精确 prompt
- 6 心理疗法锚定 (叙事/CBT/人本/ACT/积极/赋权)
- 6 调式 (五声羽/商/宫/徵/角/清商) + 西方调式融合
- 4 风格变体 (基础/纯器乐/深度冥想/情绪疏导/静谧沉思)

之前 (v6.3): "中国传统乐器演奏的{宁静}氛围音乐，{prompt}，{潇湘馆}场景，空灵悠远" (30 字)
现在 (v6.4): 300+ 字, 9 要素, 心理疗法锚定 (差异化)

2026-06-09: 改用 MINIMAX_MUSIC_API_KEY（独立于 chat key），
如果没设，自动 fallback 到 MINIMAX_API_KEY（Token Plan 全功能场景）。
"""
import requests
import tempfile
import os
import logging
from core.config import MINIMAX_MUSIC_API_KEY, MINIMAX_BASE_URL
from core.scene_prompts import build_full_prompt, get_variant_prompt, SCENE_META

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 音乐功能是否可用
MUSIC_AVAILABLE = bool(MINIMAX_MUSIC_API_KEY)


def generate_music(
    prompt: str = "",
    place: str = "潇湘馆",
    mood: str = "宁静",
    is_instrumental: bool = True,
    variant: str = "base",
) -> str | None:
    """
    生成疗愈音乐

    Args:
        prompt: 用户补充描述 (可选, 附加到 300 字精确模板后)
        place: 9 大观园场景之一 (潇湘馆/蘅芜苑/怡红院/稻香村/藕香榭/秋爽斋/缀锦楼/紫菱洲/栊翠庵)
        mood: 6 维情绪 (宁静/释然/思念/疗愈/欢愉/沉思)
        is_instrumental: 是否纯音乐
        variant: 4 风格变体 (base/纯器乐/深度冥想/情绪疏导/静谧沉思)

    Returns:
        音频文件路径，失败返回 None

    6 大场景 (《树洞疗愈音乐提示词指南》):
    - 潇湘馆·林黛玉: 叙事疗法, 孤独思念, BPM 52, 南箫+小提琴+古琴泛音
    - 蘅芜苑·薛宝钗: CBT, 迷茫压抑, BPM 55, 洞箫+立式钢琴+古典吉他
    - 怡红院·贾宝玉: 人本主义, 焦虑不安, BPM 78, 曲笛+柔音钢琴+民谣吉他
    - 稻香村·李纨: 正念+ACT, 疲惫倦怠, BPM 45, 陶埙+手碟+木吉他
    - 藕香榭·史湘云: 积极心理学, 纠结犹豫, BPM 90, 凯尔特风笛+中音阮+笙
    - 秋爽斋·探春: 赋权+SFBT, 愤怒不满, BPM 75, 古筝+立式钢琴+电箱吉他
    """
    if not MUSIC_AVAILABLE:
        logger.warning("MINIMAX_MUSIC_API_KEY not configured")
        return None

    # v6.4: 用 300+ 字精确提示词模板 (指南 9 要素)
    full_prompt = get_variant_prompt(place, mood, variant)
    if prompt:
        # 用户补充描述附加到末尾
        full_prompt += f"\n\n[用户补充] {prompt}"

    logger.info(f"Scene: {place}, Mood: {mood}, Variant: {variant}, Prompt length: {len(full_prompt)} chars")

    headers = {
        "Authorization": f"Bearer {MINIMAX_MUSIC_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "music-2.6",  # Token Plan 用完整版
        "prompt": full_prompt,
        "is_instrumental": is_instrumental,
        "output_format": "url",
        "aigc_watermark": False,
    }

    try:
        # 先用短超时获取响应
        logger.info("Calling MiniMax music API...")
        resp = requests.post(
            f"{MINIMAX_BASE_URL}/v1/music_generation",
            headers=headers,
            json=payload,
            timeout=180,
        )
        logger.info(f"API response status: {resp.status_code}")

        resp.raise_for_status()
        data = resp.json()
        logger.info(f"API response: {data}")

        # 检查响应状态
        base_resp = data.get("base_resp", {})
        status_code = base_resp.get("status_code")
        if status_code != 0:
            logger.error(f"API error: {base_resp}")
            return None

        music_data = data.get("data", {})
        status = music_data.get("status")
        logger.info(f"Music generation status: {status}")

        if status == 1:
            # 还在生成中，需要轮询
            logger.info("Music is being generated, waiting...")
            return None  # Streamlit Cloud 不支持轮询，直接返回

        if status == 2:
            # 生成完成
            audio_url = music_data.get("audio", "")
            if not audio_url:
                logger.error("No audio URL in response")
                return None

            logger.info(f"Downloading audio from: {audio_url[:50]}...")

            # 下载音频
            audio_resp = requests.get(audio_url, timeout=120)
            if audio_resp.status_code != 200:
                logger.error(f"Failed to download audio: {audio_resp.status_code}")
                return None

            logger.info(f"Downloaded {len(audio_resp.content)} bytes")

            # 保存为临时文件
            tmp = tempfile.NamedTemporaryFile(
                suffix=".mp3", prefix=f"treehole_{place}_{mood}_", delete=False
            )
            tmp.write(audio_resp.content)
            tmp.close()
            logger.info(f"Saved to: {tmp.name}")
            return tmp.name

        logger.error(f"Unknown status: {status}")
        return None

    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return None
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        return None