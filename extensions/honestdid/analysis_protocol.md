# HonestDiD sensitivity protocol

Specification fixed before sensitivity results were inspected (September 27, 2026). This is a contemporaneous extension protocol, not a historical preregistration.

## Question and estimand

Apply the authors' official HonestDiD R implementation to the distance-bin-by-quarter and baseline one-coupon-share-bin-by-quarter adjusted event-study model on the unchanged 260-route, 6,235-observation panel. The event-study omits 2007Q4. The eleven pre coefficients span 2005Q1–2007Q3; twelve post coefficients span 2008Q1–2010Q4. The target is the equal-quarter mean of the nine coefficients for 2008Q4–2010Q4. Its twelve-element weight vector is (0, 0, 0, 1/9, ..., 1/9).

Using 2007Q4 avoids normalizing to the merger announcement period. Treating all of 2008 as potentially affected allows effects or anticipation from 2008Q1 onward; the first three quarters receive zero target weight but remain in the post coefficient vector. This does not prove that anticipation was absent before 2008. The target differs from the pooled treated-by-post coefficient, whose pre-period includes earlier quarters and the announcement window. The two numbers must not be presented as competing estimates of exactly the same contrast.

With these fixed-effect controls, the target is the adjusted regression contrast. Interpreting it as an average causal effect additionally requires an appropriate conditional counterfactual-trend model and restrictions on effect heterogeneity/weights. HonestDiD does not itself establish that the comparison group identifies an ATT.

## Assumption and method

Write delta_t for the normalized untreated difference between the two groups after projecting out the chosen controls, with delta_0 = 0 at 2007Q4. The relative-magnitude restriction is

|delta_(t+1) - delta_t| <= Mbar * max_(s<0) |delta_(s+1) - delta_s| for every post transition t >= 0.

Thus Mbar bounds *consecutive-quarter changes* in the differential counterfactual trend, not each coefficient's absolute distance from zero. The four requested scenarios are Mbar in {0, 0.5, 1, 2}. Mbar = 0 imposes flat post counterfactual differences relative to the reference; it does not require zero pre-period differences. Mbar = 1 is a sensitivity scenario, not a validated economic fact; the recession could cause larger differential shocks. Longer-horizon effects permit cumulative drift, so their robust sets may be wide.

Use createSensitivityResults_relativeMagnitudes with method = 'C-LF', alpha = 0.05, default hybrid_kappa = alpha/10, no sign or monotonicity restriction, and a fixed simulation seed of 20260927. The event-study covariance is route-cluster CR1, identical to the main estimator; HonestDiD uses its asymptotic Gaussian approximation. The ordinary target interval from constructOriginalCS therefore uses a normal quantile, while the paper's pooled interval uses t_(259). Both are separately recorded.

## Numerical checks

Export all 23 coefficients and their full 23-by-23 covariance, verify the existing event-study registry to 1e-10, require positive definiteness, and record source-panel SHA-256. First run a coarse inversion to locate the accepted region. Refine the inversion grid with explicit endpoints; report grid spacing and inspect both endpoints for acceptance. If either endpoint is accepted, expand the grid rather than reporting a truncated interval. Capture the official lower-level return grids without changing the algorithm, detect disconnected accepted components, and report the envelope only as such if disconnections occur. Numerical endpoint error is controlled by grid spacing; it is separate from statistical uncertainty.

## Sources

- Rambachan, Ashesh, and Jonathan Roth. 2023. 'A More Credible Approach to Parallel Trends.' Review of Economic Studies 90(5): 2555–2591. DOI: https://doi.org/10.1093/restud/rdad018. Author-hosted full text: https://www.jonathandroth.com/assets/files/HonestParallelTrends_Main.pdf (Sections 2.4.1 and 6).
- Official software: https://github.com/asheshrambachan/HonestDiD, version 0.2.8, commit 6813f02ed38f0b63bdca6915604b2eac90491303. Package manuals and source were inspected on September 27, 2026.

## Subsequent implementation clarification

The planned outer seed 20260927 was passed as recorded above. The September 27 follow-up source/runtime audit established that the pinned package's multi-post branch does not forward it to the least-favorable simulation helper, which instead uses its defaults seed 0 and 1,000 simulations. Original outputs are retained unchanged. This addendum records observed software behavior; it does not rewrite the original computational plan.
