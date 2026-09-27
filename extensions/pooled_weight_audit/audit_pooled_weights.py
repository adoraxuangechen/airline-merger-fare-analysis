#!/usr/bin/env python3
"""Independently derive pooled-TWFE weights on the full unadjusted event vector.

Only reads the existing analysis panel/registries and writes this audit directory.
No production estimator is imported. No HonestDiD model is run.
"""
from pathlib import Path
import argparse, hashlib, json, platform
import numpy as np
import pandas as pd
import scipy
from scipy import linalg


def qr_residualize(z, values):
    q, r, piv = linalg.qr(z, mode='economic', pivoting=True)
    rank = int(np.linalg.matrix_rank(r))
    q = q[:, :rank]
    return values - q @ (q.T @ values), rank


def cluster_cov(x, residual, groups, nuisance_rank):
    n, k = x.shape
    g = len(np.unique(groups))
    scores = np.zeros((g, k))
    np.add.at(scores, groups, x * residual[:, None])
    bread = linalg.inv(x.T @ x)
    cr1 = g / (g - 1) * (n - 1) / (n - nuisance_rank - k)
    return cr1 * bread @ scores.T @ scores @ bread, cr1


def main():
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    default_repo = here.parents[1] if (here.parents[1]/'results/panel_legacy_valid.csv').exists() else here.parent/'repository'
    parser.add_argument('--repository', type=Path, default=default_repo)
    parser.add_argument('--out', type=Path, default=here)
    args = parser.parse_args()
    results = args.repository.resolve()/'results'
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    panel_path = results/'panel_legacy_valid.csv'
    p = pd.read_csv(panel_path)
    assert len(p) == 6235 and p.route.nunique() == 260
    assert p.groupby('route').treated.nunique().max() == 1
    assert p[['route','t']].duplicated().sum() == 0
    n = len(p)
    route_codes, route_labels = pd.factorize(p.route, sort=True)
    route_dummies = np.eye(len(route_labels))[route_codes]
    quarter_codes = p.t.to_numpy(dtype=int)
    quarter_dummies = np.column_stack([quarter_codes == t for t in range(2,25)]).astype(float)
    z = np.column_stack([route_dummies, quarter_dummies])
    treated = p.treated.to_numpy(dtype=float)
    event_quarters = [t for t in range(1,25) if t != 12]
    e = np.column_stack([treated * (quarter_codes == t) for t in event_quarters])
    d = treated * (quarter_codes >= 16)
    y = p.lnfare.to_numpy()
    assert np.array_equal(d, e[:, np.array(event_quarters) >= 16].sum(axis=1))
    residuals, rank_z = qr_residualize(z, np.column_stack([y,d,e]))
    y_res, d_res, e_res = residuals[:,0], residuals[:,1], residuals[:,2:]
    beta_pool = float(d_res @ y_res / (d_res @ d_res))
    a = d_res @ e_res / (d_res @ d_res)
    b_event = linalg.lstsq(e_res, y_res, lapack_driver='gelsy')[0]
    beta_via_weights = float(a @ b_event)
    covariance_event, cr1_event = cluster_cov(e_res, y_res-e_res@b_event, route_codes, rank_z)
    covariance_pool, cr1_pool = cluster_cov(d_res[:,None], y_res-d_res*beta_pool, route_codes, rank_z)

    # Independent construction: route demeaning first, then transformed quarter projection.
    vals = np.column_stack([y,d,e,quarter_dummies])
    sums = np.zeros((len(route_labels), vals.shape[1]))
    np.add.at(sums, route_codes, vals)
    counts = np.bincount(route_codes)
    demeaned = vals - (sums/counts[:,None])[route_codes]
    yy, dd, ee, qq = demeaned[:,0],demeaned[:,1],demeaned[:,2:25],demeaned[:,25:]
    coeff_quarters = linalg.lstsq(qq, np.column_stack([yy,dd,ee]), lapack_driver='gelsy')[0]
    rr = np.column_stack([yy,dd,ee])-qq@coeff_quarters
    beta_demean = float(rr[:,1]@rr[:,0]/(rr[:,1]@rr[:,1]))
    a_demean = rr[:,1]@rr[:,2:]/(rr[:,1]@rr[:,1])

    # Independent direct full-dummy OLS, with no explicit FWL transformation.
    full_pool = linalg.lstsq(np.column_stack([z,d]),y,lapack_driver='gelsy')[0]
    full_event = linalg.lstsq(np.column_stack([z,e]),y,lapack_driver='gelsy')[0]
    saved_models = pd.read_csv(results/'model_registry.csv')
    saved_pool = saved_models.loc[saved_models.model.eq('same_sample_unadjusted')].iloc[0]
    saved_event = pd.read_csv(results/'event_coefficients.csv')
    saved_event = saved_event.loc[saved_event.model.eq('event_base')].set_index('t').loc[event_quarters]
    mask_pre = np.array(event_quarters) < 12
    mask_post = np.array(event_quarters) > 12
    mask_announcement = (np.array(event_quarters) > 12) & (np.array(event_quarters) < 16)
    mask_completion = np.array(event_quarters) >= 16
    rows = pd.DataFrame({'t':event_quarters,
        'quarter':[f'{2005+(t-1)//4}Q{(t-1)%4+1}' for t in event_quarters],
        'honestdid_block':['pre' if t<12 else 'post' for t in event_quarters],
        'pooled_period':['pre' if t<16 else 'completion_and_later' for t in event_quarters],
        'weight_a':a,'event_b':b_event,'weighted_contribution':a*b_event})
    rows.to_csv(out/'full_event_pooled_weights.csv',index=False,float_format='%.17g')
    rows.loc[mask_post,['t','quarter','weight_a']].to_csv(out/'post_target_weights.csv',index=False,float_format='%.17g')
    pd.DataFrame(covariance_event,index=rows.quarter,columns=rows.quarter).to_csv(out/'independent_event_covariance.csv',float_format='%.17g')
    post_target = float(a[mask_post]@b_event[mask_post])
    pre_contribution = float(a[mask_pre]@b_event[mask_pre])
    target_se = float(np.sqrt(a[mask_post]@covariance_event[np.ix_(mask_post,mask_post)]@a[mask_post]))
    # This synthetic causal path has eleven genuinely pre-treatment zero effects.
    # A direct pooled regression of its generated outcome checks the post-only
    # functional independently of the event-coefficient identity for observed y.
    tau_pre_zero = np.zeros(23)
    tau_pre_zero[mask_post] = np.linspace(-.08, .12, mask_post.sum())
    synthetic_causal_outcome = e @ tau_pre_zero
    synthetic_pool = linalg.lstsq(np.column_stack([z,d]), synthetic_causal_outcome,
                                  lapack_driver='gelsy')[0][-1]
    synthetic_post_functional = float(a[mask_post]@tau_pre_zero[mask_post])
    checks = {'pool_vs_saved':abs(beta_pool-float(saved_pool.b)),
        'pool_vs_event_weighted':abs(beta_pool-beta_via_weights),
        'pool_vs_direct_full_dummy':abs(beta_pool-float(full_pool[-1])),
        'pool_vs_sequential_demeaning':abs(beta_pool-beta_demean),
        'event_vs_saved_max_abs':float(np.max(np.abs(b_event-saved_event.b.to_numpy()))),
        'event_vs_direct_full_dummy_max_abs':float(np.max(np.abs(b_event-full_event[-23:]))),
        'weights_vs_sequential_demeaning_max_abs':float(np.max(np.abs(a-a_demean))),
        'event_se_vs_saved_max_abs':float(np.max(np.abs(np.sqrt(np.diag(covariance_event))-saved_event.se.to_numpy()))),
        'pool_se_vs_saved':abs(float(np.sqrt(covariance_pool[0,0]))-float(saved_pool.se)),
        'weighted_identity_using_saved_event':abs(float(a@saved_event.b.to_numpy())-float(saved_pool.b)),
        'prezero_causal_path_direct_pool_vs_post_functional':abs(float(synthetic_pool)-synthetic_post_functional)}
    other_cov_path = here.parent/('unadjusted_honestdid' if (here.parent/'unadjusted_honestdid').exists() else 'unadjusted_honestdid_extension')/'event_covariance.csv'
    covariance_cross_check = None
    if other_cov_path.exists():
        other_cov = pd.read_csv(other_cov_path,index_col=0)
        expected_names = [f'q{t}' for t in event_quarters]
        assert list(other_cov.index) == expected_names
        assert list(other_cov.columns) == expected_names
        covariance_cross_check = {'source':str(other_cov_path),
            'sha256':hashlib.sha256(other_cov_path.read_bytes()).hexdigest(),
            'max_abs_difference':float(np.max(np.abs(covariance_event-other_cov.to_numpy())))}
        checks['event_covariance_vs_independent_agent_max_abs'] = covariance_cross_check['max_abs_difference']
    assert max(checks.values()) < 1e-10, checks
    assert np.all(a[mask_pre]<0) and np.all(a[mask_announcement]<0)
    assert np.all(a[mask_completion]>0)
    assert abs(a[mask_completion].sum()-1)<1e-12
    summary = {'source_panel':str(panel_path),'source_panel_sha256':hashlib.sha256(panel_path.read_bytes()).hexdigest(),
        'n':n,'routes':len(route_labels),'nuisance_rank':rank_z,'event_target_rank':23,
        'reference':'2007Q4','pooled_post_begins':'2008Q4','honestdid_post_begins':'2008Q1',
        'pooled_beta_log':beta_pool,'pooled_percent':float(100*np.expm1(beta_pool)),
        'pooled_beta_from_full_event_a':beta_via_weights,
        'pre11_weight_sum':float(a[mask_pre].sum()),
        'early2008_negative_weight_sum':float(a[mask_announcement].sum()),
        'completion9_weight_sum':float(a[mask_completion].sum()),
        'post12_weight_sum':float(a[mask_post].sum()),
        'full23_weight_sum':float(a.sum()),
        'omitted_reference_implicit_weight':float(-a.sum()),
        'pre11_contribution_to_pooled_beta':pre_contribution,
        'post12_plugin_log_target':post_target,'post12_plugin_percent':float(100*np.expm1(post_target)),
        'post12_plugin_standard_error_from_event_covariance':target_se,
        'full_weights':a.tolist(),'post_weights_l_vec':a[mask_post].tolist(),
        'event_beta':b_event.tolist(),'event_quarters':rows.quarter.tolist(),
        'cr1_event':cr1_event,'cr1_pool':cr1_pool,'numeric_checks':checks,
        'independent_agent_covariance_check':covariance_cross_check,
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},
        'interpretation':'With effect zero before 2008Q1, a_post^T tau_post is the causal component associated with the pooled projection. It preserves negative 2008Q1-Q3 weights, so it is a completion-versus-early-effect contrast, not the equal-weight nine-quarter average. Its l_post^T b_post plug-in estimate omits the measured pre-period nuisance contribution and is not numerically the pooled coefficient.',
        'variance_note':'The exact point-estimate identity does not imply equal pooled and event-based standard errors: the constrained pooled and saturated event regressions have different residuals and residual degrees of freedom.'}
    (out/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['pooled_beta_log','pooled_percent','pre11_weight_sum','early2008_negative_weight_sum','completion9_weight_sum','post12_weight_sum','pre11_contribution_to_pooled_beta','post12_plugin_log_target','post12_plugin_percent','numeric_checks']},indent=2))

if __name__ == '__main__':
    main()
