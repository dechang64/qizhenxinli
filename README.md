# 祺臻心理

> 社区心理咨询前台网络 v0.1 demo · 由 [dgy-treehole](https://github.com/dechang64/dgy-treehole) 复用改造

## 这是什么

给社区活动中心 / 企业 EAP / 学校心理辅导站**多社区**部署的触屏前台，由祺臻心理中心运营。每个点位是一个 AI 心理助手"祺臻小愈"，配合现场咨询师远程协同，主要解决：

1. **多社区协同**: 来访者可以约本社区或跨社区老师
2. **危机响应**: 关键 24h 心理热线 + 危机广播到所有在线咨询师
3. **数据合规**: 多社区案例库脱敏共享，咨询师间可会诊
4. **科普**: 每天 3 次心理常识播报，路径触达

## v0.1 demo 范围 (1 周内可跑)

| 模块 | 状态 |
|---|---|
| 复用 dgy-treehole Streamlit 框架 | ✅ |
| 中文 sidebar (主页/倾诉/树洞/共鸣/音乐/咨询师/危机) | ✅ |
| 咨询师后台 (mock 多社区数据) | ✅ (新) |
| 危机检测 mock 输入测试 | ✅ (新) |
| 24h 心理热线卡片 | ✅ (新) |
| 来访者 → 跨社区预约 UI | ❌ (Phase 1.1) |
| 真实 AI 危机模型 | ❌ (Phase 2) |
| 真实设备端固件 | ❌ (Phase 3) |

## 本地跑

```bash
pip install -r requirements.txt
streamlit run app.py
```

打开 http://localhost:8501

## 完整 PRD

见 [PRD_qizhenxinli.docx](./PRD_qizhenxinli.docx) 或 [PRD_qizhenxinli.md](./PRD_qizhenxinli.md)

## 复用来源

- 前端框架: [dgy-treehole](https://github.com/dechang64/dgy-treehole) v6.4
- 对话风格: 部分灵感来自 [reading-fl](https://github.com/dechang64/reading-fl)
- FedRAG (规划): [organoid-fl](https://github.com/dechang64/organoid-fl) 的向量检索 + 跨节点语义基础设施

## 不做什么

- ❌ 不做严肃心理治疗
- ❌ 不直接 2C 卖个人版
- ❌ 不替代真人咨询师

## License

待定
