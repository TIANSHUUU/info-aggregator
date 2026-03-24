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
    <div className="card mb-4">
      <h2 className="section-title">实时行情</h2>

      {loading && (
        <div className="flex gap-3 flex-wrap">
          {[...Array(11)].map((_, i) => (
            <div key={i} className="h-12 w-20 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {!loading && stocks.length === 0 && (
        <p className="text-sm text-gray-500">暂无数据</p>
      )}

      {!loading && stocks.length > 0 && (
        <div className="space-y-3">
          {GROUPS.map(g => {
            const items = byGroup(g.key)
            if (!items.length) return null
            return (
              <div key={g.key}>
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
                  {g.label}
                </div>
                <div className="flex flex-wrap gap-x-2 gap-y-1">
                  {items.map(s => <QuoteChip key={s.symbol} stock={s} />)}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3 text-right">每日 11:00 更新</p>
    </div>
  )
}

function QuoteChip({ stock }) {
  const up    = stock.change >= 0
  const color = up ? 'text-red-600' : 'text-emerald-700'
  const sign  = up ? '+' : ''

  // Commodities show 2 decimals; large indices show commas
  const priceStr = stock.market === 'COMMODITY'
    ? stock.price.toFixed(2)
    : stock.price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })

  return (
    <div className="flex flex-col items-center px-3 py-2 min-w-[82px] bg-gray-50 rounded-lg">
      <span className="text-xs text-gray-500 font-medium mb-0.5 whitespace-nowrap">{stock.label}</span>
      <span className="text-[15px] font-semibold tabular-nums text-gray-900">{priceStr}</span>
      <span className={`text-xs tabular-nums font-medium ${color}`}>
        {sign}{stock.pct.toFixed(2)}%
      </span>
    </div>
  )
}
