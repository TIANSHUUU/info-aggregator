"""
Stock indices — server-side fetch (no CORS issue).
A股: Sina Finance API
美股: Yahoo Finance API
"""
import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0)",
    "Referer": "https://finance.sina.com.cn",
}

# Sina symbol -> display label
CN_SYMBOLS = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板",
    "sh000300": "沪深300",
    "sh000905": "中证500",
    "sh000688": "科创50",
}

# Yahoo symbol -> display label
US_SYMBOLS = {
    "^GSPC": "标普500",
    "^IXIC": "纳斯达克",
}


def fetch_cn():
    """Fetch Chinese indices via Sina Finance."""
    symbols = ",".join(CN_SYMBOLS.keys())
    url = f"https://hq.sinajs.cn/list={symbols}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "gbk"
    text = resp.text

    results = []
    for sym, label in CN_SYMBOLS.items():
        pattern = rf'hq_str_{re.escape(sym)}="([^"]+)"'
        m = re.search(pattern, text)
        if not m:
            continue
        fields = m.group(1).split(",")
        if len(fields) < 4:
            continue
        try:
            price      = float(fields[3])
            prev_close = float(fields[2])
            change     = price - prev_close
            pct        = (change / prev_close) * 100 if prev_close else 0
            results.append({
                "symbol": sym,
                "label":  label,
                "market": "CN",
                "price":  round(price, 2),
                "change": round(change, 2),
                "pct":    round(pct, 2),
            })
        except (ValueError, ZeroDivisionError):
            continue
    return results


def fetch_us():
    """Fetch US indices via Yahoo Finance (server-side, no CORS)."""
    results = []
    for sym, label in US_SYMBOLS.items():
        try:
            url  = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d"
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            data = resp.json()
            meta = data["chart"]["result"][0]["meta"]
            price      = meta["regularMarketPrice"]
            prev_close = meta.get("chartPreviousClose") or meta.get("previousClose", price)
            change     = price - prev_close
            pct        = (change / prev_close) * 100 if prev_close else 0
            results.append({
                "symbol": sym,
                "label":  label,
                "market": "US",
                "price":  round(price, 2),
                "change": round(change, 2),
                "pct":    round(pct, 2),
            })
        except Exception as e:
            print(f"  [stocks] {label} error: {e}")
    return results


def fetch():
    cn = fetch_cn()
    us = fetch_us()
    return cn + us
