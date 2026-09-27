#!/usr/bin/env python3
"""Descriptive nominal fare levels for the unchanged primary route panel."""
from pathlib import Path
import argparse,hashlib,json,platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repository',type=Path,required=True,help='Repository containing results/panel_legacy_valid.csv')
parser.add_argument('--out',type=Path,required=True,help='Separate output directory')
args=parser.parse_args();source=args.repository/'results/panel_legacy_valid.csv';out=args.out;out.mkdir(parents=True,exist_ok=True)
d=pd.read_csv(source)
required={'route','t','treated','fare','lnfare','pax','revenue'}
assert required.issubset(d.columns)
assert len(d)==6235 and d.route.nunique()==260
assert not d.duplicated(['route','t']).any()
assert set(d.t.unique())==set(range(1,25))
assert d.groupby('route').treated.nunique().eq(1).all()
assert d.groupby('route').treated.first().value_counts().to_dict()=={1:156,0:104}
assert np.isfinite(d[['fare','lnfare','pax','revenue']]).all().all()
assert (d[['fare','pax','revenue']]>0).all().all()
assert np.allclose(d.fare,d.revenue/d.pax,rtol=1e-12,atol=1e-9)
assert np.allclose(d.lnfare,np.log(d.fare),rtol=1e-12,atol=1e-12)
label={1:'Overlap routes',0:'Legacy comparison routes'}
counts=d.groupby('route').t.nunique()
balanced=set(counts[counts.eq(24)].index)
rows=[]
for cohort,dd in [('primary_fixed_260_available_cells',d),('balanced_24_quarters',d[d.route.isin(balanced)])]:
    members=dd.drop_duplicates('route').groupby('treated').size().to_dict()
    for (treated,t),z in dd.groupby(['treated','t'],sort=True):
        rows.append({'cohort':cohort,'treated':int(treated),'group':label[int(treated)],'t':int(t),'year':2005+(int(t)-1)//4,'quarter':1+(int(t)-1)%4,'quarter_label':str(2005+(int(t)-1)//4)+'Q'+str(1+(int(t)-1)%4),'fixed_route_members':int(members[treated]),'observed_route_count':z.route.nunique(),'missing_route_count':int(members[treated]-z.route.nunique()),'passengers':float(z.pax.sum()),'fare_revenue_proxy':float(z.revenue.sum()),'equal_route_mean_fare':float(z.fare.mean()),'pooled_passenger_weighted_fare':float(z.revenue.sum()/z.pax.sum()),'mean_route_log_fare':float(z.lnfare.mean())})
summary=pd.DataFrame(rows)
summary.to_csv(out/'raw_fare_quarterly_means.csv',index=False,float_format='%.17g')
# Phase statistics average quarterly group means, avoiding unequal quarter counts.
annual=summary.groupby(['cohort','treated','group','year'],as_index=False).agg(quarters=('t','size'),equal_route_mean_fare=('equal_route_mean_fare','mean'),mean_of_quarterly_pooled_passenger_weighted_fares=('pooled_passenger_weighted_fare','mean'),min_routes_in_quarter=('observed_route_count','min'),max_routes_in_quarter=('observed_route_count','max'))
annual.to_csv(out/'raw_fare_annual_means.csv',index=False,float_format='%.17g')
missing=[]
for route,z in d.groupby('route'):
    for t in sorted(set(range(1,25))-set(z.t)):
        missing.append({'route':route,'treated':int(z.treated.iloc[0]),'missing_t':int(t),'missing_quarter':str(2005+(t-1)//4)+'Q'+str(1+(t-1)%4)})
pd.DataFrame(missing).to_csv(out/'unobserved_route_quarters.csv',index=False)
# Independently sum source route fares and fare×passengers for six cells.
checks=[]
for treated in [0,1]:
    for t in [1,12,24]:
        z=d[d.treated.eq(treated)&d.t.eq(t)]
        manual_route=sum(float(v) for v in z.fare)/len(z)
        manual_pooled=sum(float(f)*float(p) for f,p in zip(z.fare,z.pax))/sum(float(v) for v in z.pax)
        stored=summary[summary.cohort.eq('primary_fixed_260_available_cells')&summary.treated.eq(treated)&summary.t.eq(t)].iloc[0]
        assert abs(manual_route-stored.equal_route_mean_fare)<1e-10
        assert abs(manual_pooled-stored.pooled_passenger_weighted_fare)<1e-10
        checks.append({'treated':treated,'t':t,'observed_routes':len(z),'equal_route_abs_difference':abs(manual_route-stored.equal_route_mean_fare),'pooled_passenger_abs_difference':abs(manual_pooled-stored.pooled_passenger_weighted_fare)})
primary=summary[summary.cohort.eq('primary_fixed_260_available_cells')]
balanced_table=summary[summary.cohort.eq('balanced_24_quarters')]
joined=primary.merge(balanced_table,on=['treated','t'],suffixes=('_primary','_balanced'))
validation={'source_file':'results/panel_legacy_valid.csv','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_rows':len(d),'primary_routes':d.route.nunique(),'primary_route_counts':{'overlap':156,'legacy_comparison':104},'balanced_route_counts':{'overlap':int(d[d.route.isin(balanced)].drop_duplicates('route').treated.sum()),'legacy_comparison':int((d[d.route.isin(balanced)].drop_duplicates('route').treated==0).sum())},'unobserved_route_quarters':missing,'manual_aggregation_checks':checks,'all_route_fares_equal_revenue_divided_by_passengers':True,'all_saved_log_fares_equal_log_of_saved_fare':True,'maximum_absolute_primary_minus_balanced_quarter_mean_dollars':{label[int(g)]:float(np.max(np.abs(z.equal_route_mean_fare_primary-z.equal_route_mean_fare_balanced))) for g,z in joined.groupby('treated')},'software':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'matplotlib':matplotlib.__version__},'meaning':'Descriptive nominal fare levels. Equal-route arithmetic means are not regression estimates and do not recover the log-DID coefficient.'}
(out/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
font=Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf')
if font.exists():
    font_manager.fontManager.addfont(str(font));family=font_manager.FontProperties(fname=str(font)).get_name()
else:
    family='DejaVu Serif'
plt.rcParams.update({'font.family':family,'font.size':10.5,'axes.labelsize':10.5,'xtick.labelsize':9.5,'ytick.labelsize':10,'legend.fontsize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'pdf.fonttype':42,'ps.fonttype':42,'figure.facecolor':'white','axes.facecolor':'white'})
fig,ax=plt.subplots(figsize=(7.2,3.0),layout='constrained')
ax.axvspan(13.5,16.5,facecolor='#e8d5b7',alpha=.42,zorder=0)
ax.axvline(14,color='#947047',lw=.85,ls=':',zorder=1)
ax.axvline(16,color='#947047',lw=.85,ls='--',zorder=1)
for tr,color in [(1,'#214f78'),(0,'#bb6a2a')]:
    z=primary[primary.treated.eq(tr)].sort_values('t')
    ax.plot(z.t,z.equal_route_mean_fare,color=color,lw=1.85,marker='o',ms=2.7,label=label[tr],zorder=3)
ax.text(13.75,1.017,'Announcement',transform=ax.get_xaxis_transform(),ha='right',va='bottom',fontsize=9,color='#785d3e')
ax.text(16.25,1.017,'Completion',transform=ax.get_xaxis_transform(),ha='left',va='bottom',fontsize=9,color='#785d3e')
ax.set_xlim(.5,24.5)
ax.set_xticks([1,5,9,14,16,20,24],['2005Q1','2006Q1','2007Q1','2008Q2','2008Q4','2009Q4','2010Q4'],rotation=25,ha='right')
ax.set_ylabel('Mean fare (nominal $)')
ax.legend(frameon=False,loc='upper left',ncol=1,handlelength=2.3)
ax.grid(axis='y',color='#d8dcdf',lw=.55,alpha=.7);ax.set_axisbelow(True)
fig.savefig(out/'raw_fare_trends.png',dpi=300,facecolor='white')
fig.savefig(out/'raw_fare_trends.pdf',facecolor='white',metadata={'Title':'Raw quarterly fare levels on the primary fixed route sample','Author':'Xuange (Adora) Chen','Subject':'Descriptive nominal equal-route quarterly mean fares; Borenstein 2005–2010'})
plt.close(fig)
print(annual[annual.cohort.eq('primary_fixed_260_available_cells')].to_string(index=False))
print(json.dumps({'validation_passed':True,'balanced_routes':validation['balanced_route_counts'],'missing_cells':len(missing),'maximum_absolute_primary_minus_balanced_quarter_mean_dollars':validation['maximum_absolute_primary_minus_balanced_quarter_mean_dollars']},indent=2))
