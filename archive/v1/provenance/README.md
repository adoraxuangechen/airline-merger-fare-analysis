# Independent source-archive comparison

This optional check compares the original 2005–2010 aggregate CSV with the same years in NBER's public Borenstein Stata archive. It reads both inputs without altering them. It does not reconstruct individual DB1B tickets or independently repeat upstream ticket screening.

## Rerun

First obtain the project CSV with `python scripts/download_and_verify.py`. Download the larger [NBER source archive](https://data.nber.org/dot-db1a/mktdata79q1to16q3.zip) separately and then run, from the repository root:

```sh
python provenance/verify_source_identity.py --input "data/DB1B_2005_2010 copy.csv" --archive "/path/to/mktdata79q1to16q3.zip" --out provenance_recheck
```

The source ZIP is 211,893,337 bytes and is not mirrored here. Its expected SHA256 is `75b2fe06890bf54f3466824e0309e3d52a74c3dfc3b22f940000face130ecfa9`. The comparison uses NumPy and pandas from the root requirements. `--help` displays all options without loading data. A fresh output directory retains the committed audit alongside a rerun.

## What was checked

The script selects 2005–2010, preserves source row order and compares all 11 fields. It reads carrier strings without interpreting the literal string `NA` as missing. Integer fields must agree exactly. Fare and average-distance values use absolute tolerance 10⁻⁸ and relative tolerance 10⁻¹²; the report also records the much smaller observed maximum differences.

The completed audit found 4,175,354 aligned records. Airport and integer fields match exactly; numerical serialization differences do not exceed 5.01 × 10⁻¹². Forty-two source carrier entries containing `NA` are blank in the project CSV, across 34 records. Consequently, `all_values_equal_within_tolerance` is **false**; the files are not described as identical. No carrier values were restored for the main analysis.

- `source_identity_audit.json`: sizes, fingerprints, row counts, comparisons and maximum observed errors.
- `carrier_code_discrepancies.csv`: every differing string entry.
- `verify_source_identity.py`: complete comparison implementation.
- `primary_sources.json`: source definitions, merger chronology and other primary references.

The committed audit's original machine-specific input path has been replaced by a repository-relative path; its numerical findings are unchanged and this presentation change is recorded in the JSON. A rerun records the paths supplied by that user. The source archive used in the completed check was retrieved on 21 September 2026; the script separates that historical reference date from a rerun's audit date.
