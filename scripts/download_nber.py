#!/usr/bin/env python3
"""Download the documented NBER aggregate source and extract2005–2010.

The input archive and original CSV are never overwritten. Literal carrier NA
is retained. This does not download or reconstruct BTS raw ticket records.
"""
import argparse,gzip,hashlib,io,json,os,urllib.request,zipfile
from pathlib import Path
import pandas as pd

URL='https://data.nber.org/dot-db1a/mktdata79q1to16q3.zip'
SHA='75b2fe06890bf54f3466824e0309e3d52a74c3dfc3b22f940000face130ecfa9'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--archive',type=Path,default=Path('data/mktdata79q1to16q3.zip'))
    a.add_argument('--out',type=Path,default=Path('data/NBER_2005_2010.csv.gz'))
    args=a.parse_args();args.archive.parent.mkdir(parents=True,exist_ok=True);args.out.parent.mkdir(parents=True,exist_ok=True)
    if not args.archive.exists():
        temp=args.archive.with_suffix('.download')
        request=urllib.request.Request(URL,headers={'User-Agent':'Academic research data replication'})
        try:
            with urllib.request.urlopen(request,timeout=90) as response,temp.open('wb') as f:
                for block in iter(lambda:response.read(1024*1024),b''):f.write(block)
            assert digest(temp)==SHA,'Archive checksum differs; inspect upstream revision before use.'
            os.replace(temp,args.archive)
        finally:
            if temp.exists():temp.unlink()
    assert digest(args.archive)==SHA,'Existing archive has unexpected checksum.'
    if args.out.exists():raise FileExistsError(f'Output exists; keep it or choose --out: {args.out}')
    count=0;first=True;temp=args.out.with_suffix('.partial')
    try:
        with zipfile.ZipFile(args.archive) as z,temp.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8',newline='') as writer:
            with z.open('mktdata79q1to16q3.dta') as f:
                for block in pd.read_stata(f,chunksize=250000,convert_categoricals=False):
                    b=block.loc[block.yr.between(2005,2010)].copy()
                    if b.empty:continue
                    # Stata float32 values need promotion before text export:
                    # pandas' shortest float32 formatting otherwise changes
                    # the value when the CSV is reread as float64.
                    floating=b.select_dtypes(include=['floating']).columns
                    b[floating]=b[floating].astype('float64')
                    b.to_csv(writer,index=False,header=first,float_format='%.17g');first=False;count+=len(b)
        assert count==4175354
        os.replace(temp,args.out)
    finally:
        if temp.exists():temp.unlink()
    metadata={'source_url':URL,'source_sha256':SHA,'archive_bytes':args.archive.stat().st_size,
              'extracted_file':args.out.name,'extracted_sha256':digest(args.out),'rows':count,'years':[2005,2010],
              'unit':'Borenstein operating-carrier-set / unordered airport-pair / quarter / coupon-category aggregate',
              'literal_NA_carrier_code_preserved':True,'raw_BTS_tickets':False}
    args.out.with_suffix('.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata,indent=2))

if __name__=='__main__':main()
