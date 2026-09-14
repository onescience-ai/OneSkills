# 多源文献证据检索 (multi-source-literature-evidence-retrieval)

## 任务目标
给定研究问题、作者/机构名或 DOI 列表，跨 OpenAlex（主索引）、arXiv（预印本全文）、bioRxiv 与
EuropePMC（生物侧补充）检索论文元数据与全文证据，产出可回溯的来源 URL 清单与许可声明。

## 适用范围 / 不适用场景
适用：论文检索、DOI 解析、开放获取 PDF 下载、作者/机构出版物与计量聚合（被引、h-index、按年分组）。
不适用：全文内容理解与综合（下游任务）；付费墙破解；无许可全文的再分发。

## 实体槽（Entity Slots）
- evidence_source：openalex / arxiv / biorxiv / europepmc。
- retrieval_mode：metadata（元数据概览）/ fulltext-pdf（全文）/ bulk-doi（≤100 批量 DOI 解析）。

## 输入输出契约
输入：自然语言问题、名称或 ID/DOI 列表。输出：slim 后的 results.json（--select 限字段）、
所用论文 URL 清单、每篇许可核验注记；全文 PDF 落盘并校验非空未损坏。

## 方法路线（可替换）
OpenAlex 主索引：resolve（名称→ID）→ filter（ID 过滤）两步法，禁止按名称直接 filter；
--search 全文检索成本为 --filter 的 10 倍，仅概览用。arXiv 取预印本全文（≤1 请求/3 秒）。
bioRxiv/EuropePMC 作生物医学侧互证源；跨源命中交集作为证据强度信号。

## 操作序列（Operations）
1. resolve 名称到 ID（多候选时出示 display_name+hint 供人选）；2. filter 加 --select --per-page 5–10
   落盘后 jq 瘦身；3. 需聚合时 --sort / --group-by；4. 需全文时 download-pdf 或 arXiv download_paper；
5. 汇总报告列出全部所用 URL 与来源声明。

## 验证契约（Validations）
- 禁止虚构 ID/DOI：空结果如实报告并建议换词（--search 零命中最多重试 3 次放宽术语）。
- 401/429 → 走凭据协议申请 API key；403 → 提示套餐升级。
- 每篇 retrieved 论文须核验其自身许可限制；输出必须列来源 URL。

## 资源引用（Resources）
- tools/openalex-literature-search-access：主索引、计量与 DOI 解析。
- tools/arxiv-preprint-retrieval：预印本元数据与 PDF/HTML/LaTeX 源。

## 前后置任务（Task Graph）
无强制前后置；作为各域研究任务的证据前置广泛复用。

## 缺口与降级（Fallback / Gap）
无 OpenAlex key → polite pool 低预算，压缩查询量并优先 get/filter；PDF 损坏 → 回退替代 pdf_url；
premium-only 过滤字段（from_updated_date/to_updated_date）无 key 不可用 → 改用其他过滤维度。
