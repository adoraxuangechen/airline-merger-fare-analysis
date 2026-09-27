#!/usr/bin/env python3
"""Export full covariance for a unadjusted HonestDiD specification; upstream files read-only."""
from pathlib import Path
import importlib.util, json, hashlib
import numpy as np
import pandas as pd
from scipy import linalg, stats
ROOT=Path(__file__).resolve().parent
import argparse
parser=argparse.ArgumentParser()
candidates=[ROOT.parent/'repository', ROOT.parents[1], Path.cwd()]
default_repo=next((p for p in candidates if (p/'analysis/extend_analysis.py').exists()), None)
parser.add_argument('--repository',type=Path,default=default_repo)
args=parser.parse_args()
if args.repository is None: parser.error('--repository must point to the replication repository')
REPO=args.repository.resolve()
spec=importlib.util.spec_from_file_location('upstream', REPO/'analysis/extend_analysis.py')
upstream=importlib.util.module_from_spec(spec);spec.loader.exec_module(upstream)
panel=REPO/'results/panel_legacy_valid.csv'
d=pd.read_csv(panel)
fit,(d,X,y,g)=upstream.estimate(d,[],kind='event',reference=12)
names=list(fit['coef']);k=len(names);G=len(np.unique(g));N=len(d)
# FWL reconstruction using rank-selected nuisance design returned by main estimator.
A=X[:,:k];Z=X[:,k:]
Q=linalg.qr(Z,mode='economic',check_finite=False)[0]
Ar=A-Q@(Q.T@A);yr=y-Q@(Q.T@y)
bread=np.linalg.inv(Ar.T@Ar);beta=bread@Ar.T@yr
res=yr-Ar@beta
scores=np.zeros((G,k));np.add.at(scores,g,Ar*res[:,None])
cr1=G/(G-1)*(N-1)/fit['df_resid']
cov=bread@scores.T@scores@bread*cr1
cov=(cov+cov.T)/2
saved=json.load(open(REPO/'results/extended_results.json'))['models']['event_base']
errors={'max_beta_error_vs_saved':max(abs(beta[i]-saved['coef'][x]['b']) for i,x in enumerate(names)),
        'max_se_error_vs_saved':max(abs(np.sqrt(cov[i,i])-saved['coef'][x]['se']) for i,x in enumerate(names))}
assert max(errors.values())<1e-10,errors
assert np.linalg.eigvalsh(cov).min()>0
pre=np.arange(11);post=np.arange(11,23)
l=np.r_[np.zeros(3),np.ones(9)/9]
target=float(l@beta[post]);se=float(np.sqrt(l@cov[np.ix_(post,post)]@l))
f=float(beta[pre]@np.linalg.solve(cov[np.ix_(pre,pre)], beta[pre])/11)
assert abs(f-saved['pre_2005_2007']['F'])<1e-9
rows=[]
for i,name in enumerate(names):
 t=int(name[1:]);rows.append({'term':name,'quarter':f'{2005+(t-1)//4}Q{(t-1)%4+1}','t':t,'beta':beta[i],'se':np.sqrt(cov[i,i]),'target_weight':0 if t<13 else l[t-13]})
pd.DataFrame(rows).to_csv(ROOT/'event_coefficients_full.csv',index=False)
pd.DataFrame(cov,index=names,columns=names).to_csv(ROOT/'event_covariance.csv')
meta={'source_panel_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'n':N,'routes':G,'nuisance_rank':fit['nuisance_rank'],'df_resid':fit['df_resid'],'model':'unadjusted event-study counterpart','controls':['route effects','quarter effects'],'pooled_contrast_b':-0.057445247652156896,'pooled_contrast_percent':-5.582641530824972,'cr1_factor':cr1,'numPrePeriods':11,'numPostPeriods':12,'reference':'2007Q4','post_window':'2008Q1–2010Q4','target_window':'2008Q4–2010Q4','l_vec':l.tolist(),'target_b':target,'target_se':se,'normal95_log':[target-1.959963984540054*se,target+1.959963984540054*se],'t95_log':[target-stats.t.ppf(.975,G-1)*se,target+stats.t.ppf(.975,G-1)*se],'eigenvalue_min':float(np.linalg.eigvalsh(cov).min()),'eigenvalue_max':float(np.linalg.eigvalsh(cov).max()),'condition_number':float(np.linalg.cond(cov)),'pretest_F':f,'pretest_p':float(stats.f.sf(f,11,G-1)),**errors}
(ROOT/'event_export_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
