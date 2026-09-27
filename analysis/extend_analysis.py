#!/usr/bin/env python3
"""Pre-specified design diagnostics for the Delta–Northwest fare panel.

Source data are never modified. Run --help for the source and output locations.
All designs, including unsuccessful diagnostics, are exported to the registry.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import linalg, stats
import scipy
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ARCHIVE_SHA='75b2fe06890bf54f3466824e0309e3d52a74c3dfc3b22f940000face130ecfa9'
LEGACY=['AA','AS','CO','UA','US','HP']
DISTANCE_EDGES=[0,750,1500,2000,np.inf]
SHARE_EDGES=[0,.1,.5,.9,1.0000001]

def native(v):
    if isinstance(v,np.integer):return int(v)
    if isinstance(v,np.floating):return float(v)
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.bool_):return bool(v)
    raise TypeError(type(v).__name__)

def dump(path, value):
    path.write_text(json.dumps(value,indent=2,default=native,allow_nan=False)+'\n')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def read_source(path,out):
    digest=sha(path)
    if path.suffix=='.zip':
        assert digest==ARCHIVE_SHA,'Unexpected source archive; investigate before replacing input.'
        parts=[]
        with zipfile.ZipFile(path) as z:
            with z.open('mktdata79q1to16q3.dta') as f:
                for chunk in pd.read_stata(f,chunksize=250000,convert_categoricals=False):
                    b=chunk.loc[chunk.yr.between(2005,2010)].copy()
                    if len(b):parts.append(b)
        x=pd.concat(parts,ignore_index=True)
    else:
        # Literal airline code NA must not be converted to a missing value.
        x=pd.read_csv(path,keep_default_na=False)
    for col in ['cr1','cr2','ap1','ap2']:x[col]=x[col].fillna('').astype(str).str.strip()
    x=x[x.yr.between(2005,2010)].copy()
    audit={'source_file':path.name,'source_sha256':digest,'raw_rows':len(x),
           'source_kind':'NBER Borenstein aggregate archive, not BTS raw tickets',
           'software':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},
           'source_carrier_NA_counts':{c:int(x[c].eq('NA').sum()) for c in ['cr1','cr2']}}
    assert len(x)==4175354
    assert not x.duplicated(['cr1','cr2','yr','qtr','cop','ap1','ap2']).any()
    assert (x.ap1<=x.ap2).all()
    flow=[]
    for name,mask in [('Valid calendar quarters',x.qtr.between(1,4)),
                      ('Distinct nonblank endpoints',x.ap1.ne('')&x.ap2.ne('')&x.ap1.ne(x.ap2)),
                      ('Finite positive passengers and fare',np.isfinite(x.pax)&x.pax.gt(0)&np.isfinite(x.avprc)&x.avprc.gt(0))]:
        before=len(x);x=x.loc[mask.reindex(x.index)].copy()
        flow.append({'step':name,'removed':before-len(x),'remaining':len(x)})
    pd.DataFrame(flow).to_csv(out/'cleaning_flow.csv',index=False)
    x['route']=x.ap1+'-'+x.ap2;x['t']=(x.yr-2005)*4+x.qtr
    x['revenue']=x.pax*x.avprc
    single=x.cop.eq(0)|x.cr1.eq(x.cr2)
    x['single_pax']=np.where(single,x.pax,0)
    for c in ['DL','NW']:
        x[c.lower()]=np.where(single&x.cr1.eq(c),x.pax,0)
        x[c.lower()+'_any']=np.where(x.cr1.eq(c)|x.cr2.eq(c),x.pax,0)
        x[c.lower()+'_one']=np.where(x.cop.eq(0)&x.cr1.eq(c),x.pax,0)
    x['legacy']=np.where(single&x.cr1.isin(LEGACY),x.pax,0)
    x['uaco']=np.where(x.cr1.isin(['UA','CO'])|x.cr2.isin(['UA','CO']),x.pax,0)
    x['hpus']=np.where(x.cr1.isin(['HP','US'])|x.cr2.isin(['HP','US']),x.pax,0)
    x['wn']=np.where(x.cr1.eq('WN')|x.cr2.eq('WN'),x.pax,0)
    x['one_pax']=np.where(x.cop.eq(0),x.pax,0)
    sums=['pax','revenue','single_pax','dl','nw','dl_any','nw_any','dl_one','nw_one','legacy','uaco','hpus','wn','one_pax']
    p=x.groupby(['route','t'],as_index=False).agg(**{a:(a,'sum') for a in sums},distance=('nsdst','max'),records=('pax','size'))
    assert p.pax.sum()==x.pax.sum() and np.isclose(p.revenue.sum(),x.revenue.sum())
    p['fare']=p.revenue/p.pax;p['lnfare']=np.log(p.fare)
    p['one_share']=p.one_pax/p.pax
    pre=p[p.t.between(9,12)].copy()
    pre['both']=(pre.dl/pre.pax>=.05)&(pre.nw/pre.pax>=.05)
    pre['both_one']=(pre.dl_one/pre.pax>=.05)&(pre.nw_one/pre.pax>=.05)
    pre['legacy_active']=pre.legacy/pre.pax>=.05
    r=pre.groupby('route').agg(nq=('t','size'),pax_min=('pax','min'),pax_pre=('pax','mean'),fare_pre=('fare','mean'),
       distance=('distance','mean'),one_share=('one_share','mean'),both_q=('both','sum'),both_one_q=('both_one','sum'),
       legacy_q=('legacy_active','sum'),**{c:(c,'sum') for c in ['pax','single_pax','dl','nw','dl_any','nw_any','dl_one','nw_one','uaco','hpus','wn']})
    r['eligible']=r.nq.eq(4)&r.pax_min.ge(100)
    r['treated']=r.both_q.ge(3).astype(int)
    r['unexposed']=r.dl_any.eq(0)&r.nw_any.eq(0)
    r['legacy_control']=r.unexposed&r.legacy_q.ge(3)
    r['one_overlap']=r.both_one_q.ge(3)
    r['loose_one_overlap']=r.dl_one.ge(100)&r.nw_one.ge(100)
    r['single_coverage']=r.single_pax/r.pax
    # All recorded single-carrier codes enter this conditional index. Mixed
    # itineraries are excluded from its denominator, never hidden as a firm.
    cp=x[x.t.between(9,12)&single].groupby(['route','cr1']).pax.sum().rename('carrier_pax').reset_index()
    cp=cp.merge(r[['single_pax','pax']],on='route')
    cp['conditional_share']=cp.carrier_pax/cp.single_pax
    cp['hhi_piece']=10000*cp.conditional_share**2
    r['hhi_single']=cp.groupby('route').hhi_piece.sum()
    r['effective_codes_single']=10000/r.hhi_single
    r['dl_share_all']=r.dl/r.pax;r['nw_share_all']=r.nw/r.pax
    r['delta_proxy']=20000*r.dl_share_all*r.nw_share_all
    r['delta_conditional']=20000*(r.dl/r.single_pax.replace(0,np.nan))*(r.nw/r.single_pax.replace(0,np.nan))
    r['distance_bin']=pd.cut(r.distance,DISTANCE_EDGES,right=False,labels=False)
    r['share_bin']=pd.cut(r.one_share,SHARE_EDGES,right=False,labels=False)
    assert r.loc[r.eligible&r.single_pax.gt(0),'hhi_single'].between(0,10000.0001).all()
    assert r.loc[r.single_pax.eq(0),'hhi_single'].isna().all()
    assert r.delta_proxy.between(0,5000.0001).all()
    r['cell']=r.distance_bin.astype('Int64').astype(str)+'_'+r.share_bin.astype('Int64').astype(str)
    r.to_csv(out/'route_features.csv')
    p.to_csv(out/'all_route_quarters.csv.gz',index=False)
    cp.to_csv(out/'carrier_shares_2007.csv',index=False)
    audit.update(clean_rows=len(x),clean_route_quarters=len(p),carrier_codes=int(pd.concat([x.cr1,x.cr2]).loc[lambda s:s.ne('')].nunique()),
                 source_pax=int(x.pax.sum()),source_revenue=float(x.revenue.sum()),eligible_routes=int(r.eligible.sum()),
                 eligible_routes_without_single_carrier_traffic=int((r.eligible&r.single_pax.eq(0)).sum()))
    dump(out/'source_audit.json',audit)
    return p,r,audit

def estimate(d,controls=(),kind='did',reference=12,route_trends=False,post=16):
    d=d.sort_values(['route','t']).reset_index(drop=True)
    g,ids=pd.factorize(d.route);n=len(d);G=len(ids);times=sorted(d.t.unique())
    t=d.t.to_numpy(float);tr=d.treated.to_numpy(float)
    if kind=='event':
        targets=[int(v) for v in times if v!=reference]
        A=np.column_stack([tr*(t==v) for v in targets]);names=[f'q{v}' for v in targets]
    elif kind=='dose':
        A=(d.delta_proxy.to_numpy()/100*(t>=post))[:,None];names=['per100']
    elif kind=='dose_with_group':
        # Centered within-treated gradient plus separate binary overlap effect.
        z=d.delta_proxy.to_numpy()/100
        z=z-d.loc[d.treated.eq(1)].groupby('route').delta_proxy.first().mean()/100*tr
        A=np.column_stack([tr*(t>=post),z*(t>=post)]);names=['overlap','per100_within']
    elif kind=='groups':
        A=np.column_stack([d.low.to_numpy()*(t>=post),d.high.to_numpy()*(t>=post)]);names=['low','high']
    else:A=(tr*(t>=post))[:,None];names=['did']
    Z=[np.column_stack([(t==v).astype(float) for v in times[1:]])]
    for col in controls:
        vals=d[col].astype(str).to_numpy()
        levels=sorted(set(vals))
        Z.append(np.column_stack([(vals==a)*(t==q) for a in levels[1:] for q in times[1:]]).astype(float))
    if route_trends:Z.append(np.eye(G)[g]*(t-t.mean())[:,None])
    Z=np.column_stack(Z)
    counts=np.bincount(g)
    def within(X):
        X=np.asarray(X,dtype=float)
        if X.ndim==1:return X-np.bincount(g,weights=X)[g]/counts[g]
        sums=np.zeros((G,X.shape[1]));np.add.at(sums,g,X)
        return X-sums[g]/counts[g,None]
    yw=within(d.lnfare.to_numpy());Aw=within(A);Zw=within(Z)
    Q,R,piv=linalg.qr(Zw,mode='economic',pivoting=True,check_finite=False)
    diag=np.abs(np.diag(R));rank=int((diag>max(Zw.shape)*np.finfo(float).eps*(diag.max() if len(diag) else 0)).sum())
    Q=Q[:,:rank];ay=Aw-Q@(Q.T@Aw);yy=yw-Q@(Q.T@yw)
    k=A.shape[1]
    assert np.linalg.matrix_rank(ay)==k,f'Unidentified target {kind}, controls {controls}'
    bread=np.linalg.inv(ay.T@ay);b=bread@(ay.T@yy);res=yy-ay@b
    scores=np.zeros((G,k));np.add.at(scores,g,ay*res[:,None])
    df=n-G-rank-k
    assert df>0
    cov=bread@(scores.T@scores)@bread*G/(G-1)*(n-1)/df
    se=np.sqrt(np.maximum(np.diag(cov),0));critical=stats.t.ppf(.975,G-1)
    out={'N':n,'routes':G,'treated':int(d.groupby('route').treated.first().sum()),'controls':int(G-d.groupby('route').treated.first().sum()),
         'quarter_count':len(times),'nuisance_rank':rank,'df_resid':df,'coef':{}}
    for j,name in enumerate(names):
        lo=b[j]-critical*se[j];hi=b[j]+critical*se[j]
        out['coef'][name]={'b':b[j],'se':se[j],'p':float(2*stats.t.sf(abs(b[j]/se[j]),G-1)),
                           'lo':lo,'hi':hi,'pct':100*np.expm1(b[j]),'pct_lo':100*np.expm1(lo),'pct_hi':100*np.expm1(hi)}
    if kind=='event':
        idx=[i for i,q in enumerate(targets) if q<12]
        v=b[idx];c=cov[np.ix_(idx,idx)];q=len(idx)
        F=float(v@np.linalg.solve(c,v)/q)
        out['pre_2005_2007']={'F':F,'df_num':q,'df_den':G-1,'p':float(stats.f.sf(F,q,G-1))}
    if kind=='groups':
        diff=b[1]-b[0];sd=np.sqrt(cov[0,0]+cov[1,1]-2*cov[0,1])
        out['high_minus_low']={'b':diff,'se':sd,'p':float(2*stats.t.sf(abs(diff/sd),G-1))}
    return out,(d,np.column_stack([Aw,Zw[:,piv[:rank]]]),yw,g)

def support(d,r,out,name):
    a=r.loc[d.route.unique()].copy()
    count=a.groupby(['cell','treated']).size().unstack(fill_value=0)
    for col in [0,1]:
        if col not in count:count[col]=0
    count.columns=['control_routes' if c==0 else 'treated_routes' for c in count.columns]
    count['retained']=count.control_routes.ge(3)&count.treated_routes.ge(3)
    count.to_csv(out/f'support_{name}.csv')
    keep=set(count.index[count.retained]);retained=a[a.cell.isin(keep)].index
    return d[d.route.isin(retained)].copy()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--old-panel',type=Path);ap.add_argument('--use-prepared',action='store_true',help='Reuse saved panels after verifying source checksum; for estimation/debugging only')
    args=ap.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
    print('Reading canonical source and constructing baseline features',flush=True)
    if args.use_prepared:
        audit=json.loads((out/'source_audit.json').read_text())
        assert sha(args.source)==audit['source_sha256']
        p=pd.read_csv(out/'all_route_quarters.csv.gz');r=pd.read_csv(out/'route_features.csv',index_col='route')
    else:p,r,audit=read_source(args.source,out)
    def panel(mask):
        return p.merge(r.loc[mask].drop(columns=['pax','distance','single_pax','dl','nw','dl_any','nw_any','dl_one','nw_one','uaco','hpus','wn','one_share']),on='route').merge(r[['one_share','distance','uaco','hpus','wn']],on='route',suffixes=('','_2007'))
    legacy=panel(r.eligible&(r.treated.eq(1)|r.legacy_control))
    assert len(legacy)==6259 and legacy.route.nunique()==261
    if args.old_panel:
        old=pd.read_csv(args.old_panel).sort_values(['route','t']);now=legacy.sort_values(['route','t'])
        assert np.array_equal(old.route.to_numpy(),now.route.to_numpy()) and np.array_equal(old.t.to_numpy(),now.t.to_numpy())
        assert np.allclose(old.fare,now.fare,atol=1e-9,rtol=1e-12)
        audit['prior_fare_max_abs_difference']=float(np.max(np.abs(old.fare.to_numpy()-now.fare.to_numpy())))
        dump(out/'source_audit.json',audit)
    valid=legacy[legacy.distance_2007.gt(0)].copy()
    expanded=panel(r.eligible&(r.treated.eq(1)|r.unexposed));expanded=expanded[expanded.distance_2007.gt(0)].copy()
    common=support(valid,r,out,'legacy');common_all=support(expanded,r,out,'all_unexposed')
    for label,d in [('legacy',legacy),('legacy_valid',valid),('legacy_support',common),('all_unexposed',expanded),('all_support',common_all)]:
        d.to_csv(out/f'panel_{label}.csv',index=False)
    results={};datasets={};specs=[]
    def run(label,d,controls=(),kind='did',**kwargs):
        print('Estimating '+label,flush=True)
        fit,detail=estimate(d,controls,kind=kind,**kwargs);results[label]=fit;datasets[label]=(d,controls,kind,kwargs)
        for term,c in fit['coef'].items():
            specs.append({'model':label,'term':term,**{k:v for k,v in fit.items() if k not in ['coef','pre_2005_2007','high_minus_low']},**c})
        return fit
    run('published_baseline',legacy)
    assert abs(results['published_baseline']['coef']['did']['b']+.0588984578886)<1e-9
    run('same_sample_unadjusted',valid)
    run('distance_quarter',valid,['distance_bin'])
    run('distance_and_composition_quarter',valid,['distance_bin','share_bin'])
    run('common_support_cell_quarter',common,['cell'])
    run('all_controls_unadjusted',expanded)
    run('all_controls_adjusted',expanded,['distance_bin','share_bin'])
    run('all_controls_support',common_all,['cell'])
    run('route_trends',valid,['distance_bin','share_bin'],route_trends=True)
    run('end_2009',valid[valid.t<=20],['distance_bin','share_bin'])
    run('start_2006',valid[valid.t>=5],['distance_bin','share_bin'])
    run('exclude_UA_CO',valid[valid.uaco_2007.eq(0)],['distance_bin','share_bin'])
    run('omit_transition',valid[~valid.t.between(14,16)],['distance_bin','share_bin'],post=17)
    for label,d,ctrl in [('base',valid,[]),('adjusted',valid,['distance_bin','share_bin']),('support',common,['cell']),('expanded_support',common_all,['cell'])]:
        run('event_'+label,d,ctrl,kind='event')
    median=float(r.loc[r.eligible&r.treated.eq(1),'delta_proxy'].median())
    valid['low']=(valid.treated.eq(1)&valid.delta_proxy.le(median)).astype(int)
    valid['high']=(valid.treated.eq(1)&valid.delta_proxy.gt(median)).astype(int)
    run('concentration_dose',valid,['distance_bin','share_bin'],kind='dose')
    run('concentration_within_overlap',valid,['distance_bin','share_bin'],kind='dose_with_group')
    run('concentration_groups',valid,['distance_bin','share_bin'],kind='groups')
    balance=[]
    for label,d in [('legacy',legacy),('legacy_valid',valid),('common_support',common),('all_support',common_all)]:
        a=r.loc[d.route.unique()]
        for tr,b in a.groupby('treated'):
            balance.append({'sample':label,'treated':int(tr),'routes':len(b),**{c:float(b[c].mean()) for c in ['distance','one_share','fare_pre','pax_pre','single_coverage','hhi_single','delta_proxy']},
                            'wn_positive_routes':int(b.wn.gt(0).sum()),'uaco_positive_routes':int(b.uaco.gt(0).sum()),'sustained_one_overlap_routes':int(b.one_overlap.sum()),'loose_one_overlap_routes':int(b.loose_one_overlap.sum())})
    pd.DataFrame(balance).to_csv(out/'balance.csv',index=False)
    # Check adjusted/event/trend FWL coefficient and CR1 covariance against a
    # separately constructed explicit-route-dummy statsmodels regression.
    checks=[]
    routes=list(valid[valid.treated.eq(1)].route.unique()[:15])+list(valid[valid.treated.eq(0)].route.unique()[:15])
    routes+=list(valid.groupby('route').size()[lambda z:z<24].index)
    subset=valid[valid.route.isin(routes)]
    for label,kind,trends in [('adjusted','did',False),('event','event',False),('trend','did',True)]:
        z,(sd,X,y,g)=estimate(subset,['distance_bin','share_bin'],kind=kind,route_trends=trends)
        # X includes within nuisance basis; add full independent route indicators.
        D=pd.get_dummies(sd.route).to_numpy(float)
        explicit=sm.OLS(sd.lnfare.to_numpy(),np.column_stack([X,D])).fit(cov_type='cluster',cov_kwds={'groups':g},use_t=True)
        k=len(z['coef']);b=np.array([c['b'] for c in z['coef'].values()]);se=np.array([c['se'] for c in z['coef'].values()])
        db=float(np.max(abs(explicit.params[:k]-b)));ds=float(np.max(abs(explicit.bse[:k]-se)))
        assert db<1e-8 and ds<1e-8
        checks.append({'model':label,'max_beta_difference':db,'max_se_difference':ds,'N':len(sd)})
    meta={'analysis_protocol':'analysis_plan.md dated before extension estimates','distance_edges':[0,750,1500,2000,'infinity'],'share_edges':[0,.1,.5,.9,1],
          'minimum_routes_each_group_per_support_cell':3,'concentration_median_split':median,'validation':checks,'balance':balance,
          'source_audit':audit,'estimand_note':'Conditional relative fare changes; no model selected by pretest or significance.'}
    dump(out/'extended_results.json',{'models':results,'metadata':meta})
    pd.DataFrame(specs).to_csv(out/'model_registry.csv',index=False)
    ev=[]
    for model,fit in results.items():
        if model.startswith('event_'):
            for term,c in fit['coef'].items():ev.append({'model':model,'t':int(term[1:]),**c})
    pd.DataFrame(ev).to_csv(out/'event_coefficients.csv',index=False)
    plot(pd.DataFrame(ev),out)
    print(pd.DataFrame(specs).query('term in ["did","per100","per100_within","low","high"]')[['model','term','pct','pct_lo','pct_hi','routes','treated']].to_string(index=False))
    print('PRETESTS',json.dumps({k:v.get('pre_2005_2007') for k,v in results.items() if k.startswith('event_')}))

def plot(ev,out):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(7,4.8),sharex=True,layout='constrained')
    for ax,(model,title) in zip(axes,[('event_base','A. Route and quarter effects'),('event_adjusted','B. Add baseline distance and service composition × quarter')]):
        z=ev[ev.model.eq(model)].sort_values('t')
        ax.axhline(0,color='#758089',lw=.8);ax.axvspan(13.5,16.5,color='#e5b35f',alpha=.15)
        ax.axvline(16,color='#98603e',ls='--',lw=1)
        ax.errorbar(z.t,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ms=3,capsize=2,color='#215b72',ecolor='#88a9b8',lw=.8)
        ax.scatter([12],[0],facecolors='white',edgecolors='#215b72',s=28,zorder=5)
        ax.set_title(title,loc='left',fontsize=10);ax.set_ylabel('Relative log fare');ax.grid(axis='y',alpha=.16)
    axes[-1].set_xticks([1,5,9,12,16,20,24],['2005Q1','2006Q1','2007Q1','2007Q4','2008Q4','2009Q4','2010Q4'],rotation=20)
    fig.savefig(out/'event_comparison.png',dpi=220);fig.savefig(out/'event_comparison.pdf');plt.close(fig)

if __name__=='__main__':main()
