# Literature and merger-timing verification

Research date: 2026-09-27. Prepared as editorial research notes, not as a new empirical result. The current `documents/writing_sample.md` and `documents/technical_supplement.md` were read without modification. The supplied extract remains a DB1B-derived aggregate file; literature using ticket-level DB1B and flight schedules does not automatically validate its measurement or sample.

## Verified bibliography and bounded findings

### Luo (2014)

**Luo, Dan. 2014. “The Price Effects of the Delta/Northwest Airline Merger.” Review of Industrial Organization 44 (1): 27–48. https://doi.org/10.1007/s11151-013-9380-1.** Online publication was February 28, 2013; the issue year is 2014.

[Primary publisher page](https://link.springer.com/article/10.1007/s11151-013-9380-1) verifies the bibliography, abstract, notes, and appendix. The abstract reports that fares on premerger DL–NW overlap airport pairs did not rise substantially, and distinguishes the stronger fare influence of low-cost-carrier competition from legacy competition. Accessible notes establish separate nonstop/connecting models, an unweighted baseline and passenger-weighted check, and treatment of changes in other carriers' competition. These are not the same specification as the present TWFE model.

**Verification boundary:** the publisher restricts the main article body. The complete sampling period, exclusions, baseline merger coefficients, and tables were not independently recovered here. Do not present an exact Luo percentage or assert that Luo established a fare reduction. The accessible appendix's 0.023 connecting coefficient belongs to that appendix specification, not a verified universal headline estimate. Retain only the qualified qualitative comparison in the writing sample.

### Carlton et al. (2019)

**Carlton, Dennis, Mark Israel, Ian MacSwain, and Eugene Orlov. 2019. “Are Legacy Airline Mergers Pro- or Anti-Competitive? Evidence from Recent U.S. Airline Mergers.” International Journal of Industrial Organization 62: 58–95. https://doi.org/10.1016/j.ijindorg.2017.12.002.**

[Publisher](https://www.sciencedirect.com/science/article/pii/S0167718717303533); [published PDF, indexed text](https://awards.concurrences.com/docrestreint.api/pdf/19._are_legacy_airline_mergers_pro-_or_anti-competitive__evidence_from_recent_u.s._airline_mergers.pdf); [authors' institution](https://www.compasslexecon.com/insights/publications/2020-antitrust-writing-awards-nominees).

Studies DL–NW, UA–CO, and AA–US using DiD, DB1B, OAG schedules, and T-100 seats. DL–NW periods: 2006Q4–2008Q3 versus 2009Q1–2010Q4. Nonstop exposure requires five roundtrips during July 9–15 of the approval year; baseline emphasizes 2-to-1/3-to-2 markets. Connecting exposure requires each merging carrier's share ≥10%, combined ≥40%. Controls exclude all three mergers' overlap routes. Tables use passenger weights and route-clustered errors.

Table 6, DL–NW nonstop: log-fare coefficient −0.044 (SE .021), log-passengers .066 (.031), log-seats .255 (.070). These are log coefficients; exact fare conversion is approximately −4.30%. Table 4's pooled fare coefficient is −.063 (.026). The publisher introduction calls the pooled fare decrease insignificant, conflicting with Table 4's significance marker; cite the specific table, not that sentence. Published-PDF text was recovered through indexed passages; direct PDF retrieval failed.

### Borenstein (1990)

**Borenstein, Severin. 1990. “Airline Mergers, Airport Dominance, and Market Power.” American Economic Review 80 (2): 400–404.**

[Primary author-hosted article](https://faculty.haas.berkeley.edu/borenste/download/AERPP90AirMerge.pdf). All five scanned pages were visually inspected.

Studies Northwest–Republic at Minneapolis/St. Paul and TWA–Ozark at St. Louis, both October 1986 mergers—not Delta–Northwest. Prices in 1985Q3, 1986Q3, and 1987Q3 are compared with industry prices for similar-distance routes. Table 2 uses unweighted route changes, ≥10 passengers/day, and ≥10% shares to classify active competitors; only local origin-destination traffic enters that table. Its average relative change is +9.5% (SE 2.1) across 84 NW–Republic markets and approximately zero across 67 TWA–Ozark markets. The paper finds stronger evidence of increased market power in the former case; some increases predate completion. Other tables examine origin-specific market shares, capacity, and load factors. This is historical evidence of heterogeneous outcomes and airport-level mechanisms, not an estimate for 2008 or a modern TWFE design.

### Kim and Singal (1993)

**Kim, E. Han, and Vijay Singal. 1993. “Mergers and Market Power: Evidence from the Airline Industry.” American Economic Review 83 (3): 549–569. https://www.jstor.org/stable/2117533.**

Bibliography verified against the [journal's June 1993 contents](https://www.jstor.org/stable/i337069) and [Singal's university publication list](https://finance.pamplin.vt.edu/faculty/directory/singal.html). The [publisher-attributed abstract reproduced by RePEc](https://ideas.repec.org/a/aea/aecrev/v83y1993i3p549-69.html) describes 1985–1988 mergers, comparing fares on merging firms' routes with unaffected routes, and reports relative increases interpreted as market-power effects outweighing efficiencies.

**Verification boundary:** original full text was not accessible from JSTOR here. Exact transaction list, sample construction, estimator details, and quantitative effects are unverified. Do not insert an often-repeated “10%” figure or a merger count without checking the original. The qualitative abstract is a lower-detail basis than the full Borenstein article. For a strictly full-text-verified paragraph, omit this paper's empirical claim until library access supplies the article.

## Legitimate comparison with the present estimate

The current baseline concerns 156 overlap and 105 comparison airport pairs, with single-carrier operating-code shares fixed using 2007, a 5% threshold in at least three quarters, all-carrier passenger-weighted mean fares, and equal route-quarter regression weights. Its −5.72% is a descriptive relative change after 2008Q4. The event study and the separately estimated 2005–2007 diagnostic show that the groups already had differing fare paths.

Consequently:

- Numerical proximity between −5.72% and Carlton's DL–NW nonstop estimate does **not** constitute replication. Exposure, market type, weighting, time windows, controls, and data availability differ. The present extract's one-coupon category does not establish scheduled nonstop service.
- Luo's modest overlap-price findings and this negative contrast need not conflict. Neither supplies the missing counterfactual for the other design.
- The 1980s papers motivate possible competition and hub mechanisms; they cannot predict the sign or magnitude of this later transaction.
- Fare changes alone cannot separate a markup change, marginal-cost reduction, altered service quality, or shifts in the passenger/itinerary mix. An average decline also does not establish that every passenger benefited.
- Do not choose among sample definitions because one matches the literature. Report the prespecified baseline and the full sensitivity pattern, including sign changes.

These comparisons are methodological judgments based on differences between the current documents and the sources above, not additional estimates.

## Concise economic / game-theory framing

Suggested conceptual framing, explicitly not an estimated structural model:

“A merger changes the incentives of firms that previously priced competing itineraries independently. Common ownership can reduce the incentive to undercut a close substitute, creating upward pressure on fares. Integration can also lower marginal operating costs or improve network connections, while schedule and service changes alter demand. These forces need not have the same strength across airport pairs. The sign of the observed fare change is therefore an empirical question; a fare-only comparison cannot identify which mechanism dominates.”

If a game-theory sentence is needed, add: “This is a change in a differentiated-products pricing game, with possible network and capacity adjustments.” Avoid labeling the regression a test of Cournot/Bertrand equilibrium, tacit collusion, or efficiency pass-through. None is identified by the present reduced-form exercise. Repeated-game coordination is a possible mechanism requiring additional evidence; its inclusion would create a claim this sample does not test.

## Suggested literature paragraphs

The following two paragraphs can replace an extended literature review. They intentionally avoid unavailable quantitative details.

“Retrospective airline-merger research finds that outcomes depend on the transaction and the markets examined. Borenstein (1990) documents stronger evidence of increased market power after Northwest–Republic than after TWA–Ozark. For Delta–Northwest, Luo (2014) reports limited fare increases on overlap airport pairs. Carlton et al. (2019), examining three later legacy-airline mergers, also evaluates passenger traffic and capacity, placing fare changes within a broader assessment of competitive outcomes.”

“This note asks a narrower question: how fares changed on airport pairs meeting an explicit premerger overlap rule relative to a stated comparison group. Differences in service definitions, weighting, comparison routes, and sample periods prevent a direct numerical comparison with earlier estimates. Because the groups' fare paths differed before the announcement, the results are interpreted as descriptive contrasts rather than identified merger effects. Their value lies in making the measurement and comparison choices transparent and showing which conclusions survive changes in those choices.”

Optional classic-literature addition, conditional on accepting abstract-level verification: “Kim and Singal (1993) likewise report relative fare increases across a set of 1980s mergers.” The paragraph is complete without that sentence.

## Official dates for other mergers within the study window

| Transaction | Public announcement | Corporate closing | Primary evidence |
|---|---|---|---|
| United–Continental (UA–CO) | May 3, 2010 (2010Q2) | October 1, 2010 (2010Q4) | [United-hosted filed announcement](https://ir.united.com/static-files/69c1f868-c861-48c0-8ada-6cda772720ee); [closing 8-K](https://ir.united.com/static-files/0d639e33-8958-47c8-bab7-089db8e87ea9) |
| America West–US Airways (HP–US) | May 19, 2005 (2005Q2) | September 27, 2005 (2005Q3) | [SEC filing explicitly identifying announcement date](https://www.sec.gov/Archives/edgar/data/701345/000095015305003004/p71534exv99w1.htm); [America West 10-Q, Note 1](https://www.sec.gov/Archives/edgar/data/706270/000095015305002835/p7141401e10vq.htm) |

Do not confuse agreement signing, public announcement, antitrust clearance, corporate closing, and operational integration. UA–CO's agreement was signed May 2, 2010, but public announcement was May 3. The United filing states that the airlines continued operating separately pending integration. One US Airways 8-K contains a contradictory “September 27, 2007” in Item 1.01; use its Item 2.01 and the independent contemporaneous 10-Q, which establish the 2005 closing.

### Implications for this sample (proposed checks, not completed analyses)

The current legacy comparison set includes UA, CO, US, and HP. These transactions can affect both control and treated routes through rival service; membership in a non-DL–NW group is not proof of no exposure.

1. A UA–CO timing sensitivity ending in 2010Q1 excludes the public-announcement period. Dropping only 2010Q4 addresses corporate closing but leaves 2010Q2–Q3 potentially exposed. Report both their rationale and the shorter post-DL–NW window.
2. A further route-exposure check can predefine meaningful UA/CO and US/HP service using pre-event observations and examine exclusion of exposed routes. It must apply consistently across treatment and control groups. Do not relabel all routes with any one of those carriers as merger overlap.
3. HP–US occurred early in the 2005–2010 sample. Starting in 2006 removes its immediate event quarters, not necessarily its continuing consequences. Restricting data also changes route availability and precision.
4. These checks address particular competing explanations. None repairs the main pretrend evidence automatically, and a stable coefficient would not prove a causal effect.

## Source and quotation discipline

Primary publisher/author material and official filings underpin the claims above. Bibliographic abstracts are explicitly distinguished from verified full text. No paywall was bypassed. Do not import numbers from court summaries, student papers, secondary review tables, working-paper versions, or search snippets about a different merger as if they were the final article's baseline results. Retain exact paper/table references if any literature numbers enter the supplement.


## Added mechanism and transaction context (September 27, 2026)

Kumar, V., R. C. Marshall, L. M. Marx, and L. Samkharadze (2015), "Buyer resistance for cartel versus merger," IJIO 39:71-80, doi:10.1016/j.ijindorg.2015.02.002. Author-hosted full text: https://people.duke.edu/~marx/bio/papers/KumarMarshallMarxSamkharadzeIJIO2015.pdf . The model studies procurement, buyers' ability to reject bids and qualify another supplier, and uncertainty about cartel existence. It does not supply an airline-merger prediction of gradual fare increases. The paper uses the citation for buyer information and resistance, not as an event-study null hypothesis.

DOJ October 29, 2008 closing statement: https://www.justice.gov/archive/opa/pr/2008/October/08-at-963.html . The statement emphasizes remaining competition, expected efficiencies, and complementary networks. It does not count four or twelve nonstop overlaps. The manuscript's four persistent one-coupon overlaps are sample-specific and are not attributed to DOJ. The twelve-of-over-1,000 statement, if ever used, is from Delta's own April 14 announcement.

Luo's publisher abstract supports limited fare increases and the relevance of low-cost-carrier competition. The present negative mixed-service contrast has a different sign and target. The article compares the economic question without calling the present result a replication or inferring zero causal effects from a wide interval.

## Bibliographic formatting and issuer check, September 27, 2026

The current references use author-date entries, with hyperlinks on actual titles or DOI identifiers instead of trailing research-note labels. Reopening the official United-hosted files establishes that the May 3 document is a Continental Airlines supplier letter; the October 1 Form 8-K is issued by United Continental Holdings. The references now identify these separately. The linked September 2005 SEC Form 10-Q explicitly names both US Airways Group and America West Airlines on its cover and identifies itself as their combined filing, so the joint corporate author is retained. These checks refine bibliographic attribution without changing the merger dates or analytical results.

The JEL identifiers were checked against the [AEA classification list](https://www.aeaweb.org/econlit/jelCodes.php?view=econlit): L93 (Air Transportation), L41 (Monopolization; Horizontal Anticompetitive Practices), and G34 (Mergers; Acquisitions; Restructuring; Voting; Proxy Contests; Corporate Governance).
