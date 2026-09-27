* Independent Stata validation of the already constructed Borenstein panels.
* Usage: stata-mp -b do validate_models.do REPOSITORY_DIRECTORY OUTPUT_DIRECTORY
version 19.0
clear all
set more off
set type double
set linesize 140
args repo out
if `"`repo'"' == "" | `"`out'"' == "" {
    display as error "Usage: do validate_models.do REPOSITORY_DIRECTORY OUTPUT_DIRECTORY"
    exit 198
}
capture mkdir `"`out'"'
* Suppress full regression tables and retain only explicitly selected statistics.
* No license identifiers are written into the portable results below.
file open meta using `"`out'/stata_version.txt"', write replace
file write meta "Stata version: `c(stata_version)'" _n
file write meta "Flavor: `c(flavor)'" _n
file write meta "OS: `c(os)'" _n
file close meta

tempname results
postfile `results' str50 model str8 language double N double routes double rank double df_resid double b double se double lo double hi double p double pct double pct_lo double pct_hi using `"`out'/stata_model_results.dta"', replace

foreach sample in legacy expanded {
    if "`sample'" == "legacy" local input panel_legacy_valid.csv
    else local input panel_all_unexposed.csv
    quietly import delimited using `"`repo'/results/`input'"', clear varnames(1) case(preserve) asdouble
    encode route, gen(routeid)
    generate double did = treated * (t >= 16)
    generate byte wn_present = wn_2007 > 0
    assert !missing(lnfare,did,routeid,t,distance_bin,share_bin,wn_present)
    local modelcount=1
    if "`sample'" == "legacy" local modelcount=3
    forvalues m=1/`modelcount' {
        local extra ""
        local name same_sample_unadjusted
        if `m'==2 {
            local extra "i.distance_bin#i.t"
            local name distance_quarter
        }
        if `m'==3 {
            local extra "i.distance_bin#i.t i.share_bin#i.t"
            local name distance_and_composition_quarter
        }
        if "`sample'"=="expanded" {
            local extra "i.distance_bin#i.t i.share_bin#i.t"
            local name all_controls_adjusted
        }
        quietly regress lnfare did i.routeid i.t `extra', vce(cluster routeid)
        * e(rank) is the rank of the cluster covariance, not the design rank.
        quietly _ms_omit_info e(b)
        mata: st_numscalar("designrank", cols(st_matrix("e(b)")) - sum(st_matrix("r(omit)")))
        scalar bet = _b[did]
        scalar serr = _se[did]
        scalar crit = invttail(e(N_clust)-1,.025)
        scalar low = bet-crit*serr
        scalar high = bet+crit*serr
        post `results' ("`name'") ("Stata") (e(N)) (e(N_clust)) (designrank) (e(N)-designrank) (bet) (serr) (low) (high) (2*ttail(e(N_clust)-1,abs(bet/serr))) (100*(exp(bet)-1)) (100*(exp(low)-1)) (100*(exp(high)-1))
        display "VALIDATED_MODEL `name' N=" e(N) " routes=" e(N_clust) " beta=" %21.16g bet " se=" %21.16g serr
    }
    quietly regress lnfare did i.routeid i.t i.distance_bin#i.t i.share_bin#i.t i.wn_present#i.t, vce(cluster routeid)
    local name `sample'_adjusted_wn_present
    * e(rank) is the rank of the cluster covariance, not the design rank.
        quietly _ms_omit_info e(b)
        mata: st_numscalar("designrank", cols(st_matrix("e(b)")) - sum(st_matrix("r(omit)")))
        scalar bet = _b[did]
    scalar serr = _se[did]
    scalar crit = invttail(e(N_clust)-1,.025)
    scalar low = bet-crit*serr
    scalar high = bet+crit*serr
    post `results' ("`name'") ("Stata") (e(N)) (e(N_clust)) (designrank) (e(N)-designrank) (bet) (serr) (low) (high) (2*ttail(e(N_clust)-1,abs(bet/serr))) (100*(exp(bet)-1)) (100*(exp(low)-1)) (100*(exp(high)-1))
    display "VALIDATED_MODEL `name' N=" e(N) " routes=" e(N_clust) " beta=" %21.16g bet " se=" %21.16g serr
}
postclose `results'
use `"`out'/stata_model_results.dta"', clear
format N routes rank df_resid %18.0f
format b se lo hi p pct pct_lo pct_hi %24.17g
export delimited using `"`out'/stata_model_results.csv"', replace datafmt
file open complete using `"`out'/stata_execution_status.txt"', write replace
file write complete "Successful completion: all six specified regressions executed in installed Stata." _n
file close complete
exit, clear
