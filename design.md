# 每日资讯 · 设计系统（Design System）

> **Coffee Crema Fusion** — warm editorial + two-ink zine energy
> 设计语言锁定文档。新增/改动任何页面、组件，都以本文件为准。
>
> - **落地方向：C「硬朗双油墨 Zine」**（见 §3–§7）
> - 备选方向 B「社论排版 Editorial」完整规格保留于 **附录 A**，以后可切换。
> - 字体：标题衬线（Fraunces / 宋体），正文黑体（Newsreader / 苹方），标签等宽（Geist Mono）。
> - 颜色角色：**terracotta 主强调 · 橙色高亮 · 蓝色仅作标题 hover 投影**。
>
> 状态：✅ 已与用户确认方向、字体、配色、scope（2026-06-24）。本次只做视觉层，不动数据抓取与组件逻辑。安全隐患见 **附录 B**（独立后续任务）。

---

## 1. 设计目标与原则

- **目标**：在保持现有信息结构「清晰、现代」的前提下，做一次纯视觉 overhaul，让站点呈现 sleek newspaper / 双油墨 zine 的编辑气质。
- **范围**：仅视觉层 —— 颜色、字体、间距、章节装置、交互态。**不改**数据格式、抓取脚本、组件逻辑、信息架构、按钮功能。
- **原则**：
  - 双油墨克制：terracotta + blue 是仅有的两种"油墨"，其余靠墨黑 / 纸色 / 细线撑结构。
  - 字体分工严格：标题=衬线，正文=黑体，标签/数字/源站名=等宽。
  - 报纸装置点到为止：grain、offset 重影、硬投影、描边 stamp 都低强度，不喧宾夺主。

---

## 2. 实现集成方式（不改逻辑，只换皮）

视觉层落在三处，组件 JSX 结构基本不动，只改 className / 包一层：

| 文件 | 改动 |
| --- | --- |
| `index.html` | `<head>` 加 Google Fonts（仅拉丁字形）；`<title>` 不变。 |
| `tailwind.config.js` | `theme.extend` 加 `colors`、`fontFamily`（见 §3）。 |
| `src/index.css` | 重写 `@layer base` 与 `@layer components`：纸色背景 + grain；`.card` 退役，新增 `.sec-bar-news / .sec-bar-cast / .sec-bar-mkt / .news-row / .headline / .quote-cell` 等组件类。 |
| `src/components/*.jsx` | 仅替换 className、调整少量包裹元素（如章节条结构、编号 `<span>`）。逻辑、状态、数据流不动。 |

**中文字体策略**：拉丁字形（Fraunces / Newsreader / Geist Mono）走 Web Font；**中文走系统字体栈**（标题 `Songti SC`/`Noto Serif SC`，正文 `PingFang SC`），不额外加载体积巨大的中文 Web Font。

