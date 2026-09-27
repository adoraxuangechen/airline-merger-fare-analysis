#!/usr/bin/env python3
"""Independent explicit-dummy verification of descriptive fare-gap estimates."""
import argparse,json
from pathlib import Path
import pandas as pd,numpy as np,statsmodels.api as sm
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results',type=Path,default=Path(__file__).resolve().parent/'results');args=parser.parse_args();p=args.results
cv=json.loads((p/'carrier_gap_covariance.json').read_text());checks=[]
for name in ['all_products_baseline_paired','all_products_balanced_24q','two_coupon_only_baseline_paired','two_coupon_only_balanced_24q']:
    d=pd.read_csv(p/(name+'_panel.csv')).sort_values(['route','t'])
    T=pd.get_dummies(d.t,dtype=float).drop(columns=12);R=pd.get_dummies(d.route,dtype=float)
    fit=sm.OLS(d.gap.to_numpy(),np.column_stack([T,R])).fit(cov_type='cluster',cov_kwds={'groups':d.route.to_numpy()},use_t=True)
    k=T.shape[1];expected=cv[name];db=np.max(abs(fit.params[:k]-np.array(expected['b'])));dv=np.max(abs(fit.cov_params()[:k,:k]-np.array(expected['cov'])))
    assert db<1e-9 and dv<1e-10
    checks.append({'model':name,'check':'Independent full-route-dummy statsmodels regression','max_beta_difference':float(db),'max_covariance_difference':float(dv)})
    if name.endswith('balanced_24q'):
        q=d.groupby('t').gap.mean();manual=q.loc[17:24].mean()-q.loc[9:12].mean();expectedmean=pd.read_csv(p/'carrier_gap_period_contrasts.csv').set_index('model').loc[name,'b']
        assert abs(manual-expectedmean)<1e-12
        checks.append({'model':name,'check':'Direct balanced route-quarter mean contrast','manual_log_contrast':float(manual),'stored_log_contrast':float(expectedmean),'abs_difference':abs(manual-expectedmean)})
(p/'independent_gap_model_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
