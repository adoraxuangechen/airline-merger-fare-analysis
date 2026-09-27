# Delta-Northwest Fare Analysis
## Technical Supplement: Measurement, Estimation, and Replication
Xuange (Adora) Chen
The Pennsylvania State University
xmc5171@psu.edu
Revised September 27, 2026

### A  Source data and units

The primary input is the NBER archive mktdata79q1to16q3.zip, containing Borenstein's broadened-market Stata file. This revision selects 2005-2010 directly from that archive. The original user-supplied CSV and previous published outputs are preserved separately. The analysis does not substitute BTS ticket-level records for this aggregate panel.

Source SHA256: 75b2fe06890bf54f3466824e0309e3d52a74c3dfc3b22f940000face130ecfa9

The source ZIP contains 19,436,121 records over its full historical coverage. The six selected years contain 4,175,354 records and 11 fields. Borenstein's documentation describes domestic-ticket, fare, cabin, and itinerary screens applied upstream, including splitting round trips into one-way observations. This study adopts those archived aggregates; it does not claim an independent reconstruction of every upstream ticket restriction.

Table A1: Input dictionary
| Field | Meaning |
| --- | --- |
| yr, qtr | Calendar year and quarter. |
| ap1, ap2 | Alphabetically ordered airport pair; directions combined. |
| cr1, cr2 | Alphabetically ordered operating-carrier set; blank cr2 on one-coupon records. |
| cop | 0: one coupon; 1: two coupons. |
| pax | Sampled journeys represented by the cell. |
| avprc | Cell average one-way-equivalent fare, nominal dollars. |
| nsdst | Airport-pair distance; zero treated as a sentinel. |
| avdst | Mean routing distance; not a baseline control. |
Operating-carrier order within the itinerary is not retained. The source documentation's carrier fields cannot reconstruct ticketing carriers or historical regional affiliations.

The natural key is cr1, cr2, yr, qtr, cop, ap1, ap2. Both exact records and natural keys are unique. Airport pairs are already ordered alphabetically. A blank cr2 on a one-coupon record is expected. Carrier code NA is a literal recorded code, not the default missing-value token. The new CSV reader therefore disables automatic conversion of that string to missing.

The earlier CSV matches the source in row order, airport labels, integer-valued fields, and numerical values within export precision (maximum difference below 5.01 × 10^-12). It contains 42 blank carrier entries corresponding to literal NA in the archive, across 34 rows. This revision restores those values by reading the source, without overwriting the earlier CSV or guessing affiliations. The restoration leaves the previous main route set and market fares numerically unchanged. The full field-by-field reconciliation remains in provenance/.


### B  Cleaning and construction

The calendar restriction keeps 2005Q1-2010Q4. Four records with identical airport endpoints are excluded. No further records fail the positive, finite passenger/fare requirements. No duplicates are dropped, no fares are winsorized, and missing quarters are not filled. The result is 4,175,350 records, 609,396 route-quarters, and 229,384,433 sampled journeys. Counts represent the archived sample and are not multiplied by ten.

The numerator named revenue in the code is pax × avprc, summed within a route-quarter. It is an arithmetic quantity for reconstructing mean fares, not measured airline revenue. The denominator sums pax. Assertions verify conservation of both quantities and uniqueness of route-quarter keys. The dependent variable is log(sum(pax × avprc) / sum(pax)).

For DL, NW, and other individual codes, single-carrier journeys are records with cop=0 or records with identical cr1 and cr2. For cop=0, cr1 supplies the code. All route passengers, including mixed-carrier itineraries, enter the DL/NW treatment-share denominator. Any-code presence separately checks both carrier fields. These concepts are not interchangeable.

The 2007 eligibility threshold is at least 100 sampled journeys in all four quarters, yielding 5,535 eligible routes. Treatment requires both single-carrier DL and NW shares to be at least 5% in the same quarter in at least three quarters. The legacy comparison requires zero DL/NW presence in either field throughout 2007 and at least 5% combined AA/AS/CO/UA/US/HP single-carrier traffic in at least three quarters. This selects 156 treated and 105 comparison routes.

