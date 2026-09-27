# Fare Changes After the Delta-Northwest Merger:
## Market Composition and Competitive Exposure
Xuange (Adora) Chen
The Pennsylvania State University
xmc5171@psu.edu
Revised September 27, 2026

### Abstract

I examine fare changes around the 2008 Delta-Northwest merger using Borenstein's market data for 2005-2010. The primary comparison holds 260 airport pairs fixed and allows baseline distance and itinerary composition to have different quarterly fare paths. Adjustment reduces the estimated relative decline from -5.58% to -2.45%, with an interval that includes zero. Expanding the comparison population initially yields a larger decline, but allowing routes with baseline Southwest service to follow different paths brings the two estimates closer. Carrier-specific fare comparisons and sensitivity analysis for departures from parallel trends provide additional checks. The central finding is that market and carrier composition materially shape the apparent price response; the evidence supports neither a single stable merger-effect estimate nor a direct inference about coordinated pricing.

Keywords: airline mergers; market competition; DB1B; difference-in-differences; event study

### 1  Introduction

Market composition matters quantitatively for this merger retrospective. On the same 260 routes, accounting for distance and baseline itinerary composition reduces the estimated relative fare decline from -5.58% to -2.45%, a reduction of about 3.1 percentage points. The primary design is this fixed-sample comparison: it isolates how adjustment changes the original result without changing the routes being compared. Its 95% interval, [-5.92%, 1.14%], includes zero. The broader comparison and common-support exercises assess how far that conclusion travels across markets.

Delta and Northwest announced their agreement on April 14, 2008 and completed the transaction on October 29, 2008 (Delta Air Lines, 2008a, 2008b). The analysis fixes exposure using 2007 service and begins the post-completion period in 2008Q4. The merger coincided with the financial crisis and recession, making differences in market exposure central to the comparison. In closing its investigation, the Department of Justice emphasized continued competition on most overlapping routes, expected cost savings, and the service benefits of complementary networks (U.S. Department of Justice, 2008). In this sample, only four airport pairs satisfy the persistent, material one-coupon-overlap rule. The analysis therefore primarily concerns connecting-market overlap; four is not a count of all nationwide nonstop overlaps.

### 2  Economic mechanisms and related evidence

#### 2.1 Pricing mechanisms

Before a merger, firms offering competing itineraries choose prices separately. Common ownership internalizes some passenger diversion between the merging firms: a price increase that loses customers to the partner becomes less costly to their combined profit. This creates upward pricing pressure when their products are close substitutes. Integration-related cost savings may exert downward pressure, while better connections can change service quality, willingness to pay, and fares. Schedule, capacity, and passenger-composition changes also affect measured fares. A predominantly connecting market need not respond like a market with competing nonstop services.

Repeated interaction provides another possible mechanism: a merger can change the gains from deviation and the ability to sustain coordinated pricing. Kumar, Marshall, Marx, and Samkharadze (2015, KMMS) add the role of buyer resistance. In their procurement model, buyers can reject bids and qualify another supplier; uncertainty about a hidden cartel can make that response less attractive than after an observable merger. This explains why buyer information can affect the relative profitability of collusion and merger. It is not a model-specific prediction of gradual post-merger airline fare increases.

#### 2.2 Related evidence

Earlier retrospectives show that airline-merger outcomes vary across transactions. Borenstein (1990) finds different patterns for Northwest-Republic and TWA-Ozark; Kim and Singal (1993) report relative fare increases on merging firms' routes in the 1980s. Luo (2014) reports limited fare increases on Delta-Northwest overlap airport pairs. Carlton et al. (2019) examines three legacy mergers using fares, traffic, and capacity. The limited increases in Luo and the small, imprecise adjusted contrast here both motivate caution about a large, general fare-increase account of this transaction. Their signs differ: Luo reports increases, whereas this paper estimates a negative relative change in mixed-service airport-pair fares. Differences in service definitions and comparison markets are economically relevant to that comparison.


### 3  Data and fare construction

The primary source is Borenstein's broadened-market archive hosted by NBER. I select 2005Q1-2010Q4 directly from the source Stata file and reconcile it with the dataset used in the previous version. The resulting analysis uses the same airport and numerical observations. Technical details of that reconciliation are recorded in the supplement, leaving the source file unchanged.

