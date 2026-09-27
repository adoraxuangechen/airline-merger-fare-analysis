# Revision analysis protocol — September 27, 2026

Historical planning record, retained to document the initial design sequence. Publication-status language below describes the plan at capture time; current publication is authorized separately.

This records the extension design before inspecting extension coefficients. It is a dated analysis log, not a historical preregistration. The existing -5.72% baseline and group imbalances are already known.

## Primary data and immutable inputs

Use the NBER/Borenstein market-data archive, selecting 2005–2010 and retaining literal carrier code NA. Preserve the supplied CSV and old published outputs. Compare the reconstructed source to the prior input and report any effect of source restoration. BTS raw Market/Coupon files are a separate source and will not be silently spliced into this panel.

## Fixed sequence

1. Reproduce the published 261-route, 6,259-cell baseline.
2. Exclude the zero-distance sentinel from distance-adjusted comparisons; report the same-sample unadjusted estimate.
3. Add distance-bin × quarter fixed effects using baseline distance bins [0,750), [750,1500), [1500,2000), [2000,infinity).
4. Add baseline one-coupon-share-bin × quarter fixed effects with bins [0,.1), [.1,.5), [.5,.9), [.9,1]. Covariates remain fixed at 2007 values; no post-merger service shares enter the main adjustment.
5. Restrict to joint baseline distance/share cells containing at least 3 treated and 3 comparison routes, and absorb joint-cell × quarter effects. Show exclusions and baseline balance. This changes the estimand to routes with observed support; it is not a full-sample ATT.
6. Replace the legacy restriction with all eligible routes with no observed DL/NW during 2007, retaining the same treated definition. Run unadjusted, adjusted and common-support specifications. Do not assume an LCC-only comparison is unaffected by merger/network shocks.
7. Report a pooled DID with route-specific linear trends as sensitivity only. Do not combine unrestricted route trends with an unidentified saturated event specification.
8. Run pre-specified time/contamination checks: end in 2009; omit routes with any 2007 UA/CO presence; start in 2006 (after HP/US completion). Report sample sizes even if a comparison becomes weak.
9. Compute 2007 baseline operating-code concentration measures using all recorded codes. Distinguish single-carrier normalized HHI, its coverage, and frozen-share mechanical DL/NW overlap exposure from true economic-firm HHI. Use delta=2*sDL*sNW (shares on0–1 scale, HHI×10000). Show continuous interaction per 100 HHI points and high/low exposure interactions; retain labels making proxy status explicit.
10. Count sustained one-coupon overlap using the same quarterly5%/3-of4 rule; if too few routes, report the count and decline a misleading well-powered subgroup claim. Retain loose annual100-pax criterion only as a clearly labeled descriptive comparison.

## Diagnostics and reporting

Report every planned model, standard errors clustered by route, coefficients/intervals/sample counts, full event paths with2007Q4 as reference, and a joint test of2005–2007 leads. Test results are diagnostics, not a model-selection rule. No specification is preferred because it changes sign, becomes significant or passes a pre-test. Common airport/network dependence remains a limitation. Verify absorbed coefficients and CR1 standard errors against an explicit-dummy implementation on an actual-data subset. Keep economic theory as competing mechanisms, not a test of tacit collusion or welfare.

## Delivery and publication

Prepare a new concise writing sample, technical supplement, Chinese change/data explanation, complete code/results and a local GitHub-ready revision. User reviews before any remote publication. Current website and GitHub remain unchanged until approval.