```html
<!-- index.html <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

---

## 3. Design Tokens

### 3.1 颜色（CSS 变量，oklch）

```css
:root{
  /* 纸与线 */
  --color-paper:    oklch(97%   0.012 75);  /* 页面底色 */
  --color-paper-2:  oklch(94.5% 0.018 70);  /* 次级块底 / 行情格 */
  --color-rule:     oklch(84%   0.018 65);  /* 细分隔线 */
  --color-rule-2:   oklch(74%   0.020 60);  /* 次级线 / 双线内线 */
  /* 文字层级 */
  --color-neutral:  oklch(58%   0.015 60);  /* 元信息 / 弱标签 */
  --color-muted:    oklch(44%   0.018 55);  /* 正文摘要 */
  --color-ink:      oklch(24%   0.022 50);  /* 主文字 / 墨线 / 深报头 */
  --color-accent-ink: oklch(98% 0.010 75);  /* 实心色块上的反白字 */
  /* 双油墨 + 高亮 */
  --color-accent:   oklch(52%   0.15  47);  /* terracotta — 主强调，text-safe */
  --color-orange:   oklch(63%   0.18  48);  /* 高亮填充（NEW / 强调） */
  --color-blue:     oklch(47%   0.115 248); /* 第二油墨 — 仅用于标题 hover 投影 */
  --color-focus:    oklch(52%   0.16  47);  /* 焦点环 */
  /* 行情涨跌（中国习惯：红涨绿跌，保持现状） */
  --color-up:       oklch(55%   0.18  25);  /* 涨 红 */
  --color-down:     oklch(52%   0.12  155); /* 跌 绿 */
}
```

### 3.2 字体

```css
--font-display: 'Fraunces','Songti SC','Noto Serif SC',serif;        /* 标题 */
--font-body:    'Newsreader','PingFang SC','Hiragino Sans GB',system-ui,sans-serif; /* 正文/摘要 */
--font-mono:    'Geist Mono',ui-monospace,SFMono-Regular,monospace;  /* 标签/数字/源站名 */
```

> 注意：**正文中文用黑体**（苹方），拉丁部分用 Newsreader；标题中文用宋体，拉丁用 Fraunces。这是与用户确认的混排方案。

### 3.3 Tailwind 映射

```js
// tailwind.config.js → theme.extend
colors: {
  paper: 'var(--color-paper)', 'paper-2': 'var(--color-paper-2)',
  rule: 'var(--color-rule)', 'rule-2': 'var(--color-rule-2)',
  neutral: 'var(--color-neutral)', muted: 'var(--color-muted)',
  ink: 'var(--color-ink)', 'accent-ink': 'var(--color-accent-ink)',
  accent: 'var(--color-accent)', orange: 'var(--color-orange)',
  blue: 'var(--color-blue)', up: 'var(--color-up)', down: 'var(--color-down)',
},
fontFamily: {
  display: ['Fraunces','Songti SC','Noto Serif SC','serif'],
  body: ['Newsreader','PingFang SC','Hiragino Sans GB','system-ui','sans-serif'],
  mono: ['Geist Mono','ui-monospace','monospace'],
},
```

---

## 4. 颜色角色（怎么用，不只是有什么）

| 角色 | 颜色 | 用在哪 |
| --- | --- | --- |
| 主强调 terracotta | `--color-accent` | 新闻源章节条（实心）、编号、stamp 描边、章节名英文标签、焦点环 |
| 高亮 orange | `--color-orange` | `NEW` pill、「立即更新」按钮描边、个别需要跳出的强调 |
| 结构 blue | `--color-blue` | 仅用于标题 hover 的文字与硬投影（terracotta 之外唯一的彩色油墨；播客章节条/分节标题已按用户要求统一为 terracotta） |
| 墨黑 ink | `--color-ink` | 主文字、墨线（nav 底线、行情边框、footer 顶线）、深色报头底 |
| 涨/跌 | `--color-up` / `--color-down` | 行情百分比与价格涨跌（红涨绿跌） |

**双油墨纪律**：除涨跌色外，整页只允许 terracotta 与 blue 两种彩色油墨。新增元素若想用别的颜色 → 先回到墨黑 / 纸色 / 细线方案。

---

## 5. 视觉装置（Devices）

| 装置 | 规格 | 应用 |
| --- | --- | --- |
| Halftone grain | SVG `feTurbulence` 噪点，`opacity: ~4.5%`，`position: fixed` 全屏覆盖、`pointer-events:none`、`z-index` 居于内容之上但不挡交互 | 全站背景 |
| Offset 重影标题 | 标题文字下叠两层伪元素：terracotta（`+1.5px,+1.5px` opacity .28）与 blue（`-1.5px,-1px` opacity .22） | 仅报头 nameplate（B 方向标配；C 方向可选，默认关闭，留在附录 A） |
| Hard-offset hover 投影 | `text-shadow: 2px 2px 0 oklch(47% 0.115 248 / .16)` + 文字转 blue，过渡 `.12s` | 所有可点标题（headline / episode 标题） |
| Terracotta 描边 stamp | `1px solid --accent`，`border-radius:3px`，Geist Mono 9px caps，terracotta 字 | 「最新」标记（每源第 1 条或带 note 的源） |
| NEW pill | 实心 `--orange` 底 + 深字，Geist Mono 8.5px caps | 突出条目（可选） |

---

## 6. 组件规格（现状 → 改为）

逐组件给出视觉映射。结构尽量沿用现有 JSX。

### 6.1 顶栏 Masthead — `App.jsx <header>`
- **底**：深墨 `--color-ink`，反白内容。沿用现有 `sticky top-0` + ~52px 高度；导航紧贴其下层叠（见 §6.2），层叠关系不变。
- **左**：logo 圆形（`--accent` 或现有 `logo.png`）+ 报头「每日资讯」`font-display` 600 ~19px。
- **右**：日期 `font-mono` 10.5px caps（`MM·DD 周X`）+ 「立即更新」按钮 = `font-mono` 11px、`--orange` 描边、透明底。
- **按钮状态**：idle 橙描边 / pending 灰描边灰字 / done `--down` 绿描边「已更新 ✓」/ error `--up` 红描边「失败，重试」。

### 6.2 导航 NavBar — `NavBar.jsx`
- 容器：纸底 + `border-bottom: 2px solid --ink`，`sticky` 于报头之下。
- tab：`font-mono` 11px 500 caps，未选 `--color-muted`。
- **active**：`--accent` 实心底 + `--accent-ink` 字，`border-radius:3px`。
- 横向滚动、隐藏滚动条（沿用 `.scrollbar-none`）。滚动高亮逻辑不变。

### 6.3 行情 StockBar — `StockBar.jsx`
- 章节条 `.sec-bar-mkt`：透明底 + 上下 `2px solid --ink` 墨线，左「实时行情 · Markets」（`font-mono` caps），右「每日 11:00 更新」`--neutral`。
- 分组（A股 / 海外 / 大宗）：组标签 `font-mono` 9.5px caps `--neutral`。
- 报价网格 `.quotes`：外框 `2px solid --ink`，格子 `--rule-2` 内分隔线，三列。
  - 标签 `font-mono` 9px caps `--neutral`；价格 `font-display` 15px 600 `--ink` `tabular-nums`；涨跌 `font-mono` 11px，`--up`/`--down`。
- 涨跌判定逻辑、`toLocaleString`、commodity 两位小数等**全部保留**。

### 6.4 新闻源 NewsSection — `NewsSection.jsx`
- 章节条 `.sec-bar-news`：实心 `--accent` 底 + `--accent-ink` 字。左 = `<span class="cn">财新</span> Caixin`（中文 `font-display` + 英文 `font-mono` caps）；右 = 「前往源站 →」`font-mono` 10px。
- 列表行 `.news-row`：`编号 + 内容`，行间 `1px solid --rule`，末行无线。
  - 编号 `.no`：`font-mono` 600 13px `--accent`，两位 `01/02/…`（用 `String(i+1).padStart(2,'0')`）。
  - 标题 `.headline`：`font-display` 600 ~15.5px `--ink`，hover → blue + 硬投影（§5）。
  - 摘要（`showSummary && item.summary`）：`font-body` 13.5px `--muted`，行高 1.55。
  - 元信息（`item.date`）：`font-mono` 10px `--neutral`，`dayjs().fromNow()` 不变。
  - 第 1 条加 `.stamp`「最新」。`note`（如 Schwab）样式改为 `--accent` 文字的提示行。
- loading 骨架：`--paper-2` 块 + `animate-pulse`。error / empty：`--muted` 文案。

### 6.5 播客 PodcastSection — `PodcastSection.jsx`
- 章节条 `.sec-bar-cast`：实心 **`--accent`** 底 + 反白字（与新闻源一致；按用户要求不再用蓝色区分播客）。
- 单集标题 `.ep`：`font-display` 600 16px `--ink`，hover → blue；日期 `font-mono` 10px `--neutral`。
- 分节：heading `font-mono` 11px caps **`--accent`**；要点 `font-body` 13.5px `--ink`，前导符用 `—`（`--accent`）。
- 提及标的：上方 `1px solid --rule`，标签 `font-mono` caps `--neutral`；每个 tag = `font-mono` 10.5px `--ink` + `--rule-2` 描边。

### 6.6 页脚 Footer — `App.jsx <footer>`
- 顶 `2px solid --ink` 墨线，`font-mono` 10px caps `--neutral`，文案不变。

---

## 7. 交互与状态色

| 状态 | 表现 |
| --- | --- |
| 标题 hover | 文字 `--blue` + `text-shadow: 2px 2px 0 oklch(47% 0.115 248 /.16)`，`transition .12s` |
| 链接 focus | `outline: 2px solid --color-focus`，`outline-offset: 2px`（可访问性） |
| 刷新按钮 | 见 §6.1 四态配色 |
| loading | `--paper-2` skeleton + pulse |
| 章节 error / empty 文案 | `--muted` 文字（如「暂时无法获取」「今日暂无更新」），**不**用红色，避免与涨跌红混淆 |
| 刷新按钮 error 态 | 例外：按钮失败用 `--up` 红描边「失败，重试」属通用交互反馈，与上一行的章节文案是不同对象 |

---

## 8. 明确不做（YAGNI）

- 不做暗色模式（本轮）。
- 不改数据 JSON 结构、抓取脚本、Groq 摘要逻辑、GitHub Actions 流程。
- 不改信息架构、源的顺序、导航行为、刷新轮询逻辑。
- 不引入组件库 / CSS-in-JS / 新构建工具。
- 不在本轮处理安全隐患（见附录 B，独立任务）。

---

## 附录 A — 备选方向 B「社论排版 Editorial」（保留待选）

若日后想从 C 切到更克制的报纸排版，按此规格：

- **去卡片**：章节不用实心色条与外框，改为**报纸式细线**分隔；章节头 = kicker（`font-mono` caps `--accent`）+ 其下 `2px solid --ink` 重线，右侧「前往源站 →」。
- **报头 nameplate**：居中 `font-display` 600 大字「每日资讯」，上下 `3px double --rule-2`；**开启 offset 重影**（terracotta `+1.5/+1.5` .28、blue `-1.5/-1` .22）；上方一行 `font-mono` caps（期号 / 日期）。
- **标题**：`font-display` 500–600，hover 同样 blue + 硬投影。
- **行情**：上下细线 + 等分列，无外框实块，数字 `font-mono`。
- **stamp / 提及标的**：与 C 相同。
- 色彩更省：terracotta 仅用于 kicker、stamp、编号；蓝色仅用于 hover 与播客标识。整体更"安静"。

> 两方向共用 §3 tokens 与 §5 装置，差别只在**章节装置的强度**（C=实心色条/编号；B=细线/kicker）。切换成本低。

---

## 附录 B — 安全隐患修复记录：前端 GitHub Token 暴露（✅ 已修复 2026-06-24）

**✅ 修复方案（已实施）：方案 1 + 按钮重载数据 + 每日 cron**
- `App.jsx`：删除 `DISPATCH_URL` / `VITE_GITHUB_TOKEN` 引用；「立即更新」按钮改为重新拉取 meta + 所有源 JSON（`no-store`），不再触发 `workflow_dispatch`、不再需要任何 token。
- `update.yml`：删除 Build step 注入的 `VITE_GITHUB_TOKEN`；新增 `schedule: cron '30 3 * * *'`（≈墨尔本 13:30，夏令时 AEDT 期间漂到 14:30），实现真正的每日自动抓取（此前仅靠不可靠的外部 trigger，从未稳定每日运行）。
- **待用户手动**：GitHub 删除 `VITE_GITHUB_TOKEN` secret、吊销对应 PAT、（可选）删 `.env.local` 中该行。
- **未来若需"手机一键强制重抓"**：再加方案 2（serverless 代理），与本修复叠加、无返工。

**问题（原始记录）**：`App.jsx` 的「立即更新」按钮用 `import.meta.env.VITE_GITHUB_TOKEN` 在浏览器端直接 `POST` GitHub Actions `workflow_dispatch`。Vite 在 build 时把该值内联进 `dist/assets/index-*.js`；站点部署于 GitHub Pages（公开），故**任何访客都能从源码读出 token 并滥用**（刷 Actions 额度，或视 token 权限造成更大影响）。已在构建产物中确认明文 `Bearer <token>`。

**修复选项**（择一，待用户决定后另起任务）：
1. **移除前端手动触发**：删按钮 + token，仅靠定时 remote trigger。最简单最安全，代价是失去「立即更新」。
2. **Serverless 代理**：用 Cloudflare Worker / Netlify Function 在服务端保管 token，前端只调代理。保留功能，但引入新基础设施。
3. **最小缓解**：换成只对该仓库 `actions:write` 的 fine-grained PAT，缩小爆炸半径。token 仍暴露、仍可被滥用刷额度，仅作过渡。

**附带**：`.env.local` 已在 `.gitignore` 中（未泄露源文件），问题仅在构建注入这一环。
