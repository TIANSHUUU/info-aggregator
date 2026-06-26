# 手动「立即更新」按钮（方案2：Cloudflare Worker 代理）设计

> 在不向前端暴露任何 token 的前提下，给站点恢复一个**站内一键、真·触发抓取**的「立即更新」按钮。
> 同时把每日 cron 错峰到墨尔本 13:41。
>
> 状态：✅ 已与用户确认架构、平台、防滥用程度、cron 时间（2026-06-25）。

---

## 1. 目标与背景

- 现状：前端已无 token；「立即更新」按钮只能**重载已有数据**（方案1），不能触发服务端重新抓取。每日 cron 因 GitHub schedule 高峰排队，实际常延迟数小时。
- 目标：用户在任意设备（尤其手机）**站内一键**即可触发一次真正的抓取+部署，过程零跳转、无需登录 GitHub、不暴露任何 token。
- 非目标：不改抓取脚本、不改视觉、不引入账号系统。cron 的"准点"不在本设计承诺范围（GitHub 限制），仅做错峰缓解。

## 2. 架构与数据流

```
[前端按钮] --POST(no body)--> [Cloudflare Worker]
                                   | 校验 Origin = https://tianshuuu.github.io
                                   | 60s 节流（Cache API）
                                   | 用服务端保管的 PAT 调：
                                   v
        POST api.github.com/repos/TIANSHUUU/info-aggregator/actions/workflows/update.yml/dispatches
                                   | (workflow 抓取+构建+部署 ~1-2 min)
[前端] --轮询 public/data/meta.json (no-store)--> updated_at 变化 => 重载数据 + 「已更新 ✓」
```

token 只存在于 Worker 的加密环境变量里，永不进入前端 bundle、不进 git。

## 3. 组件

### 3.1 Cloudflare Worker — `worker/trigger-refresh.js` + `worker/wrangler.toml`

职责：单一端点，校验来源 → 节流 → 触发 `workflow_dispatch`。

```js
// worker/trigger-refresh.js
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

```toml
# worker/wrangler.toml
name = "infoaggre-refresh"
main = "trigger-refresh.js"
compatibility_date = "2025-01-01"
# GH_TOKEN 不写在这里，用 `wrangler secret put GH_TOKEN` 注入
```

要点：
- `GH_TOKEN` 经 `wrangler secret put GH_TOKEN`（或 Dashboard）注入，是加密 Secret，不在仓库、不在前端。
- GitHub API 必须带 `User-Agent`，否则 403。
- 节流用 `caches.default`：无需额外开通 KV，部署最简单；它是**边缘节点级**（个人使用请求基本落同一节点，足够）。如未来需要严格全局节流再换 KV。

### 3.2 前端 — `src/App.jsx`

新增一个常量（Worker 网址不是秘密，可硬编码；用户部署 Worker 后填入真实值）：

```js
const REFRESH_ENDPOINT = 'https://infoaggre-refresh.<your-subdomain>.workers.dev'
```

`handleRefresh` 改为：调用 Worker 触发抓取，然后轮询 `meta.json` 直到 `updated_at` 变化（复用方案1之前的轮询思路；不再带任何 token）：

```js
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

- 状态机恢复 4 态：`idle | pending | done | error`。
- 按钮文案恢复：`立即更新 / 更新中… / 已更新 ✓ / 失败，重试`（沿用现有深色报头按钮的配色：橙/灰/绿/红）。
- 节流命中（429）当作失败处理 → 「失败，重试」即可（个人用极少撞到 60s 窗口）。

### 3.3 workflow cron 错峰 — `.github/workflows/update.yml`

```yaml
  schedule:
    - cron: '41 3 * * *'    # 03:41 UTC ≈ 墨尔本 13:41（AEST；夏令时 AEDT 期间为 14:41）
```

仅把 `30 3` 改成 `41 3`（非整点/半点，稍微避开高峰）。不加兜底时间点。

### 3.4 Token — fine-grained PAT

- 类型：Fine-grained personal access token。
- Repository access：仅 `TIANSHUUU/info-aggregator`。
- Permissions：`Actions` → **Read and write**（触发 `workflow_dispatch` 所需的最小权限）。
- 过期：按需（建议设较长或定期轮换）。
- 用途：仅注入到 Worker 的 `GH_TOKEN` Secret。

## 4. 防滥用

- **Origin 校验**：非 `https://tianshuuu.github.io` 一律 403。
- **60s 节流**：Cache API，距上次触发 < 60s 返回 429。
- **残余风险（已接受）**：Origin 头可被非浏览器伪造，故理论上有人若知道 Worker 地址可绕过 Origin 触发你的 workflow（仅"帮你刷新"，消耗少量 Actions/Groq 额度）。token 在服务端、仅 `actions:write`，无法做任何别的事。用户为个人使用、不分享，风险可接受。

## 5. 用户一次性部署步骤（实现时我提供可照抄的命令）

1. 注册/登录 Cloudflare（免费，无需绑卡）。
2. 在 GitHub 建上述 fine-grained PAT，复制 token 串。
3. 本地：`cd worker && npx wrangler login && npx wrangler secret put GH_TOKEN`（粘贴 token）→ `npx wrangler deploy`。
4. 记下部署输出的 Worker 网址（形如 `https://infoaggre-refresh.<subdomain>.workers.dev`），发给我填进 `REFRESH_ENDPOINT`。
5. 我提交前端改动 → 合并 → 部署上线。

## 6. 验证

- Worker 部署后：`curl -X POST -H "Origin: https://tianshuuu.github.io" <worker-url>` 应返回 `{"ok":true}` 并在 Actions 里看到一次新 run；不带正确 Origin 应 403。
- 前端上线后：强刷站点 → 点「立即更新」→「更新中…」→ 约 1-2 分钟后「已更新 ✓」并刷新内容。

## 7. 明确不做（YAGNI）

- 不做用户鉴权/登录、不做 KV 全局节流（边缘级够用）、不做多区域一致性。
- 不改抓取脚本、视觉、信息架构。
- 不承诺 cron 准点（GitHub 限制），仅错峰缓解。

## 8. 涉及文件

| 文件 | 改动 |
|---|---|
| `worker/trigger-refresh.js` | 新建：Worker 入口 |
| `worker/wrangler.toml` | 新建：Worker 配置 |
| `worker/README.md` | 新建：部署步骤备查 |
| `src/App.jsx` | 改 `handleRefresh` + 加 `REFRESH_ENDPOINT`，恢复 4 态按钮 |
| `.github/workflows/update.yml` | cron `30 3` → `41 3` |
| `design.md` 附录 B | 追加：已从方案1 升级为方案2 |