Each of the 4,175,354 input records describes an unordered airport pair, quarter, operating-carrier set, and one- or two-coupon category. Directions are combined, and a row is an aggregate of sampled passenger journeys rather than an individual ticket. The archive includes all recorded carriers; the source documentation describes restrictions to domestic, one-way or round-trip itineraries and other upstream ticket filters (Borenstein, n.d.). The analysis adds no new fare trimming or winsorization.

For airport pair r in quarter t, I recover the passenger-weighted mean fare from the cell means:

p̄_rt = Σ_i(n_i × p̄_i) / Σ_i(n_i), for cells i in market (r,t); y_rt = log(p̄_rt). (1)

Here n_i is the sampled passenger count and the barred price is the cell mean. The regression outcome is the natural logarithm of the market mean. An unweighted average of record-level fares would give a cell representing one passenger the same influence as a cell representing thousands. Passenger weighting in constructing the fare is separate from the equal route-quarter weights used in estimation.

Table 1: Sample construction
| Stage | Count |
| --- | --- |
| NBER aggregate records, 2005-2010 | 4,175,354 |
| Records after cleaning | 4,175,350 |
| Observed airport-pair quarters | 609,396 |
| Routes meeting 2007 eligibility | 5,535 |
| Initial overlap / comparison routes | 156 /105 |
| Initial route-quarter observations | 6,259 |
| Distance-adjusted routes / observations | 260 /6,235 |
Passenger counts are sampled journeys, without expansion to population totals. All group-selection rules use 2007. The distance-adjusted sample omits one route with a recorded zero distance.

Four same-airport records are removed. All remaining fares and passenger counts are finite and positive, and the natural record keys are unique. Missing second-carrier fields on one-coupon journeys are structural and do not trigger deletion. Missing market quarters are not filled. The original main panel has five absent route-quarter cells; all treated routes are observed in all 24 quarters.

Fares are nominal, one-way-equivalent dollars. A common quarterly deflator is absorbed by the quarter effects in a log-fare regression. It would not remove different fuel-price or demand responses across market types. The data do not retain ticket-level price dispersion, ticketing carriers, or complete regional-carrier affiliations. One coupon is an observed service category, not confirmation of a physically nonstop flight. Newly retrieved BTS Market, Coupon, and Ticket source files are documented separately and are not mixed into this analysis.


### 4  Comparison design and market composition

A route is eligible if it has at least 100 sampled journeys in each quarter of 2007. A carrier's single-carrier service includes one-coupon records under its operating code and two-coupon records with that code in both carrier fields. Shares divide these journeys by all journeys on the route, including mixed-carrier itineraries. An overlap route has Delta and Northwest shares of at least 5% in the same quarter in at least three of the four quarters. This identifies 156 treated routes.

The initial comparison consists of 105 eligible routes with no DL or NW code in either field during 2007 and a combined single-carrier share of at least 5% for AA, AS, CO, UA, US, or HP in at least three quarters. This rule requires legacy-carrier participation; it does not exclude low-cost carriers. Southwest appears on 30 of these comparison routes in 2007. The treatment and comparison labels remain fixed after the merger.

Table 2: Baseline route characteristics
| Characteristic | Initial overlap | Initial comparison | Support overlap | Support comparison |
| --- | --- | --- | --- | --- |
| Routes | 156 | 105 | 133 | 35 |
| Distance (miles) | 1,818 | 717 | 1,834 | 1,407 |
| One-coupon share | 9.6% | 65.1% | 3.7% | 2.9% |
| Mean fare ($) | 233.27 | 193.95 | 236.05 | 251.70 |
| Quarterly sample passengers | 1,121 | 2,144 | 721 | 309 |
Values are equal-weighted route means of 2007 quarterly characteristics. The distance-adjusted comparison excludes SJU-STT, whose source distance is zero. The common-support columns retain joint distance/service-composition cells with at least three routes from each group.

The initial imbalance suggests a specific explanation for differential trends: long connecting markets and short one-coupon markets could respond differently to fuel prices and the recession. This is a hypothesis about confounding, not an estimated decomposition of those shocks. I examine it by adding fixed 2007 distance-bin × quarter and one-coupon-share-bin × quarter effects. Distance bins have boundaries at 750, 1,500, and 2,000 miles. Share bins are below 10%, 10% to below 50%, 50% to below 90%, and at least 90%. No post-merger composition variables enter these controls.

