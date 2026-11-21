import argparse
import concurrent.futures
import functools
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

from collect import parse_feed

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/editions/2026-11-19-sample-02"
LOCAL = timezone(timedelta(hours=8))
DOCUMENTS = [
    ("p_meeting", "新华社：习近平在深圳会见特朗普", "https://www.xinhuanet.com/politics/leaders/20261119/f888648ca1f04a05bfa02fea3bac27fe/c.html"),
    ("p_russia", "外交部：习近平会见普京", "https://www.fmprc.gov.cn/zyxw/202611/t20261118_12062007.shtml"),
    ("p_trilateral", "外交部：三方会晤预告", "https://www.fmprc.gov.cn/wjdt_674879/wsrc_674883/202611/t20261116_12059654.shtml"),
    ("p_airport", "新华社／辽宁省政府：机场迎接", "https://www.ln.gov.cn/web/ywdt/rdgz/2026111908315914821/"),
    ("f_fed", "美联储：10月27日至28日会议纪要", "https://www.federalreserve.gov/monetarypolicy/fomcminutes20261028.htm"),
    ("f_nvidia", "AP：亚洲市场与英伟达表现", "https://apnews.com/article/206c84045137824feabe052a29ff6140"),
    ("t_aws", "AWS：ElastiCache分布式KV缓存", "https://aws.amazon.com/blogs/database/announcing-distributed-kv-caching-for-self-hosted-llms-with-amazon-elasticache/"),
    ("t_offload", "arXiv：FlashOffloading", "https://arxiv.org/abs/2611.07542"),
    ("t_quant", "arXiv：Beyond Bitwidth", "https://arxiv.org/abs/2611.21974"),
    ("c_vangogh", "BBC：梵高拍卖", "https://www.bbc.com/news/articles/c5dj1dkwzvzwo"),
]
INDICES = [
    ("sh000001", "上证指数"), ("sz399001", "深证成指"),
    ("sz399006", "创业板指"), ("sh000688", "科创50"),
    ("hkHSI", "恒生指数"), ("hkHSTECH", "恒生科技"),
    ("us.DJI", "道琼斯"), ("us.IXIC", "纳斯达克"), ("us.INX", "标普500"),
]
SECTORS = [
    ("sh512480", "半导体ETF"), ("sh512800", "银行ETF"),
    ("sh512660", "军工ETF"), ("sh512170", "医疗ETF"),
]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def fetch(target, output_dir=None):
    output_dir = output_dir or OUT
    identifier, title, url, category = target
    started = datetime.now(LOCAL).isoformat()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read()
            charset = response.headers.get_content_charset()
            final_url = response.url
        encodings = ["gb18030"] if category == "quotes" else [charset, "utf-8", "gb18030"]
        for encoding in encodings:
            if not encoding:
                continue
            try:
                decoded = body.decode(encoding)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            decoded = body.decode("utf-8", errors="replace")
        raw_path = output_dir / "raw" / (identifier + (".xml" if category == "feed" else ".txt"))
        raw_path.write_text(decoded, encoding="utf-8")
        parser = PlainText()
        if category == "document":
            parser.feed(decoded)
        text_value = re.sub(r"\s+", " ", " ".join(parser.parts)).strip() if category == "document" else decoded
        result = {"id": identifier, "title": title, "url": url, "final_url": final_url,
                  "category": category, "fetched_at": started, "status": "ok",
                  "raw_path": str(raw_path.relative_to(ROOT)), "sha256": hashlib.sha256(body).hexdigest(),
                  "response_bytes": len(body), "text": text_value}
        if category == "feed":
            result["items"] = parse_feed(decoded)
            if not result["items"]:
                raise ValueError("Feed contains no parseable articles")
        print(identifier, "ok", len(body), flush=True)
        return result
    except Exception as error:
        print(identifier, type(error).__name__, str(error), flush=True)
        return {"id": identifier, "title": title, "url": url, "category": category,
                "status": "failed", "fetched_at": started, "error": str(error)}


def parse_quotes(text_value, instruments):
    output = []
    for match in re.finditer(r'v_([^=\s]+)="([^"\n]*)";', text_value):
        code, payload = match.groups()
        if code not in instruments:
            continue
        fields = payload.split("~")
        try:
            last, previous = float(fields[3]), float(fields[4])
            if previous <= 0:
                continue
            output.append({"code": code, **instruments[code], "provider_name": fields[1],
                           "last": last, "previous": previous, "provider_change": float(fields[31]),
                           "provider_pct": float(fields[32]), "provider_time": fields[30],
                           "computed_change": round(last - previous, 6),
                           "computed_pct": round((last / previous - 1) * 100, 6),
                           "source_id": "market_quotes"})
        except (ValueError, IndexError):
            continue
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", default="2026-11-19-sample-02")
    parser.add_argument("--documents", type=Path)
    parser.add_argument("--skip-weather", action="store_true")
    args = parser.parse_args()
    output_dir = ROOT / "data/editions" / args.edition
    (output_dir / "raw").mkdir(parents=True, exist_ok=True)
    config = json.loads((ROOT / "config/sources.json").read_text())
    watchlist = json.loads((ROOT / "config/watchlist.json").read_text())
    instruments = {code: {"label": label, "group": "index"} for code, label in INDICES}
    instruments.update({code: {"label": label, "group": "sector_etf"} for code, label in SECTORS})
    instruments.update({stock["code"]: {"label": stock["label"], "symbol": stock["symbol"], "group": "watchlist_demo"} for stock in watchlist["stocks"]})
    quote_url = "https://qt.gtimg.cn/q=" + ",".join(instruments)
    if args.documents:
        selected = json.loads(args.documents.read_text())
        targets = [(source["id"], source["name"], source["url"], "document") for source in selected]
    else:
        targets = [(identifier, title, url, "document") for identifier, title, url in DOCUMENTS]
        targets.extend((source["id"], source["name"], source["url"], "document") for source in config.get("documents", []))
    targets.extend((source["id"], source["name"], source["url"], "feed") for source in config["sources"])
    targets.append(("market_quotes", "腾讯行情接口", quote_url, "quotes"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        documents = list(executor.map(functools.partial(fetch, output_dir=output_dir), targets))
    articles = []
    for document in documents:
        for article in document.get("items", []):
            articles.append({**article, "source_id": document["id"]})
    quote_document = next(document for document in documents if document["id"] == "market_quotes")
    quotes = parse_quotes(quote_document.get("text", ""), instruments)
    payload = {"edition": args.edition, "collected_at": datetime.now(LOCAL).isoformat(),
               "documents": documents, "articles": articles, "quotes": quotes,
               "requested_instruments": list(instruments), "watchlist_status": watchlist["status"]}
    (output_dir / "collection.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.skip_weather and (ROOT / "config/weather.json").exists() and args.edition == datetime.now(LOCAL).strftime("%Y-%m-%d"):
        subprocess.run([sys.executable,str(ROOT / "pipeline/weather_collect.py"),"--edition",args.edition,"--quiet"],check=True)
    print(json.dumps({"articles": len(articles), "quotes": len(quotes),
                      "failures": [document["id"] for document in documents if document["status"] != "ok"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
