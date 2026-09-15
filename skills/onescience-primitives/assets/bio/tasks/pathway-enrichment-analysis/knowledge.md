# 通路富集分析 (pathway-enrichment-analysis)

## 任务目标
对基因列表或排名基因数据执行通路/基因集富集分析，回答"我的基因集中哪些生物学通路、GO 术语或基因集被过度代表？"。覆盖两种核心方法：ORA（过代表分析，Fisher/hypergeometric 检验）和 preranked GSEA（全排名基因集富集），以及 ssGSEA/GSVA 单样本评分。工具链以 gseapy（Enrichr 后端）和 g:Profiler 为主，输出经 FDR 校正的富集结果表与可视化。

## 适用范围 / 不适用场景
适用：差异表达基因（PyDESeq2/edgeR/limma/Scanpy）的功能注释；CRISPR 筛选命中基因的通路分析；聚类 marker 基因富集；蛋白质组学命中基因集注释；GO/KEGG/Reactome/WikiPathways/MSigDB Hallmark 富集；ssGSEA/GSVA 单样本通路活性评分。
不适用：原始通路/互作 API 查询（Reactome、KEGG、STRING — 应使用 database-lookup）；轻量单次 Enrichr 查询（gget enrichr 更轻便）；网络分析/模块检测（应使用 networkx）；基因调控网络推断。

## 实体槽（Entity Slots）
- organism: 物种（human/mouse/...），决定基因符号大小写与库选择
- method: 分析方法（ora / prerank-gsea / gsea / ssgsea / gsva）
- gene_sets: 基因集库列表（如 MSigDB_Hallmark_2020, GO_Biological_Process_2023, KEGG_2021_Human, Reactome_2022）
- gene_id_type: 输入基因 ID 类型（symbol / ensembl / entrez），Enrichr/MSigDB 要求 symbol
- background: 背景基因集（ORA 用，应为实验中可检测到的基因而非全基因组）
- fdr_cutoff: FDR 阈值（默认 0.05）
- rank_metric: GSEA 排名指标（推荐 DESeq2 `stat`；备选 `sign(LFC)*-log10(pvalue)`）
- seed: GSEA 随机种子（确保可重复，如 123）

## 输入输出契约
输入：
- ORA：阈值化基因列表（如 padj < 0.05 的 gene symbols，每行一个，human UPPERCASE）
- GSEA：全基因排名序列（Series: gene_symbol → score，降序排列，无阈值截断）
- 或 DESeq2 results CSV（含 stat 列，用于自动构建排名）
- 可选：自定义背景基因文件（ORA 用）

输出：
- ORA 结果表：Gene_set, Term, Overlap, Adjusted P-value, Combined Score, Genes 列
- GSEA 结果表：Term, ES, NES, NOM p-val, FDR q-val, Lead_genes 列
- 可视化：dotplot、barplot、enrichment map、GSEA running-score plot
- 发表用表格：经冗余缩减、代表性 term 筛选后的精选结果

## 方法路线（可替换）
路线 A（ORA，离散命中列表）：`gp.enrichr(gene_list, gene_sets=[...], organism="human")` — Fisher exact 检验，Enrichr 固定背景；或 g:Profiler `gp.profile()` 支持自定义背景（`domain_scope='custom'`）。
路线 B（Preranked GSEA，全排名列表）：`gp.prerank(rnk=ranked_series, gene_sets=[...], min_size=15, max_size=500, permutation_num=1000, seed=123)` — 基于 Kolmogorov-Smirnov 统计量检测基因集是否集中在排名顶部/底部。
路线 C（ssGSEA/GSVA，单样本评分）：`gp.ssgsea()` / `gp.gsva()` — 为每个样本/细胞生成通路活性评分矩阵。
路线 D（离线/自定义 GMT）：`gp.enrich(gene_list, gene_sets=local.gmt, background=custom_list)` — 无网络依赖。

