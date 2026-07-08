# architecture_overview

该应用卡把群体遗传、系统发育和演化基因组学中的可执行轻量检查与模板化计划合并为一个 application。任务必须区分样本亲缘、群体结构、系统树和传播链，且必须记录参考面板、基因组 build、群体来源和采样时间。

# parameter_scale

非固定模型规模。输入规模从单个 Newick 字符串到大型 GWAS summary 表、样本元数据表或多基因组比较计划不等。

# architecture_structure

- `newick_qc.py`：执行 Newick 括号、分支长度和基本树格式检查。
- `gwas_summary_qc.py`：检查 GWAS summary stats 的必要列、P 值范围和缺失情况。
- `phylo_analysis_plan.yaml`：记录比对、模型选择、bootstrap/rooting 和图形输出。
- `gwas_qc_manifest.csv`：记录样本、群体、表型、协变量、批次和文件路径。
- `comparative_genomics_plan.yaml`、`imputation_prs_manifest.yaml`、`pathogen_surveillance_metadata.csv`：作为对应分析场景的结构化交接模板。

# input_schema

输入包括 Newick/Nexus 树、GWAS summary stats、VCF/PLINK 元数据、样本表、群体标签、参考或比对、统计模型、采样时间和预期输出。

# output_schema

输出包括树格式 QC 报告、GWAS summary QC 表、分析计划 YAML、样本/群体 manifest、病原监测元数据表和下游执行交接。

# shape_transformations

tabular cohort metadata
  -> validation by required columns
  -> per-sample/per-variant QC flags
  -> analysis manifest

Newick text
  -> parse/check tree syntax
  -> branch/node summary
  -> QC status table

# key_dependencies

- CSV/TSV/YAML 结构化文本。
- GWAS summary stats 字段约定。
- Newick 树字符串格式。
- 群体/采样/参考版本元数据。

# common_modification_points

- GWAS 列名映射和等位基因字段。
- P 值、效应量、缺失率阈值。
- Newick 分支长度、bootstrap/posterior 等支持度字段处理。
- pathogen surveillance 采样时间、地点和 lineage 字段。

# implementation_risks

- 不可混淆 bootstrap、posterior probability、SH-aLRT 和 concordance factor。
- 未确认参考基因组、群体来源或采样时间时，不应解释 GWAS/填补/传播结论。
- 轻量 QC 不替代 PLINK/IQ-TREE/BEAST 等正式分析。

# code_references

- primitive 脚本目录：`assets/bio_population_phylo_app/script/`
- 模板资源目录：`assets/bio_population_phylo_app/script/bio_population_templates/`
- 脚本资源目录：`assets/bio_population_phylo_app/script/bio_population_tools/`
- 语义来源标签：`population-phylo-evolution`
