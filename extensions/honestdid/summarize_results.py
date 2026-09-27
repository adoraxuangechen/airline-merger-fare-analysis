#!/usr/bin/env python3
"""Audit all official acceptance grids, save tabular reporting and a figure."""
from pathlib import Path
import json, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'event_export_metadata.json').read_text())
rows=[]
for mode,m in [('single_0',0),('single_05',.5),('single_1',1),('single_2',2)]:
 f=next((ROOT/f'{mode}_grids').glob('M*.csv'))
 d=pd.read_csv(f); a=d.accept.to_numpy();x=d.grid.to_numpy()
 assert set(a)<=set([0,1]) and len(x)>10
 assert np.all(np.diff(x)>0)
 assert a[0]==a[-1]==0,'Open full grid requires expansion'
 ix=np.flatnonzero(a==1); assert len(ix)
 starts=ix[np.r_[True,np.diff(ix)>1]];ends=ix[np.r_[np.diff(ix)>1,True]]
 components=[[float(x[i]),float(x[j])] for i,j in zip(starts,ends)]
 published=pd.read_csv(ROOT/f'{mode}_sensitivity.csv').iloc[0]
 assert abs(published.lb-x[ix[0]])<1e-12 and abs(published.ub-x[ix[-1]])<1e-12
 row=dict(Mbar=m,accepted_lower=float(x[ix[0]]),accepted_upper=float(x[ix[-1]]),
    lower_adjacent_reject=float(x[ix[0]-1]),upper_adjacent_reject=float(x[ix[-1]+1]),
    lower_percent=100*np.expm1(x[ix[0]]),upper_percent=100*np.expm1(x[ix[-1]]),
    grid_lower=float(x[0]),grid_upper=float(x[-1]),grid_points=len(x),
    grid_step=float(np.diff(x).max()),number_of_components=len(components),
    endpoint_truncation=False,zero_in_grid_acceptance=bool(a[np.argmin(abs(x))]),components=components)
 rows.append(row)
pd.DataFrame([{k:v for k,v in r.items() if k!='components'} for r in rows]).to_csv(ROOT/'sensitivity_summary.csv',index=False)
report={'specification':meta,'official_package_version':'0.2.8','official_git_commit':'6813f02ed38f0b63bdca6915604b2eac90491303','seed':20260927,'method':'C-LF','alpha':.05,'rows':rows,
 'interpretation':'Finite-grid approximations to official confidence sets. Endpoint crossings bracketed by adjacent rejected grid points. No full-grid endpoint was accepted; all four sampled acceptance sets have one connected component. Sampling grid cannot mathematically exclude features narrower than its spacing. No estimate was selected using these diagnostics.'}
(ROOT/'sensitivity_results.json').write_text(json.dumps(report,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7,3.5))
for i,row in enumerate(rows):
 ax.hlines(i,row['accepted_lower'],row['accepted_upper'],color='#24566D',lw=3)
 ax.plot([row['accepted_lower'],row['accepted_upper']],[i,i],'|',color='#24566D',ms=9)
ax.axvline(0,color='black',lw=.8);ax.axvline(meta['target_b'],color='#b66b35',ls='--',lw=1)
ax.set_yticks(range(4),['M = 0','M = 0.5','M = 1','M = 2']);ax.invert_yaxis()
ax.set_xlabel('Average adjusted log-fare effect, 2008Q4–2010Q4')
ax.set_title('HonestDiD: relative-magnitude sensitivity',loc='left',fontsize=12)
fig.tight_layout();fig.savefig(ROOT/'honestdid_sensitivity.png',dpi=200);fig.savefig(ROOT/'honestdid_sensitivity.pdf');plt.close(fig)
print(pd.DataFrame(rows).drop(columns='components').to_string(index=False))
