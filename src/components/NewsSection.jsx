import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export default function NewsSection({ title, source, items = [], loading, error, showSummary = false, note }) {
  return (
    <section className="mb-7">
      <div className="sec-bar-news">
        <span className="sec-name"><span className="cn">{title}</span></span>
        {source && (
          <a
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            className="sec-src hover:underline"
          >
            前往源站 →
          </a>
        )}
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-5" />
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <p className="font-body text-sm text-muted">暂时无法获取内容，请稍后重试。</p>
      )}

      {/* Date-unavailable note (e.g. Schwab) */}
      {note && !loading && !error && items.length > 0 && (
        <p className="font-mono text-xs text-accent mb-3 tracking-wide">{note}</p>
      )}

      {/* Empty state */}
      {!loading && !error && items.length === 0 && (
        <p className="font-body text-sm text-muted">今日暂无更新。</p>
      )}

      {/* Article list */}
      {!loading && !error && items.length > 0 && (
        <ul>
          {items.map((item, i) => (
            <li key={i} className="news-row">
              <span className="news-no">{String(i + 1).padStart(2, '0')}</span>
              <div>
                {i === 0 && <span className="stamp">最新</span>}
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="headline"
                >
                  {item.title}
                </a>
                {showSummary && item.summary && (
                  <p className="news-sum">{item.summary}</p>
                )}
                {item.date && (
                  <div className="news-meta">{dayjs(item.date).fromNow()}</div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
