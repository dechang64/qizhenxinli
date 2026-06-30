"""批量生成缺失 + 太短 的 10 段 mp3, 上传到 GitHub Release v1.0-music

10 段:
- 6 段缺失 (404): 藕香榭 × 6 情绪
- 2 段太短 (<60s): 稻香村·疗愈, 怡红院·释然
- 2 段偏短 (60-90s): 潇湘馆·欢愉, 蘅芜苑·思念

v6.4 精确 prompt (300+ 字 9 要素):
- 心理疗法锚定 (叙事/CBT/人本/ACT/积极/赋权)
- 6 调式 (五声羽/商/宫/徵/角/清商) + 西方调式融合
- 精确 BPM (45-90)
- 乐器分层 (主奏/和声/低频/点缀)
- 环境音叠加

跑: python scripts/regen_music_v2.py MINIMAX_API_KEY
"""
import sys
import os
import requests
import json
import time
from pathlib import Path

# 接受命令行传入 key (避免硬编码, 避免 echo)
if len(sys.argv) < 2:
    print("Usage: python regen_music_v2.py <MINIMAX_API_KEY>")
    sys.exit(1)
API_KEY = sys.argv[1]

# 1. scene_prompts 复用 (已有, 不重新写)
sys.path.insert(0, '.')
from core.scene_prompts import SCENE_META, get_variant_prompt

# 2. 10 段目标
TARGETS = [
    # 缺失 6 段 (404) - 藕香榭全情绪
    ("ouxxiangxie", "ningjing"),
    ("ouxxiangxie", "sinian"),
    ("ouxxiangxie", "huanyu"),
    ("ouxxiangxie", "chensi"),
    ("ouxxiangxie", "liaoyu"),
    ("ouxxiangxie", "shiran"),
    # 太短 2 段 (<60s) - 用更长 prompt 强制
    ("daoxiangcun", "liaoyu"),
    ("yihongyuan", "shiran"),
    # 偏短 2 段 (60-90s)
    ("xiaoxiangguan", "huanyu"),
    ("hengwuyuan", "sinian"),
]

# 3. 反向映射: ASCII 名 → 中文 (匹配 FILENAME_MAP)
CN_MAP = {
    "xiaoxiangguan": "潇湘馆",
    "hengwuyuan": "蘅芜苑",
    "yihongyuan": "怡红院",
    "daoxiangcun": "稻香村",
    "ouxxiangxie": "藕香榭",
    "qiushuangzhai": "秋爽斋",
}
MOOD_CN = {
    "ningjing": "宁静", "sinian": "思念", "huanyu": "欢愉",
    "chensi": "沉思", "liaoyu": "疗愈", "shiran": "释然",
}

# 4. 输出目录
OUT_DIR = Path("data/mp3_v2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 5. API 调用
API_URL = "https://api.minimaxi.com/v1/music_generation"


def call_minimax(prompt: str) -> bytes | None:
    """调 MiniMax music-2.6, 返回 mp3 bytes"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "music-2.6",
        "prompt": prompt,
        "is_instrumental": True,
        "output_format": "url",  # 先 url, 下载; 也可 "hex"
        "aigc_watermark": False,
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            print(f"  API err: {base_resp}")
            return None

        music_data = data.get("data", {})
        status = music_data.get("status")

        if status == 1:
            print(f"  还在生成中, skip")
            return None
        if status != 2:
            print(f"  Unknown status: {status}")
            return None

        # 下载 url
        audio_url = music_data.get("audio", "")
        if not audio_url:
            return None

        audio_resp = requests.get(audio_url, timeout=120)
        audio_resp.raise_for_status()
        return audio_resp.content

    except Exception as e:
        print(f"  Exception: {type(e).__name__}: {e}")
        return None


# 6. 批量生成
print(f"=== 批量生成 {len(TARGETS)} 段 mp3 ===\n")
success = []
for scene_ascii, mood_ascii in TARGETS:
    scene_cn = CN_MAP[scene_ascii]
    mood_cn = MOOD_CN[mood_ascii]
    name = f"{scene_ascii}_{mood_ascii}"
    out_path = OUT_DIR / f"{name}.mp3"

    print(f"-> {name} ({scene_cn}·{mood_cn})")

    # 拿 meta
    meta = SCENE_META.get(scene_cn, SCENE_META["潇湘馆"])

    # 拼精确 prompt (用 base 变体, 不用纯器乐)
    full_prompt = get_variant_prompt(scene_cn, mood_cn, "base")

    # 强制 2 分钟+ (BPM 调慢, 提示加 "extended duration")
    full_prompt += "\n\n[规格] 时长 2:00-3:00 分钟, 适合深度冥想, 不急不缓"

    print(f"   prompt: {len(full_prompt)} chars")

    # 调 API
    mp3_bytes = call_minimax(full_prompt)
    if mp3_bytes:
        out_path.write_bytes(mp3_bytes)
        size_kb = len(mp3_bytes) / 1024
        print(f"   OK, {size_kb:.0f} KB, -> {out_path}\n")
        success.append(name)
    else:
        print(f"   FAILED\n")

    time.sleep(2)  # 限流

print(f"\n=== 完成: {len(success)}/{len(TARGETS)} ===")
print(f"成功: {success}")
print(f"\n下一步: python scripts/upload_mp3_to_release.py")
