# Assessing Fare Changes After the Delta–Northwest Merger
## Evidence and Limits
@byline Xuange (Adora) Chen · September 2026

### 1 The question and the finding

Fares on routes with substantial observed Delta–Northwest overlap fell relative to fares on a specified group of comparison routes after the merger. In a panel covering 2005–2010, the estimated relative change is -5.72%, with a conventional 95% confidence interval of [-9.16%, -2.15%]. The comparison, however, also reveals differences before the merger, including before its public announcement. I therefore interpret the estimate as a descriptive difference in fare changes. The evidence does not establish that the merger caused fares to fall.

The Delta–Northwest transaction presents a useful setting for examining these issues. The airlines announced their agreement on April 14, 2008, and completed the merger on October 29, 2008 (Delta Air Lines, 2008a, 2008b). I use 2008Q4 as the completion quarter and classify routes using 2007 service. This timing keeps the main classification before the public announcement, although it cannot rule out every form of earlier anticipation.

There are competing economic reasons for fares to change. Combining two suppliers can reduce independent competition on a route. Combining networks can also improve connections or lower operating costs. Changes in schedules, capacity, and service quality affect both passengers’ willingness to pay and the fares observed in a ticket sample. These channels can operate simultaneously and can differ between routes with mainly connecting service and routes with mainly one-coupon service.

This note relates to the literature on retrospective airline-merger evaluation. Luo (2014) reports limited fare increases on Delta–Northwest overlap airport pairs, while Remer and Orchinik (2026) highlight the importance of pre-merger fare trends and price effects extending beyond overlap routes. These studies motivate the present focus on transparent fare measurement, explicit exposure definitions, and diagnostic checks of the comparison group.

I ask how average fares changed on airport pairs with material observed service by both carriers, relative to explicitly defined comparison airport pairs. I reconstruct fares from aggregated records, fix route classifications using a stated pre-announcement rule, and examine the comparison against the pre-merger evidence. The contribution is an auditable assessment of measurement and comparison design: each result can be traced to its fare measure, route population, and estimating equation.

@page

### 2 What the data measure

The analysis begins with a supplied extract containing 4,175,354 records and 11 fields for 2005Q1–2010Q4. I verified its airport and numeric fields against the corresponding NBER archive of Borenstein’s broadened-market data; float differences are limited to text-export precision (Borenstein, n.d.; NBER, n.d.). The underlying survey samples tickets, but this extract is already aggregated. One row describes a carrier set, an unordered airport pair, a quarter, and a one- or two-coupon itinerary category. It is not an individual ticket, flight, or traveler.

The airport pair is the unit I follow over time. Travel directions have been combined, so ATL–MEM and MEM–ATL are not separate markets. The carrier fields identify observed operating codes without preserving segment order. A one-coupon record is distinguished from a two-coupon record; I do not equate the former with a verified nonstop flight. Both categories enter the airport-pair fare measure.

For each airport pair and quarter, I multiply each record’s mean fare, avprc, by the number of sampled passengers it represents, pax. I sum these products and divide by the total pax. This recovers a passenger-weighted mean of the fares represented in the extract. An unweighted average of avprc would instead give a record representing one passenger the same influence as a record representing thousands. I take the natural logarithm of the resulting market mean for estimation.

@table sample
@caption Table 1. Construction of the analysis sample. Counts refer to this extract, not the full population of domestic journeys. Group definitions are stated on the next page.

The cleaning removes four records whose two airports are identical. Required numeric fields contain no missing values, and all supplied fares and passenger counts are positive. Natural record keys are unique. The archive comparison identifies 42 carrier-code entries lost during an earlier export; these rows remain in fare totals, and none contributes to the main sample’s 2007 classification. No new fare trimming, winsorization, carrier-family imputation, or replacement of missing market quarters is applied.

Fares are nominal one-way-equivalent dollars. A common quarterly deflator would subtract the same constant from every log fare in a quarter, which quarter fixed effects absorb. This does not remove route-specific responses to fuel prices or the recession. The extract also lacks within-record fare variances: dispersion across its mean fares cannot recover dispersion across individual tickets. I therefore analyze average fares only. The technical supplement documents cleaning, source verification, and estimation in detail.

@page

### 3 Choosing the comparison

The main definition uses 2007, the last complete calendar year before the public announcement. A route is eligible if it has at least 100 sampled passenger journeys in each quarter of that year. A carrier’s single-carrier service comprises one-coupon records under its own operating code and two-coupon records for which both operating codes equal that carrier. Its share is measured against all sampled passengers on the airport pair, including mixed-carrier journeys.

