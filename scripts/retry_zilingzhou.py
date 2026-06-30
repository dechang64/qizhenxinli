"""Retry 3 紫菱洲 timeout tracks — long timeout (300s)"""
import os
import requests
import time
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not API_KEY:
    raise SystemExit("需要 MINIMAX_API_KEY 环境变量")
BASE_URL = "https://api.minimaxi.com"

RETRY = [
    ("紫菱洲", "释然", "菱洲晨光，水面雾气散开，箫声悠远，温柔地放过自己"),
    ("紫菱洲", "思念", "菱洲黄昏，菱花映残照，琵琶低语，水波轻拍，柔软的乡愁与自怜"),
    ("紫菱洲", "沉思", "菱洲月夜，水面如镜，箫与古琴对答，与自己温柔对话"),
]

OUTPUT_DIR = Path("static/music")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

success = 0
for place, mood, prompt in RETRY:
    filename = f"{place}_{mood}.mp3"
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        print(f"  skip: {filename}")
        continue

    print(f"  生成: {place} - {mood}...", end=" ", flush=True)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "music-2.6",
        "prompt": prompt,
        "is_instrumental": True,
        "output_format": "url",
        "aigc_watermark": False,
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                f"{BASE_URL}/v1/music_generation",
                headers=headers,
                json=payload,
                timeout=300,
            )
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}, retry...")
                time.sleep(5)
                continue
            data = resp.json()
            if data.get("base_resp", {}).get("status_code") != 0:
                print(f"API err, retry...")
                time.sleep(5)
                continue
            md = data.get("data", {})
            if md.get("status") != 2:
                print(f"status {md.get('status')}, retry...")
                time.sleep(5)
                continue
            url = md.get("audio", "")
            if not url:
                print("no url, retry...")
                time.sleep(5)
                continue
            audio = requests.get(url, timeout=180)
            if audio.status_code != 200:
                print(f"dl {audio.status_code}, retry...")
                time.sleep(5)
                continue
            with open(filepath, "wb") as f:
                f.write(audio.content)
            mb = len(audio.content) / (1024 * 1024)
            print(f"OK {mb:.1f} MB (attempt {attempt+1})")
            success += 1
            break
        except Exception as e:
            print(f"{type(e).__name__}, retry...")
            time.sleep(5)
    else:
        print(f"FAILED after 3 attempts")

    time.sleep(2)

print(f"\nretry: {success}/3")
