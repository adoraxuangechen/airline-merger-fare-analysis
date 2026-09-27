#!/usr/bin/env python3
"""Auditable Delta–Northwest fare analysis. Run from any directory.

This file never modifies the source CSV. No winsorization or random sampling is
used. All source columns and cleaning decisions are documented in README.md.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels
import statsmodels.api as sm

OLD_PAIRS=[('DTW','MSP'),('DTW','SEA'),('DTW','SLC'),('DTW','MEM'),('DTW','PHX'),('MSP','SEA'),('MSP','SLC'),('MSP','MEM'),('MSP','PHX'),('SEA','SLC'),('MEM','ATL'),('MEM','SLC')]
OLD_ROUTES={'-'.join(sorted(x)) for x in OLD_PAIRS}
LEGACY=['AA','AS','CO','UA','US','HP']

def native(o):
    if isinstance(o,(np.integer,)):return int(o)
    if isinstance(o,(np.floating,)):return float(o)
    if isinstance(o,np.ndarray):return o.tolist()
    raise TypeError(type(o).__name__)

def save_json(path, obj):
    path.write_text(json.dumps(obj,indent=2,default=native,allow_nan=False)+'\n')

def cluster_fit(y,X,g,absorbed=0,normal=False):
    """OLS on a supplied design; CR1 covariance clustered by route.

    absorbed counts route intercepts removed beforehand. For the legacy partial
    transformation it is deliberately 0, matching statsmodels' reported SEs.
    """
    n,k=X.shape;G=int(g.max()+1)
    assert np.linalg.matrix_rank(X)==k, 'Rank deficient regression'
    bread=np.linalg.inv(X.T@X)
    beta=bread@(X.T@y);res=y-X@beta
    score=np.zeros((G,k));np.add.at(score,g,X*res[:,None])
    df=n-k-absorbed
    assert df>0 and G>1
    cov=bread@(score.T@score)@bread*(G/(G-1))*((n-1)/df)
    se=np.sqrt(np.maximum(np.diag(cov),0))
    crit=stats.norm.ppf(.975) if normal else stats.t.ppf(.975,G-1)
    p=2*(stats.norm.sf(abs(beta/se)) if normal else stats.t.sf(abs(beta/se),G-1))
    return beta,se,cov,p,crit,df,res

def fit(d,event=False,weight=None,legacy=False,reference=15,post=16,ycol='lnfare',event_window=None,precomputed_y=None,return_details=False):
    """Route and quarter FE via weighted within transformation of ALL columns.

    t=1 is 2005Q1, t=16 is 2008Q4; reference 15 is 2008Q3. Route
    weights, when supplied, stay fixed at mean 2007 route passenger count.
    Legacy event mode intentionally leaves event regressors undemeaned, as in
    the supplied pasted script, with y demeaned over its original 24Q sample.
    """
    d=d.sort_values(['route','t']).copy()
    if event_window is not None:d=d[d.t.between(*event_window)].copy()
    g,ids=pd.factorize(d.route);G=len(ids);n=len(d)
    t=d.t.to_numpy();tr=d.treated.to_numpy(float);y=d[ycol].to_numpy(float)
    w=np.ones(n) if weight is None else d[weight].to_numpy(float)
    assert np.isfinite(y).all() and (w>0).all()
    times=sorted(d.t.unique());timeX=np.column_stack([(t==v).astype(float) for v in times[1:]])
    if event:
        targets=[int(j) for j in times if j!=reference]
        X0=np.column_stack([tr*(t==j) for j in targets]);names=['event_'+str(j-16) for j in targets]
    else:
        targets=[];X0=(tr*(t>=post)).reshape(-1,1);names=['did']
    sw=np.bincount(g,weights=w,minlength=G)
    def within(A):
        A=np.asarray(A)
        if A.ndim==1:return A-np.bincount(g,weights=w*A,minlength=G)[g]/sw[g]
        sums=np.column_stack([np.bincount(g,weights=w*A[:,j],minlength=G) for j in range(A.shape[1])])
        return A-sums[g]/sw[g,None]
    if legacy:
        if event:
            yy=d[precomputed_y].to_numpy(float)
            xx=np.column_stack([X0,np.ones(n),timeX])
        else:
            yy=within(y);xx=np.column_stack([within(X0),np.ones(n),timeX])
        b,se,cov,p,crit,df,res=cluster_fit(yy,xx,g,normal=True)
    else:
        yy=within(y);xx=within(np.column_stack([X0,timeX]))
        yy=yy*np.sqrt(w);xx=xx*np.sqrt(w)[:,None]
        b,se,cov,p,crit,df,res=cluster_fit(yy,xx,g,absorbed=G)
    out={'N':n,'routes':G,'treated_routes':int(d.groupby('route').treated.first().sum()),'control_routes':int(G-d.groupby('route').treated.first().sum()),'quarters':len(times),'df_resid':df,'coef':{}}
    for j,name in enumerate(names):
        out['coef'][name]={'b':b[j],'se':se[j],'p':p[j],'lo':b[j]-crit*se[j],'hi':b[j]+crit*se[j], 'percent':100*np.expm1(b[j]),'percent_lo':100*np.expm1(b[j]-crit*se[j]),'percent_hi':100*np.expm1(b[j]+crit*se[j])}
    if event and not legacy:
        for label,idx in [('all_pre',[i for i,v in enumerate(targets) if v<reference]),('pre_announcement',[i for i,v in enumerate(targets) if v<=13])]:
            if idx:
                beta=b[idx];cv=cov[np.ix_(idx,idx)];q=len(idx)
                F=float(beta@np.linalg.solve(cv,beta)/q)
                out[label]={'F':F,'df_num':q,'df_den':G-1,'p':float(stats.f.sf(F,q,G-1))}
    if return_details:return out,(d,g,yy,xx,cov,res)
    return out

def model_row(label,res):
    return {'specification':label,**{k:v for k,v in res.items() if k not in ('coef',)},**res['coef']['did']}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    ap.add_argument('--printed-b1',type=Path,help='Optional CSV transcription of original Table B1, for audit comparison only')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    print('Reading and auditing source CSV',flush=True)
    x=pd.read_csv(args.input)
    raw_cols=list(x)
    digest=hashlib.sha256(args.input.read_bytes()).hexdigest()
    assert set(raw_cols)=={'cr1','cr2','yr','qtr','cop','ap1','ap2','pax','nsdst','avprc','avdst'}
    key=['cr1','cr2','yr','qtr','cop','ap1','ap2']
    audit={'input_name':args.input.name,'sha256':digest,'bytes':args.input.stat().st_size,'raw_rows':len(x),'columns':raw_cols,'dtypes':x.dtypes.astype(str).to_dict(),'missing':x.isna().sum().to_dict(),'exact_duplicates':int(x.duplicated().sum()),'natural_key_duplicates':int(x.duplicated(key).sum()),'natural_key':key,'all_pairs_lexically_ordered':bool((x.ap1<=x.ap2).all()),'same_endpoint_rows':int(x.ap1.eq(x.ap2).sum()),'zero_distance_rows':int(x.nsdst.eq(0).sum()),'cop_counts':x.cop.value_counts().sort_index().to_dict(),'numeric':x.describe().to_dict(),'nunique':x.nunique().to_dict(),'carrier_missing_by_cop':pd.crosstab(x.cop,x.cr2.isna()).to_dict()}
    assert audit['exact_duplicates']==0 and audit['natural_key_duplicates']==0
    assert audit['all_pairs_lexically_ordered']
    audit['software']={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__,'matplotlib':matplotlib.__version__}
    flow=[]
    def step(name,mask):
        nonlocal x
        n=len(x);x=x.loc[mask].copy();flow.append({'step':name,'removed':n-len(x),'remaining':len(x)})
    step('Calendar years 2005 through 2010',x.yr.between(2005,2010)&x.qtr.between(1,4))
    x['route']=x.ap1+'-'+x.ap2;x['t']=(x.yr-2005)*4+x.qtr
    # Preserve the original data aggregation BEFORE any new cleaning.
    orig=x.groupby(['route','t'],as_index=False).agg(fare=('avprc','mean'),disp=('avprc','std'),records=('avprc','size'),pax=('pax','sum'))
    orig['treated']=orig.route.isin(OLD_ROUTES).astype(int);orig['lnfare']=np.log(orig.fare)
    old_counts=orig.groupby('route').t.nunique();old=orig[orig.route.isin(old_counts[old_counts>=4].index)].copy()
    inventory=pd.DataFrame({'listed_route':sorted(OLD_ROUTES)})
    inventory['observed_raw']=inventory.listed_route.isin(orig.route.unique())
    inventory['in_original_regression']=inventory.listed_route.isin(old.route.unique())
    inventory.to_csv(out/'original_treated_inventory.csv',index=False)
    print('Reproducing original regressions',flush=True)
    old['lnfare_fullsample_route_demeaned']=old.lnfare-old.groupby('route').lnfare.transform('mean')
    original={'fare':fit(old,legacy=True),'fare_correct_twfe_same_sample':fit(old),'event':fit(old,event=True,legacy=True,event_window=(8,24),precomputed_y='lnfare_fullsample_route_demeaned'),'omit_recession':fit(old[~old.t.isin([15,16,17,18,19,20])],legacy=True)}
    disp=orig[(orig.records>=2)&orig.disp.notna()&(orig.disp>0)].copy();dc=disp.groupby('route').t.nunique();disp=disp[disp.route.isin(dc[dc>=4].index)].copy();disp['lndisp']=np.log(disp.disp)
    original['dispersion']=fit(disp,legacy=True,ycol='lndisp')
    save_json(out/'original_reproduction.json',original)
    oe=pd.DataFrame([{'rel_time':int(k.split('_')[1]),**v} for k,v in original['event']['coef'].items()])
    oe.to_csv(out/'original_event_coefficients.csv',index=False)
    if args.printed_b1:
        printed=pd.read_csv(args.printed_b1)
        cmp=printed.merge(oe,left_on='event_quarter',right_on='rel_time')
        cmp['coefficient_difference']=cmp.b-cmp.printed_coefficient
        cmp['standard_error_difference']=cmp.se-cmp.printed_standard_error
        cmp['coefficient_matches_printed_3dp']=cmp.b.round(3).eq(cmp.printed_coefficient)
        cmp.to_csv(out/'original_table_b1_comparison.csv',index=False)
    orig.to_csv(out/'original_route_quarter_panel.csv',index=False)
    # No guessed values are imputed. Missing carrier labels remain in market fares
    # but do not count as named-carrier evidence in the exposure classifier.
    step('Nonmissing, distinct airport endpoints',x.ap1.notna()&x.ap2.notna()&x.ap1.ne(x.ap2))
    step('Finite positive passenger count',np.isfinite(x.pax)&x.pax.gt(0))
    step('Finite positive cell mean fare',np.isfinite(x.avprc)&x.avprc.gt(0))
    x['revenue']=x.pax*x.avprc
    single=x.cop.eq(0)|x.cr1.eq(x.cr2)
    for code in ['DL','NW']:
        x[code+'_pax']=np.where(single&x.cr1.eq(code),x.pax,0)
        x[code+'_any']=np.where(x.cr1.eq(code)|x.cr2.eq(code),x.pax,0)
        x[code+'_direct']=np.where(x.cop.eq(0)&x.cr1.eq(code),x.pax,0)
    x['legacy_pax']=np.where(single&x.cr1.isin(LEGACY),x.pax,0)
    x['direct_pax']=np.where(x.cop.eq(0),x.pax,0)
    x['unknown_pax']=np.where(x.cr1.isna()|(x.cop.eq(1)&x.cr2.isna()),x.pax,0)
    panel=x.groupby(['route','t'],as_index=False).agg(pax=('pax','sum'),revenue=('revenue','sum'),records=('pax','size'),fare_unweighted=('avprc','mean'),dl=('DL_pax','sum'),nw=('NW_pax','sum'),dl_any=('DL_any','sum'),nw_any=('NW_any','sum'),dl_direct=('DL_direct','sum'),nw_direct=('NW_direct','sum'),legacy=('legacy_pax','sum'),direct_pax=('direct_pax','sum'),distance=('nsdst','max'),unknown_pax=('unknown_pax','sum'))
    assert not panel.duplicated(['route','t']).any()
    panel['fare']=panel.revenue/panel.pax;panel['lnfare']=np.log(panel.fare);panel['direct_share']=panel.direct_pax/panel.pax
    assert np.isfinite(panel.lnfare).all()
    assert np.isclose(panel.revenue.sum(),x.revenue.sum()) and panel.pax.sum()==x.pax.sum()
    for code in ['dl','nw','legacy']:panel[code+'_active']=panel[code].div(panel.pax).ge(.05).astype(int)
    panel['both_active']=panel.dl_active.eq(1)&panel.nw_active.eq(1)
    pre=panel[panel.t.between(9,12)]
    c=pre.groupby('route').agg(nq=('t','size'),pax_min=('pax','min'),pax_pre=('pax','mean'),fare_pre=('fare','mean'),dl_q=('dl_active','sum'),nw_q=('nw_active','sum'),both_q=('both_active','sum'),legacy_q=('legacy_active','sum'),dl_any=('dl_any','sum'),nw_any=('nw_any','sum'),direct=('direct_share','mean'),distance=('distance','mean'),dl_direct=('dl_direct','sum'),nw_direct=('nw_direct','sum'),unknown_pax=('unknown_pax','sum'))
    c['group']=np.select([c.both_q>=3,(c.dl_any==0)&(c.nw_any==0)&(c.legacy_q>=3)],['overlap','unexposed_legacy'],default='other')
    c['eligible']=(c.nq==4)&(c.pax_min>=100)
    c['direct_overlap']=(c.dl_direct>=100)&(c.nw_direct>=100)
    c['original_treated']=c.index.isin(OLD_ROUTES)
    c.to_csv(out/'route_classification.csv')
    pd.DataFrame(flow).to_csv(out/'row_cleaning_flow.csv',index=False)
    panel.to_csv(out/'clean_route_quarter_panel.csv',index=False)
    mainc=c[c.eligible&c.group.isin(['overlap','unexposed_legacy'])].copy()
    d=panel.merge(mainc[['group','pax_pre','fare_pre','direct','distance']],on='route',suffixes=('','_pre'))
    d['treated']=d.group.eq('overlap').astype(int);d['yr']=2005+(d.t-1)//4;d['qtr']=(d.t-1)%4+1
    d.to_csv(out/'analysis_panel.csv',index=False)
    mainc.to_csv(out/'main_route_inventory.csv')
    balanced=d.groupby('route').t.nunique();broutes=balanced[balanced==24].index
    print('Estimating main and sensitivity specifications',flush=True)
    results={'baseline':fit(d),'fixed_pre_pax':fit(d,weight='pax_pre'),'balanced':fit(d[d.route.isin(broutes)]),'omit_announcement_completion':fit(d[~d.t.between(14,16)],post=17),'exclude_crisis_window':fit(d[~d.t.between(15,20)]),'event':fit(d,event=True),'early_pre_event':fit(d[d.t<=12],event=True,reference=12)}
    # Inherited matching sensitivity, fixed pre-period characteristics only.
    from scipy.spatial.distance import cdist
    a=mainc.copy();features=np.column_stack([np.log(a.fare_pre),np.log(a.pax_pre),a.distance/1000,a.direct]);features=(features-features.mean(0))/features.std(0,ddof=1)
    ti=np.where(a.group=='overlap')[0];ci=np.where(a.group=='unexposed_legacy')[0];mat=cdist(features[ti],features[ci]);idx=ci[mat.argmin(axis=1)];counts=pd.Series(a.index[idx]).value_counts();weights={r:1. for r in a.index[ti]};weights.update(counts.to_dict())
    md=d[d.route.isin(weights)].copy();md['match_weight']=md.route.map(weights)
    results['matched']=fit(md,weight='match_weight');results['matched_event']=fit(md,event=True,weight='match_weight');results['matching']={'controls_used':len(counts),'median_distance':float(np.median(mat.min(1))),'max_control_reuse':int(counts.max())}
    # Broader carrier-presence definition sensitivity; same 2007 eligibility.
    # Here any itinerary mentioning both airlines at least once in 2007 suffices.
    bc=c[c.eligible].copy();bc['broad_treated']=(bc.dl_any>0)&(bc.nw_any>0)
    bm=bc[bc.broad_treated|bc.group.eq('unexposed_legacy')]
    bd=panel.merge(bm[['broad_treated']],on='route');bd['treated']=bd.broad_treated.astype(int)
    results['broad_any_presence']=fit(bd)
    # Exact broader definitions from revised check_scope.py / check_full_panel.py.
    # Any-code2007 comparison group is any other route with positive single-
    # carrier legacy passengers, not necessarily unexposed to DL or NW.
    q=pre.groupby('route').agg(dl_any=('dl_any','sum'),nw_any=('nw_any','sum'),legacy=('legacy','sum')).join(c[['eligible']])
    q=q[q.eligible].copy();q['treated']=(q.dl_any.gt(0)&q.nw_any.gt(0)).astype(int)
    q=q[q.treated.eq(1)|q.legacy.gt(0)]
    results['anycode_2007']=fit(panel.merge(q[['treated']],on='route'))
    nc=panel.groupby('route').t.nunique();ss=panel[panel.route.isin(nc[nc>=4].index)].copy()
    b=ss[ss.t<16].groupby('route').agg(dl=('dl_any','sum'),nw=('nw_any','sum'),legacy=('legacy','sum'))
    b['treated']=(b.dl.gt(0)&b.nw.gt(0)).astype(int)
    broad=ss.merge(b.loc[b.treated.eq(1)|b.legacy.gt(0),['treated']],on='route')
    results['broad_reconstruction']=fit(broad)
    before=broad[broad.t<16].route.unique();after=broad[broad.t>=16].route.unique()
    results['broad_both_periods']=fit(broad[broad.route.isin(np.intersect1d(before,after))])
    results['broad_all_controls']=fit(ss.merge(b[['treated']],on='route'))
    # Zero endpoint distances are source sentinels: retained for fare outcomes.
    distance_nunique=x.groupby('route').nsdst.nunique()
    audit['distance_audit']={'within_route_varying_distance_routes':int(distance_nunique.gt(1).sum()),'main_zero_distance_routes':sorted(d.loc[d.distance.eq(0),'route'].unique()),'main_zero_distance_rows':int(d.distance.eq(0).sum()),'main_zero_distance_rows_2007':int(d[d.t.between(9,12)].distance.eq(0).sum())}
    results['exclude_zero_distance_route']=fit(d[d.distance.gt(0)])
    # Sequential bridge: each adjacent row alters one specified element.
    bridge=[]
    bridge.append(model_row('A Original arithmetic fares, old groups, partial demeaning',original['fare']))
    bridge.append(model_row('B Same observations/outcome/groups, correct TWFE',original['fare_correct_twfe_same_sample']))
    pw=panel[panel.route.isin(old.route.unique())].copy();pw['treated']=pw.route.isin(OLD_ROUTES).astype(int)
    # The four self-airport records fall outside original >=4Q route sample.
    assert set(zip(pw.route,pw.t))==set(zip(old.route,old.t))
    bridge.append(model_row('C Same observations/groups, passenger-weighted market fare',fit(pw)))
    eligible=pw[pw.route.isin(c[c.eligible].index)].copy()
    bridge.append(model_row('D Add 2007 four-quarter and >=100 pax eligibility',fit(eligible)))
    empirical=eligible.copy();empirical['treated']=empirical.route.isin(c[c.eligible&c.group.eq('overlap')].index).astype(int)
    bridge.append(model_row('E Change treatment to empirical 2007 material overlap',fit(empirical)))
    bridge.append(model_row('F Restrict controls to 2007 unexposed legacy routes (main)',results['baseline']))
    pd.DataFrame(bridge).to_csv(out/'specification_bridge.csv',index=False)
    # Pre-period observable differences and route attrition.
    descr=[]
    for label in ['overlap','unexposed_legacy']:
        aa=mainc[mainc.group==label];dd=d[d.group==label]
        descr.append({'group':label,'routes':len(aa),'route_quarters':len(dd),'records':dd.records.sum(),'sample_pax':dd.pax.sum(),'mean_2007_pax':aa.pax_pre.mean(),'mean_2007_fare':aa.fare_pre.mean(),'mean_distance':aa.distance.mean(),'mean_direct_share':aa.direct.mean(),'median_2007_fare':aa.fare_pre.median(),'unknown_2007_pax':aa.unknown_pax.sum()})
    pd.DataFrame(descr).to_csv(out/'sample_descriptives.csv',index=False)
    results['descriptive']=descr
    results['sample_flow']={'raw_rows':audit['raw_rows'],'clean_rows':len(x),'clean_routes':panel.route.nunique(),'clean_route_quarters':len(panel),'clean_pax':panel.pax.sum(),'eligible_2007_routes':int(c.eligible.sum()),'2007_groups':c.group.value_counts().to_dict(),'eligible_groups':c.loc[c.eligible,'group'].value_counts().to_dict(),'main_routes':len(mainc),'main_route_quarters':len(d),'main_records':int(d.records.sum()),'main_pax':int(d.pax.sum()),'balanced_routes':len(broutes),'balanced_treated':int(mainc.loc[mainc.index.isin(broutes),'group'].eq('overlap').sum()),'balanced_control':int(mainc.loc[mainc.index.isin(broutes),'group'].eq('unexposed_legacy').sum()),'min_quarters':int(d.groupby('route').size().min()),'main_direct_overlap':int(mainc.direct_overlap.sum()),'main_unknown_2007_pax':mainc.unknown_pax.sum()}
    # Independent numerical verification against full dummy OLS/WLS and cluster SE.
    print('Validating absorbed estimator against explicit dummy regressions',flush=True)
    verify=[]
    unbalanced_routes=list(d.groupby('route').size()[lambda z:z<24].index)
    sr=list(dict.fromkeys(unbalanced_routes+list(d[d.treated.eq(1)].route.unique()[:12])+list(d[d.treated.eq(0)].route.unique()[:12])))
    for weighted in [False,True]:
        sd=d[d.route.isin(sr)].sort_values(['route','t']);wc='pax_pre' if weighted else None
        withinfit=fit(sd,weight=wc)
        des=np.column_stack([sd.treated*(sd.t>=16),np.ones(len(sd)),pd.get_dummies(sd.route,drop_first=True).to_numpy(),pd.get_dummies(sd.t,drop_first=True).to_numpy()]).astype(float)
        mdl=sm.WLS(sd.lnfare.to_numpy(),des,weights=sd.pax_pre.to_numpy() if weighted else np.ones(len(sd))).fit(cov_type='cluster',cov_kwds={'groups':sd.route.to_numpy()},use_t=True)
        bdiff=float(abs(mdl.params[0]-withinfit['coef']['did']['b']));sediff=float(abs(mdl.bse[0]-withinfit['coef']['did']['se']))
        assert bdiff<1e-9 and sediff<1e-9
        verify.append({'weighted':weighted,'N':len(sd),'routes':sd.route.nunique(),'dummy_beta':float(mdl.params[0]),'within_beta':withinfit['coef']['did']['b'],'beta_abs_difference':bdiff,'se_abs_difference':sediff})
    # Exact legacy SE convention verification on a representative old sample.
    os=old[old.route.isin(list(old[old.treated.eq(1)].route.unique())+list(old[old.treated.eq(0)].route.unique()[:20]))].sort_values(['route','t'])
    ofit,(_,gg,yy,xx,cv,res)=fit(os,legacy=True,return_details=True)
    om=sm.OLS(yy,xx).fit(cov_type='cluster',cov_kwds={'groups':gg})
    assert abs(om.params[0]-ofit['coef']['did']['b'])<1e-9 and abs(om.bse[0]-ofit['coef']['did']['se'])<1e-9
    # Event-study implementation check against a full dummy design.
    esd=d[d.route.isin(sr)].sort_values(['route','t']);efit=fit(esd,event=True)
    et=sorted(set(esd.t)-{15});ex=np.column_stack([*[esd.treated*(esd.t==t) for t in et],np.ones(len(esd)),pd.get_dummies(esd.route,drop_first=True).to_numpy(),pd.get_dummies(esd.t,drop_first=True).to_numpy()]).astype(float)
    em=sm.OLS(esd.lnfare.to_numpy(),ex).fit(cov_type='cluster',cov_kwds={'groups':esd.route.to_numpy()},use_t=True)
    eb=np.array([efit['coef']['event_'+str(t-16)]['b'] for t in et]);ese=np.array([efit['coef']['event_'+str(t-16)]['se'] for t in et])
    assert np.max(abs(em.params[:len(et)]-eb))<1e-9 and np.max(abs(em.bse[:len(et)]-ese))<1e-9
    results['event_validation']={'max_beta_abs_difference':float(np.max(abs(em.params[:len(et)]-eb))),'max_se_abs_difference':float(np.max(abs(em.bse[:len(et)]-ese)))}
    oe,(_,eg,ey,ex,ec,er)=fit(os,event=True,legacy=True,event_window=(8,24),precomputed_y='lnfare_fullsample_route_demeaned',return_details=True)
    oem=sm.OLS(ey,ex).fit(cov_type='cluster',cov_kwds={'groups':eg})
    ob=np.array([v['b'] for v in oe['coef'].values()]);ose=np.array([v['se'] for v in oe['coef'].values()])
    assert np.max(abs(oem.params[:16]-ob))<1e-9 and np.max(abs(oem.bse[:16]-ose))<1e-9
    results['legacy_event_validation']={'max_beta_abs_difference':float(np.max(abs(oem.params[:16]-ob))),'max_se_abs_difference':float(np.max(abs(oem.bse[:16]-ose)))}
    results['estimator_validation']=verify
    results['legacy_validation']={'beta_abs_difference':float(abs(om.params[0]-ofit['coef']['did']['b'])),'se_abs_difference':float(abs(om.bse[0]-ofit['coef']['did']['se']))}
    save_json(out/'results.json',results);save_json(out/'data_audit.json',audit)
    pd.DataFrame([model_row(k,v) for k,v in results.items() if isinstance(v,dict) and 'coef' in v and 'did' in v['coef']]).to_csv(out/'regression_results.csv',index=False)
    ev=pd.DataFrame([{'rel_time':int(k.split('_')[1]),'t':int(k.split('_')[1])+16,**v} for k,v in results['event']['coef'].items()]).sort_values('rel_time')
    ev.to_csv(out/'event_coefficients.csv',index=False)
    early=pd.DataFrame([{'t':int(k.split('_')[1])+16,**v} for k,v in results['early_pre_event']['coef'].items()])
    early.to_csv(out/'early_pre_event_coefficients.csv',index=False)
    # Honest group descriptive mean of route log fares, not passenger pooled fare.
    trends=d.groupby(['t','treated']).agg(mean_log_fare=('lnfare','mean'),mean_route_fare=('fare','mean'),route_count=('route','size')).reset_index();trends.to_csv(out/'descriptive_trends.csv',index=False)
    make_figures(ev,trends,out)
    print(json.dumps({'original':original['fare'],'main':results['baseline'],'pretrends':results['event']['all_pre'],'early_pre':results['early_pre_event']['all_pre'],'flow':results['sample_flow'],'bridge':bridge},indent=2,default=native),flush=True)

def make_figures(ev,trends,out):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#263747','xtick.color':'#344755','ytick.color':'#344755','savefig.facecolor':'white'})
    fig,ax=plt.subplots(figsize=(6.65,3.5),layout='constrained')
    ax.axhline(0,color='#6f7c85',lw=.8);ax.axvspan(-2.5,.5,color='#e5b35f',alpha=.16,label='Announcement–completion quarters')
    ax.axvline(0,color='#9c5332',ls='--',lw=1)
    ax.errorbar(ev.rel_time,ev.b,yerr=[ev.b-ev.lo,ev.hi-ev.b],fmt='o',color='#1b617b',ecolor='#739baa',markersize=3.6,capsize=2,lw=.8,label='Quarterly relative fare contrast; 95% CI')
    ax.scatter([-1],[0],facecolors='white',edgecolors='#1b617b',s=25,zorder=4,label='Reference: 2008Q3')
    ax.set_xticks([-15,-11,-7,-3,-1,0,4,8],['2005Q1','2006Q1','2007Q1','2008Q1','2008Q3','2008Q4','2009Q4','2010Q4'],rotation=30,ha='right')
    ax.set_ylabel('Difference in log fare relative to 2008Q3');ax.grid(axis='y',alpha=.16);ax.legend(loc='lower left',fontsize=7,frameon=False)
    fig.savefig(out/'event_study.png',dpi=240);fig.savefig(out/'event_study.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.65,3.1),layout='constrained')
    for k,label,color in [(1,'Material overlap','#1b617b'),(0,'Unexposed legacy comparison','#a56340')]:
        z=trends[trends.treated==k];ax.plot(z.t,z.mean_log_fare,color=color,marker='o',ms=3,lw=1.2,label=label)
    ax.axvline(16,color='#6f7c85',ls='--',lw=1);ax.set_xticks([1,5,9,13,17,21,24],['2005Q1','2006Q1','2007Q1','2008Q1','2009Q1','2010Q1','2010Q4'],rotation=20,ha='right');ax.set_ylabel('Mean log route fare');ax.legend(frameon=False);ax.grid(axis='y',alpha=.16)
    fig.savefig(out/'descriptive_trends.png',dpi=240);fig.savefig(out/'descriptive_trends.pdf');plt.close(fig)

if __name__=='__main__':main()
