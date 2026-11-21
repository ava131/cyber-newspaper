# 赛博日报 · 项目档案

> **2026-11-21 版本管理**：按用户要求，GitHub仓库已改为公开：`https://github.com/ava131/cyber-newspaper`，主分支`main`。新增`README.md`说明现有功能、代码与Agent分工、运行命令及未完成事项。历期成品和复现材料纳入版本管理；本机`config/mail.json`、`.local/`、生成邮件、页面检查截图及Python缓存不入仓。邮件测试改用示例配置，可在没有真实邮件账号和钥匙串凭证的环境运行。

> **2026-11-21 QQ邮件首投成功提交**：已配置`1144709817@qq.com`发至`otis_chang@163.com`。新增`pipeline/mail_delivery.py`及本机配置页`pipeline/mail_setup.py`；正文为天气与四栏导读，附件为完整六版HTML。用户已通过本机页面填写授权码，Mac钥匙串读取及真实QQ认证成功。15:25:15北京时间，QQ服务器接受首封周末刊（`accepted`）；163实际收件待用户确认。同一期重复投递已拦截，8项离线测试通过。操作见`config/MAIL_SETUP.md`。尚未设置定时投递。

> **2026-11-21 周末刊（最新）**：成品 `cyber-daily-2026-11-21.html`，四栏目六版，7,471个稿件非空白字符、46块、71段。新增头版「吴江·汾湖」天气条：当前预报、温度区间、风、降水概率、日落与次日天气。天气从Open-Meteo按汾湖（黎里）坐标点读取，带北京时间；中文天气、风向和提醒由程序规则生成，不计入LLM稿件。偏好保存于 `config/weather.json`，同日采集时默认一并获取天气；当期原始响应在 `data/editions/2026-11-21/raw/weather_open_meteo.json`。

本期新闻快照14:22北京时间，天气时标14:15。时政主线是英欧峰会关系重置及规则成本，财经复盘周五科技股抛售与个股分化，科技介绍TideCache、FlashMorph2与Harness Adapter，艺文采用莫奈《睡莲池上的桥》Commons CC0图像和朱熹《观书有感》。20条采用来源记录、16个域名；39个RSS入口中33个取得有效条目、2,155条候选。周六休市，18个行情标的都取11/20已结束交易日的本次接口值，无历史存档替换。来源账单与采集失败记录均已更新，X仍为0条。

天气采集／排版分别在 `pipeline/weather_collect.py` 与 `pipeline/weather_render.py`；`prepare_closed.py`核对周末版的市场日期。`render_daily.py`支持当期刊名与可选天气，来源账单按实际渠道和市场时段生成。浏览器检查新增天气只在头版出现一次、地点日期与温度和原始数据相符，仍覆盖1440／820／390px。

> **2026-11-20 今日早报**：成品 `cyber-daily-2026-11-20.html`，四栏目六版，7,465个稿件非空白字符，46块、71段，全部重新选题写作。主线为深圳会晤正式宣言与利益分析、美股隔夜下跌和个股判断、vLLM 0.34与推理优化新论文。艺文采用维米尔《持天平的女人》馆方公版原图和柳宗元《江雪》。来源账单与原始材料在 `data/editions/2026-11-20/`；21条采用来源记录、16个域名、39个RSS入口中36个成功、2,653条候选。

本期新闻与行情快照截至09:25北京时间。当前采集时处于A/H盘前，接口竞价数据已另存；成品使用美股11/19收盘与A/H11/19存档，避免把竞价当成全日表现。2份原始页面直接抓取失败的材料采用网页工具摘录，单独标为`web_excerpt`，未算作程序取得的全文。X仍未启用，实际0条。

新增 `pipeline/render_daily.py --edition YYYY-MM-DD`，读取当期完整`editorial.json`独立重渲染，复用六版样式。`sample_collect.py --documents`支持当期文档清单；`enrich_edition.py`补抓选题原文；`prepare_morning.py`保存盘前数据并选择有日期的基准。浏览器验证覆盖四栏目在1440／820／390px下的12个视图、对页与纵向阅读、来源账单、原画加载与放大。

> **2026-11-19 扩刊更新**：新增 `cyber-daily-2026-11-19-sample-03.html`，共四个栏目、六版：时政与财经各左右两版，科技、艺文各一版。正文统计6,795个非空白字符，上一版3,386，约2倍；RSS入口21→39，本次实测36个成功、2,664条候选，最终采用24条来源记录、涉及16个域名。数据与分工见 `data/editions/2026-11-19-sample-03/PROVENANCE.md`。末版现固定为艺文方向，可轮换画作、诗词、名著和哲学；本期采用苏富比的梵高《盛开的栗树》原图，搭配王维《山居秋暝》与鉴赏。图片内嵌，可放大。

X适配器在 `pipeline/x_collect.py`，查询清单在 `config/x_sources.json`；支持官方近期搜索与API JSON离线导入。当前没有X开发者Token，配置关闭，实际0条帖子、0次API请求，尚未验证真实联网调用。使用方法见 `config/X_SOURCES.md`。它与RSS采集器是独立命令，实时帖子自动合入选题流程仍待完成。独立agent分工、自动选题写作和定时投递仍未接入。

扩刊由 `pipeline/render_expanded.py`离线重渲染。浏览器检查覆盖1440／820／390px、四栏目翻页、对页与纵向切换、来源账单、原图加载和键盘放大；截图与检查结果在 `data/editions/2026-11-19-sample-03/preview/`。第一、二次会话记录保留如下。

> **2026-11-19 第二次会话更新**：新增内容试刊 `cyber-daily-2026-11-19-sample-02.html`，四版可翻页，附内嵌「来源账单」。本次程序实际抓取775条RSS候选、18个行情标的；25个稿件内容块由GPT-6在会话内撰写。原始数据、结构化稿件和统计见 `data/editions/2026-11-19-sample-02/PROVENANCE.md`。下面保留第一次会话的历史记录，其「当前阶段」与「未验证」不全部代表最新状态。

