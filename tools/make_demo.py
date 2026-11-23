#!/usr/bin/env python3
"""Génère des données FICTIVES pour tester l'app sans réseau (docs/data/stocks.json)."""
import csv, json, math, random, datetime as dt, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rng = random.Random(42)

def monday_weeks(n):
    today = dt.date.today()
    last = today - dt.timedelta(days=today.weekday())
    start = last - dt.timedelta(weeks=n - 1)
    return start

def walk(n, p0, mu, sigma):
    c, p = [], p0
    for _ in range(n):
        p *= math.exp((mu - 0.5 * sigma ** 2) / 52 + sigma / math.sqrt(52) * rng.gauss(0, 1))
        c.append(round(p, 3))
    return c

N = 521
start = monday_weeks(N)
bench = walk(N, 4500, 0.06, 0.16)
stocks = []
for row in csv.DictReader(open(ROOT / "tickers.csv", encoding="utf-8")):
    p0 = rng.uniform(25, 300)
    c = walk(N, p0, rng.uniform(0.0, 0.13), rng.uniform(0.17, 0.38))
    price = c[-1]
    rev0 = rng.uniform(5e9, 6e10)
    g = rng.uniform(-0.02, 0.12)
    m = rng.uniform(0.02, 0.2)
    rev = [round(rev0 * (1 + g) ** k) for k in range(4)]
    ni = [round(r * m * rng.uniform(0.85, 1.15)) for r in rev]
    pays = rng.random() > 0.15
    stocks.append({
        "t": row["ticker"], "name": row["name"], "sector": row["sector"],
        "country": row["country"], "currency": "EUR",
        "price": round(price, 2), "prev": round(c[-2], 2),
        "mcap": round(rev[-1] * rng.uniform(0.8, 4)),
        "per": round(rng.uniform(4, 40), 1), "pb": round(rng.uniform(0.6, 8), 2),
        "roe": round(rng.uniform(0.03, 0.25), 3), "margin": round(m, 3),
        "de": round(rng.uniform(10, 180), 1), "fcfy": round(rng.uniform(0.0, 0.08), 3),
        "dy": round(rng.uniform(0.01, 0.07), 3) if pays else 0,
        "payout": round(rng.uniform(0.2, 0.9), 2) if pays else None,
        "dgrowth": round(rng.uniform(-0.02, 0.1), 3) if pays else None,
        "dyears": rng.randint(0, 12) if pays else 0,
        "years": [dt.date.today().year - 4 + k for k in range(4)],
        "rev": rev, "ni": ni,
        "hist": {"start": start.isoformat(), "c": c},
    })

out = {"meta": {"demo": True, "source": "Données fictives (tools/make_demo.py)",
                "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "bench": {"name": "Indice fictif", "start": start.isoformat(), "c": bench}},
       "stocks": stocks}
(ROOT / "docs/data").mkdir(parents=True, exist_ok=True)
with open(ROOT / "docs/data/stocks.json", "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
print(len(stocks), "valeurs fictives écrites")