The common-support comparison retains only joint cells with at least three treated and three comparison routes, then uses joint-cell × quarter effects. It leaves 133 treated and 35 comparison routes. One-coupon shares become much closer, but mean distance, traffic, and carrier structure are not exactly balanced. This restriction targets a narrower population; it does not recover the full-sample treatment effect.

I also relax the legacy-participation requirement while retaining zero observed DL/NW exposure in 2007. With valid distance data, this expands the comparison to 460 routes. These routes offer a useful alternative but may differ in business model and may still experience network spillovers. All these specifications were recorded before examining the new coefficients; none was selected for passing a pre-trend test.


### 5  Fare changes after accounting for composition

The primary specification compares the fixed legacy sample while allowing baseline market types to have distinct quarterly fare paths. The unadjusted model and distance-only adjustment provide a stepwise benchmark:

log(fare_rt) = α_r + λ_t + β(Overlap_r × Post_t) + γ_distance(r),t + η_share(r),t + ε_rt. (2)

Post begins in 2008Q4. Standard errors are clustered by route, with a finite-sample adjustment and a t reference distribution. Table 3 reports 100[exp(β)-1] and transformed 95% intervals. These are conventional sampling intervals conditional on each design, not bounds on confounding.

Table 3: Primary fixed-sample comparison
| Specification | Change % | 95% interval |
| --- | --- | --- |
| Unadjusted benchmark | -5.58 | [-9.05%, -1.99%] |
| Distance by quarter | -3.68 | [-7.18%, -0.05%] |
| Primary: distance and composition | -2.45 | [-5.92%, 1.14%] |
All three rows use the same 156 overlap and 104 comparison routes, 6,235 observed route-quarters, passenger-weighted market fares, and equal regression weights. Percentages are 100[exp(β)-1]; intervals use route-clustered standard errors. The distance-and-composition model is the primary diagnostic specification.

On identical observations, the unadjusted estimate is -5.58%. Distance-specific quarterly effects reduce its magnitude to -3.68%; adding baseline service-composition effects yields -2.45%, with a 95% interval of [-5.92%, 1.14%]. Restricting the comparison to common-support cells yields -1.80%. Thus the original estimate is not invariant to controls motivated by the observed imbalance.

The expanded comparison is a secondary population check, not another version of the same target: it adds 356 routes and gives -4.43%, or -4.95% after its own common-support restriction. Southwest is present in 54% of the added routes, compared with 29% of the valid-distance legacy controls. Its mean share of journeys recording WN in either carrier field is 45% versus 13%. These baseline differences motivate a specific follow-up rather than a preference for whichever coefficient is smaller.

Table 4: Baseline Southwest composition and comparison-set sensitivity
| Comparison | Composition adjusted | Add WN presence by quarter | Add WN-share bin by quarter |
| --- | --- | --- | --- |
| Legacy | -2.45% [-5.92%, 1.14%] | -2.70% [-6.00%, 0.72%] | -1.63% [-5.21%, 2.09%] |
| Expanded | -4.43% [-6.72%, -2.09%] | -2.55% [-4.99%, -0.06%] | 0.82% [-2.34%, 4.08%] |
Each cell reports the relative change and 95% interval. Legacy uses 156/104 treated/comparison routes; expanded uses 156/460. All models include distance- and itinerary-composition-bin × quarter effects. Additional interactions use 2007 WN presence or any-WN journey-share groups of zero, above zero but below 50%, and at least 50%. These follow-up checks were added after inspecting the initial comparison-set discrepancy.

With baseline WN-presence × quarter effects, the legacy and expanded estimates are -2.70% and -2.55%. This narrowing supports carrier mix as a relevant dimension of the comparison, without identifying a causal Southwest channel. The share-group version yields -1.63% and +0.82%, showing that presence alone does not resolve the sensitivity. Only two treated routes have WN shares of at least 50%, so that specification also has weak overlap in carrier composition. All versions are retained; baseline groups are fixed and no post-merger carrier shares enter the controls.


### 6  Dynamics and the adequacy of the comparison

The event regressions replace the single post interaction with quarterly overlap interactions. Figure 1 uses 2007Q4 as the reference, before the April 2008 announcement. The two panels share the same 260-route sample, which isolates the effect of adding baseline composition controls.

