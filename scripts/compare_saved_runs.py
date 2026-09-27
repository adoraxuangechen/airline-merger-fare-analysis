"""Compare every saved model from two complete analysis runs."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    a = json.loads(args.reference.read_text())
    b = json.loads(args.candidate.read_text())
    differences = []

    def compare(x, y, path):
        if isinstance(x, dict):
            assert isinstance(y, dict) and set(x) == set(y), path
            for key in x:
                compare(x[key], y[key], f'{path}.{key}')
        elif isinstance(x, list):
            assert isinstance(y, list) and len(x) == len(y), path
            for i, (xx, yy) in enumerate(zip(x, y)):
                compare(xx, yy, f'{path}.{i}')
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            if math.isnan(x) and math.isnan(y):
                return
            assert math.isclose(x, y, rel_tol=1e-10, abs_tol=1e-10), (path, x, y)
            differences.append((abs(x-y), path))
        else:
            assert x == y, (path, x, y)

    compare(a['models'], b['models'], 'models')
    maximum, field = max(differences)
    report = {
        'status': 'passed',
        'scope': 'All model fields, including coefficients, uncertainty, sample counts, and pre-period tests',
        'reference_sha256': hashlib.sha256(args.reference.read_bytes()).hexdigest(),
        'candidate_sha256': hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        'models_compared': len(a['models']),
        'numeric_fields_compared': len(differences),
        'maximum_absolute_difference': maximum,
        'field_at_maximum': field,
        'absolute_tolerance': 1e-10,
        'relative_tolerance': 1e-10,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
