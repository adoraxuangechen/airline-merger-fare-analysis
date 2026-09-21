# Reproducible Delta–Northwest fare analysis

This folder contains the complete code for the new writing sample. The source
CSV is an externally supplied aggregate extract, not raw DB1B tickets. The script
never modifies that CSV and cannot reconstruct filters used before its creation.

## Run

Python 3.12 is the verified version. Create a virtual environment, install the
versions in the root `requirements.txt`, then run from the repository root:

```sh
python scripts/download_and_verify.py
python analysis/run_analysis.py --input "data/DB1B_2005_2010 copy.csv" --out results_recheck \
  --printed-b1 analysis/original_table_b1_transcribed.csv
```

All substantive choices are fixed in `run_analysis.py`; there is no interactive
step, no random draw, and no undocumented manual adjustment to the outputs.
The source SHA256, software versions, assertions and sample counts are recorded
in `results/data_audit.json` and `results/results.json`.

## What a row represents

The supplied columns are year, quarter, two alphabetically ordered airport
endpoints, one-coupon versus two-coupon category (`cop`), operating carrier identifiers
(`cr1`, `cr2`, in alphabetical order rather than flight sequence), sampled passenger count (`pax`), cell average one-way-
equivalent fare (`avprc`), endpoint distance (`nsdst`) and average itinerary
distance (`avdst`). A one-coupon observation need not be labeled a nonstop flight
without further flight-level information. These are aggregated carrier/itinerary
cells. A row is not a passenger and not an individual ticket.

The observed unique key is `cr1 cr2 yr qtr cop ap1 ap2`; missing second carrier
is structurally expected for one-coupon records. An absent carrier code is not
imputed. A zero endpoint distance is retained for fare analysis, not interpreted
as evidence of zero physical distance. The only selected market with a zero
distance sentinel is SJU–STT (24 quarters); a separate sensitivity excludes it.
The inherited matching sensitivity retains that source value to reproduce the
prior implementation, so it should not be treated as a validated distance match.

## Cleaning, in order

1. Verify required columns, raw row count, missingness, natural-key uniqueness,
   exact duplicates, numeric ranges and airport-pair ordering.
2. Restrict to 2005–2010 and quarter 1–4.
3. Drop missing or identical airport endpoints.
4. Require finite positive passenger count and finite positive cell mean fare.
5. Keep all other records. Do not trim extreme fares, winsorize, impute a carrier,
   replace distance zeros, inflate sampled passengers, or expand cells into tickets.
6. Form the canonical unordered airport-pair × quarter panel. Sum `pax` and
   `pax*avprc` across all retained cells. Their ratio is the market fare. Take the
   natural log only after this aggregation.

Independent source-archive reconciliation (see the provenance audit in the
replication package) found that literal carrier code NA had already been exported
as blanks in 22 first-carrier and 20 second-carrier entries. These are not changes
made by this script. The CSV is preserved as supplied; those cells are included
in market fares and do not count as DL/NW or a named legacy carrier. The field
`unknown_pax` means missing carrier labels only, not all unidentified carrier codes.

The data have no exact duplicates or natural-key duplicates; no duplicates are
dropped. All airport pairs already use lexical ordering. The four same-airport
rows are excluded only in the clean panel. Their removal does not alter the
original regression sample because those markets never meet its four-quarter rule.

## Exposure and comparison groups

Classification uses 2007 alone. A single-carrier itinerary is a one-coupon cell
or a two-coupon cell with the same operating carrier in both fields. For each
market-quarter, compute each airline's passenger share across such itineraries,
with all market passengers as denominator. Material overlap means both DL and
NW have at least 5% shares in the same three or four quarters of 2007. Eligible
markets must appear in all four 2007 quarters with at least 100 sampled
passengers each quarter. The comparison group has no observed DL or NW in
either operating-carrier field in any quarter of 2007 and a combined share of at least 5% from single-carrier itineraries operated
by AA/AS/CO/UA/US/HP in at least three quarters. Other eligible
markets are excluded from the main comparison. These rules are inherited from
the revised replication package; they are transparent design choices, not
historical preregistration and not proof of a valid counterfactual.

The classification stays fixed in every postmerger period. Main estimation
retains all available 2005–2010 quarters for the selected markets. It does not
select on postmerger carrier presence. The balanced-panel sensitivity requires
24 quarters and therefore does condition on postmerger observation availability.

## Estimation and inference

