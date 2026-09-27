"""Read-only profile of untouched 2007Q1 BTS Market/Coupon pilot archives.

These are coverage checks, not cleaned analysis totals or national traffic
estimates. Passengers is summed per directional market, not per itinerary.
"""
from collections import Counter
from pathlib import Path
import json
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "bts_pilot"


def main():
    profile = {}
    for table in ("Market", "Coupon"):
        path = PILOT / f"Origin_and_Destination_Survey_DB1B{table}_2007_1.zip"
        columns = ["Year", "Quarter", "TkCarrier", "OpCarrier", "RPCarrier", "Passengers"]
        columns += ["MktCoupons", "MktFare", "BulkFare", "MktGeoType", "ItinGeoType"] if table == "Market" else ["CouponType", "FareClass"]
        result = {"rows": 0, "passenger_sum": 0.0, "nonpositive_passenger_rows": 0,
                  "ticketing_differs_from_operating_rows": 0,
                  "counts": {c: Counter() for c in columns if c != "Passengers" and c != "MktFare"},
                  "passengers_by_ticketing_carrier": Counter(),
                  "nonpositive_fare_rows": 0, "one_coupon_rows":0, "one_coupon_passengers":0.0}
        with zipfile.ZipFile(path) as archive:
            name = next(n for n in archive.namelist() if n.endswith(".csv"))
            with archive.open(name) as inp:
                chunks = pd.read_csv(inp, usecols=columns, chunksize=250_000,
                                     dtype={c:"string" for c in ("TkCarrier","OpCarrier","RPCarrier")})
                for chunk in chunks:
                    result["rows"] += len(chunk)
                    result["passenger_sum"] += float(chunk.Passengers.sum())
                    result["nonpositive_passenger_rows"] += int((chunk.Passengers <= 0).sum())
                    result["ticketing_differs_from_operating_rows"] += int((chunk.TkCarrier != chunk.OpCarrier).sum())
                    for c in result["counts"]:
                        for value, count in chunk[c].fillna("<missing>").value_counts().items():
                            result["counts"][c][str(value)] += int(count)
                    for carrier, count in chunk.groupby("TkCarrier", dropna=False).Passengers.sum().items():
                        result["passengers_by_ticketing_carrier"][str(carrier)] += float(count)
                    if table == "Market":
                        result["nonpositive_fare_rows"] += int((chunk.MktFare <= 0).sum())
                        one = chunk.MktCoupons == 1
                        result["one_coupon_rows"] += int(one.sum())
                        result["one_coupon_passengers"] += float(chunk.loc[one, "Passengers"].sum())
        profile[table] = result
        (PILOT / "pilot_profile.json").write_text(json.dumps(profile, indent=2))
        print(table, result["rows"], "rows;", result["passenger_sum"], "raw passenger sum", flush=True)
    print("Pilot profile complete", flush=True)


if __name__ == "__main__":
    main()
