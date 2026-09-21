"""Convenience entry point for the current verified analysis pipeline."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "analysis" / "run_analysis.py"), run_name="__main__")
