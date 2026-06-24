/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: 'var(--color-paper)',
        'paper-2': 'var(--color-paper-2)',
        rule: 'var(--color-rule)',
        'rule-2': 'var(--color-rule-2)',
        neutral: 'var(--color-neutral)',
        muted: 'var(--color-muted)',
        ink: 'var(--color-ink)',
        'accent-ink': 'var(--color-accent-ink)',
        accent: 'var(--color-accent)',
        orange: 'var(--color-orange)',
        blue: 'var(--color-blue)',
        up: 'var(--color-up)',
        down: 'var(--color-down)',
      },
      fontFamily: {
        display: ['Fraunces', 'Songti SC', 'Noto Serif SC', 'serif'],
        body: ['Newsreader', 'PingFang SC', 'Hiragino Sans GB', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
}
