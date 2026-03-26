import dayjs from 'dayjs'

export default function PodcastSection({ data, loading, error }) {
  return (
    <div className="card mb-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="section-title mb-0">🇦🇺 Equity Mates</h2>
        {data?.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer"
            className="text-sm text-gray-500 hover:text-gray-800 flex-shrink-0">
            前往源站 →
          </a>
        )}
      </div>

      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-5 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {error && <p className="text-sm text-gray-500">暂时无法获取内容，请稍后重试。</p>}

      {!loading && !error && data?.sections?.length > 0 && (
        <>
          {/* Episode title + date */}
          <div className="mb-4 pb-3 border-b border-gray-100">
            <a href={data.url} target="_blank" rel="noopener noreferrer"
              className="text-[15px] font-semibold text-gray-900 hover:text-blue-700 leading-snug block">
              {data.title}
            </a>
            {data.date && (
              <span className="text-xs text-gray-400 mt-1 block">
                {dayjs(data.date).format('YYYY年MM月DD日')}
              </span>
            )}
          </div>

          {/* Summary sections */}
          <div className="space-y-4">
            {data.sections.map((section, i) => (
              <div key={i}>
                <h3 className="text-sm font-semibold text-gray-800 mb-1.5">
                  {section.heading}
                </h3>
                <ul className="space-y-1">
                  {section.points.map((point, j) => (
                    <li key={j} className="flex gap-2 text-sm text-gray-700 leading-relaxed">
                      <span className="text-gray-300 mt-0.5 flex-shrink-0">·</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Stocks mentioned */}
          {data.stocks?.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400 mr-2">提及标的：</span>
              {data.stocks.map((s, i) => (
                <span key={i} className="inline-block text-xs bg-gray-100 text-gray-600 rounded px-2 py-0.5 mr-1 mb-1">
                  {s}
                </span>
              ))}
            </div>
          )}
        </>
      )}

      {!loading && !error && !data?.sections?.length && (
        <p className="text-sm text-gray-500">暂无内容。</p>
      )}
    </div>
  )
}
