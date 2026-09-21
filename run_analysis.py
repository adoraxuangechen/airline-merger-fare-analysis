from pathlib import Path
import argparse,os,sys,subprocess,hashlib
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);args=parser.parse_args()
p=Path(args.input).resolve()
if not p.is_file():raise FileNotFoundError(p)
print('Input SHA256:',hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
env=os.environ.copy();env['AIRLINE_INPUT_PATH']=str(p);env.setdefault('OPENBLAS_NUM_THREADS','2')
for script in ['inspect_data.py','prepare.py','estimate.py','check_scope.py','check_full_panel.py','make_figures.py']:
 subprocess.run([sys.executable,str(R/script)],cwd=R,env=env,check=True)
