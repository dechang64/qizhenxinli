"""上传 18 个新场景音乐到 GitHub Release v1.0-music

GitHub Releases 不支持非 ASCII 文件名下载（URL 404）。
所以把中文文件名复制/重命名为 pinyin 形式再上传 — 与 pages/2_treehole.py + pages/4_music.py
的 FILENAME_MAP 保持一致。

需要环境变量 GITHUB_TOKEN (PAT) — 切勿硬编码到代码里。
"""
import os
import sys
import shutil
import time
import requests
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")  # 从环境变量读，不写死在代码里
OWNER = "dechang64"
REPO = "dgy-treehole"
TAG = "v1.0-music"
RELEASE_ID = 335551514
UPLOAD_URL = f"https://uploads.github.com/repos/{OWNER}/{REPO}/releases/{RELEASE_ID}/assets"
LIST_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/{RELEASE_ID}/assets"

# ── pinyin 映射（必须跟 pages/2_treehole.py + pages/4_music.py 的 FILENAME_MAP 一致）──
PY_MAP = {
    ("栊翠庵", "宁静"): "longcuian_ningjing.mp3",
    ("栊翠庵", "释然"): "longcuian_shiran.mp3",
    ("栊翠庵", "思念"): "longcuian_sinian.mp3",
    ("栊翠庵", "疗愈"): "longcuian_liaoyu.mp3",
    ("栊翠庵", "欢愉"): "longcuian_huanyu.mp3",
    ("栊翠庵", "沉思"): "longcuian_chensi.mp3",
    ("缀锦楼", "宁静"): "zhuilou_ningjing.mp3",
    ("缀锦楼", "释然"): "zhuilou_shiran.mp3",
    ("缀锦楼", "思念"): "zhuilou_sinian.mp3",
    ("缀锦楼", "疗愈"): "zhuilou_liaoyu.mp3",
    ("缀锦楼", "欢愉"): "zhuilou_huanyu.mp3",
    ("缀锦楼", "沉思"): "zhuilou_chensi.mp3",
    ("紫菱洲", "宁静"): "zilingzhou_ningjing.mp3",
    ("紫菱洲", "释然"): "zilingzhou_shiran.mp3",
    ("紫菱洲", "思念"): "zilingzhou_sinian.mp3",
    ("紫菱洲", "疗愈"): "zilingzhou_liaoyu.mp3",
    ("紫菱洲", "欢愉"): "zilingzhou_huanyu.mp3",
    ("紫菱洲", "沉思"): "zilingzhou_chensi.mp3",
}

NEW_SCENES = ["栊翠庵", "缀锦楼", "紫菱洲"]
MOODS = ["宁静", "释然", "思念", "疗愈", "欢愉", "沉思"]
MUSIC_DIR = Path("static/music")
TMP_DIR = Path("static/music/_pinyin_tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)


def list_existing_assets() -> set[str]:
    resp = requests.get(
        LIST_URL,
        headers={"Authorization": f"token {TOKEN}"},
        params={"per_page": 100},
    )
    if resp.status_code != 200:
        return set()
    return {a["name"] for a in resp.json()}


def delete_asset(asset_id: int) -> bool:
    resp = requests.delete(
        f"{LIST_URL}/{asset_id}",
        headers={"Authorization": f"token {TOKEN}"},
    )
    return resp.status_code == 204


def cleanup_bad_uploads():
    """删除 _.*.mp3 这种错文件（unicode 解析失败的产物）"""
    resp = requests.get(
        LIST_URL,
        headers={"Authorization": f"token {TOKEN}"},
        params={"per_page": 100},
    )
    deleted = 0
    for a in resp.json():
        name = a["name"]
        # _.mp3 是 unicode 失败的产物
        if name in ("_.mp3",) or (name.startswith("_") and name.endswith(".mp3")):
            print(f"  delete bad: {name}")
            if delete_asset(a["id"]):
                deleted += 1
    return deleted


def upload_asset(filepath: Path, upload_name: str) -> bool:
    """上传单个文件，可指定不同的 name"""
    size = filepath.stat().st_size
    print(f"  上传: {upload_name} ({size/(1024*1024):.1f} MB)...", end=" ", flush=True)

    with open(filepath, "rb") as f:
        url = f"{UPLOAD_URL}?name={upload_name}"
        resp = requests.post(
            url,
            headers={
                "Authorization": f"token {TOKEN}",
                "Content-Type": "application/octet-stream",
            },
            data=f,
            timeout=300,
        )

    if resp.status_code in (201, 202):
        actual = resp.json().get("name", "?")
        if actual == upload_name:
            print("OK")
            return True
        else:
            print(f"WRONG NAME: {actual!r}")
            asset_id = resp.json().get("id")
            if asset_id:
                delete_asset(asset_id)
            return False
    else:
        print(f"HTTP {resp.status_code}: {resp.text[:200]}")
        return False


def main():
    print("=== Step 1: 清理之前的错文件 ===")
    deleted = cleanup_bad_uploads()
    print(f"  删除: {deleted}\n")

    print("=== Step 2: 准备 pinyin 命名的临时文件 ===")
    pinyin_files = []
    for place in NEW_SCENES:
        for mood in MOODS:
            cn_name = f"{place}_{mood}.mp3"
            src = MUSIC_DIR / cn_name
            if not src.exists():
                print(f"  缺: {cn_name}")
                continue
            py_name = PY_MAP[(place, mood)]
            dst = TMP_DIR / py_name
            shutil.copy2(src, dst)
            pinyin_files.append((dst, py_name))
            print(f"  {cn_name} -> {py_name}")
    print(f"\n  共 {len(pinyin_files)} 个临时文件\n")

    print("=== Step 3: 上传到 Release ===")
    existing = list_existing_assets()
    print(f"  Release 当前 assets: {len(existing)} 个\n")

    success = 0
    skipped = 0
    failed = 0

    for filepath, pinyin_name in pinyin_files:
        if pinyin_name in existing:
            print(f"  跳过: {pinyin_name}")
            skipped += 1
            continue
        if upload_asset(filepath, pinyin_name):
            success += 1
        else:
            failed += 1
        time.sleep(1)

    print(f"\n=== Step 4: 清理临时文件 ===")
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    print(f"  删除: {TMP_DIR}\n")

    print(f"{'='*50}")
    print(f"完成! 新增: {success} | 跳过: {skipped} | 失败: {failed}")


if __name__ == "__main__":
    main()
