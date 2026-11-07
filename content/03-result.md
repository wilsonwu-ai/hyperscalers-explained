## Where the money comes from {#revenue}

Part 3 answers the five questions from the issue tree in order: revenue, costs, the build-out and who pays for it, who keeps the profit, and what happens next. Each section starts with its answer. Company figures come from each company's latest quarterly filing and are unaudited.

**The answer: the demand is real, much of it is signed years in advance, and a large part of it rests on a handful of AI labs.** For now, the companies' own numbers suggest the limit on revenue is how fast new capacity can be switched on, more than how many customers want it.

The market for renting computing power, which the industry calls cloud infrastructure services, brought in [$167.7B in the third quarter of 2026, up 55% on a year earlier](https://www.srgresearch.com/articles/cloud-market-growth-rate-surges-to-well-over-50-per-year-q3-2026), and $558B over the last 12 months, according to Synergy Research Group. Three companies, Amazon, Microsoft and Google, hold 61% of it.

| Cloud business, latest quarter | Revenue | Growth on a year earlier |
|---|---|---|
| [Amazon Web Services (AWS)](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000038/amzn-20260930xex991.htm), Jul to Sep | $46.0B | +39% |
| [Microsoft Azure](https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm), Jul to Sep | $33.2B | +48% |
| [Google Cloud](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm), Jul to Sep | $30.7B | +103% |
| [Oracle cloud infrastructure](https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/orcl-ex99_1.htm), Jun to Aug | $7.4B | +121% |
| [CoreWeave](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000362/coreweave2q26earningspress.htm), Apr to Jun | $2.6B | +112% |
| [Nebius](https://www.sec.gov/Archives/edgar/data/1513845/000110465926094568/tm2622968d1_ex99-1.htm), Apr to Jun | $0.6B | +454% |

What moves that revenue? A consultant would draw a driver tree: break the total into the few things that multiply together to make it.

<!-- FIG:fig-revenue-tree -->

1. **Capacity online.** How much computing power is switched on, measured in gigawatts (GW) of electricity it can draw. CoreWeave had 1.5 GW running at the end of June and 3.7 GW under contract. The gap is capacity still being built and connected, which is why, for now, supply more than demand sets the pace.
2. **How busy the chips are.** A chip that sits idle earns nothing. The giants spread many customers with different peaks across one fleet, which helps keep machines busy.
3. **Price per unit.** The median on-demand price for an NVIDIA H100, the workhorse AI chip, was [$4.20 an hour in October](https://uvik.net/blog/gpu-price-index/) across 16 providers, and $8.19 for the newer B200. Commit for a year and the H100 costs about $2.35 an hour, on a SemiAnalysis index for March 2026. That contract price had risen from $1.70 in October 2025, which suggests demand was outrunning supply even for older chips.
4. **Mix.** Raw chip time is the cheapest thing a cloud sells. Databases, storage, security and ready-made AI models sit on top of it and earn more from the same gigawatt. That is likely a big part of why the giants earn far higher margins than clouds that rent mainly GPUs.

The last branch of the tree is the one investors watch most: backlog, the value of signed contracts not yet delivered. Filings call it remaining performance obligations.

<!-- FIG:fig-backlog -->

The four largest backlogs add up to about $2.49T: [Microsoft $683B](https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm), [Oracle $664B](https://www.sec.gov/Archives/edgar/data/1341439/000119312526389274/orcl-20260831.htm), [Amazon $578B](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000040/amzn-20260930.htm) and [Alphabet $567.7B](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm). Divided by current yearly revenue (the whole company for Microsoft and Oracle; AWS and Google Cloud for Amazon and Alphabet, where nearly all their backlog sits), that is about 1.9 years at Microsoft, 3.1 at Amazon, 4.6 at Alphabet and 8.6 at Oracle. The GPU clouds stretch further: [CoreWeave's $103.7B](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm) is about ten years of its current revenue, and Nebius's $37.5B about 16. Timing matters too: Microsoft expects about 30% of its backlog to become revenue within 12 months, Oracle 13%, and Alphabet just over 55% within 24 months.

The catch is who signed. Microsoft recorded $10.0B of revenue from its commercial arrangements with OpenAI in a single quarter, according to a related-party note in its 10-Q. CoreWeave's largest customer was 36% of its revenue in the second quarter, and its largest a year earlier had been 71%. Anthropic, in the filing for its planned stock market listing, details about $895.4B of computing and infrastructure commitments through 2045, [The Wall Street Journal reports](https://www.wsj.com/tech/ai/ai-companies-scramble-to-navigate-a-world-hostile-to-data-centers-c6023a14). A backlog is only as strong as the customers behind it, and a large part of this one rests on a few AI labs.

<div class="simple" markdown="1">
**The simple version.** Picture a landlord who has signed tenants for an apartment tower that is still going up. The leases are real money, but the rent arrives only as each floor is finished, and two or three tenants have signed for a big share of the building.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: reading a backlog</summary>

- Remaining performance obligations are contracted revenue not yet recognized. Definitions differ: Amazon counts contracts longer than one year, mainly AWS, with a weighted-average remaining life of 6.1 years; Alphabet reports a revenue backlog, $560.8B of it Google Cloud; Microsoft's commercial backlog rose 73% in a year.
- "Years of revenue" here is backlog divided by the latest quarter's revenue times four. It measures visibility, not a forecast.
- Backlog becomes revenue only when capacity is delivered. That makes power, buildings and chip supply the main limit on near-term revenue, and it makes backlog quality (who the customer is, and whether it can pay) the real risk.

</details>

## Where the money goes {#costs}

**The answer: AI has changed the shape of the cost base.** A software company spends mostly on people. An AI cloud spends mostly on machines that wear out, so its biggest cost tends to be depreciation, the yearly write-down of chips, servers and buildings. Electricity is a smaller bill than most people expect, and one of the tightest constraints.

To make this concrete I built an illustrative model of one AI campus with 1 GW of computing load: about 600,000 of NVIDIA's newest GPUs in about 8,333 racks. It uses public inputs and it is a sketch, not a forecast. The code is in the repository linked at the bottom of the page.

<!-- FIG:fig-cost-stack -->

**The build costs about $52.6B.** The building, power and cooling systems come to $17.6B, using [Cushman & Wakefield's average of $17.6M per megawatt](https://finviz.com/news/388803/cushman-wakefield-releases-2026-data-center-development-cost-guide) for new US and Canadian data centers before chips. Chips, servers and networking add about $35B, in line with Jensen Huang's estimate, reported in September 2026, that about $35B of a gigawatt's cost goes to NVIDIA systems. The GPU racks alone come to about $25B at analyst estimates of [$3M per rack](https://fal.ai/learn/serverless/nvidia-gb200-price). Huang's reported all-in figure is [$50B to $60B per gigawatt](https://247wallst.com/investing/2026/09/24/nvidias-ceo-says-a-1-gigawatt-ai-factory-rents-for-50-billion/).

**The yearly bill:**

- Depreciation: about $6.7B a year, spreading the chips over six years ($5.8B) and the building over 20 ($0.9B).
- Electricity: about $0.8B a year. The campus uses about 8.4 terawatt-hours, priced at $96.40 per megawatt-hour, the [US average industrial price in August 2026](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a).
- Running costs (staff, maintenance, network, insurance): assumed at 12% of revenue, about $1.0B at today's GPU-cloud prices.

Depreciation is about eight times the power bill. Power is a bottleneck, not the biggest bill: the scarce thing is a grid connection, not the electricity that flows through it. Several signs point to scarcity. The capacity auction run by PJM, a grid operator in the eastern US, cleared at its [price cap for the third auction in a row](https://www.utilitydive.com/news/pjm-interconnection-capacity-auction-data-center/808264/) in December 2025, at $333.44 per megawatt-day for the 12 months from June 2027. GE Vernova's backlog and reserved production slots for gas turbines reached [116 GW at the end of June 2026](https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000147/gev2q2026form8-k.pdf). US industrial electricity cost 9.64 cents per kilowatt-hour in August, up from 8.98 a year earlier.

Efficiency is the engineer's lever. Google's fleet runs at a [power usage effectiveness (PUE) of 1.09](https://datacenters.google/efficiency/), against an industry average of 1.54, so less of each megawatt is lost to cooling and power conversion before it reaches a chip. The model assumes 1.2.

**The biggest lever is an accounting choice.** How fast a company depreciates its chips depends on their useful life, the number of years it expects them to earn their keep, and companies give different answers.

<!-- FIG:fig-depreciation -->

In the illustration, cutting the chips' useful life from six years to four adds about $2.9B of expense a year. At three years, even a busy, well-priced campus would lose money. Here is what the companies chose, from their latest annual or quarterly reports:

- Alphabet, Oracle and CoreWeave: six years (CoreWeave moved up from five in 2023).
- Amazon: five to six years. In 2025 it [shortened some servers from six years to five](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm) because AI technology moves faster, which added $1.4B of depreciation that year.
- Meta: 5.5 years from 2025, which [cut its 2025 depreciation by $2.92B](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm).
- Nebius: five years from 2026, up from four.
- Microsoft: two to six years.

Two camps argue about this online. One says the lives are too long and flatter profits. The other points to the rising one-year rental price of the older H100 as proof that old chips still earn their keep. Both read the same facts; the next two years of rental prices should help settle it.

More depreciation is likely on the way. Over the last 12 months these companies spent from 2.7 times (Amazon) to 8 times (Oracle) as much on new assets as they recorded in depreciation. As those assets go into service, the expense should keep climbing. In the latest quarter compared with a year earlier (unaudited), Microsoft's depreciation of property and equipment rose from $7.1B to $11.1B, Meta's depreciation and amortization from $5.0B to $7.2B, and Oracle's depreciation from $1.4B to $3.2B.

<div class="simple" markdown="1">
**The simple version.** Buy a delivery van for $60,000 that will be worn out in six years, and $10,000 of its value disappears every year, whether you drive it or not. Accountants call that depreciation. In the illustrative campus, the vans are the chips and the building, and their yearly wear costs about eight times the electricity that runs them.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: how the campus model works</summary>

- Energy: 1,000 MW of computing load x PUE 1.2 x 80% average load x 8,760 hours = 8.41 TWh a year. At $96.4 per MWh that is $0.81B.
- Depreciation: $35.0B of chips and servers over 6 years ($5.83B) plus $17.6B of building over 20 years ($0.88B) = $6.71B a year.
- GPUs: 1,000 MW divided by 120 kW per 72-GPU rack (an NVIDIA GB200 NVL72) = 8,333 racks, about 600,000 GPUs.
- Calibration: at CoreWeave's current revenue per gigawatt the model's operating margin (operating profit as a share of revenue) is -3.3%, against CoreWeave's reported -1.9%. In the busy case it is 36.9%, against AWS's reported 38.7%. Close enough to trust the shape, not the decimals.
- Limits: it is a year-one view before tax. It ignores construction time, price declines as chips age, and resale value. The code is `model/hyperscaler_model.py` in the repository.

</details>

## The build-out, and who pays for it {#capex}

**The answer: at most of these companies the AI build now costs more than their operations bring in, so the gap is being filled with debt, leases and other people's money.** Over the last 12 months Amazon, Oracle and CoreWeave each spent more on new assets than their operations brought in. In the latest quarter, so did Alphabet and Meta.

<!-- FIG:fig-capex-wave -->

Amazon, Microsoft, Alphabet, Meta and Oracle put $230.4B into property and equipment in their latest quarter (unaudited), more than double the $105.8B of a year earlier. Amazon alone spent $77.3B in three months. Amazon, Microsoft, Google and Meta are on track to spend more than $720B this year on data centers and other capital projects, about triple two years earlier, [The New York Times reports](https://www.nytimes.com/2026/10/29/technology/big-tech-data-center-spending.html). Worldwide, Dell'Oro Group expects data center capex to pass [$1T in 2026 and $3T a year by 2030](https://techblog.comsoc.org/2026/09/16/delloro-data-center-capex-grew-92-in-2q-2026-caveats-galore/).

<!-- FIG:fig-capex-intensity -->

Measured against revenue over the last 12 months, Oracle spent 105% of its revenue on capex, Meta 43%, Microsoft 39%, Alphabet 34% and Amazon 27%. CoreWeave spent 271%. Measured against the cash their operations generate, Amazon spent 128%, Oracle 161% and CoreWeave 298%.

Free cash flow is the cash left after paying for new assets. The latest figures, using each company's own definition where it has one:

- Amazon: -$42.4B over the last 12 months.
- Alphabet: operations brought in $42.3B in the third quarter and capex took $51.4B, a gap of about $9.1B.
- Meta: -$2.1B in the third quarter.
- Oracle: -$5.4B in its latest quarter.
- Microsoft, the exception: about +$18.6B in the quarter ($58.0B from operations less $39.4B of capex). Even there, an analyst quoted by the [Financial Times](https://www.ft.com/content/f16babea-fd38-440b-8278-5871d3a47b17) argues that much of that cash comes from financing choices such as leases, stock-based pay and slower payments to suppliers, rather than core profit.

**Does a campus pay for itself?** Try it. The chart below runs the illustrative 1 GW campus through a simple profit and loss. Pick a revenue case, a way to finance it and a chip life.

<!-- FIG:fig-campus -->

Three things stand out:

1. At CoreWeave's current revenue per gigawatt, about $8.2B a year, the campus would roughly break even before interest (an operating loss of about $0.3B) and would need 8.2 years of cash profit to pay back its cost. Breakeven before interest would be about $8.6B a year.
2. At $14.7B a year (600,000 GPUs rented at $3.50 an hour, busy 80% of the time) it would earn about 37%, close to AWS, and pay back in 4.3 years.
3. Financing decides who can ride out a slow year. Funded 70% with debt at 10%, interest would be about $3.7B a year, turning the base case from about -$0.3B into about -$4.0B and lifting breakeven to about $12.7B. Funded mostly with cash and cheap bonds (30% debt at 5%), interest would be about $0.8B.

**Where the money comes from now.** For most of these companies internal cash is no longer enough, so the build is moving onto borrowed money and other people's balance sheets.

<!-- FIG:fig-debt -->

- **Bonds.** Amazon's long-term debt went from $65.6B at the end of 2025 to $173.1B nine months later; it raised $115.1B of long-term debt in that time. Alphabet's went from $46.5B to $125.1B, and Meta's from $58.7B to $80.9B. The Economist ("The AI industry's gigantic debts are making investors nervous", 18 October 2026) reports that Alphabet, Amazon, Microsoft and Meta borrowed $214B in 2026, against $83B in all of 2025, and that JPMorgan expects about $5.5T of capex through 2030, three quarters of it funded with debt.
- **Expensive debt at the GPU clouds.** CoreWeave's recourse debt rose from $20.7B to $31.4B, and its quarterly interest expense of $640M was about 13 times its operating loss. Nebius roughly doubled its long-term debt to $8.5B and in October signed a $3.5B bridge loan with Citibank that matures in a year.
- **Leases that have not started.** Signed leases, mostly for data centers, that have not yet begun: Microsoft $364.6B, Meta $355.7B, Oracle $288B, Amazon $164.9B and Alphabet $130.5B. That is more than $1.3T together, none of it yet on the balance sheet.
- **Partners.** Meta's Hyperion campus in Louisiana sits in a [joint venture of about $27B](https://www.hubbis.com/news/meta-and-blue-owl-capital-launch-usd27-billion-joint-venture-for-hyperion), 80% funded by Blue Owl. Meta reports a [maximum exposure to loss of $68.4B](https://www.sec.gov/Archives/edgar/data/1326801/000162828026066773/meta-20260930.htm) across two such ventures, including $41.5B of guarantees on the value of the assets.
- **Customers and shareholders.** In a single quarter Oracle took in $11.4B of customer prepayments and raised $19.9B by selling new shares.

Markets noticed. S&P Global Ratings cut Meta's credit outlook, and the Nasdaq fell 5.3% in October, its worst month since March 2025 ([The New York Times](https://www.nytimes.com/2026/11/02/business/dealbook/ai-borrowing.html)). The [Financial Times](https://www.ft.com/content/5f08f1fb-4948-4420-8fe4-3c8c8cc492ef) reported higher interest rates on new hyperscaler bonds and rising prices for insurance against default. After the 3 November midterm elections the Nasdaq fell into a correction, and one day's sell-off on 5 November erased about $2.5T of Nasdaq market value ([The Wall Street Journal](https://www.wsj.com/finance/stocks/midterms-markets-week-ai-trade-97b3fc5d)). The [Financial Times](https://www.ft.com/content/5a6806f0-e82e-4b34-b761-f9877e2b511c) put that day's rout at $3.2T, without naming the index.

<div class="simple" markdown="1">
**The simple version.** A family that pays for a kitchen renovation from savings can pause the work if money gets tight. A family that borrowed for it owes the monthly payment no matter what. The cloud giants are mostly the first family. Many GPU clouds are the second.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: what the capex numbers include</summary>

- Capex here is cash purchases of property and equipment from each company's cash flow statement, read from SEC XBRL data and checked against the earnings releases. All six matched.
- It leaves out assets acquired through finance leases, which matter for Microsoft and Meta, and the leases not yet started listed above.
- Oracle's quarters end a month earlier (August, November, February, May). CoreWeave reports its third quarter after this page's date.
- Free cash flow definitions differ: Amazon nets out proceeds and incentives, Meta also subtracts finance lease principal, and Oracle subtracts capex as reported. Compare directions, not decimals.

</details>

## Who keeps the profit {#competition}

**The answer: the core of the market is an oligopoly with strong margins, and its edge is a commodity with thin ones.** The fattest margins in the AI build-out sit upstream, with the companies that make the chips.

<!-- FIG:fig-chain -->

Follow the money from chip to customer. The measure is operating margin, the share of revenue left after running costs and depreciation, for the latest quarter (unaudited):

- **Chips.** [NVIDIA](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm) kept 66.2% of its revenue as operating profit, with a gross margin of 75.0%. [TSMC](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000726/), which manufactures the chips, kept 58.7%.
- **Power and cooling equipment.** [Vertiv](https://www.sec.gov/Archives/edgar/data/1674101/000162828026067707/q32026exhibit991vrt10282026.htm) 22.8%.
- **Buildings.** [Equinix](https://www.sec.gov/Archives/edgar/data/1101239/000110123926000178/a991eqix-q326xpr.htm) 23.3% and [Digital Realty](https://www.sec.gov/Archives/edgar/data/1297996/000110465926120212/dlr-ex99d1.htm) 15.9%.
- **Full-service clouds.** AWS 38.7% and Google Cloud 36.2%.
- **GPU clouds.** CoreWeave -1.9% and Nebius -30.2%.

Fast growth does not buy margin. Nebius grew 454% and lost 30 cents on every dollar of revenue at the operating line. Google Cloud more than doubled and kept 36 cents.

<!-- FIG:fig-growth-margin -->

Porter's five forces, a standard way to judge how much profit an industry can keep, explains why:

<!-- FIG:fig-forces -->

- **Rivalry is high.** Three giants hold 61% and compete on AI capacity, price and chips, while Oracle and the neoclouds add supply.
- **Suppliers hold the most power.** NVIDIA keeps 75% gross margins and had [$279B of supply and capacity commitments](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm) at the end of July. Turbines and grid connections are scarce too, as the costs section showed.
- **Buyers are concentrated.** A few AI labs sign the biggest contracts and can play providers against each other.
- **Entry is split in two.** A GPU cloud can start quickly with borrowed money. A full-service cloud took the leaders about two decades and hundreds of billions of dollars to build.
- **Substitutes are modest.** Companies can build their own data centers, design their own chips or run smaller open models, but none of these replaces the cloud for most customers.

7 Powers, a framework for lasting advantage, adds the other half. The giants have scale economies (buying power and fleets kept busy by millions of customers), switching costs (once a company's data and applications live in one cloud, moving them is slow and expensive) and cornered resources: powered land, chip allocations and their own chips, such as Google's TPUs and Amazon's Trainium. The neoclouds win on counter-positioning, being faster and focused only on GPUs, an edge that could fade as the giants catch up.

So renting raw GPUs has so far been a thin-margin, capital-hungry business. The giants also sell the layers above it, which is the most likely reason their cloud margins are so much higher. [The Wall Street Journal](https://www.wsj.com/tech/ai/how-the-data-center-backlash-could-play-into-the-hands-of-big-tech-a37dfb29) makes a related point: a slower build-out would give existing powered data centers scarcity value, which favors the largest players.

<div class="simple" markdown="1">
**The simple version.** In a gold rush, the people selling shovels often do better than most miners. Here the shovel sellers are the chip makers. The big clouds are miners who also own the general store and the hotel, so they earn several ways. A GPU cloud is a miner with one claim and a large loan.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: how the forces were scored</summary>

Each force is scored from 1 (weak) to 5 (strong) on my judgment, using the filings: rivalry 4, new entrants 3, supplier power 5, buyer power 4, substitutes 2. Margins in the chain chart are company-wide operating margins for the latest reported quarter, except AWS and Google Cloud, which are segment figures. Microsoft and Oracle do not report a separate operating margin for Azure or Oracle cloud infrastructure, so they appear in the growth chart without one.

</details>

## What people are saying {#sentiment}

**The answer: the public conversation agrees on the facts and splits on what they mean.** Everyone sees record growth and record spending. The argument is about whether the revenue will arrive in time, and who holds the bill if it does not.

**The newspapers.** I read The Wall Street Journal, The New York Times, the Financial Times and The Economist in full. Four themes ran through them:

1. **Cash is being burned to build.** Writing in the [Financial Times](https://www.ft.com/content/b954b99c-b71e-4334-9789-18e2b69de76d), Martin Wolf notes that the largest hyperscalers' forecast spending now exceeds their operating cash flow, and that financing is moving to developers, property trusts, infrastructure funds and private credit, where risks are harder to see.
2. **Debt and credit stress**, covered in the build-out section above: record bond issuance, a cut to Meta's credit outlook and costlier insurance against default.
3. **The revenue gap.** The Economist ("AI revenues are growing fast, but not fast enough", 28 July 2026) puts today's AI revenue at $150B to $220B a year, against roughly $2.5T a year needed to cover the capex. Goldman Sachs estimates that about $1T of revenue a year would be needed for a 10% to 20% return, The Economist reported ("The AI boom is threatened by an epidemic of unreliable numbers", 14 October 2026).
4. **The backlash.** In the 3 November elections, voters chose to limit or block data centers in 40 of 41 local ballot measures (The New York Times, "A target on industry as power balance shifts", 6 November 2026, read through a university library). Texas, Georgia and Ohio hold more than 40% of planned US capacity, per Evercore ISI, and Goldman Sachs puts AI investment at 1.9% of US GDP this year ([The Wall Street Journal](https://www.wsj.com/tech/ai/the-election-day-revolt-that-threatens-americas-ai-boom-03a53b52)). OpenAI is weighing whether to reset next year's capacity plans, [the Journal reported](https://www.wsj.com/tech/ai/ai-companies-scramble-to-navigate-a-world-hostile-to-data-centers-c6023a14) on 5 November.

**X.** About 40 posts across seven searches, read but not engaged with. The loudest themes were spending versus revenue; a bullish reply that the sell-off misreads a boom in which demand still exceeds supply; a bubble story of debt, circular deals and falling stocks; backlog concentrated in OpenAI and Anthropic; Oracle as the most leveraged bet; and the fight over how long GPUs really last. Across posts about the group, stances split almost evenly: 6 bullish, 6 bearish and 9 mixed.

**Hacker News**, where engineers gather. The [most-discussed thread](https://news.ycombinator.com/item?id=47807619) compared the build to the railroads, and drew the reply that GPUs wear out in years while railways last generations. Another debated [circular financing](https://news.ycombinator.com/item?id=48873836), in which NVIDIA invests in GPU clouds that then buy NVIDIA chips. Others argued that cheap open-weight models could squeeze the AI labs, while the clouds collect rent whichever lab wins. The most-upvoted cloud threads were about trust rather than spending: price rises, billing errors and resilience.

**StockTwits**, where retail traders post. In a rough count of tagged messages on 7 November, bullish outnumbered bearish for Amazon (8 to 2), Alphabet (7 to 2) and Nebius (13 to 2), while Microsoft, Meta and CoreWeave were evenly split. Most messages carry no tag, so treat this as a temperature reading, not a poll.

**Reddit** blocked automated reading, so I have not quoted it.

What I take from it: the crowd is right that spending is outrunning cash, and right to worry about concentration. It is split on chip lives, as the filings are. And it seems to give too little weight to how much revenue is already contracted, which buys the giants time.

<div class="simple" markdown="1">
**The simple version.** It sounds like a crowded sports bar after a wild game: everyone agrees on the score, and nobody agrees on what it means for next season.
</div>

## What happens next {#future}

**The answer: whether the build-out pays comes down to two questions that nobody can answer yet.** Will AI revenue keep pace with the capacity being built? And will chips stay useful long enough, with money cheap enough, to earn back their cost? Crossing the two gives four futures.

<!-- FIG:fig-scenarios -->

- **The new utility** (revenue keeps pace; long lives and cheap money). Backlog would convert on time, capex would stay high but earn its keep, and margins would hold near today's.
- **The margin squeeze** (revenue keeps pace; short lives and costly money). Demand would be real, but faster chip cycles and higher rates would eat the profit. The cash-rich giants would likely gain share.
- **Digestion** (revenue slows; long lives and cheap money). There would be too much capacity for a while: prices would fall, capex would be cut and customers would win, as with fiber-optic networks after 2001.
- **The bust** (revenue slows; short lives and costly money). Write-downs and defaults would hit debt-funded builders. The giants would lean on their other businesses.

The gap to close is large. About $1T a year of revenue would earn a 10% to 20% return on this cycle, by Goldman Sachs's estimate, against $150B to $220B of AI revenue today (both via The Economist). My own rough estimate of AI-heavy computing sold today, built from company disclosures, is about $104.9B a year (see the one-pager below).

Signposts, in the order I would check them each quarter:

1. **Backlog turning into revenue on schedule.** Microsoft says about 30% of its $683B (unaudited) lands within 12 months. If revenue growth slows while backlog keeps growing, delivery is slipping.
2. **GPU rental prices.** On-demand H100s at $4.20 an hour and one-year contracts at $2.35 are today's markers. Falling prices would point to digestion.
3. **Useful-life changes.** A company that shortens its chip lives is saying chips age faster than planned, as Amazon did for some servers in 2025.
4. **Credit.** Bond spreads, default-swap prices and whether GPU clouds can refinance. Nebius's $3.5B bridge loan comes due in October 2027.
5. **Power and permits.** Local votes, grid auctions and turbine queues decide how fast capacity can come online.

My read: the three giants sit between the new utility and the margin squeeze, because their other businesses and their contracted backlog buy them time. The debt-funded GPU clouds sit between the squeeze and digestion, where a year of slower demand or higher rates would hurt most. The suppliers of chips, power and cooling earn the highest margins while the build runs. In digestion their orders would fall first, but their margins give them a cushion that leveraged builders lack.

What it means:

- **For investors:** on today's numbers, the toll collectors (chips, power and cooling) and the cash-rich giants look better placed than leveraged builders. Watch the signposts, not the headlines.
- **For operators and builders:** keeping the existing fleet powered, cooled and maintained is needed in every scenario. New construction would slow in digestion and largely stop in a bust.
- **For engineers:** efficiency per watt is the competitive lever: Google's PUE of 1.09 against an industry 1.54, custom chips, and software that keeps every GPU busy.

<div class="simple" markdown="1">
**The simple version.** Nobody knows which of the four boxes we will land in. A good list of things to watch is more useful than a confident forecast.
</div>
