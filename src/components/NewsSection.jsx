import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export default function NewsSection({ title, source, items = [], loading, error, showSummary = false, note }) {
  return (
    <div className="card mb-4">
      {/* Section header */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="section-title mb-0">{title}</h2>
        {source && (
          <a
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-gray-500 hover:text-gray-800 flex-shrink-0"
          >
            前往源站 →
          </a>
        )}
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-5 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <p className="text-sm text-gray-500">暂时无法获取内容，请稍后重试。</p>
      )}

      {/* Date-unavailable note (e.g. Schwab) */}
      {note && !loading && !error && items.length > 0 && (
        <p className="text-sm text-amber-600 mb-3 font-medium">{note}</p>
      )}

      {/* Empty state */}
      {!loading && !error && items.length === 0 && (
        <p className="text-sm text-gray-500">今日暂无更新。</p>
      )}

      {/* Article list */}
      {!loading && !error && items.length > 0 && (
        <ul>
          {items.map((item, i) => (
            <li key={i} className="news-item">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[15px] leading-relaxed font-medium text-gray-900 block hover:text-blue-700"
              >
                {item.title}
              </a>
              {showSummary && item.summary && (
                <p className="text-sm text-gray-600 mt-1.5 leading-relaxed">
                  {item.summary}
                </p>
              )}
              {item.date && (
                <span className="text-xs text-gray-400 mt-1 block">
                  {dayjs(item.date).fromNow()}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