An overlap route must have Delta and Northwest single-carrier shares of at least 5% in the same quarter in at least three of the four quarters of 2007. This rule selects 156 routes. The comparison group contains 105 eligible routes with no observed DL or NW code in either carrier field during 2007 and a combined single-carrier share of at least 5% for AA, AS, CO, UA, US, or HP in at least three quarters. Routes outside these groups are excluded from the main contrast.

The thresholds make the rule reproducible and reduce reliance on isolated small cells. They are analysis choices, not regulatory market definitions or evidence that assignment is exogenous. A mixed DL–NW record alone does not establish two independent services. Overlap includes connecting journeys; it does not mean that both carriers operated nonstop flights. Regional partners are not assigned to parent airlines without a dated affiliation crosswalk.

@table balance
@caption Table 2. Route characteristics in 2007. Each characteristic is averaged across quarters within a route, then equally across routes. One-coupon share uses sampled passengers. Distance uses the supplied field, including one comparison route with a recorded zero; that value is not a physical distance estimate.

The groups differ substantially. The overlap routes are longer and have much less one-coupon service. Route fixed effects remove persistent differences in levels, but cannot remove different changes caused by these characteristics. For example, fuel-price changes may have different implications for long connecting journeys and short one-coupon journeys. Demand shocks may also differ across the airports and travelers represented in each group.

Regional affiliations, competition through nearby airports, or network-wide changes may also transmit merger effects to comparison routes with no observed DL or NW code. I therefore assess the comparison using its pre-period behavior rather than assuming that legacy-airline service makes the groups comparable.

@page

### 4 Estimation and the average fare contrast

I estimate a difference-in-differences regression with an airport-pair fixed effect, a calendar-quarter fixed effect, and an interaction between the overlap indicator and a post-completion indicator. The post period begins in 2008Q4. The outcome is the log of the passenger-weighted airport-pair fare. Every observed route-quarter receives equal regression weight in the baseline. Weighting passengers when constructing a fare and weighting routes when estimating a regression answer different questions.

@equation

Here, T identifies overlap routes and Post identifies 2008Q4–2010Q4. The coefficient β summarizes their relative change after controlling for fixed route attributes and common quarterly shocks. I report 100[exp(β) − 1] to express the log coefficient as a percentage contrast. It is not an estimate of the percentage change in every traveler’s fare or an aggregate consumer-welfare measure.

@table regression
@caption Table 3. Fare contrasts under the main route definition. All rows use passenger-weighted fares and route and quarter fixed effects. Standard errors cluster by airport pair; intervals use a t reference distribution with G − 1 degrees of freedom. N is the number of observed route-quarters. Fixed passenger weights use each route’s average 2007 pax. The replication files retain the results for each stated specification.

The baseline coefficient is -0.0589, with a route-clustered standard error of 0.0189. Its -5.72% contrast is reasonably similar when the panel is restricted to routes observed in all 24 quarters or when the announcement-through-completion quarters are omitted. These checks establish numerical stability within this route definition; the event study next examines the comparison over time.

Using fixed 2007 passenger counts as regression weights yields -10.73%, giving more influence to larger routes. This is a different weighted average, not a correction that invalidates equal route weights. Removing 2008Q3–2009Q4 also changes the periods being compared; the resulting -6.18% contrast cannot be interpreted as an effect insulated from the recession. Route clustering allows within-route dependence but not unrestricted dependence across routes sharing airports or networks. The reported intervals quantify model-based sampling uncertainty, not comparison-group bias.

@page

### 5 What the event study reveals

The event study replaces the pooled interaction with separate overlap-by-quarter interactions over all 24 quarters. I omit 2008Q3 and include route and quarter fixed effects. Each point therefore compares the change in the overlap–comparison log-fare gap with that reference quarter. The reference quarter follows the public announcement, so it cannot automatically be treated as unaffected by the merger process.

@figure event_study.png
@caption Figure 1. Quarterly relative log-fare contrasts. Bars are pointwise 95% route-clustered confidence intervals, not simultaneous bands. The hollow marker is the normalized 2008Q3 reference. Shading spans announcement through completion; the dashed line marks 2008Q4. These coefficients describe relative fare paths, not a causal response to completion.

The pre-completion coefficients are jointly different from zero: F(14, 260) = 8.925, p < 0.001. To check whether this concern comes only from announcement-period behavior, I re-estimate the dynamic comparison using 2005–2007 alone, with 2007Q4 as the reference. That test also rejects: F(11, 260) = 7.456, p < 0.001. The comparison problem is visible before the public announcement. These tests detect changing relative gaps, which may include group-specific seasonality rather than a smooth divergent trend.