The baseline includes every observed quarter for those routes: 6,259 cells. SJU-STT has a zero source distance, interpreted as a sentinel rather than physical distance. Distance models omit that route, leaving 6,235 cells and 260 routes. Labels, distance bins, and composition bins are fixed before the merger; no post-period service or traffic variable determines the main classification.

Relaxing the legacy requirement admits every eligible route with no observed DL or NW in 2007. There are 469 such candidate routes, of which 460 have positive baseline distance. With the same 156 treated routes, the expanded distance sample has 616 routes. Southwest appears in 222 of these 460 comparisons, versus 30 of the original 105. These are any-WN presence counts, not a definition of low-cost-carrier dominance.

Table A2: Common-support restrictions
| Population | Treated | Comparison | Quarters |
| --- | --- | --- | --- |
| Legacy; valid distance | 156 | 104 | 6,235 |
| Legacy common support | 133 | 35 | 4,032 |
| All unexposed; valid distance | 156 | 460 | 14,430 |
| All unexposed common support | 146 | 178 | 7,774 |
Joint cells use four baseline distance bins and four baseline one-coupon-share bins. A cell is retained only if it contains at least three routes in each group. Counts are based solely on 2007 features and group membership. Detailed cell counts are saved as CSVs.


### C  Estimating equations and inference

The unadjusted model uses route and quarter fixed effects. Distance adjustment adds distance-bin × quarter effects; the full adjustment also adds baseline one-coupon-share-bin × quarter effects. The common-support model instead adds joint-cell × quarter effects. Because route-invariant baseline characteristics are absorbed by route effects, the added terms allow their associations with fares to vary over time.

Distance bins are [0,750), [750,1500), [1500,2000), and [2000,infinity), with zero sentinels excluded first. One-coupon-share bins are [0,.1), [.1,.5), [.5,.9), and [.9,1]. The estimator drops mathematically redundant nuisance columns through pivoted QR decomposition; it verifies that the treatment regressors remain identified. Unidentified target terms are errors, not silently pseudoinverted coefficients.

The implementation subtracts each route's mean from the outcome and every regressor, then removes the nuisance-regressor projection from the target regressors and outcome (Frisch-Waugh-Lovell). Let X denote the residualized target matrix and u the resulting residuals. Route score g is sum_r(X_ru_r) over observations belonging to that route. The sandwich covariance uses the outer products of these route scores, multiplied by G/(G-1) × (N-1)/(N-G-rank(Z)-K). Here G is the number of routes, Z the within-transformed nuisance matrix, and K the number of target terms. Two-sided intervals and p-values use t(G-1).

This covariance permits heteroskedasticity and serial dependence within routes. It does not account for unrestricted dependence across routes sharing airports, carriers, or networks. The resulting intervals summarize sampling uncertainty under that clustering assumption and do not measure bias from nonparallel trends or spillovers.

The event study includes overlap × quarter indicators for all observed quarters except 2007Q4. The joint pre-period test concerns the eleven 2005Q1-2007Q3 coefficients from this full-window regression. The pointwise intervals are not simultaneous confidence bands. Tests are used to diagnose comparisons, not to select a specification with an acceptable p-value (Roth, 2022).

The route-trend sensitivity adds a separate linear time slope for every route to the pooled post regression. It imposes a stronger functional-form assumption and can absorb gradual merger responses. It is not combined with the saturated event model: unrestricted route trends and a saturated relative event path require additional normalizations for identification.

Two independent checks are included. The production script verifies adjusted, event, and trend coefficients and CR1 standard errors on an actual-data subset against explicit dummy regressions. A separate checker reconstructs the raw full-sample dummy designs without importing the production estimator, covering seven models. Its largest coefficient discrepancy is below 8 × 10^-13 and largest standard-error discrepancy below 2 × 10^-14. Verification establishes computational agreement, not causal identification.


