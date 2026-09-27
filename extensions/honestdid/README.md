# HonestDiD sensitivity extension

This extension applies the authors' **official HonestDiD R package** to the saved, adjusted Delta–Northwest event study. It does not alter the main analysis or its input panel. The main result is sensitivity: even M = 0.5 gives a wide confidence set containing both positive and negative effects. A failure of the pre-trend test is not treated as a reason to stop at a diagnostic; this exercise states explicit counterfactual-trend restrictions and reports what follows under them.

## Files to read

- `manuscript_text.md`: ready-to-edit main-paper paragraph, methods appendix, and citation.
- `analysis_protocol.md`: estimand, timing, assumptions, numerical plan, and sources.
- `sensitivity_summary.csv` / `sensitivity_results.json`: complete results and numerical audit.
- `event_coefficients_full.csv` / `event_covariance.csv`: all 23 coefficients and their full covariance.
- `event_export_metadata.json`: source checksum, CR1 factor, rank, eigenvalues, and reproduction errors.
- `single_*_grids/`: full official test-inversion acceptance grids.
- `single_*_sensitivity.rds`: exact R inputs, outputs, settings, and session information.
- `R_dependency_versions.csv`, `R_sessionInfo.txt`, `official_source_version.txt`: computational provenance.
- `honestdid_sensitivity.pdf` / `.png`: sensitivity plot in log points.
- `artifact_checksums.json`: SHA-256 checksums for the published extension files.

`pilot*` and `widepilot*` files document numerical exploration of the inversion domain, not model selection. The first coarse M = 2 pilot was truncated at the initially chosen domain [-1, 1]; the final expanded grid rejects both domain endpoints. All final sampled acceptance sets have one connected component. No main-paper result uses the truncated pilot.

## Reproduce

From this directory after it is placed at `repository/extensions/honestdid/`:

```sh
python export_eventstudy.py --repository ../..
Rscript install.R
Rscript run_honestdid.R single_0 0
Rscript run_honestdid.R single_05 0.5
Rscript run_honestdid.R single_1 1
Rscript run_honestdid.R single_2 2
python summarize_results.py
```

Use the repository's Python environment and requirements. R 4.5.3 was used for the saved outputs. `install.R` requires internet access and git. It fetches the official GitHub repository at commit `6813f02ed38f0b63bdca6915604b2eac90491303`, installs version 0.2.8 and dependencies into this directory's `Rlibrary`, and records package versions. It does not install or modify global R packages. On systems without binary packages, compiler/system dependencies for the R packages may be needed. The first installation can therefore take longer than the numerical calculation.

The extension locates its R library relative to its own script, not the launch directory. The Python exporter accepts an explicit repository path and also recognizes the packaged directory layout. R dependencies are recorded for reproducibility; exact historical dependency versions are not automatically locked by this lightweight installer.

Do not package `Rlibrary/`, `.cache/`, or a git checkout of the official package. The fixed-commit installer reconstructs the official source and the local environment. These folders are ignored in `.gitignore`.

## Statistical interpretation

The target is the average of nine event coefficients from 2008Q4–2010Q4 relative to 2007Q4. It equals −0.0373887 log points (−3.67%) and differs from the pooled −2.45% estimate because of its calendar and normalization. The twelve-post-period weight vector assigns zero weight to 2008Q1–Q3, allowing anticipation/announcement-period effects in those quarters. No anticipation is assumed before 2008Q1.

Relative-magnitude M bounds consecutive-quarter changes in the differential counterfactual trend, not absolute event-coefficient levels. M = 0 permits pre-period nonparallelism but requires a flat post-period counterfactual difference. Positive M permits cumulative drift; this accounts for the wide intervals for an outcome averaged over quarters four through twelve after the reference period. M is an assumption, not an estimated or validated cutoff. The method does not establish that a controlled regression contrast equals a population ATT under arbitrary treatment-effect heterogeneity.

The saved confidence sets are the official C-LF outputs, including uncertainty in the pre-period coefficients. They are not a home-made point estimate plus a plug-in worst-case bias. Final inversion resolutions are 0.00015, 0.00105, 0.005, and 0.005 log points. Adjacent rejected points bracket every reported endpoint; the grids are finite numerical approximations, so endpoint precision should not be overstated. No PSD adjustment was applied to the covariance matrix.

## Implementation audit: effective least-favorable simulation seed

The scripts pass the requested outer seed 20260927. A follow-up audit of the pinned official source and runtime shows that its multi-post-period branch uses the internal default seed 0 and 1,000 least-favorable simulations. This also applies to these saved adjusted results. The clarification changes no estimates or confidence sets; the source version and defaults make them reproducible. The corresponding source links and argument trace are saved in the unadjusted sensitivity extension's `software_seed_audit.md` and `internal_seed_runtime_audit.csv`.
