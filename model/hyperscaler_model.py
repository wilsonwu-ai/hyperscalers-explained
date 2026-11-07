"""Model for "Hyperscalers, explained": turns verified filings and anchored industry figures into chart data and a fact sheet.

Inputs (local files, every figure anchored):
  model/xbrl_quarterly.json           quarterly series from SEC XBRL company facts (made by model/xbrl_series.py)
  research/financials/<TICKER>.json   metrics extracted from 10-Q, 10-K and earnings releases; each quote was checked
                                      against the filing text (research/financials/reduce_filings.py)
  research/filings/manifest.json      filing URLs
  INDUSTRY (below)                    third-party figures with source, URL, date and how the number was checked
Outputs:
  model/site_data.json                everything the charts and diagrams draw
  brief/facts.md                      the fact sheet writers and checkers work from (local working file)

The 1 GW campus is an illustration, not a forecast. Every input is listed with its source or marked as an assumption.
Interim (10-Q and earnings release) figures are unaudited.

Run from the project folder:  python3 -I model/hyperscaler_model.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIN = ROOT / "research" / "financials"
XBRL = json.loads((ROOT / "model" / "xbrl_quarterly.json").read_text())
MANIFEST = json.loads((ROOT / "research" / "filings" / "manifest.json").read_text())["tickers"]
OUT = ROOT / "model" / "site_data.json"
FACTS = ROOT / "brief" / "facts.md"
AS_OF = "2026-11-07"

NAMES = {"AMZN": "Amazon", "MSFT": "Microsoft", "GOOGL": "Alphabet", "META": "Meta", "ORCL": "Oracle",
         "CRWV": "CoreWeave", "NBIS": "Nebius", "NVDA": "NVIDIA", "EQIX": "Equinix", "DLR": "Digital Realty",
         "VRT": "Vertiv"}
FISCAL = {"MSFT": "fiscal year ends June 30; FY27 Q1 = Jul to Sep 2026",
          "ORCL": "fiscal year ends May 31; FY27 Q1 = Jun to Aug 2026",
          "NVDA": "fiscal year ends late January; FY27 Q2 = May to Jul 2026"}

# ---------------------------------------------------------------------------------------------------------------
# Third-party figures. anchor: "page" = the number was found in the saved source page (research/web_raw/anchors.json);
# "filing" = an SEC filing; "gov" = government statistics table; "read" = read in full by a research agent but the
# page refused a second fetch; "news" = reported by the named publication (paraphrased, linked).
# ---------------------------------------------------------------------------------------------------------------
INDUSTRY = {
    "synergy_q3": {"value": 167.7, "unit": "$B", "label": "Worldwide cloud infrastructure services revenue, Q3 2026, up 55% year on year",
                   "source": "Synergy Research Group, Q3 2026 cloud market release", "date": "2026-10",
                   "url": "https://www.srgresearch.com/articles/cloud-market-growth-rate-surges-to-well-over-50-per-year-q3-2026", "anchor": "page"},
    "synergy_ttm": {"value": 558, "unit": "$B", "label": "Cloud infrastructure services revenue, trailing 12 months to Q3 2026",
                    "source": "Synergy Research Group", "date": "2026-10", "url": "same as synergy_q3", "anchor": "page"},
    "synergy_shares": {"value": {"Amazon": 26, "Microsoft": 19, "Google": 16}, "unit": "% share, Q3 2026",
                       "label": "Cloud infrastructure market shares, Q3 2026 (61% combined)", "source": "Synergy Research Group",
                       "date": "2026-10", "url": "same as synergy_q3", "anchor": "page"},
    "synergy_hyperscale_capacity": {"value": {"2025": 48, "2031": 67}, "unit": "% of worldwide data center capacity",
                                    "label": "Hyperscale operators' share of all data center capacity, 2025 and 2031 forecast",
                                    "source": "Synergy Research Group", "date": "2026",
                                    "url": "https://www.srgresearch.com/articles/hyperscale-operators-to-account-for-67-of-all-data-center-capacity-by-2031", "anchor": "page"},
    "delloro_2026": {"value": 1000, "unit": "$B", "label": "Worldwide data center capex in 2026, more than $1 trillion (June 2026 outlook)",
                     "source": "Dell'Oro Group, as summarised by IEEE ComSoc Technology Blog", "date": "2026-09-16",
                     "url": "https://techblog.comsoc.org/2026/09/16/delloro-data-center-capex-grew-92-in-2q-2026-caveats-galore/", "anchor": "page"},
    "delloro_2030": {"value": 3000, "unit": "$B", "label": "Worldwide data center capex expected to surpass $3 trillion by 2030",
                     "source": "Dell'Oro Group, as summarised by IEEE ComSoc Technology Blog", "date": "2026-09-16",
                     "url": "same as delloro_2026", "anchor": "page"},
    "mckinsey_2030": {"value": 6.7, "unit": "$T", "label": "Cumulative data center capital spending needed worldwide by 2030 ($5.2T of it for AI)",
                      "source": "McKinsey & Company, 'The cost of compute: A $7 trillion race to scale data centers'", "date": "2025-04-28",
                      "url": "https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-cost-of-compute-a-7-trillion-dollar-race-to-scale-data-centers", "anchor": "read"},
    "gpu_h100_od": {"value": 4.20, "unit": "$ per GPU-hour", "label": "Median on-demand list price, NVIDIA H100, 7 Oct 2026 (16 providers)",
                    "source": "Uvik GPU price index", "date": "2026-10-07", "url": "https://uvik.net/blog/gpu-price-index/", "anchor": "page"},
    "gpu_b200_od": {"value": 8.19, "unit": "$ per GPU-hour", "label": "Median on-demand list price, NVIDIA B200, 7 Oct 2026 (9 providers)",
                    "source": "Uvik GPU price index", "date": "2026-10-07", "url": "https://uvik.net/blog/gpu-price-index/", "anchor": "page"},
    "gpu_h100_1yr": {"value": 2.35, "unit": "$ per GPU-hour", "label": "SemiAnalysis H100 one-year contract index, March 2026 (from $1.70 in Oct 2025)",
                     "source": "SemiAnalysis index as cited by Uvik", "date": "2026-03", "url": "https://uvik.net/blog/gpu-price-index/", "anchor": "page"},
    "gb200_rack_price": {"value": 3.0, "unit": "$M per rack", "label": "Analyst estimates for one GB200 NVL72 rack (72 GPUs); NVIDIA does not publish a price",
                         "source": "fal.ai summary of analyst estimates", "date": "2026", "url": "https://fal.ai/learn/serverless/nvidia-gb200-price", "anchor": "page"},
    "gb200_rack_kw": {"value": 120, "unit": "kW per rack", "label": "Power draw of one GB200 NVL72 rack, about 120 kW",
                      "source": "fal.ai", "date": "2026", "url": "https://fal.ai/learn/serverless/nvidia-gb200-price", "anchor": "page"},
    "cw_cost_per_mw": {"value": 17.6, "unit": "$M per MW", "label": "Average all-in greenfield cost of new US and Canadian data centers, excluding chips and GPUs",
                       "source": "Cushman & Wakefield 2026 Data Center Development Cost Guide", "date": "2026-09",
                       "url": "https://finviz.com/news/388803/cushman-wakefield-releases-2026-data-center-development-cost-guide", "anchor": "page"},
    "jll_cost_per_mw": {"value": 11.3, "unit": "$M per MW", "label": "JLL global average data center construction cost forecast for 2026",
                        "source": "JLL 2026 Global Data Center Outlook", "date": "2026", "url": "https://www.jll.com/en-us/insights/market-outlook/data-center-outlook", "anchor": "read"},
    "huang_per_gw": {"value": "50 to 60", "unit": "$B per GW", "label": "Jensen Huang's reported estimate of the all-in cost of 1 GW of AI data center, about $35B of it NVIDIA systems",
                     "source": "Reported remarks (secondhand), 24/7 Wall St.", "date": "2026-09-24",
                     "url": "https://247wallst.com/investing/2026/09/24/nvidias-ceo-says-a-1-gigawatt-ai-factory-rents-for-50-billion/", "anchor": "news"},
    "pue_google": {"value": 1.09, "unit": "PUE", "label": "Google fleet-wide average power usage effectiveness, 2025",
                   "source": "Google data center efficiency page", "date": "2026", "url": "https://datacenters.google/efficiency/", "anchor": "page"},
    "pue_industry": {"value": 1.54, "unit": "PUE", "label": "Industry average PUE (Uptime Institute survey), as cited by Google",
                     "source": "Uptime Institute via Google", "date": "2026", "url": "https://datacenters.google/efficiency/", "anchor": "page"},
    "eia_industrial": {"value": 9.64, "unit": "cents per kWh", "label": "US average retail electricity price, industrial customers, August 2026 (8.98 a year earlier; preliminary)",
                       "source": "US Energy Information Administration, Electric Power Monthly Table 5.6.A", "date": "2026-10",
                       "url": "https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a", "anchor": "gov"},
    "pjm_cap": {"value": 333.44, "unit": "$ per MW-day", "label": "PJM capacity auction price for 2027/28, at the price cap for a third straight auction",
                "source": "Utility Dive", "date": "2025-12-18",
                "url": "https://www.utilitydive.com/news/pjm-interconnection-capacity-auction-data-center/808264/", "anchor": "read"},
    "tsmc_margins": {"value": {"gross": 66.4, "operating": 58.7}, "unit": "% of revenue, Q3 2026", "label": "TSMC gross and operating margin, Q3 2026",
                     "source": "TSMC Q3 2026 management report (SEC Form 6-K)", "date": "2026-10",
                     "url": "https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000726/", "anchor": "filing"},
    "gev_backlog": {"value": 116, "unit": "GW", "label": "GE Vernova gas power equipment backlog plus slot reservations, Q2 2026 (up from 100 GW)",
                    "source": "GE Vernova Q2 2026 Form 8-K", "date": "2026-07",
                    "url": "https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000147/gev2q2026form8-k.pdf", "anchor": "filing"},
    "hyperion_jv": {"value": 27, "unit": "$B", "label": "Meta and Blue Owl joint venture for the Hyperion campus in Louisiana: about $27B, Blue Owl funds 80%, Meta 20%",
                    "source": "Hubbis (Meta and Blue Owl announcement coverage)", "date": "2025-10-21",
                    "url": "https://www.hubbis.com/news/meta-and-blue-owl-capital-launch-usd27-billion-joint-venture-for-hyperion", "anchor": "page"},
    "aws_savings_plans": {"value": 72, "unit": "% maximum discount", "label": "AWS Savings Plans: a one- or three-year spending commitment for discounts of up to 72% versus on-demand prices",
                          "source": "AWS Savings Plans pricing page", "date": "2026", "url": "https://aws.amazon.com/savingsplans/compute-pricing/", "anchor": "read"},
    "aws_spot": {"value": 90, "unit": "% maximum discount", "label": "AWS Spot: spare capacity at up to 90% off on-demand prices, which AWS can take back at short notice",
                 "source": "AWS EC2 Spot pricing page", "date": "2026", "url": "https://aws.amazon.com/ec2/spot/pricing/", "anchor": "read"},
    "bedrock_tokens": {"value": "0.50 / 1.50", "unit": "$ per 1M input / output tokens", "label": "Example of per-token AI pricing on Amazon Bedrock (Mistral Large 3, on demand)",
                       "source": "Amazon Bedrock pricing page", "date": "2026", "url": "https://aws.amazon.com/bedrock/pricing/", "anchor": "read"},
}

IBIS = {  # IBISWorld US industry reports, 2026, from the 6 Nov 2026 screen of 31 industries. Headline figures only.
    "source": "IBISWorld US industry reports, 2026 (screen of 31 industries, 6 November 2026)",
    "hyperscale_margin": 29.9, "hyperscale_cagr_10y_real": 25.1, "hyperscale_rev_start_b": 29.0, "hyperscale_rev_now_b": 271.6,
    "hyperscale_forecast_cagr": 12.2,
    "buckets": [
        {"id": "profitable", "title": "Most profitable", "items": [
            {"name": "Hyperscale data centers", "stat": "29.9% margin", "hot": True},
            {"name": "Occupational health and safety", "stat": "26.7%"}, {"name": "Security software", "stat": "24.9%"},
            {"name": "Insurance brokers", "stat": "20.6%"}]},
        {"id": "growing", "title": "Fastest growing", "items": [
            {"name": "Hyperscale data centers", "stat": "25.1% a year", "hot": True},
            {"name": "3D printing services", "stat": "18.3%"}, {"name": "Security software", "stat": "14.3%"}]},
        {"id": "steady", "title": "Steadiest", "items": [
            {"name": "Janitorial services", "stat": "no down year since 2012"}, {"name": "IT consulting", "stat": ""},
            {"name": "Insurance brokers", "stat": ""}]},
        {"id": "declining", "title": "Declining", "items": [
            {"name": "Directory publishing", "stat": "12% of its 2007 peak"}, {"name": "Newsprint", "stat": "16% of its 2008 peak"},
            {"name": "Printing", "stat": "53% of its 2007 peak"}]},
    ],
    "note": "Growth is after inflation over 10 years. Margins are the reports' profit margins, not IBISWorld's public list figure.",
}

NEWS = [  # paraphrased; every item links to the original
    {"pub": "Financial Times", "date": "2026-11-07", "headline": "How Wall Street's all-in bet on AI blew up",
     "url": "https://www.ft.com/content/5a6806f0-e82e-4b34-b761-f9877e2b511c", "via": None,
     "point": "Put the 5 November sell-off at $3.2T without naming the index or data provider; hedge funds unwound leveraged tech positions and retail investors sold single stocks."},
    {"pub": "Financial Times", "date": "2026-11-02", "headline": "Unpicking Microsoft's free cash flow",
     "url": "https://www.ft.com/content/f16babea-fd38-440b-8278-5871d3a47b17", "via": None,
     "point": "An analyst argues that much of Microsoft's free cash flow comes from financing choices such as stock pay, leases and deferred payables rather than core profit."},
    {"pub": "The Wall Street Journal", "date": "2026-11-06", "headline": "The Wild Week That Brought AI Investors to the Brink",
     "url": "https://www.wsj.com/finance/stocks/midterms-markets-week-ai-trade-97b3fc5d", "via": None,
     "point": "After the 3 November midterms, the Nasdaq Composite entered correction territory on 5 November; that day's sell-off erased about $2.5T of Nasdaq market value."},
    {"pub": "The Wall Street Journal", "date": "2026-11-05", "headline": "AI Companies Scramble to Navigate a World Hostile to Data Centers",
     "url": "https://www.wsj.com/tech/ai/ai-companies-scramble-to-navigate-a-world-hostile-to-data-centers-c6023a14", "via": None,
     "point": "Anthropic's S-1 details about $895.4B of computing and infrastructure commitments through 2045 and flags local moratoriums as a risk; OpenAI is weighing whether to reset next year's capacity plans."},
    {"pub": "The New York Times", "date": "2026-10-29", "headline": "Big Tech's Data Center Blitz Is Burning Through Cash and Scaring Wall St.",
     "url": "https://www.nytimes.com/2026/10/29/technology/big-tech-data-center-spending.html", "via": "https://www.proquest.com/docview/3406427287",
     "point": "Amazon, Microsoft, Google and Meta are on track to spend more than $720B this year on data centers and other capital projects, about triple two years earlier."},
    {"pub": "The New York Times", "date": "2026-11-02", "headline": "Cracks in the A.I. Borrowing Binge (DealBook)",
     "url": "https://www.nytimes.com/2026/11/02/business/dealbook/ai-borrowing.html", "via": "https://www.proquest.com/docview/3407500605",
     "point": "S&P Global Ratings cut Meta's credit outlook; Goldman Sachs expects $420B of tech debt issuance next year; the Nasdaq Composite fell 5.3% in October, its worst month since March 2025."},
    {"pub": "The New York Times", "date": "2026-11-06", "headline": "A target on industry as power balance shifts.",
     "url": "https://www.proquest.com/docview/3409700015", "via": "https://www.proquest.com/docview/3409700015",
     "point": "In 40 of 41 local ballot measures, voters chose to limit or block data center development."},
    {"pub": "The Economist", "date": "2026-10-18", "headline": "The AI industry's gigantic debts are making investors nervous",
     "url": "https://www.economist.com/", "via": "https://www.proquest.com/docview/3401849289",
     "point": "Alphabet, Amazon, Microsoft and Meta borrowed $214B in 2026 versus $83B in all of 2025; JPMorgan expects about $5.5T of capex through 2030, three quarters debt-funded."},
    {"pub": "The Economist", "date": "2026-07-28", "headline": "AI revenues are growing fast, but not fast enough",
     "url": "https://www.economist.com/", "via": "https://www.proquest.com/docview/3368998783",
     "point": "Current AI revenue estimates run $150B to $220B a year, against a rough $2.5T a year needed to cover the capex."},
    {"pub": "The Economist", "date": "2026-10-14", "headline": "The AI boom is threatened by an epidemic of unreliable numbers",
     "url": "https://www.economist.com/", "via": "https://www.proquest.com/docview/3399788681",
     "point": "Microsoft put its AI revenue run rate at $37B in April and Amazon at $25B in July; Goldman Sachs estimates about $1T of annual revenue is needed for 10% to 20% returns."},
    {"pub": "Financial Times", "date": "2026-11-03", "headline": "A chill wind in the AI credit market",
     "url": "https://www.ft.com/content/5f08f1fb-4948-4420-8fe4-3c8c8cc492ef", "via": None,
     "point": "Hyperscalers are paying higher coupons on new bonds, and default-swap prices for AI borrowers have risen."},
    {"pub": "Financial Times", "date": "2026-11-04", "headline": "Are we ready for an AI bust? (Martin Wolf)",
     "url": "https://www.ft.com/content/b954b99c-b71e-4334-9789-18e2b69de76d", "via": None,
     "point": "Forecast hyperscaler spending now exceeds operating cash flow, and financing is moving to developers, REITs and private credit."},
    {"pub": "The Wall Street Journal", "date": "2026-11-04", "headline": "The Election Day Revolt That Threatens America's AI Boom",
     "url": "https://www.wsj.com/tech/ai/the-election-day-revolt-that-threatens-americas-ai-boom-03a53b52", "via": None,
     "point": "Goldman Sachs puts AI investment at 1.9% of US GDP this year; Texas, Georgia and Ohio hold over 40% of planned capacity (Evercore ISI)."},
    {"pub": "The Wall Street Journal", "date": "2026-11-05", "headline": "How the Data Center Backlash Could Play Into the Hands of Big Tech",
     "url": "https://www.wsj.com/tech/ai/how-the-data-center-backlash-could-play-into-the-hands-of-big-tech-a37dfb29", "via": None,
     "point": "A slower build-out would ease costs and give existing powered data centers scarcity value, which favors the largest players."},
]


# ---------------------------------------------------------------------------------------------------------------
def num(v):
    """First number in a value string; parentheses or a leading minus mean negative."""
    m = re.search(r"(\()?\s*(-)?\$?\s*(\d[\d,]*(?:\.\d+)?)", str(v))
    if not m:
        return None
    x = float(m.group(3).replace(",", ""))
    return -x if (m.group(1) or m.group(2)) else x


def prior_of(m: dict):
    lab = re.search(r":\s*\$?\(?([\d,]+(?:\.\d+)?)\)?\)", m.get("label", ""))
    if lab:
        return float(lab.group(1).replace(",", ""))
    vs = re.search(r"vs\.?\s*\$?\(?([\d,]+(?:\.\d+)?)", str(m.get("value", "")))
    return float(vs.group(1).replace(",", "")) if vs else None


_FIN = {}


def fin(t: str) -> dict:
    if t not in _FIN:
        co = json.loads((FIN / f"{t}.json").read_text())
        _FIN[t] = {m["key"]: m for m in co["metrics"]}
    return _FIN[t]


def get(t: str, key: str, scale: float = 1.0, need: bool = True):
    m = fin(t).get(key)
    if m is None:
        if need:
            raise KeyError(f"{t}.{key} missing from research/financials/{t}.json")
        return None
    v = num(m["value"])
    return None if v is None else v * scale


def doc_url(t: str, kind: str):
    for d in MANIFEST.get(t, {}).get("docs", []):
        if d.get("kind") == kind:
            return d.get("url")
    return None


def quarters(t: str, metric: str):
    return [(q["end"], q["value"]) for q in XBRL.get(t, {}).get(metric, {}).get("quarters", [])]


def ttm(t: str, metric: str):
    from datetime import date
    q = quarters(t, metric)[-4:]
    if len(q) < 4:
        return None, None
    ends = [date.fromisoformat(e) for e, _ in q]
    if any(not (80 <= (b - a).days <= 100) for a, b in zip(ends, ends[1:])):
        return None, None
    return sum(v for _, v in q), q[-1][0]


def cal_label(end: str) -> str:
    y, mth = int(end[:4]), int(end[5:7])
    return f"Q{(mth - 1) // 3 + 1} {str(y)[2:]}"


def r1(x):
    return None if x is None else round(x, 1)


# ---------------------------------------------------------------------------------------------------------------
def capex_wave():
    tickers = ["AMZN", "MSFT", "GOOGL", "META", "ORCL", "CRWV"]
    by = {t: {cal_label(e): v / 1e9 for e, v in quarters(t, "capex") if e >= "2020-01-01"} for t in tickers}
    labels = sorted({lab for d in by.values() for lab in d}, key=lambda s: (int(s[3:]), int(s[1])))
    series = [{"ticker": t, "name": NAMES[t], "values": [r1(by[t].get(lab)) for lab in labels]} for t in tickers]
    big5_latest = sum(by[t].get(labels[-1], 0) for t in tickers[:5])
    big5_year_ago = sum(by[t].get(labels[-5], 0) for t in tickers[:5])
    return {"labels": labels, "series": series, "unit": "$B per quarter",
            "big5_latest": r1(big5_latest), "big5_year_ago": r1(big5_year_ago),
            "note": ("Cash purchases of property and equipment from SEC filings (XBRL), by calendar quarter of the period end. "
                     "Oracle's quarters end one month earlier (Aug, Nov, Feb, May). Microsoft and Meta also add assets "
                     "through finance leases, not shown. CoreWeave reports Q3 2026 after this page's date. Interim figures unaudited."),
            "source": "SEC EDGAR company facts (XBRL), 10-Q and 10-K filings"}


def annual_capex():
    out = {}
    for t in ["AMZN", "MSFT", "GOOGL", "META", "ORCL"]:
        years = {}
        for e, v in quarters(t, "capex"):
            y = int(e[:4])
            years.setdefault(y, []).append(v)
        out[t] = {str(y): r1(sum(vs) / 1e9) for y, vs in sorted(years.items()) if 2019 <= y <= 2026 and (len(vs) == 4 or y == 2026)}
    return out


def intensity():
    rows = []
    for t in ["AMZN", "MSFT", "GOOGL", "META", "ORCL", "CRWV"]:
        cap, end = ttm(t, "capex")
        rev, _ = ttm(t, "revenue")
        ocf, _ = ttm(t, "op_cash_flow")
        da, _ = ttm(t, "dep_amort")
        rows.append({"ticker": t, "name": NAMES[t], "ttm_end": end,
                     "capex_b": r1(cap / 1e9) if cap else None, "revenue_b": r1(rev / 1e9) if rev else None,
                     "ocf_b": r1(ocf / 1e9) if ocf else None, "da_b": r1(da / 1e9) if da else None,
                     "capex_to_revenue": round(cap / rev * 100) if cap and rev else None,
                     "capex_to_ocf": round(cap / ocf * 100) if cap and ocf and ocf > 0 else None,
                     "capex_to_da": round(cap / da, 1) if cap and da else None,
                     "fcf_b": r1((ocf - cap) / 1e9) if cap and ocf else None})
    return {"rows": rows, "note": "Trailing 12 months from SEC XBRL. Free cash flow here = operating cash flow minus cash capex; "
                                  "company definitions differ slightly. Interim figures unaudited."}


def cloud_units():
    U = [  # (label, ticker, rev, rev_prior, op, op_prior, period)
        ("AWS", "AMZN", "cloud_segment_revenue_q", "cloud_segment_revenue_q_prior", "cloud_segment_op_income_q", "cloud_segment_op_income_q_prior", "Q3 2026 (Jul to Sep)"),
        ("Google Cloud", "GOOGL", "cloud_segment_revenue_q", "cloud_segment_revenue_q_prior", "cloud_segment_op_income_q", "cloud_segment_op_income_q_prior", "Q3 2026 (Jul to Sep)"),
        ("Microsoft Azure", "MSFT", "azure_revenue_q", None, None, None, "FY27 Q1 (Jul to Sep 2026)"),
        ("Oracle cloud infrastructure", "ORCL", "cloud_infrastructure_revenue_q", "cloud_infrastructure_revenue_q_prior", None, None, "FY27 Q1 (Jun to Aug 2026)"),
        ("CoreWeave", "CRWV", "total_revenue_q", "total_revenue_q_prior", "company_op_income_q", None, "Q2 2026 (Apr to Jun)"),
        ("Nebius", "NBIS", "total_revenue_q", "total_revenue_q_prior", "company_op_income_q", None, "Q2 2026 (Apr to Jun)"),
    ]
    rows = []
    for name, t, rk, rpk, ok, opk, period in U:
        rev = get(t, rk)
        prior = get(t, rpk) if rpk else None
        if t == "MSFT":
            prior = prior_of(fin(t)[rk])  # Azure FY26 Q1 is in the label
        op = get(t, ok) if ok else None
        rows.append({"name": name, "ticker": t, "period": period, "revenue_m": rev, "revenue_prior_m": prior,
                     "growth_pct": round((rev / prior - 1) * 100) if prior else None,
                     "op_income_m": op, "op_margin_pct": round(op / rev * 100, 1) if op is not None else None,
                     "op_income_prior_m": get(t, opk) if opk else None,
                     "source_url": doc_url(t, "earnings") or doc_url(t, "quarterly")})
    return {"rows": rows, "note": "Microsoft and Oracle do not report operating income for Azure or cloud infrastructure. "
                                  "CoreWeave adjusted operating margin (non-GAAP) was 5%. Interim figures unaudited."}


def backlog():
    B = [("Microsoft", "MSFT", "rpo_total", 1.0, "total remaining performance obligation, Sep 30 2026"),
         ("Oracle", "ORCL", "rpo_total", 1.0, "remaining performance obligations, Aug 31 2026 ($455B a year earlier)"),
         ("Amazon", "AMZN", "rpo_total", 1.0, "performance obligations not yet recognized, mainly AWS, Sep 30 2026"),
         ("Alphabet", "GOOGL", "rpo_total", 1.0, "revenue backlog, Sep 30 2026 ($560.8B of it Google Cloud)"),
         ("CoreWeave", "CRWV", "rpo_total", 1.0, "remaining performance obligations, Jun 30 2026"),
         ("Nebius", "NBIS", "rpo_total", 0.001, "remaining performance obligations, Jun 30 2026")]
    rows = [{"name": n, "ticker": t, "rpo_b": r1(get(t, k) * s), "note": note,
             "source_url": doc_url(t, "quarterly")} for n, t, k, s, note in B]
    run_key = {"AMZN": "cloud_segment_revenue_q", "GOOGL": "cloud_segment_revenue_q"}  # their backlog is mostly cloud
    for r in rows:
        q = get(r["ticker"], run_key.get(r["ticker"], "total_revenue_q"))
        r["run_rate_b"] = r1(q * 4 / 1000)
        r["run_rate_basis"] = "AWS" if r["ticker"] == "AMZN" else "Google Cloud" if r["ticker"] == "GOOGL" else "company"
        r["years_of_revenue"] = round(r["rpo_b"] / (q * 4 / 1000), 1)
    big4 = sum(r["rpo_b"] for r in rows[:4])
    return {"rows": rows, "big4_total_b": r1(big4),
            "years_note": "Backlog divided by the latest quarter's revenue x 4 (AWS and Google Cloud revenue for Amazon and Alphabet; total company revenue for the others).",
            "note": "Signed contracts not yet delivered. Microsoft says about 30% lands in the next 12 months; Oracle 13%; "
                    "Alphabet just over 55% in 24 months. Interim figures unaudited."}


def chain():
    def m(t, op_key="company_op_income_q", rev_key="total_revenue_q"):
        return round(get(t, op_key) / get(t, rev_key) * 100, 1)
    aws = next(r for r in cloud_units()["rows"] if r["name"] == "AWS")
    gcp = next(r for r in cloud_units()["rows"] if r["name"] == "Google Cloud")
    rows = [
        {"name": "TSMC (makes the chips)", "layer": "chips", "op_margin": INDUSTRY["tsmc_margins"]["value"]["operating"], "period": "Q3 2026", "source": "TSMC 6-K"},
        {"name": "NVIDIA (designs GPUs and systems)", "layer": "chips", "op_margin": m("NVDA"), "period": "FY27 Q2 (May to Jul 2026)", "source": "NVIDIA 8-K"},
        {"name": "Vertiv (power and cooling gear)", "layer": "power", "op_margin": m("VRT"), "period": "Q3 2026", "source": "Vertiv 8-K"},
        {"name": "AWS (full-service cloud)", "layer": "compute", "op_margin": aws["op_margin_pct"], "period": "Q3 2026", "source": "Amazon 8-K"},
        {"name": "Google Cloud (full-service cloud)", "layer": "compute", "op_margin": gcp["op_margin_pct"], "period": "Q3 2026", "source": "Alphabet 8-K"},
        {"name": "Equinix (data center landlord)", "layer": "buildings", "op_margin": m("EQIX"), "period": "Q3 2026", "source": "Equinix 8-K"},
        {"name": "Digital Realty (data center landlord)", "layer": "buildings", "op_margin": m("DLR"), "period": "Q3 2026", "source": "Digital Realty 8-K"},
        {"name": "CoreWeave (GPU cloud)", "layer": "compute", "op_margin": m("CRWV"), "period": "Q2 2026", "source": "CoreWeave 8-K"},
        {"name": "Nebius (GPU cloud)", "layer": "compute", "op_margin": m("NBIS"), "period": "Q2 2026", "source": "Nebius 6-K"},
    ]
    return {"rows": rows, "note": "GAAP operating income as a share of revenue, latest reported quarter. Interim figures unaudited.",
            "nvda_gross_margin": 75.0}


def lives():
    return {"rows": [
        {"name": "Alphabet", "years": "6", "low": 6, "high": 6},
        {"name": "Microsoft", "years": "2 to 6", "low": 2, "high": 6},
        {"name": "Oracle", "years": "6", "low": 6, "high": 6},
        {"name": "CoreWeave", "years": "6 (from 5 in 2023)", "low": 6, "high": 6},
        {"name": "Amazon", "years": "5 to 6 (some cut from 6 to 5)", "low": 5, "high": 6},
        {"name": "Meta", "years": "5.5 (from 2025)", "low": 5.5, "high": 5.5},
        {"name": "Nebius", "years": "5 (from 4 in 2026)", "low": 5, "high": 5}],
        "meta_2025_saving_b": get("META", "useful_life_change_depreciation_reduction"),
        "note": "Useful life policy for servers and network gear, from each company's latest 10-K or 10-Q."}


def debt():
    rows = []
    for t, key in [("AMZN", "long_term_debt"), ("GOOGL", "long_term_debt"), ("META", "long_term_debt"),
                   ("CRWV", "long_term_debt"), ("NBIS", "long_term_debt")]:  # Oracle left out: part of its debt moved to current
        m = fin(t)[key]
        now, before = num(m["value"]), prior_of(m)
        rows.append({"name": NAMES[t], "ticker": t, "now_b": r1(now / 1000), "before_b": r1(before / 1000) if before else None,
                     "label": m["label"]})
    return {"rows": rows, "note": "Long-term debt on the balance sheet, Dec 31 2025 versus latest quarter. Unaudited."}


# ---------------------------------------------------------------------------------------------------------------
# The 1 GW campus (illustrative)
# ---------------------------------------------------------------------------------------------------------------
def campus():
    it_mw = 1000.0
    pue = 1.2                     # assumption: between Google's fleet 1.09 and the industry's 1.54
    load = 0.80                   # assumption: average share of capacity drawing power over a year
    price_mwh = INDUSTRY["eia_industrial"]["value"] * 10   # cents/kWh -> $/MWh
    facility_per_mw = INDUSTRY["cw_cost_per_mw"]["value"]   # $M per MW, excludes chips
    it_per_mw = 35.0              # $M per MW: Huang's reported ~$35B of NVIDIA systems per GW
    racks = it_mw * 1000 / INDUSTRY["gb200_rack_kw"]["value"]
    gpus = racks * 72
    rack_capex_b = racks * INDUSTRY["gb200_rack_price"]["value"] / 1000
    life_it, life_fac = 6, 20     # 6 = Alphabet, Microsoft, Oracle, CoreWeave policy; 20 = assumption (blend of 15 to 40 year assets)
    opex_share = 0.12             # assumption: staff, maintenance, network, software and overhead, share of revenue

    crwv_ann = get("CRWV", "total_revenue_q") * 4 / 1000          # $B
    crwv_gw_end = get("CRWV", "active_power")                      # GW
    crwv_gw_avg = crwv_gw_end - 0.5 / 2                            # it added nearly 500 MW in the quarter
    realized = 3.50                                                # assumption, $/GPU-hour
    cases = {
        "low": {"label": "CoreWeave today (end-of-quarter power)", "revenue_b": crwv_ann / crwv_gw_end,
                "how": f"CoreWeave Q2 2026 revenue x 4 = ${crwv_ann:.1f}B, divided by {crwv_gw_end:.1f} GW of active power"},
        "base": {"label": "CoreWeave today (average power in quarter)", "revenue_b": crwv_ann / crwv_gw_avg,
                 "how": f"${crwv_ann:.1f}B divided by about {crwv_gw_avg:.2f} GW, the average active power during the quarter"},
        "high": {"label": "Busy, well-priced campus", "revenue_b": gpus * realized * 8760 * load / 1e9,
                 "how": f"{gpus:,.0f} GPUs x ${realized:.2f} per GPU-hour x 8,760 hours x {load:.0%} busy"},
    }
    capex_fac = it_mw * facility_per_mw / 1000
    capex_it = it_mw * it_per_mw / 1000
    capex = capex_fac + capex_it
    power_b = it_mw * pue * 8760 * load * price_mwh / 1e9
    fin_cases = {"hyperscaler": {"debt_share": 0.30, "rate": 0.05, "label": "Hyperscaler: mostly cash, investment-grade bonds"},
                 "neocloud": {"debt_share": 0.70, "rate": 0.10, "label": "Neocloud: mostly debt, high-yield rates"}}

    def pnl(rev, life=life_it, fin_case=None):
        dep = capex_it / life + capex_fac / life_fac
        opex = rev * opex_share
        ebitda = rev - power_b - opex
        ebit = ebitda - dep
        interest = capex * fin_cases[fin_case]["debt_share"] * fin_cases[fin_case]["rate"] if fin_case else 0.0
        return {"revenue": round(rev, 2), "power": round(power_b, 2), "opex": round(opex, 2), "ebitda": round(ebitda, 2),
                "depreciation": round(dep, 2), "ebit": round(ebit, 2), "interest": round(interest, 2),
                "pretax": round(ebit - interest, 2), "ebit_margin_pct": round(ebit / rev * 100, 1),
                "payback_years": round(capex / ebitda, 1) if ebitda > 0 else None}

    for c in cases.values():
        c["pnl"] = pnl(c["revenue_b"])
        c["pnl_neocloud"] = pnl(c["revenue_b"], fin_case="neocloud")
        c["pnl_hyperscaler"] = pnl(c["revenue_b"], fin_case="hyperscaler")
        c["revenue_b"] = round(c["revenue_b"], 2)
    life_sens = [{"years": y, "base_ebit": pnl(cases["base"]["revenue_b"], life=y)["ebit"],
                  "high_ebit": pnl(cases["high"]["revenue_b"], life=y)["ebit"],
                  "it_depreciation": round(capex_it / y, 2)} for y in (3, 4, 5, 6)]
    dep6 = capex_it / life_it + capex_fac / life_fac
    breakeven = (power_b + dep6) / (1 - opex_share)
    breakeven_neo = (power_b + dep6 + capex * 0.70 * 0.10) / (1 - opex_share)
    crwv_margin = round(get("CRWV", "company_op_income_q") / get("CRWV", "total_revenue_q") * 100, 1)
    inputs = [
        {"input": "IT capacity", "value": "1,000 MW (1 GW)", "source": "Definition used throughout"},
        {"input": "Building, power and cooling", "value": f"${facility_per_mw}M per MW = ${capex_fac:.1f}B", "source": "Cushman & Wakefield 2026 (excludes chips); JLL's global average is $11.3M"},
        {"input": "Chips, servers and network", "value": f"${it_per_mw:.0f}M per MW = ${capex_it:.1f}B", "source": "About $35B of NVIDIA systems per GW (Huang, as reported); racks alone: "
                                                                                                          f"{racks:,.0f} x $3M = ${rack_capex_b:.1f}B"},
        {"input": "Total capex", "value": f"${capex:.1f}B", "source": "Sum; Huang's reported all-in estimate is $50B to $60B per GW"},
        {"input": "GPUs", "value": f"{gpus:,.0f}", "source": "1 GW / 120 kW per 72-GPU rack (fal.ai)"},
        {"input": "PUE", "value": f"{pue}", "source": "Assumption between Google (1.09) and the industry average (1.54)"},
        {"input": "Busy share of the year", "value": f"{load:.0%}", "source": "Assumption"},
        {"input": "Electricity price", "value": f"${price_mwh:.1f} per MWh", "source": "EIA US industrial average, August 2026"},
        {"input": "Useful life", "value": f"{life_it} years for IT, {life_fac} for the building", "source": "Hyperscaler policy (IT); assumption (building)"},
        {"input": "Running costs", "value": f"{opex_share:.0%} of revenue", "source": "Assumption: staff, maintenance, network, software, overhead"},
        {"input": "Financing", "value": "30% debt at 5% (hyperscaler); 70% debt at 10% (neocloud)", "source": "Assumption; CoreWeave's bonds yielded 10% to 15% in 2026 (The Economist)"},
    ]
    params = {"it_mw": it_mw, "pue": pue, "load": load, "price_mwh": round(price_mwh, 1), "facility_per_mw_m": facility_per_mw,
              "it_per_mw_m": it_per_mw, "life_it": life_it, "life_fac": life_fac, "opex_share": opex_share,
              "realized_price": realized, "gpus_per_rack": 72, "rack_kw": INDUSTRY["gb200_rack_kw"]["value"]}
    return {"params": params, "capex_b": round(capex, 1), "capex_facility_b": round(capex_fac, 1), "capex_it_b": round(capex_it, 1),
            "rack_capex_b": round(rack_capex_b, 1), "racks": round(racks), "gpus": round(gpus), "power_b": round(power_b, 2),
            "energy_twh": round(it_mw * pue * 8760 * load / 1e6, 2), "price_mwh": round(price_mwh, 1),
            "cases": cases, "financing": fin_cases, "life_sensitivity": life_sens,
            "breakeven_revenue_b": round(breakeven, 2), "breakeven_revenue_neocloud_b": round(breakeven_neo, 2),
            "calibration": {"model_base_ebit_margin": cases["base"]["pnl"]["ebit_margin_pct"],
                            "coreweave_actual_op_margin": crwv_margin,
                            "aws_actual_op_margin": next(r for r in cloud_units()["rows"] if r["name"] == "AWS")["op_margin_pct"],
                            "model_high_ebit_margin": cases["high"]["pnl"]["ebit_margin_pct"]},
            "inputs": inputs,
            "note": "Illustration only, not a forecast. Year-one view, before taxes; interest on the full starting debt."}


def tam():
    ttm_b = INDUSTRY["synergy_ttm"]["value"]
    run = INDUSTRY["synergy_q3"]["value"] * 4
    parts = [("Microsoft AI run rate (April 2026)", 37.0, "The Economist, 14 Oct 2026"),
             ("Amazon AI run rate (July 2026)", 25.0, "The Economist, 14 Oct 2026"),
             ("Oracle cloud infrastructure, annualized", round(get("ORCL", "cloud_infrastructure_revenue_q") * 4 / 1000, 1), "Oracle FY27 Q1 release"),
             ("CoreWeave, annualized", round(get("CRWV", "total_revenue_q") * 4 / 1000, 1), "CoreWeave Q2 2026 release"),
             ("Nebius annualized run rate", get("NBIS", "arr"), "Nebius Q2 2026 release")]
    sam = sum(p[1] for p in parts)
    crwv_ann = get("CRWV", "total_revenue_q") * 4 / 1000
    return {"tam_b": ttm_b, "tam_run_rate_b": round(run, 1),
            "tam_label": "Worldwide cloud infrastructure services, last 12 months (Synergy Research)",
            "sam_b": round(sam, 1), "sam_parts": [{"name": n, "value_b": v, "source": s} for n, v, s in parts],
            "sam_label": "AI-heavy compute sold by the hour or by contract, a rough sum of company run rates that leaves out Google",
            "som_low_b": round(sam * 0.05, 1), "som_high_b": round(sam * 0.10, 1),
            "som_label": "What a well-funded new entrant could win in about five years: 5% to 10% of today's SAM",
            "som_check": f"CoreWeave's annualized revenue is ${crwv_ann:.1f}B on "
                         f"{get('CRWV', 'active_power'):.1f} GW of active power and ${get('CRWV', 'long_term_debt') / 1000:.1f}B of debt."}


def drivers():
    return {"crwv_active_gw": get("CRWV", "active_power"), "crwv_contracted_gw": get("CRWV", "contracted_power"),
            "h100_od": INDUSTRY["gpu_h100_od"]["value"], "b200_od": INDUSTRY["gpu_b200_od"]["value"],
            "h100_1yr": INDUSTRY["gpu_h100_1yr"]["value"], "synergy_growth_pct": 55,
            "msft_openai_rev_q_b": 10.0, "msft_rpo_12m_pct": get("MSFT", "rpo_next_12m_pct"),
            "crwv_top_customer_pct": get("CRWV", "largest_customer_share_q"),
            "note": "Microsoft's OpenAI revenue is from its 10-Q related-party note (FY27 Q1)."}


def growth_margin():
    rows = [r for r in cloud_units()["rows"] if r["op_margin_pct"] is not None and r["growth_pct"] is not None]
    pts = [{"name": r["name"], "growth_pct": r["growth_pct"], "op_margin_pct": r["op_margin_pct"], "kind": "cloud",
            "period": r["period"]} for r in rows]
    nv_rev, nv_prior = get("NVDA", "total_revenue_q"), prior_of(fin("NVDA")["total_revenue_q"])
    pts.append({"name": "NVIDIA (supplier)", "growth_pct": round((nv_rev / nv_prior - 1) * 100),
                "op_margin_pct": round(get("NVDA", "company_op_income_q") / nv_rev * 100, 1), "kind": "supplier",
                "period": "FY27 Q2 (May to Jul 2026)"})
    no_margin = [{"name": r["name"], "growth_pct": r["growth_pct"]} for r in cloud_units()["rows"] if r["op_margin_pct"] is None]
    return {"points": pts, "no_margin": no_margin,
            "note": "Revenue growth versus a year earlier and operating margin, latest quarter. Unaudited."}


FORCES = [
    {"force": "Rivalry", "level": 4, "why": "Three giants hold 61% and fight on AI capacity, price and chips; Oracle and neoclouds add supply."},
    {"force": "New entrants", "level": 3, "why": "GPU clouds can start fast with debt, but full-service cloud takes decades and hundreds of billions."},
    {"force": "Supplier power", "level": 5, "why": "NVIDIA keeps 75% gross margins; turbines and grid connections are scarce too."},
    {"force": "Buyer power", "level": 4, "why": "A few AI labs sign the largest contracts; CoreWeave's top customer is 36% of revenue."},
    {"force": "Substitutes", "level": 2, "why": "Own data centers, custom chips and smaller open models can replace some rented compute."},
]

SCENARIOS = [
    {"id": "utility", "name": "The new utility", "x": "AI revenue keeps pace", "y": "Long asset lives, cheap money",
     "what": "Backlog converts on time; capex stays high but earns its keep; margins near today's.",
     "watch": "Backlog turning into revenue on schedule; GPU rental prices holding"},
    {"id": "squeeze", "name": "The margin squeeze", "x": "AI revenue keeps pace", "y": "Short lives, costly money",
     "what": "Demand is real, but faster chip cycles and higher rates eat profit; cash-rich giants gain share.",
     "watch": "Useful-life cuts; bond spreads and default-swap prices"},
    {"id": "digestion", "name": "Digestion", "x": "AI revenue slows", "y": "Long asset lives, cheap money",
     "what": "Too much capacity for a while; prices fall, capex is cut, customers win, as with fiber after 2001.",
     "watch": "Capex guidance cuts; on-demand GPU prices falling"},
    {"id": "bust", "name": "The bust", "x": "AI revenue slows", "y": "Short lives, costly money",
     "what": "Write-downs and defaults among debt-funded builders; the giants survive on their other businesses.",
     "watch": "Neocloud refinancing; lease cancellations; impairment charges"},
]


# ---------------------------------------------------------------------------------------------------------------
def cross_check(wave: dict) -> list:
    """Two independent anchors must agree: XBRL quarterly capex vs the capex line read from the earnings release."""
    out = []
    for t in ["AMZN", "MSFT", "GOOGL", "META", "ORCL", "CRWV"]:
        x = quarters(t, "capex")[-1][1] / 1e6
        e = get(t, "capex_q")
        ok = abs(x - e) / e < 0.005
        out.append({"ticker": t, "xbrl_m": round(x), "release_m": e, "agree": ok})
    return out


def facts_md(d: dict) -> str:
    L = ["# Fact sheet (generated by model/hyperscaler_model.py; do not edit by hand)", "",
         f"As of {AS_OF}. Interim figures are unaudited. Fiscal calendars: " + "; ".join(f"{NAMES[k]} {v}" for k, v in FISCAL.items()) + ".", "",
         "## Company figures (SEC filings, each quote verified against the filing text)", ""]
    for t in ["AMZN", "MSFT", "GOOGL", "META", "ORCL", "CRWV", "NBIS", "NVDA", "EQIX", "DLR", "VRT"]:
        L.append(f"### {NAMES[t]} ({t})")
        L.append(f"Earnings release: {doc_url(t, 'earnings') or 'n/a'}  |  10-Q: {doc_url(t, 'quarterly') or 'n/a'}  |  annual: {doc_url(t, 'annual') or 'n/a'}")
        for k, m in fin(t).items():
            L.append(f"- {m['label']}: **{m['value']}** {m.get('unit') or ''} ({m.get('period')})")
        L.append("")
    L += ["## Industry figures", ""]
    for k, v in INDUSTRY.items():
        L.append(f"- `{k}`: {v['label']}: **{v['value']} {v['unit']}**. {v['source']}, {v['date']}. {v['url']} (checked: {v['anchor']})")
    L += ["", "## News (paraphrase only; at most one quote under 15 words per article)", ""]
    for n in NEWS:
        L.append(f"- {n['pub']}, {n['date']}, \"{n['headline']}\": {n['point']} {n['url']}" + (f" (read via {n['via']})" if n.get("via") else ""))
    c = d["campus"]
    L += ["", "## Model outputs (illustrative; label as such)", "",
          f"- 1 GW campus capex: ${c['capex_b']}B (building ${c['capex_facility_b']}B + IT ${c['capex_it_b']}B); {c['gpus']:,} GPUs in {c['racks']:,} racks",
          f"- Power: {c['energy_twh']} TWh a year, ${c['power_b']}B at ${c['price_mwh']}/MWh",
          f"- Breakeven revenue per GW-year: ${c['breakeven_revenue_b']}B before interest; ${c['breakeven_revenue_neocloud_b']}B for a neocloud after interest"]
    for name, cs in c["cases"].items():
        p = cs["pnl"]
        L.append(f"- Case {name} ({cs['label']}): revenue ${cs['revenue_b']}B ({cs['how']}); EBITDA ${p['ebitda']}B; depreciation ${p['depreciation']}B; "
                 f"operating profit ${p['ebit']}B ({p['ebit_margin_pct']}%); neocloud after interest ${cs['pnl_neocloud']['pretax']}B; payback {p['payback_years']} years")
    L.append(f"- Calibration: model base margin {c['calibration']['model_base_ebit_margin']}% vs CoreWeave actual {c['calibration']['coreweave_actual_op_margin']}%; "
             f"model high {c['calibration']['model_high_ebit_margin']}% vs AWS actual {c['calibration']['aws_actual_op_margin']}%")
    for r in c["life_sensitivity"]:
        L.append(f"- IT life {r['years']} years: IT depreciation ${r['it_depreciation']}B a year; operating profit base ${r['base_ebit']}B, high ${r['high_ebit']}B")
    t = d["tam"]
    L += [f"- TAM ${t['tam_b']}B ({t['tam_label']}); Q3 run rate ${t['tam_run_rate_b']}B",
          f"- SAM ${t['sam_b']}B ({t['sam_label']}): " + "; ".join(f"{p['name']} ${p['value_b']}B ({p['source']})" for p in t["sam_parts"]),
          f"- SOM ${t['som_low_b']}B to ${t['som_high_b']}B ({t['som_label']}). Check: {t['som_check']}"]
    L += ["", "## Derived tables", "", "Capex intensity (TTM): " + json.dumps(d["intensity"]["rows"]), "",
          "Cloud units: " + json.dumps(d["cloud_units"]["rows"]), "", "Backlog: " + json.dumps(d["backlog"]), "",
          "Value chain margins: " + json.dumps(d["chain"]["rows"]), "", "Debt: " + json.dumps(d["debt"]["rows"]), "",
          "Annual capex ($B, calendar years, 2026 = first nine months): " + json.dumps(d["annual_capex"]), ""]
    return "\n".join(L) + "\n"


def main() -> None:
    wave = capex_wave()
    d = {"as_of": AS_OF, "capex_wave": wave, "annual_capex": annual_capex(), "intensity": intensity(),
         "cloud_units": cloud_units(), "backlog": backlog(), "chain": chain(), "lives": lives(), "debt": debt(),
         "campus": campus(), "tam": tam(), "forces": FORCES, "scenarios": SCENARIOS, "industry": INDUSTRY,
         "news": NEWS, "cross_check": cross_check(wave), "fiscal": FISCAL, "ibis": IBIS,
         "drivers": drivers(), "growth_margin": growth_margin()}
    OUT.write_text(json.dumps(d, indent=1))
    FACTS.write_text(facts_md(d))
    # console summary
    print("cross-check XBRL vs release capex:", [(c["ticker"], c["agree"]) for c in d["cross_check"]])
    print("big-5 capex latest quarter $B:", wave["big5_latest"], "year ago:", wave["big5_year_ago"], "labels:", wave["labels"][0], "to", wave["labels"][-1])
    for r in d["intensity"]["rows"]:
        print(f"  {r['ticker']:5} TTM to {r['ttm_end']} capex {r['capex_b']} rev {r['revenue_b']} ocf {r['ocf_b']} da {r['da_b']} "
              f"capex/rev {r['capex_to_revenue']}% capex/ocf {r['capex_to_ocf']}% capex/da {r['capex_to_da']}x fcf {r['fcf_b']}")
    for r in d["cloud_units"]["rows"]:
        print(f"  {r['name']:28} rev {r['revenue_m']} prior {r['revenue_prior_m']} growth {r['growth_pct']}% op {r['op_income_m']} margin {r['op_margin_pct']}%")
    print("backlog big4 $B:", d["backlog"]["big4_total_b"], [(r["name"], r["rpo_b"]) for r in d["backlog"]["rows"]])
    print("chain:", [(r["name"].split(" (")[0], r["op_margin"]) for r in d["chain"]["rows"]])
    print("debt:", [(r["name"], r["before_b"], r["now_b"]) for r in d["debt"]["rows"]])
    print("annual capex:", d["annual_capex"])
    c = d["campus"]
    print(f"campus capex {c['capex_b']} (fac {c['capex_facility_b']} it {c['capex_it_b']} racks-only {c['rack_capex_b']}) gpus {c['gpus']} power {c['power_b']} "
          f"breakeven {c['breakeven_revenue_b']} / neocloud {c['breakeven_revenue_neocloud_b']}")
    for k, cs in c["cases"].items():
        print(f"  {k:5} rev {cs['revenue_b']} pnl {cs['pnl']} neo {cs['pnl_neocloud']['pretax']} hyper {cs['pnl_hyperscaler']['pretax']}")
    print("  calibration:", c["calibration"])
    print("  life:", c["life_sensitivity"])
    t = d["tam"]
    print("tam/sam/som:", t["tam_b"], t["tam_run_rate_b"], t["sam_b"], t["som_low_b"], t["som_high_b"])
    print("wrote", OUT.relative_to(ROOT), "and", FACTS.relative_to(ROOT), f"({FACTS.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
