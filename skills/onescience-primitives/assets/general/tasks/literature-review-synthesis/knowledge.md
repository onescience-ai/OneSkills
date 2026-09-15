# 文献综述与引用综合 (literature-review-synthesis)

## 任务目标
执行系统性文献综述全流程：从多数据库检索、筛选、数据提取、质量评估、主题综合，到引文元数据提取/验证/BibTeX 格式化/Zotero 库管理，最终输出含已验证引用的专业 Markdown/PDF 综述文档。目标是可复现、引文准确、符合 PRISMA 标准的学术综述。

## 适用范围 / 不适用场景
适用：系统性文献综述、元分析（meta-analysis）、范围综述（scoping review）、研究现状综合、论文文献回顾章节撰写、研究空白识别、引文验证与 BibTeX 清洗、DOI/PMID/arXiv ID 到元数据的转换、Zotero 库的编程式增删改查与导出。
不适用：原始实验数据的统计分析（应转 statistical-analysis-eda）；实验设计与功效分析（应转 experimental-design-power-analysis）；无网络访问环境下的检索任务；非学术类文档撰写（品牌文案/内部沟通等）。

## 实体槽（Entity Slots）
- review_type：综述类型（systematic / scoping / narrative / meta-analysis）
- research_question：研究问题（PICO 或自由形式）
- databases：检索数据库列表（openalex / pubmed / google_scholar / arxiv / semantic_scholar / parallel-web）
- inclusion_criteria：纳入标准（年份范围、语言、研究类型、领域）
- exclusion_criteria：排除标准
- citation_style：引用格式（apa / nature / vancouver / chicago / ieee）
- zotero_library_id：Zotero 库 ID（user 或 group）
- zotero_api_key：Zotero API 密钥
- output_format：输出格式（markdown / pdf / bibtex）

## 输入输出契约
输入：研究问题/主题描述、纳入排除标准、目标数据库列表、引用格式要求、（可选）Zotero 凭据用于库集成、（可选）已有引文列表需验证。
输出：
1. 检索策略文档（每库检索式、日期、结果数量）；
2. PRISMA 流程图（标识 → 筛选 → 纳入各阶段计数）；
3. 筛选后纳入文献清单（含排除原因记录）；
4. 数据提取表（作者/年份/设计/样本/结局/效应量/质量评估）；
5. 主题综合正文（按主题组织而非逐文献摘要）；
6. 已验证 BibTeX 文件（经 validate_citations.py 通过，无高严重性错误）；
7. 最终 Markdown/PDF 综述文档（含完整参考文献列表）。

## 方法路线（可替换）
A. 多数据库系统检索路线：parallel-cli search（广覆盖学术域过滤）→ search_openalex.py（~250M 作品，无 API key）→ search_pubmed.py（生物医学权威，35M+）→ search_google_scholar.py（补充，易被限流）。最少 3 个库，记录所有检索式与日期。
B. 引文管理路线：extract_metadata.py（DOI/PMID/PMCID/arXiv/URL → 完整元数据）→ Web 搜索补缺字段（volume/pages/doi）→ format_bibtex.py --rekey --deduplicate（标准化+去重）→ validate_citations.py（完整性+DOI 验证）。
C. Zotero 集成路线：pyzotero 客户端连接 Zotero Web API v3 → zot.items(q=...) 检索库内条目 → create_items / update_item 管理条目 → add_parameters(format='bibtex') 导出 → 本地模式（local=True）或 CLI/MCP（Zotero 7）作为无 API key 替代。
D. 综合与写作路线：按主题（非逐文献）组织 → 比较/对比/识别模式 → 评估证据质量与一致性 → 标注研究空白 → 填充 review_template.md → generate_pdf.py 输出。

## 操作序列（Operations）
1. 定义研究问题与范围；制定纳入/排除标准并文档化。
2. 构建检索式（MeSH 词/布尔算符/同义词）；在 ≥3 个数据库执行检索，保存所有检索式、日期、结果数。
3. 去重合并检索结果（search_databases.py 或 format_bibtex.py --rekey --deduplicate）。
4. 标题/摘要筛选 → 全文筛选；记录各阶段计数与排除原因（PRISMA 流程）。
5. 数据提取：结构化表格提取关键信息（设计/样本/结局/效应量）；质量评估（risk-of-bias 或 AMSTAR 2）。
6. 元数据提取与补全：extract_metadata.py / doi_to_bibtex.py 转换标识符；对缺失 volume/pages/doi 执行 Web 搜索补全并记录来源。
7. BibTeX 格式化：format_bibtex.py 标准化键名、去重；validate_citations.py 检查完整性与 DOI 有效性。
8. Zotero 同步（若适用）：pyzotero 创建/更新条目到 Zotero 库；或从 Zotero 导出 BibTeX 用于综述。
9. 主题综合：按主题分组文献（非逐篇摘要）；比较对比、识别模式与矛盾；评估证据质量；标注研究空白。
10. 引文验证：verify_citations.py 对所有 DOI 最终验证；检查预印本是否已正式发表并更新。
11. 文档生成：填充 review_template.md → 生成 ≥1 张示意图（PRISMA 流程图/主题综合图）→ generate_pdf.py 输出 Markdown + PDF。

