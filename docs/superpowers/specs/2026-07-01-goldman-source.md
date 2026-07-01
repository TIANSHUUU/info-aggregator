# 新增信息源：高盛 Goldman Sachs Insights 设计

> 在 info 主页新增一条源「高盛」，抓 Goldman Sachs `/insights` 的最新文章，
> 以 **Charles Schwab 同款方式**呈现（文章列表：中文标题 + 中文摘要 + 相对时间 + 前往源站）。
>
> 状态：✅ 已与用户确认——文章（非播客）、像 Schwab、中文翻译、显示名「高盛」、放 Schwab 之后、最新 8 篇（2026-07-01）。

## 1. 目标与可行性（已验证）

- 目标：主页加「高盛」源，展示 Goldman Insights 最新文章的中文标题 + 摘要。
- **可行性调查结论**：
  - `https://www.goldmansachs.com/insights` 返回 HTTP 200、无任何反爬（无 Cloudflare/Akamai/captcha），不像 HKET/明报。
  - 文章正文是 JS 渲染（抓不到），**但**首页的 `<script id="__NEXT_DATA__">` 内嵌 JSON 含文章元数据：解析后可提取 **15 条带 `publishDate` + `title` + `description` + `url` 的条目**（无需 JS 渲染）。
  - 因此走"解析 __NEXT_DATA__ 拿标题+摘要"，而非抓正文。

## 2. 架构与数据流

```
GET https://www.goldmansachs.com/insights  (requests, 浏览器 UA)
  → 提取 <script id="__NEXT_DATA__"> 的 JSON
  → 递归收集含 publishDate + title 的对象 {title, description, url, publishDate}
  → 过滤（纯文章 + 有摘要）→ 按 publishDate 降序 → 取最新 8 篇
  → 逐篇用 Google 翻译把 title + description 译成中文（复用 Schwab 的 _translate_to_zh）
  → 返回 [{title(中), url(绝对), date(ISO), summary(中)}]
写入 public/data/goldman.json；前端用 NewsSection(showSummary=true) 呈现。
```

## 3. 组件

### 3.1 `scripts/fetch_goldman.py`（新建，参照 fetch_schwab.py 的翻译）

职责：抓首页 → 解析 __NEXT_DATA__ → 过滤/排序/取 8 → 翻译 → 返回列表。

要点：
- `LIST_URL = "https://www.goldmansachs.com/insights"`，`BASE_URL = "https://www.goldmansachs.com"`。
- HEADERS 用完整浏览器 UA（同 fetch_schwab/fetch_hket 风格）。
- 提取 JSON：`re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)` → `json.loads`。
- 递归遍历（dict/list），收集满足条件的对象：有 `publishDate`（或 `publishedDate`）+ 字符串 `title` + `description`（非空）+ `url`。按 `title` 去重。
- **过滤（纯文章、去多媒体）**：排除 `url` 含 `goldman-sachs-exchanges`（播客）、`/videos/`、`talks-at-gs`（访谈）的条目；其余保留（`/insights/articles/`、`/insights/the-markets/` 等文字文章）。
- **排序取新**：按 `publishDate` 降序，取前 **8** 篇。
- **绝对化 url**：`BASE_URL + path`（path 以 `/` 开头时）。
- **翻译**：复用 fetch_schwab 的 `_translate_to_zh(text, session)`（`translate.googleapis.com`，en→zh-CN，截断 500 字）。对 `title` 与 `description` 各翻译一次；翻译失败（返回 None）则**回退英文原文**。
- 返回 `[{"title": 中文标题, "url": 绝对url, "date": publishDate, "summary": 中文摘要}]`。
- `date` 用 `publishDate` 原值（形如 `2026-06-18`，前端 `dayjs().fromNow()` 可解析）。

> 复用方式：`_translate_to_zh` 直接在 fetch_goldman.py 内复制一份同样的函数（保持各 fetcher 自包含，与现有风格一致），不跨文件 import。

### 3.2 `scripts/fetch_all.py`（改）

- 顶部加 `import fetch_goldman`（放 `import fetch_schwab` 之后）。
- `sources` dict 里 `"schwab"` 之后加 `"goldman": fetch_goldman.fetch,`（它返回 list，与其它新闻源一致，走通用的 list 写入逻辑）。

### 3.3 `src/App.jsx`（改 SOURCES）

在 `schwab` 条目之后插入：
```js
{ key: 'goldman', title: '高盛', source: 'https://www.goldmansachs.com/insights', showSummary: true },
```
新顺序：财新 → Charles Schwab → **高盛** → 端传媒 → Gorozen → 🇦🇺 Equity Mates。前端自动用 `NewsSection`（非 podcast key）+ `showSummary=true`，呈现同 Schwab。

## 4. 错误处理

- 抓取/解析失败 → 由 `fetch_all.py` 的 `run_fetcher` 兜住，返回 `[]` → 前端「今日暂无更新」。
- 单篇翻译失败 → 回退英文原文（不影响该篇展示）。
- 若某次首页精选里文章类不足 8 篇 → 有几篇取几篇。

## 5. 验证

- 本地跑 `fetch_goldman.fetch()`：应返回约 6–8 篇，中文标题 + 中文摘要 + 日期 + 绝对 url。
- `npm run build` 通过。
- 部署后 CI 日志 `[goldman] OK — N items`；线上「高盛」区有内容、位于 Schwab 之后。

## 6. 明确不做（YAGNI）

- 不抓文章正文（JS 渲染）、不做正文级 AI 提炼——摘要即 Goldman 自带 description 的翻译。
- 不引入 headless 浏览器、不调 Goldman 的异步 API。
- 不改视觉/其它源/Worker。

## 7. 涉及文件

| 文件 | 改动 |
|---|---|
| `scripts/fetch_goldman.py` | 新建 |
| `scripts/fetch_all.py` | +import +sources 一条 |
| `src/App.jsx` | SOURCES +一条（Schwab 后） |
