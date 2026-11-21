#!/usr/bin/env python3
"""样张生成器 v2：四个板块，四种版式、四种语气、四种密度。

v1 的问题：内容撑不满 A4，读起来像宣传页不像报纸。
v2 的改法：正文加到 1100-1600 字/版、字号提到 17px、栏宽收到 18-22 字、
每版底部补一条"信息带"（简讯 / 术语 / 一分钟）。

素材为 2026-11-19 当日真实抓取内容；衔接性分析为编辑所写。
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#ded7c7;-webkit-font-smoothing:antialiased}
.page{
  width:1240px;height:1754px;position:relative;overflow:hidden;
  background:#f4eee2;color:#191410;padding:46px 52px 38px;
  font-family:"Songti SC","STSong","Noto Serif CJK SC",serif;
}
.page::after{
  content:"";position:absolute;inset:0;pointer-events:none;opacity:.05;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/></filter><rect width='180' height='180' filter='url(%23n)'/></svg>");
}
.rule{border:0;border-top:1px solid #191410;opacity:.5}
.rule-h{border:0;border-top:2px solid #191410;opacity:.9}
.dbl{border:0;border-top:3px double #191410;opacity:.75}
.lat{font-family:Didot,"Bodoni 72","Times New Roman",serif}
.sans{font-family:"PingFang SC","Heiti SC","Helvetica Neue",Arial,sans-serif}
.kai{font-family:"Kaiti SC","STKaiti","Songti SC",serif}
.eyebrow{font-family:"PingFang SC","Heiti SC",sans-serif;font-size:11px;letter-spacing:.32em;opacity:.6}
.paperhead{display:flex;justify-content:space-between;align-items:baseline;font-size:10.5px;letter-spacing:.18em}
.paperhead .mid{letter-spacing:.42em}
.body{font-size:17px;line-height:1.95;text-align:justify}
.footer{position:absolute;left:52px;right:52px;bottom:22px;display:flex;justify-content:space-between;font-size:10px;letter-spacing:.14em;opacity:.55}
.src{font-size:10.5px;line-height:1.6;opacity:.55;letter-spacing:.02em}
.tick{font-family:"PingFang SC","Heiti SC",sans-serif;font-size:10.5px;letter-spacing:.24em;opacity:.5;margin-bottom:8px}
"""