The dependent variable is the log of the passenger-weighted route-quarter fare.
The main regression gives every route-quarter equal weight. It includes route
and quarter fixed effects and the interaction between overlap status and the
2008Q4-or-later indicator. The code removes route means from the dependent
variable AND every regressor, including every quarter dummy, before fitting.
For the fixed-2007-passenger-weight sensitivity it uses weighted route means
and weights that never change with postmerger traffic.

Uncertainty uses a route-clustered CR1 covariance matrix with the finite-sample
factor G/(G−1)*(N−1)/(N−G−K), where K includes the residualized treatment and
quarter regressors. Two-sided p-values and 95% intervals use t(G−1). This assumes
independence across markets; common-airport/network correlation may violate it.
These intervals do not fix confounding or establish causation.

The original reproduction deliberately preserves the incomplete demeaning in
the supplied code: only y and the DID interaction are route-demeaned; quarter
dummies remain raw. Its event-study y is demeaned over the full original sample
before restricting the event window, and its event indicators remain raw. Its
reported inference follows statsmodels' legacy normal-reference convention and
its original degrees-of-freedom correction, to reproduce the supplied code.
Only 12 treated markets occur in that original sample; the large control count
does not by itself ensure dependable inference for such a concentrated exposure.
Use its intervals for audit only, not a substantive causal conclusion.

The full event study omits 2008Q3 and reports 23 quarterly relative contrasts.
It includes the full 24-quarter sample. Joint F tests assess all available
pre-reference coefficients, plus a separate strictly 2005–2007 event study with
2007Q4 as reference. The latter avoids the 2008 announcement/anticipation period.
Rejection warns against the simple parallel-trends interpretation; nonrejection
would not prove it. All event intervals are pointwise, not simultaneous bands.

## Bridge between implementations

`specification_bridge.csv` changes one component at a time:

A. Original row-mean market fare, hand-coded overlap markets, partial demeaning.
B. Same observations/outcome/groups, correct two-way fixed effects.
C. Same observations/groups, passenger-weighted market fare.
D. Add the 2007 eligibility rule, keep the old group labels.
E. Same eligible market pool, replace treatment with empirical material overlap.
F. Keep empirical treatment, restrict controls to the unexposed legacy group.

This is an order-dependent accounting exercise, not a unique decomposition.
Do not explain the difference between the old and revised headline numbers by
one coding correction or select favorable estimates across incompatible samples.

## Validation and outputs

- Independent statsmodels full-dummy OLS/WLS regressions verify both coefficient
  and clustered standard-error equality on an actual-data subset including every
  unbalanced main-sample market and treated and comparison markets.
- Separate statsmodels checks verify legacy DID and event coefficient/SE conventions.
- An event-study check compares the absorbed implementation with explicit route
  and quarter dummies, checking every quarterly coefficient and clustered SE.
- Assertions verify positive finite log outcomes, route-quarter key uniqueness,
  conservation of passengers and fare-weighted sums, and unchanged observations
  for bridge B→C.
- `original_reproduction.json` and `original_event_coefficients.csv`: exact rerun
  of the supplied original implementation. `original_table_b1_comparison.csv` checks
  every printed B1 coefficient and SE against its rerun (none match at printed
  precision); this does not certify historical provenance
  of a printed table that lacks matching saved output.
- `row_cleaning_flow.csv`, `data_audit.json`: complete row-level attrition and audit.
- `original_route_quarter_panel.csv`, `clean_route_quarter_panel.csv`: aggregate
  panels sufficient to inspect the original and clean market-fare calculations.
- `route_classification.csv`, `main_route_inventory.csv`: full 2007 classifier and
  selected market inventory.
- `analysis_panel.csv`: main regression data; `t=1` means 2005Q1.
- `regression_results.csv`, `results.json`, `specification_bridge.csv`: estimates,
  sample sizes, exact exp(beta)−1 conversions and diagnostics.
- `event_coefficients.csv`, `early_pre_event_coefficients.csv`: event outputs.
- `sample_descriptives.csv`, `descriptive_trends.csv`: descriptive comparisons.
- `event_study.png/.pdf`, `descriptive_trends.png/.pdf`: figures generated from
  the saved estimates and panel, with no hand-adjusted values.

Fare dispersion across cell mean fares is only reproduced to audit the old code.
It cannot recover dispersion across passenger fares without within-cell second
moments. It is excluded from the new paper's economic conclusions.

The supplied original implementation is reproduced within `run_analysis.py` for
historical audit. Its source file is not distributed here; the repository history
also retains the previously published analysis. Use the current analysis entry
point for the writing sample. Large all-market panels are generated by a full run
but omitted from Git; the 6,259-row main analysis panel is included.
