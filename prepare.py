import os
from pathlib import Path
import pandas as pd,numpy as np,json
R=Path(__file__).resolve().parent
x=pd.read_csv(Path(os.environ.get('AIRLINE_INPUT_PATH',R.parent/'upload/DB1B_2005_2010 copy.csv')),dtype={k:'category' for k in ['cr1','cr2','ap1','ap2']})
raw_n=len(x)
a=x.ap1.astype(str);b=x.ap2.astype(str)
x=x[(a!=b)&(x.pax>0)&(x.avprc>0)&x.avprc.notna()].copy()
x['route']=x.ap1.astype(str)+'-'+x.ap2.astype(str);x['t']=(x.yr-2005)*4+x.qtr-1
x['revenue']=x.pax*x.avprc;x['fare2']=x.pax*x.avprc**2
c1=x.cr1.astype(str);c2=x.cr2.astype(str)
single=(x.cop==0)|(c1==c2)
for code in ['DL','NW']:
 x[code+'_pax']=np.where(single&(c1==code),x.pax,0)
 x[code+'_any']=np.where((c1==code)|(c2==code),x.pax,0)
 x[code+'_direct']=np.where((x.cop==0)&(c1==code),x.pax,0)
x['legacy_pax']=np.where(single&c1.isin(['AA','AS','CO','UA','US','HP']),x.pax,0)
x['direct_pax']=np.where(x.cop==0,x.pax,0)
panel=x.groupby(['route','t'],observed=True).agg(pax=('pax','sum'),revenue=('revenue','sum'),fare2=('fare2','sum'),records=('pax','size'),dl=('DL_pax','sum'),nw=('NW_pax','sum'),dl_any=('DL_any','sum'),nw_any=('NW_any','sum'),dl_direct=('DL_direct','sum'),nw_direct=('NW_direct','sum'),legacy=('legacy_pax','sum'),direct_pax=('direct_pax','sum'),distance=('nsdst','max')).reset_index()
panel['fare']=panel.revenue/panel.pax;panel['lnfare']=np.log(panel.fare);panel['between_sd']=np.sqrt(np.maximum(panel.fare2/panel.pax-panel.fare**2,0));panel['direct_share']=panel.direct_pax/panel.pax
for code in ['dl','nw','legacy']:
 panel[code+'_active']=(panel[code]/panel.pax>=.05).astype(int)
panel['both_active']=((panel.dl_active==1)&(panel.nw_active==1)).astype(int)
pre=panel[panel.t.between(8,11)]
c=pre.groupby('route').agg(nq=('t','size'),pax_min=('pax','min'),pax_pre=('pax','mean'),fare_pre=('fare','mean'),dl_q=('dl_active','sum'),nw_q=('nw_active','sum'),both_q=('both_active','sum'),legacy_q=('legacy_active','sum'),dl_any=('dl_any','sum'),nw_any=('nw_any','sum'),direct=('direct_share','mean'),distance=('distance','mean'),dl_direct=('dl_direct','sum'),nw_direct=('nw_direct','sum'))
c['group']=np.select([c.both_q>=3,(c.dl_any==0)&(c.nw_any==0)&(c.legacy_q>=3)],['overlap','unexposed_legacy'],default='other')
c['direct_overlap']=(c.dl_direct>=100)&(c.nw_direct>=100)
c.to_csv(R/'classification.csv')
panel.to_pickle(R/'panel.pkl')
stats={'raw_rows':raw_n,'valid_rows':len(x),'route_quarters':len(panel),'routes':panel.route.nunique(),'pax_sum':int(x.pax.sum()),'quarter_count':int(panel.t.nunique()),'overall_groups':c.group.value_counts().to_dict(),'eligible_groups':c.loc[(c.nq==4)&(c.pax_min>=100),'group'].value_counts().to_dict(),'direct_overlap_count':int(c.direct_overlap.sum()),'group_characteristics':c.groupby('group')[['pax_pre','fare_pre','direct','distance']].median().to_dict(),'row_filter_count':raw_n-len(x),'unknown_c1_rows':int(x.cr1.isna().sum()),'airport_pair_count_perquarter':panel.groupby('t').size().to_dict()}
(R/'preparation.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
