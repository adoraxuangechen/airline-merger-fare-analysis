# Current analysis

`extend_analysis.py` reconstructs the 2005–2010 route-quarter panel directly from the NBER/Borenstein archive or its checksum-recorded six-year extraction. It preserves source files. The previous script and its outputs are archived under `archive/v1/`.

The complete cleaning and estimation description is in the [technical supplement](../papers/technical_supplement_v2.pdf). The [dated design log](../provenance/analysis_plan.md) specifies the extension sequence. It is a contemporaneous analysis log, not a preregistration predating the project.

```sh
python analysis/extend_analysis.py --source data/NBER_2005_2010.csv.gz --out results_recheck
python analysis/independent_check.py --results results_recheck
```

`--source` also accepts the verified NBER ZIP; `--old-panel` optionally checks equality against an old saved main panel. `--use-prepared` reuses the selected output directory's features and all-route intermediate after checking the source hash, for estimation debugging. A fresh replication should omit that flag.

Outputs include every specification, not only those selected for the main table. Route features use 2007 only. Treatment is never reclassified from post-merger carrier presence. Fare weighting and regression weighting are separate. Quarter effects absorb a common deflator, not heterogeneous macroeconomic shocks.

The estimator uses route demeaning of every regressor followed by a rank-checked QR projection of nuisance effects. CR1 route-clustered inference accounts for absorbed degrees of freedom. The independent checker rebuilds full raw dummy matrices, rather than importing the production estimator. See [validation details](INDEPENDENT_VALIDATION.md).

`hhi_single` is conditional on single-carrier journeys. `delta_proxy` uses all-market passenger denominators. They are not the same measure, and neither reconstructs all economic-firm affiliations. Undefined conditional HHI is retained as missing for zero-coverage routes. One-coupon overlap is not relabeled as verified nonstop overlap.
