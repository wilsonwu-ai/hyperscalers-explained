"""Build the GitHub Pages site in docs/ from the markdown copy, the figure partials and the model.

    python3 -I model/xbrl_series.py         # SEC XBRL -> model/xbrl_quarterly.json
    python3 -I model/hyperscaler_model.py   # filings + industry figures -> model/site_data.json
    python3 build.py                        # site_data -> docs/assets/data.js; copy + figures + template -> docs/index.html
    python3 build.py --draft                # same, but a missing figure becomes a visible placeholder instead of an error

Copy: content/00-intro.md ... 05-glossary.md, joined in order. Each section is a level-2 heading "## Title {#id}" and lands
in the template's <!-- COPY:id --> placeholder; text before the first section is the intro. The sources section is
generated from model/site_data.json and research/filings/manifest.json.
Figures: a line "<!-- FIG:fig-name -->" in the copy (or the template) is replaced by templates/figures/fig-name.html.
Numbers inside figures: any leaf element with data-k="path" data-f="format" gets its text from site_data at build time
(same formats as docs/assets/js/core.js). "<!-- TABLE:name -->" inside a figure becomes a fallback data table.
"""
import json
import math
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
FIGS = TEMPLATES / "figures"
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"
ORDER = ["00-intro.md", "01-situation.md", "02-task-action.md", "03-result.md", "04-conclusion.md", "05-glossary.md"]
DRAFT = "--draft" in sys.argv

SECTION_RE = re.compile(r"^## (.+?)\s*\{#([a-z0-9-]+)\}\s*$", re.M)
PLACEHOLDER_RE = re.compile(r"<!-- COPY:([a-z0-9-]+) -->")
FIG_RE = re.compile(r"(?:<p>\s*)?<!-- FIG:([a-z0-9-]+) -->(?:\s*</p>)?")
TABLE_RE = re.compile(r"<!-- TABLE:([a-z0-9-]+) -->")
HOOK_RE = re.compile(r"<(\w+)(\s[^<>]*?\bdata-k=\"[^\"]+\"[^<>]*)>([^<]*)</\1>")
BANNED_CHARS = {"\u2014": "em dash", "\u2013": "en dash"}
DISCLAIMER = ("Educational only. Not investment advice. Figures come from public filings and the sources listed, "
              "as of 7 November 2026; quarterly figures are unaudited.")

DATA = json.loads((ROOT / "model" / "site_data.json").read_text())


# ---------------------------------------------------------------- formats (must match core.js)
def fmt(v, f: str) -> str:
    if v is None:
        return ""
    if f == "raw" or not isinstance(v, (int, float)):
        return str(v)
    neg, a = v < 0, abs(float(v))
    s = {"b0": lambda: f"${a:,.0f}B", "b1": lambda: f"${a:,.1f}B", "b2": lambda: f"${a:,.2f}B",
         "t2": lambda: f"${a / 1000:,.2f}T", "m0": lambda: f"${a:,.0f}M", "p0": lambda: f"{math.floor(a + 0.5)}%",
         "p1": lambda: f"{a:.1f}%", "x1": lambda: f"{a:.1f}x", "n0": lambda: f"{a:,.0f}", "n2": lambda: f"{a:,.2f}",
         "y1": lambda: f"{a:.1f} years"}.get(f)
    if s is None:
        sys.exit(f"build: unknown data-f format '{f}'")
    return ("-" if neg else "") + s()


def get(path: str):
    cur = DATA
    for p in re.findall(r"[^.\[\]]+|\[[^\]]+\]", path):
        if cur is None:
            return None
        if p.startswith("["):
            inner = p[1:-1]
            if "=" in inner:
                k, v = inner.split("=", 1)
                cur = next((o for o in cur if isinstance(o, dict) and str(o.get(k)) == v), None)
            else:
                cur = cur[int(inner)] if int(inner) < len(cur) else None
        else:
            cur = cur.get(p) if isinstance(cur, dict) else None
    return cur