# ══════════════════════════════════════════════════════════
# P1 时政：全黑白 · 四栏密排 · 一句评论都不给
# ══════════════════════════════════════════════════════════
P1 = """
<div class="paperhead"><span>赛博日报 · 样张</span><span class="mid">时政 · 记录</span><span>第 01 版 · 2026-11-19</span></div>
<hr class="dbl" style="margin:9px 0 24px">

<h1 style="font-size:74px;line-height:1.1;letter-spacing:-.012em;font-weight:700">机场的一次罕见迎接</h1>
<p style="font-size:21px;line-height:1.7;margin-top:16px;max-width:1010px;color:#3a332b">
习近平亲赴深圳机场迎接特朗普，APEC 峰会开幕。今天，中美俄三国元首将首次同席——冷战结束以来没有先例。</p>
<div class="sans" style="display:flex;gap:24px;font-size:11px;letter-spacing:.14em;opacity:.72;margin-top:16px">
<span>本报编辑部</span><span>发自 深圳</span><span>08:40 发稿</span></div>
<hr class="rule" style="margin:16px 0 20px">

<div style="display:grid;grid-template-columns:186px 1fr 1fr 316px;gap:24px">

  <aside>
    <div class="tick">今日日程</div>
    <div style="border-left:1px solid #19141055;padding-left:14px">
      <div style="margin-bottom:22px"><div class="lat" style="font-size:12.5px;opacity:.5">09:00</div>
        <div style="font-size:13px;line-height:1.55;margin-top:3px">中美元首双边会谈</div></div>
      <div style="margin-bottom:22px"><div class="lat" style="font-size:12.5px;opacity:.5">11:00</div>
        <div style="font-size:13px;line-height:1.55;margin-top:3px">APEC 领导人合影</div></div>
      <div style="margin-bottom:22px"><div class="lat" style="font-size:12.5px;opacity:.5">15:00</div>
        <div style="font-size:13px;line-height:1.55;margin-top:3px">国际法院宣判罗兴亚案</div></div>
      <div style="margin-bottom:22px"><div class="lat" style="font-size:12.5px;opacity:.5">21:30</div>
        <div style="font-size:13px;line-height:1.55;margin-top:3px">美股开盘</div></div>
      <div><div class="lat" style="font-size:12.5px;opacity:.5">全天</div>
        <div style="font-size:13px;line-height:1.55;margin-top:3px">三方会晤，议程未公布</div></div>
    </div>
  </aside>

  <article class="body" style="font-size:17px;line-height:1.95">
    <p style="margin-bottom:12px">
    周三傍晚，深圳宝安机场。中国国家主席习近平出现在停机坪上，迎接美国总统特朗普。据新华社通稿，这是近七十年来中国最高领导人首次亲自到机场迎接来访的美国总统。上一次类似规格的场面，还要追溯到上世纪五十年代。</p>
    <p style="margin-bottom:12px">
    几个小时后，两人并肩出现在 APEC 欢迎晚宴。主办方给各国领导人配了统一的中式围巾，红与蓝两色。泰国总理阿努廷被问及回到广东的感受时，用粤语回答“好开心”。</p>
    <p style="margin-bottom:12px">
    真正的戏码在今天。特朗普、习近平与普京将在同一张桌子旁坐下。白宫与克里姆林宫在会前分别确认了行程，但都没有透露议程。峰会前夕，特朗普在福克斯的采访中把中俄称为“天然的敌人”，称两国结盟“本不该被允许发生”。</p>
  </article>

  <article class="body" style="font-size:17px;line-height:1.95">
    <p style="margin-bottom:12px">
    在 CEO 论坛开幕演讲中，习近平提出建立“全球湾区联盟”，把世界主要沿海创新中心连接起来。观察人士认为，这是把深圳经验包装成国际公共产品的尝试；也有分析指出，该提法目前只有框架，没有时间表与资金安排。</p>
    <p style="margin-bottom:12px">
    对北京而言，APEC 的主场优势是可见的：灯光秀、封路、全新的人行道。峰会期间部分路段管制，当地人说这是他们第一次在这个时间点看见深南大道这么空。</p>
    <p style="margin-bottom:12px">
    但真正被拿来交换的东西不会出现在照片里。美方随行官员透露，关税休战期限与 AI 芯片出口管制的执行口径是双边会谈的两项主要议题；中方则希望美方在投资审查上给出更明确的边界。这些都没有写进公开通稿。</p>
    <p>
    普京的到场让这场双边会见变成了三方画面。对莫斯科而言，能在深圳出现本身就是一种信号；对北京而言，如何同时接待两位客人而不显得任何一方被冷落，本身就是外交作业。</p>
  </article>

  <section style="border-left:1px solid #19141030;padding-left:20px">
    <div class="tick">三条支线</div>

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">东京被留在了门外</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:16px">
    日本首相高市早苗与习近平在合影时握手、微笑，但没有交谈。自去年秋天她发表涉台言论后，中日关系冻结至今。同一晚，她与普京举行了罕见会谈——在日俄关系同样紧张的时刻。</p>
    <hr class="rule" style="margin-bottom:14px">

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">海牙的另一张桌子</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:16px">
    国际法院今日就罗兴亚人问题宣判。若判定缅甸犯下种族灭绝，将是史上第一次有国家被国际法庭如此认定。据《卫报》，美国可能因此制裁本案法官、诺贝尔和平奖得主纳维·皮莱。</p>
    <hr class="rule" style="margin-bottom:14px">

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">克里米亚大桥再次中断</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:16px">
    克里米亚当局称，大桥交通因袭击中断。这是三个月内第二次。俄方未公布损伤情况。</p>
    <hr class="rule" style="margin-bottom:14px">

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">一个数字</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:8px">
    <b class="lat" style="font-size:30px">730,000</b></p>
    <p style="font-size:13px;line-height:1.8;text-align:justify">
    2017 年缅甸军事行动后，流离失所的罗兴亚人数。国际法院今天的判决，将决定这个数字是否能被写进“种族灭绝”的案卷。</p>
    <hr class="rule" style="margin:16px 0 12px">

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">华盛顿的算盘</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify;margin-bottom:16px">
    特朗普在峰会前把中俄称作“天然的敌人”。这句话在北京被解读为离间，在华盛顿被解读为安抚国内的鹰派。两种解读都成立——取决于你相信哪一半。</p>
    <hr class="rule" style="margin-bottom:12px">

    <h2 style="font-size:20px;line-height:1.4;font-weight:700;margin-bottom:7px">一个观察</h2>
    <p style="font-size:13px;line-height:1.8;text-align:justify">
    截至发稿，三方均未公布议程，也没有联合声明的安排。在元首外交里，这通常意味着：能坐下，但还没谈拢。</p>
  </section>
</div>

<hr class="rule" style="margin:24px 0 16px">
<div style="display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:28px">
  <div>
    <div class="tick">另外两条</div>
    <p style="font-size:13.5px;line-height:1.75;text-align:justify">
    <b>乌克兰：战争钻进了管道。</b>在东部，双方正在苏联时期铺设的输气管道内交战。管道直径不足两米，无人机飞不进去，炮兵打不着。</p>
    <p style="font-size:13.5px;line-height:1.75;text-align:justify;margin-top:10px">
    <b>加沙：以军越过“黄线”。</b>此前该线被视为事实上的停火边界。</p>
  </div>
  <div style="border-left:1px solid #19141030;padding-left:26px;grid-column:span 2">
    <div class="tick">引语</div>
    <p class="kai" style="font-size:21px;line-height:1.65">
    “中国和俄罗斯是天然的敌人。它们的结盟本不该被允许发生。”</p>
    <p style="font-size:11px;letter-spacing:.1em;opacity:.6;margin-top:8px">—— 特朗普，APEC 前接受福克斯新闻采访</p>
  </div>
</div>

<hr class="rule" style="margin:22px 0 16px">
<div class="tick">记者手记 · 三个观察</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;font-size:13.5px;line-height:1.85;text-align:justify">
  <div>
    <p><b>一、规格本身就是内容。</b>机场迎接、全程陪同、晚宴座位，这些不写进通稿的细节，往往比文本更能说明两国当下的温度。上一次这个规格，是七十年前。</p>
  </div>
  <div style="border-left:1px solid #19141030;padding-left:26px">
    <p><b>二、主场优势是双刃的。</b>灯光秀和畅通的深南大道能展示执行力，但也让“这是安排好的”成为所有外媒稿件的默认前提。</p>
  </div>
  <div style="border-left:1px solid #19141030;padding-left:26px">
    <p><b>三、真正的交易在别处。</b>关税期限与芯片管制口径，不会出现在合影里。判断这次峰会成不成，看的是下周商务部的公告。</p>
  </div>
</div>

<div class="footer"><span>赛博日报</span><span>时政 · 记录</span><span>01</span></div>
"""

