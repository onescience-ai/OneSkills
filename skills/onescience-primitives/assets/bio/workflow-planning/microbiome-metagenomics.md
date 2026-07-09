# 微生物组与宏基因组工作流

- workflow_id: `microbiome-metagenomics`

## 适用范围

用于 16S/ITS、shotgun metagenomics、eDNA、pathogen metagenomics、taxonomy、alpha/beta diversity、QIIME2、DADA2、Kraken、MetaPhlAn、HUMAnN、AMR、strain tracking 和 outbreak surveillance。

## 输入

- 必需：FASTQ 或 feature table；sample metadata；assay type；环境/宿主背景；reference database。
- amplicon 分支：primer、target region、ASV/OTU 策略。
- shotgun 分支：host genome、taxonomy/function database、AMR/strain 需求。
- 可选：negative controls、mock community、batch/run 信息。

## 输出

- ASV/OTU 或 taxonomic profile。
- taxonomy table、feature table。
- alpha/beta diversity、ordination plots。
- differential abundance table。
- functional profiles、AMR、strain tracking 或 outbreak summary。
- QC report。

## 流程节点

1. 判定 16S/ITS、shotgun、eDNA、pathogen surveillance、AMR 或 strain tracking 分支。
2. 做 read QC、adapter/primer trimming、host depletion、contamination/control 处理。
3. amplicon 分支生成 ASV/OTU 和 taxonomy。
4. shotgun 分支生成 taxonomy、functional profile、AMR 或 strain 结果。
5. 做 diversity、ordination、group comparison 和 differential abundance。
6. 输出数据库版本、表格、图和解释边界。

## 边界与分流

- 宿主或病原 variant-level 分析转到 `variant-calling-interpretation`。
- pathogen phylogeny 或 outbreak tree 可联动 `bio_population_phylo_app`。
- 16S ASV 结果不等于物种级绝对定量。

## 模型与工具选择边界

- amplicon：QIIME2/DADA2 风格 ASV 分支。
- shotgun：Kraken/MetaPhlAn/HUMAnN 风格 taxonomy/function 分支。
- AMR 和 strain tracking 使用专用数据库和工具。
- compositional data 分析不能直接解释 raw relative abundance。

## 质量检查

- read depth、negative controls、mock community。
- host depletion 和 contamination。
- database version。
- rarefaction/compositional assumptions。
- batch/run effect。

## 回退策略

- 缺 controls：标记污染风险，尤其低生物量样本不做强结论。
- read depth 不足：限制 diversity 和 rare taxa 解释。
- 数据库版本不明：暂停强 taxonomy/function 结论。

## 资源召回建议

- 工具交接：`bio_analysis_toolkit_app`。
- 数据库查询：`bio_knowledge_query_app`。
- pathogen surveillance/phylogeny：`bio_population_phylo_app`。
- 报告：`bio_qc_report_app`。