def fill_hooks(html_text: str, where: str) -> str:
    def rep(m):
        tag, attrs = m.group(1), m.group(2)
        k = re.search(r'\bdata-k="([^"]+)"', attrs).group(1)
        fm = re.search(r'\bdata-f="([^"]+)"', attrs)
        v = get(k)
        if v is None:
            sys.exit(f"build: {where}: data-k=\"{k}\" not found in model/site_data.json")
        return f"<{tag}{attrs}>{fmt(v, fm.group(1) if fm else 'raw')}</{tag}>"
    return HOOK_RE.sub(rep, html_text)


# ---------------------------------------------------------------- fallback tables
def table(head: list, rows: list, caption: str = "") -> str:
    th = "".join(f"<th scope=\"col\">{h}</th>" for h in head)
    body = "".join("<tr>" + "".join((f"<th scope=\"row\">{c}</th>" if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r))
                   + "</tr>" for r in rows)
    cap = f"<caption class=\"sr-only\">{caption}</caption>" if caption else ""
    return f"<div class=\"table-wrap\"><table>{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"


def t_capex_wave():
    w = DATA["capex_wave"]
    labs = w["labels"][-5:]
    rows = [[s["name"]] + [fmt(v, "b1") if v is not None else "n/a" for v in s["values"][-5:]] for s in w["series"]]
    return table(["Company"] + labs, rows, "Quarterly capex, $ billions")


def t_intensity():
    rows = [[r["name"], fmt(r["capex_b"], "b1"), fmt(r["revenue_b"], "b1"), fmt(r["capex_to_revenue"], "p0"),
             fmt(r["capex_to_ocf"], "p0") if r["capex_to_ocf"] is not None else "n/a", fmt(r["fcf_b"], "b1")]
            for r in DATA["intensity"]["rows"]]
    return table(["Company", "Capex, 12 months", "Revenue, 12 months", "Capex / revenue", "Capex / operating cash",
                  "Free cash flow"], rows, "Capex intensity, trailing 12 months")


def t_campus():
    c = DATA["campus"]["cases"]
    keys = [("revenue", "Revenue"), ("power", "Electricity"), ("opex", "Running costs"), ("ebitda", "Cash profit (EBITDA)"),
            ("depreciation", "Depreciation"), ("ebit", "Operating profit")]
    rows = [[lab] + [fmt(c[k]["pnl"][key], "b2") for k in ("low", "base", "high")] for key, lab in keys]
    rows.append(["Interest (neocloud financing)"] + [fmt(c[k]["pnl_neocloud"]["interest"], "b2") for k in ("low", "base", "high")])
    rows.append(["Profit before tax (neocloud)"] + [fmt(c[k]["pnl_neocloud"]["pretax"], "b2") for k in ("low", "base", "high")])
    return table(["Per year, one 1 GW campus", "Low", "Base", "High"], rows, "Illustrative 1 GW campus, $ billions a year")


def t_debt():
    rows = [[r["name"], fmt(r["before_b"], "b1"), fmt(r["now_b"], "b1")] for r in DATA["debt"]["rows"]]
    return table(["Company", "Dec 31 2025", "Latest quarter"], rows, "Long-term debt, $ billions")


def t_backlog():
    rows = [[r["name"], fmt(r["rpo_b"], "b1"), fmt(r["run_rate_b"], "b1"), fmt(r["years_of_revenue"], "x1")]
            for r in DATA["backlog"]["rows"]]
    return table(["Company", "Backlog", "Revenue run rate", "Backlog / run rate"], rows, "Signed backlog, $ billions")


def t_depreciation():
    rows = [[f"{r['years']} years", fmt(r["it_depreciation"], "b2"), fmt(r["base_ebit"], "b2"), fmt(r["high_ebit"], "b2")]
            for r in DATA["campus"]["life_sensitivity"]]
    t1 = table(["Chip life", "Chip depreciation a year", "Operating profit, base", "Operating profit, high"], rows,
               "Useful life sensitivity, 1 GW campus, $ billions a year")
    t2 = table(["Company", "Server life policy"], [[r["name"], r["years"] + " years"] for r in DATA["lives"]["rows"]],
               "Server useful life by company")
    return t1 + t2


