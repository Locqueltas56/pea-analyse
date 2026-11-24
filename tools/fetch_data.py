#!/usr/bin/env python3
"""Récupère cours (hebdo, 10 ans) et fondamentaux depuis Yahoo Finance (yfinance)
et écrit docs/data/stocks.json. Liste des valeurs : tickers.csv (modifiable).

Usage : python tools/fetch_data.py
"""
import csv, json, math, pathlib, sys, time, datetime as dt

import pandas as pd
import yfinance as yf

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/data/stocks.json"
BENCH = ("^FCHI", "CAC 40")
MIN_OK_RATIO = 0.5  # n'écrase pas les données si trop d'échecs


def num(x, nd=None):
    try:
        if x is None:
            return None
        x = float(x)
        if math.isnan(x) or math.isinf(x):
            return None
        return round(x, nd) if nd is not None else x
    except (TypeError, ValueError):
        return None


def weekly_closes(ticker):
    """Cours hebdomadaires : "c" = cours réel, "a" = cours ajusté des dividendes (rendement total)."""
    h = yf.Ticker(ticker).history(period="10y", interval="1wk", auto_adjust=False)
    h = h.dropna(subset=["Close"])
    if h.empty:
        return None
    idx = h.index.tz_localize(None) if h.index.tz is not None else h.index
    df = pd.DataFrame({"c": h["Close"].values}, index=pd.DatetimeIndex(idx).normalize())
    if "Adj Close" in h.columns:
        df["a"] = h["Adj Close"].values
        df["a"] = df["a"].fillna(df["c"])
    df = df[~df.index.duplicated(keep="last")]
    full = pd.date_range(df.index[0], df.index[-1], freq="7D")
    df = df.reindex(full).ffill()
    out = {"start": df.index[0].date().isoformat(), "c": [round(float(v), 3) for v in df["c"].values]}
    if "a" in df:
        out["a"] = [round(float(v), 3) for v in df["a"].values]
    return out


def dividend_stats(t, price):
    d = t.dividends
    if d is None or len(d) == 0:
        return 0.0, None, 0
    d = d.copy()
    d.index = pd.DatetimeIndex(d.index).tz_localize(None) if d.index.tz is not None else d.index
    last12 = d[d.index >= pd.Timestamp.now() - pd.Timedelta(days=365)].sum()
    dy = float(last12) / price if price else None
    by_year = d.groupby(d.index.year).sum()
    cur = dt.date.today().year
    by_year = by_year[by_year.index < cur]  # années complètes seulement
    growth, years = None, 0
    if len(by_year) >= 6 and by_year.iloc[-6] > 0:
        growth = (by_year.iloc[-1] / by_year.iloc[-6]) ** (1 / 5) - 1
    vals = list(by_year.values)
    for i in range(len(vals) - 1, 0, -1):
        if vals[i] >= vals[i - 1] * 0.999:
            years += 1
        else:
            break
    return num(dy, 4), num(growth, 4), years


def statements(t):
    try:
        fin = t.financials
        rev = fin.loc["Total Revenue"].dropna().sort_index()
        ni = fin.loc["Net Income"].dropna().sort_index()
        both = rev.index.intersection(ni.index)[-4:]
        return ([d.year for d in both], [num(rev[d]) for d in both], [num(ni[d]) for d in both])
    except Exception:
        return [], [], []


def fetch_one(row):
    tk = row["ticker"]
    hist = weekly_closes(tk)
    if not hist or len(hist["c"]) < 60:
        raise ValueError("historique insuffisant")
    t = yf.Ticker(tk)
    info = t.info or {}
    c = hist["c"]
    price = num(info.get("currentPrice") or info.get("regularMarketPrice")) or c[-1]
    mcap = num(info.get("marketCap"))
    fcf = num(info.get("freeCashflow"))
    dy, dgrowth, dyears = dividend_stats(t, price)
    years, rev, ni = statements(t)
    return {
        "t": tk, "name": row.get("name") or info.get("shortName") or tk,
        "sector": info.get("sector") or row.get("sector") or "Autre",
        "country": row.get("country") or "", "currency": info.get("currency") or "EUR",
        "kind": row.get("kind") or "stock",
        "price": num(price, 3), "prev": num(info.get("previousClose") or c[-2], 3),
        "mcap": mcap,
        "per": num(info.get("trailingPE"), 2), "pb": num(info.get("priceToBook"), 2),
        "roe": num(info.get("returnOnEquity"), 4), "margin": num(info.get("profitMargins"), 4),
        "de": num(info.get("debtToEquity"), 1),
        "fcfy": num(fcf / mcap, 4) if fcf is not None and mcap else None,
        "dy": dy, "payout": num(info.get("payoutRatio"), 3), "dgrowth": dgrowth, "dyears": dyears,
        "years": years, "rev": rev, "ni": ni, "hist": hist,
    }


def main():
    rows = list(csv.DictReader(open(ROOT / "tickers.csv", encoding="utf-8")))
    stocks, failed = [], []
    for i, row in enumerate(rows, 1):
        try:
            stocks.append(fetch_one(row))
            print(f"[{i}/{len(rows)}] OK  {row['ticker']}")
        except Exception as e:  # on continue : une valeur en échec ne bloque pas les autres
            failed.append(row["ticker"])
            print(f"[{i}/{len(rows)}] ERR {row['ticker']} : {e}", file=sys.stderr)
        time.sleep(0.6)

    if len(stocks) < len(rows) * MIN_OK_RATIO:
        sys.exit(f"Trop d'échecs ({len(failed)}/{len(rows)}) : données existantes conservées.")

    bench = weekly_closes(BENCH[0])
    out = {"meta": {"demo": False, "source": "Yahoo Finance",
                    "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    "failed": failed,
                    "bench": {"name": BENCH[1], **(bench or {"start": None, "c": []})}},
           "stocks": stocks}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    print(f"{len(stocks)} valeurs écrites, {len(failed)} en échec : {failed}")


if __name__ == "__main__":
    main()
