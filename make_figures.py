from pathlib import Path
import json,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;(R/'figures').mkdir(exist_ok=True)
r=json.loads((R/'results.json').read_text());d=pd.read_csv(R/'analysis_panel.csv')
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.22,'axes.axisbelow':True,'savefig.bbox':'tight'})
fig,ax=plt.subplots(figsize=(6.5,3.25))
for grp,color,label in [('overlap','#1e4163','Material DL/NW overlap'),('unexposed_legacy','#9a563d','Comparison routes')]:
 v=d[d.group==grp].groupby('t').lnfare.mean();index=100*np.exp(v-v.loc[8:11].mean());ax.plot(index.index,index.values,label=label,color=color,lw=1.8,marker='o',ms=3)
ax.axvline(15,color='#444444',ls='--',lw=1);ax.axvspan(13,14.9,color='#aaaaaa',alpha=.12)
ax.set_xticks([0,4,8,12,16,20,23],['2005Q1','2006Q1','2007Q1','2008Q1','2009Q1','2010Q1','2010Q4']);ax.tick_params(axis='x',labelsize=8)
ax.set_ylabel('Fare index (2007 mean log fare = 100)');ax.legend(frameon=False,fontsize=9,loc='best');fig.tight_layout();fig.savefig(R/'figures/trends.pdf');fig.savefig(R/'figures/trends.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3.6));co=r['event']['coef'];ks=sorted([int(k[1:]) for k in co]);vals=[co['k'+str(k)] for k in ks]
b=np.array([v['b'] for v in vals]);lo=np.array([v['lo'] for v in vals]);hi=np.array([v['hi'] for v in vals]);ax.errorbar(ks,b,yerr=[b-lo,hi-b],fmt='o',color='#1e4163',ms=4,capsize=2,lw=1.1)
ax.scatter([-1],[0],facecolors='white',edgecolors='#1e4163',s=30,zorder=3);ax.axhline(0,color='black',lw=.8);ax.axvline(-.5,color='#555555',ls='--',lw=.9);ax.axvspan(-2.7,-.6,color='#aaaaaa',alpha=.12)
ax.set_xticks([-15,-12,-9,-6,-3,-1,0,2,4,6,8]);ax.set_xlabel('Quarters relative to 2008Q4; 2008Q3 omitted');ax.set_ylabel('Difference in log fares');fig.tight_layout();fig.savefig(R/'figures/event.pdf');fig.savefig(R/'figures/event.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3.0));keys=['baseline','anycode_2007','broad_reconstruction','broad_all_controls'];labels=['Material overlap; 2007','Any-code overlap; 2007','Broad pre-merger; legacy controls','Broad pre-merger; all controls'];vs=[r[k]['coef']['did'] for k in keys];b=np.array([100*np.expm1(v['b']) for v in vs]);lo=np.array([100*np.expm1(v['lo']) for v in vs]);hi=np.array([100*np.expm1(v['hi']) for v in vs]);y=np.arange(4)[::-1];ax.errorbar(b,y,xerr=[b-lo,hi-b],fmt='o',color='#1e4163',capsize=3);ax.set_yticks(y,labels);ax.set_xlabel('Relative fare change (%)');ax.axvline(0,color='black',lw=.8);ax.set_ylim(-.5,3.5);fig.tight_layout();fig.savefig(R/'figures/definitions.pdf');fig.savefig(R/'figures/definitions.png',dpi=180);plt.close(fig)
# LaTeX tables are generated from result files rather than manually entered estimates.
def esc(s):return s.replace('_','\\_')
def pct(v):return f'{100*np.expm1(v):.2f}'
def pval(v):return '$<0.001$' if v<.001 else f'{v:.3f}'
rows=[]
for key,label in [('baseline','Equal route weights'),('fixed_pre_pax','Fixed 2007 passenger weights'),('balanced','Balanced 24-quarter routes'),('omit_announcement_completion','Omit 2008Q2--2008Q4'),('matched','Match on 2007 observables'),('exclude_crisis_window','Omit 2008Q3--2009Q4')]:
 v=r[key];c=v['coef']['did'];rows.append(f"{label} & {c['b']:.4f} & {c['se']:.4f} & {pct(c['b'])} & {pval(c['p'])} & {v['N']:,} \\\\")
(R/'table_results.tex').write_text('\n'.join(rows)+'\n')
rows=[]
for key,label in zip(keys,['Material overlap, 2007','Any-code overlap, 2007','Broad pre-merger, legacy controls','Broad pre-merger, all controls']):
 v=r[key];c=v['coef']['did'];rows.append(f"{label} & {v['treated_routes']:,} & {v['control_routes']:,} & {v['N']:,} & {pct(c['b'])} \\\\")
(R/'table_definitions.tex').write_text('\n'.join(rows)+'\n')
rows=[]
for k in sorted(int(k[1:]) for k in r['event']['coef']):
 v=r['event']['coef']['k'+str(k)];t=k+15;year=2005+t//4;q=t%4+1;rows.append(f"{year}Q{q} & {k:+d} & {v['b']:.4f} & {v['se']:.4f} & [{v['lo']:.4f}, {v['hi']:.4f}] & {pval(v['p'])} \\\\")
(R/'table_event.tex').write_text('\n'.join(rows)+'\n')
print('Baseline percent and CI:',pct(r['baseline']['coef']['did']['b']),pct(r['baseline']['coef']['did']['lo']),pct(r['baseline']['coef']['did']['hi']))
print('event late', {k:r['event']['coef'][k] for k in ['k0','k4','k5','k8']})
