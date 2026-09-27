# Additional carrier-composition diagnostics

These supplementary analyses answer two specific questions raised during revision. They use only the same Borenstein 2005–2010 data as the main paper. The original source and existing main results are unchanged. All fixed specifications and results are retained. No finding is selected by statistical significance.

## Reproduction

Requirements are the main repository's scientific Python environment. From the working project:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python run_additional_diagnostics.py --repository /path/to/repository --source /path/to/NBER_2005_2010.csv.gz --out /path/to/additional_results
python independent_gap_check.py --results /path/to/additional_results
```

Both scripts are in `extensions/carrier_diagnostics/`; run the commands from that directory. `--repository` explicitly locates the existing analysis code and results, and `--source` identifies the precision-preserving extract. It reads `analysis/extend_analysis.py` for the already validated clustered route-fixed-effects estimator. It does not overwrite the repository's main results. `protocol.md` records the contemporaneous specification plan, written before examining these new estimates; it is not a historical preregistration.

## 1. Southwest and the expanded comparison

The original valid-distance comparison contains 104 routes; adding all eligible unexposed markets adds 356 routes, for 460 expanded comparison routes. The overlap group remains 156 routes. This comparison does not change the treatment rule.

Southwest (WN) presence means any positive 2007 passenger count on a source record with WN in either operating-carrier field. The share is passengers on such records divided by *all* 2007 route passengers. A logical OR ensures an itinerary is counted only once even if both fields contain WN. Mixed itineraries involving WN are included. This definition is distinct from the single-carrier grouping in the next section and does not proxy for every low-cost carrier.

| Baseline 2007 measure | Overlap | Legacy comparison | Added comparison |
|---|---:|---:|---:|
| Routes | 156 | 104 | 356 |
| WN-positive routes | 86 | 30 | 192 |
| Percentage of routes WN-positive | 55.1% | 28.8% | 53.9% |
| Route-average WN journey share | 8.0% | 12.6% | 44.7% |
| Passenger-weighted WN journey share | 7.8% | 40.1% | 66.7% |

The expanded controls have substantially higher WN exposure intensity. To assess its relevance, all models retain the previously fixed distance-bin and baseline one-coupon-share-bin by quarter effects. Additional effects interact the 2007 WN indicator or fixed share categories (zero; positive below 50%; at least 50%) with quarters. Neither WN definition uses post-merger data.

| Sample | Distance/composition adjusted | Also WN presence × quarter | Also WN share category × quarter |
|---|---:|---:|---:|
| Legacy comparison | −2.45% [−5.92, 1.14] | −2.70% [−6.00, 0.72] | −1.63% [−5.21, 2.09] |
| Expanded comparison | −4.43% [−6.72, −2.09] | −2.55% [−4.99, −0.06] | +0.82% [−2.34, 4.08] |

Brackets contain 95% route-clustered confidence intervals. Estimates transform the log coefficient as 100[exp(beta)−1]. All use 2005Q1–2010Q4, with the main post period beginning 2008Q4. The baseline WN-presence adjustment brings the two estimates close together, while intensity categories produce further sensitivity. Only 2 overlap routes have WN shares of at least 50%, compared with 17 legacy and 172 added comparison routes. Thus share-category adjustment has thin treated support in WN-dominant markets; it is not evidence that the positive expanded estimate is a better causal estimate.

WN-presence-adjusted event studies continue to reject the pre-period joint test: legacy F(11,259)=4.582, p=2.29e−6; expanded F(11,615)=6.756, p=9.14e−11. These results help diagnose *association between carrier composition and comparison sensitivity*; they neither identify a causal Southwest effect nor repair parallel trends.

`comparison_quarterly_paths.csv` reports available-sample and fully balanced 24-quarter geometric mean fare indices normalized to 2007Q4, including sample counts and separate WN-presence strata. The fully balanced cohort retains 156 overlap, 102 legacy, and 303 added comparison routes. Between average 2007 and average 2009–2010, fares in the added WN-positive balanced stratum rise 12.53%, whereas those in its WN-absent stratum fall 1.52%. The analogous legacy figures are +7.73% and +5.06%. These are descriptive nominal within-cohort paths with no causal interpretation. Period averages here exclude 2008 and are not the main pooled-regression coefficient.

## 2. Within-route DL/NW versus other single-carrier fares

Source records are partitioned, never duplicated, into:

1. **DL/NW single-carrier**: one coupon (`cop=0`) or equal operating-carrier codes, with the single code DL or NW.
2. **Other single-carrier**: the same single-carrier rule but another recorded code.
3. **Mixed-carrier**: all other records, kept separately, including DL–NW combinations or an itinerary containing only one merging party.

No regional carrier is reassigned to a parent. Columns retaining the historical label `rival` mean all single-carrier journeys recorded under operating codes other than DL or NW. This pool may include regional affiliates of DL/NW or other airlines, because the source does not map every code to its parent. The label does not verify independent competitors or identify the fare-setting/ticketing carrier. Within each carrier-group–route–quarter cell, fares are passenger-weighted source fares. Positive finite passenger and fare observations are required, exactly as in the main construction. Mixed fare rows are never imputed to either single-carrier group.

The original control group has no DL/NW records in 2007 by definition, so a baseline DL/NW-minus-other fare gap is undefined there. The descriptive gap analysis therefore uses original overlap routes with both groups observed with positive passengers in every quarter of 2007. This retains **144 of 156** routes. All 156 have DL/NW traffic in every 2007 quarter; the 12 exclusions have other-single-carrier traffic absent in one or more quarters. For one excluded route, ATL–BZN, the other group is absent in all four quarters. The other 11 have one to three observed quarters. The full route-level ledger is saved in `carrier_gap_baseline_availability.csv`.

The outcome is ln(DL/NW fare)−ln(other fare). Regressing this on route and quarter indicators, with 2007Q4 omitted, gives the plotted descriptive within-route path. Equal weight is placed on each available route-quarter gap. Inference clusters by route with the same CR1 degrees-of-freedom correction as the main model and t critical values with G−1 degrees of freedom. The contrast below averages the eight 2009–2010 quarter coefficients and subtracts the four 2007 coefficients, treating the omitted quarter as zero. It is a change in the **ratio of group fares**, not a standalone merger fare effect and not the main pooled post-period coefficient.

| Product/cohort | Routes | Paired cells | Ratio change: 2009–2010 vs. 2007 | 95% interval |
|---|---:|---:|---:|---:|
| All products; baseline paired | 144 | 3,438 | +1.57% | [−0.70%, +3.89%] |
| All products; all 24 quarters paired | 133 | 3,192 | +0.97% | [−1.18%, +3.18%] |
| Two-coupon only; baseline paired | 142 | 3,385 | +1.46% | [−0.77%, +3.75%] |
| Two-coupon only; all 24 quarters paired | 129 | 3,096 | +0.76% | [−1.32%, +2.89%] |

The 144-route baseline-paired cohort has 18 unpaired cells outside 2007, out of 3,456 possible cells; the all-quarter sensitivity removes routes with any unpaired cell. The analogous two-coupon cohort has 23 unpaired cells out of 3,408, with full details in `carrier_gap_cohorts.csv`. Two-coupon-only grouping reduces one- versus two-coupon composition changes but does not hold the connection airport, itinerary characteristics, fare class, or passenger type fixed.

Separate nominal group-fare paths on these same paired observations are also saved. In the 144-route cohort, average 2009–2010 versus 2007 is +0.35% [−2.17%, 2.94%] for DL/NW and −1.20% [−3.40%, 1.05%] for the other single-carrier group. In the fully balanced 133-route cohort the corresponding changes are +0.12% and −0.85%. Common economy-wide price changes are not removed from those nominal level paths; only their within-route difference cancels route-quarter shocks common to the two groups.

The internal gap falls in late 2008 and rebounds in 2009. It is already on a descending path over 2005–2007 and its 2009–2010 average contrast with all of 2007 is imprecise. This is a different outcome from the route-average overlap-versus-control event study. The two should not be described as having the same time path, and a rebound from the late-2008 trough cannot establish coordination.

Mixed itineraries account for 30.8% of route-quarter-average passengers on overlap routes in 2007, 39.7% in 2009, and 37.7% in 2010. Passenger-weighted shares across routes are 20.5%, 25.0%, and 23.0%, respectively. The difference between those averaging conventions matters. Such changes, source carrier coding, and unobserved within-group product composition prevent interpreting the group-fare gap as a clean strategic response.

## Suggested short paper text

> The expanded comparison set has much greater baseline Southwest exposure: WN journey shares average 44.7% among added routes, against 12.6% among legacy controls. Allowing separate quarterly movements by baseline WN presence moves the expanded estimate from −4.43% to −2.55%, close to the corresponding legacy estimate of −2.70%; finer exposure categories produce further sensitivity, with very few overlap routes in WN-dominant markets. Carrier composition therefore helps explain the comparison dependence, without identifying a Southwest effect or resolving differential pre-trends.

> Separating single-carrier itineraries within the same overlap routes yields a modest, imprecise increase in the DL/NW-to-other-carrier fare ratio: 1.57% in 2009–2010 relative to 2007 (95% CI: −0.70% to 3.89%; 144 routes). The ratio falls in late 2008 and rebounds in 2009, while its longer pre-merger decline and changing mixed-itinerary shares caution against reading that rebound as a strategic pricing response.

## Files and verification

- `comparison_baseline_2007.csv`, `comparison_baseline_by_wn.csv`, `wn_share_bin_route_counts.csv`: baseline composition and categorical support.
- `comparison_quarterly_paths.csv`, `comparison_pre_post_summary.csv`, `comparison_fare_paths.{png,pdf}`: complete descriptive comparison paths and counts.
- `wn_models.json`, `wn_model_registry.csv`, `wn_event_coefficients.csv`: all WN-adjusted specifications, coefficients, confidence intervals, and pretests.
- `carrier_group_route_quarters.csv.gz`, `carrier_group_coverage_and_shares.csv`: complete carrier-group fares, shares, and coverage.
- `carrier_gap_*_panel.csv` is represented by the four `all_products_*_panel.csv` and `two_coupon_only_*_panel.csv` files: every row used by the gap regressions.
- `carrier_gap_period_contrasts.csv`, `carrier_gap_event_coefficients.csv`, `carrier_gap_covariance.json`, `carrier_gap_event.{png,pdf}`: all internal-gap results and full joint covariance matrices.
- `carrier_level_period_contrasts.csv`, `carrier_level_event_coefficients.csv`: the corresponding separate carrier-group nominal fare paths.
- `validation_checks.json`: passenger totals exactly partition all 6,235 legacy-valid route-quarter cells; revenue difference is at most 4.66e−10 dollars from floating-point summation. Selected source-row weighted fares and all 260 routes' baseline WN counts are independently recomputed.
- `independent_gap_model_checks.json`: an independent statsmodels regression with explicit route indicators reproduces every gap model's coefficients and covariance; the fully balanced contrasts additionally agree with direct arithmetic of mean log gaps.

These output files contain all supplementary estimates rather than a selected subset. They should accompany, not silently replace, the main design and model registry.

To re-render the saved carrier-gap plot with explicit other-code labels, without re-estimating the models, run `python extensions/carrier_diagnostics/replot_carrier_gap.py` from the repository root. Numerical column names retaining `rival` preserve compatibility with earlier result files and use the other-code definition above.
