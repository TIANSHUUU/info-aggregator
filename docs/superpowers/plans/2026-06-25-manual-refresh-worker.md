# 手动「立即更新」按钮（Cloudflare Worker 代理）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给站点恢复一个站内一键、真·触发抓取的「立即更新」按钮，token 只存在于 Cloudflare Worker（不进前端）；并把每日 cron 错峰到墨尔本 13:41。

**Architecture:** 前端按钮 POST 一个 Cloudflare Worker；Worker 校验 Origin + 60s 节流后，用服务端保管的 fine-grained PAT 调 GitHub `workflow_dispatch`；前端随后轮询 `meta.json` 等抓取完成并重载。

**Tech Stack:** Cloudflare Workers（wrangler）、React/Vite 前端、GitHub Actions。

**权威 spec：** `docs/superpowers/specs/2026-06-25-manual-refresh-worker.md`。

---

## 验证方式

无测试框架（沿用本项目惯例）。各任务验证：
- **前端**：`npm run build` 退出码 0。
- **Worker**：`node --input-type=module --check < worker/trigger-refresh.js`（ESM 语法检查，退出码 0、无输出）。真正的功能验证在 **Task 6** 用户部署后用 `curl` 实测。
- **workflow**：`grep` 确认 cron 值。

**两阶段交接**：Task 1–4 是我可独立完成的代码改动；**Task 5 是用户的一次性部署**（产出 Worker 网址）；Task 6 用该网址收尾并上线。

**前置**：当前分支 `feat/manual-refresh-worker`（spec 已提交于此）。

---

## 文件清单

| 文件 | 职责 | 任务 |
|---|---|---|
| `worker/trigger-refresh.js` | Worker 入口：Origin 校验 + 节流 + 触发 dispatch | Task 1 |
| `worker/wrangler.toml` | Worker 部署配置 | Task 1 |
| `worker/README.md` | 部署步骤备查 | Task 1 |
| `src/App.jsx` | `handleRefresh` 调 Worker + 轮询；按钮恢复 4 态；加 `REFRESH_ENDPOINT` | Task 2 |
| `.github/workflows/update.yml` | cron `30 3` → `41 3` | Task 3 |
| `design.md` | 附录 B 追加：方案1 → 方案2 | Task 4 |

---

## Task 1: Cloudflare Worker

**Files:**
- Create: `worker/trigger-refresh.js`
- Create: `worker/wrangler.toml`
- Create: `worker/README.md`

- [ ] **Step 1: 创建 `worker/trigger-refresh.js`**

```js
const ALLOWED_ORIGIN = 'https://tianshuuu.github.io'
const DISPATCH_URL =
  'https://api.github.com/repos/TIANSHUUU/info-aggregator/actions/workflows/update.yml/dispatches'

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin === ALLOWED_ORIGIN ? ALLOWED_ORIGIN : '',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  }
}

const json = (obj, status, origin) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) },
  })

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || ''

    if (request.method === 'OPTIONS')
      return new Response(null, { status: 204, headers: corsHeaders(origin) })
    if (request.method !== 'POST')
      return json({ error: 'method_not_allowed' }, 405, origin)
    if (origin !== ALLOWED_ORIGIN)
      return json({ error: 'forbidden' }, 403, origin)

    // 60s 节流（边缘节点级，足够个人用）
    const cache = caches.default
    const throttleKey = new Request('https://throttle.local/last-trigger')
    if (await cache.match(throttleKey))
      return json({ error: 'too_soon', retry_after: 60 }, 429, origin)

    const gh = await fetch(DISPATCH_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.GH_TOKEN}`,
        Accept: 'application/vnd.github+json',
        'User-Agent': 'infoaggre-refresh-worker',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ref: 'main' }),
    })
    if (gh.status !== 204)
      return json({ error: 'dispatch_failed', status: gh.status }, 502, origin)

    await cache.put(
      throttleKey,
      new Response('1', { headers: { 'Cache-Control': 'max-age=60' } })
    )
    return json({ ok: true }, 200, origin)
  },
}
```

- [ ] **Step 2: 创建 `worker/wrangler.toml`**

```toml
name = "infoaggre-refresh"
main = "trigger-refresh.js"
compatibility_date = "2025-01-01"
# GH_TOKEN 不写在此处，用 `npx wrangler secret put GH_TOKEN` 注入为加密 Secret
```

- [ ] **Step 3: 创建 `worker/README.md`**

````markdown
# infoaggre-refresh Worker

前端「立即更新」按钮的触发代理。持有一个 fine-grained PAT，校验来源 + 60s 节流后
触发 GitHub `workflow_dispatch`。token 只在这里，永不进前端。

## 一次性部署

1. 注册/登录 Cloudflare（免费，无需绑卡）。
2. 在 GitHub 建 fine-grained PAT：Settings → Developer settings → Fine-grained tokens
   - Repository access：仅 `TIANSHUUU/info-aggregator`
   - Permissions：`Actions` → Read and write
   - 复制生成的 token 串
3. 在本目录部署：
   ```bash
   cd worker
   npx wrangler login
   npx wrangler secret put GH_TOKEN   # 粘贴上一步的 token
   npx wrangler deploy
   ```
4. 记下输出里的 Worker 网址（形如 `https://infoaggre-refresh.<subdomain>.workers.dev`），
   填入前端 `src/App.jsx` 的 `REFRESH_ENDPOINT`。

