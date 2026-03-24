"""
Stock indices & commodities — server-side fetch (no CORS issue).
A股: Sina Finance API
其余: Yahoo Finance API
"""
import re
import requests

SINA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0)",
    "Referer": "https://finance.sina.com.cn",
}
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InfoAggre/1.0)"}

# Sina symbol -> (label, market)
CN_SYMBOLS = {
    "sh000001": ("上证指数", "CN"),
    "sz399001": ("深证成指", "CN"),
    "sz399006": ("创业板",   "CN"),
    "sh000300": ("沪深300",  "CN"),
    "sh000905": ("中证500",  "CN"),
    "sh000688": ("科创50",   "CN"),
}

# Yahoo symbol -> (label, market)
YAHOO_SYMBOLS = {
    "^N225": ("日经225",  "INTL"),
    "^GSPC": ("标普500",  "INTL"),
    "^IXIC": ("纳斯达克", "INTL"),
    "GC=F":  ("黄金",     "COMMODITY"),
    "BZ=F":  ("布伦特原油", "COMMODITY"),
}


def fetch_cn():
    symbols = ",".join(CN_SYMBOLS.keys())
    url  = f"https://hq.sinajs.cn/list={symbols}"
    resp = requests.get(url, headers=SINA_HEADERS, timeout=15)
    resp.encoding = "gbk"
    text = resp.text

    results = []
    for sym, (label, market) in CN_SYMBOLS.items():
        m = re.search(rf'hq_str_{re.escape(sym)}="([^"]+)"', text)
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
                "symbol": sym, "label": label, "market": market,
                "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
            })
        except (ValueError, ZeroDivisionError):
            continue
    return results


def fetch_yahoo():
    results = []
    for sym, (label, market) in YAHOO_SYMBOLS.items():
        try:
            url  = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d"
            resp = requests.get(url, headers=YAHOO_HEADERS, timeout=15)
            data = resp.json()
            meta = data["chart"]["result"][0]["meta"]
            price      = meta["regularMarketPrice"]
            prev_close = meta.get("chartPreviousClose") or meta.get("previousClose", price)
            change     = price - prev_close
            pct        = (change / prev_close) * 100 if prev_close else 0
            # Commodities: 2 decimal places; indices: vary
            decimals   = 2
            results.append({
                "symbol": sym, "label": label, "market": market,
                "price": round(price, decimals), "change": round(change, decimals), "pct": round(pct, 2),
            })
        except Exception as e:
            print(f"  [stocks] {label} ({sym}) error: {e}")
    return results


def fetch():
    return fetch_cn() + fetch_yahoo()