def t_chain():
    rows = [[r["name"], fmt(r["op_margin"], "p1"), r["period"]] for r in DATA["chain"]["rows"]]
    return table(["Company", "Operating margin", "Period"], rows, "Operating margin along the value chain")


def t_growth_margin():
    rows = [[p["name"], fmt(p["growth_pct"], "p0"), fmt(p["op_margin_pct"], "p1"), p["period"]] for p in DATA["growth_margin"]["points"]]
    rows += [[p["name"], fmt(p["growth_pct"], "p0"), "not reported", ""] for p in DATA["growth_margin"]["no_margin"]]
    return table(["Business", "Revenue growth", "Operating margin", "Period"], rows, "Growth versus operating margin")


TABLES = {"capex-wave": t_capex_wave, "intensity": t_intensity, "campus": t_campus, "debt": t_debt, "backlog": t_backlog,
          "depreciation": t_depreciation, "chain": t_chain, "growth-margin": t_growth_margin}


# ---------------------------------------------------------------- sources section (generated)
def sources_md() -> str:
    man = json.loads((ROOT / "research" / "filings" / "manifest.json").read_text())["tickers"]
    names = {"AMZN": "Amazon", "MSFT": "Microsoft", "GOOGL": "Alphabet", "META": "Meta", "ORCL": "Oracle", "CRWV": "CoreWeave",
             "NBIS": "Nebius", "NVDA": "NVIDIA", "EQIX": "Equinix", "DLR": "Digital Realty", "VRT": "Vertiv"}
    kinds = {"earnings": "earnings release", "quarterly": "quarterly report", "annual": "annual report"}
    L = ["## Sources {#sources}", "",
         "Every number on this page comes from one of the sources below. Company figures come from SEC filings; "
         "quarterly figures are unaudited. The 1 GW campus is an illustration built from these inputs, not a forecast. "
         "The model and the data behind every chart are in the [GitHub repository](https://github.com/wilsonwu-ai/hyperscalers-explained).", "",
         "### Company filings (SEC EDGAR)", ""]
    for t, n in names.items():
        docs = man.get(t, {}).get("docs", [])
        links = []
        for d in docs:
            k = d.get("kind")
            if k in kinds and d.get("url") and not any(kinds[k] in x for x in links):
                links.append(f"[{kinds[k]} ({d.get('form')}, filed {d.get('filed')})]({d['url']})")
        if links:
            L.append(f"- **{n}**: " + "; ".join(links))
    L += ["", "### Industry research and data", ""]
    seen = set()
    for v in DATA["industry"].values():
        url = v["url"]
        if url.startswith("same as") or url in seen:
            continue
        seen.add(url)
        L.append(f"- {v['source']} ({v['date']}): [{v['label']}]({url})")
    L.append(f"- {DATA['ibis']['source']}. Headline figures only.")
    L += ["", "### News", ""]
    for n in DATA["news"]:
        via = f" (read through a university library)" if n.get("via") and "proquest" in n["via"] else ""
        title = f"[{n['headline']}]({n['url']})" if n.get("url") else n["headline"]
        L.append(f"- {n['pub']}, \"{title}\", {n['date']}{via}.")
    L += ["", "### Social media and forums", "",
          "Themes were read from public posts on X, Hacker News threads and StockTwits message boards in the week after "
          "third-quarter earnings. Only public figures are named. Reddit could not be read directly and is not quoted.", ""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- build
def md_to_html(text: str) -> str:
    out = markdown.markdown(text, extensions=["tables", "attr_list", "md_in_html", "fenced_code"], output_format="html5")
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out).replace("</table>", "</table></div>")
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    return out


