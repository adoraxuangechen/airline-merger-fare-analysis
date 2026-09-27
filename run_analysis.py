#!/usr/bin/env python3
"""Current entry point; forwards all arguments to analysis/extend_analysis.py."""
import runpy
from pathlib import Path
if __name__=='__main__':
    runpy.run_path(str(Path(__file__).resolve().parent/'analysis/extend_analysis.py'),run_name='__main__')
