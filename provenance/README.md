# Source and design records

The current revision directly reads the NBER/Borenstein archive, retaining literal carrier code `NA`. The older source audit intentionally left the supplied CSV untouched. Its statement that no values were restored described **v1 only**, now retained under [archive/v1/provenance](../archive/v1/provenance/). It is not the current data-loading rule.

Current records:

- [Analysis protocol](analysis_plan.md): fixed design sequence recorded before extension results; not historical preregistration.
- [Independent design review](design_review.md) and [code review](code_review.md): methodological and implementation boundaries.
- [Literature notes](literature_notes.md): primary citations, what was actually verified, and limits of inaccessible full texts.
- [Economic framing notes](economic_framing.md): mechanisms consistent with the available evidence.
- [Raw BTS source report](raw_data_discovery.md): source distinctions, raw schemas, field caveats and full Market download verification.
- [BTS Market manifest](bts_market/download_manifest.json), [verification](bts_market/verification_summary.json), [hashes](bts_market/SHA256SUMS.txt).

Scientific estimates come from `results/`, not from exploratory editorial notes. The latter preserve the reasoning and review record; occasional proposed checks in those notes are not claims that a model was run. Completed models are enumerated in the machine-readable registry.

No BTS raw data are silently substituted for the primary Borenstein market panel. Source reconciliation and reproducibility do not establish causal identification. The original CSV, original paper results, and prior public revision remain archived for inspection.

## Completed source and replication checks

The [current source identity audit](source_identity_audit.json) compares all 4,175,354 extracted records and all 11 fields with the Stata archive. Carrier and integer fields agree exactly; floating-point discrepancies are below 1.14e-13. The [ZIP-versus-CSV replication check](zip_csv_replication_check.json) compares every field in all 20 fitted models from separate complete pipeline runs. All 1,039 numeric model fields agree to numerical precision.

To repeat the source comparison from the repository root after downloading:

```sh
python scripts/verify_source_identity.py --input data/NBER_2005_2010.csv.gz --archive data/mktdata79q1to16q3.zip --out source_recheck
```

To compare independent archive- and CSV-based runs:

```sh
python analysis/extend_analysis.py --source data/mktdata79q1to16q3.zip --out results_from_zip
python analysis/extend_analysis.py --source data/NBER_2005_2010.csv.gz --out results_from_csv
python scripts/compare_saved_runs.py --reference results_from_zip/extended_results.json --candidate results_from_csv/extended_results.json --out source_recheck/replication.json
```

Source reconciliation, full-pipeline reproduction, and independent estimator verification test different parts of the workflow. None establishes a causal interpretation.
