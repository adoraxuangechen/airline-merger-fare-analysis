# Data sources and access

## Primary: Borenstein market aggregates, 2005–2010

The main analysis uses the NBER-hosted Borenstein archive. This is a processed aggregate product based on DOT DB1A/DB1B records, not raw ticket data. It includes all recorded carrier codes, with domestic itinerary/fare screens described by Borenstein. Source ZIP SHA256:

`75b2fe06890bf54f3466824e0309e3d52a74c3dfc3b22f940000face130ecfa9`

Run `python scripts/download_nber.py` to obtain the archive and create `data/NBER_2005_2010.csv.gz`. The extraction selects 4,175,354 rows, preserves literal carrier code `NA`, and writes metadata. The reviewed extraction SHA256 is recorded in [NBER_2005_2010.metadata.json](NBER_2005_2010.metadata.json). Existing outputs are never silently overwritten. Main cleaning then removes four same-airport records.

The prior supplied CSV is a historical input preserved through the earlier [release-download instructions](../archive/v1/data/README.md). Its numerical observations match the source to export precision, but 42 carrier entries lost literal `NA`. This version reads the source instead of imputing those codes. To retrieve the historical input from the current repository root, run `python archive/v1/scripts/download_and_verify.py`.

## Supplementary: original BTS quarterly archives

All 72 official Market/Coupon/Ticket URLs and sizes for 2005–2010 are listed in [bts_2005_2010_url_manifest.json](bts_2005_2010_url_manifest.json). These tables retain different information and are not appended to the main Borenstein panel.

Optional original-source acquisition:

```sh
python scripts/discover_raw_bts.py
python scripts/download_bts_market.py
python scripts/profile_bts_pilot.py
python scripts/verify_bts_download_manifest.py
```

This retrieves 24 Market archives (approximately 2.01 GB compressed) plus a 2007Q1 Coupon/Ticket pilot. The full Market CSVs exceed 31 GB uncompressed; scripts stream ZIP members rather than expanding all files. The downloader uses at most two connections and checks disk capacity. Relevant source dictionaries are inside each ZIP. A row's sampled passenger count remains its weight.

Market includes ticketing and operating codes, but carrier 99 represents mixed-carrier itineraries and is not a standalone firm. Its fare is prorated from itinerary measures. Ticket is needed for some fare-credibility and trip-level screening. One coupon can represent direct through service, so schedules or flight-level evidence are needed for verified physical nonstop status.

See [the raw-source report](../provenance/raw_data_discovery.md) and [verification summary](../provenance/bts_market/verification_summary.json). Raw ZIPs and large regenerated intermediates are excluded from Git; URLs and hashes establish reproducible access. Historical source dictionaries and screening assumptions remain attributable to their providers.
