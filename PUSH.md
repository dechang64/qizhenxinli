# 祺臻心理 — 推送步骤 (手动跑)

## 1. 创仓库 (一次性, Web UI)

浏览器打开: https://github.com/new

填:
- Repository name: `qizhenxinli`
- Description: `祺臻心理 — 社区心理咨询前台网络 v0.1 demo`
- ❌ 取消 Add README (本地已有)
- ❌ 取消 Add .gitignore
- ❌ 取消 Choose license
- 点 **Create repository**

## 2. 本地 git init + commit + push

打开 PowerShell, 跑以下 (一行一行):

```powershell
cd C:\Users\decha\.mavis\agents\mavis\workspace\qizhenxinli

# 初始化 git
git init -b main
git config user.email "dechang64@users.noreply.github.com"
git config user.name "Dechang Xu"

# 加所有文件
git add -A

# 看要提交的清单
git status --short

# 提交
git commit -m "init qizhenxinli: 祺臻心理 v0.1 demo

复用 dgy-treehole v6.4:
- 复用 Streamlit + 中文 sidebar
- 新增 community_hub.py (咨询师后台)
- 新增 crisis_alert.py (危机检测)
- README + PRD v0.2 多社区版"

# 设 remote (用你之前给我的 PAT, 这样不用输密码)
git remote add origin https://github.com/dechang64/qizhenxinli.git

# push (会跳出凭证, 把 PAT 当密码粘进去)
git push -u origin main
```

## 3. 推送成功

去 https://github.com/dechang64/qizhenxinli 看.

## 4. (可选) 部署 streamlit cloud

打开: https://share.streamlit.io/deploy?repository=dechang64/qizhenxinli&branch=main&mainModule=app.py

## 备注

- 整个目录只有 **0.58 MB** (清过 800+ MB mp3 残留)
- 50 个文件, Streamlit AppTest **0 exceptions**
- PRD 在 `PRD_qizhenxinli.md` / `.docx`