![Figure 1: Event-study contrasts before and after composition adjustment](../results/event_comparison.png)
Points and bars show relative log-fare contrasts and pointwise 95% route-clustered intervals. The open point is the normalized 2007Q4 reference, not an estimated zero-variance observation. Shading covers 2008Q2-2008Q4; the dashed line marks the completion quarter. The coefficients describe the changing overlap-comparison gap relative to the reference, not each group's absolute fare level.

Composition adjustment changes the path, but does not remove the earlier differences. A joint test of the eleven 2005Q1-2007Q3 coefficients gives F = 7.95 without the additional controls and F = 4.32 with them; both p-values are below 0.001. The common-support event model also rejects equality of the pre-reference contrasts (p = 0.00039). These are diagnostics from full-window event regressions, not separate tests estimated only on pre-merger observations.

I respond to the remaining pre-period differences with the relative-magnitude sensitivity framework of Rambachan and Roth (2023), using their official HonestDiD implementation. The target is the average of the nine completion-and-later event coefficients, 2008Q4-2010Q4; this is a different estimand from the pooled coefficient in Table 3. The counterfactual gap may change each post-reference quarter by at most M times its largest pre-reference quarterly change. The 2008Q1-2008Q3 coefficients remain in the vector with zero target weight, allowing for announcement-period effects.

At M=0.5, the approximate 95% robust interval is [-34.4%, 42.0%]. Even a restriction limiting later quarterly deviations to half the largest earlier deviation leaves the sign unresolved. This is an informative limit on the design: over a long post period, small differential changes can accumulate. It also shows why the narrow conventional interval cannot be treated as the full uncertainty about the merger. The supplement reports M=0, 0.5, 1, and 2, the complete covariance matrix, target weights, and inversion-grid checks. The exercises diagnose and quantify sensitivity rather than select a model by whether its pre-test passes (Roth, 2022).


### 7  Carrier responses and competitive exposure

The operating-code records also permit a within-route pricing comparison. I separately aggregate single-carrier DL/NW journeys and other single-carrier journeys, leaving mixed-carrier records in their own category. Here "rival" is shorthand for other recorded codes, without assigning parent affiliations. Of the 156 overlap routes, 144 have both fare series in all four 2007 quarters. For each observed paired quarter, the outcome is log(DL/NW mean fare) minus log(other-carrier mean fare); route and quarter effects summarize its evolution.

The DL/NW-to-rival fare ratio rises by 1.57% in 2009-2010 relative to 2007, with a 95% interval of [-0.70%, 3.89%]. Keeping only the 133 routes paired in all 24 quarters gives 0.97% [-1.18%, 3.18%]; restricting to two-coupon journeys gives a similarly imprecise increase. Thus the market-average decline does not mean that the merging carriers cut fares more than rivals. The within-route gap falls around completion and then rebounds, against an already declining pre-merger gap. These comparisons hold the airport pair fixed but still mix passenger and itinerary types; rival fares are another outcome, not an untreated counterfactual. Full paths, mixed-carrier coverage, and sample counts appear in the supplement.

The concentration diagnostic gives no precise exposure gradient: the coefficient is 0.10% per 100 points of the frozen-share proxy 20,000 × s_DL × s_NW, with interval [-0.28%, 0.47%]. The high-low difference has p=0.157. The shares use all route passengers; mixed itineraries and regional affiliations prevent treating this operating-code proxy as full firm-level ΔHHI. Conditional concentration measures and all exposure models are reported in the supplement.

Checks ending in 2009 and starting in 2006 address the timing of United-Continental and America West-US Airways, respectively. Their adjusted estimates are -2.72% and -2.99%, both with intervals including zero. A stricter screen removing every route with baseline UA or CO presence leaves only six treated routes. Table A4 reports these time-window checks and route-trend sensitivities together.

### 8  Economic interpretation

The strongest result is the role of market and carrier composition. On fixed routes, adjustment reduces the apparent decline by about 3.1 percentage points; accounting for baseline Southwest presence also substantially narrows the gap between the legacy and expanded comparisons. The primary estimate is a modest, imprecise relative decline. The carrier-group comparison adds a different result: the merging carriers' fares do not clearly fall relative to rival fares on the same routes. Together these findings favor an economic account that distinguishes aggregate market changes from relative carrier pricing.

