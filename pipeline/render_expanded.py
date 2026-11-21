import base64
import copy
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from render_sample import CSS, escape, percentage, quote_table, quote_time, render_block, source_links, change_class

ROOT = Path(__file__).resolve().parent.parent
EDITION = ROOT / "data/editions/2026-11-19-sample-03"
OUTPUT = ROOT / "cyber-daily-2026-11-19-sample-03.html"

SPREAD_CSS = """
.edition{width:min(1940px,calc(100% - 40px))}.reader{padding-left:24px;padding-right:24px}.reader-actions{display:flex;gap:7px}.reader-actions button{border:1px solid #6b6759}.spread{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:stretch}.spread[hidden]{display:none}.spread.single{display:block;max-width:1220px;margin:auto}.page{min-width:0;min-height:0;display:flex;flex-direction:column}.page-footer{margin-top:auto;padding-top:17px}.page-footer:before{content:'';height:16px}.spread.pair .page{padding:28px 27px 22px}.spread.pair .headline{font-size:43px;line-height:1.16}.spread.pair .deck{font-size:16px;line-height:1.8}.spread.pair .masthead{padding:18px 0 15px}.spread.pair .masthead h2{font-size:60px}.spread.pair .masthead .latin{font-size:22px}.spread.pair .motto{font-size:9px}.spread.pair .body-grid{display:block}.spread.pair .main-columns{gap:22px}.spread.pair .story p{font-size:15px;line-height:1.92}.spread.pair .story h3{font-size:20px}.spread.pair .story.main:first-child .paragraphs{columns:2;column-gap:22px}.spread.pair .sidebar{display:grid;grid-template-columns:1fr 1fr;gap:22px;border-left:0;border-top:2px solid var(--ink);padding:20px 0 0;margin-top:22px}.spread.pair .sidebar .story p{font-size:13px;line-height:1.9}.spread.pair .sidebar h3{font-size:18px}.spread.pair .feature{margin-bottom:24px;padding:18px 20px}.spread.pair .topline{font-size:9px;letter-spacing:.03em}.spread.pair .topline span:nth-child(2){display:none}.spread.pair .section-mark strong{font-size:28px}.spread.pair .section-mark span{font-size:11px;letter-spacing:.08em}.spread.pair .diplomacy{gap:0;padding:14px 0}.spread.pair .diplomacy b{font-size:22px}.spread.pair .diplomacy span{font-size:9px;line-height:1.7}.spread.pair .finance .hero{display:block;padding:24px}.spread.pair .hero-figure{border:0;border-top:1px solid #666151;display:flex;align-items:center;justify-content:space-between;padding:15px 0 0;margin-top:18px;text-align:right}.spread.pair .hero-figure b{font-size:48px}.spread.pair .market-grid{grid-template-columns:repeat(3,1fr);gap:0 12px}.spread.pair .market-card{display:block;font-size:11px}.market-card strong{margin-right:7px}.spread.pair .market-card>span{display:block;margin-bottom:6px}.spread.pair .market-card strong{font-size:17px;display:block;margin-bottom:4px}.spread.pair .market-card small{font-size:8px}.spread.pair .market-tables{display:block;margin-bottom:25px}.spread.pair .table-caption{font-size:10px}.spread.pair .byline{font-size:9px;line-height:1.8}.spread.pair .page-footer{font-size:9px;line-height:1.8;gap:8px}.spread.pair .page-footer span:nth-child(2){display:none}.spread.pair .main-columns{margin-bottom:18px}.section-intro{border-left:3px solid var(--accent);padding:10px 14px;margin:0 0 22px;font-size:15px;line-height:1.8;background:#eae2ce}.culture{--accent:#825b39}.culture .headline{font-size:65px}.art-hero{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:30px;margin:10px 0 30px;padding-top:22px;border-top:2px solid var(--ink)}.artwork{margin:0;min-width:0}.artwork img{width:100%;height:auto;display:block;cursor:zoom-in;border:9px solid #d3c2a0;box-shadow:0 3px 13px #3b2a1520}.artwork figcaption{font:11px var(--sans);color:var(--muted);line-height:1.8;margin:14px 0}.poem-card{padding:24px 25px;border:1px solid #c4b390;background:#ebe3d0}.poem-card .eyebrow{font-size:10px}.poem-card h3{font-size:31px;letter-spacing:.16em;margin:12px 0}.poem-card .author{font-size:12px;color:var(--muted);margin:0 0 20px}.poem-card blockquote{margin:0;font-family:'Kaiti SC','STKaiti',var(--serif);font-size:24px;line-height:2.35;letter-spacing:.02em}.poem-card .poem-note{font:10px var(--sans);line-height:1.8;color:var(--muted);margin-top:20px}.art-caption-note{font-size:15px;line-height:1.9;margin-top:22px;padding:0 6px}.culture .body-grid{margin-bottom:28px}.spread.single .page-footer{margin-top:28px}.art-modal{background:#201f1b;color:#eee5ce;border:0;max-width:95vw;width:auto;padding:18px}.art-modal img{display:block;max-width:85vw;max-height:82vh;width:auto;height:auto}.art-modal .close{color:inherit;border-color:#82775f;margin-bottom:12px}.art-modal p{clear:both;font-size:11px;margin-bottom:0}.source-status{font:11px var(--sans);line-height:1.8;border-left:3px solid #a18d65;padding:10px 14px;background:#e9e2d0}.layout-control{white-space:nowrap}
body.vertical-mode .spread.pair{display:block;max-width:1120px;margin:auto}body.vertical-mode .spread.pair .page+.page{margin-top:22px}body.vertical-mode .spread.pair .headline{font-size:58px}body.vertical-mode .spread.pair .story p{font-size:17px}body.vertical-mode .spread.pair .deck{font-size:19px}
.spread.single[hidden]{display:none}
.finance>.deck{color:#4c4a40}.sidebar>.story:last-child:nth-child(odd){grid-column:1/-1}
@media(min-width:1800px){.spread.pair .headline{font-size:52px}.spread.pair .story p{font-size:17px}.spread.pair .deck{font-size:18px}.spread.pair .sidebar .story p{font-size:15px}}
@media(max-width:1150px){.edition{width:min(1000px,calc(100% - 24px))}.spread{display:block}.spread .page+.page{margin-top:20px}.spread.pair .headline{font-size:51px}.spread.pair .story p{font-size:17px}.spread.pair .deck{font-size:18px}.layout-control{display:none}.spread.pair .sidebar .story p{font-size:15px}}
@media(max-width:650px){.edition{width:100%;margin-top:0}.reader-actions{gap:5px}.reader-actions button{font-size:10px;padding:6px 8px}.reader nav{order:3}.reader .brand{margin-right:auto}.spread.pair .page{padding:24px 20px}.spread.pair .headline,.culture .headline,body.vertical-mode .spread.pair .headline{font-size:38px}.spread.pair .deck{font-size:17px}.spread.pair .masthead h2{font-size:49px}.spread.pair .masthead .latin{font-size:16px}.spread.pair .main-columns{display:block}.spread.pair .story.main:first-child .paragraphs{columns:1}.spread.pair .story p{font-size:17px}.spread.pair .sidebar{gap:20px}.spread.pair .sidebar .story p{font-size:14px}.spread.pair .finance .hero{padding:22px 20px}.spread.pair .market-grid{grid-template-columns:repeat(2,1fr);gap:0 18px}.spread.pair .market-card strong{display:inline;font-size:17px}.spread.pair .hero-figure b{font-size:41px}.spread.pair .hero-figure span{font-size:9px}.spread.pair .page-footer{font-size:9px}.art-hero{display:block}.poem-card{margin-top:25px;padding:25px}.poem-card blockquote{font-size:24px}.culture .headline{font-size:38px}.art-caption-note{font-size:16px}.artwork img{border-width:6px}.topline{font-size:9px}.section-intro{font-size:15px}.bottom-nav button{padding:10px 12px}.bottom-nav span{font-size:10px}}
@media print{.spread,.spread[hidden],body.vertical-mode .spread.pair{display:block!important;max-width:none}.edition{width:100%}.page{display:block!important;break-after:page}.spread .page+.page{margin:0}.spread.pair .page{padding:0}.spread.pair .headline,.culture .headline{font-size:36px}.spread.pair .story p{font-size:11px;line-height:1.65}.spread.pair .sidebar .story p{font-size:10px}.spread.pair .body-grid{display:block}.spread.pair .page-footer{font-size:8px}.artwork img{max-height:160mm;width:auto;max-width:100%}.art-hero{gap:20px}.poem-card{padding:15px}.poem-card blockquote{font-size:17px}.art-caption-note{font-size:11px}.art-modal{display:none!important}}
"""