## 验证契约（Validations）
- 检索可复现：所有检索式 + 数据库 + 日期 + 结果数量已记录；他人可用相同策略重现。
- 引文完整性：每条 @article 含 volume / pages / doi（或 note 说明缺失原因）；validate_citations.py 零高严重性错误。
- DOI 有效性：validate_citations.py --check-dois 或 verify_citations.py 确认所有 DOI 可解析。
- 去重确认：同一文献不以不同 key 出现多次（format_bibtex.py --rekey 后检查）。
- PRISMA 计数一致：标识数 = 去重后数 + 重复数；筛选排除数 + 纳入数 = 去重后总数。
- 预印本已检查发表状态：若存在正式版本，引用期刊版而非预印本。
- 综合非逐篇摘要：正文按主题组织，跨文献比较/对比可见。
- 元数据视为不可信输入：citation key 验证 ^[A-Za-z0-9]+$；shell 命令用参数列表传递（非字符串拼接）。

## 资源引用（Resources）
- scripts/verify_citations.py：DOI 验证与格式化引文生成。
- scripts/generate_pdf.py：Markdown → PDF 转换（依赖 pandoc + LaTeX）。
- scripts/search_databases.py：检索结果处理、去重、格式化。
- scripts/search_openalex.py / search_pubmed.py / search_google_scholar.py：多库检索客户端。
- scripts/extract_metadata.py / doi_to_bibtex.py：标识符 → 完整元数据转换。
- scripts/format_bibtex.py / validate_citations.py：BibTeX 标准化与验证。
- scripts/generate_schematic.py：AI 驱动示意图生成。
- pyzotero 1.13+：Zotero Web API v3 Python 客户端（read/write/export/collections/tags/attachments）。
- references/core_workflow.md、search_and_citation.md、citation_styles.md、database_strategies.md、bibtex_formatting.md、citation_validation.md。
- assets/review_template.md、bibtex_template.bib、citation_checklist.md。
- 依赖：Python ≥3.9（pyzotero ≥3.10）, requests, scholarly（可选/Google Scholar）, parallel-cli（主要检索工具）, pandoc + texlive-xetex（PDF 生成）。
- 外部 API：api.openalex.org, api.crossref.org, eutils.ncbi.nlm.nih.gov, export.arxiv.org, api.datacite.org。
- Zotero 凭据：ZOTERO_API_KEY（必需）, ZOTERO_LIBRARY_ID（必需）, ZOTERO_LIBRARY_TYPE（可选，默认 user）。

## 前后置任务（Task Graph）
无强制前后置；作为通用方法层任务被各域复用。典型上游：研究问题定义（为实验设计或统计分析提供效应量依据）。典型下游：综述结果用于指导实验设计、确定分析框架、或支撑论文引言/讨论章节写作。引文管理子流程为综述写作的前置。

## 缺口与降级（Fallback / Gap）
- Google Scholar 被限流/封锁：降级为仅用 OpenAlex + PubMed 作为主要来源（覆盖已足够广），Google Scholar 仅作补充而非依赖。
- parallel-cli 不可用（无网络/无认证）：降级为直接使用各数据库 Python 脚本（search_openalex.py / search_pubmed.py），这些仅需 requests 库。
- Zotero API key 不可用：使用 pyzotero local 模式（local=True，Zotero 7 桌面端本地 API）或 Zotero CLI/MCP 进行只读检索；写入操作需 API key 无法降级。
- 元数据字段缺失（volume/pages/doi）：执行 Phase 2.5 Web 搜索补全；若确实无法找到，在 BibTeX note 字段记录缺失原因而非留空。
- pandoc/LaTeX 未安装（无法生成 PDF）：仅输出 Markdown 格式；提示用户安装 pandoc + texlive-xetex 后重试。
- 预印本未发表但需引用：标注为 preprint，注明服务器（bioRxiv/medRxiv/arXiv）与访问日期；后续检查发表状态并更新。
- 检索结果过多（>5000）：细化检索式（增加限定词/年份/研究类型过滤器）；或先用标题筛选缩小范围再全文筛选。
