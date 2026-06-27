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

const HKET_PAGE = 'https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B'

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || ''
    const url = new URL(request.url)

    // GET /hket —— 代抓 HKET「即時中國」HTML 列表页（内容比 RSS 丰富）。HKET 反爬封
    // 数据中心 IP（CI/jina 直连 405），由 Cloudflare 出口代抓。URL 写死，非开放代理。
    if (request.method === 'GET' && url.pathname === '/hket') {
      const upstream = await fetch(HKET_PAGE, {
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
          'Referer': 'https://china.hket.com/',
        },
      })
      return new Response(await upstream.text(), {
        status: upstream.status,
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      })
    }

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
