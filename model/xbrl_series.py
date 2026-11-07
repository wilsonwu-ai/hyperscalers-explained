"""Quarterly series from SEC XBRL company facts (the anchor for the capex-wave chart and the model).

Reads research/filings/<TICKER>/companyfacts.json (downloaded by pull_filings.py) and writes
model/xbrl_quarterly.json and model/xbrl_quarterly.csv.

Cash-flow items are reported year-to-date in 10-Qs, so a quarter is derived by differencing
consecutive year-to-date values that share a start date (Q4 = full year minus nine months).
Every derived value records the two reported facts it came from (accession numbers).

Run from the project folder:  python3 -I model/xbrl_series.py
"""
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILINGS = ROOT / "research" / "filings"
OUT_JSON = ROOT / "model" / "xbrl_quarterly.json"
OUT_CSV = ROOT / "model" / "xbrl_quarterly.csv"

TICKERS = ["AMZN", "MSFT", "GOOGL", "META", "ORCL", "CRWV", "NVDA", "EQIX", "DLR", "VRT"]
CONCEPTS = {
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "finance_lease_principal": ["FinanceLeasePrincipalPayments"],
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "op_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "operating_income": ["OperatingIncomeLoss"],
    "dep_amort": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet",
                  "DepreciationAndAmortization", "Depreciation"],
}
FIRST_YEAR = 2019


def days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def best_concept(gaap: dict, names: list[str]):
    """Pick the candidate concept with the most recent reported value (companies switch tags over time)."""
    best = None
    for n in names:
        facts = gaap.get(n, {}).get("units", {}).get("USD", [])
        if not facts:
            continue
        last_end = max(f["end"] for f in facts)
        if best is None or last_end > best[1]:
            best = (n, last_end, facts)
    return best


def quarters_from_facts(facts: list[dict]) -> dict:
    """Return {end_date: {value, start, derived, sources}} for ~3-month periods."""
    # keep the latest-filed fact for each (start, end)
    by_span = {}
    for f in facts:
        if "start" not in f:
            continue
        k = (f["start"], f["end"])
        if k not in by_span or f["filed"] > by_span[k]["filed"]:
            by_span[k] = f
    q = {}
    for (s, e), f in by_span.items():
        if 80 <= days(s, e) <= 100:
            q[e] = {"value": f["val"], "start": s, "derived": False, "sources": [f["accn"]]}
    # derive quarters from year-to-date runs that share a start date
    runs = defaultdict(list)
    for (s, e), f in by_span.items():
        if days(s, e) >= 80:
            runs[s].append((e, f))
    for s, items in runs.items():
        items.sort()
        prev = None
        for e, f in items:
            span = days(s, e)
            if prev is not None and e not in q:
                pe, pf = prev
                gap = days(pe, e)
                if 80 <= gap <= 100:
                    q[e] = {"value": f["val"] - pf["val"], "start": pe, "derived": True,
                            "sources": [pf["accn"], f["accn"]]}
            if span <= 370:
                prev = (e, f)
    return q


def main() -> None:
    out, rows = {}, []
    for t in TICKERS:
        p = FILINGS / t / "companyfacts.json"
        if not p.exists():
            continue
        gaap = json.loads(p.read_text()).get("facts", {}).get("us-gaap", {})
        out[t] = {}
        for metric, names in CONCEPTS.items():
            pick = best_concept(gaap, names)
            if not pick:
                continue
            name, _, facts = pick
            q = quarters_from_facts(facts)
            series = [{"end": e, **v} for e, v in sorted(q.items()) if int(e[:4]) >= FIRST_YEAR]
            out[t][metric] = {"concept": name, "quarters": series}
            for s in series:
                rows.append([t, metric, name, s["end"], s["value"], s["derived"], " ".join(s["sources"])])
    OUT_JSON.write_text(json.dumps(out, indent=1))
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ticker", "metric", "concept", "quarter_end", "value_usd", "derived", "accessions"])
        w.writerows(rows)
    # compact console summary: latest four quarters of capex per ticker, in $ billions
    for t, m in out.items():
        cap = m.get("capex", {}).get("quarters", [])[-4:]
        rev = m.get("revenue", {}).get("quarters", [])[-1:]
        print(t, m.get("capex", {}).get("concept", "-"), "capex last 4q ($B):",
              [f"{c['end']}:{c['value'] / 1e9:.1f}" for c in cap],
              "| latest revenue q ($B):", [f"{r['end']}:{r['value'] / 1e9:.1f}" for r in rev])


if __name__ == "__main__":
    main()
