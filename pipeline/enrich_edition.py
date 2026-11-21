import argparse
import concurrent.futures
import functools
import json
from datetime import datetime
from pathlib import Path

from sample_collect import LOCAL, ROOT, fetch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", required=True)
    parser.add_argument("--documents", required=True, type=Path)
    args = parser.parse_args()
    edition = ROOT / "data/editions" / args.edition
    path = edition / "collection.json"
    collection = json.loads(path.read_text())
    manifest = json.loads(args.documents.read_text())
    targets = [(source["id"], source["name"], source["url"], "document") for source in manifest]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        documents = list(executor.map(functools.partial(fetch, output_dir=edition), targets))
    identifiers = {document["id"] for document in documents}
    collection["documents"] = [document for document in collection["documents"] if document["id"] not in identifiers] + documents
    collection["enriched_at"] = datetime.now(LOCAL).isoformat()
    path.write_text(json.dumps(collection, ensure_ascii=False, indent=2))
    print(json.dumps({"added": len(documents), "failed": [document["id"] for document in documents if document["status"] != "ok"]}))


if __name__ == "__main__":
    main()