### D  Concentration: denominators and economic interpretation

For each route, 2007 passenger counts are pooled across quarters. Let P be total route passengers, p_j single-carrier passengers recorded under code j, and S=sum_j p_j. The coverage statistic is S/P. A mixed-carrier journey is not arbitrarily allocated to an airline; regional codes are not assigned to a parent without a dated affiliation rule.

The conditional single-carrier index is H_single = 10,000 × sum_j(p_j/S)^2. All recorded single-carrier codes enter the sum. This is concentration among the single-carrier subset, not concentration in the whole economically defined airline market. Nineteen eligible routes have S=0, so the conditional index is missing rather than zero. None is in the 261-route baseline; two occur in the expanded common-support controls. Any reported mean for that latter index excludes these two and should be labeled accordingly.

The principal exposure diagnostic uses shares s_DL=p_DL/P and s_NW=p_NW/P, with the all-passenger denominator. Define D=20,000 × s_DL × s_NW. This is the arithmetic increase in the observed single-carrier squared-share component if the two recorded codes are combined while everything else is fixed. It is not the change in H_single, because H_single uses S as denominator. The saved alternative delta_conditional uses S consistently. Neither construction identifies true firm-level HHI in the presence of mixed itineraries and regional affiliations.

The baseline treated routes have mean D=428.28 and median D=312.45. The high/low split is that treated-route median, producing 78 routes in each group. A continuous model interacts D/100 with Post. A further supplementary model includes a binary overlap interaction and a centered within-treated D/100 interaction, distinguishing a mean overlap contrast from the linear exposure gradient. The registry retains both specifications; Table A3 reports the simple continuous diagnostic and the high/low comparison.

Table A3: Exposure models with baseline distance- and share-bin × quarter effects
| Model / term | β | SE | Change % [95% interval] |
| --- | --- | --- | --- |
| Lower exposure | -0.03872 | 0.02110 | -3.80 [-7.71%, 0.28%] |
| Higher exposure | -0.01348 | 0.02015 | -1.34 [-5.18%, 2.66%] |
| Continuous: per 100 proxy points | 0.00098 | 0.00190 | 0.10 [-0.28%, 0.47%] |
| Binary overlap; centered dose | -0.02750 | 0.01889 | -2.71 [-6.27%, 0.98%] |
| Within-overlap: per 100 | 0.00352 | 0.00224 | 0.35 [-0.09%, 0.80%] |
Percentages transform each log coefficient. Per-100 terms describe a change of 100 proxy points, conditional on the fitted linear specification. The high-minus-low test has p=0.157 and is calculated using the full covariance between the two coefficients.

Applying the same 5%-in-three-quarters rule to one-coupon DL and NW shares identifies only ATL-DTW, ATL-MEM, ATL-MSP, and HNL-SFO. The looser annual requirement of at least 100 one-coupon passengers under each carrier gives five routes, adding LGA-PHX, but does not impose sustained contemporaneous overlap. Neither rule verifies physical nonstop service. A standalone four-route subgroup regression would add little dependable evidence and is not reported as a principal result.


### E  Full pooled specification registry

All models below were run on the same primary Borenstein data. Baseline fare construction stays fixed. Additional controls, time windows, route populations, and sample sizes are reported so that estimates with different targets are not averaged together.