本次用户补充的内容指导：

- 时政：前半部引用官方报道，后半部分析大国博弈和含义，允许明确标注的大胆推演；侧栏放小事件。
- 财经：美联储、A股／港股／美股、板块行业，以及持久化清单中的重点股票；讲清事件、价格表现、投资上的意义。
- 科技：AI圈动态，加大模型推理优化方向的论文与实现。
- 末版：其他有趣新闻，不固定主题。
- 用户认为GPT写稿的防御性话术过多，要求先交一版成品，并准确说明程序与LLM分别贡献什么。

本次新增 `config/watchlist.json` 是明确标注的演示名单，尚不是用户真实持仓。采集器、数据驱动渲染器和浏览器截图检查已分别落到 `pipeline/sample_collect.py`、`pipeline/render_sample.py`、`pipeline/preview_sample.mjs`。选题与写作仍在会话内完成，独立agent编排和定时投递尚未接入。

> 2026-11-19 第一次工作会话的完整记录：需求、调研、技术验证、代码、产物、遗留问题。
> 这份文档的目的只有一个——**换一个人（或换一个模型）接手，读完就能继续干**。

| 项目 | 内容 |
|---|---|
| 项目代号 | 赛博日报 / Cyber Daily |
| 工作目录 | `/Users/Admin/Workspace/cyber-newspaper` |
| 当前阶段 | 样张验证通过（版式 + 语气），流水线未建 |
| 电子报成品 | `cyber-daily-2026-11-19.html`（单文件，48 KB） |
| 下次接手先看 | 第 10 节「遗留问题」、第 12 节「SKILL.md 草案」 |
| 用户原话 | **附录 D**（逐条原话 + 全部选项记录） |

---

## 目录

