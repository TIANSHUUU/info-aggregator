import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export default function NewsSection({ title, source, items = [], loading, error, showSummary = false }) {
  return (
    <div className="card mb-4">
      <div className="flex items-center justify-between mb-3">
        <div className="section-title mb-0">{title}</div>
        {source && (
          <a
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-300 hover:text-gray-500"
          >
            前往源站 →
          </a>
        )}
      </div>

      {loading && (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {error && (
        <p className="text-xs text-gray-400">暂时无法获取内容，请稍后重试。</p>
      )}

      {!loading && !error && items.length === 0 && (
        <p className="text-xs text-gray-400">今日暂无更新。</p>
      )}

      {!loading && !error && items.length > 0 && (
        <ul>
          {items.map((item, i) => (
            <li key={i} className="news-item">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm leading-snug block"
              >
                {item.title}
              </a>
              {showSummary && item.summary && (
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">{item.summary}</p>
              )}
              {item.date && (
                <span className="text-xs text-gray-300 mt-0.5 block">
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