The market-level event path falls around completion, rebounds during 2009, and fluctuates thereafter; the carrier-group gap also rebounds. Neither establishes a gradual coordinated price increase. That pattern is descriptive evidence about the pricing path, not a test of KMMS's buyer-resistance mechanism. The aggregate data contain neither buyer identities nor procurement and supplier-qualification decisions. A direct mechanism test would require those variables. Ticketing-carrier affiliations, verified nonstop schedules, capacity, and entry data would also sharpen the interpretation of the carrier-level fare comparisons.


### References

Borenstein, Severin. 1990. "Airline Mergers, Airport Dominance, and Market Power." American Economic Review 80(2): 400-404. [Author-hosted article](https://faculty.haas.berkeley.edu/borenste/download/AERPP90AirMerge.pdf).

Borenstein, Severin. n.d. "Description of Market Data Files Created by Severin Borenstein." [Data documentation](https://faculty.haas.berkeley.edu/borenste/mktdata.htm).

Carlton, Dennis, Mark Israel, Ian MacSwain, and Eugene Orlov. 2019. "Are Legacy Airline Mergers Pro- or Anti-Competitive? Evidence from Recent U.S. Airline Mergers." International Journal of Industrial Organization 62: 58-95. [doi:10.1016/j.ijindorg.2017.12.002](https://doi.org/10.1016/j.ijindorg.2017.12.002).

Delta Air Lines. 2008a. "Delta Air Lines, Northwest Airlines Combining To Create America's Premier Global Airline." April 14. [Company announcement](https://ir.delta.com/news/news-details/2008/Delta-Air-Lines-Northwest-Airlines-Combining-To-Create-Americas-Premier-Global-Airline/default.aspx).

Delta Air Lines. 2008b. "Delta and Northwest Merge, Creating Premier Global Airline." October 29. [Company announcement](https://ir.delta.com/news/news-details/2008/Delta-and-Northwest-Merge-Creating-Premier-Global-Airline/default.aspx).

Kim, E. Han, and Vijay Singal. 1993. "Mergers and Market Power: Evidence from the Airline Industry." American Economic Review 83(3): 549-569. [Journal article](https://www.jstor.org/stable/2117533).

Kumar, Vikram, Robert C. Marshall, Leslie M. Marx, and Lily Samkharadze. 2015. "Buyer Resistance for Cartel versus Merger." International Journal of Industrial Organization 39: 71-80. [doi:10.1016/j.ijindorg.2015.02.002](https://doi.org/10.1016/j.ijindorg.2015.02.002).

Luo, Dan. 2014. "The Price Effects of the Delta/Northwest Airline Merger." Review of Industrial Organization 44(1): 27-48. [doi:10.1007/s11151-013-9380-1](https://doi.org/10.1007/s11151-013-9380-1).

National Bureau of Economic Research. n.d. "Department of Transportation DB1A/DB1B." Borenstein market-data archive. [doi:10.60592/tb1p-9p78](https://doi.org/10.60592/tb1p-9p78).

Rambachan, Ashesh, and Jonathan Roth. 2023. "A More Credible Approach to Parallel Trends." Review of Economic Studies 90(5): 2555-2591. [doi:10.1093/restud/rdad018](https://doi.org/10.1093/restud/rdad018).

Roth, Jonathan. 2022. "Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends." American Economic Review: Insights 4(3): 305-322. [doi:10.1257/aeri.20210236](https://doi.org/10.1257/aeri.20210236).

United Airlines. 2010. Merger announcement, May 3, and closing Form 8-K, October 1. [Announcement](https://ir.united.com/static-files/69c1f868-c861-48c0-8ada-6cda772720ee); [closing filing](https://ir.united.com/static-files/0d639e33-8958-47c8-bab7-089db8e87ea9).

U.S. Department of Justice. 2008. "Statement of the Department of Justice's Antitrust Division on Its Decision to Close Its Investigation of the Merger of Delta Air Lines Inc. and Northwest Airlines Corporation." October 29. [Closing statement](https://www.justice.gov/archive/opa/pr/2008/October/08-at-963.html).

US Airways Group, Inc., and America West Airlines, Inc. 2005. Form 10-Q, Note 1: merger completed September 27, 2005. [SEC filing](https://www.sec.gov/Archives/edgar/data/706270/000095015305002835/p7141401e10vq.htm).

### Replication and acknowledgment

Code, data access, full results, and technical details are available in the accompanying supplement and [replication repository](https://github.com/adoraxuangechen/airline-merger-fare-analysis).

I thank Robert C. Marshall for his instruction in ECON 449, which motivated this project. Of course, all errors are my own.