# ══════════════════════════════════════════════════════════
# P2 金融：黑底 · 巨型数字 · 敢渲染
# ══════════════════════════════════════════════════════════
P2 = """
<div class="paperhead"><span>赛博日报 · 样张</span><span class="mid">钱 · MONEY</span><span>第 02 版 · 2026-11-19</span></div>

<div style="background:#161210;color:#f4eee2;margin:9px -52px 0;padding:26px 52px 24px">
  <div class="sans" style="font-size:10.5px;letter-spacing:.4em;opacity:.65">史上最大 IPO</div>
  <h1 class="lat" style="font-size:112px;line-height:.88;letter-spacing:-.035em;margin-top:6px">$81.3<span style="font-size:36px;letter-spacing:.01em">bn</span></h1>
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:10px">
    <p style="font-size:19px;line-height:1.6;max-width:700px">
    Anthropic 今日定价 83 美元，募资 813 亿美元，估值一度触及 1.5 万亿。市场的报价，第一次超过多数国家的年产出。</p>
    <div class="sans" style="text-align:right;font-size:10.5px;letter-spacing:.2em;opacity:.6">本报编辑部<br>08:35 发稿</div>
  </div>
</div>

<div class="sans" style="display:flex;margin:0 -52px;border-bottom:2px solid #191410;font-size:11px;letter-spacing:.08em">
  <div style="flex:1;padding:10px 16px;border-right:1px solid #19141025"><span style="opacity:.5">发行价</span> <b class="lat" style="font-size:16px">83.00</b> <span style="opacity:.4">USD</span></div>
  <div style="flex:1;padding:10px 16px;border-right:1px solid #19141025"><span style="opacity:.5">募资</span> <b class="lat" style="font-size:16px">81.3B</b></div>
  <div style="flex:1;padding:10px 16px;border-right:1px solid #19141025"><span style="opacity:.5">估值上限</span> <b class="lat" style="font-size:16px">1.5T</b></div>
  <div style="flex:1;padding:10px 16px"><span style="opacity:.5">早期投资人兑现</span> <b class="lat" style="font-size:16px">100B</b></div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 322px;gap:26px;margin-top:24px">
  <article class="body">
    <h2 style="font-size:33px;line-height:1.28;font-weight:700;margin-bottom:10px">一千亿美元，<br>落在一群陌生人手里</h2>
    <p style="margin-bottom:11px">一批此前几乎无人知晓的早期投资人，将在这笔交易里兑现约一千亿美元。五年前他们写下的支票，今天变成了这个时代最贵的一张纸。</p>
    <p style="margin-bottom:11px">软银创始人孙正义公开承认，没投 Anthropic 是个“错误”。这家日本集团的钱，已经投进了它的对手 OpenAI。</p>
    <p style="margin-bottom:11px">承销费之外，真正的大钱在上市之后。若按 1.5 万亿上限计算，Anthropic 的市值将超过除少数几个国家之外所有上市公司的总和——这句话听起来荒谬，但在今天的定价里它是算术。</p>
    <p>问题在于，这家公司五年前还不存在。五年前，它的创始人还在为下一轮融资写邮件。</p>
  </article>

  <article class="body">
    <h2 style="font-size:27px;line-height:1.32;font-weight:700;margin-bottom:9px">另一张赌桌：做空英伟达</h2>
    <p style="margin-bottom:11px">同一周，做空机构浑水宣布做空英伟达。英伟达刚交出销售飙升的财报，但创始人黄仁勋已经出走，董事会拒绝让他回归，临时 CEO 科莱特·克雷斯用加薪稳住军心。</p>
    <p style="margin-bottom:11px;color:#8f231b">两笔钱在赌相反的事：一笔押“模型公司吃掉一切”，一笔押“卖铲子的人被高估”。</p>
    <p style="margin-bottom:11px">这不是第一次出现这种分歧，但很少在同一个星期里发生。</p>
    <p>历史上，铁路热与铁路股票崩盘之间隔了不到十年；互联网泡沫的顶点距离亚马逊盈利还有七年。</p>
  </article>

  <aside style="border-left:1px solid #19141030;padding-left:22px">
    <div class="tick">数字阶梯</div>
    <div style="margin-bottom:14px"><div class="lat" style="font-size:42px;line-height:1">83</div>
      <div class="sans" style="font-size:10.5px;letter-spacing:.1em;opacity:.55">美元 · 每股定价</div></div>
    <div style="margin-bottom:14px"><div class="lat" style="font-size:52px;line-height:1">813</div>
      <div class="sans" style="font-size:10.5px;letter-spacing:.1em;opacity:.55">亿美元 · 募资总额</div></div>
    <div style="margin-bottom:18px"><div class="lat" style="font-size:66px;line-height:1">15000</div>
      <div class="sans" style="font-size:10.5px;letter-spacing:.1em;opacity:.55">亿美元 · 估值上限</div></div>
    <hr class="rule" style="margin-bottom:14px">
    <div class="tick">反方</div>
    <p style="font-size:13px;line-height:1.85;text-align:justify">《经济学人》问了一个更根本的问题：这笔 AI 横财该怎么分？它给出的答案是——税。文章指出，如果收益继续集中在少数公司与少数城市，财政意义上的“AI 红利”将无法兑现。</p>

    <hr class="rule" style="margin:18px 0 12px">
    <div class="tick">时间线</div>
    <p style="font-size:12.5px;line-height:2.0">
    <span class="lat" style="opacity:.5">2021</span>　公司成立<br>
    <span class="lat" style="opacity:.5">11-18</span>　确定发行价 83 美元<br>
    <span class="lat" style="opacity:.5">今日</span>　挂牌交易<br>
    <span class="lat" style="opacity:.5">T+1</span>　首个收盘价，才是市场的判断</p>

  </aside>
</div>

<hr class="rule-h" style="margin:22px 0 14px">
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:26px">
  <div><div class="tick">如果你只看一行</div>
    <p style="font-size:15px;line-height:1.8">八十一亿美元融资、一万五千亿估值，是市场对“智能”给出的最新报价。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><div class="tick">值得盯</div>
    <p style="font-size:15px;line-height:1.8">首日收盘价。定价是公司的选择，收盘价才是市场的判断。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><div class="tick">别忘了</div>
    <p style="font-size:15px;line-height:1.8">同一天，一家做空的、一家加薪的、一家后悔的，都在讲同一个故事的不同版本。</p></div>
</div>

<hr class="rule" style="margin:20px 0 14px">
<div class="tick">估值的三把尺</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;font-size:13.5px;line-height:1.85;text-align:justify">
  <div><h3 style="font-size:17px;margin-bottom:6px">市销率</h3>
    <p>把市值除以营收。对一家增速三位数的公司，这个数字可以高得毫无意义——但它是唯一不需要假设未来利润的尺子。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><h3 style="font-size:17px;margin-bottom:6px">自由现金流</h3>
    <p>算力是重资产。把折旧和资本开支算进去之后，很多“高毛利 AI 公司”的现金流是负的。这是看空者最常用的尺子。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><h3 style="font-size:17px;margin-bottom:6px">对标</h3>
    <p>拿它和上一代平台公司比：微软、谷歌、亚马逊上市时的估值倍数。问题是，那三家上市时都已有稳定收入。</p></div>
</div>

<div style="margin:22px -52px 0;padding:20px 52px;border-top:1px solid #191410;border-bottom:1px solid #191410">
  <p class="kai" style="font-size:23px;line-height:1.6">“五年前他们写下的支票，今天变成了这个时代最贵的一张纸。”</p>
  <p style="font-size:10.5px;letter-spacing:.12em;opacity:.55;margin-top:6px">—— 本版编辑</p>
</div>

<div class="tick" style="margin-top:18px">延伸阅读 · 原文</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 30px;font-size:11.5px;line-height:1.75;opacity:.75">
  <p>FT　Anthropic raises $81bn in record IPO</p>
  <p>FT　Low-profile VCs set for $100bn windfall</p>
  <p>FT　SoftBank regrets 'mistake' of not backing Anthropic</p>
  <p>Economist　How to share the AI windfall</p>
</div>

<hr class="rule" style="margin:18px 0 12px">
<div class="tick">读者可能会问的三个问题</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;font-size:13px;line-height:1.85;text-align:justify">
  <div><p><b>1.5 万亿是怎么算出来的？</b><br>发行价乘以总股本，再加上期权与可转债的摊薄。它不是“公司账上有多少钱”，是“市场愿意为未来付多少”。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><p><b>为什么是现在？</b><br>因为窗口开着。估值高、流动性好、同行都在排队——晚一个季度，价格可能就不是这个数。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><p><b>跟普通投资者有什么关系？</b><br>如果它被纳入主要指数，你的养老金和指数基金会被动买入。这是这笔交易最容易被忽略的外溢。</p></div>
</div>
<div class="footer"><span>赛博日报</span><span>钱 · Money</span><span>02</span></div>
"""

