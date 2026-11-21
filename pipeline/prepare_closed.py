import argparse
import json
from datetime import datetime, timedelta

from sample_collect import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", required=True)
    args = parser.parse_args()
    day = datetime.strptime(args.edition, "%Y-%m-%d")
    if day.weekday() not in (5, 6):
        raise ValueError("This preparation step requires a weekend edition")
    friday = (day - timedelta(days=day.weekday()-4)).strftime("%Y-%m-%d")
    path = ROOT / "data/editions" / args.edition / "collection.json"
    collection = json.loads(path.read_text())
    for quote in collection["quotes"]:
        raw = quote["provider_time"]
        stamp = datetime.strptime(raw[:8], "%Y%m%d").strftime("%Y-%m-%d") if raw[:8].isdigit() else raw[:10].replace("/", "-")
        if stamp != friday:
            raise ValueError("Unexpected session for " + quote["code"] + ": " + stamp)
    label = datetime.strptime(friday, "%Y-%m-%d").strftime("%m/%d")
    collection["market_context"] = {"mode":"weekend_closed_markets", "US_snapshot_label":label,"AH_snapshot_label":label,
                                     "note":f"周末休市；美股、A股及港股均采用{label}已结束交易日的接口快照，各市场时标单独保留。"}
    path.write_text(json.dumps(collection, ensure_ascii=False, indent=2))
    print(json.dumps(collection["market_context"], ensure_ascii=False))


if __name__ == "__main__":
    main()
