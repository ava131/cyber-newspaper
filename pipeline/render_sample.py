import html
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
EDITION = ROOT / "data/editions/2026-11-19-sample-02"
OUTPUT = ROOT / "cyber-daily-2026-11-19-sample-02.html"
KINDS = {"report": "报道", "analysis": "本报观察", "speculation": "大胆推演 · 未证实", "humor": "编辑闲笔"}

CSS = """
:root{--paper:#f4efdf;--ink:#24231f;--muted:#6d6b60;--line:#c6bda7;--accent:#8b312b;--sans:'PingFang SC','Helvetica Neue',sans-serif;--serif:'Songti SC','STSong','Noto Serif CJK SC',serif}
*{box-sizing:border-box}body{margin:0;background:#302f2b;color:var(--ink);font-family:var(--serif);-webkit-font-smoothing:antialiased}button,a{-webkit-tap-highlight-color:transparent}button{font:inherit;cursor:pointer}a{color:inherit;text-underline-offset:4px}button:focus-visible,a:focus-visible{outline:2px solid #bd682d;outline-offset:4px}
.reader{position:sticky;top:0;z-index:20;background:#24241f;color:#e9e3d3;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:14px max(24px,calc((100vw - 1176px)/2));font:12px var(--sans);border-bottom:1px solid #575449}.brand{letter-spacing:.2em;white-space:nowrap}.reader nav{display:flex;gap:5px}.reader button{border:1px solid transparent;background:none;color:inherit;padding:8px 13px;font-size:12px}.reader nav button[aria-selected=true]{background:#ece6d6;color:#24241f}.reader .audit-button{border-color:#6b6759;white-space:nowrap}.edition{width:min(1220px,calc(100% - 48px));margin:28px auto 0}.page{background:var(--paper);padding:38px 46px 28px;box-shadow:0 12px 50px #0004;min-height:1460px;position:relative}.page[hidden]{display:none}.topline{display:flex;justify-content:space-between;gap:20px;font:10px var(--sans);letter-spacing:.13em;padding-bottom:14px;border-bottom:1px solid var(--ink)}.masthead{display:flex;align-items:center;justify-content:space-between;border-bottom:5px double var(--ink);padding:20px 0 17px;margin-bottom:25px}.masthead h2{font-size:85px;letter-spacing:.12em;margin:0;line-height:1.1}.masthead .latin{font-family:Didot,Georgia,serif;font-size:28px;letter-spacing:.07em}.masthead .motto{font-size:12px;line-height:2.1;text-align:right;color:var(--muted)}.section-mark{display:flex;align-items:center;justify-content:space-between;padding:23px 0;border-bottom:4px double var(--ink);margin-bottom:25px}.section-mark strong{font-size:34px;letter-spacing:.12em}.section-mark span{font:13px Georgia,serif;letter-spacing:.2em}.eyebrow{font:11px var(--sans);letter-spacing:.18em;color:var(--accent);margin:0 0 14px}.headline{font-size:64px;line-height:1.13;letter-spacing:-.035em;margin:0 0 22px;max-width:1000px}.deck{font-size:20px;line-height:1.7;max-width:930px;margin:0 0 17px;color:#4c4a40}.byline{font:10px var(--sans);color:var(--muted);letter-spacing:.05em;margin-bottom:25px}.body-grid{display:grid;grid-template-columns:minmax(0,1fr) 255px;gap:30px;border-top:2px solid var(--ink);padding-top:24px}.main-columns{display:grid;grid-template-columns:1fr 1fr;gap:25px;align-items:start}.story{break-inside:avoid;margin-bottom:23px}.story .tag{font:9px var(--sans);color:var(--muted);letter-spacing:.16em;margin:0 0 8px}.story h3{font-size:21px;line-height:1.45;margin:0 0 10px}.story p{font-size:16px;line-height:1.95;text-align:justify;margin:0 0 13px;overflow-wrap:anywhere}.story.main:first-child{grid-column:1/-1;border-bottom:1px solid var(--line);padding-bottom:10px}.story.main:first-child .paragraphs{columns:2;column-gap:25px}.sidebar{border-left:1px solid var(--line);padding-left:22px}.sidebar .story{padding-bottom:17px;border-bottom:1px solid var(--line)}.sidebar .story h3{font-size:19px}.sidebar .story p{font-size:14px;line-height:1.85}.source-links{display:flex;flex-wrap:wrap;gap:8px;font:10px var(--sans);color:var(--muted);line-height:1.6}.feature{margin-top:20px;border:1px solid var(--ink);padding:20px 24px;background:#e9e2ce}.feature .story{margin:0}.feature h3{font-size:22px}.feature p{font-size:16px;line-height:1.9;margin-bottom:0}.feature .tag{color:var(--accent)}.page-footer{display:flex;justify-content:space-between;gap:15px;margin-top:30px;border-top:3px double var(--ink);padding-top:13px;font:10px var(--sans);letter-spacing:.08em;color:var(--muted)}.folio{font:23px Georgia,serif;color:var(--ink)}.bottom-nav{display:flex;align-items:center;justify-content:space-between;color:#dfd7c5;font:12px var(--sans);padding:23px 0 35px}.bottom-nav button{background:transparent;border:1px solid #77705e;color:inherit;padding:10px 20px}.bottom-nav button:disabled{opacity:.3;cursor:default}.quote-ref{font:10px var(--sans);color:var(--muted);margin:12px 0 20px;line-height:1.8}.politics .headline{max-width:1000px}.diplomacy{display:grid;grid-template-columns:1fr 1fr 1fr;margin:22px 0 25px;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:17px 0;gap:15px}.diplomacy div{border-right:1px solid var(--line);padding:0 15px}.diplomacy div:last-child{border:0}.diplomacy b{font-size:29px;letter-spacing:.08em}.diplomacy span{display:block;font:11px var(--sans);margin-top:9px;color:var(--muted)}
.finance{--accent:#903a2c}.finance .hero{background:#24241f;color:#f7f0dd;padding:27px 30px 25px;margin-bottom:22px;display:grid;grid-template-columns:1fr auto;gap:25px;align-items:center}.finance .hero .eyebrow{color:#bfb49b}.finance .headline{font-size:58px;margin-bottom:15px}.finance .deck{color:#d3cbb8;font-size:16px;max-width:700px}.hero-figure{text-align:right;border-left:1px solid #77705f;padding-left:28px}.hero-figure b{display:block;font:64px Georgia,serif;color:#b6c8b7}.hero-figure span{font:11px var(--sans);line-height:1.7;display:block}.market-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0 22px;margin-bottom:12px}.market-card{display:flex;justify-content:space-between;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);padding:11px 0;font:12px var(--sans)}.market-card strong{font:18px Georgia,serif}.market-card small{font-size:10px;color:var(--muted);display:block;margin-top:4px}.positive{color:#a43c2e}.negative{color:#366850}.flat{color:var(--muted)}.market-tables{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:26px;padding-top:20px;border-top:2px solid var(--ink)}.table-title{font-size:20px;margin:0 0 8px}.table-caption{font:10px var(--sans);color:var(--muted);line-height:1.8;margin-bottom:9px}table{width:100%;border-collapse:collapse;font:12px var(--sans)}th,td{padding:11px 4px;text-align:right;border-bottom:1px solid var(--line)}th{font-weight:400;color:var(--muted);font-size:10px}th:first-child,td:first-child{text-align:left}.symbol{font-size:10px;color:var(--muted);display:block;margin-top:3px}.finance .body-grid{grid-template-columns:1fr 255px}.finance .feature{background:#25251f;color:#eee6d2;border:0}.finance .feature .tag{color:#c8ba94}.finance .feature .source-links{color:#d0c6b0}.finance .main-columns .story h3{font-size:20px}
.technology{--accent:#315d66}.technology .eyebrow{color:#315d66}.technology .headline{font-size:62px}.system-diagram{display:grid;grid-template-columns:1fr 36px 1fr 36px 1fr;align-items:center;gap:12px;padding:23px 24px;background:#e3e8df;border:1px solid #9eafa6;margin:24px 0}.system-diagram div{font-size:18px;line-height:1.55}.system-diagram b{display:block;font:10px var(--sans);color:#53736b;margin-bottom:10px}.system-diagram span{font:11px var(--sans);color:#51615c;display:block;margin-top:8px}.system-diagram i{font-style:normal;font-size:25px;color:#5c7970}.paper-grid{display:grid;grid-template-columns:1fr 1fr;gap:25px;margin-top:25px;padding-top:22px;border-top:2px solid var(--ink)}.paper-grid .story{border:1px solid #a6b4a9;padding:20px;background:#e9ebdf;margin:0}.paper-grid .story h3{font-size:20px}.paper-grid .story p{font-size:15px}.reading-level{font:10px var(--sans);color:#547264;margin-top:13px}
.miscellany{--accent:#9d5c29}.miscellany .headline{font-size:70px}.art-strip{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:22px;margin:25px 0 28px;padding:23px 0;border-top:2px solid var(--ink);border-bottom:1px solid var(--ink);align-items:center}.art-strip strong{display:block;font:58px Didot,Georgia,serif;color:#8b4f28}.art-strip span{font:11px var(--sans);line-height:1.8}.tree-art{margin:22px 0;text-align:center}.tree-art svg{width:100%;height:230px;display:block}.tree-art small{display:block;font:10px var(--sans);color:var(--muted);margin-top:14px}.miscellany .feature{background:#e7dac1}.miscellany .feature h3{font-style:italic}.miscellany .body-grid{padding-top:28px}.miscellany .main-columns{grid-template-columns:1fr 1fr}
dialog{border:1px solid #8a816c;background:#f5f0e2;color:#24231f;width:min(1050px,calc(100% - 32px));max-height:88vh;padding:30px;font-family:var(--sans);box-shadow:0 15px 80px #0007}dialog::backdrop{background:#111b}dialog h2{font:30px var(--serif);margin:0 0 18px}dialog h3{font:21px var(--serif);margin:28px 0 13px}dialog p{font-size:13px;line-height:1.9}dialog .close{float:right;border:1px solid #a89b80;background:none;padding:7px 13px}dialog table{font-size:12px}dialog th,dialog td{text-align:left;vertical-align:top;line-height:1.7}dialog details{border-bottom:1px solid #d1c5ae;padding:12px 0;font-size:12px;line-height:1.8}dialog summary{cursor:pointer}dialog code{font-size:11px;word-break:break-all}.audit-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}.audit-stats div{border:1px solid #cfc2a6;padding:16px}.audit-stats b{display:block;font:32px Georgia,serif}.audit-stats span{font-size:11px;line-height:1.8}.evidence-row{padding:10px 0;border-bottom:1px solid #e0d4bd;font-size:12px;line-height:1.8}
@media(max-width:900px){.reader{padding:10px 14px;gap:8px}.brand{font-size:10px}.reader button{padding:8px 10px}.edition{width:calc(100% - 24px);margin-top:12px}.page{padding:28px 28px;min-height:0}.masthead h2{font-size:62px}.masthead .latin{font-size:20px}.body-grid,.finance .body-grid{grid-template-columns:minmax(0,1fr) 210px;gap:22px}.headline,.technology .headline{font-size:51px}.finance .headline{font-size:46px}.hero-figure b{font-size:44px}.finance .hero{padding:24px 22px}.story p{font-size:15px}.main-columns{gap:20px}.market-grid{gap:0 16px}.market-card{display:block}.market-card strong{margin-right:12px}.market-card>span{display:block;margin-bottom:5px}}
@media(max-width:650px){.reader{flex-wrap:wrap;padding:9px 12px;gap:4px}.brand{margin-right:auto}.reader nav{order:3;width:100%;justify-content:space-between;margin-top:5px}.reader nav button{flex:1}.reader .audit-button{font-size:10px;padding:6px 10px}.edition{width:100%;margin:0}.page{padding:24px 20px}.topline{font-size:9px;letter-spacing:0;gap:12px}.topline span:nth-child(2){display:none}.masthead{padding-top:20px}.masthead h2{font-size:49px;letter-spacing:.07em}.masthead .latin{font-size:15px}.masthead .motto{display:none}.headline,.technology .headline,.miscellany .headline{font-size:40px;line-height:1.2}.finance .headline{font-size:38px}.deck{font-size:17px}.body-grid,.finance .body-grid{display:block}.main-columns,.miscellany .main-columns{display:block}.story.main:first-child .paragraphs{columns:1}.story h3{font-size:22px}.story p{font-size:17px;line-height:1.9}.sidebar{border-left:0;border-top:2px solid var(--ink);padding:22px 0 0;margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:22px}.sidebar .story h3{font-size:18px}.sidebar .story p{font-size:14px}.feature{padding:20px}.diplomacy{gap:0}.diplomacy div{padding:0 10px}.diplomacy b{font-size:22px}.diplomacy span{font-size:9px;line-height:1.7}.finance .hero{display:block;padding:24px 18px;margin-left:-20px;margin-right:-20px}.hero-figure{padding:16px 0 0;border-left:0;border-top:1px solid #77705f;text-align:left;display:flex;align-items:center;gap:16px}.hero-figure b{font-size:43px}.finance .deck{font-size:16px}.market-grid{grid-template-columns:repeat(2,1fr);gap:0 18px}.market-card strong{font-size:17px}.market-tables,.paper-grid{display:block}.market-tables>div+div,.paper-grid .story+.story{margin-top:24px}.system-diagram{grid-template-columns:1fr;gap:10px;padding:20px}.system-diagram i{transform:rotate(90deg);width:22px;text-align:center}.system-diagram div{font-size:18px}.system-diagram b,.system-diagram span{margin:5px 0}.art-strip{grid-template-columns:1fr 1fr;gap:20px}.art-strip>div:first-child{grid-column:1/-1}.art-strip strong{font-size:45px}.section-mark strong{font-size:28px}.section-mark span{font-size:10px;letter-spacing:.08em}.page-footer{font-size:9px;line-height:1.8}.bottom-nav{padding:20px}.bottom-nav span{font-size:10px}dialog{padding:22px 18px}dialog h2{font-size:25px}.audit-stats{grid-template-columns:1fr 1fr}.audit-stats b{font-size:27px}dialog table{font-size:10px}dialog td{padding:10px 5px}}
@media print{@page{size:A4;margin:12mm}body{background:white}.reader,.bottom-nav,dialog{display:none!important}.edition{width:100%;margin:0}.page,.page[hidden]{display:block!important;box-shadow:none;min-height:0;padding:0;background:white;break-after:page}.page:last-child{break-after:auto}.masthead h2{font-size:50px}.headline,.technology .headline,.miscellany .headline{font-size:40px}.finance .headline{font-size:38px}.deck{font-size:14px}.story p{font-size:11px;line-height:1.65}.story h3{font-size:16px}.sidebar .story p{font-size:10px}.body-grid,.finance .body-grid{grid-template-columns:1fr 170px;gap:18px}.main-columns{gap:16px}.sidebar{padding-left:15px}.page-footer{font-size:8px}.market-card{font-size:9px;padding:6px 0}.market-card strong{font-size:13px}.market-card small{font-size:8px}.hero-figure b{font-size:44px}.finance .hero{print-color-adjust:exact;-webkit-print-color-adjust:exact}.paper-grid .story{padding:12px}.paper-grid .story p{font-size:10px}.system-diagram{padding:12px}.system-diagram div{font-size:14px}.art-strip strong{font-size:40px}.tree-art svg{height:150px}.feature p{font-size:12px}table{font-size:9px}td,th{padding:6px 3px}a{text-decoration:none}}
"""