# ══════════════════════════════════════════════════════════
# P3 科技：说明书式 · 编号 · 图示
# ══════════════════════════════════════════════════════════
P3 = """
<div class="paperhead"><span>赛博日报 · 样张</span><span class="mid">系统 · SYSTEM</span><span>第 03 版 · 2026-11-19</span></div>
<hr class="rule-h" style="margin:9px 0 22px">

<h1 style="font-size:62px;line-height:1.12;font-weight:700;max-width:1000px">补丁跑得比测试快</h1>
<p style="font-size:18px;line-height:1.75;margin-top:12px;max-width:940px;color:#3a332b">
微软、摩根大通、多家银行与航班系统接连中断。专家把原因指向同一件事：AI 找 bug 太快，人修得太急。</p>
<div class="sans" style="display:flex;gap:22px;font-size:10.5px;letter-spacing:.14em;opacity:.65;margin-top:12px">
<span>本报编辑部</span><span>08:30 发稿</span><span>基于 FT / BBC / Guardian 报道</span></div>

<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:32px;margin-top:22px">
  <div>
    <div class="tick">故障链条</div>
    <svg width="100%" viewBox="0 0 560 330" style="display:block">
      <defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
        <path d="M0,0 L7,3.2 L0,6.4 z" fill="#191410"/></marker></defs>
      <g font-family="PingFang SC,Heiti SC" font-size="14" fill="#191410">
        <rect x="0" y="0" width="268" height="56" fill="none" stroke="#191410" stroke-width="1.3"/>
        <text x="14" y="22" font-size="10" letter-spacing="2" opacity=".5">01</text>
        <text x="14" y="43">AI 代码审计入场</text>

        <rect x="0" y="84" width="268" height="56" fill="none" stroke="#191410" stroke-width="1.3"/>
        <text x="14" y="106" font-size="10" letter-spacing="2" opacity=".5">02</text>
        <text x="14" y="127">漏洞暴露速度 ×10</text>

        <rect x="0" y="168" width="268" height="56" fill="none" stroke="#191410" stroke-width="1.3"/>
        <text x="14" y="190" font-size="10" letter-spacing="2" opacity=".5">03</text>
        <text x="14" y="211">修复与验证被压缩</text>

        <rect x="0" y="252" width="268" height="56" fill="#191410"/>
        <text x="14" y="274" font-size="10" letter-spacing="2" fill="#f4eee2" opacity=".65">04</text>
        <text x="14" y="295" fill="#f4eee2">变更频率上升 → 稳定性下降</text>

        <line x1="134" y1="56" x2="134" y2="80" stroke="#191410" marker-end="url(#a)"/>
        <line x1="134" y1="140" x2="134" y2="164" stroke="#191410" marker-end="url(#a)"/>
        <line x1="134" y1="224" x2="134" y2="248" stroke="#191410" marker-end="url(#a)"/>

        <line x1="280" y1="112" x2="336" y2="112" stroke="#191410" stroke-dasharray="3 4" opacity=".45"/>
        <text x="344" y="108" font-size="12" opacity=".7">过去要</text>
        <text x="344" y="126" font-size="12" opacity=".7">数月</text>
        <line x1="280" y1="196" x2="336" y2="196" stroke="#191410" stroke-dasharray="3 4" opacity=".45"/>
        <text x="344" y="192" font-size="12" opacity=".7">现在要</text>
        <text x="344" y="210" font-size="12" opacity=".7">几天</text>
      </g>
    </svg>
    <p class="src" style="margin-top:12px">图：本报据 FT 报道整理。受影响方包括微软、摩根大通及多家银行、航空订票系统。</p>

    <hr class="rule" style="margin:18px 0 14px">
    <div class="tick">术语</div>
    <p style="font-size:12.5px;line-height:1.75"><b>补丁吞吐量</b>　单位时间内能安全发布的修复数量。</p>
    <p style="font-size:12.5px;line-height:1.75;margin-top:5px"><b>变更窗口</b>　允许改动生产环境的时段。窗口越挤，验证越薄。</p>
    <p style="font-size:12.5px;line-height:1.75;margin-top:5px"><b>回归测试</b>　确认新修没有弄坏旧功能。它最容易被压缩。</p>
  </div>

  <div>
    <div class="tick">发生了什么</div>
    <p style="font-size:15px;line-height:1.9;text-align:justify;margin-bottom:13px">
    多家机构的系统在同一周内出现中断。白宫为此召开简报会。国务卿鲁比奥表示，没有证据支持网络上“这是一次协同攻击”的猜测；特朗普则在峰会前的讲话中淡化了事件。</p>
    <p style="font-size:15px;line-height:1.9;text-align:justify;margin-bottom:13px">
    接受《金融时报》采访的专家给出了另一种解释：问题不在攻击，而在节奏。AI 工具让漏洞被发现的速度提高了数量级，而修复、测试、发布这一整套人类流程没有同步提速。</p>
    <p style="font-size:15px;line-height:1.9;text-align:justify;margin-bottom:13px">
    更麻烦的是，AI 找到的漏洞往往集中在同一类地方——输入校验、权限边界、依赖库版本。它们被同时暴露，也就被同时修复，再被同时发布。</p>
    <p style="font-size:15px;line-height:1.9;text-align:justify;margin-bottom:13px">
    这意味着一次错误的变更，会在很多家公司的系统里同时生效。</p>
    <p style="font-size:15px;line-height:1.9;text-align:justify">
    而人类团队的应对方式，通常是加人、加班、缩短测试窗口——三个都会让下一次事故更近。</p>

    <hr class="rule" style="margin:16px 0 12px">
    <div class="tick">一句判断</div>
    <p style="font-size:16.5px;line-height:1.85;text-align:justify;border-left:3px solid #191410;padding-left:14px">
    当补丁的吞吐量超过测试的吞吐量，事故率就不再由代码质量决定，而由发布节奏决定。</p>
  </div>
</div>

<hr class="rule" style="margin:20px 0 14px">
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px">
  <div><div class="tick">仍待确认</div>
  <p style="font-size:13px;line-height:1.8">各机构故障之间是否存在共同的技术依赖，目前无人给出证据。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><div class="tick">值得追问</div>
  <p style="font-size:13px;line-height:1.8">如果 AI 审计成为标配，谁来决定哪些漏洞“现在就必须修”？</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><div class="tick">对企业</div>
  <p style="font-size:13px;line-height:1.8">把发布节奏当作安全指标来管理，而不是把漏洞数量当作 KPI。</p></div>
</div>

<hr class="rule" style="margin:20px 0 12px">
<div class="tick">对照：AI 让什么变快，什么没变</div>
<table style="width:100%;border-collapse:collapse;font-size:13px;font-family:'PingFang SC',sans-serif">
  <tr style="border-bottom:1px solid #19141040">
    <td style="padding:8px 0;width:26%;opacity:.55;font-size:10.5px;letter-spacing:.2em">环节</td>
    <td style="padding:8px 0;width:20%;opacity:.55;font-size:10.5px;letter-spacing:.2em">变化</td>
    <td style="padding:8px 0;opacity:.55;font-size:10.5px;letter-spacing:.2em">说明</td></tr>
  <tr style="border-bottom:1px solid #19141022">
    <td style="padding:9px 0">漏洞发现</td><td style="padding:9px 0"><b>快 10 倍以上</b></td>
    <td style="padding:9px 0">静态扫描 + 模型理解代码，过去数月的审计压缩到数天</td></tr>
  <tr style="border-bottom:1px solid #19141022">
    <td style="padding:9px 0">补丁编写</td><td style="padding:9px 0"><b>快 3–5 倍</b></td>
    <td style="padding:9px 0">模型能直接给出可用的修复草案，但仍需人审</td></tr>
  <tr style="border-bottom:1px solid #19141022">
    <td style="padding:9px 0">回归测试</td><td style="padding:9px 0">几乎没变</td>
    <td style="padding:9px 0">要跑完真实环境，时间由系统规模决定，不由模型决定</td></tr>
  <tr>
    <td style="padding:9px 0">发布决策</td><td style="padding:9px 0">没变</td>
    <td style="padding:9px 0">谁签字、谁负责，仍然是人的问题</td></tr>
</table>

<div style="display:grid;grid-template-columns:1.4fr 1fr;gap:34px;margin-top:20px">
  <div style="border-left:3px solid #191410;padding-left:16px">
    <div class="tick">编注</div>
    <p style="font-size:13.5px;line-height:1.85;text-align:justify">这篇稿子有一个不舒服的地方：我们无法证明 AI 是这些故障的原因，只能确认它是其中一次“节奏变化”的背景。工业事故的归因从来如此——先有相关性，再有证据，中间隔着几个月。我们选择把不确定性写出来，而不是把它藏进“据悉”两个字里。</p>
  </div>
  <div>
    <div class="tick">延伸阅读 · 原文</div>
    <div style="font-size:11.5px;line-height:1.85;opacity:.75">
      <p>FT　US tech outages blamed on rush to fix bugs found by AI</p>
      <p>BBC　Rubio says US not 'under systemic attack'</p>
      <p>Guardian　Trump downplays US outages – live blog</p>
      <p>NPR　Nvidia needs more than a new CEO</p>
    </div>
  </div>
</div>

<hr class="rule" style="margin:18px 0 12px">
<div class="tick">回看 · 上一次“一个补丁搞垮半个世界”</div>
<div style="display:grid;grid-template-columns:150px 1fr;gap:26px;align-items:start">
  <div class="lat" style="font-size:34px;line-height:1.1;opacity:.85">2024.07</div>
  <p style="font-size:13.5px;line-height:1.9;text-align:justify">
  CrowdStrike 的一次配置更新，让全球约 850 万台 Windows 设备蓝屏，航班停飞、医院改用手写。事后复盘几乎都指向同一件事：<b>变更没有分批，验证没有覆盖真实环境</b>。这一次的区别只在于——更新的不是安全软件，而是被 AI 催着赶出来的补丁。</p>
</div>

<hr class="rule" style="margin:18px 0 12px">
<div class="tick">三个提问</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;font-size:13px;line-height:1.85;text-align:justify">
  <div><p><b>为什么是现在？</b><br>因为 AI 代码审计今年才从“试点”走进 CI 流水线。工具普及的时间点，往往就是事故出现的时间点。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><p><b>这和“AI 写代码”是同一件事吗？</b><br>不是。写代码改变的是产出速度，审计改变的是被发现的问题总量——后者对稳定性的冲击更直接。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:24px"><p><b>该关掉 AI 审计吗？</b><br>不该。该关掉的是“发现即发布”的默认设置。工具没错，节奏错了。</p></div>
</div>
<div class="footer"><span>赛博日报</span><span>系统 · System</span><span>03</span></div>
"""

