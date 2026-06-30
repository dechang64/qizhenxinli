"""继续生成剩下 7 段 (跳过已存在), 单段长 timeout"""
import sys
import os
import requests
import time
from pathlib import Path

# 接受命令行 key
if len(sys.argv) < 2:
    print("Usage: python regen_remaining.py <KEY>")
    sys.exit(1)
API_KEY = sys.argv[1]

sys.path.insert(0, '.')
from core.scene_prompts import get_variant_prompt

# 剩下 7 段
TARGETS = [
    ("ouxxiangxie", "chensi"),
    ("ouxxiangxie", "liaoyu"),
    ("ouxxiangxie", "shiran"),
    ("daoxiangcun", "liaoyu"),
    ("yihongyuan", "shiran"),
    ("xiaoxiangguan", "huanyu"),
    ("hengwuyuan", "sinian"),
]
CN_MAP = {
    "xiaoxiangguan": "潇湘馆", "hengwuyuan": "蘅芜苑",
    "yihongyuan": "怡红院", "daoxiangcun": "稻香村",
    "ouxxiangxie": "藕香榭",
}
MOOD_CN = {
    "ningjing": "宁静", "sinian": "思念", "huanyu": "欢愉",
    "chensi": "沉思", "liaoyu": "疗愈", "shiran": "释然",
}
OUT_DIR = Path("data/mp3_v2")
OUT_DIR.mkdir(parents=True, exist_ok=True)
API_URL = "https://api.minimaxi.com/v1/music_generation"


def call_minimax(prompt: str) -> bytes | None:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "music-2.6",
        "prompt": prompt,
        "is_instrumental": True,
        "output_format": "url",
        "aigc_watermark": False,
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            print(f"  API err: {base_resp}")
            return None
        music_data = data.get("data", {})
        if music_data.get("status") != 2:
            print(f"  status: {music_data.get('status')}")
            return None
        audio_url = music_data.get("audio", "")
        if not audio_url:
            return None
        audio_resp = requests.get(audio_url, timeout=180)
        audio_resp.raise_for_status()
        return audio_resp.content
    except Exception as e:
        print(f"  Exception: {type(e).__name__}: {str(e)[:200]}")
        return None


# 跳过已存在
print(f"=== 续生成 {len(TARGETS)} 段 (跳过已存在) ===\n")
success = []
for scene_ascii, mood_ascii in TARGETS:
    name = f"{scene_ascii}_{mood_ascii}"
    out_path = OUT_DIR / f"{name}.mp3"

    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"-> {name} 跳过 (已存在 {out_path.stat().st_size/1024:.0f} KB)")
        success.append(name)
        continue

    print(f"-> {name} ({CN_MAP[scene_ascii]}·{MOOD_CN[mood_ascii]})")

    full_prompt = get_variant_prompt(CN_MAP[scene_ascii], MOOD_CN[mood_ascii], "base")
    full_prompt += "\n\n[规格] 时长 2:00-3:00 分钟, 适合深度冥想, 不急不缓"
    print(f"   prompt: {len(full_prompt)} chars, 调 API...")

    start = time.time()
    mp3_bytes = call_minimax(full_prompt)
    elapsed = time.time() - start

    if mp3_bytes:
        out_path.write_bytes(mp3_bytes)
        size_kb = len(mp3_bytes) / 1024
        print(f"   OK, {size_kb:.0f} KB, {elapsed:.0f}s\n")
        success.append(name)
    else:
        print(f"   FAILED {elapsed:.0f}s\n")
    time.sleep(3)

print(f"\n=== 本轮完成: {len(success)}/{len(TARGETS)} ===")
print(f"成功: {success}")
