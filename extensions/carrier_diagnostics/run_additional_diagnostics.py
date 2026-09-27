#!/usr/bin/env python3
"""Supplementary fixed-rule carrier composition and within-route fare diagnostics."""
from pathlib import Path
import argparse,importlib.util,json,hashlib,sys
import numpy as np
import pandas as pd
from scipy import stats,linalg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repository',type=Path,default=(HERE.parent/'repository' if (HERE.parent/'repository').exists() else HERE.parents[1]),help='Repository containing analysis/extend_analysis.py and existing results/')
parser.add_argument('--source',type=Path,required=True,help='Precision-preserving Borenstein 2005–2010 CSV or CSV.gz')
parser.add_argument('--out',type=Path,default=HERE/'results')
args=parser.parse_args()
REPO=args.repository.resolve()
OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
source=args.source.resolve()
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('existing_estimator', REPO/'analysis/extend_analysis.py')
prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)

def save(name,obj):prod.dump(OUT/name,obj)

def gap_event(d,label):
    d=d.sort_values(['route','t']).reset_index(drop=True)
    g,ids=pd.factorize(d.route);G=len(ids);n=len(d);ts=sorted(d.t.unique());targets=[int(t) for t in ts if t!=12]
    A=np.column_stack([d.t.eq(t).to_numpy(float) for t in targets])
    # Route demeaning is exactly equivalent to full route intercepts.
    c=np.bincount(g)
    def within(x):
        if x.ndim==1:return x-np.bincount(g,weights=x)[g]/c[g]
        a=np.zeros((G,x.shape[1]));np.add.at(a,g,x);return x-a[g]/c[g,None]
    X=within(A);y=within(d.gap.to_numpy());assert np.linalg.matrix_rank(X)==len(targets)
    inv=np.linalg.inv(X.T@X);b=inv@X.T@y;u=y-X@b;k=len(targets)
    score=np.zeros((G,k));np.add.at(score,g,X*u[:,None])
    V=inv@score.T@score@inv*(G/(G-1))*((n-1)/(n-G-k))
    crit=stats.t.ppf(.975,G-1);se=np.sqrt(np.maximum(np.diag(V),0))
    ev=pd.DataFrame({'model':label,'t':targets,'b':b,'se':se,'lo':b-crit*se,'hi':b+crit*se})
    ev=pd.concat([ev,pd.DataFrame([{'model':label,'t':12,'b':0,'se':0,'lo':0,'hi':0}])]).sort_values('t')
    # 2007Q4 is the omitted baseline and implicitly has coefficient zero.
    w=np.array([1/8 if t>=17 else -1/4 if 9<=t<=12 else 0 for t in targets])
    val=float(w@b);sd=float(np.sqrt(w@V@w));lo=val-crit*sd;hi=val+crit*sd
    return {'model':label,'N':n,'routes':G,'reference':'2007Q4','period_contrast':'Mean 2009–2010 minus mean 2007','b':val,'se':sd,'lo':lo,'hi':hi,'pct_ratio_change':float(100*np.expm1(val)),'pct_lo':float(100*np.expm1(lo)),'pct_hi':float(100*np.expm1(hi)),'p':float(2*stats.t.sf(abs(val/sd),G-1))},ev,{'times':targets,'b':b,'cov':V}

r=pd.read_csv(REPO/'results/route_features.csv',index_col='route')
a=pd.read_csv(REPO/'results/panel_all_unexposed.csv')
v=pd.read_csv(REPO/'results/panel_legacy_valid.csv')
r['wn_present']=(r.wn>0).astype(int);r['wn_share']=r.wn/r.pax
r['wn_bin']=np.select([r.wn_share.eq(0),r.wn_share.lt(.5)],['zero','positive_below_50'],default='at_least_50')
for d in [a,v]:
    for c in ['wn_present','wn_share','wn_bin']:d[c]=d.route.map(r[c])
    d['comparison_group']=np.select([d.treated.eq(1),d.legacy_control],['Overlap','Legacy comparison'],default='Added comparison')
