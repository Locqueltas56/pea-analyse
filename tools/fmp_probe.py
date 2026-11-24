"""Test de couverture FMP : combien d'années renvoyées pour quelques valeurs européennes."""
import os, json, urllib.request, urllib.error
KEY = os.environ.get("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com/stable"
TESTS = ["AI.PA", "TTE.PA", "MC.PA", "SAP.DE", "NESN.SW", "ASML.AS"]
EPS = ["income-statement", "cash-flow-statement", "key-metrics", "ratios"]
out = {"key_set": bool(KEY), "results": {}}
def get(ep, sym):
    url = f"{BASE}/{ep}?symbol={sym}&limit=40&apikey={KEY}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200].replace(KEY, "***")
    except Exception as e:
        return 0, str(e).replace(KEY, "***")[:200]
for sym in TESTS:
    out["results"][sym] = {}
    for ep in EPS:
        st, d = get(ep, sym)
        if isinstance(d, list):
            yrs = sorted({str(x.get("fiscalYear") or x.get("calendarYear") or x.get("date", ""))[:4] for x in d})
            out["results"][sym][ep] = {"status": st, "n": len(d), "years": yrs}
        else:
            out["results"][sym][ep] = {"status": st, "msg": d}
os.makedirs("docs/data", exist_ok=True)
json.dump(out, open("docs/data/fmp_probe.json", "w"), indent=1, ensure_ascii=False)
print("done")
