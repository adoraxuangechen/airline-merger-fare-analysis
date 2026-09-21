from pathlib import Path
import numpy as np,pandas as pd,json
from scipy import stats
R=Path(__file__).resolve().parent
from estimator import fit
p=pd.read_pickle(R/'panel.pkl');n=p.groupby('route').t.nunique();d=p[p.route.isin(n[n>=4].index)].copy()
a=d[d.t<15].groupby('route').agg(dl=('dl_any','sum'),nw=('nw_any','sum'))
a['treated']=((a.dl>0)&(a.nw>0)).astype(int)
d=d.merge(a[['treated']],on='route');r=fit(d)
print(r)
js=json.loads((R/'results.json').read_text());js['broad_all_controls']=r;(R/'results.json').write_text(json.dumps(js,indent=2))
