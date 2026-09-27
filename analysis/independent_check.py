#!/usr/bin/env python3
"""Independent checks from saved extension panels; never rereads source data."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import linalg, stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--results', type=Path, default=ROOT / 'results',
                    help='Directory containing the saved extension outputs (default: repository results/)')
parser.add_argument('--out', type=Path,
                    help='Verification JSON path (default: <results>/independent_check_results.json)')
args = parser.parse_args()
OUT = args.results.resolve()
REPORT_PATH = (args.out if args.out is not None else OUT / 'independent_check_results.json').resolve()
RESULT = json.loads((OUT / 'extended_results.json').read_text())
r = pd.read_csv(OUT / 'route_features.csv', index_col='route')
cp = pd.read_csv(OUT / 'carrier_shares_2007.csv', keep_default_na=False)
checks = {}
panels = {k: pd.read_csv(OUT / f'panel_{k}.csv') for k in ['legacy','legacy_valid','legacy_support','all_unexposed','all_support']}

def close(a,b,tol=1e-10):
    aa=np.asarray(a,float);bb=np.asarray(b,float)
    assert np.allclose(aa,bb,atol=tol,rtol=tol,equal_nan=True)

for name,d in panels.items():
    assert not d.duplicated(['route','t']).any()
    assert np.isfinite(d.lnfare).all()
    close(d.fare,d.revenue/d.pax)
    for var,base in [('distance_2007','distance'),('one_share_2007','one_share'),('uaco_2007','uaco')]:
        close(d[var],d.route.map(r[base]))
    for var in ['treated','distance_bin','share_bin','delta_proxy','hhi_single']:
        close(d[var],d.route.map(r[var]))
    close(d['distance_bin'],pd.cut(d.distance_2007,[0,750,1500,2000,np.inf],right=False,labels=False))
    close(d['share_bin'],pd.cut(d.one_share_2007,[0,.1,.5,.9,1.0000001],right=False,labels=False))
    checks[name]={'N':len(d),'routes':d.route.nunique(),'treated':int(d.groupby('route').treated.first().sum())}

assert (cp.cr1!='').all(), 'Unnamed carrier included as firm'
close(cp.carrier_pax/cp.single_pax,cp.conditional_share,tol=1e-7)
close(cp.groupby('route').conditional_share.sum(),np.ones(cp.route.nunique()),tol=1e-6)
recalc=(10000*(cp.carrier_pax/cp.single_pax)**2).groupby(cp.route).sum()
close(recalc,r.loc[recalc.index,'hhi_single'],tol=1e-6)
close(r.delta_proxy,20000*(r.dl/r.pax)*(r.nw/r.pax),tol=1e-6)
positive=r.single_pax.gt(0)
close(r.loc[positive,'delta_conditional'],20000*(r.loc[positive,'dl']/r.loc[positive,'single_pax'])*(r.loc[positive,'nw']/r.loc[positive,'single_pax']),tol=1e-6)
checks['concentration']={'named_codes_2007':int(cp.cr1.nunique()),'zero_single_eligible':int((r.eligible&~positive).sum()),'minimum_coverage_eligible':float(r.loc[r.eligible,'single_coverage'].min())}

for key,parent,child in [('legacy','legacy_valid','legacy_support'),('all_unexposed','all_unexposed','all_support')]:
    a=r.loc[panels[parent].route.unique()]
    counts=a.groupby(['cell','treated']).size().unstack(fill_value=0)
    cells=set(counts.index[counts[0].ge(3)&counts[1].ge(3)])
    expected=set(a.index[a.cell.isin(cells)])
    assert expected==set(panels[child].route)
    checks['support_'+key]={'retained_cells':len(cells),'retained_routes':len(expected),'cell_counts':counts.rename(columns={0:'controls',1:'treated'}).to_dict('index')}

def raw_dummy_check(label,d,controls=(),event=False,trends=False):
    d=d.sort_values(['route','t']).reset_index(drop=True)
    n=len(d);g,ids=pd.factorize(d.route);G=len(ids)
    t=d.t.to_numpy(float);T=d.treated.to_numpy(float)
    times=sorted(d.t.unique())
    # Independently build raw route/time/bin interactions; no production imports,
    # within transform, or saved transformed regressors.
    if event:
        qs=[q for q in times if q!=12]
        A=np.column_stack([T*(t==q) for q in qs]);terms=[f'q{q}' for q in qs]
    else:
        A=(T*(t>=16))[:,None];terms=['did']
    nuisance=[pd.get_dummies(d.route).to_numpy(float),pd.get_dummies(d.t,drop_first=True).to_numpy(float)]
    for col in controls:
        levels=sorted(d[col].unique())
        nuisance.append(np.column_stack([(d[col].to_numpy()==v)*(t==q) for v in levels[1:] for q in times[1:]]))
    if trends:
        nuisance.append(pd.get_dummies(d.route).to_numpy(float)*(t-12)[:,None])
    Z=np.column_stack(nuisance)
    Q,R,piv=linalg.qr(Z,mode='economic',pivoting=True)
    tol=max(Z.shape)*np.finfo(float).eps*abs(R.diagonal()).max()
    rank=int((abs(R.diagonal())>tol).sum())
    Z=Z[:,piv[:rank]]
    residual=A-Q[:,:rank]@(Q[:,:rank].T@A)
    residual_fraction=np.linalg.norm(residual,axis=0)/np.linalg.norm(A,axis=0)
    assert residual_fraction.min()>1e-8
    X=np.column_stack([A,Z])
    assert np.linalg.matrix_rank(X)==X.shape[1]
    fit=sm.OLS(d.lnfare.to_numpy(),X).fit(cov_type='cluster',cov_kwds={'groups':g},use_t=True)
    stored=RESULT['models'][label];K=len(terms)
    b=np.array([stored['coef'][v]['b'] for v in terms]);se=np.array([stored['coef'][v]['se'] for v in terms])
    diffb=float(abs(fit.params[:K]-b).max());diffse=float(abs(fit.bse[:K]-se).max())
    assert diffb<1e-8 and diffse<1e-8,(label,diffb,diffse)
    assert fit.df_resid==stored['df_resid']
    out={'max_beta_difference':diffb,'max_se_difference':diffse,'df_resid':int(fit.df_resid),'N':n,'min_target_residual_fraction':float(residual_fraction.min())}
    if event:
        idx=[i for i,q in enumerate(qs) if q<12]
        bv=fit.params[idx];cv=fit.cov_params()[np.ix_(idx,idx)]
        assert np.linalg.matrix_rank(cv)==len(idx)
        F=float(bv@np.linalg.solve(cv,bv)/len(idx));p=float(stats.f.sf(F,len(idx),G-1))
        close(F,stored['pre_2005_2007']['F'],tol=1e-7)
        out.update(pretest_F=F,pretest_p=p)
    print(label,out,flush=True)
    return out

valid=panels['legacy_valid']
numeric={}
for label,d,ctrl,event,trends in [
    ('published_baseline',panels['legacy'],[],False,False),
    ('distance_and_composition_quarter',valid,['distance_bin','share_bin'],False,False),
    ('common_support_cell_quarter',panels['legacy_support'],['cell'],False,False),
    ('event_adjusted',valid,['distance_bin','share_bin'],True,False),
    ('route_trends',valid,['distance_bin','share_bin'],False,True),
    ('end_2009',valid[valid.t<=20],['distance_bin','share_bin'],False,False),
    ('exclude_UA_CO',valid[valid.uaco_2007==0],['distance_bin','share_bin'],False,False),
]:
    numeric[label]=raw_dummy_check(label,d,ctrl,event,trends)

report={'status':'passed','source':'saved panels and route/carrier features only','checks':checks,'independent_raw_dummy_estimates':numeric,
        'analysis_sha256':hashlib.sha256((ROOT/'analysis/extend_analysis.py').read_bytes()).hexdigest()}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(f'All independent saved-output checks passed. Report: {REPORT_PATH}',flush=True)
