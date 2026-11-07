## The question, and how I answered it {#task}

The question: will the AI build-out pay, and who carries the risk? To keep from wandering, I split it with an issue tree, a way of breaking a big question into parts that do not overlap and together cover the whole. Five questions came out:

1. Demand and revenue drivers: is the demand real, and what moves revenue?
2. Costs and cost drivers: what does it cost to serve?
3. Financing: who pays for the build, and with what money?
4. Competition and who keeps the profit: where does the profit end up?
5. Scenarios and what has to be true: what must happen from here for the build-out to pay?

- **Filings.** I read the latest 10-Q (a company's quarterly report to the US regulator, the SEC), 10-K (its annual report) and earnings release for 11 public companies: Amazon, Microsoft, Alphabet, Meta, Oracle, CoreWeave, Nebius, NVIDIA, Equinix, Digital Realty and Vertiv. Amazon's [10-Q](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000040/amzn-20260930.htm) and [earnings release](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000038/amzn-20260930xex991.htm) show the style. Quarterly figures are unaudited: outside accountants have not signed off on them as they do for annual accounts.
- **Checks.** I checked every figure I pulled against the filing text. Of 339 quotes, 337 sat on the exact line I cited, one sat elsewhere in the same filing, and I did not use the one I could not find. Quarterly capex (money spent on buildings and chips that last for years) was checked two ways: the SEC's machine-readable XBRL data against the earnings release.
- **News.** Full articles from The Wall Street Journal, The New York Times, the Financial Times and The Economist (the Times and The Economist through a university library).
- **Sentiment.** Themes from X, Hacker News and StockTwits. Reddit could not be read directly, so I do not quote it.
- **Industry figures.** [Synergy Research](https://www.srgresearch.com/articles/cloud-market-growth-rate-surges-to-well-over-50-per-year-q3-2026), [Dell'Oro](https://techblog.comsoc.org/2026/09/16/delloro-data-center-capex-grew-92-in-2q-2026-caveats-galore/), [Cushman & Wakefield](https://finviz.com/news/388803/cushman-wakefield-releases-2026-data-center-development-cost-guide), [JLL](https://www.jll.com/en-us/insights/market-outlook/data-center-outlook) and the [US Energy Information Administration](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a), each checked against the saved source page where the site allowed it.
- **A model.** An illustrative campus of 1 GW (a gigawatt, a billion watts of power), to see what one site might earn and cost.
- **Frameworks.** Issue tree, pyramid principle (answer first, then the support), Porter's five forces (a checklist for sizing up competition), 7 Powers (seven kinds of lasting advantage), scenario planning (several futures, not one guess) and TAM/SAM/SOM (the whole market, the part you can serve, the part you might win).

<div class="simple" markdown="1">
**The simple version.** Judging whether a restaurant chain's new kitchens will pay works the same way. Ask if diners queue, what the kitchens cost, who lent the money, who the rivals are, and what must go right. Then check the claims against the receipts, not the menu.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: how the numbers were checked</summary>

Fiscal years differ. Microsoft's ends June 30, Oracle's May 31 and NVIDIA's in late January, so "latest quarter" covers different months. Capex definitions differ too: Meta's company-defined figure includes principal payments on finance leases. The 1 GW campus is a model, not a forecast, and its inputs are shown beside each result.

</details>

## How the business works {#how-it-works}

### What a hyperscaler is

A hyperscaler is a company that runs data centers at a size few others can match and rents out the computing power inside them. Three giants lead: Amazon Web Services (AWS), Microsoft Azure and Google Cloud. Synergy Research Group's Q3 2026 release puts their shares of cloud infrastructure at 26%, 19% and 16%, or 61% together ([Synergy](https://www.srgresearch.com/articles/cloud-market-growth-rate-surges-to-well-over-50-per-year-q3-2026)). Meta also builds huge data centers, but mostly to run its own apps. Oracle and the neoclouds, newer companies such as CoreWeave and Nebius built to rent out computing for AI, sell capacity too, much of it to AI labs.

The easiest picture is renting instead of buying.

<!-- FIG:fig-garage -->

### The simple machine

Think of a stack of layers, each needed by the one above it:

1. **Land and power.** A site, plus a grid connection that delivers electricity around the clock.
2. **Buildings and cooling.** Halls, backup power and cooling systems that carry the heat away.
3. **Chips and servers.** Computers full of GPUs (graphics processing units, chips that do huge numbers of sums at once and do most of AI's heavy work).
4. **Network and storage.** The cables, switches and disks that connect machines and keep data.
5. **Software.** The services customers actually use, from basic virtual computers to ready-made AI tools.

The business is to build all five once, then rent the result out many times over.

<!-- FIG:fig-stack -->

Different companies earn money at different layers: utilities and turbine makers at the bottom, data center landlords such as Equinix and Digital Realty, chip makers such as NVIDIA and TSMC, and the clouds on top.

### Who rents it, and why

- **A streaming service at peak hours.** Millions watch in the evening and few at 4 a.m., so it rents extra capacity for the rush and hands it back.
- **A bank's apps.** The apps must stay up and stay fast, so the bank rents space across several sites instead of building them all.
- **A startup training a model.** Training can need thousands of GPUs for weeks. Buying them first would drain the startup's cash.
- **An AI lab serving a chatbot.** Every answer takes computing, and the more people ask, the more capacity the lab needs.

The thread is the same: needs rise and fall, and owning is expensive.

### Five ways to buy

1. **On demand.** Pay by the hour, no promises. This is the most flexible and the highest price. For AI chips the unit is the GPU-hour: one GPU rented for one hour.
2. **Commit for a discount.** Promise to spend a set amount for one or three years. AWS Savings Plans offer discounts of up to 72% against on-demand prices ([AWS](https://aws.amazon.com/savingsplans/compute-pricing/)).
3. **Spare capacity.** AWS Spot sells unused machines at up to 90% off, but AWS can take them back at short notice ([AWS](https://aws.amazon.com/ec2/spot/pricing/)). It suits jobs that can pause.
4. **Multi-year contracts for whole data centers.** A customer signs for years of capacity. Revenue that is signed but not yet delivered is called backlog, and formally remaining performance obligations. Microsoft reported $683B at 30 September 2026 in its [10-Q](https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm) (unaudited). By my sum, the four biggest (Microsoft, Oracle, Amazon and Alphabet) hold about $2.49T. Later sections return to this.
5. **Per-token pricing for AI.** A token is a small chunk of text, roughly a word or part of one. Amazon Bedrock lists Mistral Large 3 at $0.50 per 1M input tokens and $1.50 per 1M output tokens ([Amazon Bedrock](https://aws.amazon.com/bedrock/pricing/)).

### Why scale wins

Three advantages help the giants, and none is guaranteed:

- **Keeping machines busy.** An idle machine earns nothing. Utilization, the share of capacity actually in use, can rise when many customers with different peaks share one pool.
- **Buying power.** Huge orders for chips, equipment and electricity may bring better terms and earlier delivery than a small buyer gets.
- **Custom chips.** Google designs its own TPU chips and Amazon its Trainium chips, so each can tune hardware to its own work.

Scale can also make buildings more efficient. Google reports a fleet-wide PUE (total power drawn divided by power that reaches the computers) of 1.09, against an industry average of 1.54 ([Google](https://datacenters.google/efficiency/)).

### Training and inference

Training is teaching a model by running it over enormous amounts of data, which can take thousands of chips for weeks. Inference is using the finished model to answer a question. One answer is small, but it happens millions of times. Training is writing the textbook. Inference is every student who looks something up. Where the rent comes from, and how fast each grows, is part of what this page asks.

<div class="simple" markdown="1">
**The simple version.** A hyperscaler is a very large landlord for computing power. Instead of buying computers that sit idle most of the day, a company rents what it needs by the hour, like taking a taxi instead of owning a car. The landlord's job is to keep every room rented.
</div>

<details class="deep" markdown="1">
<summary>For engineers and investors: GPU-hour prices, on demand versus a contract</summary>

The median on-demand list price for an NVIDIA H100 was $4.20 per GPU-hour on 7 October 2026, across 16 providers ([Uvik GPU price index](https://uvik.net/blog/gpu-price-index/)). SemiAnalysis's one-year contract index for the same chip stood at $2.35 in March 2026, up from $1.70 in October 2025, as cited by Uvik. By my arithmetic the contract price is about 44% below on demand, though the dates differ. For the newer B200, the median on-demand price was $8.19 (9 providers). These are list and index prices, not what any one customer pays.

</details>
