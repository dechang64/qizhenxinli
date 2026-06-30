"""继续批量生成疗愈音乐 - 断点续传

跳过已生成的文件，继续生成剩余的音乐
需要环境变量 MINIMAX_API_KEY — 切勿硬编码到代码里。
"""

import requests
import os
import time
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not API_KEY:
    raise SystemExit("需要 MINIMAX_API_KEY 环境变量")
BASE_URL = "https://api.minimaxi.com"

# 场景和情绪
SCENES = ["潇湘馆","蘅芜苑", "怡红院", "稻香村", "藕香榭", "秋爽斋"]
MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]

# 输出目录
OUTPUT_DIR = Path("static/music")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_music(place: str, mood: str) -> str | None:
    """生成单个音乐文件"""
    filename = f"{place}_{mood}.mp3"
    filepath = OUTPUT_DIR / filename

    # 跳过已存在的文件
    if filepath.exists():
        print(f"  跳过: {place} - {mood} (已存在)")
        return str(filepath)

    prompt = f"中国传统乐器演奏的{mood}氛围音乐，{place}场景，空灵悠远，适合冥想放松"

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

    print(f"  生成: {place} - {mood}...", end=" ", flush=True)

    try:
        resp = requests.post(
            f"{BASE_URL}/v1/music_generation",
            headers=headers,
            json=payload,
            timeout=180,
        )

        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}")
            return None

        data = resp.json()
        base_resp = data.get("base_resp", {})

        if base_resp.get("status_code") != 0:
            print(f"API error: {base_resp}")
            return None

        music_data = data.get("data", {})
        if music_data.get("status") != 2:
            print(f"Status: {music_data.get('status')}")
            return None

        audio_url = music_data.get("audio", "")
        if not audio_url:
            print("No URL")
            return None

        # 下载音频
        audio_resp = requests.get(audio_url, timeout=120)
        if audio_resp.status_code != 200:
            print(f"Download failed: {audio_resp.status_code}")
            return None

        # 保存文件
        with open(filepath, "wb") as f:
            f.write(audio_resp.content)

        size_mb = len(audio_resp.content) / (1024*1024)
        print(f"OK {size_mb:.1f} MB")

        return str(filepath)

    except requests.exceptions.Timeout:
        print("Timeout")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    print(f"继续批量生成音乐...")
    print(f"输出目录: {OUTPUT_DIR.absolute()}")
    print(f"总组合数: {len(SCENES)} x {len(MOODS)} = {len(SCENES) * len(MOODS)}")
    print()

    success = 0
    failed = 0
    skipped = 0

    for i, place in enumerate(SCENES):
        print(f"\n场景 {i+1}/{len(SCENES)}: {place}")
        for j, mood in enumerate(MOODS):
            result = generate_music(place, mood)
            if result:
                if "已存在" in result:
                    skipped += 1
                else:
                    success += 1
            else:
                failed += 1

            # 稍微等一下
            time.sleep(2)

    # 统计
    files = list(OUTPUT_DIR.glob("*.mp3"))

    print()
    print("=" * 50)
    print(f"完成!")
    print(f"新增成功: {success} | 跳过: {skipped} | 失败: {failed}")
    print(f"总计文件: {len(files)}")
    print(f"文件位置: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()