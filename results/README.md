# Saved outputs

These are saved results from the complete verified run on the original CSV. A fresh run with `--out results_recheck` recreates the same outputs separately; last-bit floating-point differences across numerical libraries are possible.

- **`analysis_panel.csv`**: 6,259 main-sample market-quarter rows. `route` joins the alphabetically ordered airport endpoints; `t=1` is 2005Q1 and `t=24` is 2010Q4. `treated=1` denotes 2007 material overlap. `fare` is the passenger-weighted market mean; `lnfare` is its natural logarithm.
- **`route_classification.csv`**, **`main_route_inventory.csv`**: full 2007 classification and the 261 selected routes, including pre-period characteristics.
- **`regression_results.csv`**, **`results.json`**: all specifications, sample sizes, log coefficients (`b`), route-clustered standard errors (`se`), p-values, confidence limits and exact `100 × (exp(b) − 1)` conversions. `lo`/`hi` are log-coefficient limits; `percent_lo`/`percent_hi` are their transformations.
- **`event_coefficients.csv`**, **`early_pre_event_coefficients.csv`**: quarterly contrasts. Main `rel_time=0` is 2008Q4; main `rel_time=-1` (2008Q3) is omitted and normalized to zero. The separate early-period model uses 2007Q4 as reference.
- **`event_study.png/.pdf`**, **`descriptive_trends.png/.pdf`**: figures generated directly from estimates and the panel.
- **`row_cleaning_flow.csv`**, **`data_audit.json`**: row attrition, missingness, input fingerprint, data ranges, sample properties and software versions.
- **`sample_descriptives.csv`**, **`descriptive_trends.csv`**: group comparisons; time trends average route outcomes and are not passenger-pooled fare series.
- **`specification_bridge.csv`**: ordered changes from the original implementation to the current main model, separating estimation, aggregation, eligibility and group definition.
- **`original_reproduction.json`**, **`original_event_coefficients.csv`**, **`original_table_b1_comparison.csv`**, **`original_treated_inventory.csv`**: historical implementation audit, not the current substantive model.

The original and clean all-market route-quarter panels are larger intermediate outputs omitted from Git. A full run regenerates them. Validation diagnostics in `results.json` compare absorbed and explicit-dummy coefficients and clustered standard errors on an actual-data subset, including unbalanced markets; they do not certify a causal interpretation.