Table A4: Complete pooled-model results
| Specification | β (SE) | Change % [95% interval] | N |
| --- | --- | --- | --- |
| Initial comparison | -0.0589 (0.0189) | -5.72 [-9.16%, -2.15%] | 6,259 |
| Same sample; valid distance | -0.0574 (0.0190) | -5.58 [-9.05%, -1.99%] | 6,235 |
| Distance × quarter | -0.0375 (0.0188) | -3.68 [-7.18%, -0.05%] | 6,235 |
| Distance + composition × quarter | -0.0248 (0.0184) | -2.45 [-5.92%, 1.14%] | 6,235 |
| Common support; joint-cell × quarter | -0.0181 (0.0205) | -1.80 [-5.69%, 2.26%] | 4,032 |
| All controls; unadjusted | -0.0378 (0.0118) | -3.71 [-5.92%, -1.44%] | 14,430 |
| Broader controls; adjusted | -0.0453 (0.0123) | -4.43 [-6.72%, -2.09%] | 14,430 |
| Broader controls; common support | -0.0508 (0.0126) | -4.95 [-7.28%, -2.56%] | 7,774 |
| End in 2009 | -0.0276 (0.0171) | -2.72 [-5.95%, 0.62%] | 5,196 |
| Start in 2006 | -0.0303 (0.0173) | -2.99 [-6.23%, 0.36%] | 5,199 |
| Exclude 2007 UA/CO presence | -0.1044 (0.0539) | -9.91 [-19.22%, 0.47%] | 936 |
| Add route-specific linear trends | -0.0476 (0.0187) | -4.65 [-8.10%, -1.08%] | 6,235 |
| Omit 2008Q2-2008Q4 | -0.0208 (0.0208) | -2.06 [-5.99%, 2.04%] | 5,455 |
Coefficients are log points; percentage intervals are exponential transformations. N is route-quarters. Unadjusted rows have only route and quarter effects. The distance-only row adds distance-bin × quarter effects. Adjusted and remaining sensitivity rows add both baseline bin sets; support models instead add joint-cell × quarter effects.

The stricter UA/CO exclusion applies to any 2007 presence in either carrier field and to both treatment and comparison groups. It removes 150 of 156 treated routes and leaves six treated plus 33 comparisons. It addresses a broad rival-carrier exposure concern at the cost of substantial loss of coverage. It is not a targeted estimate of UA-CO merger contamination.

The end-2009 check removes the entire year of the United-Continental announcement and closing. Starting in 2006 removes the immediate 2005 America West-US Airways event period but cannot remove all subsequent integration effects. The transition sensitivity omits 2008Q2-2008Q4 and begins its post period in 2009Q1. It was carried over as a supplementary diagnostic, not used to choose the headline specification.

The dated protocol is a design log, not a historical preregistration. Transition-window and within-overlap dose models are supplementary. All estimates are retained; sign, significance, or a favorable pre-test does not establish a causal design.


### F  Event coefficients and pre-period diagnostics

Table A5: Full adjusted event path
| Quarter | Coefficient | SE | 95% interval |
| --- | --- | --- | --- |
| 2005Q1 | -0.0308 | 0.0253 | [-0.0806, +0.0190] |
| 2005Q2 | -0.0352 | 0.0246 | [-0.0837, +0.0133] |
| 2005Q3 | -0.0566 | 0.0274 | [-0.1106, -0.0025] |
| 2005Q4 | +0.0119 | 0.0254 | [-0.0382, +0.0620] |
| 2006Q1 | -0.0373 | 0.0232 | [-0.0830, +0.0085] |
| 2006Q2 | +0.0054 | 0.0216 | [-0.0372, +0.0480] |
| 2006Q3 | +0.0035 | 0.0243 | [-0.0443, +0.0513] |
| 2006Q4 | -0.0177 | 0.0215 | [-0.0601, +0.0247] |
| 2007Q1 | +0.0024 | 0.0178 | [-0.0327, +0.0374] |
| 2007Q2 | +0.0203 | 0.0176 | [-0.0143, +0.0550] |
| 2007Q3 | -0.0206 | 0.0139 | [-0.0480, +0.0068] |
| 2007Q4 | 0 (reference) | - | - |
| 2008Q1 | +0.0300 | 0.0186 | [-0.0067, +0.0666] |
| 2008Q2 | +0.0004 | 0.0182 | [-0.0356, +0.0363] |
| 2008Q3 | -0.0639 | 0.0229 | [-0.1090, -0.0188] |
| 2008Q4 | -0.0933 | 0.0198 | [-0.1323, -0.0543] |
| 2009Q1 | -0.0713 | 0.0232 | [-0.1170, -0.0255] |
| 2009Q2 | -0.0110 | 0.0223 | [-0.0549, +0.0330] |
| 2009Q3 | +0.0009 | 0.0252 | [-0.0487, +0.0506] |
| 2009Q4 | -0.0261 | 0.0210 | [-0.0675, +0.0152] |
| 2010Q1 | -0.0304 | 0.0239 | [-0.0774, +0.0166] |
| 2010Q2 | +0.0005 | 0.0276 | [-0.0538, +0.0548] |
| 2010Q3 | -0.0444 | 0.0277 | [-0.0990, +0.0102] |
| 2010Q4 | -0.0614 | 0.0276 | [-0.1158, -0.0071] |
Reference 2007Q4 is normalized to zero. The dependent variable is the log of the passenger-weighted route-quarter fare; route, quarter, baseline distance-bin × quarter, and baseline composition-bin × quarter effects are included. Intervals are pointwise 95% route-clustered intervals in log points.

