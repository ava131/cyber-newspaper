#!/usr/bin/env python3
"""把四个版面装订成一本可翻阅的电子报（单文件 HTML，双击即开）。

翻页：← → / 空格 / Home End / 触屏左右滑 / 点两侧箭头 / 点底部圆点
打印：Cmd+P 直接出 PDF（每版一页 A4）
"""
from pathlib import Path

from build import BASE_CSS, P1, P2, P3, P4, COLOPHON

OUT = Path(__file__).resolve().parent

SHEETS = [
    ("p1", P1, "时政 · 记录", "01"),
    ("p2", P2, "钱 · Money", "02"),
    ("p3", P3, "系统 · System", "03"),
    ("p4", P4, "末版 · 边角", "04"),
]

VIEWER_CSS = """
html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#1c1916}
body{font-family:"Songti SC","STSong",serif;-webkit-font-smoothing:antialiased}

#desk{
  position:fixed;inset:0;display:flex;overflow:auto;
  scrollbar-width:thin;
  background:
    radial-gradient(120% 90% at 50% 0%,#332e28 0%,#1c1916 55%,#141110 100%);
}
#desk::before{
  content:"";position:absolute;inset:0;pointer-events:none;opacity:.35;
  background-image:radial-gradient(rgba(255,255,255,.05) .5px,transparent .5px);
  background-size:3px 3px;
}

#frame{margin:auto;position:relative;flex:0 0 auto;padding:24px 30px 62px;}
#book{width:1240px;height:1754px;position:relative;transform-origin:top left;
  filter:drop-shadow(0 22px 52px rgba(0,0,0,.6));}

.sheet{position:absolute;inset:0;opacity:0;pointer-events:none;
  transform:translateX(70px) scale(.985);
  transition:opacity .42s ease,transform .42s cubic-bezier(.22,.61,.36,1);}
.sheet.active{opacity:1;pointer-events:auto;transform:none;}
.noanim .sheet{transition:none!important}
.sheet.left{transform:translateX(-70px) scale(.985);}
.sheet .page{border-radius:1px;}

/* 控件 */
#chrome{position:fixed;left:0;right:0;bottom:0;padding:14px 26px 16px;z-index:50;
  display:flex;align-items:center;justify-content:space-between;
  font-family:"PingFang SC","Heiti SC",sans-serif;opacity:.55;transition:opacity .4s;
  background:linear-gradient(to top,rgba(12,10,9,.9),rgba(12,10,9,0));}
#chrome:hover{opacity:1}
#meta{color:#c9bfae;font-size:11.5px;letter-spacing:.18em}
#meta b{color:#f0e7d6;font-weight:500;letter-spacing:.24em}
#meta span{opacity:.45;margin:0 10px}

#zoom{position:absolute;left:50%;transform:translateX(-50%);background:none;border:0;
  color:#c9bfae;font-size:16px;cursor:pointer;opacity:.6;transition:.25s;padding:4px 10px}
#zoom:hover{opacity:1;color:#f0e7d6}
#dots{display:flex;gap:9px;align-items:center}
.dot{width:26px;height:2px;background:rgba(240,231,214,.22);border:0;padding:0;
  cursor:pointer;transition:.3s}
.dot.on{background:#f0e7d6;width:44px}

.arrow{position:fixed;top:50%;transform:translateY(-50%);z-index:60;
  width:52px;height:76px;border:0;background:rgba(12,10,9,.42);color:#efe7d6;
  font-size:30px;line-height:1;cursor:pointer;border-radius:2px;
  opacity:0;transition:opacity .3s,background .3s;font-family:Georgia,serif;}
.arrow:hover{background:rgba(12,10,9,.72)}
#prev{left:14px}#next{right:14px}
#desk:hover .arrow{opacity:.85}

#hint{position:fixed;left:50%;bottom:52px;transform:translateX(-50%);z-index:70;
  color:#efe7d6;background:rgba(12,10,9,.72);padding:14px 22px;border-radius:3px;
  font-family:"PingFang SC",sans-serif;font-size:12.5px;letter-spacing:.22em;
  transition:opacity .7s;pointer-events:none}
#hint.gone{opacity:0}

@media print{
  html,body{overflow:visible;background:#fff;height:auto}
  #desk{position:static;background:none;display:block;overflow:visible}
  #book{transform:none!important;filter:none;position:static;
    width:1240px;height:auto}
  .sheet{position:static;opacity:1!important;transform:none!important;
    break-after:page;page-break-after:always}
  #stack,#chrome,.arrow,#hint{display:none!important}
  .sheet .page{box-shadow:none}
}
@page{size:1240px 1754px;margin:0}
"""

