# Cross-language regression validation: Python, R, and Stata

**Status: executed successfully.** R 4.5.3 and installed Stata 19.5 independently estimated all six specified regressions on September 27, 2026. This is an actual comparison of executed estimates, not a translation of code that was left unrun. No new R packages or commercial software were installed.

Both programs read the same saved Borenstein route-quarter panels used for the Python results. They independently construct the post-by-overlap indicator, the full fixed-effect regressors, and the regression estimates. R computes the route-clustered covariance directly; Stata uses its built-in `regress, vce(cluster routeid)` implementation.

Across twelve comparisons with Python (six models in each additional language):

- All sample sizes, numbers of route clusters, design ranks, and residual degrees of freedom agree exactly.
- Maximum absolute coefficient difference: **2.14 × 10^-13 log points**.
- Maximum absolute standard-error difference: **6.96 × 10^-16 log points**.
- Both differences are well below the specified numerical tolerance of 10^-9.

These checks validate the regression computations on shared analysis inputs. They do not independently reconstruct the raw-data cleaning and do not establish parallel trends or causal identification.

## Models verified

All models include route and quarter effects. The post period begins in 2008Q4, and the sample covers 2005Q1–2010Q4. Route-quarter observations are equally weighted. Fares within a route-quarter were constructed as passenger-weighted means by the main pipeline.

| Model | Route-quarter observations | Routes | Relative fare estimate | Clustered SE of log coefficient |
|---|---:|---:|---:|---:|
| Legacy comparison, unadjusted | 6,235 | 260 | −5.582642% | 0.0189728824 |
| Legacy, distance bin × quarter | 6,235 | 260 | −3.684076% | 0.0187836364 |
| Legacy, distance and baseline one-coupon-share bins × quarter | 6,235 | 260 | −2.453769% | 0.0183950367 |
| Expanded comparison, distance and composition adjusted | 14,430 | 616 | −4.429464% | 0.0123293542 |
| Legacy adjusted, plus baseline WN presence × quarter | 6,235 | 260 | −2.698186% | 0.0175504550 |
| Expanded adjusted, plus baseline WN presence × quarter | 14,430 | 616 | −2.554553% | 0.0128840758 |

WN presence is fixed from 2007: positive passengers on a source itinerary with WN in either carrier field. R constructs it from the route-feature file; Stata constructs the same indicator from the saved `wn_2007` field. Neither uses post-merger WN entry or share.

## Independent implementations

### R

`validate_models.R` uses only base R. It estimates ordinary least squares with explicit route and quarter factors and the prescribed factor-by-quarter interactions. R's QR decomposition selects the independent design columns.

For N observations, G routes, and design rank K, the covariance calculation is

`V = [G/(G−1)] [(N−1)/(N−K)] (X'X)^−1 [Σ_g s_g s_g'] (X'X)^−1`,

where `s_g = Σ_i_in_g x_i u_i`. The script independently computes the required diagonal element using cluster scores. Confidence intervals use the t distribution with G−1 degrees of freedom. It does not import or call the Python estimator.

### Stata

`validate_models.do` imports numeric data with `asdouble`, constructs `did = treated * (t >= 16)`, encodes route identifiers, and estimates explicit fixed-effect regressions using `vce(cluster routeid)`. For example:

```stata
regress lnfare did i.routeid i.t i.distance_bin#i.t i.share_bin#i.t, vce(cluster routeid)
```

All exported numeric results are stored explicitly as `double`. The design rank is counted from non-omitted design columns. With clustered standard errors, `e(rank)` is the rank of the covariance matrix and is not interchangeable with the design rank; it is not used for the reported N−K residual degrees of freedom. Confidence intervals use the same route-cluster degrees of freedom as R and Python.

The installed batch executable was `/Applications/StataNow/StataMP.app/Contents/MacOS/stata-mp`. Portable output records only version and execution status. Selected model-execution lines are archived without the Stata startup/license banner.

## Reproduction

Run from the repository root and choose a fresh output directory. Arguments also accept quoted absolute paths. Run R first as shown; it creates missing parent directories. If running Stata alone, create its complete output directory first.

```bash
Rscript extensions/cross_language/validate_models.R "$PWD" "$PWD/validation-rerun"
stata-mp -b do extensions/cross_language/validate_models.do "$PWD" "$PWD/validation-rerun"
python extensions/cross_language/compare_results.py --repository "$PWD" --extension-results "$PWD/extensions/carrier_diagnostics/results" --results "$PWD/validation-rerun"
```

If `stata-mp` is not on the command path, invoke the installed executable by its absolute path. The `.do` file was tested in Stata 19.5 and declares `version 19.0`. `compare_results.py` uses the Python standard library only. It requires six completed output rows from each independent language and fails if a sample count, design rank, coefficient, or standard error differs beyond tolerance.

Inputs are `results/panel_legacy_valid.csv`, `results/panel_all_unexposed.csv`, and `results/route_features.csv` from the main repository, plus the existing Python benchmarks in `results/extended_results.json` and the supplementary `wn_models.json`. Their SHA-256 fingerprints are recorded in the validation summary.

## Output inventory

- `results/r_model_results.csv`: all six independently executed R estimates and intervals.
- `results/stata_model_results.csv`: all six independently executed Stata estimates and intervals.
- `results/stata_model_results.dta`: the same Stata results in native double-precision storage.
- `results/cross_language_comparison.csv`: each language's coefficient, SE, sample/rank checks, and differences from Python.
- `results/validation_summary.json`: pass/fail, maximum differences, versions, tolerances, and input checksums.
- `results/r_session_info.txt`: R version and session information.
- `results/stata_version.txt`, `stata_execution_status.txt`, and `stata_selected_execution_log.txt`: concise execution evidence.

This validation uses the fixed analysis panels and does not modify the main analysis inputs. The saved scripts, estimates, software records, and comparisons are included in this release.
