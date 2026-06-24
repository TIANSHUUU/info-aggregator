import { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import StockBar from './components/StockBar'
import NewsSection from './components/NewsSection'
import PodcastSection from './components/PodcastSection'
import NavBar from './components/NavBar'

const BASE = import.meta.env.BASE_URL

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
  const [refreshState, setRefreshState] = useState('idle') // idle | pending | done

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

  // Reload the latest published data (does NOT trigger a fresh server-side
  // fetch — that runs daily via the workflow's cron schedule). No token needed.
  async function handleRefresh() {
    if (refreshState === 'pending') return
    setRefreshState('pending')
    try {
      const meta = await loadJson(`meta?t=${Date.now()}`)
      setLastUpdated(meta.updated_at)
    } catch {}
    await loadAll()
    setRefreshState('done')
    setTimeout(() => setRefreshState('idle'), 2500)
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
                  : 'border-orange text-orange hover:bg-orange hover:text-ink'
              }`}
            >
              {refreshState === 'pending' ? '刷新中…' : refreshState === 'done' ? '已刷新 ✓' : '立即更新'}
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
        每日 13:30（墨尔本）自动更新 · GitHub Actions
      </footer>
    </div>
  )
}