Table A6: Tests of all eleven pre-reference coefficients in the full-window event regressions
| Model | F(11,G-1) | p |
| --- | --- | --- |
| Unadjusted | 7.953 | 6.54e-12 |
| Composition adjusted | 4.324 | 6.15e-06 |
| Legacy support | 3.311 | 0.000388 |
| Expanded support | 6.318 | 1.8e-09 |
All comparisons retain evidence of pre-period differences. Smaller F values do not by themselves establish an improved causal design, and nonrejection would not prove parallel trends.


### G  What the earlier versions measured

The new main paper concentrates on economic interpretation and comparison design. This section preserves the reconciliation needed to understand earlier figures, without attributing the change in sign to a single coding correction.

Table A7: Historical sequential bridge
| Sequential change | Change % | Treated | Comparison |
| --- | --- | --- | --- |
| A. Original implementation | +5.13 | 12 | 32,214 |
| B. Correct fixed effects only | +5.02 | 12 | 32,214 |
| C. Passenger-weighted fare | +1.97 | 12 | 32,214 |
| D. 2007 eligibility | +0.48 | 12 | 5,523 |
| E. Empirical overlap | -0.85 | 156 | 5,379 |
| F. Legacy comparison restriction | -5.72 | 156 | 105 |
The original implementation and the first corrected specification use the same observations, fares, and groups. Later rows change fare aggregation, eligibility, and classification. The decomposition is order-dependent; it is not a unique attribution of the difference between two headline numbers.

The original code uses arithmetic means of aggregate-record fares and twelve hand-coded overlap routes. Correcting only its incomplete fixed-effect transformation changes approximately +5.13% to +5.02%, preserving the sign. Further changes in measurement and sample selection lead to the previous -5.72% specification. The new extension starts from that verified -5.72% result and changes the comparison design as documented above.

The original Figure 2 pattern can be reproduced from the supplied code. The original Table B1 coefficients and standard errors do not match the rerun at printed precision, and the code does not export that table. The discrepancy remains a historical provenance limit, not a result used in the current paper. Original audit output is retained in the archive.

The original dispersion calculation measures variation across aggregate cell means. Without within-cell second moments, it cannot recover dispersion across individual ticket fares. It is therefore not used as evidence of coordinated pricing in this revision.

The useful conceptual part of the original paper is the distinction between unilateral pricing incentives, repeated interaction, and network efficiencies. Those mechanisms remain in the main economic framework. A fare comparison alone does not estimate the equilibrium, establish collusion, or measure welfare. Removing those unsupported empirical claims preserves the theory while aligning conclusions with the available evidence.