JS = """
const spreads=Array.from(document.querySelectorAll('.spread'));
const tabs=Array.from(document.querySelectorAll('[data-spread]'));
const audit=document.querySelector('#audit');
const artDialog=document.querySelector('#art-view');
let active=0;
function showSpread(index,scroll=true){
  active=Math.max(0,Math.min(spreads.length-1,index));
  spreads.forEach((spread,position)=>spread.hidden=position!==active);
  tabs.forEach((tab,position)=>tab.setAttribute('aria-selected',String(position===active)));
  document.querySelector('#previous').disabled=active===0;
  document.querySelector('#next').disabled=active===spreads.length-1;
  document.querySelector('#position').textContent=spreads[active].dataset.caption+' / 共6版';
  history.replaceState(null,'','#'+(active+1));
  if(scroll)window.scrollTo(0,0);
}
tabs.forEach((tab,index)=>tab.addEventListener('click',()=>showSpread(index)));
document.querySelector('#previous').addEventListener('click',()=>showSpread(active-1));
document.querySelector('#next').addEventListener('click',()=>showSpread(active+1));
document.querySelector('#audit-open').addEventListener('click',()=>audit.showModal());
document.querySelector('#audit-close').addEventListener('click',()=>audit.close());
document.querySelector('#art-open').addEventListener('click',()=>artDialog.showModal());
document.querySelector('#art-open').addEventListener('keydown',event=>{
  if(event.key==='Enter'||event.key===' '){event.preventDefault();artDialog.showModal()}
});
document.querySelector('#art-close').addEventListener('click',()=>artDialog.close());
document.querySelector('#layout-toggle').addEventListener('click',event=>{
  const vertical=document.body.classList.toggle('vertical-mode');
  event.currentTarget.textContent=vertical?'对页阅读':'纵向阅读';
  event.currentTarget.setAttribute('aria-pressed',String(vertical));
});
document.addEventListener('keydown',event=>{
  if(audit.open||artDialog.open||/INPUT|TEXTAREA|SELECT/.test(event.target.tagName))return;
  if(event.key==='ArrowRight'){event.preventDefault();showSpread(active+1)}
  if(event.key==='ArrowLeft'){event.preventDefault();showSpread(active-1)}
});
showSpread((Number(location.hash.slice(1))||1)-1,false);
"""


