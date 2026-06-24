# 每日资讯 · Coffee Crema Fusion 视觉改造实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把现有「每日资讯」聚合站从灰白现代风改造成 `design.md` 锁定的「Coffee Crema Fusion / 双油墨 zine」编辑风，纯视觉层，不改数据与逻辑。

**Architecture:** 三层改动 —— ①`index.html` 加拉丁 Web Font；②`tailwind.config.js` 映射设计 token；③`src/index.css` 重写为 tokens + grain + 语义化组件类；④五个组件（App/NavBar/StockBar/NewsSection/PodcastSection）仅替换 className 与少量包裹结构。组件逻辑、状态、数据流、信息架构完全不动。

**Tech Stack:** React 18 + Vite 6 + Tailwind v3。字体 Fraunces / Newsreader / Geist Mono（拉丁，Google Fonts）+ 系统中文字体（宋体/苹方）。

**权威规格：** 项目根 `design.md`（§3 tokens、§5 装置、§6 各组件"现状→改为"）。本计划是它的可执行展开。

---

## 验证方式（重要）

本项目**没有测试框架**（`package.json` 无 `test` 脚本，无 vitest/jest），且本次是纯视觉改造，视觉结果无法用单元测试有意义地断言。给它引入测试框架属于 scope 蔓延（YAGNI）。因此每个任务的验证是：

1. **构建通过**：`npm run build` 退出码 0、无报错。
2. **目视对照**：`npm run dev`（默认 http://localhost:5173/info-aggregator/）在浏览器对照 `design.md` §6 与 brainstorm mockup（`.superpowers/brainstorm/*/content/page-c.html`）检查该任务涉及的视觉点。

> Task 2–7 之间页面会处于「部分新、部分旧」的过渡视觉态，属正常；Task 8 做整体验收。

**前置**：已在分支 `design/coffee-crema-fusion` 上（design.md 已提交于此分支）。继续在该分支提交。开发服务器若需启动：`npm run dev`。

---

## 文件清单

| 文件 | 职责 | 任务 |
| --- | --- | --- |
| `index.html` | 加载拉丁 Web Font | Task 1 |
| `tailwind.config.js` | 把 oklch token 映射为 Tailwind 颜色/字体类 | Task 1 |
| `src/index.css` | tokens(`:root`) + 纸色背景 + grain + focus + 全部语义组件类 | Task 2 |
| `src/App.jsx` | 顶层底色、深色报头 masthead、刷新按钮配色、页脚 | Task 3 |
| `src/components/NavBar.jsx` | 等宽 tab、terracotta active、墨线底边 | Task 4 |
| `src/components/StockBar.jsx` | 墨线网格行情、分组、红涨绿跌 | Task 5 |
| `src/components/NewsSection.jsx` | terracotta 章节条、编号、衬线标题、stamp | Task 6 |
| `src/components/PodcastSection.jsx` | blue 章节条、分节、提及标的 tag | Task 7 |

---

## Task 1: 字体加载 + Tailwind token 映射

**Files:**
- Modify: `index.html`（`<head>` 内）
- Modify: `tailwind.config.js`

- [ ] **Step 1: 在 `index.html` 的 `<head>` 加入 Google Fonts（仅拉丁字形）**

把现有 `<head>` 内的 `<title>` 行之后插入字体链接。`index.html` 改为：

