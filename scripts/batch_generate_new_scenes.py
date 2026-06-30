"""为 3 个新场景生成疗愈音乐（6 情绪 × 3 院 = 18 首）

新场景的 prompt 模板：每个院有自己的"乐器+氛围"配色，避免 prompt 跟场景脱节。
- 栊翠庵：禅意、清冷、钟磬、木鱼
- 缀锦楼：绣线、丝竹、柔美、闺阁
- 紫菱洲：水波、菱花、温柔、柔软

跳过已存在的文件（断点续传）。
需要环境变量 MINIMAX_API_KEY — 切勿硬编码到代码里。
"""

import os
import requests
import time
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not API_KEY:
    raise SystemExit("需要 MINIMAX_API_KEY 环境变量")
BASE_URL = "https://api.minimaxi.com"

# 3 个新场景
NEW_SCENES = ["栊翠庵", "缀锦楼", "紫菱洲"]
MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]

# 输出目录
OUTPUT_DIR = Path("static/music")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 每个新场景的 prompt 模板（按 mood 调色）──
SCENE_PROMPTS = {
    "栊翠庵": {
        "宁静":  "古寺禅意，远处钟磬声回荡，木鱼轻敲如雨点，雪落空山，松风入林，极静极远，无人声，无鼓点",
        "释然":  "古寺晨雾散去，禅房檀香袅袅，木鱼由密转疏，钟磬余音渐远，顿悟后的安宁，无人声",
        "思念":  "禅房孤灯，窗外竹影摇曳，远处古琴一声叹息，檀香与月光，无人声，淡淡的怅然",
        "疗愈":  "古寺梵音轻唱，木鱼节奏如呼吸，铜磬一响一收，山间流水，疗愈疲惫的心，无人声",
        "欢愉":  "禅寺早课，铃铛与木鱼齐鸣，明亮欢喜，晨光初照，鸟鸣点缀，喜悦但不喧闹",
        "沉思":  "古寺黄昏，木鱼疏落，钟磬悠长，禅意沉思，无人声，适合冥想",
    },
    "缀锦楼": {
        "宁静":  "绣楼静夜，月光透过绣帘，古筝低吟，丝线轻响，闺阁安然，无人声",
        "释然":  "绣完最后一针，长舒一口气，古琴轻拨，窗前茉莉飘香，释怀的午后",
        "思念":  "绣楼独坐，手拈针线望向远方，二胡低诉，丝竹细语，闺中思念，无人声",
        "疗愈":  "绣楼午后，丝竹轻音乐，针线穿梭如流水，温暖包裹，疗愈内耗的心",
        "欢愉":  "绣楼清晨，鸟鸣啾啾，丝竹欢快，彩线翻飞，少女的喜悦，明亮轻盈",
        "沉思":  "绣楼黄昏，独对一盏灯，琵琶慢捻，丝竹沉思，细腻的内心独白",
    },
    "紫菱洲": {
        "宁静":  "菱洲水波，碧水清浅，古琴泛音如水面涟漪，菱花轻摇，无人声",
        "释然":  "菱洲晨光，水面雾气散开，箫声悠远，温柔地放过自己",
        "思念":  "菱洲黄昏，菱花映残照，琵琶低语，水波轻拍，柔软的乡愁与自怜",
        "疗愈":  "菱洲水岸，温柔的古琴与水声交织，把委屈轻轻包住，慢慢放下",
        "欢愉":  "菱洲夏日，菱花盛开，笛子明亮，水波欢快，温柔的喜悦",
        "沉思":  "菱洲月夜，水面如镜，箫与古琴对答，与自己温柔对话",
    },
}


def generate_music(place: str, mood: str) -> str | None:
    """生成单个音乐文件"""
    filename = f"{place}_{mood}.mp3"
    filepath = OUTPUT_DIR / filename

    # 跳过已存在的文件
    if filepath.exists():
        print(f"  跳过: {place} - {mood} (已存在)")
        return str(filepath)

    # 用 scene-specific prompt
    prompt = SCENE_PROMPTS[place][mood]

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
            print(f"HTTP {resp.status_code}: {resp.text[:200]}")
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
    print(f"为 3 个新场景生成疗愈音乐...")
    print(f"输出目录: {OUTPUT_DIR.absolute()}")
    print(f"总组合数: {len(NEW_SCENES)} x {len(MOODS)} = {len(NEW_SCENES) * len(MOODS)}")
    print()

    success = 0
    failed = 0
    skipped = 0

    for i, place in enumerate(NEW_SCENES):
        print(f"\n场景 {i+1}/{len(NEW_SCENES)}: {place}")
        for j, mood in enumerate(MOODS):
            result = generate_music(place, mood)
            if result:
                # 通过"已存在"判断跳过的逻辑（filepath.exists 检查在函数内）
                if (OUTPUT_DIR / f"{place}_{mood}.mp3").exists():
                    # 看是这次新生成还是之前就存在
                    # 简单判断：如果是新生成 success+=1, 跳过 skipped+=1
                    # 用文件 mtime 区分
                    import os
                    filepath = OUTPUT_DIR / f"{place}_{mood}.mp3"
                    mtime = filepath.stat().st_mtime
                    if time.time() - mtime < 60:  # 1 分钟内新建的
                        success += 1
                    else:
                        skipped += 1
            else:
                failed += 1

            time.sleep(2)

    # 统计
    files = list(OUTPUT_DIR.glob("*.mp3"))
    new_files = [f for f in files if any(s in f.name for s in NEW_SCENES)]

    print()
    print("=" * 50)
    print(f"完成!")
    print(f"新增成功: {success} | 跳过: {failed and 0 or 0} | 失败: {failed}")
    print(f"新场景文件数: {len(new_files)}/18")
    print(f"文件位置: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
