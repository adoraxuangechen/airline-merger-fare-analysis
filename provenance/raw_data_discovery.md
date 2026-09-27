# Authentic BTS DB1B raw data discovery

Retrieved 27 September 2026. This note describes the source downloads and a raw-data coverage audit. It does not report a cleaned estimation sample or any new merger-effect estimate.

## Source distinction and download status

The authentic source is the U.S. Bureau of Transportation Statistics (BTS), TranStats **Airline Origin and Destination Survey (DB1B)**. Its historical `PREZIP` directory contains all **72 requested archives: 24 quarters (2005Q1–2010Q4) × Market, Coupon, and Ticket**. Each quarter's tables are complementary, not interchangeable.

The local NBER/Borenstein archive `provenance/mktdata79q1to16q3.zip` is a separately processed market-summary product. It is not the BTS ticket/market/coupon microdata and must not be described as the original BTS raw dataset. The old supplied CSV must retain its own provenance and processing description.

- Official directory: <https://transtats.bts.gov/PREZIP/>
- Direct URL pattern: `https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1B{Market|Coupon|Ticket}_{year}_{quarter}.zip`
- All 72 exact URLs and directory byte sizes: `data/bts_pilot/bts_2005_2010_url_manifest.json`.
- Preserved source directory listing: `data/bts_pilot/bts_prezip_directory.html`.
- Live HEAD checks for all three tables in 2005Q1, 2007Q1, and 2010Q4: `data/bts_pilot/sample_http_metadata.json`; all nine returned HTTP 200 and nonzero ZIP content lengths.
- **Completed pilot:** all three 2007Q1 tables, unchanged ZIP files, verified by ZIP CRC and SHA-256.
- **Completed full Market download:** all 24 quarters are present and have passed byte-count and ZIP CRC checks; SHA-256 hashes are recorded. There are no missing quarters or download errors. Final records are in `data/bts_market/download_manifest.json`, `verification_summary.json`, and `SHA256SUMS.txt`.

Storage was checked before the full download: approximately **201 GiB free**. All 24 Market archives total **2,007,986,102 bytes** compressed (approximately 2.01 GB), containing **31,726,071,075 CSV bytes** uncompressed. All 24 Market files have the same 41 named columns, and the first row's year and quarter agree with its archive name. The full Market downloader uses two simultaneous connections, resumes partial downloads, checks at least 8 GiB free, and reuses the pilot Market ZIP with a hard link. Only the pilot Coupon and Ticket archives were downloaded; their full 24-quarter collections would total 1,843,117,798 and 840,915,618 bytes respectively. CSVs are read inside ZIPs without permanently extracting them.

## Requested sample archive sizes

These are exact live HTTP Content-Length values in bytes, matching the official directory.

| Quarter | Market | Coupon | Ticket |
|---|---:|---:|---:|
| 2005Q1 | 74,496,017 | 69,071,885 | 30,479,359 |
| 2007Q1 | 77,400,513 | 71,465,546 | 32,223,826 |
| 2010Q4 | 90,822,893 | 81,726,966 | 38,802,694 |

All nine requested table/quarter combinations were also inspected at the ZIP member and CSV-header level. The headers match within each table across 2005Q1, 2007Q1, and 2010Q4: 41 Market, 36 Coupon, and 25 Ticket named columns. Each inspected ZIP contains a CSV and `readme.html`. Results are in `data/bts_pilot/requested_sample_schemas.json`. Archives outside the downloaded set were inspected through public HTTP byte ranges (8,495 bytes each), not fully downloaded or hash/CRC-verified; the metadata explicitly labels that difference. The 2010Q4 Market header was initially range-inspected while its full download was finishing and was then also included in the completed full-file verification.

| Quarter | Market uncompressed CSV bytes | Coupon uncompressed CSV bytes | Ticket uncompressed CSV bytes |
|---|---:|---:|---:|
| 2005Q1 | 1,180,933,060 | 1,544,379,137 | 355,559,982 |
| 2007Q1 | 1,212,749,697 | 1,562,553,607 | 374,661,998 |
| 2010Q4 | 1,449,995,644 | 1,843,327,741 | 455,753,098 |