JS = """
const pages=Array.from(document.querySelectorAll('.page'));
const tabs=Array.from(document.querySelectorAll('[data-page]'));
const previous=document.querySelector('#previous');
const next=document.querySelector('#next');
const audit=document.querySelector('#audit');
let active=0;
function showPage(index,scroll=true){
  active=Math.max(0,Math.min(pages.length-1,index));
  pages.forEach((page,position)=>page.hidden=position!==active);
  tabs.forEach((tab,position)=>tab.setAttribute('aria-selected',String(position===active)));
  previous.disabled=active===0;
  next.disabled=active===pages.length-1;
  document.querySelector('#position').textContent=`第 ${active+1} 版 / 共 ${pages.length} 版`;
  history.replaceState(null,'','#'+(active+1));
  if(scroll)window.scrollTo(0,0);
}
tabs.forEach((tab,index)=>tab.addEventListener('click',()=>showPage(index)));
previous.addEventListener('click',()=>showPage(active-1));
next.addEventListener('click',()=>showPage(active+1));
document.querySelector('#audit-open').addEventListener('click',()=>audit.showModal());
document.querySelector('#audit-close').addEventListener('click',()=>audit.close());
document.addEventListener('keydown',event=>{
  if(audit.open || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName))return;
  if(event.key==='ArrowRight'){event.preventDefault();showPage(active+1)}
  if(event.key==='ArrowLeft'){event.preventDefault();showPage(active-1)}
  if(event.key==='Home'&&event.ctrlKey)showPage(0);
});
showPage((Number(location.hash.slice(1))||1)-1,false);
"""


