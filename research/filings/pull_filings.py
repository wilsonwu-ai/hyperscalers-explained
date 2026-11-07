"""Pull the raw SEC filings the hyperscaler article is anchored on.

For each ticker: the latest 10-Q (6-K for foreign filers), the latest 10-K (20-F), the latest earnings
release (8-K item 2.02, exhibit 99.1) and the XBRL company facts (all reported values, used for the
capex history). Saves raw HTML, a text version with table rows kept on one line, and manifest.json.

Run from the project folder:  python3 -I research/filings/pull_filings.py
No email is sent to SEC: a generic client name is used as the User-Agent.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
UA = "hyperscalers-explained research-reader/1.0"
TICKERS = ["AMZN", "MSFT", "GOOGL", "ORCL", "META", "CRWV", "NBIS", "EQIX", "DLR", "NVDA", "VRT"]
PAUSE = 0.2  # SEC fair-access limit is 10 requests per second


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            time.sleep(PAUSE)
            return data
        except Exception as e:  # noqa: BLE001 - report and retry
            if attempt == 2:
                raise RuntimeError(f"{url}: {e}") from e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(url)


def html_to_text(raw: bytes) -> str:
    soup = BeautifulSoup(raw, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(["ix:header"]):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display:\s*none", re.I)):
        t.decompose()
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            cells = [c for c in cells if c]
            if cells:
                row = " | ".join(cells)
                row = re.sub(r"\$ \| ", "$", row)
                row = re.sub(r" \| \)", ")", row)
                row = re.sub(r" \| %", "%", row)
                rows.append(row)
        table.replace_with(soup.new_string("\n" + "\n".join(rows) + "\n"))
    text = soup.get_text("\n")
    text = re.sub("[ \\t\\u00a0\\u200b]+", " ", text)  # spaces, tabs, no-break and zero-width spaces
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip() + "\n"


def latest(recent: dict, forms: tuple, item: str | None = None):
    for i, form in enumerate(recent["form"]):
        if form in forms and (item is None or item in (recent.get("items") or [""] * len(recent["form"]))[i]):
            return {k: recent[k][i] for k in ("form", "filingDate", "reportDate", "accessionNumber", "primaryDocument")}
    return None


def exhibit_991(cik: int, acc: str) -> str | None:
    acc_nd = acc.replace("-", "")
    idx = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nd}/{acc}-index.htm")
    soup = BeautifulSoup(idx, "lxml")
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 4 and tds[3].get_text(strip=True).upper().startswith("EX-99"):
            a = tds[2].find("a")
            if a and a.get("href", "").lower().endswith((".htm", ".html")):
                return "https://www.sec.gov" + a["href"].replace("/ix?doc=", "")
    return None


def save(ticker_dir: Path, name: str, url: str, raw: bytes) -> dict:
    (ticker_dir / f"{name}.htm").write_bytes(raw)
    text = html_to_text(raw)
    (ticker_dir / f"{name}.txt").write_text(text)
    return {"name": name, "url": url, "txt": str((ticker_dir / f"{name}.txt").relative_to(ROOT.parent.parent)),
            "lines": text.count("\n"), "bytes": len(raw)}


def main() -> int:
    tickers = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    cik_of = {v["ticker"]: int(v["cik_str"]) for v in tickers.values()}
    manifest, problems = {}, []
    for t in TICKERS:
        cik = cik_of.get(t)
        if not cik:
            problems.append(f"{t}: no CIK")
            continue
        d = ROOT / t
        d.mkdir(exist_ok=True)
        sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
        recent = sub["filings"]["recent"]
        entry = {"cik": cik, "name": sub.get("name"), "fiscal_year_end": sub.get("fiscalYearEnd"), "docs": []}
        picks = {
            "quarterly": latest(recent, ("10-Q",)) or latest(recent, ("6-K",)),
            "annual": latest(recent, ("10-K",)) or latest(recent, ("20-F",)),
            "earnings": latest(recent, ("8-K",), "2.02"),
        }
        for kind, f in picks.items():
            if not f:
                problems.append(f"{t}: no {kind} filing found")
                continue
            acc_nd = f["accessionNumber"].replace("-", "")
            try:
                if kind == "earnings":
                    url = exhibit_991(cik, f["accessionNumber"])
                    if not url:
                        problems.append(f"{t}: earnings 8-K {f['filingDate']} has no EX-99 htm")
                        continue
                else:
                    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nd}/{f['primaryDocument']}"
                rec = save(d, f"{kind}_{f['form'].replace('/', '')}_{f['filingDate']}", url, get(url))
                rec.update({"kind": kind, "form": f["form"], "filed": f["filingDate"], "period": f["reportDate"],
                            "accession": f["accessionNumber"]})
                entry["docs"].append(rec)
            except Exception as e:  # noqa: BLE001
                problems.append(f"{t} {kind}: {e}")
        try:
            facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
            (d / "companyfacts.json").write_bytes(facts)
            entry["companyfacts"] = {"path": str((d / "companyfacts.json").relative_to(ROOT.parent.parent)),
                                     "bytes": len(facts)}
        except Exception as e:  # noqa: BLE001
            problems.append(f"{t} companyfacts: {e}")
        manifest[t] = entry
        print(t, cik, " | ".join(f"{x['kind']}:{x['form']} {x['filed']} (period {x['period']}, {x['lines']} lines)"
                                 for x in entry["docs"]), flush=True)
    (ROOT / "manifest.json").write_text(json.dumps({"tickers": manifest, "problems": problems,
                                                    "user_agent": UA}, indent=1))
    print("problems:", problems or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