## 操作序列（Operations）
1. 安装：`uv pip install gseapy gprofiler-official`；验证可用库 `gp.get_library_name(organism="human")`
2. 确定方法与输入：有阈值列表→ORA；有全排名+score→GSEA；绝不可阈值截断后喂 GSEA
3. 基因 ID 转换：若输入为 Ensembl/Entrez，转换为 gene symbol（human UPPERCASE, mouse Title-case）；使用 `gp.Biomart`、g:Profiler `g:Convert` 或 mygene
4. 选择基因集库：根据生物学问题选 2-4 个库（Hallmark=广泛主题, GO:BP=机制, KEGG/Reactome=策展通路）；不贪多
5. 设定背景（ORA）：背景=实验中可检测/已测试的基因集，非全基因组；g:Profiler 用 `domain_scope='custom'`
6. 执行分析：ORA `gp.enrichr(...)`；GSEA `gp.prerank(rnk, gene_sets, permutation_num=1000, seed=123)`；或使用 `scripts/run_enrichment.py ora/gsea` CLI
7. FDR 过滤：ORA 用 `Adjusted P-value < 0.05`；GSEA 用 `FDR q-val < 0.05`；检查 Overlap/gene count 排除仅 1-2 基因命中的假阳性
8. 可视化：`gp.dotplot()`、`gp.barplot()`、`gp.enrichment_map()`、`gp.gseaplot()`
9. 冗余缩减：GO 近重复 term 用 enrichment map / leading-edge overlap / parent term 折叠，报告代表性条目
10. 记录复现元数据：库名+版本日期、GSEA seed、permutation_num、organism

## 验证契约（Validations）
- 基因 ID/物种必须匹配：symbols vs Ensembl、human vs mouse 大小写 — 静默 ID 不匹配是"nothing is significant"的首要原因
- GSEA 输入必须为完整排名列表（无阈值截断）；ORA 输入必须为阈值化离散列表
- GSEA 排名推荐用 `stat`（DESeq2 test statistic）而非单独 log2FoldChange（低计数基因 LFC 不稳定）
- FDR 在单库内计算；跨多库运行时测试数倍增，需保守报告 per-library FDR
- 显著性 ≠ 相关性：检查 Overlap 基因数和基因集大小，tiny sets（< 15 基因）轻易达显著但无生物学意义
- ORA 输入列表长度：< 10 基因功效不足；> 2000 基因丧失特异性（考虑 GSEA）
- Enrichr/GO 库有版本漂移：记录库名+访问日期，设置 GSEA seed 确保可重复
- 背景设定错误会膨胀显著性：Enrichr 使用固定背景，需自定义时用 g:Profiler 或 `gp.enrich(background=...)`

## 资源引用（Resources）
- gseapy 文档: https://gseapy.readthedocs.io/
- gseapy GitHub: https://github.com/zqfang/GSEApy
- g:Profiler: https://biit.cs.ut.ee/gprofiler/
- gprofiler-official (Python): https://pypi.org/project/gprofiler-official/
- Enrichr: https://maayanlab.cloud/Enrichr/
- MSigDB: https://www.gsea-msigdb.org/gsea/msigdb/
- GSEA 方法学: Subramanian et al. (2005) PNAS, DOI: 10.1073/pnas.0506580102

## 前后置任务（Task Graph）
- 前置：无强制前后置（基因列表来源多样：DE 分析、筛选、聚类 marker）
- 后置：富集结果可衔接 scientific-visualization（自定义图表）或 scientific-writing（发表叙述）

## 缺口与降级（Fallback / Gap）
- 无网络访问（Enrichr/g:Profiler 不可达）：使用本地 GMT 文件 + `gp.enrich()` 离线 ORA
- 基因 ID 映射失败（非模式物种）：尝试 g:Profiler 的 g:Convert（支持 500+ 物种）或 mygene；极端情况降级为手动映射表
- ORA 命中列表过短（< 10 基因）：功效不足，降级为 GSEA（使用全排名）或扩大阈值放宽列表
- ORA 命中列表过长（> 2000 基因）：丧失特异性，改用 GSEA 利用排名信息
- Enrichr 速率限制/超时：重试或切换至 g:Profiler（不同后端）；离线 GMT 为最终降级
- GSEA 无 stat 列：构建替代排名 `sign(log2FoldChange) * -log10(pvalue)`
- 冗余 GO term 过多难以解读：使用 enrichment map 网络聚类 + 报告每簇代表 term
