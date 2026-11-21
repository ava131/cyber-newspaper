import argparse
import copy
import hashlib
import json
from datetime import datetime

from sample_collect import LOCAL, ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", required=True)
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args()
    edition = ROOT / "data/editions" / args.edition
    path = edition / "collection.json"
    collection = json.loads(path.read_text())
    baseline = json.loads((ROOT / "data/editions" / args.baseline / "collection.json").read_text())
    if "preopen_quotes" not in collection:
        collection["preopen_quotes"] = copy.deepcopy(collection["quotes"])
    prior = {quote["code"]: quote for quote in baseline["quotes"]}
    if any(not quote["provider_time"].startswith((args.edition.replace("-", ""), args.edition.replace("-", "/"))) for quote in collection["preopen_quotes"] if not quote["code"].startswith("us")):
        raise ValueError("Expected the edition day's A/H pre-open snapshot")
    collection["quotes"] = [quote if quote["code"].startswith("us") else {**copy.deepcopy(prior[quote["code"]]), "source_id":"market_quotes_prior"} for quote in collection["preopen_quotes"]]
    prior_source = copy.deepcopy(next(document for document in baseline["documents"] if document["id"] == "market_quotes"))
    baseline_day = datetime.fromisoformat(baseline["collected_at"]).strftime("%m/%d")
    us_days = {quote["provider_time"][:10] for quote in collection["quotes"] if quote["code"].startswith("us")}
    if len(us_days) != 1:
        raise ValueError("US snapshot sessions are mixed")
    us_day = datetime.strptime(next(iter(us_days)), "%Y-%m-%d").strftime("%m/%d")
    prior_source.update({"id":"market_quotes_prior", "title":f"腾讯行情：{baseline_day} A股及港股存档快照", "retrieval_method":"prior_edition_snapshot", "archived_edition":args.baseline})
    extras = [prior_source]
    for source in json.loads((edition / "web_sources.json").read_text()):
        raw_path = edition / "raw" / (source["id"] + ".txt")
        raw_path.write_text(source["text"])
        extras.append({**source, "category":"web_excerpt", "status":"ok", "fetched_at":datetime.now(LOCAL).isoformat(), "raw_path":str(raw_path.relative_to(ROOT)), "sha256":hashlib.sha256(source["text"].encode()).hexdigest()})
    identifiers = {document["id"] for document in extras}
    collection["documents"] = [document for document in collection["documents"] if document["id"] not in identifiers] + extras
    collection["market_context"] = {"mode":"morning_before_AH_open", "baseline_edition":args.baseline, "AH_snapshot_label":baseline_day, "US_snapshot_label":us_day, "note":f"美股采用{us_day}常规收盘接口；A股、港股沿用{baseline_day}存档快照。今日盘前及竞价另记，未纳入本表。"}
    path.write_text(json.dumps(collection, ensure_ascii=False, indent=2))
    print(json.dumps({"quotes":len(collection["quotes"]), "prior_AH":sum(not quote["code"].startswith("us") for quote in collection["quotes"]), "web_excerpts":len(extras)-1}, ensure_ascii=False))


if __name__ == "__main__":
    main()
