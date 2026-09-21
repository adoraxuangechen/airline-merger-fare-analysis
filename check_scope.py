from pathlib import Path
import pandas as pd,numpy as np,json
from scipy import stats
R=Path(__file__).resolve().parent
p=pd.read_pickle(R/'panel.pkl');n=p.groupby('route').t.nunique();s=p[p.route.isin(n[n>=4].index)].copy()
print('>=4quarter sample',len(s),s.route.nunique())
from estimator import fit
b=s[s.t<15].groupby('route').agg(dl=('dl_any','sum'),nw=('nw_any','sum'),legacy=('legacy','sum'))
b['treated']=((b.dl>0)&(b.nw>0)).astype(int)
keep=(b.treated==1)|(b.legacy>0)
x=s.merge(b.loc[keep,['treated']],on='route')
res=fit(x)
y=x[x.t<15].groupby('route').size();z=x[x.t>=15].groupby('route').size();both=y.index.intersection(z.index)
res2=fit(x[x.route.isin(both)])
c=pd.read_csv(R/'classification.csv').set_index('route');q=p[p.t.between(8,11)].groupby('route').agg(dl=('dl_any','sum'),nw=('nw_any','sum'),leg=('legacy','sum'))
q=q.join(c[['nq','pax_min']]);q=q[(q.nq==4)&(q.pax_min>=100)]
q['treated']=((q.dl>0)&(q.nw>0)).astype(int);q=q[(q.treated==1)|(q.leg>0)]
xx=p.merge(q[['treated']],on='route');res3=fit(xx)
print('broad text reconstruction',res)
print('broad both periods',res2)
print('any-code 2007',res3)
main=json.loads((R/'results.json').read_text());main['broad_reconstruction']=res;main['broad_both_periods']=res2;main['anycode_2007']=res3;main['allpanel_min4']={'N':len(s),'routes':s.route.nunique()}
(R/'results.json').write_text(json.dumps(main,indent=2))
