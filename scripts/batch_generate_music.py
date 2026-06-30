"""批量生成疗愈音乐 - 预生成所有场景×情绪组合

生成 6 场景 × 6 情绪 = 36 个音乐文件
"""

import requests
import os
import time
from pathlib import Path

# API 配置
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
BASE_URL = "https://api.minimaxi.com"

# 场景和情绪
SCENES = ["潇湘馆","蘅芜苑", "怡红院", "稻香村", "藕香榭", "秋爽斋"]
MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]

# 输出目录
OUTPUT_DIR = Path("static/music")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_music(place: str, mood: str) -> str | None:
    """生成单个音乐文件"""
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

    print(f"  生成中: {place} - {mood}...", end=" ", flush=True)

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
        filename = f"{place}_{mood}.mp3"
        filepath = OUTPUT_DIR / filename
        with open(filepath, "wb") as f:
            f.write(audio_resp.content)

        size_kb = len(audio_resp.content) / 1024
        print(f"OK {size_kb:.0f} KB")

        return str(filepath)

    except requests.exceptions.Timeout:
        print("Timeout")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    if not API_KEY:
        print("请设置环境变量 MINIMAX_API_KEY")
        return

    print(f"开始批量生成音乐...")
    print(f"输出目录: {OUTPUT_DIR.absolute()}")
    print(f"组合数量: {len(SCENES)} x {len(MOODS)} = {len(SCENES) * len(MOODS)}")
    print()

    success = 0
    failed = 0
    start_time = time.time()

    for i, place in enumerate(SCENES):
        print(f"\n场景 {i+1}/{len(SCENES)}: {place}")
        for j, mood in enumerate(MOODS):
            result = generate_music(place, mood)
            if result:
                success += 1
            else:
                failed += 1

            # 稍微等一下，避免请求过快
            time.sleep(2)

    elapsed = time.time() - start_time

    print()
    print("=" * 50)
    print(f"完成!")
    print(f"成功: {success} | 失败: {failed} | 耗时: {elapsed/60:.1f} 分钟")
    print(f"文件位置: {OUTPUT_DIR.absolute()}")

    # 列出生成的文件
    files = list(OUTPUT_DIR.glob("*.mp3"))
    print(f"\n已生成 {len(files)} 个文件:")
    for f in sorted(files):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()