1. [原始需求](#1-原始需求)
2. [今天达成的共识](#2-今天达成的共识)
3. [调研：同类实现盘点](#3-调研同类实现盘点)
4. [五条工程教训](#4-五条工程教训)
5. [技术验证：今天真跑过的东西](#5-技术验证今天真跑过的东西)
6. [代码清单与函数说明](#6-代码清单与函数说明)
7. [产物清单](#7-产物清单)
8. [内容质量与事实核查记录](#8-内容质量与事实核查记录)
9. [已知问题](#9-已知问题)
10. [遗留问题与下一步](#10-遗留问题与下一步)
11. [附录 A：信源清单](#附录-a信源清单)
12. [附录 B：SKILL.md 草案](#附录-bskillmd-草案)
13. [附录 C：常用命令](#附录-c常用命令)
14. [附录 D：对话原文与选项](#附录-d对话原文与选项)

---

## 1. 原始需求

用户原话要点：

- **形态**：每天早上 9 点，到工位打开一份「赛博报纸」。要排版、大标题、作者、正文，精美、直观、可读，**跟真的报纸一样**。
- **内容**：地缘政治、时政大事、金融股市，加一些有趣的新闻。**必须和我的兴趣强相关**，我关注什么就呈现什么，内容可以通过 prompt 调整。
- **生产**：多 agent 分工——侦察、核实、撰稿、审稿。模型不限 DS，Grok / GPT 都行。
- **最终产物**：每天定时推送一个 HTML。

第一次回答里给出的判断：**这个想法不新，但组合是新的**。四个要素（9 点定时 / 强兴趣相关 / 多 agent 分工 / 真报纸版式）各自都有成熟参考，但没有一个现成项目能直接变成"装在这台 Mac 上、按你口味出版"的状态。结论是**抄架构、自己写排版和画像**。

---

## 2. 今天达成的共识

### 2.1 已确认的决策

| # | 议题 | 结论 | 备注 |
|---|---|---|---|
| 1 | 报纸结构 | **每个板块内部「先总后分」**：一个板块先抛一件事，再由它引出 2–3 路分析 | 中途纠正过一次：最初理解成"整份报纸一条主线"，被否决 |
| 2 | 版式差异化 | **每个板块风格不同**，不共用一套模板 | 用户原话："不要每个栏目都一个模版，那太枯燥了" |
| 3 | 语气分版 | 时政**严肃**、金融**夸张渲染**、科技**务实**、趣闻**妙趣横生** | 用户选定 |
| 4 | 报头 | **赛博日报**（英文 Cyber Daily） | 四选一 |
| 5 | 推送形态 | 本地单文件 HTML + PDF/可打印 + 邮件投递 | 多选，三样都要 |
| 6 | 插图 | 允许，但**优先确定性 SVG**，不用 AI 生图 | 贵、慢、风格每天漂移 |
| 7 | 现阶段优先级 | **先验证功能，推送和调度不着急** | 用户原话 |

### 2.2 仍未定的

| 议题 | 现状 | 建议默认值 |
|---|---|---|
| 运行环境 | 用户："这个再说" | 假定 Mac 常开，launchd 08:20 触发 |
| 核实强度 | 用户："先验证功能" | 结构化核对 + 置信度标注，不做双源交叉 |
| 每日阅读时长 | 用户未答，改成了"先说一件事再引发分析" | 按 5 分钟读完设计：4 版、每版 1200–1500 字 |
| 趣闻边界 | 未答 | 荒诞 / 冷知识 / 人物，不收明星八卦与段子 |
| 署名方式 | 未答 | 统一「本报编辑部」，每版可加一个虚拟编辑名 |
| 是否要「昨日回看」 | 未答 | 要。这是报纸区别于新闻聚合的唯一理由 |
| 双语 | 未答 | 目前只在「延伸阅读」里保留英文原题 |

### 2.3 一次关键的概念纠正

用户先说「我其实想要点，先说了一件事，然后引发各种分析」，被理解成**整份报纸围绕一件事**，做了一版「单主线」样张（头版事件 → 账本 → 棋局 → 技术 → 前例 → 反方）。

用户回复：**「不是啊。就是每个板块都是这样。总分。」**

即：结构单位是**板块**，不是整份报纸。这个纠正决定了后面所有版式设计——报纸仍然有四个板块，但每个板块内部是"一总多分"。

---

## 3. 调研：同类实现盘点

按接近程度排序。全部为 2026-11-19 检索到的真实项目。

| 项目 | 形态 | 最值得抄的地方 | 差距 |
|---|---|---|---|
| [openpaper](https://github.com/falense/openpaper) | Claude Code 插件，一条 `/openpaper` 出报 | **版式天花板**：blackletter 报头、多栏栅格、网点图、墨迹动效；把抓取固化成每个源一个 Python fetcher，之后不再调 AI；`preferences.md` 做画像 | 没有定时，要手动喊；没有核实环节 |
| [The Daily Crosswire](https://github.com/yamijuan/the-daily-crosswire) | 自托管 Web App，LangGraph 12 节点 | **流水线工程化**：跨期去重（URL + 标题指纹 + pgvector 余弦）、每条被淘汰的稿子都写 `drop_trace`、定时 + 邮件发 PDF、每天换谜题 | 重（Docker + Postgres + SearXNG），部署成本高 |
| [The Daily Brief](https://github.com/kawaiier/daily-brief) | launchd/cron + 纯 Python | **单文件自包含 HTML**（CSS / 字体 / 图片全内嵌）+ 每行勾选反馈回写 | 内容是工作流不是新闻；版式偏"简报"不偏"报纸" |
| [The AI Times](https://github.com/firstninja-v/the-ai-times) | Next.js + Python agents | 邮箱投递 + AirPrint 实体打印、暂停/恢复、每天换谜题 | 工程偏产品化，兴趣匹配较粗 |
| [AI Research Arm](https://github.com/guzus/ai-research-arm) | GitHub Actions 舰队 | **确定性渲染**：SVG→PNG，渲染路径里不放模型，版式永不漂移 | 只做 AI 主题，英文 |
| [morning-newspaper](https://github.com/DjangoPeng/agentic-ai/tree/main/morning-newspaper) | 中文，OpenClaw Skill | 三道 LLM 关口（标题粗筛 → 中文成稿 → Top10 精排），资讯流与事务流分离，飞书推送 | 偏"早报 dashboard"，不是报纸版式 |

学术侧对照：[The Daily Agent](https://app.readytensor.ai/publications/the-daily-agent-a-multi-agent-system-for-autonomous-newspaper-generation-uJcbxKaNYy7J)（多 agent 自动办报）。

### 3.1 两张参考图（已下载到本地）

- `refs/openpaper-hero.png` — OpenPaper 的版面样张。字体、留白、网点、墨迹，是"精美"的现实上限。
- `refs/ara-frontpage.png` — AI Research Arm 的头版。确定性 SVG 渲染，栅格严格，可复现。

两种美学路线：前者靠字体与质感，后者靠栅格与确定性。**本项目的选择：走前者的视觉，用后者的工程方式实现。**

### 3.2 检索环境的一个坑

`web_fetch` 对 `github.com` 报错 `URL hostname resolves to a non-public IP address`，`curl https://github.com` 也失败（SSL_ERROR_SYSCALL）。

**但 `raw.githubusercontent.com` 完全可达**。所以拉 README 的办法是：

```bash
curl -sS "https://raw.githubusercontent.com/<owner>/<repo>/main/README.md"
```

这个技巧后面还会用到（拉 skill 定义、拉模板文件）。

---

## 4. 五条工程教训

从上面这些项目里读出来的，写进了后面的设计约束。

1. **绝不让 LLM 直接写 HTML。**
   每天版式会漂、会崩、会溢出。正确姿势：LLM 只产出结构化 `story card` JSON，模板 + 确定性渲染器负责"好看"。openpaper、ARA、crosswire 全部这么干。

2. **抓取要固化，不要每次让模型即兴爬。**
   一次性为每个源写好抓取逻辑，之后纯脚本跑，快、可审计、可缓存。

3. **必须有跨期去重。**
   否则第三天你就会看到"同一件事换个标题"占掉头版。

4. **必须有淘汰记录。**
   你只看到 12 条，但当天可能进了 300 条。哪条为什么被砍，要能回溯，否则永远调不准口味。

5. **时间窗是硬约束。**
   今天实测发现：WSJ 的市场 feed 里还挂着 2025 年 1 月的「DeepSeek 冲击美股」。**不做发布时间过滤，头版就会登一年前的旧闻。**

---

## 5. 技术验证：今天真跑过的东西

这一节记录的是**实际执行过的命令和真实结果**，不是推测。

### 5.1 RSS 连通性（三批，30 个 URL）

可用（200 且能解析出条目）：

| 源 | Feed | 条数 |
|---|---|---|
| BBC World | `feeds.bbci.co.uk/news/world/rss.xml` | 33 |
| The Guardian | `theguardian.com/world/rss` | 45 |
| Al Jazeera | `aljazeera.com/xml/rss/all.xml` | 25 |
| NPR World | `feeds.npr.org/1004/rss.xml` | 10 |
| SCMP | `scmp.com/rss/91/feed` | 50 |
| 纽约时报中文网 | `cn.nytimes.com/rss/` | 20 |
| Financial Times | `ft.com/rss/home` | 11 |
| FT 中文网 | `ftchinese.com/rss/news` | 20 |
| WSJ Markets | `feeds.a.dj.com/rss/RSSMarketsMain.xml` | 20（**内容陈旧**） |
| WSJ Business | `feeds.a.dj.com/rss/WSJcomUSBusiness.xml` | 20 |
| The Economist | `economist.com/finance-and-economics/rss.xml` | 300 |
| 36氪 | `36kr.com/feed` | 30 |
| IT之家 | `ithome.com/rss/` | 60 |
| 少数派 | `sspai.com/feed` | 10 |
| Ars Technica | `arstechnica.com/feed/` | 20 |
| Hacker News | `hnrss.org/best` | ❌ 握手失败 |
| Quanta | `quantamagazine.org/feed/` | 5 |
| Phys.org | `phys.org/rss-feed/` | ❌ 超时 |
| Smithsonian | `smithsonianmag.com/rss/latest_articles/` | ❌ 握手失败 |
| Atlas Obscura | `atlasobscura.com/feeds/latest` | ❌ 握手失败 |
| 联合早报 | `zaobao.com/rss/realtime/china` | ❌ 非 XML（228 KB 但不是 feed） |

不可用 / 需付费：Reuters（404）、财新、澎湃、第一财经、界面、财联社、新浪财经（全部 404）、知乎（Cloudflare 403）、WSJ 中文 / Reuters 中文（401）。

> 注意：`hnrss / atlasobscura / smithsonian` 在 `curl` 里能拿到 200，但 Python `urllib` 报握手失败——是 TLS 指纹差异，不是网络不通。要补这几个源，得换 `requests` 或加 `curl` 子进程兜底。

### 5.2 行情接口

腾讯行情可用，纯文本、无需鉴权：

```bash
curl "https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,hkHSI"
# v_sh000001="1~上证指数~000001~3571.99~3587.83~...~20261119114400~-15.84~-0.44~..."
```

字段用 `~` 分隔：`[3]` 现价、`[4]` 昨收、`[30]` 时间、`[31]` 涨跌额、`[32]` 涨跌幅。

> 当前 `collect.py` 里 `collect_markets()` 的解析有 bug：`markets.indices` 返回空数组（应为字段索引或编码问题），**待修**。样张里因此没有用实时指数，避免编造数字。

### 5.3 本机环境

| 项 | 状态 |
|---|---|
| Node | v24.19.0 |
| pnpm | 11.22.0 |
| Python | 3.9.6（系统自带，无 uv、无 Pillow） |
| Chrome | 有（`/Applications/Google Chrome.app`），headless 截图与 `--print-to-pdf` 可用 |
| codex / claude / gemini / grok CLI | 均不在 PATH |
| `~/.codex/auth.json` | 存在（Codex 已登录，DSH 里有 `codex_ask` / `codex_review` 桥） |
| 环境变量里的 API key | 无 |

### 5.4 DSH 的调度能力（重要发现）

`dsh` CLI 不在 PATH，但存在：

```
/Applications/DeepSeek Harness.app/Contents/Resources/runtime/cli/bin/dsh
```

`dsh --help` 里有关键一行：

```
dsh headless "run the tests"    answer one task, print the result, and exit
```

**这意味着不用开 GUI 也能跑任务**——理论上 launchd 可以每天 08:20 调起 `dsh headless`，跑完整条流水线，9 点前产出 HTML。

但有一个当前未解的障碍：

```
$ dsh headless --help
Error: EPERM: operation not permitted, mkdir '/Users/Admin/.dsh/profiles/headless'
```

沙箱（workspace-write）不允许写 `~/.dsh/profiles/`。**没有验证过** headless 模式下：DS 凭据是否可用、skill 是否加载、codex 桥是否在。

> 这是整个项目里**唯一没有把握的环节**，接手后第一件事应该把它验掉。

### 5.5 渲染与截图

Chrome headless 截图（2 倍分辨率，2480×3508）：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1240,1754 \
  --user-data-dir=/tmp/cn-shot \
  --screenshot="$PWD/p1.png" "file://$PWD/p1.html"
```

**页面溢出检测技巧**（用来判断内容有没有超出 A4）：

```python
js = """
var m=0;
document.querySelectorAll('.page > *').forEach(function(e){
  if(e.classList.contains('footer'))return;
  var b=e.getBoundingClientRect(); if(b.bottom>m)m=b.bottom;
});
document.title='BOTTOM:'+Math.round(m);
"""
# 注入到 </body> 前，然后 --dump-dom 读 <title>
```

页高 1754、页脚线约 1728，`BOTTOM` 超过 1728 就会压字。

---

## 6. 代码清单与函数说明

### 6.1 `config/sources.json`（35 行）

结构：

```json
{
  "sources": [
    { "id": "ft", "name": "Financial Times", "url": "https://www.ft.com/rss/home",
      "channel": "finance", "weight": 0.9, "lang": "en" }
  ],
  "markets": {
    "indices": [{ "code": "sh000001", "label": "上证指数" }],
    "quote_api": "https://qt.gtimg.cn/q="
  }
}
```

- `channel` 决定版面归位：`world / china / finance / markets / tech / science / curious`
- `weight` 给打分用（FT 0.9 高于 IT之家 0.6）
- 21 个源，全部为已验证的公开 RSS

### 6.2 `pipeline/collect.py`（185 行，零依赖）

职责：RSS + 行情 → 一个统一 JSON。**不含任何模型判断。**

| 函数 | 说明 |
|---|---|
| `fetch(url, timeout=15)` | `urllib` 请求，带 UA / `Accept-Encoding: identity`；按 charset → utf-8 → gb18030 顺序尝试解码 |
| `plain(html, limit=600)` | 去标签、反转义、折叠空白，截断 |
| `text_of(node, *paths)` | 按多个路径取第一个非空文本，用于兼容 RSS/Atom 命名空间 |
| `parse_date(s)` | 先 `parsedate_to_datetime`（RFC 822），失败再试三种 ISO 格式，统一转 UTC ISO |
| `parse_feed(xml_text)` | 同时解析 RSS 2.0 的 `<item>` 和 Atom 的 `<entry>`，返回 `{title, url, summary, published, categories}` |
| `collect_markets(cfg)` | 调腾讯行情，按 `~` 切分取字段。**当前有 bug，返回空数组** |
| `main()` | `--date` / `--out`；逐源抓取，标注 `channel/weight/lang`；单源失败不影响整体，写入 `failures` |

输出：`data/raw/<date>.json`

```json
{
  "date": "2026-11-19",
  "counts": { "articles": 679, "sources_ok": 16, "sources_failed": 5 },
  "failures": [{ "source_id": "zaobao", "error": "ParseError: ..." }],
  "markets": { "indices": [] },
  "articles": [{ "title": "...", "url": "...", "summary": "...", "published": "...",
                 "source_id": "ft", "channel": "finance", "source_weight": 0.9 }]
}
```

实际运行结果：**679 条 / 16 源可用 / 5 源失败**。

### 6.3 `specimen/build.py`（537 行）

职责：手写四个版面的 HTML 字符串，输出 `p1.html` – `p4.html`。**这是样张，不是正式渲染器。**

关键设计：

| 部分 | 做法 |
|---|---|
| 纸张基底 | `#f4eee2` + `::after` 叠一层 `feTurbulence` 噪点（opacity .05），做出纸纹 |
| 分隔线 | `.rule`（1px 半透明）/ `.rule-h`（2px）/ `.dbl`（3px 双线）——三种层级对应三级信息分割 |
| 字体分工 | 正文 `Songti SC`；数字 `Didot`；标签/说明 `PingFang SC`；引语 `Kaiti SC` |
| 版头 | `.paperhead` 三段式：左"赛博日报·样张" / 中"板块名" / 右"第 N 版·日期" |
| 版记 | `COLOPHON` 常量：Cyber Daily 大字 + 采信数 / 抓取数 / 选用数 + "仅限一位读者订阅" |
| 页脚 | `.footer` 绝对定位，页码 |

四个版的核心差异：

| 版 | 栅格 | 视觉签名 | 语气 |
|---|---|---|---|
| P1 时政 | 4 栏：188 / 1fr / 1fr / 316 | 纯黑白、无彩色、竖排时间线、密排 | 克制，一句评论都不给 |
| P2 金融 | 黑底通栏 + 3 栏正文 + 右轨 | 112px `$81.3bn`、数据带、数字阶梯（83 / 813 / 15000 递增字号） | 敢渲染，短句 + 数字 |
| P3 科技 | 图示 + 2 栏 | 编号流程图（SVG）、术语表、对照表 | 像说明书，无感叹号 |
| P4 趣闻 | 双栏标题 + 3 栏正文 | 网点圆徽章、楷体导语、三条常识 | 轻，有包袱 |

### 6.4 `specimen/book.py`（231 行）

职责：把四个版面装订成可翻阅的单文件电子报 `edition.html`。

- `from build import BASE_CSS, P1..P4, COLOPHON` —— 复用样张内容，不重复维护
- 每个版面套一层 `.sheet`，绝对定位叠放，靠 `.active` / `.left` 做滑入滑出
- `layout(s)`：把 `#frame` 的宽高设为缩放后的尺寸，`#book` 用 `transform: scale(s)` + `transform-origin: top left`
  —— 这样缩放后仍能正确滚动（`transform` 本身不改变布局尺寸）
- `fit()`：非放大态取 `min(宽比, 高比)` 适配整页；放大态取 `(innerWidth-96)/1240` 适配宽度
- `toggleZoom()`：双击版面 / `+` `-` / `Esc` / 点 ⤢
- 键盘：`← →` 空格 `PageUp/Down` `Home End`
- 触屏：`touchstart/end` 判 `deltaX > 60`
- URL：`#2` 直达第 2 版（`history.replaceState` 同步）
- `noanim`：首帧禁用过渡，避免加载时闪一下
- `@media print`：`.sheet{position:static; break-after:page}`，`Cmd+P` 直接出 4 页 A4

---

## 7. 产物清单

```
cyber-newspaper/
├── cyber-daily-2026-11-19.html   ← 成品：可翻阅电子报（单文件 48 KB）
├── PROJECT.md                    ← 本文档
├── config/
│   └── sources.json              21 个信源 + 行情配置
├── pipeline/
│   └── collect.py                RSS + 行情采集（零依赖）
├── data/raw/
│   └── 2026-11-19.json           679 条原始素材（496 KB）
├── specimen/
│   ├── build.py                  四个版面的 HTML 生成器
│   ├── book.py                   装订成册 + 阅读器
│   ├── p1.html – p4.html         单版 HTML
│   ├── p1.png – p4.png           单版截图（2480×3508）
│   ├── edition.html              电子报（= 根目录那份）
│   └── _final.png                电子报整屏截图
└── refs/
    ├── openpaper-hero.png        参考：OpenPaper 版面
    └── ara-frontpage.png         参考：AI Research Arm 头版
```

### 7.1 四个版面各自的内容

| 版 | 标题 | 总起（一件事） | 分（分析） |
|---|---|---|---|
| 01 时政 | 机场的一次罕见迎接 | 习近平赴深圳机场迎接特朗普，APEC 开幕，今日中美俄三方会晤 | 东京被留在门外 / 海牙的另一张桌子 / 克里米亚大桥 / 一个数字 / 华盛顿的算盘 / 一个观察 + 记者手记三条 |
| 02 金融 | 一千亿美元，落在一群陌生人手里 | Anthropic 定价 83 美元，募资 813 亿，估值 1.5 万亿 | 孙正义的后悔 / 做空英伟达 / 估值的三把尺 / 读者三问 / 数字阶梯 / 时间线 |
| 03 科技 | 补丁跑得比测试快 | 微软、摩根大通等系统中断，专家归因于"AI 找 bug 太快" | 故障链条图 / 术语 / 对照表 / 回看 CrowdStrike 2024 / 三个提问 |
| 04 趣闻 | 一亿九千万，买一棵开花的栗树 | 梵高《盛开的栗树》拍出 1.904 亿美元 | 纳粹时期流转史 / 为什么总是梵高 / 边角料 10 条 / 拍卖行三条常识 / 三个数字 |

---

## 8. 内容质量与事实核查记录

### 8.1 素材来源

全部来自 `data/raw/2026-11-19.json` 当日真实抓取。数字类事实可追溯：

- Anthropic IPO：定价 83 美元、募资 813 亿美元、估值上限 1.5 万亿、超越 SpaceX（FT / Al Jazeera / BBC）
- 早期投资人兑现约 1000 亿美元（FT）
- 软银孙正义称"后悔"（FT）
- 浑水做空英伟达（36氪）
- 英伟达不恢复黄仁勋职务、临时 CEO 科莱特·克雷斯加薪（BBC / NPR / FT）
- 特朗普称中俄"天然的敌人"（SCMP）
- 高市早苗与习近平握手无对话（SCMP）
- 国际法院罗兴亚案、法官纳维·皮莱可能被制裁（Guardian / BBC / Al Jazeera）
- 罗兴亚流离失所 73 万人（Al Jazeera）
- 梵高《盛开的栗树》1.904 亿美元、作于 1890 年（BBC）
- 马斯克"我不是 MAGA"、近 5 亿美元"挺蠢的"（BBC / FT / Guardian）
- 尼日利亚机场 75 磅大麻案（Guardian）
- 泰国总理用粤语答"好开心"（SCMP）
- CrowdStrike 2024 年 7 月致约 850 万台 Windows 设备蓝屏（公开历史事实）

### 8.2 抓到的两个错（已修）

1. **梵高的地点错了。** 初稿写"画面是南方小镇阿尔的栗树"，但 1890 年梵高在奥维尔（Auvers-sur-Oise），不在阿尔。改成"画面上是开着花的栗树"，不写地名。
   → 教训：**一个看起来无害的地名，就是幻觉最容易钻进来的地方。**

2. **旧闻混入。** WSJ Markets feed 返回 2025-01-27 的"DeepSeek 冲击美股""阿拉比卡咖啡创纪录"。若不按 `published` 过滤，这些会直接登上头版。
   → 教训：**时间窗是硬过滤，不是排序偏好。**

### 8.3 哪些文字是"编辑"写的

样张里的分析性文字（记者手记、编注、三个提问、读者三问、估值三把尺）由本会话撰写，事实部分来自抓取。正式流水线里这些由 agent 产出——**质量会波动，这正是必须有审稿环节的原因**。

---

## 9. 已知问题

| # | 问题 | 严重度 | 说明 |
|---|---|---|---|
| 1 | `collect_markets()` 返回空 | 中 | 字段索引/编码问题，导致样张没有实时指数，只能不用 |
| 2 | 5 个源抓不到 | 低 | hnrss / atlasobscura / smithsonian 是 TLS 指纹问题（curl 能拿到），zaobao 不是标准 XML |
| 3 | 中文财经源缺失 | 高 | A股/港股盘面信息只能靠行情接口，RSS 侧基本空白 |
| 4 | 第 4 版底部空约 250px | 低 | 稿量不足，不是排版问题 |
| 5 | 整页预览时字号仅约 8px | 中 | A4 竖版在 1440×960 屏上必然如此，靠双击放大解决 |
| 6 | 字体依赖 macOS | 低 | 换 Windows 会退化成通用衬线 |
| 7 | `dsh headless` 未验证 | **高** | EPERM 无法建 profile；凭据、skill 加载、codex 桥均未验 |
| 8 | 无去重、无打分、无核实 | 高 | 目前 `collect.py` 之后全靠人（本会话）手工完成 |

---

## 10. 遗留问题与下一步

### 10.1 必须先验的（阻塞项）

**`dsh headless` 能不能在非 GUI 环境跑通一个任务。**

如果不行，"每天 9 点自动出报"就只能靠 GUI 常驻 + 会话内定时提醒，可靠性差很多。

验证方法：在沙箱外（或授权后）执行

```bash
dsh headless "在 /tmp 建一个 hello.txt，内容为 ok"
```

再验：能否加载自定义 skill、能否调用 `codex_ask`。

### 10.2 建议的实现顺序

1. **`score.py`** —— 去重（URL 指纹 + 标题归一化）+ 兴趣打分 + 频道归位，输出 `shortlist.json`
2. **`newsroom.schema.json`** —— 定死 story card 结构（见附录 B）
3. **`render.py`** —— 把 `build.py` 里手写的四个版面改造成「槽位 + 模板」，输入 story card 输出 HTML
4. **SKILL.md** —— 把编前会 / 侦察 / 核实 / 撰稿 / 审稿的契约写死（附录 B 已有草案）
5. **多 agent 编排** —— 侦察 4 路并行 → 核实 → 撰稿 → GPT 审稿（走 codex 桥）
6. **定时** —— launchd 08:20 + `pmset` 定时唤醒
7. **投递** —— macOS 通知 + 自动打开 + PDF + 邮件

### 10.3 两个备选方向

- **B｜先磨阅读体验**：默认放大、正文可点开原文、读报时点踩/收藏写回画像
- **C｜先扩信源**：补中文财经、补 TLS 兜底、接 X/Grok

判断：**A 优先**。版式和语气的"感觉"已经验证过，再磨 CSS 收益不大；真正没验证的是"agent 每天能不能写出这种质量"——这只有跑起来才知道。

---

## 附录 A：信源清单

| id | 名称 | 频道 | 权重 | 语言 | 状态 |
|---|---|---|---|---|---|
| bbc_world | BBC World | world | 0.85 | en | ✅ |
| guardian_world | The Guardian | world | 0.80 | en | ✅ |
| aljazeera | Al Jazeera | world | 0.80 | en | ✅ |
| npr_world | NPR World | world | 0.70 | en | ✅ |
| scmp | South China Morning Post | world | 0.85 | en | ✅ |
| zaobao | 联合早报 | china | 0.85 | zh | ❌ 非 XML |
| nytimes_cn | 纽约时报中文网 | china | 0.80 | zh | ✅ |
| ft | Financial Times | finance | 0.90 | en | ✅ |
| ftchinese | FT 中文网 | finance | 0.90 | zh | ✅ |
| wsj_markets | WSJ Markets | markets | 0.90 | en | ⚠️ 内容陈旧 |
| wsj_business | WSJ Business | markets | 0.85 | en | ✅ |
| economist | The Economist | finance | 0.90 | en | ✅ |
| 36kr | 36氪 | tech | 0.75 | zh | ✅ |
| ithome | IT之家 | tech | 0.60 | zh | ✅ |
| sspai | 少数派 | tech | 0.55 | zh | ✅ |
| ars | Ars Technica | tech | 0.70 | en | ✅ |
| hn_best | Hacker News | tech | 0.65 | en | ❌ TLS |
| quanta | Quanta Magazine | science | 0.85 | en | ✅ |
| phys | Phys.org | science | 0.65 | en | ❌ 超时 |
| smithsonian | Smithsonian | science | 0.70 | en | ❌ TLS |
| atlas | Atlas Obscura | curious | 0.80 | en | ❌ TLS |

---

## 附录 B：SKILL.md 草案

> 未落地成文件，验证 `dsh headless` 后再写进 `skills/cyber-daily/SKILL.md`。

````markdown
---
name: cyber-daily
description: >
  生成《赛博日报》——每天一份中文报纸，四个板块各自"先总后分"，四种语气。
  当用户说"出报纸""今天的报纸""赛博日报""生成早报"时使用。
---

# 赛博日报

## 板块单位，不是报纸单位
每个板块 = 一个总起 + 2-3 路分析。
报纸仍然是「时政 / 金融 / 科技 / 趣闻」四个板块。

## 硬契约
1. 每版必须回答一个别版回答不了的问题，且必须带来新事实
   （新数字 / 新当事人 / 新政策 / 新类比 / 真实的反方证据）。
2. 答不上来 → **撤版**，换成常规简讯。宁可今天只有 3 版。
3. LLM 只产出 story card JSON，**绝不直接写 HTML**。
4. 每条断言必须能对回原文；对不上的删掉，不写"据悉"。
5. 只收 12 小时内的内容。陈旧条目一律丢弃。

## 流程
0 编前会   读 preferences + 昨日反馈 → 今日选题单
1 侦察 ×4  按频道并行抓取 → candidates.json
2 去重打分 URL 指纹 + 标题归一化 + 兴趣权重 → shortlist.json
3 核实     逐条断言对回原文，标 confidence 与引文锚点
4 撰稿     story card JSON
5 审稿     事实 / 口吻 / 重复 / 标题党 → 打回重修
6 排版     模板 + 槽位规则 → 单文件 HTML
7 校验     链接可用、无溢出、字体回退、图片内嵌

## story card
```json
{
  "slot": "lead | second | rail | brief | bottom",
  "kicker": "地缘政治",
  "headline": "...",
  "standfirst": "...",
  "byline": "本报编辑部",
  "body": ["...", "..."],
  "shift": "总 | 分",
  "question": "本版回答的那个问题",
  "evidence": [{ "claim": "...", "source": "url", "quote": "..." }],
  "confidence": "high | medium | low"
}
```

## 语气
- 时政：克制。不评论。用事实排序代替形容词。
- 金融：敢渲染。短句 + 数字。允许一句判断。
- 科技：像说明书。编号、机制、对照表。不用感叹号。
- 趣闻：轻。有人物、有转折、最后一句留个包袱。
````

---

## 附录 C：常用命令

```bash
# 采集当天素材
cd /Users/Admin/Workspace/cyber-newspaper
python3 pipeline/collect.py

# 重新生成四个版面 + 电子报
cd specimen && python3 build.py && python3 book.py
cp edition.html ../cyber-daily-2026-11-19.html

# 截单版
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1240,1754 \
  --user-data-dir=/tmp/cn-shot --screenshot="$PWD/p1.png" "file://$PWD/p1.html"

# 打开电子报
open /Users/Admin/Workspace/cyber-newspaper/cyber-daily-2026-11-19.html
```

---

---

## 附录 D：对话原文与选项

> 本节是**逐字存档**，不做改写、不做压缩。所有决策都可回溯到这里。
> 用户消息按时间顺序排列；选择题单独列在 D.2。

### D.1 原话（按时间顺序）

#### ① 最初的完整需求

> 我想做一个agent/skill。功能是：每天早上9点给我呈现一份电脑上的报纸。
>
> 报纸的内容是：地缘政治，时政大事，金融股市，还有一些有趣的新闻。当然这个要和我的兴趣爱好强相关。我关注什么，他就呈现什么。这个内容要可以通过prompt调整。
>
> 形式：跟真的报纸一样。想象中，我就每天9点到工位，打开我的赛博报纸，阅读一下新闻。要有排版，大标题，作者，内容什么的。精美，直观，可读，报纸排版。就跟真的报纸一样。
>
> 怎么生成。比如一个agent负责搜集信息，一个agent负责核实信息，一个撰稿，一个审稿。这里的agent不限于ds，可以grok啊，gpt啥的都行。
>
> 最终产物：每天定时给我推送一个，比方说html。
>
> 你先去搜搜有没有类似或者一样的实现。然后看看目标上哪里还不清晰。然后我们再聊聊实现的方案。

#### ② 叫停搭建，要求先出样张

> 你先不要搭。还有什么问题。比如每个栏目呈现什么东西。你还有什么要问的？比如具体要写些什么？你可以给个示例，然后我看下感觉对不对

#### ③ 否决「整份报纸一条主线」

> 不是啊。就是每个板块都是这样。总分。

#### ④ 对视角与模板的态度

> 都可以。技术能达到的话还可以有插图。不要每个栏目都一个模版。那太枯燥了

#### ⑤ 两条连发的单字消息

> ？

> ？

（原文只有这两个问号，未作展开。对应的是结构理解上的分歧。）

#### ⑥ 确认分版语气

> 可以。就是说每个板块的风格可以不太一样。时政就可以严肃点。金融就可以夸张渲染点。科技可以务实点，轶闻就可以妙趣横生点。

#### ⑦ 要可翻阅的成品

> 给我一个能打开，甚至翻页 的html

#### ⑧ 要求落成文档

> 哦。你先落一份材料，或者skill出来。把我们今天的前因后果，你搜集到的资料，写到的函数，产出的结果。给写成一个完成的md。完事告诉我路径。

#### ⑨ 要求补全原话

> 你把我所有的原话，选择给加进去。

### D.2 选择题记录

三轮结构化提问，共 9 个问题。以下为**用户实际勾选/输入的内容**（原样保留）。

#### 第一轮：兴趣配方 / 推送形态 / 运行环境 / 核实强度

**兴趣配方（多选，勾中 6 项）：**

| 勾选 | 选项 |
|---|---|
| ✅ | 地缘政治与安全（中美关系、俄乌、中东、台海、出口管制） |
| ✅ | 美股与科技巨头（财报、估值、Mag7、IPO） |
| ✅ | A股 / 港股（国内股市、板块轮动、监管动向） |
| ✅ | 宏观与央行（利率、通胀、汇率、财政政策） |
| ✅ | AI 与前沿科技（模型发布、论文、算力、开源生态） |
| ✅ | 科学 / 历史冷知识（天文、生物、考古、数学趣题） |
| ⬜ | 创投与商业 |
| ⬜ | 科技产品与数码 |
| ⬜ | 社会奇闻与轻松趣闻 |
| ⬜ | 大宗商品 / 加密货币 |

> 注意：最终样张里仍然保留了一个"趣闻"版——这是为了验证版式，**不代表用户勾了"社会奇闻"**。要不要长期保留这个版，需要再确认。

**推送形态（多选，勾中 3 项）：**

| 勾选 | 选项 |
|---|---|
| ✅ | 本地单文件 HTML，自动打开（推荐） |
| ✅ | 同时生成 PDF / 可打印版 |
| ✅ | 邮件投递到邮箱 |
| ⬜ | 常驻本地网址，手机同网也能看 |

**运行环境（未选，自行输入）：**

> 这个再说，先验证功能。推送啥的不着急。

**核实强度（未选，自行输入）：**

> 先验证功能。

#### 第二轮：口吻 / 报头 / 份量

**口吻：** 分版不同：头版 B、财经 A、趣闻 C

> 对应方案：头版用「老编辑体」（有节奏、允许一句判断），财经用「通讯社体」（只陈述数字），趣闻用「冷幽默体」。

**报头：** 赛博日报

**份量（未选，自行输入）：**

> 我其实想要点，先说了一件事，然后引发各种分析。

> 这句话被误读为"整份报纸一条主线"，导致了下一轮的纠正。

#### 第三轮：报纸结构 / 视角清单

**报纸结构（未选，自行输入）：**

> 不是啊。就是每个板块都是这样。总分。

**视角清单（未选，自行输入）：**

> 都可以。技术能达到的话还可以有插图。不要每个栏目都一个模版。那太枯燥了

### D.3 每句话决定了什么

| 原话 | 落到了哪里 |
|---|---|
| 「每天早上9点…打开我的赛博报纸」 | 第 10 节：调度的硬约束（08:20 开跑，9:00 前出报） |
| 「要和我的兴趣爱好强相关…可以通过 prompt 调整」 | 第 2.2 节：兴趣画像未落地，`preferences.md` 仍是空的 |
| 「跟真的报纸一样…大标题，作者，内容」 | 第 6.3 节：四版式设计（报头 / 大标题 / 署名 / 正文） |
| 「一个agent搜集、一个核实、一个撰稿、一个审稿」 | 附录 B 的流程 1–5；第 9 节问题 8（目前全靠人工） |
| 「agent 不限于 ds，可以 grok、gpt」 | 第 5.3 节：本机只有 DS + Codex 桥；Grok 需 API key |
| 「先不要搭…给个示例，我看下感觉对不对」 | 直接催生了 `specimen/` 整个目录 |
| 「不是啊。就是每个板块都是这样。总分。」 | **改变了报纸的结构单位**：从"整份一条主线"改为"每版一个总分" |
| 「不要每个栏目都一个模版。那太枯燥了」 | 第 6.3 节：四个版四套栅格，不共用模板 |
| 「时政严肃、金融夸张、科技务实、轶闻妙趣」 | 第 2.1 节决策 3；四个版的语气分工 |
| 「给我一个能打开，甚至翻页 的html」 | `book.py` + `cyber-daily-2026-11-19.html` |
| 「先验证功能，推送啥的不着急」 | 第 10 节：调度与投递排到最后 |
| 「把我所有的原话…加进去」 | 本节 |

---

*文档生成于 2026-11-19，记录当日第一次工作会话。*
