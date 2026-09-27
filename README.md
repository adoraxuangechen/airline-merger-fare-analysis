# Fare Changes After the Delta–Northwest Merger: Market Composition and Competitive Exposure

**Research question:** How did fares change on airport pairs with substantial pre-merger Delta–Northwest overlap, and how much does that comparison depend on market composition?

This project uses **Borenstein's NBER-hosted market data for 2005–2010**. It reconstructs passenger-weighted airport-pair fares and compares changes across fixed, pre-announcement route groups. The primary analysis remains on this data source; newly retrieved BTS raw files are a separate documented resource.

**Revision: September 27, 2026.**

Accepted for poster presentation at the Econometric Society Summer School.

**Software and methods:** Python for data construction and estimation; R for HonestDiD and independent regression checks; Stata for independent fixed-effects replication. The design combines route and quarter fixed effects, event studies, baseline market-composition controls, and within-route carrier fare comparisons.

## Read the work

- [Writing sample — English PDF](papers/writing_sample_v2.pdf)
- [Technical supplement](papers/technical_supplement_v2.pdf)
- [Readable paper text](papers/writing_sample_v2.md)

## Main findings

| Comparison | Relative fare change | 95% interval | Treated / comparison routes |
|---|---:|---:|---:|
| Previous baseline | −5.72% | [−9.16%, −2.15%] |156 / 105|
| Same valid-distance sample, unadjusted | −5.58% | [−9.05%, −1.99%] |156 / 104|
| Distance-bin × quarter effects | −3.68% | [−7.18%, −0.05%] |156 / 104|
| Distance and baseline itinerary-composition × quarter effects | −2.45% | [−5.92%, 1.14%] |156 / 104|
| Legacy comparison, common support | −1.80% | [−5.69%, 2.26%] |133 / 35|
| Expanded comparison, common support | −4.95% | [−7.28%, −2.56%] |146 / 178|

Allowing different market types to follow different quarterly fare paths changes the estimate materially. Expanding the comparison population also matters. **Pre-merger fare differences remain after adjustment**, so these are conditional relative fare changes, not identified merger effects or consumer-welfare estimates. All planned diagnostics, including unfavorable ones, are saved in the [model registry](results/model_registry.csv).

The concentration extension reports operating-code shares, their coverage, a conditional single-carrier HHI, and a frozen-share merger-exposure proxy. It does not label incomplete carrier attribution as a regulatory firm-level HHI. Only four treated routes satisfy the sustained one-coupon-overlap rule; one coupon does not independently establish physical nonstop service.

## Reproduce

