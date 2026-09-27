"""Inspect requested 2005Q1/2007Q1/2010Q4 ZIP schemas without full downloads.

Fully downloaded archives are read locally. For other tables, public HTTP byte
ranges retrieve only ZIP metadata and enough compressed CSV data for the header.
Remote-only inspection is explicitly not a whole-file CRC/hash verification.
"""
from pathlib import Path
import csv
import io
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "bts_pilot"
MARKET = ROOT / "data" / "bts_market"


class RemoteZip(io.RawIOBase):
    def __init__(self, url, size):
        self.url, self.size, self.pos, self.transferred = url, size, 0, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        self.pos = offset if whence == io.SEEK_SET else self.pos + offset if whence == io.SEEK_CUR else self.size + offset
        return self.pos

    def read(self, count=-1):
        if count < 0:
            count = self.size - self.pos
        count = min(count, self.size - self.pos)
        if count <= 0:
            return b""
        if count > 1024 * 1024:
            raise ValueError("Unexpectedly large metadata range request")
        request = urllib.request.Request(self.url, headers={"Range":f"bytes={self.pos}-{self.pos+count-1}"})
        with urllib.request.urlopen(request, timeout=45) as response:
            if response.status != 206:
                raise RuntimeError("Server did not honor byte range; no full download attempted")
            data = response.read(count)
        self.pos += len(data)
        self.transferred += len(data)
        return data


def main():
    source = json.loads((PILOT / "sample_http_metadata.json").read_text())
    results = []
    for entry in source:
        local = next((p for p in (PILOT/entry["filename"], MARKET/entry["filename"]) if p.exists()), None)
        result = {"table":entry["table"], "year":entry["year"], "quarter":entry["quarter"],
                  "url":entry["url"], "zip_bytes":entry["content_length"],
                  "verification": "local complete archive" if local else "remote ZIP metadata and header ranges only"}
        remote = None
        try:
            if local:
                archive = zipfile.ZipFile(local)
            else:
                remote = RemoteZip(entry["url"], entry["content_length"])
                archive = zipfile.ZipFile(remote)
            with archive:
                result["members"] = []
                for member in archive.infolist():
                    m = {"name":member.filename, "uncompressed_bytes":member.file_size,
                         "compressed_bytes":member.compress_size, "crc32_in_directory":f"{member.CRC:08x}"}
                    if member.filename.lower().endswith(".csv"):
                        with archive.open(member) as inp:
                            reader = csv.reader(io.TextIOWrapper(inp, encoding="utf-8-sig"))
                            m["columns"] = next(reader)
                    result["members"].append(m)
            if remote:
                result["http_range_bytes_received"] = remote.transferred
        except Exception as error:
            result["error"] = repr(error)
        results.append(result)
        print(entry["filename"], result.get("error", result["verification"]), flush=True)
    (PILOT / "requested_sample_schemas.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
