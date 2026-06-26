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
