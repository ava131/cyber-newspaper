# X信源适配器

`x_sources.json`保存关注账号、关键词与查询上限；`pipeline/x_collect.py`将官方API响应转为带作者、时间、原帖链接的新闻候选。它与RSS采集器是独立命令，尚未自动合并进入选题流程。本期样报没有使用X帖子。

## 离线导入

给定官方近期搜索API响应JSON，保留`data`和`includes.users`：

```bash
python3 pipeline/x_collect.py --import-json /absolute/path/response.json --out data/x/latest.json
```

解析与离线导入已通过本地样例验证，测试数据没有写入正式报纸。

## 实时搜索

需要X开发者账号的Bearer Token及可用额度。使用环境变量`X_BEARER_TOKEN`，不要把密钥放进配置或版本库；xAI/Grok的API Key不能代替X开发者凭证。将配置的`enabled`改为`true`后运行：

```bash
python3 pipeline/x_collect.py --live --out data/x/latest.json
```

只有同时具备`--live`、配置启用和环境变量，才会发起联网请求。目前上限为每次运行3个查询、每个查询10条结果；没有自动翻页，遇到401／402／403／429即停止。这个上限控制请求规模，并非货币预算。正式使用前，在开发者控制台设置适当的额度。

三个查询分别关注官方时政账号、美联储与市场账号、KV缓存／推测解码／vLLM讨论。用户可以在配置中调整账号清单。转发默认排除；热度指标随原帖保存，不能替代来源核实。

[官方近期搜索文档](https://docs.x.com/x-api/posts/search/introduction) · [官方计费文档](https://docs.x.com/x-api/getting-started/pricing)

X用于发现当事人发言、技术线索和讨论。进入报道前，仍应追到公告、论文、仓库或公司原文；帖子与正文事实各自保留来源。