## Pilot integrity and actual ZIP contents

Each pilot ZIP contains one CSV named like its ZIP and one `readme.html` with the field dictionary. The CSVs contain a trailing empty header/field after the meaningful columns; this is a formatting artifact, not an extra economic variable.

| 2007Q1 table | Named columns | Uncompressed CSV bytes | ZIP SHA-256 |
|---|---:|---:|---|
| Market | 41 | 1,212,749,697 | `948c0b98c54f41ebeabccafdfbddcddf12024f828c24aa6c35eff8aab8dfabcb` |
| Coupon | 36 | 1,562,553,607 | `4447f663e8dea5ab61a5389437831feeb5a5cb32d759530c1ebe2d1aa36b87c2` |
| Ticket | 25 | 374,661,998 | `10be6b2ce31acd97e919576931495a4559b33f506fb6d025e3e752b68dcf62fb` |

Complete headers, ZIP members, CRCs, first rows, byte counts and hash records are saved in `pilot_download_metadata.json` (Market/Coupon), `Origin_and_Destination_Survey_DB1BTicket_2007_1.metadata.json` (Ticket), and the full Market manifest. The raw ZIPs remain unmodified.

### Actual Market header

```text
ItinID, MktID, MktCoupons, Year, Quarter,
OriginAirportID, OriginAirportSeqID, OriginCityMarketID, Origin, OriginCountry,
OriginStateFips, OriginState, OriginStateName, OriginWac,
DestAirportID, DestAirportSeqID, DestCityMarketID, Dest, DestCountry,
DestStateFips, DestState, DestStateName, DestWac,
AirportGroup, WacGroup, TkCarrierChange, TkCarrierGroup,
OpCarrierChange, OpCarrierGroup, RPCarrier, TkCarrier, OpCarrier,
BulkFare, Passengers, MktFare, MktDistance, MktDistanceGroup,
MktMilesFlown, NonStopMiles, ItinGeoType, MktGeoType
```

### Actual Coupon header

```text
ItinID, MktID, SeqNum, Coupons, Year,
OriginAirportID, OriginAirportSeqID, OriginCityMarketID, Quarter, Origin,
OriginCountry, OriginStateFips, OriginState, OriginStateName, OriginWac,
DestAirportID, DestAirportSeqID, DestCityMarketID, Dest, DestCountry,
DestStateFips, DestState, DestStateName, DestWac, Break, CouponType,
TkCarrier, OpCarrier, RPCarrier, Passengers, FareClass, Distance,
DistanceGroup, Gateway, ItinGeoType, CouponGeoType
```

### Actual Ticket header

```text
ItinID, Coupons, Year, Quarter, Origin, OriginAirportID, OriginAirportSeqID,
OriginCityMarketID, OriginCountry, OriginStateFips, OriginState, OriginStateName,
OriginWac, RoundTrip, OnLine, DollarCred, FarePerMile, RPCarrier,
Passengers, ItinFare, BulkFare, Distance, DistanceGroup, MilesFlown, ItinGeoType
```

## What each observation means and how to join

- **Ticket:** an itinerary record with a fare per person and represented passenger count. A row is not necessarily one passenger. Carrier reporting rules allow passengers with matching itinerary information to be summarized. `ItinID` links its markets and coupons.
- **Market:** a directional origin–destination part of an itinerary separated by a trip break. A simple round trip generally contributes two directional markets. `MktID` is a record identifier, not the airport-pair route definition used in regressions.
- **Coupon:** the individual reported coupon within the itinerary, ordered by `SeqNum`, carrying coupon-specific origin/destination and ticketing/operating carriers. The Coupon file's `Coupons` counts the whole itinerary's coupons; it is not `MktCoupons`.
- Join Ticket to Market with `(Year, Quarter, ItinID)` after checking Ticket-key uniqueness. Link Coupon to Market with `(Year, Quarter, ItinID, MktID)` and check the coupon count against `MktCoupons`. These are proposed validation requirements; the discovery step has not yet performed full-key reconciliation.
- Joining Market directly to all its Coupons and then summing fares/passengers would multiply the market record by its coupon count. Aggregate coupon information to the market before joining or keep the long coupon representation solely for coupon-level questions.

