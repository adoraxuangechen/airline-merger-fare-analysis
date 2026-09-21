import os
from pathlib import Path
import pandas as pd,json,hashlib
root=Path(__file__).resolve().parent
path=Path(os.environ.get('AIRLINE_INPUT_PATH',root.parent/'upload/DB1B_2005_2010 copy.csv'))
df=pd.read_csv(path,dtype={k:'category' for k in ['cr1','cr2','ap1','ap2']})
r={'rows':len(df),'columns':list(df),'missing':df.isna().sum().to_dict(),'year_counts':df.groupby('yr').size().to_dict(),'cop_counts':df.groupby('cop').size().to_dict(),'carriers1':df.cr1.value_counts().to_dict(),'carriers2':df.cr2.value_counts().to_dict(),'numeric':df[['pax','avprc','nsdst','avdst']].describe(percentiles=[.01,.5,.99]).to_dict(),'duplicate_keys':int(df.duplicated(['cr1','cr2','yr','qtr','cop','ap1','ap2']).sum()),'ap1_lt_ap2_fraction':float((df.ap1.astype(str)<df.ap2.astype(str)).mean()),'same_carrier_fraction':float((df.cr1.astype(str)==df.cr2.astype(str)).mean()),'cop0_cr2':df.loc[df.cop==0,'cr2'].value_counts().to_dict(),'hash':hashlib.sha256(path.read_bytes()).hexdigest()}
(root/'data_audit.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