def escape(value):
    return html.escape(str(value), quote=True)


def change_class(value):
    return "positive" if value > 0 else "negative" if value < 0 else "flat"


def percentage(value):
    return f"{value:+.2f}%"


def source_links(identifiers, sources):
    return '<div class="source-links">' + "".join(
        f'<a href="{escape(sources[identifier]["url"])}" target="_blank" rel="noopener noreferrer">↗ {escape(sources[identifier]["short_title"])}</a>'
        for identifier in sorted(set(identifiers))) + "</div>"


def render_block(block, replacements, sources):
    paragraphs = []
    placement_class = "main" if block["placement"] == "main" else "slot-" + block["placement"]
    for paragraph in block["paragraphs"]:
        for key, value in replacements.items():
            paragraph = paragraph.replace("{{" + key + "}}", value)
        if "{{" in paragraph:
            raise ValueError(f"Unresolved value in {block['id']}")
        paragraphs.append(f"<p>{escape(paragraph)}</p>")
    return (f'<article class="story {placement_class}" data-story="{block["id"]}" data-author="llm" data-kind="{block["kind"]}">'
            f'<div class="tag">{KINDS[block["kind"]]}</div><h3>{escape(block["title"])}</h3>'
            f'<div class="paragraphs">{"".join(paragraphs)}</div>'
            + source_links(block["source_ids"], sources) + "</article>")


