# Airline Merger Fare Analysis

Python analysis of route-level fares around the Delta–Northwest merger, using a DB1B-derived market-summary dataset covering 2005–2010.

## Research question and approach

How do fare patterns differ between routes with pre-merger Delta/Northwest overlap and comparison routes? The workflow constructs passenger-weighted route-quarter fares, defines exposure using 2007 carrier presence, estimates route and quarter fixed-effects models, examines pre-period trends, and checks sensitivity to route definitions and weighting.

**Interpretation:** Pre-period trend differences limit causal interpretation. Regression contrasts should not be described as the causal effect of the merger. Different route definitions target different populations. Input rows are market/carrier/service summaries, not individual tickets; the code does not establish ticket-level fare dispersion or a coordination mechanism.

## Contents

- `run_analysis.py`: runs the complete analysis pipeline.
- `inspect_data.py`: checks schema, missingness, duplicate keys and input hash.
- `prepare.py`: constructs the route-quarter panel and exposure classifications.
- `estimator.py`: within estimator with route-clustered standard errors.
- `estimate.py`: baseline estimates, event studies, weighting/matching checks and a numerical comparison with explicit fixed effects.
- `check_scope.py` and `check_full_panel.py`: alternative sample definitions.
- `make_figures.py`: produces figures and LaTeX result tables.
- `environment.json`: environment recorded in the September 2026 source package.

## Run locally

Use Python 3.12 and install the recorded dependencies:

```sh
python -m pip install -r requirements.txt
python run_analysis.py --input "/path/to/DB1B_2005_2010.csv"
```

The input dataset is **not included**. Required columns are `yr`, `qtr`, `cr1`, `cr2`, `cop`, `ap1`, `ap2`, `pax`, `avprc`, `nsdst`, and `avdst`. Supply the same preprocessed DB1B-derived schema used by this project; an arbitrary raw BTS download is not a drop-in replacement. Airport pairs are treated as directed routes. See `prepare.py` for the precise carrier and service definitions.

Outputs are written alongside the scripts and excluded from version control: panel data, classifications, audit summaries, regression results, figures, and table fragments. Running on a different input may change results or invalidate assumptions.

## Provenance and validation status

Analysis scripts are taken from the September 8, 2026 revised replication package for Xuange (Adora) Chen. This code-only repository omits manuscript files, stored results and datasets; the optional PDF-build switch was removed from the runner. Statistical code is otherwise preserved.

The original package records this expected input SHA256:
`68822d60114c61af9f6ce8d9084aa20276f0d5b1b64a9a80b0e372929f1d19cb`.

The runner prints the supplied file hash but does not enforce a match. Before public portfolio use, reproduce results with the intended dataset and review assumptions. Initial upload checks cover Python syntax and command-line help, not a fresh end-to-end replication.
