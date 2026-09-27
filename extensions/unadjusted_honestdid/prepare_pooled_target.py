#!/usr/bin/env python3
"""Import independently audited FWL weights; keep their signs and original scale."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--audit-directory',type=Path,default=ROOT.parent/'pooled_weight_audit')
audit_dir=parser.parse_args().audit_directory.resolve()
summary=json.loads((audit_dir/'audit_summary.json').read_text())
meta=json.loads((ROOT/'event_export_metadata.json').read_text())
assert summary['source_panel_sha256']==meta['source_panel_sha256']
events=pd.read_csv(ROOT/'event_coefficients_full.csv')
cov=pd.read_csv(ROOT/'event_covariance.csv',index_col=0).to_numpy()
independent_cov=pd.read_csv(audit_dir/'independent_event_covariance.csv',index_col=0)
assert list(independent_cov.index)==events.quarter.tolist()
assert list(independent_cov.columns)==events.quarter.tolist()
max_cov_difference=float(np.abs(cov-independent_cov.to_numpy()).max())
assert max_cov_difference<1e-10
beta=events.beta.to_numpy();a=np.array(summary['full_weights']);l=np.array(summary['post_weights_l_vec'])
assert len(l)==12 and len(a)==23
assert np.max(np.abs(a[11:]-l))<1e-14
pooled_reconstructed=float(a@beta)
assert abs(pooled_reconstructed-summary['pooled_beta_log'])<1e-10
assert abs(pooled_reconstructed-meta['pooled_contrast_b'])<1e-10
point=float(l@beta[11:]);se=float(np.sqrt(l@cov[11:,11:]@l))
pre_contribution=float(a[:11]@beta[:11])
ci=[point-1.959963984540054*se,point+1.959963984540054*se]
weights=pd.read_csv(audit_dir/'post_target_weights.csv').rename(columns={'weight_a':'weight'})
assert weights.quarter.tolist()==events.quarter.tolist()[11:]
assert np.max(np.abs(weights.weight.to_numpy()-l))<1e-14
(ROOT/'pooled_target_weights.csv').write_text((audit_dir/'post_target_weights.csv').read_text().replace('weight_a','weight',1))
ref08q3=float(events.loc[events.t.eq(15),'beta'].iloc[0])
out={'source_panel_sha256':meta['source_panel_sha256'],
     'source_weights_sha256':hashlib.sha256((audit_dir/'post_target_weights.csv').read_bytes()).hexdigest(),
     'source_weight_audit_sha256':hashlib.sha256((audit_dir/'audit_summary.json').read_bytes()).hexdigest(),
     'independent_covariance_max_abs_difference':max_cov_difference,
     'reference':'2007Q4','allowed_effect_window':'2008Q1–2010Q4',
     'no_effect_assumption':'Effects are zero before 2008Q1.',
     'l_vec':l.tolist(),'sum_early_three_weights':float(l[:3].sum()),'sum_completion_nine_weights':float(l[3:].sum()),'sum_weights':float(l.sum()),
     'full_pooled_log_coefficient':pooled_reconstructed,'full_pooled_percent':float(100*np.expm1(pooled_reconstructed)),
     'pre_period_nuisance_contribution_log':pre_contribution,
     'pooled_associated_target_b':point,'pooled_associated_target_se':se,
     'pooled_associated_target_percent':float(100*np.expm1(point)),
     'normal95_log':ci,'normal95_percent':[float(100*np.expm1(x)) for x in ci],
     'exact_bridge_error':pooled_reconstructed-(pre_contribution+point),
     'nine_quarter_reference_rebase':{'2007Q4_target_log':meta['target_b'],'2007Q4_target_percent':float(100*np.expm1(meta['target_b'])),
          '2008Q3_reference_event_coefficient':ref08q3,'2008Q3_rebased_target_log':meta['target_b']-ref08q3,
          '2008Q3_rebased_target_percent':float(100*np.expm1(meta['target_b']-ref08q3)),
          'interpretation':'This is a descriptive normalization comparison, not a second HonestDiD run. Changing the unaffected reference assumptions would change the sensitivity exercise.'},
     'interpretation':'a_post prime tau_post is the causal functional associated with the pooled projection under zero effects before 2008Q1. It preserves negative 2008Q1–Q3 weights. Its a_post prime b_post plug-in estimate is not the original pooled coefficient and is not a simple post-completion average. No pre-period recentering or manual confidence-set shifting is performed.'}
(ROOT/'pooled_target_metadata.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
