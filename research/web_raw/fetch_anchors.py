"""Anchor check for the industry numbers: fetch each cited source page once and look for its numbers in the page text.

Reads the findings chosen below from research/industry/r1_economics.json and r2_debates.json, fetches each source_url
(one request per page, human-scale), saves the page text to research/web_raw/<lane>_<id>.txt (local only, never
published) and checks every numeric token of the finding's "number" field against the text.
Status per finding: found (all tokens), partial, not_in_page, blocked (HTTP error or empty page).
Writes research/web_raw/anchors.json.

Run from the project folder:  python3 -I research/web_raw/fetch_anchors.py
"""
import json
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "research" / "web_raw"
PICK = {"r1": [0, 1, 3, 4, 5, 6, 13, 14, 15, 16, 17, 21, 22, 24],
        "r2": [8, 9, 10, 11, 12, 17, 19, 20, 21, 23]}
FILES = {"r1": ROOT / "research/industry/r1_economics.json", "r2": ROOT / "research/industry/r2_debates.json"}
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SEC_UA = "hyperscalers-explained research-reader/1.0"


def fetch(url: str) -> tuple[int, bytes, str]:
    ua = SEC_UA if "sec.gov" in url else BROWSER_UA
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity",
                                               "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, b"", ""
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode(), "error"


def to_text(raw: bytes, ctype: str) -> str:
    if "pdf" in ctype or raw[:4] == b"%PDF":
        try:
            import subprocess
            p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=raw, capture_output=True, timeout=60)
            return p.stdout.decode(errors="replace")
        except Exception:  # noqa: BLE001
            return ""
    soup = BeautifulSoup(raw, "lxml")
    for t in soup(["script", "style", "noscript", "svg"]):
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))


def tokens(number: str) -> list[str]:
    out = []
    for m in re.findall(r"\d[\d,]*(?:\.\d+)?", str(number)):
        m = m.rstrip(",")
        if len(m.replace(",", "").replace(".", "")) >= 2 or "." in m:
            out.append(m)
    return list(dict.fromkeys(out))


def present(tok: str, text: str) -> bool:
    plain = tok.replace(",", "")
    variants = {tok, plain}
    if "." in plain and plain.endswith("0"):
        variants.add(plain.rstrip("0").rstrip("."))
    if plain.isdigit() and len(plain) >= 4:
        variants.add(f"{int(plain):,}")
    return any(re.search(r"(?<![\d.])" + re.escape(v) + r"(?![\d])", text) for v in variants)


def main() -> None:
    results, seen = [], {}
    for lane, ids in PICK.items():
        d = json.loads(FILES[lane].read_text())
        d = d.get("result", d)
        fl = d["findings"]
        for i in ids:
            f = fl[i]
            url = f.get("source_url", "")
            if url in seen:
                status_code, text = seen[url]
            else:
                status_code, raw, ctype = fetch(url)
                text = to_text(raw, ctype) if raw and status_code == 200 else ""
                seen[url] = (status_code, text)
                time.sleep(0.6)
            path = OUT / f"{lane}_{i:02d}.txt"
            if text:
                path.write_text(text)
            toks = tokens(f.get("number", ""))
            hits = [t for t in toks if text and present(t, text)]
            if not text:
                status = "blocked"
            elif toks and len(hits) == len(toks):
                status = "found"
            elif hits:
                status = "partial"
            else:
                status = "not_in_page"
            results.append({"lane": lane, "id": i, "status": status, "http": status_code, "url": url,
                            "number": f.get("number"), "tokens": toks, "hits": hits,
                            "seen_as": f.get("seen_as"), "confidence": f.get("confidence"),
                            "chars": len(text), "claim": f.get("claim", "")[:160]})
            print(f"{lane}_{i:02d} {status:11} http={status_code} toks={toks} hits={hits} "
                  f"[{f.get('seen_as')}/{f.get('confidence')}] {url[:70]}")
    (OUT / "anchors.json").write_text(json.dumps(results, indent=1))
    tally = {}
    for r in results:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print("TALLY", tally)


if __name__ == "__main__":
    main()
