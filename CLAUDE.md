# CLAUDE.md — 项目上下文（每日资讯聚合站）

> 新对话读这份就能 pickup。用**中文**跟用户交流（用户是外行、非技术，解释要通俗）。

## 这是什么

个人用的**每日资讯聚合网页**，静态站部署在 GitHub Pages：
- 线上：https://tianshuuu.github.io/info-aggregator/
- 仓库：`TIANSHUUU/info-aggregator`（public）
- 一个页面：顶部实时行情 + 若干信息源（新闻列表 / 播客摘要），全中文。

## 技术栈 & 数据流

React 18 + Vite 6 + Tailwind v3（前端）｜Python（抓取脚本）｜GitHub Actions（构建部署）｜Cloudflare Worker（手动刷新触发）。

```
Python 抓取(scripts/fetch_*.py) → 写 public/data/*.json → Vite build → 部署 GitHub Pages
```
**数据不 commit 回 repo**：CI 每次现抓、打包、部署；repo 里的 `public/data/*.json` 只是历史快照。

## 部署（重要）

- Workflow：`.github/workflows/update.yml`，跑 `fetch_all.py`（抓所有源）→ `npm run build` → 部署 Pages。
- 触发：① 每日 `cron: '41 3 * * *'`（03:41 UTC ≈ 墨尔本 13:41；GitHub schedule 常延迟数小时，属正常）② 手动 `gh workflow run update.yml --ref main` ③ 站内「立即更新」按钮。
- **合并到 main 不会自动部署**，需手动触发 workflow 才上线。
- 部署验证：`gh run watch <id> --exit-status`，看日志 `[<source>] OK — N items`。

## 当前信息源（顺序即 App.jsx 的 SOURCES）

实时行情 → 财新 → Charles Schwab → **高盛** → 端传媒 → Gorozen → 🇦🇺 Equity Mates

| key | 显示名 | 抓法 | 摘要 |
|---|---|---|---|
| `caixin` | 财新 | leafduo JSON feed | feed 自带 |
| `schwab` | Charles Schwab | HTML + Google 翻译 | 有（中译） |
| `goldman` | 高盛 | 解析 `/insights` 的 `__NEXT_DATA__` JSON + Google 翻译 | 有（中译） |
| `initium` | 端传媒 | RSS | 无 |
| `gorozen` | Gorozen | HTML | 有 |
| `equitymates` | 🇦🇺 Equity Mates | Acast 播客 RSS + **Groq LLM 摘要** | 播客分节摘要 |
| `stocks` | 实时行情 | — | — |

## 加/改信息源的模式（小改动，走轻量流程）

用户希望这类小改动**不写正式 spec/plan**，轻量走：**先验证 CI 能抓 → 问关键偏好（显示名/语言/位置）→ 实现 → 本地实测 + 部署看日志**。

1. `scripts/fetch_<key>.py`：`fetch()` 返回 `list[{title,url,date,summary?}]`（新闻）或单个 `dict`（播客，见 fetch_equitymates）。
2. `scripts/fetch_all.py`：加 `import` + `sources` dict 一条（决定抓取；播客类单独 dict 写入，见文件末尾 equitymates 块）。
3. `src/App.jsx` 的 `SOURCES`：加一条 `{ key, title, source, showSummary }`（`showSummary:true` → 显示摘要）。播客用 `PodcastSection`（在 App.jsx 里按 key 分支），新闻用 `NewsSection`（默认）。
4. 中译摘要：复用各 fetcher 里的 `_translate_to_zh(text, session)`（`translate.googleapis.com`，免费）。
5. **务必先本地实测** `fetch_<key>.fetch()` 抓到内容再接入（见下"反爬教训"）。

## 反爬教训（别再踩）

服务端（GitHub Actions 美国机房 IP）抓取会被一些站点反爬拦：
- **HKET**：地理相关 IP 封锁（机房/甚至 Cloudflare 美国 colo 出口都 405）→ 已移除。
- **明报**：Cloudflare Challenge，连住宅 IP 脚本都 403 → 停用（`fetch_mingpao.py`/`mingpao.json` 在 repo 但没接入）。
- **规则**：加新抓取源前，先在 CI 视角确认能抓（本地能抓 ≠ CI 能抓，因 IP 不同）。优先选有 RSS/JSON feed、或数据内嵌在 HTML（如 `__NEXT_DATA__`）的源。

## AI 摘要（Groq）

只有 `fetch_equitymates.py` 用 Groq LLM 生成中文分节摘要。模型 `openai/gpt-oss-120b`（`llama-3.3-70b-versatile` 于 2026-08-16 停用后迁移），fallback `llama-3.1-8b-instant`（兜任何主模型失败）。key 是 Actions secret `GROQ_API_KEY`（本地在 `.env.local`）。换模型先本地端到端测 `fetch_equitymates.fetch()`。

## 「立即更新」按钮 & Cloudflare Worker

前端按钮 POST → Cloudflare Worker `https://infoaggre-refresh.tianshu-tan.workers.dev` → 触发 `workflow_dispatch`。**token 只在 Worker 加密 secret，不进前端 bundle**（历史上曾把 `VITE_GITHUB_TOKEN` 打进公开 JS，已修复）。Worker 代码在 `worker/`（改后需 `cd worker && npx wrangler deploy`，这步只有用户能做）。前端点按钮后轮询 `meta.json` 等抓取完成。

## 视觉 / 设计系统

见项目根 `design.md`（"Coffee Crema Fusion" 双油墨 zine：terracotta 主 / 橙高亮 / 蓝仅用于标题 hover；标题衬线、正文黑体、标签 Geist Mono）。改视觉按它来。

## 工作约定

- 每个改动**开分支 → PR → 合并**（不在 main 直接改）；提交 message 末尾带 `Co-Authored-By: Claude`。
- 改完抓取/前端后**触发一次部署并看 CI 日志**确认，再声明成功（有据）。
- 关键命令：`npm run build`（构建）｜`gh workflow run update.yml --ref main`（部署）｜`gh run watch <id> --exit-status`（盯部署）。
