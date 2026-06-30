"""测试 GitHub release 中文 asset URL"""
import requests

RELEASE_BASE = "https://github.com/dechang64/dgy-treehole/releases/download/v1.0-music"

# 测试 1: 不编码 (浏览器/requests 会自动处理 unicode url?)
url1 = f"{RELEASE_BASE}/蘅芜苑_沉思.mp3"
# 测试 2: 编码
from urllib.parse import quote
url2 = f"{RELEASE_BASE}/{quote('蘅芜苑_沉思.mp3')}"
# 测试 3: 下载 release-info
info_url = "https://api.github.com/repos/dechang64/dgy-treehole/releases/tags/v1.0-music"

print("--- url1 (raw chinese) ---")
try:
    r = requests.head(url1, timeout=30, allow_redirects=True)
    print(f"  {r.status_code} {r.headers.get('Content-Length')}")
except Exception as e:
    print(f"  FAIL: {e}")

print("--- url2 (percent-encoded) ---")
try:
    r = requests.head(url2, timeout=30, allow_redirects=True)
    print(f"  {r.status_code} {r.headers.get('Content-Length')}")
except Exception as e:
    print(f"  FAIL: {e}")

print("--- info (api) ---")
try:
    r = requests.get(info_url, timeout=30)
    r.raise_for_status()
    data = r.json()
    assets = data.get("assets", [])
    print(f"  release: {data.get('name')}, assets: {len(assets)}")
    for a in assets[:5]:
        print(f"    - name='{a.get('name')}' size={a.get('size')}")
    # 找 1 个中文
    for a in assets:
        if "蘅芜苑" in a.get("name", ""):
            print(f"  found 蘅芜苑: {a.get('name')} -> {a.get('browser_download_url')}")
            break
except Exception as e:
    print(f"  FAIL: {e}")
