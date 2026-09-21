#!/usr/bin/env python3
"""Download, verify and unpack the byte-preserving original CSV from GitHub Releases.

Uses only Python's standard library. Existing matching output is left unchanged;
an existing different file is never overwritten. Run from any directory.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            checksum.update(block)
    return checksum.hexdigest()


def main() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Destination CSV; defaults to the original filename in data/.")
    args = parser.parse_args()
    metadata = json.loads((data_dir / "metadata.json").read_text())
    archive = data_dir / metadata["archive_name"]
    output = args.out or data_dir / metadata["original_filename"]
    expected = metadata["original_sha256"]
    if not archive.exists():
        temporary_archive: Path | None = None
        try:
            print(f"Downloading original CSV archive ({metadata['archive_bytes']:,} bytes)...")
            with tempfile.NamedTemporaryFile(mode="wb", dir=data_dir, prefix=".db1b-download-", delete=False) as dest:
                temporary_archive = Path(dest.name)
                request = urllib.request.Request(metadata["archive_url"], headers={"User-Agent": "delta-northwest-replication"})
                with urllib.request.urlopen(request, timeout=120) as source:
                    while block := source.read(1024 * 1024):
                        dest.write(block)
            if temporary_archive.stat().st_size != metadata["archive_bytes"] or sha256(temporary_archive) != metadata["archive_sha256"]:
                raise SystemExit("Downloaded archive checksum or size mismatch; temporary file removed.")
            archive.hardlink_to(temporary_archive)
        finally:
            if temporary_archive is not None:
                temporary_archive.unlink(missing_ok=True)
    if sha256(archive) != metadata["archive_sha256"]:
        raise SystemExit("Archive checksum mismatch: download the original archive again.")
    if output.exists():
        if output.stat().st_size == metadata["original_bytes"] and sha256(output) == expected:
            print(f"Verified existing CSV: {output}\nSHA256: {expected}")
            return
        raise SystemExit(f"Destination exists with different bytes; choose another --out path: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        checksum = hashlib.sha256()
        size = 0
        with tempfile.NamedTemporaryFile(mode="wb", dir=output.parent, prefix=".db1b-unpack-", delete=False) as dest:
            temporary = Path(dest.name)
            with gzip.open(archive, "rb") as source:
                while block := source.read(1024 * 1024):
                    dest.write(block)
                    checksum.update(block)
                    size += len(block)
        if size != metadata["original_bytes"] or checksum.hexdigest() != expected:
            raise SystemExit("Unpacked CSV checksum or size mismatch; the temporary file will be removed.")
        # A hard link fails rather than replacing a destination created meanwhile.
        output.hardlink_to(temporary)
        print(f"Verified and extracted CSV: {output}\nRows: {metadata['rows']:,}\nSHA256: {expected}")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
