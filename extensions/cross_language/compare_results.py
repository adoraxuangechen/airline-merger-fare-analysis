#!/usr/bin/env python3
"""Compare independent R and Stata estimates with saved Python benchmarks."""
import argparse,csv,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repository',type=Path,required=True)
p.add_argument('--extension-results',type=Path,required=True,help='Directory containing wn_models.json')
p.add_argument('--results',type=Path,default=Path(__file__).resolve().parent/'results')
a=p.parse_args()
def read_csv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
bench=json.loads((a.repository/'results/extended_results.json').read_text())['models']
bench.update(json.loads((a.extension_results/'wn_models.json').read_text()))
expected_models = {'same_sample_unadjusted', 'distance_quarter', 'distance_and_composition_quarter', 'all_controls_adjusted', 'legacy_adjusted_wn_present', 'expanded_adjusted_wn_present'}
rows=[]
for lang,filename in [('R','r_model_results.csv'),('Stata','stata_model_results.csv')]:
    estimates = read_csv(a.results/filename)
    assert len(estimates) == 6 and {r['model'] for r in estimates} == expected_models, f'{lang}: expected six distinct prescribed models'
    for row in estimates:
        ref=bench[row['model']];target=ref['coef']['did'];rank=ref['N']-ref['df_resid']
        z={'model':row['model'],'language':lang,'N':int(float(row['N'])),'routes':int(float(row['routes'])),'rank':int(float(row['rank'])),'df_resid':int(float(row['df_resid'])),'b':float(row['b']),'se':float(row['se']),'python_b':target['b'],'python_se':target['se']}
        z['abs_beta_difference']=abs(z['b']-z['python_b']);z['abs_se_difference']=abs(z['se']-z['python_se'])
        z['sample_and_rank_equal']=z['N']==ref['N'] and z['routes']==ref['routes'] and z['rank']==rank and z['df_resid']==ref['df_resid']
        z['pass']=z['sample_and_rank_equal'] and z['abs_beta_difference']<1e-9 and z['abs_se_difference']<1e-9
        rows.append(z)
with (a.results/'cross_language_comparison.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
assert len(rows)==12 and all(z['pass'] for z in rows), 'Cross-language regression verification failed; inspect the complete comparison.'
version=(a.results/'stata_version.txt').read_text().strip().splitlines()
summary={'status':'passed','regressions_per_language':6,'languages_compared':['Python (existing estimates)','R (independent explicit-dummy OLS)','Stata (independent regress with clustered VCE)'],'max_abs_beta_difference':max(z['abs_beta_difference'] for z in rows),'max_abs_se_difference':max(z['abs_se_difference'] for z in rows),'all_sample_counts_and_design_ranks_equal':all(z['sample_and_rank_equal'] for z in rows),'tolerance':{'coefficient_absolute':1e-9,'standard_error_absolute':1e-9},'stata_version_information':version,'r_version':(a.results/'r_session_info.txt').read_text().splitlines()[0],'input_sha256':{name:digest(a.repository/'results'/name) for name in ['panel_legacy_valid.csv','panel_all_unexposed.csv','route_features.csv']},'benchmark_sha256':{'extended_results.json':digest(a.repository/'results/extended_results.json'),'wn_models.json':digest(a.extension_results/'wn_models.json')},'scope':'Regression replication on the same already constructed panels. Does not independently recreate raw-data cleaning or establish causal identification.'}
(a.results/'validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
