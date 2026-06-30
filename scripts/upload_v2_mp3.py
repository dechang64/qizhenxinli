"""上传 10 段新 mp3 到 GitHub Release v1.0-music

跑: python scripts/upload_v2_mp3.py <GITHUB_PAT>
"""
import sys
import os
import requests
import json
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python upload_v2_mp3.py <GITHUB_PAT>")
    sys.exit(1)

PAT = sys.argv[1]
REPO = "dechang64/dgy-treehole"
TAG = "v1.0-music"
OUT_DIR = Path("data/mp3_v2")

headers = {
    "Authorization": f"Bearer {PAT}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# 1. 拿 release id
print(f"=== 拿 release {TAG} 信息 ===")
resp = requests.get(
    f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}",
    headers=headers,
)
resp.raise_for_status()
release = resp.json()
release_id = release["id"]
print(f"release id: {release_id}, name: {release.get('name')}\n")

# 2. 上传每个 mp3 (asset 名 = filename)
mp3s = sorted(OUT_DIR.glob("*_v2.mp3"))
print(f"待上传: {len(mp3s)} 个文件\n")

success = []
failed = []
for mp3 in mp3s:
    asset_name = mp3.name  # e.g. ouxxiangxie_ningjing_v2.mp3
    size_mb = mp3.stat().st_size / 1024 / 1024
    print(f"-> {asset_name} ({size_mb:.1f} MB)")

    upload_url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets"
    with open(mp3, "rb") as f:
        upload_headers = {
            **headers,
            "Content-Type": "audio/mpeg",
        }
        params = {"name": asset_name}
        try:
            r = requests.post(
                upload_url,
                headers=upload_headers,
                params=params,
                data=f.read(),
                timeout=600,
            )
            r.raise_for_status()
            asset = r.json()
            print(f"   OK -> {asset.get('browser_download_url')}\n")
            success.append(asset_name)
        except Exception as e:
            print(f"   FAILED: {type(e).__name__}: {str(e)[:200]}\n")
            failed.append(asset_name)

print(f"\n=== 完成: {len(success)}/{len(mp3s)} ===")
print(f"成功: {success}")
if failed:
    print(f"失败: {failed}")