summary=[]
for label,rows in a.groupby('comparison_group'):
    routes=r.loc[rows.route.unique()]
    summary.append({'group':label,'routes':len(routes),'wn_present_routes':int(routes.wn_present.sum()),'wn_presence_pct':100*routes.wn_present.mean(),'route_mean_wn_share':routes.wn_share.mean(),'passenger_weighted_wn_share':routes.wn.sum()/routes.pax.sum(),**{c:float(routes[c].mean()) for c in ['distance','one_share','fare_pre','pax_pre','single_coverage']}})
pd.DataFrame(summary).to_csv(OUT/'comparison_baseline_2007.csv',index=False)
balance_split=[]
for (label,wn),rows in a.groupby(['comparison_group','wn_present']):
    routes=r.loc[rows.route.unique()]
    balance_split.append({'group':label,'wn_present':wn,'routes':len(routes),**{c:float(routes[c].mean()) for c in ['wn_share','distance','one_share','fare_pre','pax_pre']}})
pd.DataFrame(balance_split).to_csv(OUT/'comparison_baseline_by_wn.csv',index=False)
pd.crosstab(a.drop_duplicates('route').comparison_group,a.drop_duplicates('route').wn_bin).to_csv(OUT/'wn_share_bin_route_counts.csv')

paths=[];phases=[]
for cohort,d in [('available',a),('balanced_24q',a[a.route.isin(a.groupby('route').t.nunique().loc[lambda s:s.eq(24)].index)])]:
    d=d.copy()
    for strat,keys in [('all',['comparison_group']),('by_wn',['comparison_group','wn_present'])]:
        z=d.groupby(keys+['t']).agg(mean_lnfare=('lnfare','mean'),mean_fare=('fare','mean'),routes=('route','nunique'),passengers=('pax','sum'),revenue=('revenue','sum')).reset_index()
        z['passenger_weighted_fare']=z.revenue/z.passengers
        base=z[z.t.eq(12)][keys+['mean_lnfare']].rename(columns={'mean_lnfare':'reference_lnfare'})
        z=z.merge(base,on=keys,how='left');z['index_2007q4_100']=100*np.exp(z.mean_lnfare-z.reference_lnfare)
        z['cohort']=cohort;z['stratification']=strat;paths.append(z)
        for group,rows in d.groupby(keys):
            if not isinstance(group,tuple):group=(group,)
            pre=rows[rows.t.between(9,12)];post=rows[rows.t.between(17,24)]
            phase={'cohort':cohort,'stratification':strat,**dict(zip(keys,group)),'pre_cells':len(pre),'post_cells':len(post),'pre_routes':pre.route.nunique(),'post_routes':post.route.nunique(),'mean_lnfare_2007':pre.lnfare.mean(),'mean_lnfare_2009_2010':post.lnfare.mean()}
            phase['change_log']=phase['mean_lnfare_2009_2010']-phase['mean_lnfare_2007'];phase['change_pct']=100*np.expm1(phase['change_log']);phases.append(phase)
pd.concat(paths,ignore_index=True).to_csv(OUT/'comparison_quarterly_paths.csv',index=False)
pd.DataFrame(phases).to_csv(OUT/'comparison_pre_post_summary.csv',index=False)

models={};registry=[];events=[]
for lab,d in [('legacy',v),('expanded',a)]:
    for extra in [None,'wn_present','wn_bin']:
        name=lab+'_adjusted'+('' if extra is None else '_'+extra)
        controls=['distance_bin','share_bin']+([] if extra is None else [extra])
        print('Estimating '+name,flush=True)
        fit,_=prod.estimate(d,controls);models[name]=fit
        registry.append({'model':name,**{k:v for k,v in fit.items() if k!='coef'},**fit['coef']['did']})
    name=lab+'_event_adjusted_wn_present'
    fit,_=prod.estimate(d,['distance_bin','share_bin','wn_present'],kind='event');models[name]=fit
    for term,value in fit['coef'].items():events.append({'model':name,'t':int(term[1:]),**value})
save('wn_models.json',models);pd.DataFrame(registry).to_csv(OUT/'wn_model_registry.csv',index=False);pd.DataFrame(events).to_csv(OUT/'wn_event_coefficients.csv',index=False)

