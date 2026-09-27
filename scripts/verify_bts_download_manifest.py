"""Verify completed Market download coverage and headers from saved metadata."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "bts_market"
report = json.loads((DEST / "download_manifest.json").read_text())
market = [row for row in report["completed"] if row["table"] == "Market"]
expected = {(year, quarter) for year in range(2005, 2011) for quarter in range(1,5)}
actual = {(row["year"], row["quarter"]) for row in market}
schemas = set()
issues = []
for row in market:
    path = Path(row["local_path"])
    if not path.exists() or path.stat().st_size != row["directory_bytes"]:
        issues.append({"filename":row["filename"], "issue":"local byte count"})
    if row["zip_crc_test"] != "pass":
        issues.append({"filename":row["filename"], "issue":"CRC"})
    for member in row["members"]:
        if "columns" not in member:
            continue
        schema = tuple(c for c in member["columns"] if c)
        schemas.add(schema)
        first = dict(zip(member["columns"], member["first_row"]))
        if (int(first["Year"]), int(first["Quarter"])) != (row["year"],row["quarter"]):
            issues.append({"filename":row["filename"], "issue":"first-row date differs"})
summary = {"expected_quarters":24, "completed_market_files":len(market),
           "missing_quarters":sorted(expected-actual), "unexpected_quarters":sorted(actual-expected),
           "unique_named_schemas":len(schemas), "named_column_counts":[len(s) for s in schemas],
           "total_compressed_bytes":sum(row["actual_bytes"] for row in market),
           "total_uncompressed_csv_bytes":sum(m["uncompressed_bytes"] for row in market for m in row["members"] if "columns" in m),
           "issues":issues, "download_errors":report["errors"],
           "all_checks_pass":len(market)==24 and actual==expected and not issues and not report["errors"] and len(schemas)==1}
(DEST / "verification_summary.json").write_text(json.dumps(summary, indent=2))
(DEST / "SHA256SUMS.txt").write_text("".join(row["sha256"]+"  "+row["filename"]+"\n" for row in sorted(market,key=lambda r:(r["year"],r["quarter"]))))
print(json.dumps(summary, indent=2))
if not summary["all_checks_pass"]:
    raise SystemExit(1)