def quote_time(quote):
    raw_time = quote["provider_time"]
    if re.fullmatch(r"\d{14}", raw_time):
        return datetime.strptime(raw_time, "%Y%m%d%H%M%S").strftime("%m/%d %H:%M") + " 北京"
    if quote["code"].startswith("us"):
        return raw_time[5:16] + " 接口美东时标"
    return raw_time[5:16] + " 香港"


def quote_table(quotes):
    rows = "".join(
        f'<tr data-origin="program-market" data-code="{quote["code"]}"><td>{escape(quote["label"])}'
        f'<span class="symbol">{escape(quote.get("symbol",quote["code"]))}</span></td>'
        f'<td>{quote["last"]:,.3f}</td><td class="{change_class(quote["computed_pct"])}">{percentage(quote["computed_pct"])}</td>'
        f'<td style="font-size:9px">{escape(quote_time(quote))}</td></tr>' for quote in quotes)
    return '<table><thead><tr><th>标的</th><th>接口现价</th><th>较昨收</th><th>报价时标</th></tr></thead><tbody>' + rows + "</tbody></table>"


def main():
    collection = json.loads((EDITION / "collection.json").read_text())
    editorial = json.loads((EDITION / "editorial.json").read_text())
    documents = {document["id"]: document for document in collection["documents"]}
    sources = {identifier: {**document, "short_title": document["title"].split("：")[0]} for identifier, document in documents.items() if document["status"] == "ok"}
    evidence = {entry["id"]: entry for entry in editorial["evidence"]}
    for entry in evidence.values():
        if entry["quote"] not in sources[entry["source"]]["text"]:
            raise ValueError(f"Evidence excerpt absent: {entry['id']}")
    quotes = {quote["code"]: quote for quote in collection["quotes"]}
    missing = set(collection["requested_instruments"]) - set(quotes)
    if missing:
        raise ValueError(f"Missing quote instruments: {missing}")
    for quote in quotes.values():
        if abs(quote["provider_pct"] - quote["computed_pct"]) > 0.011:
            raise ValueError(f"Inconsistent market percentage: {quote['code']}")
    replacements = {
        "nvda_gap": f'{quotes["us.IXIC"]["computed_pct"] - quotes["usNVDA"]["computed_pct"]:.2f}',
        "a_gap": f'{quotes["sh000688"]["computed_pct"] - quotes["sz399006"]["computed_pct"]:.2f}',
    }
    art_sale = editorial["numeric_inputs"]["art_sale_usd_millions"]["value"]
    art_previous = editorial["numeric_inputs"]["art_previous_record_usd_millions"]["value"]
    art_growth = (art_sale / art_previous - 1) * 100
    blocks = []
    adopted_sources = {"market_quotes"}
    for page in editorial["pages"]:
        for block in page["blocks"]:
            identifiers = {evidence[identifier]["source"] for identifier in block.get("evidence", [])}
            if block.get("rss_title"):
                candidates = [article for article in collection["articles"] if article["title"] == block["rss_title"]]
                if not candidates:
                    raise ValueError(f"RSS item absent: {block['rss_title']}")
                article = candidates[0]
                identifier = "rss_" + str(len(blocks))
                sources[identifier] = {"id": identifier, "title": article["title"], "short_title": sources[article["source_id"]]["title"] + " · RSS摘要",
                                       "url": article["url"], "category": "rss_item", "published": article["published"],
                                       "parent_feed": article["source_id"], "text": article["summary"],
                                       "fetched_at": sources[article["source_id"]]["fetched_at"]}
                identifiers.add(identifier)
            if block.get("quote_codes"):
                if not set(block["quote_codes"]).issubset(quotes):
                    raise ValueError(f"Missing quote reference: {block['id']}")
                identifiers.add("market_quotes")
            block["source_ids"] = sorted(identifiers)
            blocks.append(block)
            adopted_sources.update(identifiers)
    cutoff = datetime.fromisoformat(collection["collected_at"])
    freshness = Counter()
    seen_urls = set()
    for article in collection["articles"]:
        if article["url"] in seen_urls:
            freshness["duplicate_url"] += 1
            continue
        seen_urls.add(article["url"])
        try:
            published = datetime.fromisoformat(article["published"])
            if published.tzinfo is None:
                freshness["missing_or_invalid_date"] += 1
            elif published > cutoff:
                freshness["future_timestamp"] += 1
            elif cutoff - published <= timedelta(hours=24):
                freshness["within_24h"] += 1
            else:
                freshness["older_than_24h"] += 1
        except (TypeError, ValueError):
            freshness["missing_or_invalid_date"] += 1
    prose = []
    for page in editorial["pages"]:
        prose.extend([page["headline"], page["deck"]])
        for block in page["blocks"]:
            prose.extend([block["title"], *block["paragraphs"]])
    prose_chars = sum(len(re.sub(r"\s|\{\{.*?\}\}", "", text)) for text in prose)
    stats = {
        "edition": collection["edition"], "collected_at": collection["collected_at"],
        "fetch_requests": len(documents), "fetch_success": sum(document["status"] == "ok" for document in documents.values()),
        "feed_sources_requested": sum(document["category"] == "feed" for document in documents.values()),
        "feed_sources_ok": sum(document["category"] == "feed" and document["status"] == "ok" for document in documents.values()),
        "rss_candidates": len(collection["articles"]), "rss_time_and_url_accounting": dict(freshness),
        "adopted_source_records": len(adopted_sources), "rss_items_used": sum(sources[identifier]["category"] == "rss_item" for identifier in adopted_sources),
        "market_instruments": len(quotes), "market_groups": dict(Counter(quote["group"] for quote in quotes.values())),
        "original_market_fields_per_instrument": ["provider_name", "last", "previous", "provider_change", "provider_pct", "provider_time"],
        "original_market_field_values": len(quotes) * 6, "computed_per_instrument_values": len(quotes) * 2,
        "computed_comparisons": {"nvda_underperformance_pp": float(replacements["nvda_gap"]), "star50_vs_chinext_pp": float(replacements["a_gap"]), "art_record_increase_pct": round(art_growth, 6)},
        "llm_extracted_evidence_units": len(evidence), "evidence_excerpt_substring_checks_passed": len(evidence),
        "llm_structured_numeric_inputs": editorial["numeric_inputs"],
        "pages": len(editorial["pages"]), "llm_blocks_by_kind": dict(Counter(block["kind"] for block in blocks)),
        "llm_blocks": len(blocks), "llm_paragraphs": sum(len(block["paragraphs"]) for block in blocks),
        "llm_editorial_nonwhitespace_characters": prose_chars, "writer": editorial["writer"],
        "selection": editorial["selection"], "prose_llm_share": "100%（标题、导语、稿件小标题、段落；不含程序表格和界面标签）",
        "failure_records": [document for document in documents.values() if document["status"] != "ok"],
        "automation_limits": "选题、阅读、证据摘录和成稿由会话内LLM完成。证据字符串匹配只证明片段存在，不等于自动完成语义核实。",
        "source_records": [{key: value for key, value in sources[identifier].items() if key not in ("text", "items")} for identifier in sorted(adopted_sources)],
        "story_provenance": [{"id": block["id"], "title": block["title"], "author": "llm", "kind": block["kind"], "sources": block["source_ids"], "evidence": block.get("evidence", []), "quote_codes": block.get("quote_codes", [])} for block in blocks],
    }
    (EDITION / "provenance.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (EDITION / "verified_evidence.json").write_text(json.dumps(editorial["evidence"], ensure_ascii=False, indent=2), encoding="utf-8")
    def block_html(block):
        return render_block(block, replacements, sources)
    pages_html = []
    for page_number, page in enumerate(editorial["pages"], 1):
        hero = (f'<p class="eyebrow">{escape(page["kicker"])}</p><h1 class="headline">{escape(page["headline"]).replace(chr(10),"<br>")}</h1>'
                f'<p class="deck">{escape(page["deck"])}</p>')
        header = ('<div class="masthead"><div><h2>赛博日报</h2><div class="latin">CYBER DAILY</div></div><div class="motto">只有一位读者的报纸<br>把消息读明白，把日子过有趣。</div></div>' if page_number == 1 else f'<div class="section-mark"><strong>{page["label"]}</strong><span>{page["english"]}</span></div>')
        inserts = ""
        extras = ""
        if page["id"] == "politics":
            inserts = '<div class="diplomacy"><div><b>北京</b><span>本报观察：组织对话的空间</span></div><div><b>华盛顿</b><span>本报观察：试探交易的条件</span></div><div><b>莫斯科</b><span>本报观察：打开谈判的通道</span></div></div>'
        if page["id"] == "finance":
            quote = quotes["usNVDA"]
            hero = f'<div class="hero"><div>{hero}</div><div class="hero-figure"><b>{percentage(quote["computed_pct"])}</b><span>NVDA · 11/18美股常规收盘<br>接口价 ${quote["last"]:.2f}</span></div></div>'
            inserts = '<div class="market-grid">' + "".join(
                f'<div class="market-card" data-origin="program-market"><span>{quote["label"]}<small>{escape(quote_time(quote))}</small></span><div><strong>{quote["last"]:,.2f}</strong><b class="{change_class(quote["computed_pct"])}">{percentage(quote["computed_pct"])}</b></div></div>'
                for quote in quotes.values() if quote["group"] == "index") + '</div><div class="quote-ref">腾讯行情快照；A股为11/19收盘后接口值，港股为16:02附近报价，美股为11/18接口值。接口时间不等于最终结算确认；涨跌幅由昨收重新计算。红涨绿跌。</div>'
            extras = '<div class="market-tables"><div><h3 class="table-title">行业温度 · ETF样本</h3><div class="table-caption">展示四个方向的代理标的，并非全市场行业排名。</div>' + quote_table([quote for quote in quotes.values() if quote["group"] == "sector_etf"]) + '</div><div><h3 class="table-title">演示观察名单</h3><div class="table-caption">NVDA / MSFT / GOOGL / 9988.HK / 0700.HK<br>名单可在 config/watchlist.json 替换；尚非用户持仓。</div>' + quote_table([quote for quote in quotes.values() if quote["group"] == "watchlist_demo"]) + '</div></div>'
        if page["id"] == "technology":
            inserts = '<div class="system-diagram" aria-label="共享KV缓存机制示意"><div><b>01 / FIND</b>请求进入引擎<span>先查已有前缀的KV状态</span></div><i>→</i><div><b>02 / REUSE</b>共享缓存池<span>跨机器复用已完成的计算</span></div><i>→</i><div><b>03 / COMPUTE</b>只补缺失部分<span>收益取决于复用率和搬运成本</span></div></div>'
            extras = '<div class="paper-grid">' + "".join(block_html(block) for block in page["blocks"] if block["placement"] == "paper") + '</div><div class="reading-level">论文阅读深度：arXiv摘要；未读实验全文、未跑benchmark。旧论文明确标为回看。</div>'
        if page["id"] == "miscellany":
            inserts = f'<div class="art-strip"><div><strong>$190.4m</strong><span>本次拍卖成交价 · BBC报道</span></div><div><strong>1890</strong><span>这棵栗树开花的年份</span></div><div><strong>+{art_growth:.2f}%</strong><span>较此前拍卖纪录 · 程序计算</span></div></div>'
            extras = '<div class="tree-art"><svg viewBox="0 0 1000 230" role="img" aria-label="装饰性栗树线描，并非梵高原作"><g fill="none" stroke="#8c7651" stroke-width="1.7"><path d="M30 212Q280 193 490 211T970 207M492 213L500 117 467 85M501 172L550 121 575 73M500 145L443 121 420 83M514 159L527 85M483 137L472 59"/><path d="M445 108Q355 105 383 65Q348 22 413 28Q434-6 470 22Q502-10 537 23Q596 10 598 50Q660 75 610 114Q595 149 550 133Q507 150 468 128Q430 151 398 122"/></g><g fill="#c1ad7b"><circle cx="416" cy="48" r="5"/><circle cx="458" cy="36" r="5"/><circle cx="526" cy="42" r="6"/><circle cx="570" cy="64" r="5"/><circle cx="406" cy="90" r="6"/><circle cx="539" cy="102" r="5"/><circle cx="591" cy="94" r="4"/><circle cx="466" cy="88" r="6"/></g></svg><small>本报装饰性SVG线描 · 不是拍卖作品图片</small></div>'
        main_blocks = "".join(block_html(block) for block in page["blocks"] if block["placement"] == "main")
        sidebar = "".join(block_html(block) for block in page["blocks"] if block["placement"] == "sidebar")
        features = "".join('<div class="feature">' + block_html(block) + '</div>' for block in page["blocks"] if block["placement"] == "feature")
        pages_html.append(f'<section class="page {page["id"]}" id="page-{page_number}" aria-label="第{page_number}版：{page["label"]}"'+(" hidden" if page_number > 1 else "")+'>'
                          f'<div class="topline"><span>赛博日报 / CYBER DAILY</span><span>{page["english"]}</span><span>2026年11月19日 · 周四 · 内容试刊</span></div>'
                          + header + hero + '<div class="byline">本报编辑部 · GPT-6试写 / 数据快照 16:17 北京时间 / 来源账单可查</div>' + inserts
                          + f'<div class="body-grid"><div><div class="main-columns">{main_blocks}</div>{features}</div><aside class="sidebar">{sidebar}</aside></div>'
                          + extras + f'<footer class="page-footer"><span>事实来自所列外部信源 · 选题与文字由GPT-6撰写</span><span>CYBER DAILY / {page["english"]}</span><span class="folio">0{page_number}</span></footer></section>')
    source_rows = "".join(f'<details><summary>{escape(sources[identifier]["title"])} · {escape(sources[identifier]["category"])}</summary><p><a target="_blank" rel="noopener noreferrer" href="{escape(sources[identifier]["url"])}">打开来源</a><br>抓取时间：{escape(sources[identifier]["fetched_at"])}<br>原始文件：<code>{escape(sources[identifier].get("raw_path",sources[identifier].get("parent_feed","")))}</code></p></details>' for identifier in sorted(adopted_sources))
    evidence_rows = "".join(f'<div class="evidence-row"><b>{entry["id"]}</b> {escape(entry["claim"])}<br>来源：{escape(sources[entry["source"]]["title"])}</div>' for entry in evidence.values())
    audit = f'''<dialog id="audit" aria-labelledby="audit-title"><button class="close" id="audit-close" autofocus>关闭 ×</button><h2 id="audit-title">这份报纸，是怎么做出来的？</h2>
<p>本版为真实数据的内容试刊。{escape(editorial["selection"])} 所有中文标题、导语、分析和点评均由GPT-6写作；程序负责抓取、解析、计算和排版。数据来源与文字作者是两个维度，不做没有意义的“程序70% / 模型30%”。</p>
<div class="audit-stats"><div><b>{stats["rss_candidates"]}</b><span>程序抓到的RSS候选条目</span></div><div><b>{len(quotes)}</b><span>程序解析的行情标的</span></div><div><b>{len(evidence)}</b><span>LLM摘录的原文证据单元</span></div><div><b>{len(blocks)}</b><span>LLM写作的稿件内容块</span></div></div>
<table><thead><tr><th>内容</th><th>数量</th><th>程序做什么</th><th>LLM做什么</th></tr></thead><tbody>
<tr><td>RSS素材</td><td>{stats["rss_candidates"]}条 / {stats["feed_sources_ok"]}个成功信源</td><td>下载、解析标题／URL／摘要／时间，统计去重与时间</td><td>决定采用哪些事件</td></tr>
<tr><td>市场数据</td><td>18标的 × 6原始字段 = 108值</td><td>解析名称、现价、昨收、接口涨跌额／幅、时间；保留原始响应</td><td>选演示标的、解释行情</td></tr>
<tr><td>计算</td><td>36个单标的派生值 + 3个比较值</td><td>重算18组涨跌额／幅，再算两组相对表现与艺术品纪录增幅</td><td>设计比较的问题；提供2个有证据的拍卖价结构化输入</td></tr>
<tr><td>新闻／论文事实</td><td>19个证据单元；另采用4条RSS摘要</td><td>抓取原文，检查摘录确实存在</td><td>阅读、摘录、转述；论文读到摘要层</td></tr>
<tr><td>中文稿件</td><td>4版 / {stats["llm_paragraphs"]}段 / {prose_chars}非空白字符</td><td>模板排版；替换2处行情比较数值</td><td>选题、标题、导语、正文、分析、推演和笑话，写作占比100%</td></tr>
<tr><td>页面／交互</td><td>4套版面 / 1个自包含HTML</td><td>固定CSS与模板渲染、翻页、响应式布局</td><td>本次编写模板代码；运行时不调用模型排版</td></tr>
</tbody></table><h3>计数与边界</h3><p>共请求{stats["fetch_requests"]}个入口，{stats["fetch_success"]}个成功。RSS去重与时间统计：{escape(json.dumps(dict(freshness),ensure_ascii=False))}。本版允许引用明确标注的背景通稿与旧论文回看。实际采用{len(adopted_sources)}个来源记录，包括9篇原文、4条RSS摘要和1个行情接口；没有把775条候选说成逐条核实。19项程序检查是原文片段存在性检查，不代表独立事实核查。</p><p>完整原始响应、稿件JSON、逐块来源和精确计数保存在项目的data/editions/2026-11-19-sample-02目录。新增自选文件为演示清单，并非真实持仓。</p><h3>采用的来源</h3>{source_rows}<h3>原文事实清单</h3>{evidence_rows}<h3>未成功的入口</h3><p>{escape('；'.join(document['id']+': '+document['error'] for document in stats['failure_records']))}</p></dialog>'''
    tabs = "".join(f'<button role="tab" data-page="{position}" aria-controls="page-{position+1}" aria-selected="{str(position==0).lower()}">0{position+1} {page["label"]}</button>' for position,page in enumerate(editorial["pages"]))
    document_html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赛博日报 · 2026-11-19 · 内容试刊02</title><style>' + CSS + '</style></head><body><header class="reader"><span class="brand">赛博日报</span><nav role="tablist" aria-label="版面">' + tabs + '</nav><button class="audit-button" id="audit-open">来源账单 ↗</button></header><main class="edition">' + "".join(pages_html) + '<div class="bottom-nav"><button id="previous">← 上一版</button><span id="position">第1版 / 共4版</span><button id="next">下一版 →</button></div></main>' + audit + '<script>' + JS + '</script></body></html>'
    OUTPUT.write_text(document_html, encoding="utf-8")
    report = f'''# 赛博日报内容试刊02：程序与LLM来源账单

样报：`{OUTPUT.name}`。数据快照：{collection['collected_at']}。

| 项目 | 实际数量 | 来源与执行者 |
|---|---:|---|
| 抓取入口 | {stats['fetch_requests']}个，成功{stats['fetch_success']}个 | 程序并行下载；失败原样记录 |
| RSS候选 | {stats['rss_candidates']}条，来自{stats['feed_sources_ok']}个成功RSS源 | 标题、URL、摘要、发布时间由程序解析 |
| 真正采用来源 | {len(adopted_sources)}个记录 | 9篇原文、4条RSS摘要、1个行情接口；由LLM选择 |
| 行情 | {len(quotes)}个标的，108个原始字段值 | 程序读取9个指数、4个行业ETF、5个演示观察股；每个保留名称、现价、昨收、接口涨跌额、接口涨跌幅、接口时间 |
| 数学计算 | 36个单标的派生值、3个跨数据比较 | 程序重算涨跌额／幅、两组相对涨跌、拍卖纪录增幅；拍卖的2个输入值由LLM从原文摘录 |
| 原文事实摘录 | {len(evidence)}单元 | LLM摘录和转述；程序检查原文存在对应片段。不是19条自动核实结论 |
| 稿件 | 4版，{len(blocks)}个内容块，{stats['llm_paragraphs']}段 | 标题、导语、分析、报道转述、推演、点评和幽默均由{editorial['writer']}撰写 |
| 字符数 | {prose_chars} | 统计标题、导语、稿件小标题和段落，去空白与程序填数占位符；不含行情表与界面标签 |
| 排版 | 1个单文件HTML、4套版面 | LLM本次写模板代码，程序运行模板，固定布局；正文不在模板代码中维护 |

## 准确的占比口径

- 行情底表的原始数据：100%来自程序请求公开接口；LLM没有填造报价。
- 中文标题、导语和稿件文字：100%由LLM写作，包含有来源的事实转述；外部原文提供事实，并不是“LLM自己提供新闻”。
- 分析／判断／推演／笑话：100%由LLM生成，不是程序算出来的结论。
- 选题、来源选择、阅读与证据摘录：本次由会话内LLM完成，未自动化。
- 不把“事实的来源”和“文字的作者”相加成一个百分比。

## 阅读与核实深度

官方通稿、美联储纪要、AWS博客、BBC拍卖报道保留网页响应。两篇论文仅阅读arXiv摘要，未复现benchmark；4条快讯仅采用RSS标题和摘要。失败入口是AP正文403与联合早报非标准XML。未运行独立审稿agent，也未调用DeepSeek、Claude或Grok。

RSS去重与时间统计：`{json.dumps(dict(freshness),ensure_ascii=False)}`。该统计覆盖全部候选；采用旧背景材料和旧论文时在稿内交代，不冒充当日新发现。

## 文件

- `collection.json`：程序抓取的完整数据及失败记录。
- `raw/`：原始响应。
- `editorial.json`：LLM写出的结构化稿件、原文摘录、数值输入。
- `provenance.json`：渲染器生成的统计、逐块来源与时间。
- `verified_evidence.json`：已通过原文片段存在性检查的19个摘录。
- `../../../config/watchlist.json`：演示观察名单，不代表用户持仓。

重新抓取：`python3 pipeline/sample_collect.py`。离线重渲染与重算账单：`python3 pipeline/render_sample.py`。
'''
    (EDITION / "PROVENANCE.md").write_text(report, encoding="utf-8")
    print(json.dumps({key:value for key,value in stats.items() if key not in ("source_records", "story_provenance", "failure_records", "llm_structured_numeric_inputs")},ensure_ascii=False,indent=2))
    print(OUTPUT)


if __name__ == "__main__":
    main()
