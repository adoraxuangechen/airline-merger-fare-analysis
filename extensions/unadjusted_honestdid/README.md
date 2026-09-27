# Unadjusted HonestDiD breakdown values

This extension evaluates sensitivity of the **unadjusted route-and-quarter model** to departures from parallel trends. Two explicit targets are reported. Neither numerical target should be relabeled as the pooled −5.58% coefficient.

1. **Nine-quarter event-study mean:** the average of 2008Q4–2010Q4 event coefficients relative to 2007Q4; its point estimate is about −8.00%. This uses exactly the calendar and target weights of the adjusted HonestDiD exercise, but omits the distance/service-composition controls.
2. **Pooled-associated causal functional:** the post-period component implied by an independently audited FWL decomposition of the pooled coefficient. Its plug-in point estimate is about −7.54%. It preserves the three negative 2008Q1–Q3 weights; it is a completion-versus-early-effect contrast, not a simple post-completion average.

The exact coefficient bridge in log units is

**−0.05744525 = +0.02099203 − 0.07843727.**

The left side is the pooled coefficient (−5.58%). The first right-hand component comes from the eleven pre-reference event coefficients. The second is the pooled-associated post functional. Under zero effects before 2008Q1, the post functional is the component associated with the pooled projection's causal response. The pre-period nuisance contribution is retained in the bridge and is not silently subtracted from, or shifted into, a confidence interval. Exponentiated percentages are not additive; the identity is in log units.

## Findings and meaning

Both targets reject a zero effect at M = 0. Their first observed transition to accepting zero occurs between **M = 0.076 and M = 0.077**, so the reported numerical breakdown is **approximately 0.08**. This means that the negative inference is sensitive even when the permitted post-period quarterly differential-trend change is about 8% of the largest pre-period quarterly change. M is a multiplier, not a percentage-point change in fares, and it is an assumption on the counterfactual differential trend rather than on observed fare movements.

The full acceptance registry records all tested M values. The sampled sequences are monotone, the local M resolution is 0.001, and direct zero tests agree with official full-confidence-set inversions at both bracket endpoints. A finite M grid does not prove the global continuous infimum between every pair of sampled points. The simulation-based critical values also have numerical approximation error; the bracket should not be presented as an exact population constant.

All specifications omit 2007Q4 and permit effects from 2008Q1. Rebasing the descriptive nine-quarter contrast to 2008Q3 would give about −3.50%, but a sensitivity exercise with that reference would change its unaffected-period assumptions. The reported breakdown values retain the 2007Q4 calendar. Changing an event-study reference does not change the separately estimated pooled −5.58% coefficient.

## Statistical and software details

The unchanged input has 260 routes and 6,235 route-quarters. Complete event coefficients and their route-clustered CR1 covariance are exported and checked against the saved unadjusted event study. An independent full-dummy reconstruction agrees with the covariance to below 4e-16. No PSD correction is applied.

The official HonestDiD 0.2.8 package at commit `6813f02ed38f0b63bdca6915604b2eac90491303` supplies all tests. `run_breakdown.R` calls its exported `computeConditionalCS_DeltaRM` at the singleton theta grid `{0}`, using C-LF, alpha 0.05, and hybrid_kappa 0.005. A singleton grid directly tests membership of zero; it does not estimate a full confidence-set endpoint. Expected open-grid warnings when zero is accepted are saved as such; other warnings fail the run. `validate_full_grids.R` independently invokes `createSensitivityResults_relativeMagnitudes` on a grid from −0.25 to 0.10 with 0.001 spacing, including zero exactly. Both outer grid endpoints are rejected.

External seed argument 20260927 is passed, but this fixed package version's multi-post branch uses internal LF defaults **seed 0 and 1,000 simulations**. `software_seed_audit.md` links the exact official source lines; the runtime audit confirms these values for both the existing adjusted analysis and this unadjusted analysis. The official algorithm was not modified.

The official implementation accepts arbitrary nonzero `l_vec` vectors, including the pooled-associated target's negative early-period weights; its invertible Gamma construction and successful full-grid runs verify compatibility. The weights are never normalized to sum to one.

## Reproduce

From `repository/extensions/unadjusted_honestdid/`, using the repository's Python environment:

```sh
python export_eventstudy.py --repository ../..
python ../pooled_weight_audit/audit_pooled_weights.py --repository ../.. --out ../pooled_weight_audit
```

Then import the independently audited weights and run the sensitivity calculations:

```sh
python prepare_pooled_target.py --audit-directory ../pooled_weight_audit
Rscript install.R
Rscript run_breakdown.R
Rscript run_breakdown.R probe .025 .03 .035 .04 .045 .055 .06 .065 .07 .075 .08 .085 .09 .095
Rscript run_breakdown.R probe .005 .015 .076 .077 .078 .079
Rscript validate_full_grids.R .076 .077
Rscript run_breakdown.R --weights pooled_target_weights.csv probe 0 .05 .07 .075 .08 .09 .1
Rscript run_breakdown.R --weights pooled_target_weights.csv probe .01 .02 .03 .04 .06 .065 .076 .077 .078 .079
Rscript validate_full_grids.R --weights pooled_target_weights.csv .076 .077
Rscript audit_internal_seed.R
python summarize_breakdown.py
```

`install.R` installs the fixed official source and dependencies into an extension-local `Rlibrary`; it does not modify global R packages. The numerical scripts can also use the sibling adjusted extension's local library. The source download needs network access and git. Do not edit running R scripts while a process is reading them.

`published_files.json` lists the small files to include in the replication package. Do not copy `.cache/`, `Rlibrary/`, or the non-authoritative failed diagnostic log `local_probe.log`. The initial failed probe was completely rerun; only successful CSV/RDS outputs enter `breakdown_results.json`.
