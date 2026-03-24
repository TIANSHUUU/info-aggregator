import { useState, useEffect } from 'react'
import dayjs from 'dayjs'
import StockBar from './components/StockBar'
import NewsSection from './components/NewsSection'
import NavBar from './components/NavBar'

const BASE = import.meta.env.BASE_URL

async function loadJson(name) {
  const r = await fetch(`${BASE}data/${name}.json`)
  if (!r.ok) throw new Error(`${name} fetch failed`)
  return r.json()
}

const SOURCES = [
  { key: 'initium',  title: '端传媒',         source: 'https://theinitium.com/',                                          showSummary: false },
  { key: 'caixin',   title: '财新',            source: 'https://www.caixin.com/',                                          showSummary: true  },
  { key: 'schwab',   title: 'Charles Schwab', source: 'https://www.schwab.com/learn/market-commentary',                   showSummary: true, note: '日期信息暂不可用，以下为最新文章' },
  { key: 'hket',     title: 'HKET',           source: 'https://china.hket.com/srac002/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B', showSummary: false },
]

export default function App() {
  const [data, setData] = useState({})
  const [loadingMap, setLoadingMap] = useState(
    Object.fromEntries(SOURCES.map(s => [s.key, true]))
  )
  const [errorMap, setErrorMap] = useState({})
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    loadJson('meta')
      .then(meta => setLastUpdated(meta.updated_at))
      .catch(() => {})

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
      {/* Top header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-20 h-[52px] flex items-center">
        <div className="max-w-3xl mx-auto px-4 w-full flex items-center justify-between">
          <h1 className="text-base font-semibold text-gray-900 tracking-tight">每日资讯</h1>
          <span className="text-sm text-gray-500">
            {lastUpdated
              ? `更新于 ${dayjs(lastUpdated).format('MM/DD HH:mm')}`
              : dayjs().format('MM月DD日')}
          </span>
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
