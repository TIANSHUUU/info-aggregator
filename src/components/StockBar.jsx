import { useState, useEffect } from 'react'

const INDICES = [
  // A股
  { symbol: '000001.SS', label: '上证指数', market: 'CN' },
  { symbol: '399001.SZ', label: '深证成指', market: 'CN' },
  { symbol: '399006.SZ', label: '创业板',   market: 'CN' },
  { symbol: '000300.SS', label: '沪深300',  market: 'CN' },
  { symbol: '000905.SS', label: '中证500',  market: 'CN' },
  { symbol: '000688.SS', label: '科创50',   market: 'CN' },
  // 美股
  { symbol: '^GSPC',     label: '标普500',  market: 'US' },
  { symbol: '^IXIC',     label: '纳斯达克', market: 'US' },
]

function fetchQuote(symbol) {
  // Yahoo Finance v8 — CORS supported from browser
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`
  return fetch(url)
    .then(r => r.json())
    .then(data => {
      const meta = data?.chart?.result?.[0]?.meta
      if (!meta) throw new Error('no data')
      const price = meta.regularMarketPrice
      const prev  = meta.chartPreviousClose || meta.previousClose
      const change = price - prev
      const pct    = (change / prev) * 100
      return { price, change, pct, currency: meta.currency }
    })
}

function QuoteChip({ index }) {
  const [quote, setQuote] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetchQuote(index.symbol)
      .then(setQuote)
      .catch(() => setError(true))
  }, [index.symbol])

  const color = quote
    ? quote.change >= 0 ? 'text-red-500' : 'text-green-600'
    : 'text-gray-400'

  const sign = quote?.change >= 0 ? '+' : ''

  return (
    <div className="flex flex-col items-center px-4 py-2 min-w-[90px]">
      <span className="text-xs text-gray-400 mb-0.5">{index.label}</span>
      {error ? (
        <span className="text-xs text-gray-300">—</span>
      ) : quote ? (
        <>
          <span className="text-sm font-semibold tabular-nums">
            {quote.price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })}
          </span>
          <span className={`text-xs tabular-nums ${color}`}>
            {sign}{quote.pct.toFixed(2)}%
          </span>
        </>
      ) : (
        <span className="text-xs text-gray-300 animate-pulse">载入中</span>
      )}
    </div>
  )
}

export default function StockBar() {
  const cn = INDICES.filter(i => i.market === 'CN')
  const us = INDICES.filter(i => i.market === 'US')

  return (
    <div className="card mb-4">
      <div className="section-title">实时行情</div>
      <div className="flex flex-wrap">
        <div className="flex flex-wrap border-r border-gray-100 mr-2 pr-2">
          {cn.map(i => <QuoteChip key={i.symbol} index={i} />)}
        </div>
        <div className="flex flex-wrap">
          {us.map(i => <QuoteChip key={i.symbol} index={i} />)}
        </div>
      </div>
      <p className="text-xs text-gray-300 mt-2 text-right">数据来源 Yahoo Finance · 页面加载时更新</p>
    </div>
  )
}
