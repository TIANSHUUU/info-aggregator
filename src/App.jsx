import { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import StockBar from './components/StockBar'
import NewsSection from './components/NewsSection'
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
  { key: 'hket',     title: 'HKET',           source: 'https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B', showSummary: false },
]

const DISPATCH_URL = 'https://api.github.com/repos/TIANSHUUU/info-aggregator/actions/workflows/update.yml/dispatches'
const FRONTEND_TOKEN = import.meta.env.VITE_GITHUB_TOKEN

export default function App() {
  const [data, setData] = useState({})
  const [loadingMap, setLoadingMap] = useState(
    Object.fromEntries(SOURCES.map(s => [s.key, true]))
  )
  const [errorMap, setErrorMap] = useState({})
  const [lastUpdated, setLastUpdated] = useState(null)
  const [refreshState, setRefreshState] = useState('idle') // idle | pending | done | error

  function loadAll() {
    SOURCES.forEach(({ key }) => {
      loadJson(`${key}?t=${Date.now()}`)
        .then(items => {
          setData(prev => ({ ...prev, [key]: items }))
          setLoadingMap(prev => ({ ...prev, [key]: false }))
        })
        .catch(() => {
          setLoadingMap(prev => ({ ...prev, [key]: false }))
          setErrorMap(prev => ({ ...prev, [key]: true }))
        })
    })
  }

  useEffect(() => {
    loadJson('meta')
      .then(meta => setLastUpdated(meta.updated_at))
      .catch(() => {})
    loadAll()
  }, [])

  async function handleRefresh() {
    if (refreshState === 'pending') return
    setRefreshState('pending')

    try {
      const res = await fetch(DISPATCH_URL, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${FRONTEND_TOKEN}`,
          Accept: 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ref: 'main' }),
      })
      if (res.status !== 204) throw new Error(`dispatch ${res.status}`)
    } catch {
      setRefreshState('error')
      setTimeout(() => setRefreshState('idle'), 3000)
      return
    }

    // Poll meta.json until updated_at changes (max 5 min)
    const baseline = lastUpdated
    const deadline = Date.now() + 5 * 60 * 1000
    const poll = setInterval(async () => {
      try {
        const meta = await loadJson(`meta?t=${Date.now()}`)
        if (meta.updated_at !== baseline) {
          clearInterval(poll)
          setLastUpdated(meta.updated_at)
          setRefreshState('done')
          loadAll()
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
    <div className="min-h-screen bg-gray-50">
      {/* Top header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-20 h-[52px] flex items-center">
        <div className="max-w-3xl mx-auto px-4 w-full flex items-center justify-between">
          <h1 className="text-base font-semibold text-gray-900 tracking-tight">每日资讯</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {lastUpdated
                ? `更新于 ${dayjs(lastUpdated).format('MM/DD HH:mm')}`
                : dayjs().format('MM月DD日')}
            </span>
            <button
              onClick={handleRefresh}
              disabled={refreshState === 'pending'}
              className={`text-sm px-3 py-1 rounded-full border transition-all ${
                refreshState === 'pending'
                  ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                  : refreshState === 'done'
                  ? 'border-green-400 text-green-600'
                  : refreshState === 'error'
                  ? 'border-red-400 text-red-500'
                  : 'border-gray-300 text-gray-600 hover:border-gray-500 hover:text-gray-900'
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

        {/* News sources — each with an anchor id */}
        {SOURCES.map(s => (
          <div id={`section-${s.key}`} key={s.key}>
            <NewsSection
              title={s.title}
              source={s.source}
              items={data[s.key] || []}
              loading={loadingMap[s.key]}
              error={errorMap[s.key]}
              showSummary={s.showSummary}
              note={s.note}
            />
          </div>
        ))}
      </main>

      <footer className="text-center text-sm text-gray-400 py-8">
        每日 11:00 自动更新 · GitHub Actions
      </footer>
    </div>
  )
}