### H  Original BTS files and replication

The official BTS archive supplies quarterly Market, Coupon, and Ticket ZIPs for every quarter of 2005-2010. The accompanying source manifest lists all 72 URLs. All 24 Market files and the 2007Q1 Coupon and Ticket pilots were retrieved separately, checked for ZIP integrity, and given SHA256 fingerprints. The original files are preserved on disk and omitted from the Git repository because of their size.

Market data retain reporting, ticketing, and operating-carrier fields, coupon counts, itinerary/market identifiers, passenger counts, and prorated market fares. Ticket records contain itinerary-level variables used for screening, including the dollar-credibility field. Coupon records retain segment-level information. A proposed future panel must document joins, fare allocation, mixed-carrier codes, screening, and ticketing/operating-carrier choice. These distinctions are why the raw pilot is not simply appended to Borenstein's aggregates.

The primary analysis can be regenerated from the NBER archive using the source-download script and analysis/extend_analysis.py. The repository README gives exact commands. All chart points and tables are created from saved result files; no numerical result is hand-adjusted. The source extractor preserves NA and emits an archive fingerprint, extracted-file fingerprint, row count, and year range.

Table A8: Current replication files
| Location | Purpose |
| --- | --- |
| analysis/extend_analysis.py | Canonical-source preparation, fixed design sequence, all estimates and plots. |
| analysis/independent_check.py | Independent raw-dummy regression validation. |
| scripts/download_nber.py | Download/check source and extract six years preserving NA. |
| results/model_registry.csv | All pooled and event coefficients, intervals, sample counts. |
| results/route_features.csv | All route classifications and 2007 concentration measures. |
| results/panel_*.csv | Saved analysis panels for each comparison. |
| provenance/ | Source manifests, archive audit, research notes. |
| documents/ | Source text and PDF builder. |
| archive/v1/ | Prior paper, outputs, code and documentation. |
Historical scripts and outputs are stored under archive/v1 rather than serving as the current entry point. Raw-source download manifests and independent checks are kept alongside current documentation.

The verified numerical environment uses Python 3.12, NumPy 2.3.5, pandas 2.2.3, SciPy 1.18.1, statsmodels 0.15.0, and matplotlib 3.11.2. A separate reportlab document build produces the PDFs from the Markdown templates and saved results. File hashes, validation differences, and the dated protocol accompany the delivery.

### Literature verification boundary

The main paper's Borenstein 1990 comparison is based on the author-hosted article. Luo 2014 is cited at the level supported by the publisher's abstract and accessible notes; no unverified exact percentage is assigned to it. Carlton et al. 2019 has different service definitions, windows, weighting, and capacity/traffic information. Kim and Singal 1993, American Economic Review 83(3):549-569, is bibliographically verified and relevant historical context, but its unavailable full text is not used to supply a numerical benchmark. Detailed source notes record these access limits.