A pre-period test cannot prove the unobserved post-merger counterfactual, and a failure to reject would not establish parallel trends (Roth, 2022). Here the observed rejection, together with the differences in route characteristics, weakens a causal reading of the pooled estimate. Adding fixed effects does not supply the missing counterfactual.

The hollow zero at 2008Q3 is a normalization, not an estimated zero effect or a missing observation. The neighboring points need not connect smoothly to it. Each point is measured relative to that single quarter, whereas the pooled coefficient summarizes a broader before-and-after comparison. Their magnitudes therefore need not coincide.

@page

### 6 How far the result travels

Broader definitions admit routes with thinner or less sustained observed exposure. Table 4 summarizes how both the population and the fare contrast change.

@table definitions
@caption Table 4. Sensitivity to route definitions. Change is 100[exp(β) − 1]. All rows use passenger-weighted fares, equal route-quarter regression weights, and route and quarter fixed effects. Counts and coefficients come from the same reproducible estimation pipeline.

The 2007 any-code rule requires each merging carrier to appear at least once in either field during 2007, retaining the 100-passenger requirement in each quarter. Its controls are other eligible routes with positive single-carrier traffic from the stated legacy group and may include one merging carrier. Broad pre-completion rules use appearances through 2008Q3 and require at least four observed quarters anywhere in 2005–2010. Their exposure window includes post-announcement information, and eligibility can depend on later observation availability. The supplement states every rule precisely.

The sign changes concern different populations and comparisons, rather than alternative estimates of one fixed population effect. They make the result’s scope consequential for an assessment: a conclusion about material observed overlap cannot automatically be extended to every route that ever carries either airline’s code.

Two extensions would most improve the analysis. First, dated regional-carrier affiliations and ticket or coupon records would distinguish independent services and separate changes in itinerary composition from changes in comparable fares. Second, a longer pre-announcement panel, with evidence of common support in traffic, distance, itinerary type, and airport exposure, would help evaluate a more credible comparison. Matching on the available 2007 characteristics alone does not remove the pre-period differences, as the supplement shows. Capacity, schedules, service quality, and a demand framework would additionally be needed to assess mechanisms or consumer welfare.

@page

### 7 Judgment

For the main observed-code overlap sample, the post-completion relative fare change is -5.72%. Its stability under narrow checks supports a descriptive finding, while the pre-period evidence and the population changes in Table 4 prevent a general causal claim. The analysis does not establish merger-induced fare savings, tacit coordination, or a welfare effect.

For a merger assessment, the immediate priority is to improve the service definition and the counterfactual comparison. This project provides an auditable starting point: documented data construction, explicit route rules, verified estimates, and a clear distinction between a measured contrast and an attributed effect.

### References

Borenstein, Severin. n.d. Description of “Market Data” Files Created by Severin Borenstein. Variable definitions and construction of broadened airline markets. https://faculty.haas.berkeley.edu/borenste/mktdata.htm

Delta Air Lines. 2008a. Delta Air Lines, Northwest Airlines Combining To Create America’s Premier Global Airline. April 14. https://ir.delta.com/news/news-details/2008/Delta-Air-Lines-Northwest-Airlines-Combining-To-Create-Americas-Premier-Global-Airline/default.aspx

Delta Air Lines. 2008b. Delta and Northwest Merge, Creating Premier Global Airline. October 29. https://ir.delta.com/news/news-details/2008/Delta-and-Northwest-Merge-Creating-Premier-Global-Airline/default.aspx

Luo, Dan. 2014. The Price Effects of the Delta/Northwest Airline Merger. Review of Industrial Organization 44 (1): 27–48. https://doi.org/10.1007/s11151-013-9380-1

National Bureau of Economic Research. n.d. Department of Transportation DB1A/DB1B. Borenstein refined market files. https://doi.org/10.60592/tb1p-9p78

Remer, Marc, and Reed Orchinik. 2026. Multimarket Contact and Prices: Evidence From an Airline Merger Wave. MIT Sloan Research Paper 7158-24, June 4 version. https://doi.org/10.2139/ssrn.4919118

Roth, Jonathan. 2022. Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends. American Economic Review: Insights 4 (3): 305–322. https://doi.org/10.1257/aeri.20210236

@caption Online documentation accessed September 21, 2026. The accompanying replication files contain the input fingerprint, exact sample rules, regression outputs, and a separate reconciliation of earlier versions.
