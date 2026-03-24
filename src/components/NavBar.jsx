import { useState, useEffect, useRef } from 'react'

export default function NavBar({ sources }) {
  const [active, setActive] = useState(sources[0]?.key)
  const navRef = useRef(null)

  // Highlight nav item based on scroll position
  useEffect(() => {
    const handler = () => {
      const offsets = sources.map(s => {
        const el = document.getElementById(`section-${s.key}`)
        return el ? { key: s.key, top: el.getBoundingClientRect().top } : null
      }).filter(Boolean)

      // The section whose top is closest to (but still above) 120px wins
      const visible = offsets.filter(o => o.top <= 120)
      if (visible.length > 0) {
        setActive(visible[visible.length - 1].key)
      } else if (offsets.length > 0) {
        setActive(offsets[0].key)
      }
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [sources])

  const scrollTo = (key) => {
    const el = document.getElementById(`section-${key}`)
    if (!el) return
    const y = el.getBoundingClientRect().top + window.scrollY - 110
    window.scrollTo({ top: y, behavior: 'smooth' })
    setActive(key)
  }

  return (
    <nav
      ref={navRef}
      className="sticky top-[52px] z-10 bg-white border-b border-gray-200 shadow-sm"
    >
      <div className="max-w-3xl mx-auto px-4">
        <div className="flex gap-1 overflow-x-auto scrollbar-none py-2">
          {sources.map(s => (
            <button
              key={s.key}
              onClick={() => scrollTo(s.key)}
              className={`
                flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium
                transition-colors duration-150 whitespace-nowrap
                ${active === s.key
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
            >
              {s.title}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}