def check_text(name: str, text: str) -> None:
    for ch, label in BANNED_CHARS.items():
        if ch in text:
            line = text[: text.index(ch)].count("\n") + 1
            sys.exit(f"build: {name} line {line} contains an {label}")


def load_copy() -> str:
    parts = []
    for name in ORDER:
        p = CONTENT / name
        if not p.exists():
            if DRAFT:
                print(f"build: note: {name} missing (draft mode)")
                continue
            sys.exit(f"build: content/{name} is missing")
        text = p.read_text()
        check_text(f"content/{name}", text)
        parts.append(text)
    parts.append(sources_md())
    return "\n\n".join(parts)


def split_sections(text: str):
    matches = list(SECTION_RE.finditer(text))
    intro = text[: matches[0].start()] if matches else text
    sections = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        if m.group(2) in sections:
            sys.exit(f"build: section id '{m.group(2)}' appears twice")
        sections[m.group(2)] = f"## {m.group(1)}\n{text[m.end():end]}".strip() + "\n"
    return intro, sections


def insert_figures(html_text: str, used: list) -> str:
    def rep(m):
        fid = m.group(1)
        used.append(fid)
        p = FIGS / f"{fid}.html"
        if not p.exists():
            if DRAFT:
                return f'<figure class="fig" id="{fid}"><p class="fig-title">[{fid} pending]</p></figure>'
            sys.exit(f"build: figure partial templates/figures/{fid}.html is missing")
        part = p.read_text()
        check_text(f"templates/figures/{fid}.html", part)
        part = TABLE_RE.sub(lambda t: TABLES[t.group(1)]() if t.group(1) in TABLES else sys.exit(f"build: unknown TABLE:{t.group(1)}"), part)
        return fill_hooks(part, f"templates/figures/{fid}.html")
    return FIG_RE.sub(rep, html_text)


def main() -> None:
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    (DOCS / "assets" / "data.js").write_text("// Generated from model/site_data.json by build.py. Do not edit by hand.\n"
                                              "window.SITE_DATA = " + json.dumps(DATA, separators=(",", ":")) + ";\n")
    intro, sections = split_sections(load_copy())
    page = (TEMPLATES / "index.html").read_text()
    wanted = PLACEHOLDER_RE.findall(page)
    intro_md = re.sub(r"^# .*$", "", intro, flags=re.M).strip()
    sections["intro"] = intro_md
    missing = [k for k in wanted if k not in sections]
    extra = [k for k in sections if k not in wanted]
    if missing and not DRAFT:
        sys.exit(f"build: no copy for placeholder(s): {', '.join(missing)}")
    if extra:
        sys.exit(f"build: copy with no placeholder: {', '.join(extra)}")

    def fill(m):
        key = m.group(1)
        if key not in sections:
            return f"<p>[{key} pending]</p>"
        out = md_to_html(sections[key])
        return out.replace("<p>", '<p class="dek">', 1) if key == "intro" else out

    page = PLACEHOLDER_RE.sub(fill, page)
    page = page.replace("<!-- DISCLAIMER -->", DISCLAIMER)
    used = []
    page = insert_figures(page, used)
    dup = sorted({f for f in used if used.count(f) > 1})
    if dup:
        sys.exit(f"build: figure(s) placed more than once: {dup}")
    unused = sorted(p.stem for p in FIGS.glob("fig-*.html") if p.stem not in used) if FIGS.exists() else []
    if unused:
        print(f"build: note: figure partial(s) not placed: {unused}")
    check_text("docs/index.html", page)
    left = PLACEHOLDER_RE.findall(page) + FIG_RE.findall(page) + TABLE_RE.findall(page)
    if left and not DRAFT:
        sys.exit(f"build: docs/index.html still has placeholder(s): {left}")
    (DOCS / "index.html").write_text(page)
    (DOCS / ".nojekyll").write_text("")
    print(f"build: wrote docs/index.html ({len(page):,} bytes, {len(used)} figures), docs/assets/data.js"
          + (" [draft]" if DRAFT else ""))


if __name__ == "__main__":
    main()