```html
<!doctype html>
<html lang="zh-Hans">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/png" href="/info-aggregator/logo.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>每日资讯</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 2: 替换 `tailwind.config.js` 全文**，把 oklch token 映射为颜色/字体类

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: 'var(--color-paper)',
        'paper-2': 'var(--color-paper-2)',
        rule: 'var(--color-rule)',
        'rule-2': 'var(--color-rule-2)',
        neutral: 'var(--color-neutral)',
        muted: 'var(--color-muted)',
        ink: 'var(--color-ink)',
        'accent-ink': 'var(--color-accent-ink)',
        accent: 'var(--color-accent)',
        orange: 'var(--color-orange)',
        blue: 'var(--color-blue)',
        up: 'var(--color-up)',
        down: 'var(--color-down)',
      },
      fontFamily: {
        display: ['Fraunces', 'Songti SC', 'Noto Serif SC', 'serif'],
        body: ['Newsreader', 'PingFang SC', 'Hiragino Sans GB', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 3: 构建验证**

Run: `npm run build`
Expected: 退出码 0，无报错（此时页面仍是旧样式，但字体已加载、新颜色/字体类已可用）。

- [ ] **Step 4: Commit**

```bash
git add index.html tailwind.config.js
git commit -m "feat(design): load Fraunces/Newsreader/Geist Mono + map design tokens to Tailwind"
```

---

## Task 2: 重写 `src/index.css`（tokens + 背景 + grain + 组件类）

**Files:**
- Modify（整文件替换）: `src/index.css`

- [ ] **Step 1: 用以下内容整体替换 `src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* 纸与线 */
    --color-paper: oklch(97% 0.012 75);
    --color-paper-2: oklch(94.5% 0.018 70);
    --color-rule: oklch(84% 0.018 65);
    --color-rule-2: oklch(74% 0.020 60);
    /* 文字层级 */
    --color-neutral: oklch(58% 0.015 60);
    --color-muted: oklch(44% 0.018 55);
    --color-ink: oklch(24% 0.022 50);
    --color-accent-ink: oklch(98% 0.010 75);
    /* 双油墨 + 高亮 */
    --color-accent: oklch(52% 0.15 47);
    --color-orange: oklch(63% 0.18 48);
    --color-blue: oklch(47% 0.115 248);
    --color-focus: oklch(52% 0.16 47);
    /* 行情涨跌（红涨绿跌） */
    --color-up: oklch(55% 0.18 25);
    --color-down: oklch(52% 0.12 155);
  }

  body {
    @apply bg-paper text-ink antialiased font-body;
    font-size: 16px;
  }

  /* halftone grain：全屏覆盖、不挡交互 */
  body::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 50;
    opacity: 0.045;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }

  a {
    @apply transition-colors duration-150;
  }

  :focus-visible {
    outline: 2px solid var(--color-focus);
    outline-offset: 2px;
  }
}

