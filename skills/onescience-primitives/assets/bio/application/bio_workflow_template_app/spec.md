# architecture_overview

该应用卡承载端到端生信流程中可复用的结构化模板，用于把流程请求转成样本表、contrast、运行计划或分析分支配置。完整科研编排由 research-workflow 负责；本应用卡只提供模板资产、输入输出契约和执行前交接，需要写脚本或补配置时交给 coder，需要提交运行时交给 runtime。

# parameter_scale

非模型原语。规模由样本数、contrast 数、测序平台、分析分支、参考版本和输出类型决定。

# architecture_structure

- `rnaseq_metadata.csv`、`rnaseq_contrast.yaml`：bulk RNA-seq FASTQ/count matrix 到差异表达的样本表和 contrast 模板。
- `long_read_run_plan.yaml`：ONT/PacBio 平台、basecalling、QC、比对、SV/Iso-Seq/methylation/phasing 和输出模板。
- `cohort_sample_map.tsv`：germline/somatic variant calling、GVCF joint calling 或 cohort annotation 的样本映射模板。
- `post_transcriptional_plan.yaml`：alternative splicing、Ribo-seq、small RNA、CLIP、m6A 等分析分支模板。
- `screen_analysis_plan.yaml`：pooled CRISPR/RNAi/Perturb-seq 的 library、样本、count matrix、contrast、QC 和 hit calling 模板。
- 无专用模板文件的流程以 `pipeline_family`、`input_object`、`reference_build_or_database`、`workflow_stages`、`qc_checkpoints` 和 `expected_outputs` 字段生成骨架配置，覆盖 epigenomics、genome assembly/annotation、immune repertoire/neoantigen、microbiome/metagenomics、multiomics/systems biology、proteomics/metabolomics、single-cell、spatial multiomics 和 protein design validation。

# input_schema

输入包括 pipeline_family、input_object、organism_or_taxon、reference_build_or_database、sample_metadata、workflow_stages、qc_checkpoints、expected_outputs 和 execution_boundary。不同流程需补充 platform、library_strategy、contrast、caller_strategy、analysis_branch、screen_type、modalities、model_chain、tool_choices 或 report_requirements。

# output_schema

输出为 CSV/TSV/YAML 模板、流程配置交接、QC checkpoint 清单、工具选择草案、资源需求和 runtime 前置条件。

# shape_transformations

natural language pipeline request
  -> pipeline family routing
  -> structured sample/template files
  -> coder/runtime handoff

# key_dependencies

- 样本表、参考版本、分组/contrast 和批次字段。
- 测序平台和输入对象格式。
- pipeline 分支和 QC checkpoint。

# common_modification_points

- 新增流程模板。
- 扩展 contrast、分支和工具选择字段。
- 与具体工具应用卡、模型卡、数据卡或 research-workflow 编排知识建立引用关系。

# implementation_risks

- 不可把 template_only 配置当成已经可直接运行的 pipeline。
- 不可混用 scRNA-seq 与 bulk RNA-seq 矩阵语义。
- 不可混用 ONT raw signal、ONT FASTQ 和 PacBio HiFi 的 QC 指标。
- 不可混用 germline/somatic caller 和不同 reference build。
- 不可把蛋白设计模型链路、免疫信息学、多组学或空间组学的骨架配置当成已完成的端到端科研计划。

# code_references

- primitive 模板目录：`assets/bio_workflow_template_app/script/bio_workflow_templates/`
- 语义来源标签：`bio-pipeline-template`
- 语义来源标签：`epigenomics-regulation`
- 语义来源标签：`functional-genomics-screens`
- 语义来源标签：`genome-assembly-annotation`
- 语义来源标签：`immune-repertoire-neoantigen`
- 语义来源标签：`long-read-sequencing-analysis`
- 语义来源标签：`microbiome-metagenomics`
- 语义来源标签：`multiomics-systems-biology`
- 语义来源标签：`post-transcriptional-regulation`
- 语义来源标签：`protein-design-structure-validation`
- 语义来源标签：`proteomics-metabolomics`
- 语义来源标签：`rnaseq-differential-expression`
- 语义来源标签：`single-cell-rna-analysis`
- 语义来源标签：`spatial-multiomics-analysis`
- 语义来源标签：`variant-calling-interpretation`
