# Hyperscalers, explained

How the companies that rent out the world's computing power make money, what the AI build-out costs, who pays for it, and what has to be true for it to pay off.

**Read it here:** https://wilsonwu-ai.github.io/hyperscalers-explained/

By Wilson Wu, an operator who studies AI engineering and screens small businesses to buy.

## The story in four parts

- **Situation.** I compared 31 US industries using IBISWorld's 2026 industry reports. Hyperscale data centers came first on both profit margin (29.9%) and growth (25.1% a year over 10 years, after inflation). A ranking cannot say how the business works or who carries the risk, so I studied it.
- **Task.** One question: will the AI build-out pay, and who carries the risk? I split it into five parts: revenue, costs, financing, competition and what happens next.
- **Action.** I read the latest SEC filings for 11 public companies and checked every figure I pulled against the filing text. I read the coverage in The Wall Street Journal, The New York Times, the Financial Times and The Economist, and the discussion on X, Hacker News and StockTwits. I also built a small model of a 1 GW AI campus.
- **Result.** The revenue is real, growing fast and, for the biggest players, backed by years of signed contracts. The bill is growing faster, and more of it now arrives as depreciation and interest. The winners would be the companies whose revenue per gigawatt stays ahead of both. The page ends with a one-page pitch: what the business is, why an investor should care, the capex it takes, the skills it needs, how competitive it is, and TAM, SAM and SOM.

The page is written for two readers at once. Every section has a box called "The simple version" for non-technical readers, and most have a deeper box for engineers and investors. There are 17 diagrams and charts, several of them interactive, and a narrated video of about one minute with captions.

## How the numbers were checked

- **Filings.** 339 figures were pulled from 10-Qs, 10-Ks and earnings releases, each with the line it came from. A script then looked for every quote in the filing text: 337 were on the exact line cited, 1 was elsewhere in the same filing, and 1 could not be found, so it was not used. The extracts are in `research/financials/`, with the check results in `verify_report.json`.
- **Capex.** Quarterly capital spending was checked two ways, against the SEC's XBRL data and against the earnings releases (`model/xbrl_series.py`).
- **Industry and market figures.** Each one links to its source, and each was checked against the saved source page where the site allowed it.
- **News.** Articles were read in full and are paraphrased, never copied. Each is listed in the page's Sources section.
- **The campus model.** It is an illustration, not a forecast. Its inputs are listed beside every result, and the code is in `model/hyperscaler_model.py`.

## What is in this repository

| Path | What it holds |
|---|---|
| `content/` | The copy, one markdown file per part |
| `templates/` | The page template and the 17 figure partials |
| `model/` | The data model, the SEC XBRL capex series and `site_data.json`, which feeds every chart |
| `research/financials/` | Figures extracted from the filings, with the verification report |
| `research/filings/` | The script that pulled the filings from SEC EDGAR, and its manifest |
| `docs/` | The built site that GitHub Pages serves |
| `motion/` | Source for the narrated video (HyperFrames compositions, script and caption builder) |

## Rebuild the page

Python 3 and the `markdown` package are all the build needs.

```bash
pip install markdown
python3 model/xbrl_series.py         # optional: refresh the SEC XBRL capex series
python3 model/hyperscaler_model.py   # filings and industry figures -> model/site_data.json
python3 build.py                     # copy, figures and data -> docs/index.html
python3 -m http.server --directory docs 8000
```

The charts use D3 and GSAP from cdnjs. Each chart drawn in JavaScript has a data table behind it, so its numbers can still be read if the script fails to load.

## Sources

The full list, with links, is at the bottom of the page: SEC filings for Amazon, Microsoft, Alphabet, Meta, Oracle, CoreWeave, Nebius, NVIDIA, Equinix, Digital Realty and Vertiv; Synergy Research Group, Dell'Oro Group, Cushman & Wakefield, JLL, the US Energy Information Administration and others for industry figures; IBISWorld for the industry screen (headline figures only); and the newspapers above.

Educational only. Not investment advice. Figures come from public filings and the sources listed, as of 7 November 2026; quarterly figures are unaudited.