@layer components {
  /* ===== 章节条 ===== */
  .sec-bar-news {
    @apply flex items-center justify-between px-3 py-1.5 mb-3 bg-accent text-accent-ink;
  }
  .sec-bar-cast {
    @apply flex items-center justify-between px-3 py-1.5 mb-3 bg-blue text-accent-ink;
  }
  .sec-bar-mkt {
    @apply flex items-center justify-between py-1.5 mb-3 border-y-2 border-ink text-ink;
  }
  .sec-name {
    @apply font-mono text-[12.5px] font-semibold tracking-[0.1em] uppercase flex items-baseline gap-2;
  }
  .sec-name .cn {
    @apply font-display text-sm font-semibold tracking-normal normal-case;
  }
  .sec-src {
    @apply font-mono text-[10px] tracking-[0.03em] opacity-90;
  }

  /* ===== 新闻行 ===== */
  .news-row {
    @apply flex gap-3 py-3 border-b border-rule last:border-0;
  }
  .news-no {
    @apply font-mono font-semibold text-[13px] text-accent flex-shrink-0 w-5 pt-[3px];
  }
  .headline {
    @apply font-display font-semibold text-[15.5px] leading-snug text-ink transition-all duration-150;
  }
  .headline:hover {
    @apply text-blue;
    text-shadow: 2px 2px 0 oklch(47% 0.115 248 / 0.16);
  }
  .news-sum {
    @apply font-body text-[13.5px] text-muted leading-relaxed mt-1.5;
  }
  .news-meta {
    @apply font-mono text-[10px] text-neutral mt-1.5 tracking-[0.03em];
  }
  .stamp {
    @apply font-mono text-[9px] tracking-[0.05em] uppercase text-accent border border-accent rounded-[3px] px-1.5 py-px mr-1.5 whitespace-nowrap;
  }

  /* ===== 行情 ===== */
  .mkt-group-label {
    @apply font-mono text-[9.5px] font-semibold tracking-[0.14em] uppercase text-neutral mb-1.5;
  }
  .quotes {
    @apply flex flex-wrap border-2 border-ink;
  }
  .quote-cell {
    @apply flex-1 text-center px-1 py-[7px] border-r border-b border-rule-2;
    min-width: 33.33%;
  }
  .quote-lab {
    @apply font-mono text-[9px] tracking-[0.04em] uppercase text-neutral block;
  }
  .quote-px {
    @apply font-display text-[15px] font-semibold text-ink block mt-px tabular-nums;
  }
  .quote-pct {
    @apply font-mono text-[11px] font-semibold tabular-nums;
  }

  /* ===== 播客 ===== */
  .ep-title {
    @apply font-display font-semibold text-base leading-snug text-ink transition-colors duration-150;
  }
  .ep-title:hover {
    @apply text-blue;
  }
  .ep-date {
    @apply font-mono text-[10px] text-neutral tracking-[0.03em];
  }
  .cast-sec-h {
    @apply font-mono text-[11px] font-semibold tracking-[0.1em] uppercase text-blue mb-1.5;
  }
  .cast-point {
    @apply font-body text-[13.5px] leading-relaxed text-ink flex gap-2;
  }
  .cast-tag-label {
    @apply font-mono text-[9.5px] tracking-[0.06em] uppercase text-neutral mr-2;
  }
  .cast-tag {
    @apply inline-block font-mono text-[10.5px] text-ink border border-rule-2 rounded-[3px] px-1.5 py-px mr-1 mb-1;
  }

  /* ===== 导航 ===== */
  .nav-tabs {
    @apply flex gap-1 overflow-x-auto py-2;
  }
  .nav-tab {
    @apply font-mono text-[11px] font-medium tracking-[0.05em] uppercase whitespace-nowrap px-[11px] py-[5px] text-muted rounded-[3px] flex-shrink-0 transition-colors duration-150;
  }
  .nav-tab-on {
    @apply bg-accent text-accent-ink;
  }

  /* ===== 杂项 ===== */
  .skeleton {
    @apply bg-paper-2 rounded animate-pulse;
  }
  .scrollbar-none {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .scrollbar-none::-webkit-scrollbar {
    display: none;
  }
}
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。若报 `class does not exist` 之类错误，多半是 Task 1 的 `tailwind.config.js` 颜色未生效——回查 Task 1 是否已提交。

- [ ] **Step 3: 目视验证**

Run: `npm run dev`，浏览器打开。
Expected: 背景变暖纸色、有极轻噪点；正文中文变苹方黑体。（章节/卡片此时仍引用旧类，样式会错乱，属过渡态，后续任务修复。）

- [ ] **Step 4: Commit**

```bash
git add src/index.css
git commit -m "feat(design): rewrite index.css with tokens, grain, and editorial component classes"
```

---

## Task 3: `src/App.jsx` —— 顶层底色 + 深色报头 + 刷新按钮 + 页脚

**Files:**
- Modify: `src/App.jsx`（仅 `return (...)` 内的 JSX：顶层 div、`<header>`、`<footer>`；逻辑、`SOURCES`、`handleRefresh`、`useEffect` 全部不动）

- [ ] **Step 1: 替换顶层容器底色**

把 `src/App.jsx:111` 的
```jsx
    <div className="min-h-screen bg-gray-50">
```
改为
```jsx
    <div className="min-h-screen bg-paper">
```

- [ ] **Step 2: 替换 `<header>` 整块**（`src/App.jsx:113-139`）为深色报头

```jsx
      {/* Top masthead */}
      <header className="bg-ink text-paper sticky top-0 z-20 h-[52px] flex items-center">
        <div className="max-w-3xl mx-auto px-4 w-full flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src={`${BASE}logo.png`} alt="每日资讯" className="h-7 w-7 rounded-full object-cover" />
            <span className="font-display font-semibold text-[19px] tracking-tight">每日资讯</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[10.5px] tracking-wide uppercase text-paper opacity-70">
              {lastUpdated
                ? dayjs(lastUpdated).format('MM·DD HH:mm')
                : dayjs().format('MM·DD')}
            </span>
            <button
              onClick={handleRefresh}
              disabled={refreshState === 'pending'}
              className={`font-mono text-[11px] tracking-wide px-2.5 py-1 rounded border transition-colors duration-150 ${
                refreshState === 'pending'
                  ? 'border-paper text-paper opacity-40 cursor-not-allowed'
                  : refreshState === 'done'
                  ? 'border-down text-down'
                  : refreshState === 'error'
                  ? 'border-up text-up'
                  : 'border-orange text-orange hover:bg-orange hover:text-ink'
              }`}
            >
              {refreshState === 'pending' ? '更新中…' : refreshState === 'done' ? '已更新 ✓' : refreshState === 'error' ? '失败，重试' : '立即更新'}
            </button>
          </div>
        </div>
      </header>
```

- [ ] **Step 3: 替换 `<footer>` 整块**（`src/App.jsx:162-164`）

```jsx
      <footer className="border-t-2 border-ink text-center font-mono text-[10px] tracking-widest uppercase text-neutral py-5">
        每日 11:00 自动更新 · GitHub Actions
      </footer>
```

- [ ] **Step 4: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 5: 目视验证**

`npm run dev`：顶栏变深墨底、反白「每日资讯」用 Fraunces；右侧日期等宽、刷新按钮橙色描边，hover 橙底深字；页脚为墨线 + 等宽小字。

- [ ] **Step 6: Commit**

```bash
git add src/App.jsx
git commit -m "feat(design): dark masthead, mono refresh button states, ruled footer"
```

---

## Task 4: `src/components/NavBar.jsx` —— 等宽 tab + terracotta active

**Files:**
- Modify: `src/components/NavBar.jsx`（仅 `return (...)` 的 className；滚动高亮逻辑 `useEffect`/`scrollTo` 不动）

- [ ] **Step 1: 替换 `return (...)` 块**（`NavBar.jsx:35-61`）

```jsx
  return (
    <nav
      ref={navRef}
      className="sticky top-[52px] z-10 bg-paper border-b-2 border-ink"
    >
      <div className="max-w-3xl mx-auto px-4">
        <div className="nav-tabs scrollbar-none">
          {sources.map(s => (
            <button
              key={s.key}
              onClick={() => scrollTo(s.key)}
              className={`nav-tab ${active === s.key ? 'nav-tab-on' : 'hover:text-ink'}`}
            >
              {s.title}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 3: 目视验证**

`npm run dev`：导航条墨线底边；tab 为等宽大写灰字；当前 section 对应 tab 为 terracotta 实心底 + 反白字；滚动时高亮跟随。

- [ ] **Step 4: Commit**

```bash
git add src/components/NavBar.jsx
git commit -m "feat(design): mono nav tabs with terracotta active state"
```

---

## Task 5: `src/components/StockBar.jsx` —— 墨线网格行情

**Files:**
- Modify（整文件替换）: `src/components/StockBar.jsx`

- [ ] **Step 1: 用以下内容整体替换 `src/components/StockBar.jsx`**（数据加载与涨跌判定逻辑保持原样，仅样式与类名变化；`QuoteChip` 改名 `QuoteCell`）

```jsx
import { useState, useEffect } from 'react'

const BASE = import.meta.env.BASE_URL

const GROUPS = [
  { key: 'CN',        label: 'A股'   },
  { key: 'INTL',      label: '海外'  },
  { key: 'COMMODITY', label: '大宗'  },
]

export default function StockBar() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/stocks.json`)
      .then(r => r.json())
      .then(data => { setStocks(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const byGroup = (key) => stocks.filter(s => s.market === key)

  return (
    <section className="mb-7">
      <div className="sec-bar-mkt">
        <span className="sec-name"><span className="cn">实时行情</span> Markets</span>
        <span className="sec-src text-neutral">每日 11:00 更新</span>
      </div>

      {loading && (
        <div className="flex gap-3 flex-wrap">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="skeleton h-12 w-24" />
          ))}
        </div>
      )}

      {!loading && stocks.length === 0 && (
        <p className="font-body text-sm text-muted">暂无数据</p>
      )}

      {!loading && stocks.length > 0 && (
        <div className="space-y-3">
          {GROUPS.map(g => {
            const items = byGroup(g.key)
            if (!items.length) return null
            return (
              <div key={g.key}>
                <div className="mkt-group-label">{g.label}</div>
                <div className="quotes">
                  {items.map(s => <QuoteCell key={s.symbol} stock={s} />)}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}

function QuoteCell({ stock }) {
  const up    = stock.change >= 0
  const color = up ? 'text-up' : 'text-down'
  const sign  = up ? '+' : ''

  const priceStr = stock.market === 'COMMODITY'
    ? stock.price.toFixed(2)
    : stock.price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })

  return (
    <div className="quote-cell">
      <span className="quote-lab">{stock.label}</span>
      <span className="quote-px">{priceStr}</span>
      <span className={`quote-pct ${color}`}>
        {sign}{stock.pct.toFixed(2)}%
      </span>
    </div>
  )
}
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 3: 目视验证**

`npm run dev`：行情区标题为上下墨线条「实时行情 Markets」；A股/海外/大宗分组；报价用 2px 墨框网格，价格 Fraunces，涨红跌绿（数据现为涨→红）。

- [ ] **Step 4: Commit**

```bash
git add src/components/StockBar.jsx
git commit -m "feat(design): ink-ruled market grid with display-font quotes"
```

---

## Task 6: `src/components/NewsSection.jsx` —— terracotta 章节条 + 编号 + 衬线标题

**Files:**
- Modify（整文件替换）: `src/components/NewsSection.jsx`

- [ ] **Step 1: 用以下内容整体替换 `src/components/NewsSection.jsx`**（`showSummary`/`note`/`item` 字段用法保持；新增编号与首条 stamp）

```jsx
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export default function NewsSection({ title, source, items = [], loading, error, showSummary = false, note }) {
  return (
    <section className="mb-7">
      <div className="sec-bar-news">
        <span className="sec-name"><span className="cn">{title}</span></span>
        {source && (
          <a
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            className="sec-src hover:underline"
          >
            前往源站 →
          </a>
        )}
      </div>

      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-5" />
          ))}
        </div>
      )}

      {error && (
        <p className="font-body text-sm text-muted">暂时无法获取内容，请稍后重试。</p>
      )}

      {note && !loading && !error && items.length > 0 && (
        <p className="font-mono text-xs text-accent mb-3 tracking-wide">{note}</p>
      )}

      {!loading && !error && items.length === 0 && (
        <p className="font-body text-sm text-muted">今日暂无更新。</p>
      )}

      {!loading && !error && items.length > 0 && (
        <ul>
          {items.map((item, i) => (
            <li key={i} className="news-row">
              <span className="news-no">{String(i + 1).padStart(2, '0')}</span>
              <div>
                {i === 0 && <span className="stamp">最新</span>}
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="headline"
                >
                  {item.title}
                </a>
                {showSummary && item.summary && (
                  <p className="news-sum">{item.summary}</p>
                )}
                {item.date && (
                  <div className="news-meta">{dayjs(item.date).fromNow()}</div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 3: 目视验证**

`npm run dev`：每个新闻源标题为 terracotta 实心条 + 反白中文（宋体）；列表带 `01/02…` terracotta 编号；标题 Fraunces/宋体、hover 变蓝 + 硬投影；首条带描边「最新」；财新/Schwab 等带 summary 用黑体；Schwab 的 `note` 显示为 terracotta 提示行。

- [ ] **Step 4: Commit**

```bash
git add src/components/NewsSection.jsx
git commit -m "feat(design): terracotta section bars, numbered rows, serif headlines"
```

---

## Task 7: `src/components/PodcastSection.jsx` —— blue 章节条 + 分节 + 标的 tag

**Files:**
- Modify（整文件替换）: `src/components/PodcastSection.jsx`

- [ ] **Step 1: 用以下内容整体替换 `src/components/PodcastSection.jsx`**（`data.sections`/`points`/`stocks` 字段用法保持）

```jsx
import dayjs from 'dayjs'

export default function PodcastSection({ title, data, loading, error }) {
  return (
    <section className="mb-7">
      <div className="sec-bar-cast">
        <span className="sec-name"><span className="cn">{title}</span></span>
        {data?.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer"
            className="sec-src hover:underline">
            前往源站 →
          </a>
        )}
      </div>

      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-5" />
          ))}
        </div>
      )}

      {error && <p className="font-body text-sm text-muted">暂时无法获取内容，请稍后重试。</p>}

      {!loading && !error && data?.sections?.length > 0 && (
        <>
          <div className="mb-4 pb-3 border-b border-rule">
            <a href={data.url} target="_blank" rel="noopener noreferrer" className="ep-title block">
              {data.title}
            </a>
            {data.date && (
              <div className="ep-date mt-1">{dayjs(data.date).format('YYYY年MM月DD日')}</div>
            )}
          </div>

          <div className="space-y-4">
            {data.sections.map((section, i) => (
              <div key={i}>
                <h3 className="cast-sec-h">{section.heading}</h3>
                <ul className="space-y-1">
                  {section.points.map((point, j) => (
                    <li key={j} className="cast-point">
                      <span className="text-accent flex-shrink-0">—</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {data.stocks?.length > 0 && (
            <div className="mt-4 pt-3 border-t border-rule">
              <span className="cast-tag-label">提及标的</span>
              {data.stocks.map((s, i) => (
                <span key={i} className="cast-tag">{s}</span>
              ))}
            </div>
          )}
        </>
      )}

      {!loading && !error && !data?.sections?.length && (
        <p className="font-body text-sm text-muted">暂无内容。</p>
      )}
    </section>
  )
}
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 3: 目视验证**

`npm run dev`：播客源（Peak / Equity Mates）标题为 **blue** 实心条（与新闻源区分）；单集标题 Fraunces/宋体 hover 变蓝；分节标题等宽蓝色大写；要点前导 terracotta「—」；提及标的为描边等宽 tag。（Peak 当前数据为空 `{}`，应显示「暂无内容」。）

- [ ] **Step 4: Commit**

```bash
git add src/components/PodcastSection.jsx
git commit -m "feat(design): blue section bars and tagged podcast layout"
```

---

## Task 8: 全页验收

**Files:** 无改动（纯检查；如发现问题回对应任务修，再提交）

- [ ] **Step 1: 干净构建**

Run: `rm -rf dist && npm run build`
Expected: 退出码 0，无警告级以上报错。

- [ ] **Step 2: 预览产物**

Run: `npm run preview`（serves `dist/`，默认 http://localhost:4173/info-aggregator/）

- [ ] **Step 3: 逐项对照 `design.md` §6 + mockup `page-c.html`**

核对清单：
- [ ] 全站暖纸底 + 轻噪点；噪点**不挡点击**（能点标题/按钮/tab）。
- [ ] 顶栏深墨反白报头，sticky；导航 sticky 紧贴其下，墨线底边，active=terracotta。
- [ ] 行情墨框网格、红涨绿跌、价格 Fraunces。
- [ ] 新闻源=terracotta 条 + 编号 + 衬线标题 + 首条「最新」stamp；标题 hover 变蓝 + 硬投影。
- [ ] 播客=blue 条，与新闻源一眼可分。
- [ ] 拉丁标题确为 Fraunces、正文中文为苹方黑体、标签/数字为 Geist Mono。
- [ ] 键盘 Tab 聚焦链接有 focus 描边。
- [ ] 移动宽度（≤430px）下导航可横滑、行情网格不溢出。

- [ ] **Step 4: 如全部通过，收尾提交（若 Step 3 未产生改动则跳过）**

```bash
git add -A
git commit -m "chore(design): editorial redesign visual QA pass"
```

---

## 完成标准（Definition of Done）

- `npm run build` 通过；`design.md` §6 全部组件视觉点在浏览器中达成。
- 未触碰：数据 JSON、`scripts/*`、GitHub Actions、组件逻辑/状态/数据流、信息架构、`VITE_GITHUB_TOKEN` 相关代码（安全修复见 `design.md` 附录 B，独立任务）。
- 分支 `design/coffee-crema-fusion` 上一系列原子提交；合并/PR 由用户决定（finishing-a-development-branch）。
