import { useState, useEffect } from 'react'

const BASE = import.meta.env.BASE_URL

export default function StockBar() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/stocks.json`)
      .then(r => r.json())
      .then(data => {
        setStocks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const cn = stocks.filter(s => s.market === 'CN')
  const us = stocks.filter(s => s.market === 'US')

  return (
    <div className="card mb-4">
      <div className="section-title">实时行情</div>

      {loading && (
        <div className="flex gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-10 w-20 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {!loading && stocks.length === 0 && (
        <p className="text-xs text-gray-400">暂无数据</p>
      )}

      {!loading && stocks.length > 0 && (
        <div className="flex flex-wrap">
          {/* A股 */}
          <div className="flex flex-wrap border-r border-gray-100 mr-2 pr-2">
            {cn.map(s => <QuoteChip key={s.symbol} stock={s} />)}
          </div>
          {/* 美股 */}
          <div className="flex flex-wrap">
            {us.map(s => <QuoteChip key={s.symbol} stock={s} />)}
          </div>
        </div>
      )}

      <p className="text-xs text-gray-300 mt-2 text-right">每日 11:00 更新</p>
    </div>
  )
}

function QuoteChip({ stock }) {
  const up    = stock.change >= 0
  const color = up ? 'text-red-500' : 'text-green-600'
  const sign  = up ? '+' : ''

  return (
    <div className="flex flex-col items-center px-4 py-2 min-w-[90px]">
      <span className="text-xs text-gray-400 mb-0.5">{stock.label}</span>
      <span className="text-sm font-semibold tabular-nums">
        {stock.price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })}
      </span>
      <span className={`text-xs tabular-nums ${color}`}>
        {sign}{stock.pct.toFixed(2)}%
      </span>
    </div>
  )
}
