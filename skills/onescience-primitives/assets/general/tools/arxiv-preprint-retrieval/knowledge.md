# arXiv 预印本检索与全文获取 (arxiv-preprint-retrieval)

## 定位与适用任务
预印本与论文元数据搜索（标题/作者/摘要字段语法）、PDF 或 HTML 全文下载、LaTeX 源码获取。
是多源文献证据检索任务的预印本全文通道。

## 访问方式与鉴权
arXiv API 经封装脚本：search_arxiv.py（--query 支持 au:/ti:/abs: 前缀与布尔、--id_list 直取、
--start/--max_results 分页、--sort_by relevance|lastUpdatedDate|submittedDate 配 --sort_order）、
download_paper.py（--format pdf|html）、download_paper_source.py（tar.gz）；无需 key。

## 核心操作模式
- 限流硬约束：最多 1 请求/3 秒，脚本自动执行，禁止自写请求绕过。
- 搜索输出必须重定向落盘：100+ 结果的 JSON 会爆上下文；--max_results 控在 5–10。
- 全文下载后校验非空未损坏；HTML 仅较新论文可用。
- 源码解包必须进专用新目录（mkdir paper_source && tar -xzf source.tar.gz -C paper_source），
  禁止直接解到工作目录。

## 输出契约与关键字段
搜索 JSON 字段：id/title/summary/published/authors/pdf_url/primary_category/doi/journal_ref/comment；
doi 字段仅含外部 DOI（仅 arXiv 自发 DOI 时不返回）。

## 限流与合规
遵循 arXiv API 条款与使用政策；输出须列所用论文 URL 并声明来源。

## 常见坑与降级
doi 字段为空不等于论文无 DOI（可能仅 arXiv 自发）→ 经 OpenAlex 补解析；
PDF 损坏 → 重试或改 HTML；源码档案目录结构不可信 → 专用目录解包后审查。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 literature_search_arxiv 技能；
上游条款见 info.arxiv.org/help/api。
