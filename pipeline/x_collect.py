import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def normalize(payload, channel="research"):
    users = {user["id"]: user for user in payload.get("includes", {}).get("users", [])}
    result = []
    for post in payload.get("data", []):
        user = users.get(post.get("author_id"), {})
        identifier = str(post.get("id", ""))
        if not identifier.isdigit() or not post.get("text"):
            continue
        username = user.get("username")
        result.append({"id": identifier, "title": post["text"][:160], "summary": post["text"],
                       "url": f"https://x.com/{username}/status/{identifier}" if username else f"https://x.com/i/status/{identifier}",
                       "published": post.get("created_at"), "author": username or post.get("author_id"),
                       "source_id": "x", "channel": channel, "public_metrics": post.get("public_metrics", {}),
                       "verification": "social_post_not_independently_verified"})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--import-json", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "data/x/latest.json")
    args = parser.parse_args()
    config = json.loads((ROOT / "config/x_sources.json").read_text())
    result = {"collected_at": datetime.now(timezone.utc).isoformat(), "status": "disabled", "posts": [], "requests": 0, "errors": []}
    if args.import_json:
        result["posts"] = normalize(json.loads(args.import_json.read_text()))
        result["status"] = "imported"
    elif args.live:
        token = os.environ.get(config["token_environment_variable"])
        if not config["enabled"]:
            result["status"] = "disabled_in_config"
        elif not token:
            result["status"] = "missing_token"
        else:
            for query in config["queries"][:config["max_requests_per_run"]]:
                params = urllib.parse.urlencode({"query": query["query"], "max_results": config["max_results_per_request"],
                                                "tweet.fields": "created_at,author_id,public_metrics", "expansions": "author_id", "user.fields": "username,name",
                                                "start_time": (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")})
                request = urllib.request.Request(config["endpoint"] + "?" + params, headers={"Authorization": "Bearer " + token})
                result["requests"] += 1
                try:
                    with urllib.request.urlopen(request, timeout=20) as response:
                        payload = json.load(response)
                    result["posts"].extend(normalize(payload, query["channel"]))
                    if payload.get("errors"):
                        result["errors"].append({"channel": query["channel"], "error": "X API returned partial errors"})
                except urllib.error.HTTPError as error:
                    result["errors"].append({"channel": query["channel"], "status": error.code})
                    if error.code in (401, 402, 403, 429):
                        break
                except urllib.error.URLError:
                    result["errors"].append({"channel": query["channel"], "error": "Network request failed"})
            result["posts"] = list({post["id"]: post for post in result["posts"]}.values())
            result["status"] = "partial" if result["errors"] else "ok"
    result["reason"] = "实时采集需X开发者Bearer Token、可用额度和显式启用；支持导入官方API JSON。" if result["status"].startswith(("disabled", "missing")) else ""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({"status": result["status"], "posts": len(result["posts"]), "requests": result["requests"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
