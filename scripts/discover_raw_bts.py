"""Retrieve untouched BTS pilot ZIPs and inventory official DB1B archives.

Uses only public BTS endpoints. Never modifies an input archive. The default
download is 2007Q1 Market and Coupon only; other quarters receive HEAD checks.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import io
import json
import re
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "bts_pilot"
BASE = "https://transtats.bts.gov/PREZIP/"
DEST.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "DB1B academic replication provenance audit"}


def request(url, method="GET"):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS, method=method), timeout=90)


def inventory():
    with request(BASE) as response:
        raw = response.read()
    (DEST / "bts_prezip_directory.html").write_bytes(raw)
    text = raw.decode("utf-8", errors="replace")
    entries = []
    for table in ("Market", "Coupon", "Ticket"):
        for year in range(2005, 2011):
            for quarter in range(1, 5):
                filename = f"Origin_and_Destination_Survey_DB1B{table}_{year}_{quarter}.zip"
                pattern = re.compile(r"(\d+)\s+<A HREF=\"([^\"]*" + re.escape(filename) + r")\"", re.I)
                match = pattern.search(text)
                entries.append({"table": table, "year": year, "quarter": quarter,
                                "filename": filename, "url": BASE + filename,
                                "listed_in_official_directory": bool(match),
                                "directory_bytes": int(match[1]) if match else None})
    return entries


def check_head(entry):
    result = dict(entry)
    try:
        with request(entry["url"], "HEAD") as response:
            result["http_status"] = response.status
            result["content_length"] = int(response.headers.get("Content-Length", "0"))
            result["last_modified"] = response.headers.get("Last-Modified")
            result["content_type"] = response.headers.get("Content-Type")
    except Exception as error:
        result["error"] = repr(error)
    return result


def download(entry):
    path = DEST / entry["filename"]
    if not path.exists():
        temporary = path.with_suffix(".zip.partial")
        with request(entry["url"]) as response, temporary.open("wb") as out:
            while block := response.read(1024 * 1024):
                out.write(block)
        temporary.replace(path)
    h = hashlib.sha256()
    with path.open("rb") as inp:
        while block := inp.read(1024 * 1024):
            h.update(block)
    result = dict(entry)
    result.update(local_path=str(path), actual_bytes=path.stat().st_size, sha256=h.hexdigest())
    members = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        result["zip_crc_test"] = "pass" if bad is None else bad
        for member in archive.infolist():
            m = {"name": member.filename, "uncompressed_bytes": member.file_size,
                 "compressed_bytes": member.compress_size, "crc32": f"{member.CRC:08x}"}
            if member.filename.lower().endswith(".csv"):
                with archive.open(member) as inp:
                    reader = csv.reader(io.TextIOWrapper(inp, encoding="utf-8-sig"))
                    m["columns"] = next(reader)
                    m["first_rows"] = [next(reader) for _ in range(3)]
            members.append(m)
    result["members"] = members
    print("Downloaded and checked", entry["filename"], result["actual_bytes"], flush=True)
    return result


def main():
    entries = inventory()
    manifest = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "directory": BASE,
                "entries": entries}
    (DEST / "bts_2005_2010_url_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Inventory", len(entries), "files; found", sum(e["listed_in_official_directory"] for e in entries), flush=True)
    selected = [e for e in entries if (e["year"], e["quarter"]) in ((2005, 1), (2007, 1), (2010, 4))]
    with ThreadPoolExecutor(max_workers=3) as pool:
        heads = list(pool.map(check_head, selected))
    (DEST / "sample_http_metadata.json").write_text(json.dumps(heads, indent=2))
    pilot = [e for e in entries if e["year"] == 2007 and e["quarter"] == 1 and e["table"] in ("Market", "Coupon")]
    estimated_bytes = sum(e["directory_bytes"] or 0 for e in pilot)
    if not all(e["directory_bytes"] for e in pilot) or estimated_bytes >= 400_000_000:
        raise RuntimeError("Pilot size absent or exceeds authorized 400 MB cap")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [future.result() for future in as_completed([pool.submit(download, e) for e in pilot])]
    (DEST / "pilot_download_metadata.json").write_text(json.dumps(results, indent=2))
    print("Pilot metadata written", flush=True)


if __name__ == "__main__":
    main()
