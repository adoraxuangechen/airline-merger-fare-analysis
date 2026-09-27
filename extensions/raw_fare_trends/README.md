# Raw quarterly fare levels on the primary route sample

This extension produces a descriptive figure in nominal dollar levels from the **unchanged primary 260-route panel**: 156 overlap routes and 104 legacy comparison routes, classified using the existing 2007 rules. It neither reselects routes nor estimates a new treatment effect.

## Mean definitions

The input is `results/panel_legacy_valid.csv`. Its route-quarter `fare` is already the passenger-weighted mean of Borenstein aggregate records on that route: `revenue / pax`. The plotted series gives each observed route in a group equal weight:

`equal_route_mean_fare[g,t] = sum(fare[r,t]) / number_of_observed_routes[g,t]`.

This preserves the main analysis's emphasis on equally weighted route-quarter observations. The plotted arithmetic means are nevertheless different from log-fare regression coefficients; their dollar gap does not exactly recover the −5.58% unadjusted difference-in-differences estimate or any adjusted estimate. All fares are nominal one-way-equivalent dollars, with no normalization or price deflator applied to the plotted values.

The CSV also stores the distinct pooled-passenger-weighted group mean:

`pooled_passenger_weighted_fare[g,t] = sum(revenue[r,t]) / sum(pax[r,t])`.

That series gives larger routes more weight and is **not** the plotted series. Annual summaries average the four quarterly group means. The annual average of quarterly pooled means is labeled accordingly; it is not an all-year pooled passenger mean.

## Fixed membership and observed cells

There are 6,235 observed route-quarter cells out of 6,240 possible cells. All 156 overlap routes appear in all 24 quarters. Comparison counts range from 102 to 104; the five unobserved comparison cells are:

- CLD–LAX: 2005Q1, 2005Q2, 2005Q3, and 2010Q3.
- LAS–PSP: 2005Q1.

No fares are imputed for those cells. The main figure keeps the same 260-route membership and averages available observations each quarter. Every quarterly count and passenger total is saved.

A sensitivity series retains only routes observed in all 24 quarters: 156 overlap and 102 comparison routes. It is also saved in the CSV, labeled `balanced_24_quarters`. Overlap means are identical. The maximum absolute difference between primary and balanced comparison means in any quarter is **$2.32**. This balanced sensitivity changes the comparison membership, so it is recorded separately.

## Observed patterns

Both groups' mean fares rise into 2008, fall in 2009, and recover in 2010. Annual average means are:

| Year | Overlap routes | Legacy comparison routes |
|---|---:|---:|
| 2005 | $212.45 | $186.34 |
| 2006 | $229.88 | $193.68 |
| 2007 | $233.27 | $194.70 |
| 2008 | $245.46 | $211.29 |
| 2009 | $224.16 | $198.00 |
| 2010 | $240.40 | $213.57 |

The average dollar gap already changes before completion: it is $26.11 in 2005 and $38.57 in 2007, then $26.16 in 2009. These raw paths document the data and the time-varying gap; they do not attribute the movements to the merger, fuel prices, or the recession. The regression and event-study evidence provide the separate conditional comparisons.

## Suggested figure caption

**Raw quarterly fare levels on the primary route sample.** Lines show arithmetic means across observed routes of passenger-weighted route-quarter fares, in nominal one-way-equivalent dollars. The fixed sample contains 156 overlap and 104 legacy comparison routes; quarterly coverage is 156 and 102–104 routes, respectively. The shaded interval covers the announcement–completion quarters (2008Q2–2008Q4), with vertical markers at announcement and completion. The plotted means are descriptive and are not regression estimates.

## Reproduction

From the repository root, use the following command (explicit absolute paths are also supported):

```bash
python extensions/raw_fare_trends/build_raw_fare_trends.py --repository . --out raw_fare_recheck
```

It requires NumPy, pandas, and Matplotlib from the main analysis environment. Times New Roman is used when available; otherwise the portable fallback is DejaVu Serif. The white-background, single-panel figure is **7.2 × 3.0 inches**, suitable for placement at 468 points wide; the PDF contains vector lines and embedded TrueType text, while the PNG is 300 dpi.

Outputs:

- `raw_fare_trends.pdf` and `raw_fare_trends.png`: the primary figure.
- `raw_fare_quarterly_means.csv`: both weighting conventions, both coverage cohorts, and counts for every quarter.
- `raw_fare_annual_means.csv`: transparent averages of quarterly means.
- `unobserved_route_quarters.csv`: the exact five missing cells.
- `validation.json`: source checksum, sample identities, fare/log checks, six independent summation checks, and balanced-panel differences.

Validation checks confirm unique route-quarter cells; fixed treatment status; the expected 156/104 route counts; positive finite fares and passengers; `fare = revenue / pax`; and `lnfare = log(fare)`. Six group-quarter aggregates were recalculated by direct scalar summation and agree to floating-point precision. The figure has been visually checked for legibility and clipping. No canonical manuscript or published content was changed by this extension.
