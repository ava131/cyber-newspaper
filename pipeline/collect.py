#!/usr/bin/env python3
"""采集层：把 RSS 与行情抓成一个统一的 raw JSON。

设计原则（来自 openpaper / daily-crosswire 的教训）：
  1. 只用标准库，零依赖，任何时候都能跑。
  2. 单个信源失败不影响整份报纸，失败要记录而不是静默吞掉。
  3. 输出是纯数据，不含任何模型判断——写稿是下一步的事。

用法:
    python3 pipeline/collect.py [--date YYYY-MM-DD] [--out data]
"""
import argparse
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
NS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/",
      "dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        charset = r.headers.get_content_charset()
    for enc in [charset, "utf-8", "gb18030"]:
        if not enc:
            continue
        try:
            return raw.decode(enc, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def plain(html, limit=600):
    if not html:
        return ""
    txt = TAG_RE.sub(" ", unescape(html))
    txt = WS_RE.sub(" ", txt).strip()
    return txt[:limit]


def text_of(node, *paths):
    for p in paths:
        el = node.find(p, NS)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def parse_date(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s).astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    try:
        parsed = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(s, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except Exception:
            continue
    return None


def parse_feed(xml_text):
    """兼容 RSS2.0、RSS1.0/RDF 与 Atom。"""
    root = ET.fromstring(xml_text)
    items = []
    for it in (node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "item"):
        namespace = it.tag.split("}")[0] + "}" if "}" in it.tag else ""
        items.append({
            "title": plain(text_of(it, namespace + "title")),
            "url": text_of(it, namespace + "link"),
            "summary": plain(text_of(it, namespace + "description", "content:encoded"), 800),
            "published": parse_date(text_of(it, namespace + "pubDate", "dc:date")),
            "categories": [category.text.strip() for category in it.findall(namespace + "category") if category.text],
        })
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link = ""
        for l in entry.findall("atom:link", NS):
            if l.get("rel") in (None, "alternate"):
                link = l.get("href", "")
                break
        items.append({
            "title": plain(text_of(entry, "atom:title")),
            "url": link,
            "summary": plain(text_of(entry, "atom:summary", "atom:content"), 800),
            "published": parse_date(text_of(entry, "atom:updated", "atom:published")),
            "categories": [c.get("term") for c in entry.findall("atom:category", NS)],
        })
    return [i for i in items if i["title"] and i["url"]]


def collect_markets(cfg):
    codes = [i["code"] for i in cfg["indices"]]
    try:
        text = fetch(cfg["quote_api"] + ",".join(codes), timeout=8)
    except Exception as e:
        return {"error": str(e), "indices": []}
    out = []
    for line in text.splitlines():
        m = re.match(r'v_(\w+)="(.*)";', line.strip())
        if not m:
            continue
        code, payload = m.group(1), m.group(2).split("~")
        label = next((i["label"] for i in cfg["indices"] if i["code"] == code), code)
        try:
            out.append({
                "code": code, "label": label,
                "last": float(payload[3]), "prev": float(payload[4]),
                "change": float(payload[31]) if len(payload) > 31 else None,
                "pct": float(payload[32]) if len(payload) > 32 else None,
                "time": payload[30] if len(payload) > 30 else "",
            })
        except (ValueError, IndexError):
            continue
    return {"indices": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--out", default="data")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "config" / "sources.json").read_text())
    socket.setdefaulttimeout(20)
    articles, failures = [], []

    for src in cfg["sources"]:
        t0 = time.time()
        try:
            items = parse_feed(fetch(src["url"]))
            for it in items:
                it.update({"source_id": src["id"], "source_name": src["name"],
                           "channel": src["channel"], "source_weight": src["weight"],
                           "lang": src["lang"]})
            articles.extend(items)
            print(f"  ok   {src['id']:<14} {len(items):>3} 条  {time.time()-t0:.1f}s")
        except Exception as e:
            failures.append({"source_id": src["id"], "error": f"{type(e).__name__}: {e}"})
            print(f"  FAIL {src['id']:<14} {type(e).__name__}: {e}")

    markets = collect_markets(cfg.get("markets", {}))

    out_dir = ROOT / args.out / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": args.date,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"articles": len(articles), "sources_ok": len(cfg["sources"]) - len(failures),
                   "sources_failed": len(failures)},
        "failures": failures,
        "markets": markets,
        "articles": articles,
    }
    path = out_dir / f"{args.date}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"\n采集完成: {len(articles)} 条 / {payload['counts']['sources_ok']} 源可用 -> {path.relative_to(ROOT)}")
    if failures:
        print(f"失败 {len(failures)} 源: {', '.join(f['source_id'] for f in failures)}")


if __name__ == "__main__":
    main()
