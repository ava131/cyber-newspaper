import argparse
import base64
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import urlparse

from render_expanded import JS, SPREAD_CSS, prose_count
from render_sample import CSS, change_class, escape, percentage, quote_table, quote_time, render_block, source_links
from sample_collect import ROOT
from weather_render import CSS as WEATHER_CSS, render as render_weather


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", required=True)
    args = parser.parse_args()
    day = datetime.strptime(args.edition, "%Y-%m-%d")
    edition = ROOT / "data/editions" / args.edition
    collection = json.loads((edition / "collection.json").read_text())
    editorial = json.loads((edition / "editorial.json").read_text())
    issue_label = editorial.get("issue_label", "早报")
    weather_path = edition / "weather.json"
    weather = json.loads(weather_path.read_text()) if weather_path.exists() else None
    if editorial.get("weather_required") and not weather:
        raise ValueError("This edition requires the front-page weather data")
    if weather and weather["forecast"][0]["date"] != args.edition:
        raise ValueError("Weather date does not match this edition")
    market_context = collection["market_context"]
    us_label = market_context["US_snapshot_label"]
    ah_label = market_context["AH_snapshot_label"]
    sources = {document["id"]:{**document, "short_title":document["title"].split("：")[0]} for document in collection["documents"] if document["status"] == "ok"}
    evidence = {entry["id"]:entry for entry in editorial["evidence"]}
    if len(evidence) != len(editorial["evidence"]):
        raise ValueError("Duplicate evidence IDs")
    for entry in evidence.values():
        if entry["quote"] not in sources[entry["source"]]["text"]:
            raise ValueError("Missing source excerpt: " + entry["id"])
    quotes = {quote["code"]:quote for quote in collection["quotes"]}
    if set(collection["requested_instruments"]) != set(quotes):
        raise ValueError("Missing quote instruments")
    for quote in quotes.values():
        if abs(quote["computed_pct"] - quote["provider_pct"]) > 0.011:
            raise ValueError("Quote arithmetic mismatch: " + quote["code"])
    replacements = {key:value for code,quote in quotes.items() for key,value in ((code+"_pct",percentage(quote["computed_pct"])), (code+"_price",f'{quote["last"]:,.2f}'))}
    prior = json.loads((ROOT / "data/editions" / editorial["comparison_edition"] / "collection.json").read_text())
    prior_quotes = {quote["code"]:quote for quote in prior["quotes"]}
    comparisons = {"nvda_gap":quotes["us.IXIC"]["computed_pct"]-quotes["usNVDA"]["computed_pct"],
                   "a_gap":quotes["sh000688"]["computed_pct"]-quotes["sz399006"]["computed_pct"],
                   "nvda_two_day":(quotes["usNVDA"]["last"]/prior_quotes["usNVDA"]["previous"]-1)*100}
    if abs(quotes["usNVDA"]["previous"]-prior_quotes["usNVDA"]["last"])>0.001:
        raise ValueError("NVIDIA two-day comparison is not continuous")
    replacements.update({key:f'{value:.2f}' for key,value in comparisons.items()})
    collected_at = datetime.fromisoformat(collection["collected_at"])
    blocks = [block for page in editorial["pages"] for block in page["blocks"]]
    adopted = {editorial["artwork"]["source"], editorial["poem"]["source"]}
    if weather:
        if weather["source_id"] not in sources:
            raise ValueError("Weather source record missing")
        adopted.add(weather["source_id"])
    for block in blocks:
        identifiers = set(block.get("sources",[])) | {evidence[key]["source"] for key in block.get("evidence",[])}
        identifiers.update(quotes[code]["source_id"] for code in block.get("quote_codes",[]))
        rss_entries = list(block.get("rss_items",[]))
        if block.get("rss_title"):
            rss_entries.insert(0,{"title":block["rss_title"],"source":block["rss_source"]})
        for rss_entry in rss_entries:
            matches = [article for article in collection["articles"] if article["title"] == rss_entry["title"] and article["source_id"] == rss_entry["source"]]
            if not matches:
                raise ValueError("Missing RSS article: " + rss_entry["title"])
            article = matches[0]
            if article.get("published") and datetime.fromisoformat(article["published"])>collected_at:
                raise ValueError("Adopted article is from after collection")
            identifier = "rss_" + hashlib.sha256(article["url"].encode()).hexdigest()[:12]
            parent = sources[article["source_id"]]
            sources[identifier] = {"id":identifier, "title":article["title"], "short_title":parent["title"]+" · RSS摘要", "url":article["url"], "category":"rss_item", "published":article["published"], "fetched_at":parent["fetched_at"], "raw_path":parent["raw_path"], "parent_feed":article["source_id"]}
            identifiers.add(identifier)
        if not identifiers.issubset(sources):
            raise ValueError("Unknown source in " + block["id"])
        if block["kind"] == "report" and not identifiers:
            raise ValueError("Report lacks a source: " + block["id"])
        block["source_ids"] = sorted(identifiers)
        adopted.update(identifiers)
    adopted.update(quote["source_id"] for quote in quotes.values())
    art = editorial["artwork"]
    poem = editorial["poem"]
    image_bytes = (edition / art["path"]).read_bytes()
    if not image_bytes.startswith(b"\xff\xd8"):
        raise ValueError("Expected original JPEG")
    image_url = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()
    if not all(line in sources[poem["source"]]["text"] for line in poem["lines"]):
        raise ValueError("Poem text does not match source")
    page_counts = {page["id"]:prose_count(page) for page in editorial["pages"]}
    if len(editorial["pages"]) != 6 or sum(page_counts.values()) < 6000:
        raise ValueError("Daily edition requires six pages and at least 6,000 prose characters")
    feeds = [document for document in collection["documents"] if document["category"] == "feed"]
    network = [document for document in collection["documents"] if document["category"] != "web_excerpt" and document.get("retrieval_method") != "prior_edition_snapshot"]
    freshness = Counter()
    seen = set()
    for article in collection["articles"]:
        if article["url"] in seen:
            freshness["duplicate_url"] += 1
            continue
        seen.add(article["url"])
        try:
            published = datetime.fromisoformat(article["published"])
            if not published.tzinfo:
                freshness["missing_date"] += 1
            elif published>collected_at:
                freshness["future_date"] += 1
            else:
                freshness["within_24h" if collected_at-published<=timedelta(hours=24) else "older_than_24h"] += 1
        except (TypeError, ValueError):
            freshness["missing_date"] += 1
    x_status = json.loads((edition / "x_status.json").read_text())
    archived_count = sum(quote["source_id"]=="market_quotes_prior" for quote in quotes.values())
    market_counts = f'{len(quotes)-archived_count}项本次接口值；{archived_count}项历史存档'
    web_excerpts = [key for key in adopted if sources[key]["category"]=="web_excerpt"]
    web_note = "网页工具摘录分别留档，未记作程序取得的全文。" if web_excerpts else "本期采用的原文与元数据均有程序抓取记录。"
    stats = {"edition":args.edition, "collected_at":collection["collected_at"], "enriched_at":collection.get("enriched_at"), "pages":6, "sections":4,
             "feed_sources_requested":len(feeds), "feed_sources_ok":sum(document["status"]=="ok" for document in feeds), "rss_candidates":len(collection["articles"]),
             "fetch_requests":len(network), "fetch_success":sum(document["status"]=="ok" for document in network),
             "source_records_adopted":len(adopted), "source_types_adopted":dict(Counter(sources[key]["category"] for key in adopted)),
             "source_domains_adopted":len({urlparse(sources[key]["url"]).netloc for key in adopted}),
             "market_instruments":len(quotes), "original_market_field_values":6*len(quotes), "computed_market_values":2*len(quotes), "market_comparisons":comparisons,
             "market_context":collection["market_context"], "archived_AH_instruments":sum(quote["source_id"]=="market_quotes_prior" for quote in quotes.values()),
             "llm_content_blocks":len(blocks), "llm_paragraphs":sum(len(block["paragraphs"]) for block in blocks), "llm_nonwhitespace_characters":sum(page_counts.values()),
             "characters_by_page":page_counts, "blocks_by_kind":dict(Counter(block["kind"] for block in blocks)), "evidence_excerpt_checks":len(evidence), "rss_time_accounting":dict(freshness),
             "writer":"GPT-6（本次会话）", "independent_reviewer_agent":False, "x_status":x_status,
             "artwork":{**art, "sha256":hashlib.sha256(image_bytes).hexdigest(), "bytes":len(image_bytes)}, "poem_origin":"public_domain_original_verified_against_source",
             "weather":weather,
             "source_records":[{key:value for key,value in sources[identifier].items() if key not in ("text","items")} for identifier in sorted(adopted)],
             "story_provenance":[{"id":block["id"], "kind":block["kind"], "sources":block["source_ids"], "evidence":block.get("evidence",[])} for block in blocks],
             "fetch_failures":[document for document in network if document["status"] != "ok"]}
    pages_html = {}
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][day.weekday()]
    dateline = f"{day.year}年{day.month}月{day.day}日 · {weekday} · {issue_label}"
    for number,page in enumerate(editorial["pages"],1):
        hero = f'<p class="eyebrow">{escape(page["kicker"])}</p><h1 class="headline">{escape(page["headline"]).replace(chr(10),"<br>")}</h1><p class="deck">{escape(page["deck"])}</p>'
        header = '<div class="masthead"><div><h2>赛博日报</h2><div class="latin">CYBER DAILY</div></div><div class="motto">每天看见世界<br>也给自己留一页。</div></div>' if number==1 else f'<div class="section-mark"><strong>{escape(page["label"])}</strong><span>{escape(page["english"])}</span></div>'
        if number==1 and weather:
            header += render_weather(weather)
        inserts = ""
        extras = ""
        if page["id"] == "politics":
            inserts = '<div class="diplomacy">'+"".join(f'<div><b>{escape(item[0])}</b><span>{escape(item[1])}</span></div>' for item in editorial["politics_rail"])+"</div>"
        if page["id"] == "finance":
            quote = quotes["usNVDA"]
            hero = f'<div class="hero"><div>{hero}</div><div class="hero-figure"><b>{percentage(quote["computed_pct"])}</b><span>NVDA · {us_label}常规收盘<br>接口价 ${quote["last"]:.2f}</span></div></div>'
            inserts = '<div class="market-grid">'+"".join(f'<div class="market-card" data-origin="program-market"><span>{escape(quote["label"])}<small>{escape(quote_time(quote))}</small></span><div><strong>{quote["last"]:,.2f}</strong><b class="{change_class(quote["computed_pct"])}">{percentage(quote["computed_pct"])}</b></div></div>' for quote in quotes.values() if quote["group"]=="index")+'</div><p class="quote-ref">'+escape(collection["market_context"]["note"])+" 红涨绿跌。所有报价保留接口时标。</p>"
            extras = f'<div class="market-tables"><div><h3 class="table-title">行业温度 · {ah_label} ETF样本</h3><div class="table-caption">四个代理标的，不等同于行业排名。</div>'+quote_table([quote for quote in quotes.values() if quote["group"]=="sector_etf"])+"</div></div>"
        if page["id"] == "finance-stocks":
            inserts = f'<div class="market-tables"><div><h3 class="table-title">观察名单 · 分市场读</h3><div class="table-caption">沿用5只演示股票。美股{us_label}收盘；港股{ah_label}快照。名单尚未替换为你的真实自选。</div>'+quote_table([quote for quote in quotes.values() if quote["group"]=="watchlist_demo"])+"</div></div>"
        if page["id"] == "technology":
            inserts = '<div class="system-diagram">'+"<i>→</i>".join(f'<div><b>{escape(step[0])}</b>{escape(step[1])}<span>{escape(step[2])}</span></div>' for step in editorial["tech_rail"])+"</div>"
            extras = '<div class="paper-grid">'+"".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="paper")+'</div><p class="reading-level">论文基于摘要与实验设定阅读；发布日期逐项标注。代码新闻来自官方Release。性能数字均保留适用硬件。</p>'
        if page["id"] == "culture":
            inserts = f'<div class="art-hero"><figure class="artwork"><img id="art-open" tabindex="0" role="button" aria-label="放大查看原作" src="{image_url}" alt="{escape(art["alt"])}"><figcaption>{escape(art["caption"])}<br><a href="{escape(sources[art["source"]]["url"])}" target="_blank" rel="noopener noreferrer">美术馆原作档案 ↗</a> · 点画可放大</figcaption></figure><div><div class="poem-card"><p class="eyebrow">一诗短读 / PUBLIC DOMAIN</p><h3>{escape(poem["title"])}</h3><p class="author">{escape(poem["author"])}</p><blockquote>'+"<br>".join(escape(line) for line in poem["lines"])+f'</blockquote><p class="poem-note">{escape(poem["rights"])}<br><a href="{escape(sources[poem["source"]]["url"])}" target="_blank" rel="noopener noreferrer">原文出处 ↗</a></p></div><p class="art-caption-note">{escape(editorial["culture_note"])}</p></div></div>'
        main = "".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="main")
        side = "".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="sidebar")
        feature = "".join('<div class="feature">'+render_block(block,replacements,sources)+"</div>" for block in page["blocks"] if block["placement"]=="feature")
        pages_html[page["id"]] = f'<section class="page {page["section"]}" id="page-{number}" aria-label="第{number}版 {escape(page["label"])}"><div class="topline"><span>赛博日报 / 六版{escape(issue_label)}</span><span>{escape(page["english"])}</span><span>{dateline}</span></div>'+header+hero+f'<div class="byline">本报编辑部 · GPT-6撰稿 / 新闻快照 {collected_at:%H:%M} 北京时间 / 市场时段见表</div>'+inserts+f'<div class="body-grid"><div><div class="main-columns">{main}</div>{feature}</div><aside class="sidebar">{side}</aside></div>'+extras+f'<footer class="page-footer"><span>CYBER DAILY · {escape(page["label"])}</span><span>来源与文字分工见账单</span><span class="folio">0{number}</span></footer></section>'
    spreads_html = []
    tabs = []
    offset = 0
    for index,spread in enumerate(editorial["spreads"]):
        page_range = f'{offset+1}—{offset+len(spread["pages"])}' if len(spread["pages"])>1 else str(offset+1)
        caption = spread["label"]+' · 第'+page_range+'版'
        spreads_html.append(f'<div class="spread {"pair" if len(spread["pages"])>1 else "single"}" id="spread-{index}" data-caption="{escape(caption)}"'+(" hidden" if index else "")+'>'+"".join(pages_html[key] for key in spread["pages"])+"</div>")
        tabs.append(f'<button role="tab" data-spread="{index}" aria-controls="spread-{index}" aria-selected="{str(index==0).lower()}">{escape(spread["label"])} {page_range}</button>')
        offset += len(spread["pages"])
    details = "".join(f'<details><summary>{escape(sources[key]["title"])} · {sources[key]["category"]}</summary><p><a href="{escape(sources[key]["url"])}" target="_blank" rel="noopener noreferrer">打开来源</a><br>取得时间：{escape(sources[key]["fetched_at"])}<br>方式：{escape(sources[key].get("retrieval_method","program_fetch"))}<br><code>{escape(sources[key].get("raw_path",""))}</code></p></details>' for key in sorted(adopted))
    audit_rows = [
        ("行情",f"{len(quotes)}标的／{6*len(quotes)}字段",f"程序读接口；{2*len(quotes)}个单标的值、{len(comparisons)}个比较值由程序计算。"),
        ("市场时段",market_counts,market_context["note"]),
        ("正文",f"{len(blocks)}块／{stats['llm_paragraphs']}段","标题、导语、转述和分析由LLM写作，行情占位符由程序填数。"),
        ("摘录",f"{len(evidence)}项","LLM选取事实片段；程序核对片段存在。公告与论文的其他数值由LLM转录。"),
        ("网页工具",f"{len(web_excerpts)}份摘录",web_note),
        ("艺文","原作1张；古诗1首","图片由程序下载、内嵌，来源与授权见原作档案；古诗逐行核对，鉴赏由LLM撰写。"),
        ("X",f"{len(x_status['posts'])}条",f"当前{x_status['status']}，{x_status['requests']}次请求。")
    ]
    if weather:
        audit_rows.insert(2,("天气","5项当前字段＋3天×7项日字段","汾湖（黎里）定点预报来自Open-Meteo；中文天气、风向、提醒均由程序规则映射。未让LLM填写温度。"))
    audit_table = "".join("<tr>"+"".join("<td>"+escape(value)+"</td>" for value in row)+"</tr>" for row in audit_rows)
    audit = f'''<dialog id="audit" aria-labelledby="audit-title"><button id="audit-close" class="close" autofocus>关闭 ×</button><h2 id="audit-title">来源账单 · {args.edition}</h2><p>四栏目、六版。GPT-6在本次会话选题、阅读与写作，没有独立审稿agent。</p><div class="audit-stats"><div><b>{stats['feed_sources_ok']}/{len(feeds)}</b><span>RSS入口取得有效条目</span></div><div><b>{len(collection['articles'])}</b><span>抓取候选条目</span></div><div><b>{len(adopted)}</b><span>采用来源记录</span></div><div><b>{stats['llm_nonwhitespace_characters']:,}</b><span>LLM稿件非空白字符</span></div></div><table><thead><tr><th>项目</th><th>数量</th><th>实际分工</th></tr></thead><tbody>{audit_table}</tbody></table><h3>采用来源</h3><p>{escape(json.dumps(stats['source_types_adopted'],ensure_ascii=False))}，涉及{stats['source_domains_adopted']}个域名。同一家媒体不同文章分别计数。</p>{details}<h3>未取得有效内容的入口</h3><p>{escape('；'.join(document['id']+': '+document['error'] for document in stats['fetch_failures']))}</p><h3>候选时间统计</h3><p>{escape(json.dumps(dict(freshness),ensure_ascii=False))}</p><p>数据目录：data/editions/{args.edition}。稿件字符含标题、导语、段落，不含行情表、天气条、古诗原文、栏目装饰与来源界面。</p></dialog>'''
    art_modal = f'<dialog class="art-modal" id="art-view" aria-label="原作放大图"><button id="art-close" class="close">关闭 ×</button><img src="{image_url}" alt="{escape(art["alt"])}"><p>{escape(art["caption"])}</p></dialog>'
    html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赛博日报 · '+args.edition+' · 六版'+escape(issue_label)+'</title><style>'+CSS+SPREAD_CSS+WEATHER_CSS+'</style></head><body><header class="reader"><span class="brand">赛博日报 / '+day.strftime('%m.%d')+'</span><nav role="tablist" aria-label="栏目">'+"".join(tabs)+'</nav><div class="reader-actions"><button id="layout-toggle" class="layout-control" aria-pressed="false">纵向阅读</button><button id="audit-open">来源账单 ↗</button></div></header><main class="edition">'+"".join(spreads_html)+'<div class="bottom-nav"><button id="previous">← 上一栏目</button><span id="position"></span><button id="next">下一栏目 →</button></div></main>'+audit+art_modal+'<script>'+JS+'</script></body></html>'
    output = ROOT / ('cyber-daily-'+args.edition+'.html')
    output.write_text(html)
    (edition / "editorial.json").write_text(json.dumps(editorial,ensure_ascii=False,indent=2))
    (edition / "provenance.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    report = f'''# {args.edition}：来源与生成分工

成品：`{output.name}`。RSS和行情快照：{collection['collected_at']}。四栏目、六版。

程序请求{len(network)}个网络资源，成功{stats['fetch_success']}个；RSS入口{len(feeds)}个，成功{stats['feed_sources_ok']}个，共{len(collection['articles'])}条候选。实际采用{len(adopted)}条来源记录，涉及{stats['source_domains_adopted']}个域名。来源类型为{json.dumps(stats['source_types_adopted'],ensure_ascii=False)}。

{len(quotes)}个行情标的、{6*len(quotes)}个原始字段值由程序读取；{2*len(quotes)}个单标的派生值与{len(comparisons)}个比较值由程序计算。{market_counts}。{collection['market_context']['note']}

LLM贡献{len(blocks)}个稿件块、{stats['llm_paragraphs']}段、{stats['llm_nonwhitespace_characters']}个非空白字符（标题、导语和段落，排除行情占位符、古诗原文和界面文字）。LLM承担选题、报道转述、分析与艺术鉴赏。{len(evidence)}个事实摘录通过存在性核对；这不是自动语义核实。公告和论文中的其他数值由LLM转录，没有全部变成结构化API字段。

网页工具摘录{len(web_excerpts)}份。{web_note} 完整采集状态与每篇稿件的来源见`provenance.json`。

原作：{art['caption']} 图片{len(image_bytes)}字节，SHA-256 `{stats['artwork']['sha256']}`。图片从登记的原作图像来源下载，未AI生成。古诗采用维基文库公版原文，逐行核对，未计作LLM创作。

天气：{'汾湖（黎里）定点预报，5项当前字段、3天×7项日字段；原始JSON与weather.json留档，中文映射和提醒均为程序规则。天气不计作LLM稿件。' if weather else '本期未配置。'}

X：{x_status['status']}，{len(x_status['posts'])}条，{x_status['requests']}次API请求。独立审稿agent未运行。

离线重渲染：`python3 pipeline/render_daily.py --edition {args.edition}`。
浏览器验证：`node pipeline/preview_sample.mjs --edition {args.edition}`。
'''
    (edition / "PROVENANCE.md").write_text(report)
    print(json.dumps({key:value for key,value in stats.items() if key not in ("source_records","story_provenance","fetch_failures","artwork")},ensure_ascii=False,indent=2))
    print(output)


if __name__ == "__main__":
    main()