References and clickable primary sources appear in the writing sample and in provenance/literature_notes.md. The source documentation is [Borenstein's Market Data description](https://faculty.haas.berkeley.edu/borenste/mktdata.htm), with the [NBER archive](https://www.nber.org/research/data/department-transportation-db1adb1b) and the [BTS ZIP directory](https://transtats.bts.gov/PREZIP/).


### I  Southwest composition and carrier-specific fares

The additional diagnostics were specified in a dated follow-up protocol after the original comparison-set discrepancy was observed. They do not replace the original models. Southwest presence means a positive 2007 journey count with WN in either operating-carrier field. Its share counts each such journey once, including mixed-carrier records, and divides by all route passengers. This is a WN indicator rather than an exhaustive low-cost-carrier classification.

The expanded comparison adds 356 routes to the 104 valid-distance legacy controls. Any-WN presence is 53.9% in the added group and 28.8% in the legacy group; the equal-route mean WN journey shares are 44.7% and 12.6%. The fixed share bins are zero, positive but below 50%, and at least 50%. Only two treated routes fall in the last bin, compared with 17 legacy and 172 added controls. The thin support is a reason to retain the bin sensitivity without labeling it a preferred causal design. All models retain the underlying sample and baseline distance/service-composition controls. Neither specification uses post-merger WN presence or shares.

Table A9: Southwest composition sensitivity
| Comparison | Composition adjusted | Add WN presence by quarter | Add WN-share bin by quarter |
| --- | --- | --- | --- |
| Legacy | -2.45% [-5.92%, 1.14%] | -2.70% [-6.00%, 0.72%] | -1.63% [-5.21%, 2.09%] |
| Expanded | -4.43% [-6.72%, -2.09%] | -2.55% [-4.99%, -0.06%] | 0.82% [-2.34%, 4.08%] |
Each cell gives the relative percentage change and 95% route-clustered interval. These are the same follow-up specifications summarized in the main text. WN-share groups use any recorded WN journey, including mixed-carrier journeys counted once.

For carrier-specific fares, a single-carrier record has cop=0 or identical cr1 and cr2. It belongs to the merging group only when that code is DL or NW. Other single-carrier records form the rival group; mixed records remain separate and are not attributed to either group. Prices are passenger-weighted means within group, route, and quarter. Source passenger counts and fare numerators reconcile to the original route-quarter totals.

The baseline carrier-gap cohort requires positive traffic in both single-carrier groups in every quarter of 2007. Twelve of the original 156 treated routes fail because rival records are unavailable in at least one baseline quarter, leaving 144 routes. Eighteen paired route-quarter cells are unavailable outside the 2007 baseline. A separate complete-24-quarter cohort has 133 routes. The two-coupon-only versions have 142 and 129 routes, respectively. A route-specific availability ledger records every exclusion. No missing fares are filled.

Table A10: Change in the within-route DL/NW-to-rival fare ratio
| Sample | Routes / cells | Change % | 95% interval |
| --- | --- | --- | --- |
| All products; baseline paired | 144 / 3,438 | 1.57 | [-0.70%, 3.89%] |
| All products; complete panel | 133 / 3,192 | 0.97 | [-1.18%, 3.18%] |
| Two coupons; baseline paired | 142 / 3,385 | 1.46 | [-0.77%, 3.75%] |
| Two coupons; complete panel | 129 / 3,096 | 0.76 | [-1.32%, 2.89%] |
The reported contrast averages 2009-2010 quarterly gap coefficients minus their 2007 average and transforms the log contrast by 100[exp(b)-1]. All models include route and quarter effects; uncertainty is clustered by route using CR1 and t(G-1). These are within-route descriptive contrasts, not difference-in-differences against untreated rival prices.


#### I.1 Carrier-specific event paths

![Figure A1: Within-route carrier-group fare gaps](../results/../extensions/carrier_diagnostics/results/carrier_gap_event.png)
The outcome is log mean fare for DL/NW single-carrier journeys minus log mean fare for other single-carrier journeys. Each path uses its fixed 2007 paired cohort and is normalized to 2007Q4. Pointwise 95% intervals cluster by route. The two-coupon restriction reduces one dimension of product composition but does not hold passengers, marketing-carrier affiliations, schedules, or cabin mix fixed.

The gap declines before the merger, falls around completion, and rebounds in 2009. Its subsequent behavior differs from the all-carrier market-fare comparison. A positive but imprecise carrier-gap contrast can coexist with a negative market-level contrast because the denominators and comparison outcomes differ. Group-level fare paths, mixed-carrier shares, all paired panels, and independent full-dummy checks accompany the saved results. The legacy control group has no recorded DL/NW presence in 2007 by definition, so an analogous baseline gap there is undefined; no artificial control gap is imputed.


### J  HonestDiD sensitivity to departures from parallel trends

The input is the full 23-coefficient adjusted event vector and route-clustered CR1 covariance on the unchanged 260-route panel. The reference is 2007Q4. Eleven coefficients cover 2005Q1-2007Q3, and twelve cover 2008Q1-2010Q4. The target gives weight zero to the first three later coefficients and 1/9 to each 2008Q4-2010Q4 coefficient. This assumes effects before 2008Q1 are absent. Treating the full later window as potentially affected avoids using announcement-period changes to calibrate the untreated trend. The target estimate is -0.03739 log points, approximately -3.67%; it is not the pooled -2.45% estimate, which compares averages over different periods through a restricted post indicator.

Let delta_t denote the adjusted untreated overlap-comparison gap relative to the omitted quarter. The relative-magnitude restriction bounds each later absolute first difference in delta by M times the largest absolute first difference during the pre-reference window, including its link to the normalized reference. It does not bound every post-period level by M times an estimated pre-period coefficient. Later first differences can accumulate, which matters because the nine-period target lies, on average, eight quarters after the reference. At M=0, later differential changes are fixed at zero; this does not impose zero pre-period contrasts.

I use the official HonestDiD R package, version 0.2.8, with the conditional least-favorable hybrid (C-LF), alpha=0.05, and seed 20260927. The target and covariance were reconstructed and matched to the main event output. The covariance is positive definite, with minimum eigenvalue 2.56e-5. The fixed source commit is recorded with the R code. HonestDiD uses asymptotic Gaussian inference with the supplied cluster covariance; it is not an exact finite-sample guarantee.

Table A11: Relative-magnitude robust confidence sets
| M | Log-point interval | Transformed interval | Grid step |
| --- | --- | --- | --- |
| 0.0 | [-0.07245, -0.00225] | [-7.0%, -0.2%] | 0.00015 |
| 0.5 | [-0.42085, 0.35090] | [-34.4%, 42.0%] | 0.00105 |
| 1.0 | [-0.80000, 0.73000] | [-55.1%, 107.5%] | 0.00500 |
| 2.0 | [-1.55500, 1.48500] | [-78.9%, 341.5%] | 0.00500 |
Endpoints are accepted grid points from official test inversion. Percentages transform the log target, not an arithmetic passenger-average treatment effect. All sampled acceptance sets have one connected component and rejected grid endpoints; adjacent rejected points bracket each reported endpoint. The full grids and numerical tolerances are saved.

The conventional normal-reference interval for this event-average target is [-0.07329, -0.00149] log points, or approximately [-7.07%, -0.15%]. The robust sets quickly become much wider: at M=0.5 the sign is already unresolved. This is neither evidence of a zero effect nor proof that the chosen magnitude restriction is true. It reports what the data identify conditional on an explicit class of differential paths. The complete inputs, package installation script, source commit, session information, and grid audit are included in extensions/honestdid/.

### K  Independent R and Stata estimation checks

Six specifications were independently re-estimated in base R 4.5.3 and Stata 19.5: the three fixed legacy-sample models in Table 3, the expanded distance-and-composition model, and the two WN-presence adjustments. Each program reconstructs the treatment interaction and explicit fixed-effect design from the saved route-quarter panels. R computes the route-clustered CR1 covariance directly; Stata uses regress with its cluster option. Both use route-cluster degrees of freedom for confidence intervals.

Across all twelve comparisons with Python, sample counts, route counts, design ranks, and residual degrees of freedom agree exactly. The maximum absolute coefficient difference is 2.14e-13 log points and the maximum standard-error difference is 6.96e-16, below the stated tolerance of 1e-9. Stata's design rank is counted from non-omitted regressors rather than the rank of its clustered covariance matrix. Numeric imports and exports use double precision.

The executed R and Stata code, portable run instructions, input fingerprints, full numerical outputs, and comparison table are in extensions/cross_language/. This checks the regression computations on common saved inputs; the separate source and cleaning audits address data construction. Agreement across programs does not establish the counterfactual trend assumption.
