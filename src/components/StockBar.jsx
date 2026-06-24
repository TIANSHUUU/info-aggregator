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
    <section className="mb-7">
      <div className="sec-bar-mkt">
        <span className="sec-name"><span className="cn">实时行情</span> Markets</span>
        <span className="sec-src text-neutral">每日 11:00 更新</span>
      </div>

      {loading && (
        <div className="flex gap-3 flex-wrap">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="skeleton h-12 w-24" />
          ))}
        </div>
      )}

      {!loading && stocks.length === 0 && (
        <p className="font-body text-sm text-muted">暂无数据</p>
      )}

      {!loading && stocks.length > 0 && (
        <div className="space-y-3">
          {GROUPS.map(g => {
            const items = byGroup(g.key)
            if (!items.length) return null
            return (
              <div key={g.key}>
                <div className="mkt-group-label">{g.label}</div>
                <div className="quotes">
                  {items.map(s => <QuoteCell key={s.symbol} stock={s} />)}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}

function QuoteCell({ stock }) {
  const up    = stock.change >= 0
  const color = up ? 'text-up' : 'text-down'
  const sign  = up ? '+' : ''

  // Commodities show 2 decimals; large indices show commas
  const priceStr = stock.market === 'COMMODITY'
    ? stock.price.toFixed(2)
    : stock.price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })

  return (
    <div className="quote-cell">
      <span className="quote-lab">{stock.label}</span>
      <span className="quote-px">{priceStr}</span>
      <span className={`quote-pct ${color}`}>
        {sign}{stock.pct.toFixed(2)}%
      </span>
    </div>
  )
}