# Only aggregate records from routes in the unchanged legacy-valid sample.
print('Reading carrier-group rows',flush=True)
x=pd.read_csv(source,keep_default_na=False)
assert len(x)==4175354 and x.yr.between(2005,2010).all(), 'Use the verified Borenstein 2005–2010 extract.'
assert not x.duplicated(['cr1','cr2','yr','qtr','cop','ap1','ap2']).any()
for c in ['cr1','cr2','ap1','ap2']:x[c]=x[c].astype(str).str.strip()
x['route']=x.ap1+'-'+x.ap2;x['t']=(x.yr-2005)*4+x.qtr
x=x[x.route.isin(v.route.unique())].copy()
x=x[np.isfinite(x.pax)&x.pax.gt(0)&np.isfinite(x.avprc)&x.avprc.gt(0)&x.qtr.between(1,4)&x.ap1.ne(x.ap2)]
x['revenue']=x.pax*x.avprc
single=x.cop.eq(0)|x.cr1.eq(x.cr2)
x['carrier_group']=np.select([single&x.cr1.isin(['DL','NW']),single],['DL_NW_single','Rival_single'],default='Mixed')
x['one_pax']=np.where(x.cop.eq(0),x.pax,0)
x['mixed_merger_any_pax']=np.where(x.carrier_group.eq('Mixed')&(x.cr1.isin(['DL','NW'])|x.cr2.isin(['DL','NW'])),x.pax,0)
x['sample_group']=x.route.map(v.groupby('route').treated.first()).map({0:'Legacy comparison',1:'Overlap'})
g=x.groupby(['route','t','carrier_group']).agg(pax=('pax','sum'),revenue=('revenue','sum'),one_pax=('one_pax','sum'),mixed_merger_any_pax=('mixed_merger_any_pax','sum'),records=('pax','size')).reset_index()
g['fare']=g.revenue/g.pax;g['lnfare']=np.log(g.fare);g['one_share']=g.one_pax/g.pax
g=g.merge(v[['route','t','pax','revenue','treated']].rename(columns={'pax':'route_pax','revenue':'route_revenue'}),on=['route','t'],validate='many_to_one')
g['route_pax_share']=g.pax/g.route_pax;g['sample_group']=g.treated.map({0:'Legacy comparison',1:'Overlap'})
g.to_csv(OUT/'carrier_group_route_quarters.csv.gz',index=False)
checks=[]
whole=g.groupby(['route','t'])[['pax','revenue']].sum().sort_index();base=v.set_index(['route','t'])[['pax','revenue']].sort_index()
assert whole.index.equals(base.index);assert np.array_equal(whole.pax,base.pax);assert np.allclose(whole.revenue,base.revenue,rtol=1e-12,atol=1e-6)
checks.append({'test':'Carrier groups exactly partition full route-quarter records','route_quarters':len(whole),'max_passenger_difference':float(np.max(np.abs(whole.pax-base.pax))),'max_revenue_difference':float(np.max(np.abs(whole.revenue-base.revenue)))})
for i in [0,len(g)//2,len(g)-1]:
    row=g.iloc[i];sel=x[x.route.eq(row.route)&x.t.eq(row.t)&x.carrier_group.eq(row.carrier_group)]
    pax=sum(float(z) for z in sel.pax);rev=sum(float(pa)*float(pr) for pa,pr in zip(sel.pax,sel.avprc));fare=rev/pax
    assert np.isclose(fare,row.fare,rtol=1e-12)
    checks.append({'test':'Independent row-level weighted-mean check','route':row.route,'t':int(row.t),'carrier_group':row.carrier_group,'raw_rows':len(sel),'pax':pax,'manual_fare':fare,'stored_fare':float(row.fare),'abs_difference':abs(fare-row.fare)})
# Direct WN 2007 sums must agree with previously prepared features.
y=x[x.t.between(9,12)]
wn=y[y.cr1.eq('WN')|y.cr2.eq('WN')].groupby('route').pax.sum().reindex(v.route.unique(),fill_value=0).sort_index()
assert np.array_equal(wn.to_numpy(),r.loc[wn.index,'wn'].to_numpy())
checks.append({'test':'WN baseline totals independently recomputed from raw records','routes':len(wn),'exact_agreement':True})
save('validation_checks.json',checks)

# Cell availability and shares by fixed phase, including missing groups in denominator.
phase=lambda t:np.select([t<=8,t<=12,t<=16,t<=20],['2005–2006','2007','2008','2009'],default='2010')
g['phase']=phase(g.t);vp=v.copy();vp['phase']=phase(vp.t);vp['sample_group']=vp.treated.map({0:'Legacy comparison',1:'Overlap'})
coverage=[]
for (label,ph),dd in vp.groupby(['sample_group','phase']):
    gg=g[g.sample_group.eq(label)&g.phase.eq(ph)]
    for name in ['DL_NW_single','Rival_single','Mixed']:
        z=gg[gg.carrier_group.eq(name)]
        coverage.append({'sample_group':label,'phase':ph,'carrier_group':name,'possible_route_quarters':len(dd),'observed_positive_cells':len(z),'missing_cells':len(dd)-len(z),'routes_observed':z.route.nunique(),'pax':z.pax.sum(),'share_total_passengers':z.pax.sum()/dd.pax.sum(),'mean_route_quarter_share_with_missing_as_zero':z.route_pax_share.sum()/len(dd),'passenger_weighted_fare':z.revenue.sum()/z.pax.sum() if len(z) else None,'one_coupon_share':z.one_pax.sum()/z.pax.sum() if len(z) else None,'mixed_merger_any_pax':z.mixed_merger_any_pax.sum()})
pd.DataFrame(coverage).to_csv(OUT/'carrier_group_coverage_and_shares.csv',index=False)

# Paired DL/NW and other-code single-carrier records support the within-route fare-gap comparison.
gapstats=[];gapevents=[];covariances={};cohort_audit=[];baseline_availability=[];levelstats=[];levelevents=[]
for product,xx in [('all_products',x),('two_coupon_only',x[x.cop.eq(1)])]:
    grouped=xx[xx.carrier_group.isin(['DL_NW_single','Rival_single'])].groupby(['route','t','carrier_group']).agg(pax=('pax','sum'),revenue=('revenue','sum'))
    grouped['fare']=grouped.revenue/grouped.pax
    wide=grouped.fare.unstack('carrier_group').reset_index().merge(v[['route','t','treated']],on=['route','t'])
    wide=wide[wide.treated.eq(1)].copy();wide['both']=wide.DL_NW_single.gt(0)&wide.Rival_single.gt(0)
    baseline_grid=v[v.treated.eq(1)&v.t.between(9,12)][['route','t']].merge(wide[['route','t','DL_NW_single','Rival_single']],on=['route','t'],how='left')
    baseline_grid['merger_positive']=baseline_grid.DL_NW_single.gt(0);baseline_grid['other_positive']=baseline_grid.Rival_single.gt(0)
    baseline_grid['paired_positive']=baseline_grid.merger_positive&baseline_grid.other_positive
    ba=baseline_grid.groupby('route').agg(merger_positive_quarters=('merger_positive','sum'),other_positive_quarters=('other_positive','sum'),paired_positive_quarters=('paired_positive','sum')).reset_index()
    ba['product']=product;ba['included_baseline_cohort']=ba.paired_positive_quarters.eq(4);baseline_availability.append(ba)
    baseline=wide[wide.t.between(9,12)].groupby('route').both.sum();eligible=baseline[baseline.eq(4)].index
    pairs=wide[wide.route.isin(eligible)&wide.both].copy();pairs['gap']=np.log(pairs.DL_NW_single)-np.log(pairs.Rival_single)
    balanced=pairs.groupby('route').t.nunique();balanced=balanced[balanced.eq(24)].index
    for cohort,d in [('baseline_paired',pairs),('balanced_24q',pairs[pairs.route.isin(balanced)])]:
        name=product+'_'+cohort
        d.to_csv(OUT/(name+'_panel.csv'),index=False)
        counts=v[v.treated.eq(1)&v.route.isin(d.route.unique())]
        cohort_audit.append({'model':name,'original_overlap_routes':156,'baseline_paired_routes':len(eligible),'retained_routes':d.route.nunique(),'possible_cells_in_current_route_cohort':len(counts),'paired_positive_cells':len(d),'missing_paired_cells':len(counts)-len(d),'minimum_quarters_per_retained_route':int(d.groupby('route').t.nunique().min())})
        fit,ev,cv=gap_event(d,name);gapstats.append(fit);gapevents.append(ev);covariances[name]=cv
        for carrier in ['DL_NW_single','Rival_single']:
            level=d.copy();level['gap']=np.log(level[carrier]);lfit,lev,lcv=gap_event(level,name+'__'+carrier)
            lfit['outcome']='Within-carrier-group nominal log fare';lfit['carrier_group']=carrier;levelstats.append(lfit);levelevents.append(lev)
pd.DataFrame(cohort_audit).to_csv(OUT/'carrier_gap_cohorts.csv',index=False)
pd.concat(baseline_availability,ignore_index=True).to_csv(OUT/'carrier_gap_baseline_availability.csv',index=False)
pd.DataFrame(gapstats).to_csv(OUT/'carrier_gap_period_contrasts.csv',index=False)
pd.DataFrame(levelstats).to_csv(OUT/'carrier_level_period_contrasts.csv',index=False)
pd.concat(levelevents,ignore_index=True).to_csv(OUT/'carrier_level_event_coefficients.csv',index=False)
pd.concat(gapevents,ignore_index=True).to_csv(OUT/'carrier_gap_event_coefficients.csv',index=False)
save('carrier_gap_covariance.json',covariances)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
paths=pd.concat(paths,ignore_index=True)
for label,color in [('Overlap','#215b72'),('Legacy comparison','#b47938'),('Added comparison','#6b7d47')]:
    z=paths[paths.cohort.eq('balanced_24q')&paths.stratification.eq('all')&paths.comparison_group.eq(label)]
    ax.plot(z.t,z.index_2007q4_100,label=f'{label} (n={int(z.routes.iloc[0])})',color=color)
ax.axvspan(13.5,16.5,color='#d9b875',alpha=.18);ax.axvline(16,ls='--',lw=.8,color='#7c6853');ax.axhline(100,color='#a6adb0',lw=.7)
ax.set_xticks([1,5,9,12,16,20,24],['2005Q1','2006Q1','2007Q1','2007Q4','2008Q4','2009Q4','2010Q4'],rotation=20)
ax.set_ylabel('Geometric mean fare index (2007Q4 = 100)');ax.legend(frameon=False,fontsize=8);ax.grid(axis='y',alpha=.15)
fig.savefig(OUT/'comparison_fare_paths.png',dpi=220);fig.savefig(OUT/'comparison_fare_paths.pdf');plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(7,5.2),sharex=True,layout='constrained')
evall=pd.concat(gapevents)
for ax,(name,title) in zip(axes,[('all_products_baseline_paired','A. All single-carrier itineraries'),('two_coupon_only_baseline_paired','B. Two-coupon single-carrier itineraries')]):
    z=evall[evall.model.eq(name)].sort_values('t')
    ax.errorbar(z.t,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ms=3,capsize=2,color='#215b72',ecolor='#89aabb',lw=.8)
    ax.axhline(0,color='#758089',lw=.8);ax.axvspan(13.5,16.5,color='#d9b875',alpha=.18);ax.axvline(16,ls='--',lw=.8,color='#7c6853');ax.set_title(title,loc='left',fontsize=10);ax.set_ylabel('DL/NW minus other-code log fare\nrelative to 2007Q4');ax.grid(axis='y',alpha=.15)
axes[-1].set_xticks([1,5,9,12,16,20,24],['2005Q1','2006Q1','2007Q1','2007Q4','2008Q4','2009Q4','2010Q4'],rotation=20)
fig.savefig(OUT/'carrier_gap_event.png',dpi=220);fig.savefig(OUT/'carrier_gap_event.pdf');plt.close(fig)
save('source_and_specification.json',{'source_file':source.name,'source_sha256':prod.sha(source),'protocol':'../protocol.md','baseline_reference':'2007Q4','fixed_original_overlap_routes':156,'fixed_original_legacy_control_routes':104,'group_rule':'cop == 0 or cr1 == cr2 identifies single carrier; DL/NW only when cr1 in DL,NW; all mixed itineraries separate','warning':'Descriptive operating-carrier product averages; no causal strategic response or fare-setting carrier assignment.'})
print(pd.DataFrame(summary).to_string(index=False))
print(pd.DataFrame(registry)[['model','pct','pct_lo','pct_hi']].to_string(index=False))
print(pd.DataFrame(gapstats).to_string(index=False))
print('Complete',flush=True)
