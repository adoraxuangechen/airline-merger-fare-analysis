from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy import stats
from scipy.spatial.distance import cdist
R=Path(__file__).resolve().parent
p=pd.read_pickle(R/'panel.pkl');c=pd.read_csv(R/'classification.csv').set_index('route')
c['eligible']=(c.nq==4)&(c.pax_min>=100)
mainc=c[c.eligible&c.group.isin(['overlap','unexposed_legacy'])].copy()
d=p.merge(mainc[['group','pax_pre','fare_pre','direct','distance']],on='route',suffixes=('','_pre'))
d['treated']=(d.group=='overlap').astype(int)
# A complete route-within transformation of y AND every regressor, including time dummies.
from estimator import fit
results={'baseline':fit(d),'fixed_pre_pax':fit(d,wcol='pax_pre'),'event':fit(d,event=True)}
balanced=d.groupby('route').t.nunique();balanced=balanced[balanced==24].index
results['early_pre_event']=fit(d[d.t<=11],event=True,ref_t=11)
results['balanced']=fit(d[d.route.isin(balanced)])
results['omit_announcement_completion']=fit(d[~d.t.between(13,15)],t0=16)
results['exclude_crisis_window']=fit(d[~d.t.between(14,19)])
# One nearest control per treated route, with replacement, based only on 2007 observables.
a=mainc.copy();features=np.column_stack([np.log(a.fare_pre),np.log(a.pax_pre),a.distance/1000,a.direct]);features=(features-features.mean(0))/features.std(0,ddof=1)
ti=np.where(a.group=='overlap')[0];ci=np.where(a.group=='unexposed_legacy')[0]
mat=cdist(features[ti],features[ci]);idx=ci[mat.argmin(axis=1)];counts=pd.Series(a.index[idx]).value_counts();weights={r:1. for r in a.index[ti]};weights.update(counts.to_dict())
md=d[d.route.isin(weights)].copy();md['match_weight']=md.route.map(weights)
results['matched']=fit(md,wcol='match_weight');results['matched_event']=fit(md,event=True,wcol='match_weight')
results['matching']={'controls_used':len(counts),'median_distance':float(np.median(mat.min(1))),'max_distance':float(np.max(mat.min(1))),'max_control_reuse':int(counts.max())}
# Small actual-data equivalence check against full route and time dummies.
subroutes=list(d[d.treated==1].route.unique()[:12])+list(d[d.treated==0].route.unique()[:12])
s=d[d.route.isin(subroutes)].sort_values(['route','t']);res=fit(s)
xs=np.column_stack([s.treated*(s.t>=15),np.ones(len(s)),pd.get_dummies(s.route,drop_first=True).to_numpy(),pd.get_dummies(s.t,drop_first=True).to_numpy()]).astype(float)
bfull=np.linalg.lstsq(xs,s.lnfare.to_numpy(),rcond=None)[0][0]
results['estimator_check']={'within_beta':res['coef']['did']['b'],'dummy_beta':float(bfull),'absolute_difference':float(abs(bfull-res['coef']['did']['b']))}
assert abs(bfull-res['coef']['did']['b'])<1e-9
# Route-level pre-period covariate comparisons and sample flow.
summary=[]
for grp in ['overlap','unexposed_legacy']:
 aa=mainc[mainc.group==grp];dd=d[d.group==grp]
 summary.append({'group':grp,'routes':len(aa),'route_quarters':len(dd),'mean_2007_pax':float(aa.pax_pre.mean()),'mean_2007_fare':float(aa.fare_pre.mean()),'mean_distance':float(aa.distance.mean()),'mean_direct_share':float(aa.direct.mean()),'mean_2007_lnf':float(np.log(aa.fare_pre).mean()),'median_2007_fare':float(aa.fare_pre.median())})
results['descriptive']=summary
results['sample_flow']={'eligible_2007_routes':int(c.eligible.sum()),'classified_routes':int(len(mainc)),'main_rows':len(d),'balanced_routes':len(balanced),'classified_record_count':int(d.records.sum()),'sample_passenger_total':int(d.pax.sum()),'pre_min_rows':int(d.groupby('route').size().min())}
# Earlier descriptive implementation contrast uses the SAME y, panel and groups.
def oldfit(df):
 df=df.sort_values(['route','t']);g,_=pd.factorize(df.route);t=df.t.to_numpy();y=df.lnfare.to_numpy();z=(df.treated*(df.t>=15)).to_numpy();ng=np.bincount(g)
 y=y-np.bincount(g,weights=y)[g]/ng[g];z=z-np.bincount(g,weights=z)[g]/ng[g]
 xx=np.column_stack([z,np.ones(len(df)),pd.get_dummies(t,drop_first=True).to_numpy()]);return float(np.linalg.lstsq(xx,y,rcond=None)[0][0])
results['old_vs_correct']={'partial_demeaning':oldfit(d),'correct':results['baseline']['coef']['did']['b']}
d.to_csv(R/'analysis_panel.csv',index=False)
(R/'results.json').write_text(json.dumps(results,indent=2))
for k,v in results.items():
 if isinstance(v,dict) and 'coef' in v:
  print(k, {i:v[i] for i in ['N','routes','treated_routes','control_routes']},v['coef'].get('did',v.get('all_pre')))
 else:print(k,v)