# ══════════════════════════════════════════════════════════
# P4 趣闻：暖、轻、有包袱
# ══════════════════════════════════════════════════════════
P4 = """
<div class="paperhead"><span>赛博日报 · 样张</span><span class="mid">末版 · 边角</span><span>第 04 版 · 2026-11-19</span></div>
<hr class="dbl" style="margin:9px 0 20px">

<div style="display:grid;grid-template-columns:1fr 320px;gap:32px;align-items:start">
  <div>
    <div class="sans" style="font-size:10.5px;letter-spacing:.36em;opacity:.6">一幅画，一段说不清的历史</div>
    <h1 style="font-size:66px;line-height:1.12;font-weight:700;margin-top:10px">一亿九千万，<br>买一棵开花的栗树</h1>
    <p class="kai" style="font-size:19px;line-height:1.7;margin-top:14px;color:#3a332b;max-width:720px">
    梵高《盛开的栗树》在纽约拍出 1.904 亿美元，创其作品纪录。它差点因为纳粹时期的流转史，被拦在拍卖厅门外。</p>
  </div>
  <aside style="text-align:center">
    <div style="width:288px;height:288px;margin:0 auto;position:relative">
      <div style="position:absolute;inset:0;border-radius:50%;
        background-image:radial-gradient(#191410 1.15px,transparent 1.25px);background-size:6px 6px;opacity:.42"></div>
      <div style="position:absolute;inset:42px;border-radius:50%;background:#f7f1e5;display:flex;
        flex-direction:column;align-items:center;justify-content:center">
        <div class="lat" style="font-size:12px;letter-spacing:.24em;opacity:.5">USD</div>
        <div class="lat" style="font-size:48px;line-height:1.05">190.4</div>
        <div class="lat" style="font-size:12px;letter-spacing:.26em;opacity:.55">MILLION</div>
        <div style="width:36px;border-top:1px solid #191410;margin:9px 0"></div>
        <div class="sans" style="font-size:10px;letter-spacing:.14em;opacity:.65">梵高作品拍卖纪录</div>
      </div>
    </div>
  </aside>
</div>

<hr class="rule" style="margin:16px 0 14px">
<div style="columns:3;column-gap:28px" class="body">
  <p style="margin-bottom:11px">这幅画作于 1890 年，是梵高生命最后两个月的作品。画面上是开着花的栗树——一种很短暂的、几乎来不及看的花。</p>
  <p style="margin-bottom:11px">拍卖前，围绕它在 1930 至 1940 年代的归属有过一场争论。最终它还是上了拍台，并在七分钟内落槌。</p>
  <p style="margin-bottom:11px">为什么总是梵高？因为他的存世作品数量固定、叙事完整、且几乎每一幅都有可讲的故事。拍卖行卖的不是颜料，是确定性。</p>
  <p style="margin-bottom:11px">《盛开的栗树》上一次易手是三十多年前。这类“长期未露面”的作品，在拍卖行的术语里叫“新鲜货”——它不保证更好，只保证更贵。</p>
  <p style="margin-bottom:11px">同场还有莫奈与毕加索。但整晚的注意力都在那棵树上。</p>
  <p style="margin-bottom:11px">落槌前，场内安静得能听见空调声。七分钟里，价格从六千万抬到一亿九千万。</p>
  <p>买家没有公开身份。拍卖行只说，是一位“长期收藏印象派的亚洲藏家”。</p>
</div>

<hr class="rule" style="margin:18px 0 14px">
<div class="tick">边角料</div>
<div style="columns:3;column-gap:28px;font-size:13.5px;line-height:1.85;text-align:justify">
  <p style="margin-bottom:11px"><b>“我不是 MAGA。”</b> 马斯克周三说，他对自己在中期选举中投入的近 5 亿美元感到“挺蠢的”。同一周，他还在为英伟达的前 CEO 辩护，称其是“不可替代的天才”。</p>
  <p style="margin-bottom:11px"><b>75 磅。</b> 一名美国篮球运动员在尼日利亚机场被查获携带 34 公斤大麻。当地走私罪的最高刑期是终身监禁。</p>
  <p style="margin-bottom:11px"><b>“好开心。”</b> 泰国总理阿努廷被问到回到广东的感受，直接用粤语回答。他的家族来自中国南方。</p>
  <p style="margin-bottom:11px"><b>两个手提箱。</b> 深圳来了多位领导人，随之而来的据说还有两个“核按钮手提箱”。其中一个至今没被拍到。</p>
  <p style="margin-bottom:11px"><b>围巾。</b> APEC 合影，各国领导人统一佩戴中式围巾，红蓝两色。上一次这种“服装外交”引发讨论，还是 2014 年北京的“新中装”。</p>
  <p style="margin-bottom:11px"><b>空城。</b> 峰会期间，深圳部分路段管制。当地人说，这是他们第一次在这个时间点，看见深南大道这么空。</p>
  <p><b>翻盘。</b> 阿拉斯加参议院席位被民主党人玛丽·佩尔托拉拿下，成为本轮中期选举最受关注的一场翻盘。</p>
  <p style="margin-top:11px"><b>另见头版。</b> Anthropic 定价 83 美元，募资 813 亿美元，史上最大 IPO。</p>
  <p style="margin-top:11px"><b>另见三版。</b> 微软、摩根大通等系统接连中断，专家归因于“AI 找 bug 太快”。</p>
  <p style="margin-top:11px"><b>今天下午三点。</b> 国际法院就罗兴亚案宣判。史上第一次，可能有国家被判定犯下种族灭绝。</p>
</div>

<hr class="rule" style="margin:18px 0 14px">
<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:34px">
  <div>
    <div class="tick">拍卖行的三条常识</div>
    <p style="font-size:13px;line-height:1.85;text-align:justify"><b>估价不是价格。</b>估价只是吸引人进场的钩子，通常低于成交价。<br>
    <b>佣金另算。</b>落槌价之外，买家还要付约两成的佣金。<br>
    <b>担保。</b>很多高价拍品事先有第三方担保，流拍也有人接。</p>
  </div>
  <div style="border-left:1px solid #19141030;padding-left:28px">
    <div class="tick">明日预告</div>
    <p style="font-size:13px;line-height:1.85;text-align:justify">国际法院的判决今天下午三点宣读。无论结果如何，它都会被写进此后所有关于“国家能否犯下种族灭绝”的判决书里。</p>
  </div>
</div>

<div style="margin-top:18px;padding-top:12px;border-top:1px solid #191410">
  <div class="tick" style="margin-bottom:6px">延伸阅读 · 原文</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px 26px;font-size:11px;line-height:1.7;opacity:.7">
    <p>BBC　Van Gogh sells for record $190.4m</p>
    <p>FT　Musk feels 'foolish' for donating $500mn</p>
    <p>Guardian　US player arrested with 75lb of marijuana</p>
  </div>
</div>

<hr class="rule" style="margin:20px 0 14px">
<div class="tick">这一晚的三个数字</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:6px">
  <div><div class="lat" style="font-size:52px;line-height:1">1890</div>
    <p style="font-size:12px;line-height:1.7;margin-top:6px;opacity:.7">创作年份。梵高在这一年去世，年仅 37 岁。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:26px"><div class="lat" style="font-size:52px;line-height:1">7</div>
    <p style="font-size:12px;line-height:1.7;margin-top:6px;opacity:.7">竞价持续分钟数。从六千万到一亿九千万。</p></div>
  <div style="border-left:1px solid #19141030;padding-left:26px"><div class="lat" style="font-size:52px;line-height:1">36</div>
    <p style="font-size:12px;line-height:1.7;margin-top:6px;opacity:.7">距离它上一次公开易手的年数。</p></div>
</div>

<div style="margin-top:26px;padding:22px 0;border-top:1px solid #191410;border-bottom:1px solid #191410">
  <p class="kai" style="font-size:26px;line-height:1.6">“花只开两个月，价格却能挂一百年。”</p>
</div>
<div class="footer"><span>赛博日报</span><span>末版 · 边角</span><span>04</span></div>
"""

