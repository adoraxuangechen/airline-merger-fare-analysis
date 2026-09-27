# Design review for the September 27, 2026 extension

This is a prospective specification and measurement review, not a report of new regression results. I read `analysis/run_analysis.py`, the two document sources, `provenance/source_identity_audit.json`, `results/data_audit.json`, `results/results.json`, and the saved route inventory. Existing results and a baseline-characteristic cross-tab were inspected; no new outcome regressions were estimated. Only this review file was written. The existing baseline remains a descriptive relative fare contrast, not an established merger effect.

## 1. Correct the source premise before extending the analysis

The audited input is **not restricted to eight airline codes**. The audit records 125 distinct `cr1` codes and 109 distinct `cr2` codes over 2005–2010. The source comparison matches all 4,175,354 corresponding archive records in order. DL, NW, and six legacy codes are the current exposure/comparison classifier, not the universe of data carriers. Borenstein's documentation explicitly describes all carriers and all routes within its upstream ticket restrictions. Do not compute an eight-carrier HHI and label it full-market concentration.

The source still has important restrictions: operating codes, sorted carrier sets, only one- and two-coupon one-way equivalents, and upstream ticket screens. The ticketing carrier and order of the two legs are unavailable. Thus observed codes are not necessarily independent firms. Unknown carrier labels affect 34 source records; none enters main-sample 2007 classification, but this must be rechecked on every newly expanded sample. These are already aggregated sampled journeys, not observed population totals or independent ticket microdata. See [the source definitions](https://faculty.haas.berkeley.edu/borenste/mktdata.htm).

`cop == 0` should remain **one-coupon service**, or explicitly a **proxy for nonstop service**. It does not independently verify scheduled nonstop flights, carrier affiliations, or a competitive nonstop product market. Keep output variables readable (`one_coupon_share`, `one_coupon_overlap`); `direct`/`direct_overlap` are legacy internal names and should not become stronger claims in prose.

## 2. Freeze the baseline and a small extension registry

Retain the existing 2007 route classification, passenger-weighted market outcome, 2008Q4 post threshold, equal route-quarter regression weights, and observed-cell policy as the benchmark. Freeze extension rules before seeing their coefficients; date the registry honestly as an extension after earlier results were known. Report every registered result or an explicit reason it is unidentified/infeasible. Do not combine all restrictions factorially or choose the specification with a preferred sign or insignificant pretest.

Recommended compact table, with one change at a time:

1. Original baseline, plus the same model excluding the one invalid-distance route to establish a common comparison sample for rows 2–4.
2. Baseline distance-bin × calendar-quarter effects.
3. Baseline one-coupon-share-bin × calendar-quarter effects.
4. Both sets of effects jointly, **additively**, not a fully interacted cross-bin time process.
5. One prespecified common-support/reweighting estimator; display its unweighted restricted-sample estimate beside it so sample loss is separated from reweighting.
6. Pooled DID with route-specific linear trends.
7. Baseline truncated after 2009Q4, holding 2007 route membership fixed.
8. Baseline excluding routes with material pre-merger CO or UA presence, holding all other rules fixed.

Use the same unadjusted and adjusted dynamic regressions for the benchmark and the joint-bin specification only, rather than creating an event plot for every sensitivity. Keep concentration and one-coupon-overlap results in a separate exploratory measurement section because their exposure and/or target population changes. No extension should be labeled a newly verified causal answer merely because a coefficient remains negative.

## 3. Baseline bins and common support

Use the existing 2007 mean within-route one-coupon passenger share, not its post-merger value. Use valid positive `nsdst` as route distance. The audit finds it constant within every route; SJU–STT's zero is a sentinel. Drop that route from distance-dependent models and display the corresponding baseline. Do not treat zero as a very short trip or choose a distance bin from realized post-merger itinerary distances (`avdst`).

Simple prespecified bins are distance `[0,1000)`, `[1000,2000)`, `[2000,infinity)` miles after excluding nonpositive distance, and baseline coupon share `[0,.25)`, `[.25,.75)`, `[.75,1]`. Handle exact endpoints deliberately. These choices use conventional coarse scales and observed baseline composition, not post-period fit. Existing inventory counts, excluding SJU–STT, are:

| Baseline bin | Treated | Comparison |
|---|---:|---:|
| Distance below 1,000 | 38 | 87 |
| Distance 1,000–1,999 | 47 | 8 |
| Distance at least 2,000 | 71 | 9 |
| One-coupon share below .25 | 136 | 34 |
| Share .25–.749... | 15 | 3 |
| Share at least .75 | 5 | 67 |

These counts illustrate why marginally flexible adjustment is not proof of comparability. Crossed cells are even thinner. A transparent support exercise can retain only distance × coupon cells containing **at least five treated and five comparison routes**. Under these fixed proposed bins it retains the three below-.25-share cells, totaling **136 treated and 34 comparison routes**, before any additional missing-data checks. This is a substantial change in population; do not describe its coefficient as the same 156-route ATT.

For a modest matching/reweighting implementation, use coarsened exact matching on those two baseline dimensions: treated weight 1; comparison weight `n_treated_cell / n_comparison_cell`, constant for a route across quarters. First report the equal-weight restricted sample, then the weighted version. This is reproducible, has an explicit support criterion, and avoids the current unconstrained nearest-neighbor exercise that reuses one comparison route 30 times. It still does **not** balance 2007 fare or traffic within cells. Report weighted standardized mean differences for log 2007 fare, log 2007 traffic, distance, and coupon share, plus quantiles/plots and effective comparison sample size `(sum w)^2/sum(w^2)`. Residual imbalance is a finding, not permission to keep tuning bins until it vanishes. Do not claim full common support from univariate range overlap alone.

If the implementer instead commits to nearest-neighbor propensity matching, specify the score, caliper, replacement rule and tie-breaking before regression results; report discarded treated routes, reuse counts, distances and effective sample size. Do not search across both methods and report only the favorable one. Matching on noisy baseline fares can induce regression-to-mean concerns; matching is no substitute for an economic counterfactual argument.

## 4. Concentration and the predicted-merger increment

For every 2007 route-quarter, collect **all named operating codes** with single-carrier traffic: `cop==0` with named `cr1`, or `cop==1` with `cr1==cr2` and named code. Aggregate passengers across coupon categories for each code. Let `P_rq` be **all** retained route-quarter passengers, including mixed carrier sets, and `p_crq` single-carrier passengers for code c.

Construct and retain both the numerator and denominator:

- `s_crq = p_crq/P_rq`; named single-carrier coverage `C_rq = sum_c s_crq`; mixed/unknown residual `1-C_rq`.
- Partial recorded-code squared-share index `H_partial_rq = 10000 * sum_c s_crq^2`.
- A separately labeled conditional index among named single-carrier journeys, `H_conditional_rq = 10000 * sum_c (p_crq/sum_c p_crq)^2`, when that denominator is positive.
- Annual pooled 2007 shares `s_cr = sum_q p_crq / sum_q P_rq`, then `H_partial_r` and `Delta_index_r = 10000 * 2*s_DL,r*s_NW,r` using those same shares. This is **not** the unweighted mean of quarterly indices; store both only if separately named.

The conditional index covers a selected subset. The partial index's shares do not sum to one when mixed service exists. Neither is a complete independent-airline HHI. Assigning every mixed journey to both carriers double-counts passengers; an equal split is an arbitrary allocation; treating every carrier pair as an independent firm is economically wrong. A valid firm HHI needs a defensible itinerary-provider definition and dated carrier-affiliation crosswalk. Existing US/HP relationships also matter for a 2007 firm-level index. Report coverage distributions by treatment group so the interpretation is visible.

`2*s_DL*s_NW` is the algebraic increase in a squared-share index when exactly those two share categories combine and all shares/other categories are held fixed. It is **not** the realized concentration change, an instrument, or an exogenous treatment dose. Mixed DL–NW and partner itineraries can change categories too, so it need not equal a complete post-merger HHI change. Avoid antitrust regulatory thresholds on these proxies.

A time-invariant 2007 index alone is absorbed by route fixed effects. If a requested supplementary model uses `Delta_index_2007 × post`, call it a continuous-exposure association, state its scaling (e.g. per 100 index points), and keep it separate from the binary-overlap estimate. Do not replace the baseline after inspecting its sign. It mixes potentially endogenous market shares, route characteristics, and market-size-dependent composition. If examining it across all 5,535 eligible routes instead of the main 261, declare the different population. The current `fit()` summary assumes a binary treatment: summing dose values to report treated-route counts is invalid; keep route labels separate from the regressor.

## 5. One-coupon overlap and CO/UA sensitivity

The existing `direct_overlap` is annual DL one-coupon passengers ≥100 **and** annual NW one-coupon passengers ≥100. It does not require same-quarter overlap or the main sustained 5% rule. Only five main routes satisfy it: ATL–DTW, ATL–MEM, ATL–MSP, HNL–SFO, and LGA–PHX. This count must not be relabeled as five verified nonstop-overlap routes.

For a coherent new proxy, use DL and NW one-coupon passengers, each divided by all market passengers, both ≥5% in the same quarter in at least three 2007 quarters; retain the main passenger eligibility and comparison definition. Record this new sample's size before deciding whether regression inference is meaningful. With very few treated routes, an ordinary route-clustered t interval can be misleading despite many control routes. Prefer route-level descriptive paths and mark precision limitations. Do not pool five-route and broad-overlap estimates as if they estimate the same quantity. A one-coupon-only fare outcome would additionally change the outcome and observation availability, and therefore should not be quietly mixed into the same check.

For the other merger, a clear primary sensitivity is to retain 2005Q1–2009Q4, with unchanged 2007 labels. UA–CO announced on May 3, 2010 and completed on October 1, 2010. Dropping only 2010Q4 misses announcement-period responses. The shorter panel changes follow-up length; it does not remove all fuel, recession or network shocks. Sources: [United's announcement filing](https://ir.united.com/static-files/69c1f868-c861-48c0-8ada-6cda772720ee) and [completion 8-K](https://www.sec.gov/Archives/edgar/data/100517/000119312510222185/d8k.htm).

For route exclusion, use **pre-DL–NW** information: flag if either CO or UA has single-carrier share ≥5% in at least three 2007 quarters, and exclude flagged routes from **both** groups. This is deliberately broader than CO–UA overlap because network effects need not be confined to jointly served routes. Report retained treated/control counts and retain this as sensitivity. Selecting routes using 2009 or 2010 traffic to fix confounding in a 2008 merger study can condition on responses to the focal merger. Excluding every later observed CO/UA route is not a clean pretreatment design.

## 6. Estimation and code QA

The existing absorbed baseline has independent dummy-regression validation and correctly transforms quarter indicators as well as the outcome and treatment. Preserve that property. For bin interactions, absorb/transform every added regressor and use an explicit reference bin and quarter. Check column names, numerical rank, degrees of freedom and condition numbers; don't silently use a pseudoinverse to disguise unidentified exposure effects. Prefer QR/SVD least squares over explicit inversion of normal equations for the enlarged, potentially ill-conditioned designs. Match coefficient and clustered covariance against one explicit-dummy regression on an actual small subset with all relevant bin categories and missing cells.

For **pooled DID with route linear trends**, use `logfare_rt = route_FE + quarter_FE + route_slope_r*(t-centered) + beta*T_r*Post_t + error`. One linear combination of slopes is absorbed by quarter effects; choose a full-rank parameterization (e.g. reference-route slope). Estimate and report as a sensitivity, acknowledging extrapolated trend shape and that using post-period data to fit trends can absorb gradual treatment responses.

Do **not** naively add unrestricted route slopes to the saturated event study with only one omitted treated-quarter interaction: a linear combination of the event coefficients is exactly in the route-slope/intercept span. An additional substantive normalization is needed, and the event path is not uniquely identified as before. Keep the trend exercise pooled rather than dropping an arbitrary event coefficient to make the matrix invertible. Pre-period-only detrending would be a different two-stage estimator and requires inference accounting for estimated trends; treating detrended outcomes as fixed understates uncertainty.

Required output checks:

- Preserve source hash; assert `cop` in {0,1}, valid known-carrier comparisons and nonnegative numerator/denominator construction. Keep natural keys unique and passenger/fare-numerator conservation.
- Assert each baseline covariate, weight, bin and route flag is constant within a route and uses only 2007 information (distance is physically invariant and audited). Preserve both raw and constructed names.
- Assert code shares sum to coverage ≤1; store mixed and unknown residuals, single-carrier coverage, annual denominator, and units/scaling of concentration measures. Never renormalize without naming the new population.
- Report all sample attrition by group, route counts, cells, missing quarters, weighted effective sample size, and treatment variation after nuisance projection. Require positive residualized treatment variance.
- Cluster on route, with degrees of freedom reflecting absorbed route intercepts and added slopes/controls. Matching/reweighting intervals conditional on selected weights are not complete design uncertainty. Cross-route airport/network correlation remains an unresolved inference limitation.
- For joint event tests, check rank of the selected covariance matrix and `q <= G-1`; if not, return an explicit unavailable diagnostic rather than an arbitrary p-value. Report early 2005–2007 tests, not only tests relative to post-announcement 2008Q3.

Do not control contemporaneous traffic, realized market share/HHI, coupon mix, or itinerary distance as ordinary confounders in the focal total-fare comparison. The merger may affect each of them, making them mediators or selection variables. Fixed pre-period characteristics interacted with time are safer diagnostics, but assume sufficiently similar responses within those categories and do not account for all demand or cost differences. A lower post-period p-value or a newly insignificant pretest does not certify causality; see [Roth (2022)](https://doi.org/10.1257/aeri.20210236).

## 7. How to interpret a completed extension

The useful outcome is to learn whether the negative fare contrast survives explicit accommodation of baseline trip length, itinerary composition and a visibly narrower support population. If it moves substantially, report which adjustment/sample change produces that movement. If it remains, state the narrower descriptive stability and its economic scope. Neither branch automatically identifies a merger effect. Documenting sparse overlap, mismeasured provider concentration, and a tiny one-coupon-overlap sample is substantive information about what these data can credibly answer.
