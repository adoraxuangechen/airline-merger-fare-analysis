# Original data input

[Download `DB1B_2005_2010.csv.gz` from GitHub Releases](https://github.com/adoraxuangechen/airline-merger-fare-analysis/releases/download/writing-sample-2026-09/DB1B_2005_2010.csv.gz).

This is a gzip-compressed, byte-preserving copy of the original project CSV. It is an aggregate extract from **Severin Borenstein's Market Data files**, hosted by NBER, ultimately constructed from U.S. Department of Transportation DB1A/DB1B survey records. It is not the raw BTS ticket files. The original bytes are kept unchanged, including the known carrier-code export discrepancy documented below.

| Item | Value |
|---|---|
| Original filename | `DB1B_2005_2010 copy.csv` |
| Original size | 200,700,593 bytes |
| Archive size | 52,692,660 bytes (50.25 MiB) |
| Rows / fields | 4,175,354 / 11 |
| Coverage | 2005Q1–2010Q4 |
| Original SHA256 | `68822d60114c61af9f6ce8d9084aa20276f0d5b1b64a9a80b0e372929f1d19cb` |
| Archive SHA256 | `53223ba01b441d6ecbf74fbe995da2dedb272f3a1b27adc158d69ee6ab6c795a` |

Run `python scripts/download_and_verify.py` from the repository root. It downloads the archive if absent, checks its SHA256, extracts the original filename, and verifies the original SHA256 and byte count. It never overwrites an existing different CSV. The archive and extracted CSV are ignored by Git because the full archive is distributed through the release.

## Fields

| Field | Meaning |
|---|---|
| `cr1`, `cr2` | Operating-carrier identifiers; alphabetical carrier order, not flight sequence |
| `yr`, `qtr` | Year and quarter |
| `cop` | 0: one coupon; 1: two coupons |
| `ap1`, `ap2` | Unordered airport endpoints, stored alphabetically |
| `pax` | Sampled passenger count in the aggregate cell |
| `avprc` | Mean one-way-equivalent fare in nominal dollars; do not divide by two again |
| `nsdst` | Endpoint nonstop distance; zero values are source sentinels, not evidence of zero physical distance |
| `avdst` | Average routing distance |

A one-coupon cell does not independently confirm regularly scheduled nonstop service. The second carrier is structurally blank for one-coupon records. Do not drop every row with any blank field: doing so would remove the one-coupon records.

## Attribution and source audit

Please cite **Severin Borenstein, Market Data files; NBER, Department of Transportation DB1A/DB1B, DOI [10.60592/tb1p-9p78](https://doi.org/10.60592/tb1p-9p78)**, together with this analysis when using its derived results.

- [Borenstein's definitions](https://faculty.haas.berkeley.edu/borenste/mktdata.htm)
- [NBER landing page](https://www.nber.org/research/data/department-transportation-db1adb1b)
- [NBER full source archive](https://data.nber.org/dot-db1a/mktdata79q1to16q3.zip)
- [BTS survey profile](https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFI&Yv0x=D)

The comparison with the NBER archive selects the same years and preserves row order. All integer and airport fields match exactly; maximum differences in fare and average-distance fields are approximately 5.00 × 10⁻¹². However, **42 literal carrier-code `NA` entries in the source archive became blank during creation of the supplied CSV**, across 34 rows and 6,453 sampled passengers. This is an observed pre-existing export discrepancy, not a cleaning operation applied here. The main pipeline leaves these cells in all-carrier fare totals and does not identify them as DL, NW or a named legacy carrier.

These facts establish the relationship between the two aggregate files. They do not independently validate upstream individual-ticket screening. The complete reports and rerun instructions are in [provenance/](../provenance/). No separate ownership or new license over third-party source data is asserted by this repository.
