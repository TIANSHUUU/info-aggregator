import { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import StockBar from './components/StockBar'
import NewsSection from './components/NewsSection'
import PodcastSection from './components/PodcastSection'
import NavBar from './components/NavBar'

const BASE = import.meta.env.BASE_URL

// 部署 Cloudflare Worker 后，把下面替换成真实的 Worker 网址（见 plan Task 6）
const REFRESH_ENDPOINT = 'https://REPLACE_WITH_WORKER_URL'

async function loadJson(nameWithQuery) {
  const [name, qs] = nameWithQuery.split('?')
  const url = `${BASE}data/${name}.json${qs ? '?' + qs : ''}`
  const r = await fetch(url, qs ? { cache: 'no-store' } : {})
  if (!r.ok) throw new Error(`${name} fetch failed`)
  return r.json()
}

const SOURCES = [
  { key: 'initium',  title: '端传媒',         source: 'https://theinitium.com/',                                          showSummary: false },
  { key: 'caixin',   title: '财新',            source: 'https://www.caixin.com/',                                          showSummary: true  },
  { key: 'schwab',   title: 'Charles Schwab', source: 'https://www.schwab.com/learn/market-commentary',                   showSummary: true, note: '日期信息暂不可用，以下为最新文章' },
  { key: 'peakprosperity', title: 'Peak', source: 'https://peakprosperity.com/', showSummary: false },
  { key: 'gorozen',  title: 'Gorozen',        source: 'https://blog.gorozen.com/blog',                                        showSummary: true  },
  { key: 'equitymates',    title: '🇦🇺 Equity',    source: 'https://equitymates.com/show/equity-mates-investing-podcast/', showSummary: false },
  { key: 'hket',     title: 'HKET',           source: 'https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B', showSummary: false },
]

export default function App() {
  const [data, setData] = useState({})
  const [loadingMap, setLoadingMap] = useState(
    Object.fromEntries([...SOURCES.map(s => [s.key, true]), ['equitymates', true], ['peakprosperity', true]])
  )
  const [errorMap, setErrorMap] = useState({})
  const [equitymates, setEquitymates] = useState(null)
  const [peakprosperity, setPeakprosperity] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshState, setRefreshState] = useState('idle') // idle | pending | done | error

  const PODCAST_SETTERS = { equitymates: setEquitymates, peakprosperity: setPeakprosperity }

  function loadAll() {
    const t = Date.now()
    return Promise.allSettled(SOURCES.map(({ key }) =>
      loadJson(`${key}?t=${t}`)
        .then(d => {
          if (key in PODCAST_SETTERS) PODCAST_SETTERS[key](d)
          else setData(prev => ({ ...prev, [key]: d }))
          setLoadingMap(prev => ({ ...prev, [key]: false }))
        })
        .catch(() => {
          setLoadingMap(prev => ({ ...prev, [key]: false }))
          setErrorMap(prev => ({ ...prev, [key]: true }))
        })
    ))
  }

  useEffect(() => {
    loadJson('meta')
      .then(meta => setLastUpdated(meta.updated_at))
      .catch(() => {})
    loadAll()
  }, [])

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

  return (
    <div className="min-h-screen bg-paper">
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

      {/* Section nav — sticky below header */}
      <NavBar sources={SOURCES} />

      <main className="max-w-3xl mx-auto px-4 py-5">
        {/* Stock indices */}
        <StockBar />

        {/* All sections in SOURCES order */}
        {SOURCES.map(s => (
          <div id={`section-${s.key}`} key={s.key}>
            {s.key === 'equitymates' ? (
              <PodcastSection title="🇦🇺 Equity Mates" data={equitymates} loading={loadingMap['equitymates']} error={errorMap['equitymates']} />
            ) : s.key === 'peakprosperity' ? (
              <PodcastSection title="Peak" data={peakprosperity} loading={loadingMap['peakprosperity']} error={errorMap['peakprosperity']} />
            ) : (
              <NewsSection title={s.title} source={s.source} items={data[s.key] || []} loading={loadingMap[s.key]} error={errorMap[s.key]} showSummary={s.showSummary} note={s.note} />
            )}
          </div>
        ))}
      </main>

      <footer className="border-t-2 border-ink text-center font-mono text-[10px] tracking-widest uppercase text-neutral py-5">
        每日 13:41（墨尔本）自动更新 · GitHub Actions
      </footer>
    </div>
  )
}