## 自测

```bash
# 正确来源 → {"ok":true} 并在 Actions 触发一次 run
curl -X POST -H "Origin: https://tianshuuu.github.io" <worker-url>
# 错误/缺失来源 → 403
curl -X POST <worker-url>
```
````

- [ ] **Step 4: 语法验证**

Run: `node --input-type=module --check < worker/trigger-refresh.js`
Expected: 退出码 0、无输出。

- [ ] **Step 5: Commit**

```bash
git add worker/
git commit -m "feat(worker): add Cloudflare Worker that proxies workflow_dispatch"
```

---

## Task 2: 前端 — `handleRefresh` 调 Worker + 按钮恢复 4 态

**Files:**
- Modify: `src/App.jsx`

- [ ] **Step 1: 加入 `REFRESH_ENDPOINT` 常量**

在 `src/App.jsx` 顶部、`const BASE = import.meta.env.BASE_URL` 之后加入（占位值会在 Task 6 用真实 Worker 网址替换；此前 build 正常，只是点按钮会失败）：

```js
// 部署 Cloudflare Worker 后，把下面替换成真实的 Worker 网址（见 plan Task 6）
const REFRESH_ENDPOINT = 'https://REPLACE_WITH_WORKER_URL'
```

- [ ] **Step 2: 替换 `handleRefresh` 整个函数**

把现有 `handleRefresh`（重载数据版）整体替换为：

```js
  // 触发服务端重新抓取（经 Cloudflare Worker，前端不持 token），
  // 然后轮询 meta.json 直到 updated_at 变化。
  async function handleRefresh() {
    if (refreshState === 'pending') return
    setRefreshState('pending')

    try {
      const res = await fetch(REFRESH_ENDPOINT, { method: 'POST' })
      if (!res.ok) throw new Error(`trigger ${res.status}`)
    } catch {
      setRefreshState('error')
      setTimeout(() => setRefreshState('idle'), 3000)
      return
    }

    // 轮询 meta 直到 updated_at 变化（最多 5 分钟）
    const baseline = lastUpdated
    const deadline = Date.now() + 5 * 60 * 1000
    const poll = setInterval(async () => {
      try {
        const meta = await loadJson(`meta?t=${Date.now()}`)
        if (meta.updated_at !== baseline) {
          clearInterval(poll)
          setLastUpdated(meta.updated_at)
          setRefreshState('done')
          await loadAll()
          setTimeout(() => setRefreshState('idle'), 3000)
        }
      } catch {}
      if (Date.now() > deadline) {
        clearInterval(poll)
        setRefreshState('error')
        setTimeout(() => setRefreshState('idle'), 3000)
      }
    }, 15000)
  }
```

- [ ] **Step 3: 按钮恢复 error 态 + 文案改回"立即更新/更新中…"**

把 `<header>` 里那个刷新 `<button>` 整体替换为（恢复 4 态配色，文案从"刷新"改回"更新"）：

```jsx
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
```

> 说明：`refreshState` 注释行同时更新为 `// idle | pending | done | error`（位于 useState 定义处）。`loadAll` 已返回 Promise.allSettled（方案1时改过），`await loadAll()` 可用。

- [ ] **Step 4: 把 `refreshState` 状态注释改回 4 态**

把 `const [refreshState, setRefreshState] = useState('idle') // idle | pending | done` 行尾注释改为 `// idle | pending | done | error`。

- [ ] **Step 5: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 6: Commit**

```bash
git add src/App.jsx
git commit -m "feat(refresh): trigger real fetch via Worker + restore 4-state button"
```

---

## Task 3: workflow cron 错峰到 13:41

**Files:**
- Modify: `.github/workflows/update.yml`

- [ ] **Step 1: 改 cron 值**

