# Text for the main paper

The adjusted event study implies a mean post-completion fare contrast of −3.67% relative to 2007Q4; this calendar-specific contrast differs from the pooled estimate. Under Rambachan and Roth's (2023) relative-magnitude restriction, allowing each post-period change in the untreated differential trend to be at most one-half of the largest pre-period change produces a 95% confidence set of approximately [−0.421, 0.351] log points (about −34% to +42%). The data therefore require strong restrictions on differential trends to pin down the sign of a causal effect.

# Methods appendix text

We apply the official HonestDiD R package, version 0.2.8, to the adjusted event study on the unchanged 260-route panel. The input contains eleven pre-period coefficients (2005Q1–2007Q3) and twelve post-period coefficients (2008Q1–2010Q4), omitting 2007Q4. The target is the equally weighted mean of the nine coefficients from 2008Q4 through 2010Q4. The first three post coefficients have zero target weight: they remain in the post vector to allow possible anticipation or announcement-period effects, rather than being treated as unaffected observations. No effect is assumed before 2008Q1. This target is not the pooled treated-by-post coefficient, which uses a different pre-period normalization.

Let δ_t denote the normalized differential counterfactual trend in the adjusted regression, with δ_0 = 0 at 2007Q4. The restriction bounds each absolute consecutive-quarter change after the reference period by M times the largest absolute consecutive-quarter change before it. We use M = 0, 0.5, 1, and 2, without sign or monotonicity restrictions. M = 0 imposes a flat post-period counterfactual difference, while permitting nonzero pre-period differences; it is not a claim that the pre-trend test passes. M = 1 is a sensitivity scenario, not an empirically established bound on recession-era differential shocks. The target averages periods four through twelve after the reference quarter, so the restriction permits substantial cumulative drift by the later quarters.

The input variance-covariance matrix is route-clustered CR1, using the main estimator's rank-based degrees-of-freedom adjustment. Its smallest eigenvalue is 0.000025603, and no positive-semidefinite correction was needed. All 23 coefficient estimates and standard errors reproduce the saved adjusted event-study results to within 7 × 10^−16 and 2 × 10^−16, respectively. HonestDiD's C-LF procedure uses its asymptotic Gaussian approximation; the ordinary target interval is accordingly based on the normal quantile. This differs slightly from the t-based convention used for the pooled regression table.

The official function createSensitivityResults_relativeMagnitudes was run with alpha = 0.05, the default least-favorable hybrid setting, and requested outer seed 20260927. The pinned multi-post-period implementation uses internal default seed 0 for its 1,000 least-favorable simulations; a subsequent source/runtime audit documents this behavior. Full test-inversion grids were saved. Grid spacings were 0.00015, 0.00105, 0.005, and 0.005 log points for the four M values; reported endpoints are numerical approximations within these resolutions. Every full grid rejected both outer endpoints, each sampled acceptance set formed a single component, and the grid points immediately outside the reported endpoints were rejected. A finite grid cannot mathematically exclude a feature narrower than its spacing. A coarse M = 2 pilot initially reached its bounds; the grid was expanded before computing the reported result.

| Restriction | Approximate 95% C-LF set, log points | Approximate percentage transformation |
|---|---:|---:|
| M = 0 | [−0.07245, −0.00225] | [−7.0%, −0.2%] |
| M = 0.5 | [−0.42085, 0.35090] | [−34.4%, 42.0%] |
| M = 1 | [−0.800, 0.730] | [−55%, 108%] |
| M = 2 | [−1.555, 1.485] | [−79%, 341%] |

The transformation is 100 × [exp(x) − 1] at each endpoint. These are confidence sets, not plug-in bias bounds: they account for estimation uncertainty in the pre-period coefficients. The large sets at positive M are a substantive sensitivity result. The method quantifies conclusions conditional on trend restrictions; it does not demonstrate that the selected comparison group identifies a population average treatment effect under arbitrary heterogeneous responses.

# Citation

Rambachan, Ashesh, and Jonathan Roth. 2023. “A More Credible Approach to Parallel Trends.” *Review of Economic Studies* 90 (5): 2555–2591. https://doi.org/10.1093/restud/rdad018.

Official package: https://github.com/asheshrambachan/HonestDiD, commit 6813f02ed38f0b63bdca6915604b2eac90491303 (version 0.2.8).
