# 六版扩刊：来源与生成分工

成品：`cyber-daily-2026-11-19-sample-03.html`。新闻抓取完成：2026-11-19T17:33:08.692540+08:00；报价时间逐项保留。

| 指标 | 上一版 | 本版 |
|---|---:|---:|
| RSS入口 | 21 | 39 |
| RSS实际成功 | 20 | 36 |
| RSS候选 | 775 | 2664 |
| 实际采用来源记录 | 14 | 24 |
| 物理版面 | 4 | 6（时政2、财经2、科技1、艺文1） |
| LLM稿件字符 | 3386 | 6795（2.01倍） |

本版44个稿件块、64个段落；事实摘录24项。程序取18个行情标的、108个原始字段，重算36个单标的值与2个比较值。稿件由会话内GPT-6选题、摘录与撰写；没有独立审稿agent。

来源类型：{"document": 12, "rss_item": 11, "quotes": 1}。来源记录数不是独立媒体数，同一媒体不同文章分别记为记录。RSS候选时间统计：{"within_24h": 851, "older_than_24h": 1719, "missing_date": 30, "duplicate_url": 64}。

## 图片与古诗

梵高《盛开的栗树》直接取苏富比拍品档案公开图片，685425字节，SHA-256：`09b8881187526043bd28daa8b3c54a4e5af966f281a8d31f9d8205ad58e17356`，内嵌HTML。没有用SVG代替原作或AI重绘。王维《山居秋暝》采用维基文库公版原文，逐行核对；原文不计入LLM撰稿字符。艺术鉴赏、哲思与诗歌解读由LLM创作。

## X的实际状态

disabled，真实帖子0条，API请求0次。`pipeline/x_collect.py`支持官方API近期搜索和官方JSON导入，`config/x_sources.json`存查询与请求上限。需X开发者Bearer Token与可用额度；默认关闭，未发付费请求。API来源：https://docs.x.com/x-api/posts/search/introduction 。计费来源：https://docs.x.com/x-api/getting-started/pricing 。

## 可重现命令

```bash
python3 pipeline/sample_collect.py --edition 2026-11-19-sample-03
python3 pipeline/x_collect.py --out data/editions/2026-11-19-sample-03/x_status.json
python3 pipeline/render_expanded.py
node pipeline/preview_sample.mjs --edition 2026-11-19-sample-03
```

`editorial_changes.json`在前版原始稿件上扩写；渲染器输出完整`editorial.json`、`provenance.json`和单文件HTML。离线重渲染不访问网络。