把
```yaml
  schedule:
    - cron: '30 3 * * *'    # 每天 03:30 UTC ≈ 墨尔本 13:30（AEST；夏令时 AEDT 期间为 14:30）
```
改为
```yaml
  schedule:
    - cron: '41 3 * * *'    # 每天 03:41 UTC ≈ 墨尔本 13:41（AEST；夏令时 AEDT 期间为 14:41）
```

- [ ] **Step 2: 验证**

Run: `grep -A1 'schedule:' .github/workflows/update.yml`
Expected: 看到 `- cron: '41 3 * * *'`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/update.yml
git commit -m "chore(ci): offset daily cron to 03:41 UTC (Melbourne 13:41)"
```

---

## Task 4: 更新 design.md 附录 B

**Files:**
- Modify: `design.md`

- [ ] **Step 1: 在附录 B 的修复方案段落后追加升级说明**

在 `design.md` 附录 B 里 `**✅ 修复方案（已实施）：方案 1 + 按钮重载数据 + 每日 cron**` 这一段之后，紧接着插入：

```markdown
**🔼 升级（2026-06-25）：方案 2 — Cloudflare Worker 代理，恢复"真·触发抓取"按钮**
- 新增 `worker/`（Cloudflare Worker）：持有 fine-grained PAT（仅本仓库 `actions:write`），校验 `Origin` + 60s 节流后触发 `workflow_dispatch`。token 仍不进前端。
- `App.jsx`：`handleRefresh` 改为 POST 该 Worker，再轮询 meta 等抓取完成；按钮恢复 4 态。
- cron 错峰到 `41 3 * * *`（≈墨尔本 13:41）。
- 设计详见 `docs/superpowers/specs/2026-06-25-manual-refresh-worker.md`。
```

- [ ] **Step 2: Commit**

```bash
git add design.md
git commit -m "docs(design): record solution-2 Worker upgrade in appendix B"
```

---

## Task 5: 【用户操作】部署 Cloudflare Worker

> 这是用户的一次性手动步骤，产出 Worker 网址。代码已在 Task 1 就位。

- [ ] **Step 1: 建 fine-grained PAT**
  - GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token
  - Repository access：Only select repositories → `TIANSHUUU/info-aggregator`
  - Permissions：`Actions` → **Read and write**
  - Generate → 复制 token 串

- [ ] **Step 2: 部署 Worker**

```bash
cd worker
npx wrangler login          # 浏览器授权 Cloudflare
npx wrangler secret put GH_TOKEN   # 粘贴上一步的 PAT
npx wrangler deploy
```

- [ ] **Step 3: 记录 Worker 网址**
  - 部署输出会有 `https://infoaggre-refresh.<subdomain>.workers.dev`
  - 自测：`curl -X POST -H "Origin: https://tianshuuu.github.io" <worker-url>` → 应返回 `{"ok":true}` 且 Actions 出现一次新 run。
  - 把这个网址提供给下一步。

---

## Task 6: 填入 Worker 网址 + 上线

**Files:**
- Modify: `src/App.jsx`

- [ ] **Step 1: 替换 `REFRESH_ENDPOINT` 占位为真实 Worker 网址**

把 `src/App.jsx` 里
```js
const REFRESH_ENDPOINT = 'https://REPLACE_WITH_WORKER_URL'
```
改为 Task 5 得到的真实网址，例如
```js
const REFRESH_ENDPOINT = 'https://infoaggre-refresh.tianshuuu.workers.dev'
```

- [ ] **Step 2: 构建验证**

Run: `npm run build`
Expected: 退出码 0。

- [ ] **Step 3: Commit + 合并 + 部署**

```bash
git add src/App.jsx
git commit -m "feat(refresh): wire frontend to deployed Worker endpoint"
git push -u origin feat/manual-refresh-worker
gh pr create --base main --title "feat: site-internal manual refresh via Cloudflare Worker" --body "见 spec/plan：Worker 代理 + 前端轮询 + cron 错峰"
gh pr merge --merge --delete-branch
gh workflow run update.yml --ref main   # 部署上线
```

- [ ] **Step 4: 线上验收**
  - 强刷站点 → 点「立即更新」→「更新中…」→ 约 1–2 分钟后「已更新 ✓」并刷新内容。
  - 不带 Origin 的 `curl -X POST <worker-url>` 仍返回 403。

---

## 完成标准（Definition of Done）

- Worker 部署且 `curl` 自测通过；前端「立即更新」能真·触发抓取并在完成后重载。
- 前端 bundle 仍无任何 token（Worker 持 token）。
- cron 为 `41 3 * * *`。
- 未触碰抓取脚本、视觉、信息架构。