Source: BTS [Market table profile](https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FHK), [Ticket table profile](https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FKF), and each downloaded archive's `readme.html`.

## Carriers, market fares, and cleaning implications

**Carrier identities must be deliberately chosen.** `RPCarrier` identifies the submitting carrier, not necessarily the airline selling or flying each part of the journey. `TkCarrier` is the ticketing identity; `OpCarrier` is the operator. Their group and change variables retain information for multi-carrier markets. In Market, the single-carrier TK/OP fields use `99` when no single online carrier applies; `99` is not a competitive firm. Coupon records expose each coupon's carrier separately.

**A firm-level HHI is feasible only after defining the economic carrier.** An airport-pair-quarter passenger-share HHI could use ticketing carriers as a commercial-competition measure. It needs a documented ownership/affiliate/codeshare mapping with dates, consistent merger treatment, a declared policy for mixed/unknown carriers, and the same coverage denominator across firms. Do not compute a “firm HHI” from `RPCarrier`, treat `99` as one firm, or assume each regional operating code is a separate pricing competitor. The raw file is richer than a route summary, but it does not supply a ready-made corporate ownership crosswalk or identify causal competitive effects by itself.

**`MktFare` is allocated, not directly separately observed for every leg.** BTS calculates it from itinerary yield and market miles flown. A Market passenger-weighted mean uses `sum(Passengers * MktFare) / sum(Passengers)` on the explicitly selected directional-market records. Do not halve it again merely because the original itinerary is a round trip. It is not automatically comparable to a Borenstein processed fare: geography, fare filters, passenger filters, carrier attribution, and route definitions must first agree.

**Ticket-level quality screens require Ticket data.** `DollarCred`, `ItinFare`, `RoundTrip`, and `FarePerMile` are absent from Market. The BTS credibility lookup marks 0 as questionable and 1 as credible; the source lookup is preserved as `dollarcred_lookup.txt`. Implementing this screen across all 24 quarters would require downloading and joining all 24 Ticket files, not guessing quality from Market alone. `BulkFare` is present in Market. Market observations also contain zero/nonpositive fares that must be handled explicitly.

**Geography is explicit.** The preserved BTS lookup `geo_lookup.txt` defines 0 as international, 1 as non-contiguous domestic (including Alaska, Hawaii, and territories), and 2 as contiguous domestic (lower 48). “Domestic” and “contiguous U.S.” are different restrictions. Stable airport IDs are preferable for airport-pair comparisons over time; city-market IDs support a distinct metropolitan-market analysis.