def load_editorial():
    changes = json.loads((EDITION / "editorial_changes.json").read_text())
    base = json.loads((ROOT / "data/editions" / changes["base_edition"] / "editorial.json").read_text())
    blocks = {block["id"]: copy.deepcopy(block) for page in base["pages"] for block in page["blocks"]}
    blocks.update({block["id"]: block for block in changes["additions"]})
    for identifier, update in changes["overrides"].items():
        blocks[identifier].update(update)
    base["pages"] = [{**page, "blocks": [blocks[identifier] for identifier in page["block_ids"]]} for page in changes["pages"]]
    base["evidence"].extend(changes["evidence"])
    base.update({key:changes[key] for key in ("edition_name", "spreads", "poem", "artwork")})
    return base


def prose_count(page):
    texts = [page["headline"], page["deck"]]
    texts.extend(text for block in page["blocks"] for text in [block["title"], *block["paragraphs"]])
    return sum(len(re.sub(r"\s|\{\{.*?\}\}", "", text)) for text in texts)


def main():
    collection = json.loads((EDITION / "collection.json").read_text())
    editorial = load_editorial()
    sources = {document["id"]:{**document, "short_title":document["title"].split("：")[0]} for document in collection["documents"] if document["status"] == "ok"}
    evidence = {entry["id"]:entry for entry in editorial["evidence"]}
    for entry in evidence.values():
        if entry["quote"] not in sources[entry["source"]]["text"]:
            raise ValueError("Missing original excerpt: " + entry["id"])
    quotes = {quote["code"]:quote for quote in collection["quotes"]}
    if set(collection["requested_instruments"]) != set(quotes):
        raise ValueError("Quote instruments missing")
    for quote in quotes.values():
        if abs(quote["computed_pct"] - quote["provider_pct"]) > 0.011:
            raise ValueError("Quote arithmetic mismatch: " + quote["code"])
    replacements = {"nvda_gap":f'{quotes["us.IXIC"]["computed_pct"]-quotes["usNVDA"]["computed_pct"]:.2f}',
                    "a_gap":f'{quotes["sh000688"]["computed_pct"]-quotes["sz399006"]["computed_pct"]:.2f}'}
    adopted = {"market_quotes", "c_lot", "c_poem"}
    blocks = []
    for page in editorial["pages"]:
        for block in page["blocks"]:
            identifiers = {evidence[identifier]["source"] for identifier in block.get("evidence", [])}
            if block.get("rss_title"):
                candidates = [article for article in collection["articles"] if article["title"] == block["rss_title"] and (not block.get("rss_source") or article["source_id"] == block["rss_source"])]
                if not candidates:
                    raise ValueError("Missing RSS item: " + block["rss_title"])
                article = candidates[0]
                identifier = "rss_" + hashlib.sha256(article["url"].encode()).hexdigest()[:12]
                parent = sources[article["source_id"]]
                sources[identifier] = {"id":identifier, "title":article["title"], "short_title":parent["title"]+" · 摘要", "url":article["url"], "category":"rss_item", "parent_feed":article["source_id"], "published":article["published"], "fetched_at":parent["fetched_at"], "raw_path":parent["raw_path"]}
                identifiers.add(identifier)
            if block.get("quote_codes"):
                identifiers.add("market_quotes")
            if block["id"] in ("c_look", "c_brush"):
                identifiers.add("c_lot")
            block["source_ids"] = sorted(identifiers)
            adopted.update(identifiers)
            blocks.append(block)
    artwork = editorial["artwork"]
    image_bytes = (EDITION / artwork["path"]).read_bytes()
    if not image_bytes.startswith(b"\xff\xd8"):
        raise ValueError("Artwork is not a JPEG")
    image_url = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()
    poem = editorial["poem"]
    if not all(line in sources[poem["source"]]["text"] for line in poem["lines"]):
        raise ValueError("Poem transcription does not match its source")
    source_types = Counter(sources[identifier]["category"] for identifier in adopted)
    feed_success = sum(document["category"] == "feed" and document["status"] == "ok" for document in collection["documents"])
    feed_requests = sum(document["category"] == "feed" for document in collection["documents"])
    x_status = json.loads((EDITION / "x_status.json").read_text())
    freshness = Counter()
    urls = set()
    collected_at = datetime.fromisoformat(collection["collected_at"])
    for article in collection["articles"]:
        if article["url"] in urls:
            freshness["duplicate_url"] += 1
            continue
        urls.add(article["url"])
        try:
            published = datetime.fromisoformat(article["published"])
            if not published.tzinfo:
                freshness["missing_date"] += 1
            elif published > collected_at:
                freshness["future_date"] += 1
            else:
                freshness["within_24h" if collected_at-published <= timedelta(hours=24) else "older_than_24h"] += 1
        except (ValueError, TypeError):
            freshness["missing_date"] += 1
    page_counts = {page["id"]:prose_count(page) for page in editorial["pages"]}
    previous = json.loads((ROOT / "data/editions/2026-11-19-sample-02/provenance.json").read_text())
    stats = {"edition":collection["edition"], "collected_at":collection["collected_at"], "pages":6, "sections":4,
             "feed_sources_requested":feed_requests, "feed_sources_ok":feed_success, "rss_candidates":len(collection["articles"]),
             "fetch_requests":len(collection["documents"]), "fetch_success":sum(document["status"]=="ok" for document in collection["documents"]),
             "source_types_adopted":dict(source_types), "source_records_adopted":len(adopted), "source_domains_adopted":len({urlparse(sources[identifier]["url"]).netloc for identifier in adopted}),
             "market_instruments":len(quotes), "original_market_field_values":6*len(quotes), "computed_market_values":2*len(quotes),
             "market_comparisons_pp":{key:float(value) for key,value in replacements.items()},
             "llm_evidence_excerpts":len(evidence), "llm_content_blocks":len(blocks), "llm_paragraphs":sum(len(block["paragraphs"]) for block in blocks),
             "llm_nonwhitespace_characters":sum(page_counts.values()), "characters_by_page":page_counts, "previous_llm_characters":previous["llm_editorial_nonwhitespace_characters"],
             "content_growth_ratio":round(sum(page_counts.values())/previous["llm_editorial_nonwhitespace_characters"],3),
             "blocks_by_kind":dict(Counter(block["kind"] for block in blocks)), "rss_time_accounting":dict(freshness),
             "artwork":{**artwork,"sha256":hashlib.sha256(image_bytes).hexdigest(),"bytes":len(image_bytes)},
             "poem_origin":"public_domain_original_text_from_Wikisource_not_LLM_composed", "x_status":x_status,
             "writer":"GPT-6（本次会话）", "independent_reviewer_agent":False,
             "source_records":[{key:value for key,value in sources[identifier].items() if key not in ("text","items")} for identifier in sorted(adopted)],
             "story_provenance":[{"id":block["id"],"kind":block["kind"],"sources":block["source_ids"],"evidence":block.get("evidence",[])} for block in blocks],
             "fetch_failures":[document for document in collection["documents"] if document["status"] != "ok"]}
    if stats["content_growth_ratio"] < 1.8:
        raise ValueError("Expanded edition does not meet the content growth target")
    (EDITION / "editorial.json").write_text(json.dumps(editorial,ensure_ascii=False,indent=2))
    (EDITION / "provenance.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    page_html = {}
    for page_number,page in enumerate(editorial["pages"],1):
        hero = f'<p class="eyebrow">{escape(page["kicker"])}</p><h1 class="headline">{escape(page["headline"]).replace(chr(10),"<br>")}</h1><p class="deck">{escape(page["deck"])}</p>'
        header = '<div class="masthead"><div><h2>赛博日报</h2><div class="latin">CYBER DAILY</div></div><div class="motto">每天看见世界<br>也给自己留一页。</div></div>' if page_number==1 else f'<div class="section-mark"><strong>{page["label"]}</strong><span>{page["english"]}</span></div>'
        inserts = ""
        extras = ""
        if page["id"] == "politics":
            inserts = '<div class="diplomacy"><div><b>北京</b><span>本报观察：组织对话的空间</span></div><div><b>华盛顿</b><span>本报观察：试探交易的条件</span></div><div><b>莫斯科</b><span>本报观察：打开谈判的通道</span></div></div>'
        if page["id"] == "finance":
            quote = quotes["usNVDA"]
            hero = f'<div class="hero"><div>{hero}</div><div class="hero-figure"><b>{percentage(quote["computed_pct"])}</b><span>NVDA · 11/18常规收盘<br>接口价 ${quote["last"]:.2f}</span></div></div>'
            inserts = '<div class="market-grid">'+"".join(f'<div class="market-card" data-origin="program-market"><span>{quote["label"]}<small>{escape(quote_time(quote))}</small></span><div><strong>{quote["last"]:,.2f}</strong><b class="{change_class(quote["computed_pct"])}">{percentage(quote["computed_pct"])}</b></div></div>' for quote in quotes.values() if quote["group"]=="index")+'</div><p class="quote-ref">腾讯行情快照。美股为11/18，A股及港股为11/19接口值；报价时标逐项保留。红涨绿跌。不同市场的时间分开读。</p>'
            extras = '<div class="market-tables"><div><h3 class="table-title">行业温度 · ETF样本</h3><div class="table-caption">四个方向的代理标的，保留实际报价时标。</div>'+quote_table([quote for quote in quotes.values() if quote["group"]=="sector_etf"])+"</div></div>"
        if page["id"] == "finance-stocks":
            inserts = '<div class="market-tables"><div><h3 class="table-title">演示观察名单</h3><div class="table-caption">5只演示股票，尚未录入你的真实自选。价格分别使用美股和港股对应时段。</div>'+quote_table([quote for quote in quotes.values() if quote["group"]=="watchlist_demo"])+"</div></div>"
        if page["id"] == "technology":
            inserts = '<div class="system-diagram"><div><b>01 / FIND</b>找到已有计算<span>查前缀、查缓存</span></div><i>→</i><div><b>02 / REUSE</b>在机器之间分享<span>用传输换重算</span></div><i>→</i><div><b>03 / COMPUTE</b>只补缺失部分<span>对照时延再看吞吐</span></div></div>'
            extras = '<div class="paper-grid">'+"".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="paper")+'</div><p class="reading-level">论文读到摘要；代码动态来自官方Release Feed。回看材料已标日期。</p>'
        if page["id"] == "culture":
            inserts = f'<div class="art-hero"><figure class="artwork"><img id="art-open" tabindex="0" role="button" aria-label="放大查看梵高原作" src="{image_url}" alt="梵高《盛开的栗树》，蓝天、绿色树冠和浅色道路"><figcaption>{escape(artwork["caption"])}<br><a href="{escape(sources["c_lot"]["url"])}" target="_blank" rel="noopener noreferrer">苏富比拍品档案 ↗</a> · 点画可放大</figcaption></figure><div><div class="poem-card"><p class="eyebrow">一诗短读 / PUBLIC DOMAIN</p><h3>{poem["title"]}</h3><p class="author">{poem["author"]}</p><blockquote>'+"<br>".join(poem["lines"])+f'</blockquote><p class="poem-note">{escape(poem["rights"])}<br><a href="{escape(sources["c_poem"]["url"])}" target="_blank" rel="noopener noreferrer">原文出处 ↗</a></p></div><p class="art-caption-note">今天的读法：先看画的道路怎样带动视线，再读诗里的声音如何把人带进山中。两种作品，都可以从一个细节慢慢进入。</p></div></div>'
        mains = "".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="main")
        sidebar = "".join(render_block(block,replacements,sources) for block in page["blocks"] if block["placement"]=="sidebar")
        features = "".join('<div class="feature">'+render_block(block,replacements,sources)+"</div>" for block in page["blocks"] if block["placement"]=="feature")
        page_html[page["id"]] = f'<section class="page {page["section"]}" id="page-{page_number}" aria-label="第{page_number}版 {page["label"]}"><div class="topline"><span>赛博日报 / 六版扩刊</span><span>{page["english"]}</span><span>2026年11月19日 · 周四</span></div>'+header+hero+f'<div class="byline">本报编辑部 · GPT-6试写 / 新闻抓取 {collected_at:%H:%M} 北京时间 / 行情以表内时标为准</div>'+inserts+f'<div class="body-grid"><div><div class="main-columns">{mains}</div>{features}</div><aside class="sidebar">{sidebar}</aside></div>'+extras+f'<footer class="page-footer"><span>CYBER DAILY · {escape(page["label"])}</span><span>来源与文字分工见账单</span><span class="folio">0{page_number}</span></footer></section>'
    spreads_html = []
    offset = 0
    tabs = []
    for index,spread in enumerate(editorial["spreads"]):
        page_range = f'{offset+1}—{offset+len(spread["pages"])}' if len(spread["pages"])>1 else str(offset+1)
        caption = spread["label"]+' · 第'+page_range+'版'
        spreads_html.append(f'<div class="spread {"pair" if len(spread["pages"])>1 else "single"}" id="spread-{index}" data-caption="{caption}"'+(" hidden" if index else "")+'>'+"".join(page_html[identifier] for identifier in spread["pages"])+"</div>")
        tabs.append(f'<button role="tab" data-spread="{index}" aria-controls="spread-{index}" aria-selected="{str(index==0).lower()}">{spread["label"]} {page_range}</button>')
        offset += len(spread["pages"])
    source_details = "".join(f'<details><summary>{escape(sources[identifier]["title"])} · {sources[identifier]["category"]}</summary><p><a href="{escape(sources[identifier]["url"])}" target="_blank" rel="noopener noreferrer">打开来源</a><br>抓取：{escape(sources[identifier]["fetched_at"])}<br><code>{escape(sources[identifier].get("raw_path",""))}</code></p></details>' for identifier in sorted(adopted))
    audit = f'''<dialog id="audit" aria-labelledby="audit-title"><button id="audit-close" class="close" autofocus>关闭 ×</button><h2 id="audit-title">来源账单 · 六版扩刊</h2><p>时政2版、财经2版、科技1版、艺文1版。程序抓取和计算，GPT-6在本次会话选题、阅读、撰稿；没有独立审稿agent。</p><div class="audit-stats"><div><b>{feed_success}/{feed_requests}</b><span>RSS入口实测可用</span></div><div><b>{len(collection["articles"])}</b><span>RSS候选条目</span></div><div><b>{len(adopted)}</b><span>实际采用来源记录</span></div><div><b>{stats["content_growth_ratio"]:.2f}×</b><span>相对上一版稿件字符量</span></div></div><table><thead><tr><th>项目</th><th>数量</th><th>程序与LLM分工</th></tr></thead><tbody><tr><td>行情</td><td>18标的／108个原始字段</td><td>程序读接口；36个单标的派生值、2个相对表现比较由程序计算。</td></tr><tr><td>稿件</td><td>{len(blocks)}块／{stats["llm_paragraphs"]}段／{stats["llm_nonwhitespace_characters"]}字符</td><td>标题、导语、报道转述、分析由GPT写；行情占位符由程序填数。</td></tr><tr><td>事实摘录</td><td>{len(evidence)}项，另有RSS快讯</td><td>LLM挑选摘录；程序查片段存在。并不等同于自动语义核实。</td></tr><tr><td>原作图片</td><td>1张，{len(image_bytes):,}字节</td><td>程序下载苏富比公开图片并内嵌，未使用AI重绘。</td></tr><tr><td>古诗</td><td>王维原文1首</td><td>公版原文从来源核对，非LLM创作；鉴赏由LLM撰写。</td></tr><tr><td>X</td><td>真实采集{len(x_status["posts"])}条</td><td>适配器和查询配置已写，当前状态{escape(x_status["status"])}。未提供Token，未发付费请求。</td></tr></tbody></table><h3>本次扩源</h3><p>RSS入口由21个扩至{feed_requests}个，成功{feed_success}个。增加央行、中文财经、国际新闻、arXiv、vLLM/Ascend发布、Hugging Face与研究博客。配置数量、抓取成功数量与采用数量分别统计；采用来源类型为{escape(json.dumps(dict(source_types),ensure_ascii=False))}，涉及{stats["source_domains_adopted"]}个域名。</p><p class="source-status">X接入：官方近期搜索接口及离线JSON导入均已实现，当前未启用。X API按量计费；需要开发者Token及额度，配置启用后才可实时抓取。<a href="https://docs.x.com/x-api/getting-started/pricing" target="_blank" rel="noopener noreferrer">官方说明 ↗</a></p><h3>采用来源</h3>{source_details}<h3>失败入口</h3><p>{escape('；'.join(document['id']+': '+document['error'] for document in stats['fetch_failures']))}</p><h3>原始记录</h3><p>data/editions/2026-11-19-sample-03：collection.json、editorial.json、provenance.json、raw/。候选时间统计：{escape(json.dumps(dict(freshness),ensure_ascii=False))}。旧通稿和论文回看已在稿内注明。</p></dialog>'''
    art_modal = f'<dialog class="art-modal" id="art-view" aria-label="梵高原作放大图"><button id="art-close" class="close">关闭 ×</button><img src="{image_url}" alt="梵高《盛开的栗树》完整作品"><p>{escape(artwork["caption"])}</p></dialog>'
    html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赛博日报 · 六版扩刊 · 2026-11-19</title><style>'+CSS+SPREAD_CSS+'</style></head><body><header class="reader"><span class="brand">赛博日报 / 六版扩刊</span><nav role="tablist" aria-label="栏目">'+"".join(tabs)+'</nav><div class="reader-actions"><button id="layout-toggle" class="layout-control" aria-pressed="false">纵向阅读</button><button id="audit-open">来源账单 ↗</button></div></header><main class="edition">'+"".join(spreads_html)+'<div class="bottom-nav"><button id="previous">← 上一栏目</button><span id="position"></span><button id="next">下一栏目 →</button></div></main>'+audit+art_modal+'<script>'+JS+'</script></body></html>'
    OUTPUT.write_text(html,encoding="utf-8")
    report = f'''# 六版扩刊：来源与生成分工

成品：`{OUTPUT.name}`。新闻抓取完成：{collection['collected_at']}；报价时间逐项保留。

| 指标 | 上一版 | 本版 |
|---|---:|---:|
| RSS入口 | 21 | {feed_requests} |
| RSS实际成功 | 20 | {feed_success} |
| RSS候选 | 775 | {len(collection['articles'])} |
| 实际采用来源记录 | 14 | {len(adopted)} |
| 物理版面 | 4 | 6（时政2、财经2、科技1、艺文1） |
| LLM稿件字符 | {previous['llm_editorial_nonwhitespace_characters']} | {stats['llm_nonwhitespace_characters']}（{stats['content_growth_ratio']:.2f}倍） |

本版{len(blocks)}个稿件块、{stats['llm_paragraphs']}个段落；事实摘录{len(evidence)}项。程序取18个行情标的、108个原始字段，重算36个单标的值与2个比较值。稿件由会话内GPT-6选题、摘录与撰写；没有独立审稿agent。

来源类型：{json.dumps(dict(source_types),ensure_ascii=False)}。来源记录数不是独立媒体数，同一媒体不同文章分别记为记录。RSS候选时间统计：{json.dumps(dict(freshness),ensure_ascii=False)}。

## 图片与古诗

梵高《盛开的栗树》直接取苏富比拍品档案公开图片，{len(image_bytes)}字节，SHA-256：`{stats['artwork']['sha256']}`，内嵌HTML。没有用SVG代替原作或AI重绘。王维《山居秋暝》采用维基文库公版原文，逐行核对；原文不计入LLM撰稿字符。艺术鉴赏、哲思与诗歌解读由LLM创作。

## X的实际状态

{x_status['status']}，真实帖子{len(x_status['posts'])}条，API请求{x_status['requests']}次。`pipeline/x_collect.py`支持官方API近期搜索和官方JSON导入，`config/x_sources.json`存查询与请求上限。需X开发者Bearer Token与可用额度；默认关闭，未发付费请求。API来源：https://docs.x.com/x-api/posts/search/introduction 。计费来源：https://docs.x.com/x-api/getting-started/pricing 。

## 可重现命令

```bash
python3 pipeline/sample_collect.py --edition 2026-11-19-sample-03
python3 pipeline/x_collect.py --out data/editions/2026-11-19-sample-03/x_status.json
python3 pipeline/render_expanded.py
node pipeline/preview_sample.mjs --edition 2026-11-19-sample-03
```

`editorial_changes.json`在前版原始稿件上扩写；渲染器输出完整`editorial.json`、`provenance.json`和单文件HTML。离线重渲染不访问网络。
'''
    (EDITION / "PROVENANCE.md").write_text(report,encoding="utf-8")
    print(json.dumps({key:value for key,value in stats.items() if key not in ("source_records","story_provenance","artwork","fetch_failures","x_status")},ensure_ascii=False,indent=2))
    print(OUTPUT)


if __name__ == "__main__":
    main()
