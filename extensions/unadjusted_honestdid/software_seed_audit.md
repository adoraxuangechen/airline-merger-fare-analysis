# Effective simulation seed in the pinned official software

Software: official HonestDiD 0.2.8, commit `6813f02ed38f0b63bdca6915604b2eac90491303`.

Both the adjusted and unadjusted applications have twelve post-period coefficients. In this version, the multi-post branch of `.computeConditionalCS_DeltaRM_fixedS` calls `.ARP_computeCI` without a seed argument. `.ARP_computeCI` then calls `.compute_least_favorable_cv` without forwarding a seed or simulation count. The helper defaults are therefore **seed = 0 and sims = 1000**, and it explicitly calls `set.seed(seed)`.

Permanent source references:

1. [`R/deltarm.R`, lines 236–244](https://github.com/asheshrambachan/HonestDiD/blob/6813f02ed38f0b63bdca6915604b2eac90491303/R/deltarm.R#L236-L244): multi-post nuisance branch and call to `.ARP_computeCI`.
2. [`R/arp-nuisance.R`, lines 735–740](https://github.com/asheshrambachan/HonestDiD/blob/6813f02ed38f0b63bdca6915604b2eac90491303/R/arp-nuisance.R#L735-L740): least-favorable helper call, with neither `seed` nor `sims` specified.
3. [`R/arp-nuisance.R`, lines 351–352](https://github.com/asheshrambachan/HonestDiD/blob/6813f02ed38f0b63bdca6915604b2eac90491303/R/arp-nuisance.R#L351-L352): defaults `sims = 1000` and `seed = 0`.
4. [`R/arp-nuisance.R`, line 386](https://github.com/asheshrambachan/HonestDiD/blob/6813f02ed38f0b63bdca6915604b2eac90491303/R/arp-nuisance.R#L386): internal seed initialization.

The application scripts pass an external seed argument of 20260927. It is accurate to record that argument, but it should not be described as the effective seed for these multi-post least-favorable simulations. The single-post branch behaves differently and explicitly passes its seed; it is not used here.

`audit_internal_seed.R` traces function-entry arguments without changing them or replacing the statistical algorithm. It evaluates M = 0 for both the saved adjusted target and the unadjusted nine-quarter target. `internal_seed_runtime_audit.csv` records 22 helper calls for each specification (eleven possible pre-period maximum locations, each with two signs). All 44 calls use seed 0 and 1,000 simulations. These observations confirm that the source-based inference applies to the already saved adjusted analysis as well as to the current unadjusted extension.

This clarification does not change any estimates or confidence sets. The fixed source version, package environment, and internal defaults make the outputs reproducible. Reported M-search resolution concerns the parameter search, not a claim that the simulation-based critical values have zero Monte Carlo approximation error.