**One coupon does not conclusively identify a physically nonstop flight.** `MktCoupons == 1` identifies a single reported coupon/no recorded change of plane within the market. A through flight may include an unrecorded intermediate stop. `NonStopMiles` is endpoint distance, not an observed nonstop-service flag. Label a one-coupon restriction accurately. Actual operated nonstop availability/frequency/capacity would need an additional source such as T-100 Segment or schedules and a separate documented join. A [historical analysis filed in DOT docket OST-2008-0252](https://downloads.regulations.gov/DOT-OST-2008-0252-3374/attachment_3.pdf), footnote 1, explicitly distinguishes nonstop and direct flights represented by a coupon. BTS's [current coupon explanation](https://www.bts.gov/topics/airlines-and-airports/origin-and-destination-survey-data-coupon) describes through-flight stops disappearing from coupon records (that webpage describes the newer DB1C; do not silently replace the historical DB1B dictionary with it).

**Fare class is not automatically standardized.** The historical 2007Q1 Coupon archive's own dictionary warns that `FareClass` is carrier-defined and not recommended for analysis. A universal coach-only filter therefore requires additional justification; it should not be presented as a clean, comparable class restriction without validation.

Official historical field lists: [Market](https://transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FHK), [Coupon](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FLM), and [Ticket](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FKF). The archive readmes are the primary schema evidence for the downloaded vintage.

## Pilot carrier coverage: LCCs are present

The untouched 2007Q1 Market file contains **4,795,202 rows** and **10,786,370 represented directional-market passengers**. The Coupon file contains **7,903,722 rows** and **14,460,818 passenger-coupon counts**. These totals describe different units and must not be equated or called unique people. No cleaning, population expansion, or estimation selection was applied to these coverage totals.

| Ticketing code | Market rows | Raw Market passenger sum |
|---|---:|---:|
| WN | 448,803 | 2,042,181 |
| B6 | 65,808 | 434,025 |
| FL | 136,725 | 407,734 |
| F9 | 62,437 | 172,978 |
| NK | 26,222 | 124,157 |
| G4 | 6,793 | 66,156 |
| SY | 6,744 | 41,730 |
| DL | 732,552 | 1,260,650 |
| NW | 417,108 | 746,105 |

Thus important low-fare carrier codes are observable in the original pilot file. This does not establish complete carrier coverage in every 2005–2010 quarter, and an LCC classification still needs a historically appropriate, disclosed code list. The result should not be generalized from “present in one quarter” to a census of all market competition.

Other unfiltered 2007Q1 checks:

- 1,947,862 Market rows have one coupon, representing 7,380,521 directional-market passengers.
- 1,910,152 Market rows have different TK and OP identities; the attribution choice is material.
- 239,000 Market rows use ticketing code `99`, representing 257,401 passengers.
- 58,727 Market rows have `MktFare <= 0`.
- 2,882 Market rows have `BulkFare == 1`.
- 4,480,612 rows are contiguous-domestic markets and 314,590 are non-contiguous-domestic markets.

These are audit flags, not automatic exclusion decisions. The reproducible read-only profiler and full results are `code/profile_bts_pilot.py` and `data/bts_pilot/pilot_profile.json`.

## Sampling and limits

BTS describes historical DB1B as a quarterly 10% ticket sample from reporting carriers; it is not a flight census. Reporting directives also discuss group-ticket aggregation and sample standardization. Passenger-weighted shares and means should use the supplied represented passenger counts. Multiplying all counts by ten changes scale, not shares or weighted means, and does not fix missing-carrier or reporting selection.

The raw data enable different service/carrier definitions and checks unavailable in a summarized file. They do not by themselves solve non-parallel pretrends, route selection, recession/fuel confounding, or concurrent competitive changes. A new estimate based on these files must be labeled a new specification and reconciled with the old sample, not portrayed as a mechanical correction of the earlier coefficient.

Sources: BTS [survey overview](https://www.bts.gov/topics/airlines-and-airports/origin-and-destination-survey-data), [historical reporting instructions](https://www.bts.gov/topics/airlines-and-airports/number-143-passenger-origin-destination-survey-treatment-contract-bulk), and [market-fare overview](https://data.bts.gov/stories/s/Air-Fares/gsyp-spgc). The current DB1C is monthly/40% from July2025; it is a different regime and is not substituted into this 2005–2010 study.

## Reproduction

1. `code/discover_raw_bts.py`: preserve directory, create 72-file manifest, HEAD-check the requested sample dates, download/CRC/hash Market and Coupon 2007Q1.
2. `code/download_bts_market.py`: check storage, download all 24 Market ZIPs plus Ticket2007Q1, reuse completed archives, save per-file metadata and a completion manifest.
3. `code/profile_bts_pilot.py`: stream the unchanged compressed pilot files and save coverage checks without altering their contents.
4. `code/check_bts_sample_schemas.py`: inspect the three requested quarters' ZIP members and headers, using bounded public byte ranges for undownloaded files.
5. `code/verify_bts_download_manifest.py`: verify 24-quarter coverage, common Market schema, first-row date agreement, byte counts, and saved CRC status; write the checksum list and summary.

No GitHub upload or publication is performed by these scripts.