JS = """
(function(){
  var sheets=[].slice.call(document.querySelectorAll('.sheet'));
  var dots=[].slice.call(document.querySelectorAll('.dot'));
  var book=document.getElementById('book');
  var meta=document.getElementById('meta');
  var names=NAMES;
  var i=0;

  var frame=document.getElementById('frame');
  var zoomed=false;
  function layout(s){
    frame.style.width=(1240*s+60)+'px';
    frame.style.height=(1754*s+86)+'px';
    book.style.transform='scale('+s+')';
  }
  function fit(){
    var s;
    if(zoomed){
      s=(window.innerWidth-96)/1240;
    }else{
      s=Math.min((window.innerWidth-80)/1240,(window.innerHeight-96)/1754);
    }
    layout(s);
  }
  function toggleZoom(){
    zoomed=!zoomed;
    fit();
    if(zoomed){
      var top=document.getElementById('desk').scrollTop;
      document.getElementById('desk').scrollTop=top;
    }
  }
  document.getElementById('frame').addEventListener('dblclick',toggleZoom);
  document.getElementById('zoom').addEventListener('click',function(e){e.stopPropagation();toggleZoom()});
  function zoomIn(){if(!zoomed){zoomed=true;fit()}}
  function zoomOut(){if(zoomed){zoomed=false;fit()}}
  function paint(){
    sheets.forEach(function(el,n){
      el.classList.toggle('active',n===i);
      el.classList.toggle('left',n<i);
    });
    dots.forEach(function(d,n){d.classList.toggle('on',n===i)});
    meta.innerHTML='<b>'+names[i][1]+'</b><span>·</span>第 '+(i+1)+' 版 / 共 '+sheets.length+' 版'+
                   '<span>·</span>'+names[i][0];
    if(history.replaceState)history.replaceState(null,'','#'+(i+1));
  }
  function go(n){
    if(n<0||n>=sheets.length||n===i)return;
    i=n;paint();
    document.getElementById('desk').scrollTop=0;
  }
  function next(){go(Math.min(i+1,sheets.length-1))}
  function prev(){go(Math.max(i-1,0))}

  document.getElementById('next').addEventListener('click',next);
  document.getElementById('prev').addEventListener('click',prev);
  dots.forEach(function(d,n){d.addEventListener('click',function(){go(n)})});

  window.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();next()}
    else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();prev()}
    else if(e.key==='Home'){e.preventDefault();go(0)}
    else if(e.key==='End'){e.preventDefault();go(sheets.length-1)}
    else if(e.key==='+'||e.key==='='){e.preventDefault();zoomIn()}
    else if(e.key==='-'||e.key==='_'){e.preventDefault();zoomOut()}
    else if(e.key==='Escape'){e.preventDefault();zoomOut()}
  });

  var tx=null;
  window.addEventListener('touchstart',function(e){tx=e.touches[0].clientX},{passive:true});
  window.addEventListener('touchend',function(e){
    if(tx===null)return;
    var dx=e.changedTouches[0].clientX-tx;
    if(Math.abs(dx)>60){dx<0?next():prev()}
    tx=null;
  },{passive:true});

  window.addEventListener('resize',fit);



  var m=location.hash.match(/^#(\\d+)$/);
  if(m){var n=parseInt(m[1],10)-1;if(n>=0&&n<sheets.length)i=n;}

  document.getElementById('book').classList.add('noanim');
  fit();paint();
  requestAnimationFrame(function(){
    requestAnimationFrame(function(){
      document.getElementById('book').classList.remove('noanim');
    });
  });

  var hint=document.getElementById('hint');
  setTimeout(function(){hint.classList.add('gone')},4200);
})();
"""


def build_book():
    sheets_html = []
    for pid, body, _, _ in SHEETS:
        body = body.replace('<div class="footer">', COLOPHON + '<div class="footer">', 1)
        sheets_html.append(f'<div class="sheet" id="{pid}"><div class="page">{body}</div></div>')

    names_js = "[" + ",".join(f'["{label}","{name}"]' for _, _, label, name in
                              [(a, b, c, d) for a, b, c, d in SHEETS]) + "]"

    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>赛博日报 · 2026-11-19</title>
<style>{BASE_CSS}{VIEWER_CSS}</style></head>
<body>
<div id="desk">
  <div id="frame"><div id="book">
    {''.join(sheets_html)}
  </div></div>
  <button class="arrow" id="prev" aria-label="上一版">‹</button>
  <button class="arrow" id="next" aria-label="下一版">›</button>
  <div id="hint">← → 翻页 · 双击放大 · 共 4 版</div>
  <div id="chrome">
    <div id="meta"></div>
    <button id="zoom" title="放大 / 整页（双击版面、按 + / - 亦可）">⤢</button>
    <div id="dots">{''.join(f'<button class="dot{" on" if n == 0 else ""}" aria-label="第 {n+1} 版"></button>' for n in range(len(SHEETS)))}</div>
  </div>
</div>
<script>
var NAMES={names_js};
{JS}
</script>
</body></html>"""
    path = OUT / "edition.html"
    path.write_text(html, encoding="utf-8")
    print(f"已生成 {path}  ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    build_book()
