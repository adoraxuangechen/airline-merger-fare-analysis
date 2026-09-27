"""Download 24 untouched DB1B Market ZIPs with two concurrent connections.

Reuses the completed 2007Q1 pilot via a hard link, adds 2007Q1 Ticket, validates
length, ZIP CRC, and SHA256. Reruns skip complete downloads and resume partials.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import shutil
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "bts_pilot"
DEST = ROOT / "data" / "bts_market"
DEST.mkdir(parents=True, exist_ok=True)
MIN_FREE = 8 * 1024 ** 3


def fetch(entry):
    destination = PILOT if entry["table"] == "Ticket" else DEST
    path = destination / entry["filename"]
    prior = PILOT / entry["filename"]
    if not path.exists() and prior.exists() and path != prior:
        os.link(prior, path)
    expected = entry["directory_bytes"]
    metadata_path = path.with_suffix(".metadata.json")
    if path.exists() and path.stat().st_size == expected and metadata_path.exists():
        return json.loads(metadata_path.read_text())
    if not path.exists():
        temporary = path.with_suffix(".zip.partial")
        for attempt in range(3):
            try:
                if shutil.disk_usage(destination).free < MIN_FREE:
                    raise RuntimeError("Stopped: less than 8 GiB free disk space")
                already = temporary.stat().st_size if temporary.exists() else 0
                headers = {"User-Agent": "DB1B academic replication provenance audit"}
                if already:
                    headers["Range"] = f"bytes={already}-"
                request = urllib.request.Request(entry["url"], headers=headers)
                with urllib.request.urlopen(request, timeout=120) as response:
                    mode = "ab" if already and response.status == 206 else "wb"
                    http_info = {"last_modified": response.headers.get("Last-Modified"),
                                 "etag": response.headers.get("ETag"), "final_url": response.url}
                    with temporary.open(mode) as out:
                        while block := response.read(1024 * 1024):
                            out.write(block)
                if temporary.stat().st_size != expected:
                    raise RuntimeError(f"Byte count mismatch: {temporary.stat().st_size} != {expected}")
                temporary.replace(path)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)
    else:
        http_info = {"reused_existing_file": True}
    digest = hashlib.sha256()
    with path.open("rb") as inp:
        while block := inp.read(1024 * 1024):
            digest.update(block)
    result = dict(entry, **http_info, actual_bytes=path.stat().st_size,
                  sha256=digest.hexdigest(), local_path=str(path),
                  verified_utc=datetime.now(timezone.utc).isoformat())
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"CRC check failed for {bad}")
        result["zip_crc_test"] = "pass"
        result["members"] = []
        for member in archive.infolist():
            m = {"name": member.filename, "uncompressed_bytes": member.file_size,
                 "compressed_bytes": member.compress_size, "crc32": f"{member.CRC:08x}"}
            if member.filename.lower().endswith(".csv"):
                with archive.open(member) as inp:
                    rows = csv.reader(io.TextIOWrapper(inp, encoding="utf-8-sig"))
                    m["columns"] = next(rows)
                    m["first_row"] = next(rows)
            result["members"].append(m)
    metadata_path.write_text(json.dumps(result, indent=2))
    print("Verified", entry["filename"], result["actual_bytes"], flush=True)
    return result


def main():
    free = shutil.disk_usage(DEST).free
    if free < MIN_FREE:
        raise RuntimeError("Less than 8 GiB free; downloads not started")
    source = json.loads((PILOT / "bts_2005_2010_url_manifest.json").read_text())
    entries = [e for e in source["entries"] if e["table"] == "Market" or
               (e["table"] == "Ticket" and e["year"] == 2007 and e["quarter"] == 1)]
    # Put the small Ticket pilot first, then existing Market pilot, then all other quarters.
    entries.sort(key=lambda e: (0 if e["table"] == "Ticket" else 1 if (e["year"],e["quarter"]) == (2007,1) else 2,
                                e["year"], e["quarter"]))
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "free_bytes_before": free, "expected_downloaded_market_files": 24,
              "expected_bytes_all_selected_archives": sum(e["directory_bytes"] for e in entries),
              "completed": [], "errors": []}
    manifest = DEST / "download_manifest.json"
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = {pool.submit(fetch, e): e for e in entries}
        for future in as_completed(jobs):
            try:
                report["completed"].append(future.result())
            except Exception as error:
                report["errors"].append({"entry":jobs[future], "error":repr(error)})
                print("Download failed", jobs[future]["filename"], repr(error), flush=True)
            manifest.write_text(json.dumps(report, indent=2))
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["free_bytes_after"] = shutil.disk_usage(DEST).free
    report["all_selected_files_verified"] = len(report["completed"]) == len(entries) and not report["errors"]
    manifest.write_text(json.dumps(report, indent=2))
    print("Finished", len(report["completed"]), "verified; errors", len(report["errors"]), flush=True)


if __name__ == "__main__":
    main()
