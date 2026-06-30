#!/usr/bin/env python3
"""用 GitHub Contents API 推多个文件 (逐个 PUT, 简单且避免 git push token 问题)

步骤: 对每个文件 PUT /repos/{owner}/{repo}/contents/{path}
跑: python auto_push_contents.py <BASE64_OF_PAT>
"""
import sys
import base64
import requests
import time
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python auto_push_contents.py <BASE64_OF_PAT>")
    sys.exit(1)

try:
    PAT = base64.b64decode(sys.argv[1]).decode("utf-8")
except Exception as e:
    print(f"Invalid base64: {e}")
    sys.exit(1)

OWNER = "dechang64"
REPO = "qizhenxinli"
SRC = Path("C:/Users/decha/.mavis/agents/mavis/workspace/qizhenxinli")

API = "https://api.github.com"
headers = {
    "Authorization": f"Bearer {PAT}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# 跳过 .git __pycache__ .pytest_cache
SKIP_PATTERNS = {".git", "__pycache__", ".pytest_cache", "static"}


def should_skip(path):
    parts = path.parts
    for p in parts:
        if p in SKIP_PATTERNS:
            return True
    return False


def put_file(rel_path, content):
    """PUT 单个文件 (创建时不需要 SHA, 更新需要)
    rel_path 用 POSIX 风格 (/)
    """
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{rel_path}"
    body = {
        "message": f"add {rel_path}",
        "content": base64.b64encode(content).decode("utf-8"),
    }
    # 检查是否已存在
    r0 = requests.get(url, headers=headers, timeout=30)
    if r0.status_code == 200:
        body["sha"] = r0.json()["sha"]
    r = requests.put(url, headers=headers, json=body, timeout=60)
    if r.status_code in (200, 201):
        return True
    print(f"  ❌ {r.status_code} {rel_path}: {r.json().get('message','')[:100]}")
    return False


def main():
    # 收集文件
    files = []
    for path in SRC.rglob("*"):
        if path.is_file():
            rel = path.relative_to(SRC)
            if should_skip(rel):
                continue
            try:
                content = path.read_bytes()
            except Exception as e:
                print(f"  skip {rel}: {e}")
                continue
            files.append((str(rel).replace("\\", "/"), content))
    print(f"共 {len(files)} 个文件 (skip .git, __pycache__, static)")

    # 第 1 推 README (后续 commit message 链)
    readme = next((f for f in files if f[0] == "README.md"), None)
    if readme:
        ok = put_file("README.md", readme[1])
        if ok:
            print(f"  ✅ README.md")
        files = [f for f in files if f[0] != "README.md"]

    # 推其余
    success = 1 if readme else 0
    for i, (path, content) in enumerate(files):
        # 跳过太大的单文件 (>5MB Contents API 不允许)
        if len(content) > 5 * 1024 * 1024:
            print(f"  skip {path}: too big ({len(content)/1024/1024:.1f} MB)")
            continue
        if put_file(path, content):
            success += 1
            if (i + 1) % 5 == 0:
                print(f"  {success}/{len(files)} done")
        time.sleep(0.2)  # 限流

    print(f"\n✅ 完成: {success}/{len(files)}")
    print(f"📍 https://github.com/{OWNER}/{REPO}")


if __name__ == "__main__":
    main()