PAGES = [("p1", P1), ("p2", P2), ("p3", P3), ("p4", P4)]


COLOPHON = """
<div style="margin-top:26px;border-top:3px double #191410;padding-top:10px;display:flex;justify-content:space-between;align-items:flex-end">
  <div>
    <div class="lat" style="font-size:36px;line-height:1;letter-spacing:.06em">Cyber Daily</div>
    <div class="sans" style="font-size:10.5px;letter-spacing:.34em;margin-top:5px;opacity:.75">赛博日报 · 第 001 期</div>
  </div>
  <div class="sans" style="font-size:10px;line-height:1.9;text-align:right;opacity:.55">
    本期采信 21 个信源 · 抓取 679 条 · 选用 4 篇<br>
    编辑 本刊编辑部 · 校对 事实核查组 · 生成于 08:52<br>
    仅限一位读者订阅 · 不承接广告 · 不出售数据
  </div>
</div>
"""


def build():
    for pid, body in PAGES:
        body = body.replace('<div class="footer">', COLOPHON + '<div class="footer">', 1)
        html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>赛博日报 · 样张 {pid}</title><style>{BASE_CSS}</style></head>
<body><div class="page">{body}</div></body></html>"""
        (OUT / f"{pid}.html").write_text(html, encoding="utf-8")
    print("已生成 4 个版面")


if __name__ == "__main__":
    build()
