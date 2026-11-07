"""Reduce the filings-extraction fleet output into per-company JSON and verify every anchor in code.

Each extracted metric carries file, line and a verbatim quote. The quote is checked against the text file on disk:
  exact  = quote is on the cited line
  near   = within 3 lines of the cited line
  moved  = elsewhere in the cited file (line number wrong)
  other  = in another file for the same ticker (file name wrong or redacted in transit)
  short  = quote under 12 characters and not on the cited line (too short to search safely)
  miss   = not found
Writes research/financials/<TICKER>.json and research/financials/verify_report.json, prints a summary.

Run from the project folder:  python3 -I research/financials/reduce_filings.py <workflow-output-file>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FILINGS = ROOT / "research" / "filings"
OUT = ROOT / "research" / "financials"
SENT = ["AMZN", "MSFT", "GOOGL", "ORCL", "META", "CRWV", "NBIS", "EQIX", "DLR", "NVDA", "VRT"]
SHOW = ["total_revenue_q", "cloud_segment_revenue_q", "cloud_segment_op_income_q", "company_op_income_q", "capex_q",
        "capex_guidance", "da_q", "rpo_total", "server_useful_life", "free_cash_flow_ttm", "long_term_debt"]


def norm(s: str) -> str:
    s = s.replace("&amp;", "&").replace("’", "'").replace("\u2014", "-").replace("\u2013", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


class Corpus:
    def __init__(self):
        self.cache = {}

    def lines(self, p: Path) -> list:
        if p not in self.cache:
            self.cache[p] = [norm(x) for x in p.read_text(errors="replace").split("\n")]
        return self.cache[p]


def verify(ticker: str, m: dict, c: Corpus):
    q = norm(str(m.get("quote", "")))
    line = m.get("line") if isinstance(m.get("line"), int) else None
    tdir = FILINGS / ticker
    files = sorted(tdir.glob("*.txt"))
    name = str(m.get("file") or "").split("/")[-1]
    cited = tdir / name if name and "REDACTED" not in name and (tdir / name).exists() else None
    rel = lambda p: str(p.relative_to(FILINGS))  # noqa: E731
    if not q:
        return "noquote", m.get("file"), line
    order = ([cited] if cited else []) + [p for p in files if p != cited]
    # 1) the cited line, then +-3 lines, in the cited file first, then in the other files (redacted names)
    for p in order:
        L = c.lines(p)
        if line and 1 <= line <= len(L) and q in L[line - 1]:
            return ("exact" if p == cited else "other"), rel(p), line
        if line:
            for d in (1, 2, 3):
                for ln in (line - d, line + d):
                    if 1 <= ln <= len(L) and q in L[ln - 1]:
                        return ("near" if p == cited else "other"), rel(p), ln
    if len(q) < 12:
        return "short", m.get("file"), line
    # 2) anywhere (long quotes only)
    for p in order:
        for i, x in enumerate(c.lines(p), 1):
            if q in x:
                return ("moved" if p == cited else "other"), rel(p), i
    # 3) multi-line quotes: join a sliding window of 4 lines
    for p in order:
        L = c.lines(p)
        for i in range(len(L)):
            if q in " ".join(L[i:i + 4]):
                return ("moved" if p == cited else "other"), rel(p), i + 1
    return "miss", m.get("file"), line


def main() -> int:
    raw = json.loads(Path(sys.argv[1]).read_text())
    d = raw.get("result", raw) if isinstance(raw, dict) else raw
    if isinstance(d, str):
        d = json.loads(d)
    comps = d.get("companies", [])
    OUT.mkdir(exist_ok=True)
    c = Corpus()
    report, got = {"tickers": {}, "misses": []}, []
    for co in comps:
        t = co.get("ticker", "?").upper()
        got.append(t)
        tally = {}
        for i, m in enumerate(co.get("metrics", [])):
            if "REDACTED" in str(m.get("key", "")):
                m["key"] = re.sub(r"[^a-z0-9]+", "_", str(m.get("label", f"metric_{i}")).lower()).strip("_")[:48]
            status, f, ln = verify(t, m, c)
            m["verify"] = status
            if f:
                m["file"] = f if "/" in str(f) else f"{t}/{f}"
            if ln:
                m["line"] = ln
            tally[status] = tally.get(status, 0) + 1
            if status in ("miss", "short", "noquote"):
                report["misses"].append({"ticker": t, "key": m.get("key"), "status": status,
                                         "value": m.get("value"), "quote": str(m.get("quote"))[:90]})
        for dr in co.get("drivers", []):
            nm = str(dr.get("file") or "").split("/")[-1]
            if "REDACTED" in nm:
                dr["file"] = f"{t}/(redacted name, see verify of metrics)"
        # a metric whose quote could not be found in the filing is logged in verify_report.json and not published
        co["metrics"] = [m for m in co.get("metrics", []) if m.get("verify") not in ("miss", "short", "noquote")]
        (OUT / f"{t}.json").write_text(json.dumps(co, indent=1))
        report["tickers"][t] = {"metrics": len(co.get("metrics", [])), "drivers": len(co.get("drivers", [])),
                                "verify": tally, "gaps": co.get("gaps")}
    report["sent"], report["returned"] = SENT, got
    report["missing_tickers"] = [t for t in SENT if t not in got]
    # agent notes and lessons stay out of the published report
    (OUT / "verify_report.json").write_text(json.dumps(report, indent=1))

    print(f"returned {len(got)}/{len(SENT)} tickers; missing: {report['missing_tickers'] or 'none'}")
    tot = {}
    for t, r in report["tickers"].items():
        for k, v in r["verify"].items():
            tot[k] = tot.get(k, 0) + v
        print(f"{t:5} metrics={r['metrics']:3} drivers={r['drivers']:2} verify={r['verify']}")
    n = sum(tot.values())
    ok = tot.get("exact", 0) + tot.get("near", 0) + tot.get("other", 0) + tot.get("moved", 0)
    print(f"TOTAL {n} metrics: {tot} -> located {ok}/{n} = {ok / max(n, 1):.0%}")
    print("\nKEY METRICS (value | unit | period):")
    for co in comps:
        t = co["ticker"].upper()
        by = {m.get("key"): m for m in co.get("metrics", [])}
        for k in SHOW:
            if k in by:
                m = by[k]
                print(f"  {t:5} {k:26} {str(m.get('value'))[:38]:38} | {str(m.get('unit'))[:14]:14} | "
                      f"{str(m.get('period'))[:28]} [{m['verify']}]")
        other = [k for k in by if k not in SHOW]
        print(f"  {t:5} other keys: {', '.join(other)[:300]}")
    print("\nUNVERIFIED:", json.dumps(report["misses"])[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
