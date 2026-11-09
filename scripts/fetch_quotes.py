#!/usr/bin/env python3
"""Download daily closes for the tickers in tickers.txt and write data/quotes.json.

For each ticker it records the latest price, the change vs the previous close
(in dollars and percent) and the typical absolute daily move over the last ~20
sessions. During market hours the last bar is the current (delayed) price.
"""
import datetime as dt
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "quotes.json"
CHUNK = 40


def read_tickers(path=ROOT / "tickers.txt"):
    seen, out = set(), []
    for line in path.read_text(encoding="utf-8").splitlines():
        t = line.split("#", 1)[0].strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def summarize(ticker, closes):
    """closes: list of floats, oldest first. Returns a dict or None."""
    closes = [float(c) for c in closes if c is not None and not math.isnan(float(c))]
    if len(closes) < 2:
        return None
    last, prev = closes[-1], closes[-2]
    if prev <= 0:
        return None
    change = last - prev
    diffs = [abs(b - a) for a, b in zip(closes[:-1], closes[1:])][-20:]
    avg = sum(diffs) / len(diffs)
    return {
        "t": ticker,
        "p": round(last, 2),
        "pc": round(prev, 2),
        "c": round(change, 2),
        "pct": round(change / prev * 100, 2),
        "avg": round(avg, 2),
        "spark": [round(x, 2) for x in closes[-6:]],
    }


def fetch(tickers):
    import pandas as pd
    import yfinance as yf

    quotes, failed, asof = [], [], None
    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i + CHUNK]
        df = None
        for attempt in range(3):
            try:
                df = yf.download(chunk, period="2mo", interval="1d", group_by="ticker",
                                 auto_adjust=False, progress=False, threads=True)
                if df is not None and not df.empty:
                    break
            except Exception as exc:  # network, rate limit, parsing
                print(f"chunk {i // CHUNK + 1} attempt {attempt + 1} failed: {exc}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
        if df is None or df.empty:
            failed.extend(chunk)
            continue
        for t in chunk:
            try:
                s = df[t]["Close"] if isinstance(df.columns, pd.MultiIndex) else df["Close"]
                s = s.dropna()
                item = summarize(t, s.tolist())
                if item is None:
                    failed.append(t)
                    continue
                quotes.append(item)
                last_day = s.index[-1].date().isoformat()
                asof = max(asof, last_day) if asof else last_day
            except Exception:
                failed.append(t)
        time.sleep(2)
    return quotes, failed, asof


def main():
    tickers = read_tickers()
    quotes, failed, asof = fetch(tickers)
    old = None
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            old = None
    if len(quotes) < max(1, len(tickers) // 2):
        msg = f"Only {len(quotes)} of {len(tickers)} tickers returned data."
        print(msg, file=sys.stderr)
        if old and old.get("quotes"):
            old["last_error"] = msg + " Showing the previous data."
            OUT.parent.mkdir(exist_ok=True)
            OUT.write_text(json.dumps(old, separators=(",", ":")), encoding="utf-8")
            return 0
        return 1
    data = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": "yfinance (Yahoo Finance), may be delayed",
        "asof": asof,
        "count": len(quotes),
        "failed": sorted(set(failed)),
        "quotes": quotes,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(quotes)} quotes, {len(set(failed))} failed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
