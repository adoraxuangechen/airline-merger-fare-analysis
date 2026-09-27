# Audit of the pooled regression's event-coefficient weights

This audit reads the existing 260-route, 6,235-observation panel and does not change the canonical analysis or run HonestDiD. The unadjusted pooled regression uses route and quarter fixed effects and treats 2008Q4–2010Q4 as the completion-and-later period. The event regression omits 2007Q4 and has 23 treated-quarter coefficients.

## Exact algebra and independent checks

Let Z contain the route and quarter fixed effects, D the treated × completion-and-later indicator, and E the 23 treated-quarter indicators. A tilde denotes residualization on Z. Since D is the sum of E's nine completion-and-later columns, the pooled coefficient satisfies

    beta_pool = (D_tilde' y_tilde) / (D_tilde' D_tilde)
              = a' b_event,
    a' = (D_tilde' E_tilde) / (D_tilde' D_tilde).

The script constructs full dummy matrices and uses QR projection. It independently checks the result using (1) route demeaning followed by transformed-quarter residualization and (2) direct least squares on the full dummy models. A synthetic effect path with eleven zero pre-treatment effects additionally verifies that a direct pooled regression of its generated causal outcome equals the post-only effect functional. It reconstructs both regressions' route-clustered CR1 covariance matrices without importing the production estimator. The full event covariance matches the independently generated HonestDiD extension covariance to a maximum absolute difference of 3.1e-16. All coefficient and weight checks differ by less than 6e-14.

## Results and interpretation

The exact point-estimate identity is

    -0.0574452476522 = +0.0209920259024 - 0.0784372735545,
                         pre-2008 term      2008–2010 term

The left-hand side transforms to −5.58264153%. The first right-hand term is the weighted contribution of the eleven estimated pre-period event coefficients, excluding the reference quarter. It is an observed contribution, not a claim that the true pre-period merger effects are nonzero.

Assume merger effects are zero through 2007Q4. If the event-coefficient population model is b = tau + delta, the causal component associated with the pooled projection is then theta = a_post' tau_post, with twelve post-period effects from 2008Q1 to 2010Q4. This retains the negative weights for 2008Q1–Q3, so it is a contrast between completion-and-later effects and early-2008 effects. No assumption of zero early-2008 effects is added by this audit.

The first three post weights are each approximately −0.0667762; the nine completion-and-later weights sum to 1. The entire twelve-weight vector sums to 0.7996713645 and must not be normalized. The post-only plug-in value a_post' b_post is −0.07843727355, whose exponential transformation is −7.54399475%. This is the plug-in estimate for the pooled-associated causal functional in the HonestDiD representation. It is not a replacement estimate of the observed pooled coefficient and should not be labeled as the pooled −5.58% result. The twelve-quarter functional also differs from the separate equal-weight nine-quarter event-study target.

The omitted 2007Q4 coefficient is normalized to zero. For completeness, its implicit weight is −0.06677621185; including that weight gives a zero-sum, 24-quarter contrast. With zero effects in the reference quarter, this term contributes zero to the causal functional.

The post-only plug-in standard error from the full event covariance is 0.01675363726 log points. The exact coefficient identity does not imply identical pooled and event-based standard errors: the pooled and saturated event regressions use different fitted residuals and residual degrees of freedom. HonestDiD should use the full event coefficients and covariance, with the supplied post weights, without recentering its output on the observed pooled coefficient or substituting the pooled standard error.

## Files and replication

- `audit_pooled_weights.py`: self-contained derivation and numeric checks.
- `full_event_pooled_weights.csv`: all 23 event coefficients and weights, in chronological order excluding 2007Q4.
- `post_target_weights.csv`: the exact 12-element post-period vector for HonestDiD, 2008Q1–2010Q4.
- `independent_event_covariance.csv`: independently reconstructed, calendar-labelled event covariance.
- `audit_summary.json`: machine-readable results, checks, environment versions and input checksum.

From the repository root, run with Python, NumPy, pandas and SciPy installed:

    python extensions/pooled_weight_audit/audit_pooled_weights.py --repository . --out pooled_weights_recheck

The output directory defaults to this audit directory. The optional covariance cross-check runs when the sibling `unadjusted_honestdid/event_covariance.csv` is present.
