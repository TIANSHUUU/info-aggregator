import dayjs from 'dayjs'

export default function PodcastSection({ title, data, loading, error }) {
  return (
    <section className="mb-7">
      <div className="sec-bar-cast">
        <span className="sec-name"><span className="cn">{title}</span></span>
        {data?.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer"
            className="sec-src hover:underline">
            前往源站 →
          </a>
        )}
      </div>

      {loading && (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-5" />
          ))}
        </div>
      )}

      {error && <p className="font-body text-sm text-muted">暂时无法获取内容，请稍后重试。</p>}

      {!loading && !error && data?.sections?.length > 0 && (
        <>
          {/* Episode title + date */}
          <div className="mb-4 pb-3 border-b border-rule">
            <a href={data.url} target="_blank" rel="noopener noreferrer" className="ep-title block">
              {data.title}
            </a>
            {data.date && (
              <div className="ep-date mt-1">{dayjs(data.date).format('YYYY年MM月DD日')}</div>
            )}
          </div>

          {/* Summary sections */}
          <div className="space-y-4">
            {data.sections.map((section, i) => (
              <div key={i}>
                <h3 className="cast-sec-h">{section.heading}</h3>
                <ul className="space-y-1">
                  {section.points.map((point, j) => (
                    <li key={j} className="cast-point">
                      <span className="text-accent flex-shrink-0">—</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Stocks mentioned */}
          {data.stocks?.length > 0 && (
            <div className="mt-4 pt-3 border-t border-rule">
              <span className="cast-tag-label">提及标的</span>
              {data.stocks.map((s, i) => (
                <span key={i} className="cast-tag">{s}</span>
              ))}
            </div>
          )}
        </>
      )}

      {!loading && !error && !data?.sections?.length && (
        <p className="font-body text-sm text-muted">暂无内容。</p>
      )}
    </section>
  )
}
