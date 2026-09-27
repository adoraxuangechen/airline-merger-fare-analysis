"""Read-only comparison of the supplied CSV and NBER's archived Stata market data.

Usage: python verify_source_identity.py --input "INPUT.csv" [--archive "SOURCE.zip"] [--out OUTPUT_DIRECTORY]
The archive is an existing local download; this script does not fetch data.
Both input files and the archive member are read only. Reports are written to --out.
No ticket-level observations are reconstructed here.
"""
from pathlib import Path
from hashlib import sha256
import argparse, csv, json, zipfile, time
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', type=Path, required=True, help='Supplied 2005–2010 aggregate CSV to compare (read only).')
parser.add_argument('--archive', type=Path, default=HERE / 'mktdata79q1to16q3.zip', help='Existing NBER ZIP archive (read only); default: next to this script.')
parser.add_argument('--out', type=Path, default=HERE, help='Output-report directory; default: this script’s directory.')
args = parser.parse_args()
TARGET = args.input.expanduser().resolve()
ARCHIVE = args.archive.expanduser().resolve()
OUT = args.out.expanduser().resolve()
OUT.mkdir(parents=True, exist_ok=True)
RESULT = OUT / 'source_identity_audit.json'
STRINGS = ['cr1','cr2','ap1','ap2']
INTEGER = ['yr','qtr','cop','pax','nsdst']
FLOAT = ['avprc','avdst']

def digest(path):
    h = sha256()
    with path.open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()

def string_values(x):
    return x.fillna('').astype(str).str.strip().to_numpy()

started = time.time()
df = pd.read_csv(TARGET, dtype={k:'string' for k in STRINGS}, keep_default_na=False)
audit = {
    'source_url': 'https://data.nber.org/dot-db1a/mktdata79q1to16q3.zip',
    'source_landing_page': 'https://www.nber.org/research/data/department-transportation-db1adb1b',
    'reference_archive_retrieved_date': '2026-09-21',
    'audit_date_utc': datetime.now(timezone.utc).date().isoformat(),
    'source_archive_path': str(ARCHIVE),
    'target_path': str(TARGET), 'target_bytes': TARGET.stat().st_size,
    'target_sha256': digest(TARGET), 'source_archive_bytes': ARCHIVE.stat().st_size,
    'source_archive_sha256': digest(ARCHIVE),
    'target_rows': len(df),
    'comparison': 'Select 2005 <= yr <= 2010 from source, preserve source row order, compare all 11 fields row-by-row. Read CSV strings without treating literal NA as missing; trim surrounding whitespace. Integer fields exact. Fare and routing-distance tolerance: abs(source-target) <= 1e-8 + 1e-12*abs(target).',
    'source_total_rows_scanned': 0,
    'source_selected_rows': 0,
    'string_integer_mismatches': {k:0 for k in STRINGS+INTEGER},
    'float_exact_mismatches': {k:0 for k in FLOAT},
    'float_tolerance_mismatches': {k:0 for k in FLOAT},
    'float_max_absolute_difference': {k:0.0 for k in FLOAT},
    'unmatched_source_rows': 0,
    'mismatch_examples': [],
    'year_counts': {},
}
with zipfile.ZipFile(ARCHIVE, mode='r') as z:
    audit['archive_members'] = z.namelist()
    member = next(n for n in z.namelist() if n.lower().endswith('.dta'))
    with z.open(member) as fh:
        reader = pd.read_stata(fh, chunksize=250000, convert_categoricals=False)
        offset = 0
        for block in reader:
            audit['source_total_rows_scanned'] += len(block)
            b = block.loc[block.yr.between(2005,2010)].reset_index(drop=True)
            if not len(b): continue
            for yr,n in b.groupby('yr').size().items():
                audit['year_counts'][str(yr)] = audit['year_counts'].get(str(yr),0) + int(n)
            audit['source_selected_rows'] += len(b)
            t = df.iloc[offset:offset+len(b)].reset_index(drop=True)
            offset += len(b)
            if len(t) != len(b):
                audit['unmatched_source_rows'] += len(b)-len(t)
                b = b.iloc[:len(t)]
            for k in STRINGS:
                mismatch = string_values(b[k]) != string_values(t[k])
                audit['string_integer_mismatches'][k] += int(np.count_nonzero(mismatch))
                for loc in np.flatnonzero(mismatch):
                    audit['mismatch_examples'].append({'csv_row_zero_based':int(offset-len(b)+loc),'column':k,'source':str(b.iloc[loc][k]),'target':str(t.iloc[loc][k]),'raw_csv_value':str(t.iloc[loc][k]),'yr':int(b.iloc[loc]['yr']),'qtr':int(b.iloc[loc]['qtr']),'ap1':str(b.iloc[loc]['ap1']),'ap2':str(b.iloc[loc]['ap2']),'pax':int(b.iloc[loc]['pax'])})
            for k in INTEGER:
                audit['string_integer_mismatches'][k] += int(np.count_nonzero(b[k].to_numpy() != t[k].to_numpy()))
            for k in FLOAT:
                left = b[k].to_numpy(dtype=float)
                right = t[k].to_numpy(dtype=float)
                audit['float_exact_mismatches'][k] += int(np.count_nonzero(left != right))
                audit['float_tolerance_mismatches'][k] += int(np.count_nonzero(~np.isclose(left,right,rtol=1e-12,atol=1e-8,equal_nan=True)))
                if len(left): audit['float_max_absolute_difference'][k] = max(audit['float_max_absolute_difference'][k], float(np.nanmax(np.abs(left-right))))
audit['rows_equal'] = audit['source_selected_rows'] == audit['target_rows']
audit['all_values_equal_within_tolerance'] = audit['rows_equal'] and audit['unmatched_source_rows']==0 and not any(audit['string_integer_mismatches'].values()) and not any(audit['float_tolerance_mismatches'].values())
audit['distinct_rows_with_carrier_mismatch'] = len({x['csv_row_zero_based'] for x in audit['mismatch_examples']})
audit['carrier_mismatch_sample_passengers'] = sum(x['pax'] for x in {x['csv_row_zero_based']: x for x in audit['mismatch_examples']}.values())
audit['all_carrier_mismatch_source_values_are_literal_NA'] = all(x['source']=='NA' for x in audit['mismatch_examples'])
audit['all_carrier_mismatch_target_raw_values_are_empty'] = all(x['target']=='' for x in audit['mismatch_examples'])
audit['seconds'] = time.time()-started
RESULT.write_text(json.dumps(audit,indent=2))
if audit['mismatch_examples']:
    with (OUT/'carrier_code_discrepancies.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(audit['mismatch_examples'][0])); writer.writeheader(); writer.writerows(audit['mismatch_examples'])
print(json.dumps(audit,indent=2))
