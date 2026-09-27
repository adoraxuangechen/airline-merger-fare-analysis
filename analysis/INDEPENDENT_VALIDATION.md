# Independent numerical validation

`independent_check.py` checks the saved extension outputs without rereading the source archive or importing `extend_analysis.py`. Install the repository's numerical requirements before running it.

From the repository root, after generating the analysis outputs:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python analysis/independent_check.py
```

The default input directory is this repository's `results/`, located relative to the script rather than the shell's working directory. The default report is `independent_check_results.json` inside the selected results directory. Both locations can be overridden:

```sh
python analysis/independent_check.py --results /path/to/saved/results --out /path/to/validation.json
```

The checker requires the saved `extended_results.json`, `route_features.csv`, `carrier_shares_2007.csv`, and five `panel_*.csv` files produced by the extension analysis. It checks:

- Unique route-quarter keys, fare construction, fixed baseline aliases, and exact bin and common-support membership.
- Carrier-share normalization, conditional concentration calculations and the mechanical overlap-exposure formulas.
- Seven complete-panel regressions reconstructed with raw route/time/bin dummy variables: the published baseline, distance-and-composition adjustment, legacy common support, adjusted event study, route trends, the panel ending in 2009, and exclusion of baseline UA/CO routes.
- Coefficients, route-clustered CR1 standard errors, residual degrees of freedom, residual target variation and the adjusted event study's early-period joint test.

The reconstructed regression design uses its own code and full-dummy statsmodels regressions. It does not reuse the production estimator's within transformation, nuisance projection or transformed design. A failure raises an assertion rather than writing a passing report. The report records the reviewed production script's SHA256 fingerprint.

These are arithmetic and implementation checks. They do not independently reconstruct fares from raw BTS tickets, establish parallel trends, validate operating codes as economic firms, or establish a causal merger effect. The route-clustered covariance does not allow arbitrary dependence across routes sharing airports or airline networks. A numerical warning about near-zero nuisance variances can arise in the full-dummy route-trend regression; the checker explicitly verifies that the target coefficient and standard error agree and remain finite.
