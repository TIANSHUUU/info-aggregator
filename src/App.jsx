import { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import StockBar from './components/StockBar'
import NewsSection from './components/NewsSection'

const BASE = import.meta.env.BASE_URL

async function loadJson(name) {
  const r = await fetch(`${BASE}data/${name}.json`)
  if (!r.ok) throw new Error(`${name} fetch failed`)
  return r.json()
}

const SOURCES = [
  { key: 'initium',  title: '端传媒',         source: 'https://theinitium.com/',                               showSummary: false },
  { key: 'caixin',   title: '财新',            source: 'https://www.caixin.com/',                               showSummary: false },
  { key: 'schwab',   title: 'Charles Schwab', source: 'https://www.schwab.com/learn/market-commentary',        showSummary: true  },
  { key: 'hket',     title: 'HKET 即时中国',  source: 'https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B', showSummary: false },
  { key: 'mingpao',  title: '明报中国',        source: 'https://news.mingpao.com/',                             showSummary: false },
]

export default function App() {
  const [data, setData] = useState({})
  const [loadingMap, setLoadingMap] = useState(
    Object.fromEntries(SOURCES.map(s => [s.key, true]))
  )
  const [errorMap, setErrorMap] = useState({})
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    // Load last updated timestamp
    loadJson('meta')
      .then(meta => setLastUpdated(meta.updated_at))
      .catch(() => {})

    // Load each source independently so partial failures don't block others
    SOURCES.forEach(({ key }) => {
      loadJson(key)
        .then(items => {
          setData(prev => ({ ...prev, [key]: items }))
          setLoadingMap(prev => ({ ...prev, [key]: false }))
        })
        .catch(() => {
          setLoadingMap(prev => ({ ...prev, [key]: false }))
          setErrorMap(prev => ({ ...prev, [key]: true }))
        })
    })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-base font-semibold tracking-tight">每日资讯</h1>
          <span className="text-xs text-gray-400">
            {lastUpdated
              ? `更新于 ${dayjs(lastUpdated).format('MM/DD HH:mm')}`
              : dayjs().format('MM月DD日')}
          </span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-5">
        {/* Stock indices */}
        <StockBar />

        {/* News sources */}
        {SOURCES.map(s => (
          <NewsSection
            key={s.key}
            title={s.title}
            source={s.source}
            items={data[s.key] || []}
            loading={loadingMap[s.key]}
            error={errorMap[s.key]}
            showSummary={s.showSummary}
          />
        ))}
      </main>

      <footer className="text-center text-xs text-gray-300 py-6">
        每日 11:00 自动更新 · GitHub Actions
      </footer>
    </div>
  )
}