Python 3.12 or later is required; this revision was verified with Python 3.12. Run from this repository's root in a dedicated environment:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_nber.py
python analysis/extend_analysis.py --source data/NBER_2005_2010.csv.gz --out results_recheck
python analysis/independent_check.py --results results_recheck
```

The source download is about 212 MB and the extracted six-year CSV is compressed. Checksums prevent silently accepting a changed archive. The script preserves literal carrier code `NA`, selects 4,175,354 records, and never overwrites the source. To use an already downloaded archive:

```sh
python scripts/download_nber.py --archive /path/to/mktdata79q1to16q3.zip --out data/NBER_2005_2010.csv.gz
```

Alternatively, the analysis accepts the verified source ZIP directly. The earlier supplied CSV remains available through the [historical download instructions](archive/v1/data/README.md); it is retained for provenance rather than silently replaced. From the current repository root, use `python archive/v1/scripts/download_and_verify.py` to retrieve that historical input into the archive directory.

To rebuild the reviewed documents from the saved **current** `results/`:

```sh
python documents/build_reference_style.py --out papers_recheck
```

Document builds use Times New Roman on macOS or matplotlib's DejaVu Serif fonts and produce only the two English papers. The layout follows the author's reference article: centered title and abstract, numbered sections, three-rule tables, numbered equations, and hanging references. Numerical substitutions read the saved registries.

## Additional descriptive and sensitivity analyses

- [Raw mean fare paths](extensions/raw_fare_trends/README.md): nominal dollar levels for both primary route groups, with explicit equal-route averaging, alternative passenger weighting, and quarterly coverage.
- [Unadjusted-design breakdown](extensions/unadjusted_honestdid/README.md): the causal contrast underlying the unadjusted -5.58% regression loses exclusion of zero at approximately M=0.08 (tested crossing bracket 0.076-0.077). The [exact projection-weight audit](extensions/pooled_weight_audit/README.md) preserves early-2008 weights and explains why its post-effect plug-in contrast differs from the reported pooled coefficient. The equal-weight completion-period target gives the same bracket.
- [HonestDiD in R](extensions/honestdid/README.md): the authors' official package, fixed source commit, complete event covariance, and all sensitivity grids. The nine-quarter event-average target differs from the pooled main estimate. At M=0.5, the approximate robust interval is -34.4% to +42.0%; it does not establish the sign of a merger effect.
- [Carrier-composition diagnostics](extensions/carrier_diagnostics/README.md): baseline Southwest interactions and within-route DL/NW versus other operating-code fares, with all paired panels and independent checks.
- [Cross-language validation](extensions/cross_language/README.md): Six specifications actually re-estimated in R 4.5.3 and Stata 19.5. All samples and design ranks agree; maximum absolute coefficient/standard-error differences from Python are 2.14e-13 / 6.96e-16. Executed scripts, software versions, and full comparison tables are included.

Adding baseline WN-presence by quarter changes the legacy/expanded comparisons to -2.70%/-2.55%; share-bin interactions give -1.63%/+0.82%. These follow-up specifications are retained together. The within-route DL/NW-to-other-code fare ratio changes by +1.57% between 2007 and 2009-2010 (95% interval -0.70% to +3.89%). The other-code group pools single-carrier journeys with any recorded code other than DL or NW; it may include regional affiliates, including DL/NW affiliates. Mixed-code journeys are excluded. This descriptive ratio differs from the market-level comparison.


## Where to look

| Location | Contents |
|---|---|
|[analysis/](analysis/README.md)|Current source-to-results pipeline and independent validation|
|[documents/](documents/README.md)|English main paper, supplement, and PDF builders|
|[results/](results/README.md)|Saved panels, route features, estimates, event coefficients and figures|
|[data/](data/README.md)|Data access, source distinction and checksums|
|[provenance/](provenance/README.md)|Dated design log, source verification, literature notes and BTS manifests|
|[archive/v1/](archive/v1/README.md)|Preserved earlier paper, analysis, results and reconciliation|

The complete original-source data are larger than appropriate for ordinary Git tracking. Public download scripts, source URLs and cryptographic checksums make them reproducible. The large all-route intermediate is regenerated by the pipeline; selected analysis panels are included.

## What changed in this revision

The prior −5.72% design is reproduced before adding distance/service-composition controls, common support, expanded controls, competing-merger checks, route trends and concentration diagnostics. Source metadata and raw-download records are distinct from the economic argument. Theory motivates mechanisms; the paper does not infer collusion, efficiency gains or welfare from a fare coefficient.

The old approximately +5% result used different measurement and route definitions. Correcting only its fixed-effects implementation does not reverse its sign. That historical reconciliation remains [archived](archive/v1/results/specification_bridge.csv), separate from the current comparison-design extension.

Data attribution: Severin Borenstein, Market Data files; National Bureau of Economic Research, [Department of Transportation DB1A/DB1B](https://doi.org/10.60592/tb1p-9p78). Source documentation: [Borenstein's field and filtering description](https://faculty.haas.berkeley.edu/borenste/mktdata.htm). Raw BTS sources: [official archive](https://transtats.bts.gov/PREZIP/).

## Revision history and earlier drafts

The [public archive scope](archive/README.md) identifies three items retained only in the private preservation copy. Included historical PDFs and analysis files retain their original bytes; this release does not rewrite existing Git history.

The [revision history](provenance/revision_history.md) links the December 2025 course paper, the prior public writing sample, and an intermediate review snapshot. Original PDFs are preserved byte-for-byte with checksums. Existing Git history is retained; historical file dates and snapshot dates are recorded separately, without backdating commits. The current paper and replication commands above remain the entry point for current findings.
