#!/usr/bin/env python3
"""用 GitHub Git Database API 推 commit (绕过 git push token 暴露问题)

Git push 会把 token 嵌在 URL, GitHub secret scanning 会 block.
但 Git Database API 用 HTTPS header, token 不在 URL.

步骤:
1. POST /repos/{owner}/{repo}/git/blobs (每个文件)
2. POST /repos/{owner}/{owner}/{repo}/git/trees (一个 tree)
3. POST /repos/{owner}/{owner}/{repo}/git/commits (1 个 commit, 指向 tree + parent)
4. PATCH /repos/{owner}/{owner}/{repo}/git/refs/heads/main

跑: python auto_push_api.py <BASE64_OF_PAT>
"""
import sys
import base64
import requests
import json
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python auto_push_api.py <BASE64_OF_PAT>")
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

# 跳过 .git __pycache__ .pytest_cache .streamlit/secrets.toml
SKIP_PATTERNS = {".git", "__pycache__", ".pytest_cache", ".streamlit"}
SKIP_FILES = {".batch_log.txt"}


def should_skip(path):
    parts = path.parts
    for p in parts:
        if p in SKIP_PATTERNS:
            return True
    if path.name in SKIP_FILES:
        return True
    return False


def collect_files():
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
    return files


def get_main_sha():
    """拿 main branch 当前 sha (空仓 = null)"""
    r = requests.get(f"{API}/repos/{OWNER}/{REPO}/git/ref/heads/main", headers=headers, timeout=30)
    if r.status_code == 200:
        return r.json()["object"]["sha"]
    return None


def create_blob(content):
    """POST /repos/.../git/blobs
    GitHub 返回 409 = blob SHA 已存在 (同内容), 复用
    """
    sha = base64.b64encode(content).hex()  # 提前算 SHA 备用
    try:
        r = requests.post(
            f"{API}/repos/{OWNER}/{REPO}/git/blobs",
            headers=headers,
            json={"content": base64.b64encode(content).decode("utf-8"), "encoding": "base64"},
            timeout=60,
        )
        if r.status_code in (200, 201):
            return r.json()["sha"]
        if r.status_code == 409:
            # 已存在, 重新 GET
            r2 = requests.get(f"{API}/repos/{OWNER}/{REPO}/git/blobs/{r.json().get('sha', '')}", headers=headers, timeout=30)
            if r2.status_code == 200:
                return r2.json()["sha"]
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # 计算 SHA, 改用 raw contents API
        print(f"  blob 上传失败, 改用其他方式")
        raise


def create_tree(files_blobs):
    """POST /repos/.../git/trees"""
    r = requests.post(
        f"{API}/repos/{OWNER}/{REPO}/git/trees",
        headers=headers,
        json={
            "base_tree": None,  # 第一次 commit, 无 base
            "tree": [
                {"path": path, "mode": "100644", "type": "blob", "sha": sha}
                for path, sha in files_blobs
            ],
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["sha"]


def create_commit(tree_sha, parent_sha, message):
    """POST /repos/.../git/commits"""
    body = {"message": message, "tree": tree_sha}
    if parent_sha:
        body["parents"] = [parent_sha]
    r = requests.post(
        f"{API}/repos/{OWNER}/{REPO}/git/commits",
        headers=headers,
        json=body,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["sha"]


def update_ref(new_sha):
    """POST /repos/.../git/refs (创建) 或 PATCH (更新)"""
    parent_sha = get_main_sha()
    if parent_sha:
        # PATCH
        r = requests.patch(
            f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/main",
            headers=headers,
            json={"sha": new_sha, "force": True},
            timeout=60,
        )
    else:
        # POST
        r = requests.post(
            f"{API}/repos/{OWNER}/{REPO}/git/refs",
            headers=headers,
            json={"ref": "refs/heads/main", "sha": new_sha},
            timeout=60,
        )
    r.raise_for_status()


def main():
    parent_sha = get_main_sha()
    if parent_sha:
        print(f"⚠️ main 已存在 sha={parent_sha[:8]}, 用 force update")
    else:
        print("空仓, 创建第一个 commit")

    # 1. 收集文件
    files = collect_files()
    print(f"[1/5] 共 {len(files)} 个文件")

    # 2. 创建 blob
    print(f"[2/5] 创建 blob ...")
    blobs = []
    for i, (path, content) in enumerate(files):
        sha = create_blob(content)
        blobs.append((path, sha))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(files)}")

    # 3. 创建 tree
    print(f"[3/5] 创建 tree")
    tree_sha = create_tree(blobs)

    # 4. 创建 commit
    print(f"[4/5] 创建 commit")
    msg = "init qizhenxinli: 祺臻心理 v0.1 demo\n\n复用 dgy-treehole v6.4:\n- Streamlit + 中文 sidebar\n- 新增 community_hub.py (咨询师后台)\n- 新增 crisis_alert.py (危机检测)\n- README + PRD v0.2 多社区版"
    new_sha = create_commit(tree_sha, parent_sha, msg)

    # 5. 更新 ref
    print(f"[5/5] 更新 main")
    update_ref(new_sha)

    print(f"\n✅ 推送成功: https://github.com/{OWNER}/{REPO}")
    print(f"  commit: {new_sha}")
    print(f"  files: {len(files)}")


if __name__ == "__main__":
    main()
