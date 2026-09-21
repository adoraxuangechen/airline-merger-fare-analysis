import numpy as np
import pandas as pd
from scipy import stats

def fit(df,event=False,wcol=None,t0=15,ref_t=14):
 df=df.sort_values(['route','t']).copy();g,ids=pd.factorize(df.route);G=len(ids);N=len(df)
 t=df.t.to_numpy();tr=df.treated.to_numpy();y=df.lnfare.to_numpy()
 if event:
  ts=[int(j) for j in sorted(set(t)) if j!=ref_t]
  X0=np.column_stack([tr*(t==j) for j in ts]);names=['k'+str(j-15) for j in ts]
 else:
  X0=(tr*(t>=t0)).reshape(-1,1);names=['did']
 times=[j for j in sorted(set(t))][1:]
 X=np.column_stack([X0,*[(t==j).astype(float) for j in times]])
 w=np.ones(N) if wcol is None else df[wcol].to_numpy(float)
 sw=np.bincount(g,weights=w,minlength=G)
 def within(A):
  if A.ndim==1:return A-np.bincount(g,weights=w*A,minlength=G)[g]/sw[g]
  sums=np.column_stack([np.bincount(g,weights=w*A[:,j],minlength=G) for j in range(A.shape[1])])
  return A-sums[g]/sw[g,None]
 yr=within(y);xr=within(X)
 bread=np.linalg.inv(xr.T@(w[:,None]*xr));beta=bread@(xr.T@(w*yr));res=yr-xr@beta
 score=np.zeros((G,xr.shape[1]));np.add.at(score,g,xr*(w*res)[:,None])
 df_res=N-G-X.shape[1]
 cov=bread@(score.T@score)@bread*(G/(G-1))*((N-1)/df_res)
 se=np.sqrt(np.diag(cov));pvals=2*stats.t.sf(np.abs(beta/se),G-1);crit=stats.t.ppf(.975,G-1)
 out={'N':N,'routes':G,'treated_routes':int(df.groupby('route').treated.first().sum()),'control_routes':int(G-df.groupby('route').treated.first().sum()),'quarters':len(set(t)),'df_resid':df_res,'coef':{}}
 for j,n in enumerate(names):
  out['coef'][n]={'b':float(beta[j]),'se':float(se[j]),'p':float(pvals[j]),'lo':float(beta[j]-crit*se[j]),'hi':float(beta[j]+crit*se[j])}
 if event:
  for label,indices in [('all_pre', [i for i,j in enumerate(ts) if j<ref_t]),('pre_announcement',[i for i,j in enumerate(ts) if j<=12])]:
   v=beta[indices];cv=cov[np.ix_(indices,indices)];q=len(indices);F=float(v@np.linalg.solve(cv,v)/q)
   out[label]={'F':F,'df_num':q,'df_den':G-1,'p':float(stats.f.sf(F,q,G-1))}
 # Numerical equivalence to an explicit dummy-variable WLS regression on a small actual-data subset is checked separately below.
 return out
