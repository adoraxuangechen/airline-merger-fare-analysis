# Fare Changes After the Delta–Northwest Merger:
## Market Composition and Competitive Exposure
@byline Xuange (Adora) Chen | The Pennsylvania State University | September 2026

@footnote I am especially grateful to Robert C. Marshall for his individual guidance on this project in ECON 449: Economics of Collusion (Fall 2025). His generosity with his time and careful attention to data problems taught me what rigorous empirical research requires. All errors are my own. Replication code, data-access instructions, and source documentation are available at the [project repository](https://github.com/adoraxuangechen/airline-merger-fare-analysis). Data: Borenstein's NBER-hosted airline market files. Contact: [xmc5171@psu.edu](mailto:xmc5171@psu.edu).

@abstract I examine fare changes around the 2008 Delta–Northwest merger using Borenstein's market data for 2005-2010. The primary comparison holds 260 airport pairs fixed and allows baseline distance and itinerary composition to have different quarterly fare paths. Adjustment reduces the estimated relative decline from {{valid_pct}}% to {{adjusted_pct}}%, with an interval that includes zero. Expanding the comparison population initially yields a larger decline, but allowing routes with baseline Southwest service to follow different paths brings the two estimates closer. Carrier-specific fare comparisons and sensitivity analysis for departures from parallel trends provide additional checks. Market and carrier composition materially shape the apparent price response. Remaining pre-merger differences make the causal magnitude sensitive to assumptions about the counterfactual fare path.

@keywords airline mergers; market competition; DB1B; difference-in-differences; event study

@jel L93; L41; G34

### 1. Introduction

How did fares change on routes where Delta and Northwest competed before their merger? In revisiting this question, I compared the markets behind the initial estimate. Overlap routes averaged 1,818 miles, against 717 miles in the comparison group, and their one-coupon passenger shares were 9.6% and 65.1%. Those differences made market composition central to my analysis: fuel prices and the recession could affect these two groups differently.

I therefore hold the same 260 routes fixed and allow baseline market types to follow different quarterly fare paths. The estimated relative decline moves from {{valid_pct}}% to {{adjusted_pct}}%, a reduction of about 3.1 percentage points, with a 95% interval of {{adjusted_ci}}. I use this as the primary design, then examine Southwest composition and within-route carrier pricing to interpret the result.

Delta and Northwest announced their agreement on April 14, 2008 and completed the transaction on October 29, 2008 (Delta Air Lines, 2008a, 2008b). The analysis fixes exposure using 2007 service and begins the post-completion period in 2008Q4. In closing its investigation, the Department of Justice emphasized continued competition on most overlapping routes, expected cost savings, and the service benefits of complementary networks (U.S. Department of Justice, 2008). In this sample, only four airport pairs satisfy the persistent, material one-coupon-overlap rule. Under this sample rule, connecting journeys account for most of the measured overlap.

### 2. Economic mechanisms and related evidence

#### 2.1 Pricing mechanisms

Before a merger, firms offering competing itineraries choose prices separately. Common ownership internalizes some passenger diversion between the merging firms: a price increase that loses customers to the partner becomes less costly to their combined profit. This creates upward pricing pressure when their products are close substitutes. Integration-related cost savings may exert downward pressure, while better connections can change service quality, willingness to pay, and fares. Schedule, capacity, and passenger-composition changes also affect measured fares. The balance of these forces can differ between connecting and nonstop markets.

Repeated interaction provides another possible mechanism: a merger can change the gains from deviation and the ability to sustain coordinated pricing. Kumar, Marshall, Marx, and Samkharadze (2015, KMMS) add the role of buyer resistance. In their procurement model, buyers can reject bids and qualify another supplier; uncertainty about a hidden cartel can make that response less attractive than after an observable merger. This explains why buyer information can affect the relative profitability of collusion and merger.

#### 2.2 Related evidence

Earlier retrospectives show that airline-merger outcomes vary across transactions. Borenstein (1990) finds different patterns for Northwest-Republic and TWA-Ozark; Kim and Singal (1993) report relative fare increases on merging firms' routes in the 1980s. Luo (2014) reports limited fare increases on Delta–Northwest overlap airport pairs. Carlton et al. (2019) examine three legacy mergers using fares, traffic, and capacity. The limited increases in Luo and the small, imprecise adjusted contrast here both motivate caution about a large, general fare-increase account of this transaction. Their signs differ: Luo reports increases, whereas this paper estimates a negative relative change in mixed-service airport-pair fares. Differences in service definitions and comparison markets are economically relevant to that comparison.

@page
### 3. Data and fare construction

The primary source is Borenstein's broadened-market archive hosted by NBER. I select 2005Q1-2010Q4 from the source Stata file and verify the extract against that archive. The supplement documents this reconciliation and each cleaning step.

Each of the 4,175,354 input records describes an unordered airport pair, quarter, operating-carrier set, and one- or two-coupon category. Directions are combined, and each row aggregates sampled passenger journeys. The archive includes all recorded carriers; the source documentation describes restrictions to domestic, one-way or round-trip itineraries and other upstream ticket filters (Borenstein, n.d.). The analysis adds no new fare trimming or winsorization.

For airport pair r in quarter t, I recover the passenger-weighted mean fare from the cell means:

@equation p̄_rt = Σ_i(n_i × p̄_i) / Σ_i(n_i), for cells i in market (r,t); y_rt = log(p̄_rt).

Here n_i is the sampled passenger count and the barred price is the cell mean. The regression outcome is the natural logarithm of the market mean. An unweighted average of record-level fares would give a cell representing one passenger the same influence as a cell representing thousands. Passenger weighting in constructing the fare is separate from the equal route-quarter weights used in estimation.

@table sample
@caption Table 1. Sample construction. Passenger counts measure sampled journeys. All group-selection rules use 2007. The distance-adjusted sample omits one route with a recorded zero distance.

Four same-airport records are removed. All remaining fares and passenger counts are finite and positive, and the natural record keys are unique. Missing second-carrier fields on one-coupon journeys are structural and do not trigger deletion. Missing market quarters are not filled. The original main panel has five absent route-quarter cells; all treated routes are observed in all 24 quarters.

Fares are nominal, one-way-equivalent dollars. Quarter effects absorb a common quarterly deflator in the log-fare model; market-specific responses to fuel and demand require additional controls. One coupon is the observed service category; confirming physical nonstop service would require schedule data. The supplement documents separately retrieved BTS source files and the fields needed for a more detailed future panel.

@page
### 4. Comparison design and market composition

A route is eligible if it has at least 100 sampled journeys in each quarter of 2007. A carrier's single-carrier service includes one-coupon records under its operating code and two-coupon records with that code in both carrier fields. Shares divide these journeys by all journeys on the route, including mixed-carrier itineraries. An overlap route has Delta and Northwest shares of at least 5% in the same quarter in at least three of the four quarters. This identifies 156 treated routes.

The initial comparison consists of 105 eligible routes with no DL or NW code in either field during 2007 and a combined single-carrier share of at least 5% for AA, AS, CO, UA, US, or HP in at least three quarters. These markets include both legacy and low-cost-carrier service: Southwest appears on 30 comparison routes in 2007. The treatment and comparison labels remain fixed after the merger.

@table balance_main
@caption Table 2. Baseline route characteristics. Values are equal-weighted route means of 2007 quarterly characteristics. The distance-adjusted comparison excludes SJU-STT, whose source distance is zero. The common-support columns retain joint distance/service-composition cells with at least three routes from each group.

Figure 1 shows the unadjusted fare levels on the primary sample. Both groups rise into 2008, fall in 2009, and recover in 2010. The gap also changes before completion, motivating the comparison of market composition and relative trends.

@figure ../extensions/raw_fare_trends/results/raw_fare_trends.png
@caption Figure 1. Raw quarterly mean fares. Lines give equal-route arithmetic means of passenger-weighted route-quarter fares, in nominal one-way-equivalent dollars. The fixed sample contains 156 overlap and 104 comparison routes; observed quarterly counts are 156 and 102-104. Shading spans the announcement-completion quarters. These descriptive dollar levels precede the log-fare regression adjustments.

The initial imbalance suggests a specific explanation for differential trends: long connecting markets and short one-coupon markets could respond differently to fuel prices and the recession. To examine this possibility, I add fixed 2007 distance-bin × quarter and one-coupon-share-bin × quarter effects. Distance bins have boundaries at 750, 1,500, and 2,000 miles. Share bins are below 10%, 10% to below 50%, 50% to below 90%, and at least 90%. All composition measures are fixed before the announcement.

The common-support comparison retains only joint cells with at least three treated and three comparison routes, then uses joint-cell × quarter effects. It leaves {{support_treated}} treated and {{support_controls}} comparison routes. One-coupon shares become much closer, with residual differences in distance, traffic, and carrier structure. This restriction targets a narrower population.

I also relax the legacy-participation requirement while retaining zero observed DL/NW exposure in 2007. With valid distance data, this expands the comparison to {{expanded_controls}} routes. The added routes broaden the range of business models represented in the comparison. A dated design log and complete specification registry accompany the results.

@page
### 5. Fare changes after accounting for composition

The primary specification compares the fixed legacy sample while allowing baseline market types to have distinct quarterly fare paths. The unadjusted model and distance-only adjustment provide a stepwise benchmark:

@equation log(fare_rt) = α_r + λ_t + β(Overlap_r × Post_t) + γ_distance(r),t + η_share(r),t + ε_rt.

Post begins in 2008Q4. Standard errors are clustered by route, with a finite-sample adjustment and a t reference distribution. Table 3 reports 100[exp(β)-1] and transformed 95% intervals. The intervals summarize sampling uncertainty conditional on the specification.

@table primary_core
@caption Table 3. Primary fixed-sample comparison. All three rows use the same 156 overlap and 104 comparison routes, 6,235 observed route-quarters, passenger-weighted market fares, and equal regression weights. Percentages are 100[exp(β)-1]; intervals use route-clustered standard errors. The distance-and-composition model is the primary diagnostic specification.

On identical observations, the unadjusted estimate is {{valid_pct}}%. Distance-specific quarterly effects reduce its magnitude to {{distance_pct}}%; adding baseline service-composition effects yields {{adjusted_pct}}%, with a 95% interval of {{adjusted_ci}}. Restricting the comparison to common-support cells yields {{support_pct}}%. The fixed-sample comparison shows how strongly the estimated decline depends on accounting for the baseline imbalance.

As a secondary population check, the expanded comparison adds 356 routes and gives {{expanded_pct}}%, or {{expanded_support_pct}}% after its own common-support restriction. Southwest is present in 54% of the added routes, compared with 29% of the valid-distance legacy controls. Its mean share of journeys recording WN in either carrier field is 45% versus 13%. I investigate these carrier-composition differences in Table 4.

@table wn_main
@caption Table 4. Baseline Southwest composition and comparison-set sensitivity. Each cell reports the relative change and 95% interval. Legacy uses 156/104 treated/comparison routes; expanded uses 156/460. All models include distance- and itinerary-composition-bin × quarter effects. Additional interactions use 2007 WN presence or any-WN journey-share groups of zero, above zero but below 50%, and at least 50%. These follow-up checks were added after inspecting the initial comparison-set discrepancy.

With baseline WN-presence × quarter effects, the legacy and expanded estimates are -2.70% and -2.55%. The closer estimates support carrier mix as a relevant dimension of the comparison. The share-group version yields -1.63% and +0.82%, revealing further sensitivity to Southwest exposure intensity. Only two treated routes have WN shares of at least 50%, so that specification also has weak overlap in carrier composition. The table retains both adjustments, each based on fixed 2007 carrier composition.

@page
### 6. Dynamics and the adequacy of the comparison

The event regressions replace the single post interaction with quarterly overlap interactions. Figure 2 uses 2007Q4 as the reference, before the April 2008 announcement. The two panels share the same 260-route sample, which isolates the effect of adding baseline composition controls.

@figure event_comparison.png
@caption Figure 2. Event-study contrasts before and after composition adjustment. Points and bars show relative log-fare contrasts and pointwise 95% route-clustered intervals. The open point marks 2007Q4, normalized to zero by construction. Shading covers 2008Q2-2008Q4; the dashed line marks the completion quarter. The coefficients trace the overlap-comparison log-fare gap relative to that reference.

The adjusted path retains substantial pre-merger differences. A joint test of the eleven 2005Q1-2007Q3 coefficients gives F = {{pre_base_f}} without the additional controls and F = {{pre_adj_f}} with them; both p-values are below 0.001. The common-support event model also rejects equality of the pre-reference contrasts (p = {{pre_support_p}}). These diagnostics use the full-window event regressions.

I respond to the remaining pre-period differences with the relative-magnitude sensitivity framework of Rambachan and Roth (2023), using their official HonestDiD implementation. For the composition-adjusted model, the target is the average of the nine completion-and-later event coefficients, 2008Q4-2010Q4; this is a different estimand from the pooled coefficient in Table 3. The counterfactual gap may change each post-reference quarter by at most M times its largest pre-reference quarterly change. The 2008Q1-2008Q3 coefficients remain in the vector with zero target weight, allowing for announcement-period effects.

For the causal contrast underlying the unadjusted -5.58% regression, the numerical HonestDiD breakdown is approximately M=0.08: zero is excluded at M=0.076 and included at M=0.077. This sensitivity target preserves the pooled regression's causal weights; its plug-in contrast differs from the observed pooled coefficient. Appendix M derives the weights, including the early-2008 terms. A separate equal-weight completion-period target gives the same bracket. Thus the baseline negative-sign conclusion is sensitive to small allowances for continued differential quarterly changes.

For the composition-adjusted nine-quarter target, at M=0.5 the approximate 95% robust interval is [-34.4%, 42.0%]. Even a restriction limiting later quarterly deviations to half the largest earlier deviation leaves the sign unresolved. This is an informative limit on the design: over a long post period, small differential changes can accumulate. The robust interval incorporates this additional uncertainty about the counterfactual path. The supplement reports M=0, 0.5, 1, and 2, the complete covariance matrix, target weights, and inversion-grid checks. I retain the original specifications throughout this exercise, following Roth's (2022) caution about selecting designs through pre-tests.

@page
### 7. Carrier responses and competitive exposure

I compare single-carrier journeys recorded under DL or NW with those recorded under any other operating-carrier code on the same routes. A single-carrier journey has one coupon or the same code on both coupons. The other-code pool may include regional affiliates, including affiliates of DL/NW, because ownership links are unavailable. Mixed-code journeys are excluded from both groups. The baseline cohort contains 144 routes with both fare series throughout 2007; route and quarter effects summarize their log-fare difference.

The DL/NW-to-other-code fare ratio rises by 1.57% in 2009-2010 relative to 2007, with a 95% interval of [-0.70%, 3.89%]. Balanced-panel and two-coupon checks yield similarly imprecise increases (Table A10). The market-average decline therefore coexists with a small, imprecise increase in the merging carriers' relative fare ratio. The within-route gap falls around completion and then rebounds, against an already declining pre-merger gap. These comparisons hold the airport pair fixed and follow the relative prices of two changing itinerary groups. Full paths, mixed-carrier coverage, and sample counts appear in the supplement.

The concentration diagnostic estimates a small exposure gradient: {{dose_pct}}% per 100 points of the frozen-share proxy 20,000 × s_DL × s_NW, with interval {{dose_ci}}. The high-low difference has p={{dose_difference_p}}. The shares use all route passengers; mixed itineraries and regional affiliations prevent treating this operating-code proxy as full firm-level ΔHHI. Conditional concentration measures and all exposure models are reported in the supplement.

Checks ending in 2009 and starting in 2006 address the timing of United-Continental and America West-US Airways, respectively. Their adjusted estimates are -2.72% and -2.99%, both with intervals including zero. A stricter screen removing every route with baseline UA or CO presence leaves only six treated routes. Table A4 reports these time-window checks and route-trend sensitivities together.

### 8. Economic interpretation

My assessment changed when I compared the underlying markets. The unadjusted fare decline was large enough to attract attention, but the overlap and comparison routes represented very different services. Holding routes fixed and adjusting for those differences reduces the apparent decline by about 3.1 percentage points. Examining Southwest exposure then helps explain why broadening the comparison initially produces a larger decline. I interpret these findings as evidence that market and carrier composition account for an economically important part of the measured fare contrast.

The carrier-group results sharpen that judgment. DL/NW's fare ratio relative to other recorded carriers changes little and imprecisely, even as the market-level comparison shows a relative decline. The event paths fall around completion and rebound during 2009. Together with the transaction's complementary-network setting, the results provide limited evidence of a broad, sustained fare increase. They leave several plausible economic explanations open, including demand shifts, service changes, and cost savings.

Adjusted pre-merger paths still differ, and HonestDiD intervals allow sizeable positive and negative effects. The composition adjustments diagnose sensitivity; they do not identify separate fuel, recession, or Southwest effects. Changing product mixes and responsive other-code prices also complicate interpretation. Ticketing-carrier affiliations, schedules, capacity, and entry data would help distinguish strategic pricing from service changes. Testing KMMS would additionally require buyer information and supplier-qualification decisions.

@page
### References

Borenstein, Severin. 1990. "[Airline Mergers, Airport Dominance, and Market Power](https://faculty.haas.berkeley.edu/borenste/download/AERPP90AirMerge.pdf)." American Economic Review 80 (2): 400–404.

Borenstein, Severin. n.d. "[Description of Market Data Files Created by Severin Borenstein](https://faculty.haas.berkeley.edu/borenste/mktdata.htm)."

Carlton, Dennis, Mark Israel, Ian MacSwain, and Eugene Orlov. 2019. "Are Legacy Airline Mergers Pro- or Anti-Competitive? Evidence from Recent U.S. Airline Mergers." International Journal of Industrial Organization 62: 58–95. [https://doi.org/10.1016/j.ijindorg.2017.12.002](https://doi.org/10.1016/j.ijindorg.2017.12.002).

Continental Airlines, Inc. 2010. [Letter to suppliers regarding the proposed merger with United](https://ir.united.com/static-files/69c1f868-c861-48c0-8ada-6cda772720ee). May 3.

Delta Air Lines. 2008a. "[Delta Air Lines, Northwest Airlines Combining To Create America's Premier Global Airline](https://ir.delta.com/news/news-details/2008/Delta-Air-Lines-Northwest-Airlines-Combining-To-Create-Americas-Premier-Global-Airline/default.aspx)." April 14.

Delta Air Lines. 2008b. "[Delta and Northwest Merge, Creating Premier Global Airline](https://ir.delta.com/news/news-details/2008/Delta-and-Northwest-Merge-Creating-Premier-Global-Airline/default.aspx)." October 29.

Kim, E. Han, and Vijay Singal. 1993. "[Mergers and Market Power: Evidence from the Airline Industry](https://www.jstor.org/stable/2117533)." American Economic Review 83 (3): 549–569.

Kumar, Vikram, Robert C. Marshall, Leslie M. Marx, and Lily Samkharadze. 2015. "Buyer Resistance for Cartel versus Merger." International Journal of Industrial Organization 39: 71–80. [https://doi.org/10.1016/j.ijindorg.2015.02.002](https://doi.org/10.1016/j.ijindorg.2015.02.002).

Luo, Dan. 2014. "The Price Effects of the Delta/Northwest Airline Merger." Review of Industrial Organization 44 (1): 27–48. [https://doi.org/10.1007/s11151-013-9380-1](https://doi.org/10.1007/s11151-013-9380-1).

National Bureau of Economic Research. n.d. "Department of Transportation DB1A/DB1B." [https://doi.org/10.60592/tb1p-9p78](https://doi.org/10.60592/tb1p-9p78).

Rambachan, Ashesh, and Jonathan Roth. 2023. "A More Credible Approach to Parallel Trends." Review of Economic Studies 90 (5): 2555–2591. [https://doi.org/10.1093/restud/rdad018](https://doi.org/10.1093/restud/rdad018).

Roth, Jonathan. 2022. "Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends." American Economic Review: Insights 4 (3): 305–322. [https://doi.org/10.1257/aeri.20210236](https://doi.org/10.1257/aeri.20210236).

United Continental Holdings, Inc. 2010. [Form 8-K](https://ir.united.com/static-files/0d639e33-8958-47c8-bab7-089db8e87ea9). October 1.

U.S. Department of Justice. 2008. "[Statement of the Department of Justice's Antitrust Division on Its Decision to Close Its Investigation of the Merger of Delta Air Lines Inc. and Northwest Airlines Corporation](https://www.justice.gov/archive/opa/pr/2008/October/08-at-963.html)." October 29.

US Airways Group, Inc., and America West Airlines, Inc. 2005. [Form 10-Q for the Quarterly Period Ended September 30, 2005](https://www.sec.gov/Archives/edgar/data/706270/000095015305002835/p7141401e10vq.htm). Note 1.
