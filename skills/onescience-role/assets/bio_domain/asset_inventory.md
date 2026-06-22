# Bio Domain Asset Inventory

本文件记录 `bio_domain` 当前资产分层，用于后续把 role 路由内容与可执行资产逐步拆开。

## 范畴路由层

这些文件负责选择生信范畴，不应直接执行代码：

- `SKILL.md`
- `bio-inference/SKILL.md`
- `onescience-models/SKILL.md`
- `workflows/SKILL.md`
- `data-foundation/SKILL.md`
- `analysis-tools/SKILL.md`
- `knowledge-databases/SKILL.md`
- `clinical-lab-quality/SKILL.md`
- `molecular-biology-design/SKILL.md`
- `cell-imaging-cytometry/SKILL.md`
- `population-phylo-evolution/SKILL.md`
- `translational-biomarker/SKILL.md`
- `experimental-protocol-automation/SKILL.md`

## 叶子任务卡

各范畴下的 leaf `SKILL.md` 目前用于记录具体生信任务的触发信号、输入协议、交接字段和风险点。

短期保留在 role 子树中，但按以下原则使用：

- 可以读取 leaf `SKILL.md` 来选择 `selected_concrete_skill`
- 可以从 leaf `SKILL.md` 抽取 `handoff_artifacts`
- 不把 leaf `SKILL.md` 宣称为顶层公开 skill
- 不让 leaf `SKILL.md` 直接替代 `onescience-coder`、`onescience-runtime` 或 `onescience-installer`

## references

`references/` 文件是领域判断和交接依据，可继续被 role 读取。

后续如果某份 reference 主要服务代码实现或运行诊断，应迁移或抽取到更合适的位置：

- 代码实现资产：`skills/onescience-coder/assets/`
- 运行和诊断契约：`skills/onescience-runtime/references/`
- 安装与环境契约：`skills/onescience-installer/references/`

## templates

剩余 `templates/` 文件当前只作为请求、handoff 或报告结构参考；bio-inference 官方运行 request / run manifest 已迁入 OneScience 仓库。

role 层使用规则：

- 只引用模板名称和字段形状
- 不在 role 层写入最终模板文件
- 不把模板当作已生成的运行配置

迁移候选：

- OneScience 官方示例 request、run manifest、workflow request 和执行工具归 OneScience 仓库
- agent handoff 模板归 runtime 资产
- 数据 / 分析计划模板可后续迁到 coder assets
- 报告 outline 和 metadata 模板可后续迁到领域 support assets

## scripts

`bio_domain` role 子树不再保留 `scripts/` 执行目录。

role 层使用规则：

- 不直接运行脚本
- 不保存脚本兼容副本
- 只把下游需要的资产路径写入 `handoff_artifacts`
- 代码实现、运行诊断和环境准备进入 `onescience-coder`、`onescience-runtime`、`onescience-installer` 或 OneScience 仓库内对应示例/工具目录

QA 要求：

- `skills/onescience-role/assets/bio_domain/**/scripts/` 不应存在
- leaf `SKILL.md` 的脚本引用必须指向 coder/runtime/installer 资产路径或 `{onescience_path}/onescience` 下的 OneScience 仓库资产
- 新增执行脚本时必须先选择目标资产层，不再放回 role 子树

## 已迁移资产

`bio-inference` 的 agent 交接模板保留在 runtime skill：

- `skills/onescience-runtime/assets/bio_inference_templates/bio_inference_handoff.yaml`

OneScience 官方推理 request、run manifest、manifest 校验和输出产物检查工具已归属 OneScience 仓库，不在 skill 层保留兼容副本：

- `{onescience_path}/onescience/examples/biosciences/_manifests/inference_run_manifest.yaml`
- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/*.yaml`
- `{onescience_path}/onescience/examples/biosciences/_manifests/tools/validate_bio_inference_manifest.py`
- `{onescience_path}/onescience/examples/biosciences/_manifests/tools/check_inference_outputs.py`

`analysis-tools/single-cell-toolkit` 与 `workflows/single-cell-rna-analysis` 的 scvi-tools / Scanpy / scRNA QC 脚本位于 coder 资产：

- `skills/onescience-coder/assets/bio_single_cell_tools/validate_adata.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/prepare_data.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/train_model.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/cluster_embed.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/differential_expression.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/transfer_labels.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/integrate_datasets.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/model_utils.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/qc_analysis.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/qc_core.py`
- `skills/onescience-coder/assets/bio_single_cell_tools/qc_plotting.py`

role 叶子卡只应把 coder 资产路径写入 `handoff_artifacts`，由 `onescience-skill -> onescience-coder` 决定是否读取资产并生成或改造任务脚本。

`workflows` 的执行/分析计划模板位于 coder 资产：

- `skills/onescience-coder/assets/bio_workflow_templates/screen_analysis_plan.yaml`
- `skills/onescience-coder/assets/bio_workflow_templates/long_read_run_plan.yaml`
- `skills/onescience-coder/assets/bio_workflow_templates/post_transcriptional_plan.yaml`
- `skills/onescience-coder/assets/bio_workflow_templates/rnaseq_contrast.yaml`
- `skills/onescience-coder/assets/bio_workflow_templates/rnaseq_metadata.csv`
- `skills/onescience-coder/assets/bio_workflow_templates/cohort_sample_map.tsv`

`protein_design_validation_request.yaml` 已归属 OneScience 仓库：`{onescience_path}/onescience/examples/biosciences/workflows/protein_design_validation/request.yaml`。

`onescience-models` 的模型和 datapipe/adapter 交接模板位于 coder 资产：

- `skills/onescience-coder/assets/bio_model_templates/model_handoff.yaml`
- `skills/onescience-coder/assets/bio_model_templates/datapipe_adapter_handoff.yaml`

role 只使用模板字段形状整理交接摘要；实现层读取 coder 资产路径。

`molecular-biology-design` 的轻量序列和结构检查脚本位于 coder 资产：

- `skills/onescience-coder/assets/bio_molecular_templates/crispr_design_request.yaml`
- `skills/onescience-coder/assets/bio_molecular_templates/plasmid_feature_table.tsv`
- `skills/onescience-coder/assets/bio_molecular_templates/plasmid_verification_plan.yaml`
- `skills/onescience-coder/assets/bio_molecular_templates/primer_request.yaml`
- `skills/onescience-coder/assets/bio_molecular_templates/restriction_map_request.yaml`
- `skills/onescience-coder/assets/bio_molecular_templates/rna_structure_request.yaml`
- `skills/onescience-coder/assets/bio_molecular_tools/pam_scan.py`
- `skills/onescience-coder/assets/bio_molecular_tools/sequence_design_checks.py`
- `skills/onescience-coder/assets/bio_molecular_tools/restriction_digest_report.py`
- `skills/onescience-coder/assets/bio_molecular_tools/dotbracket_stats.py`

role 只把这些工具作为可交接实现资产，不直接运行。

`population-phylo-evolution` 的轻量 QC 脚本位于 coder 资产：

- `skills/onescience-coder/assets/bio_population_templates/comparative_genomics_plan.yaml`
- `skills/onescience-coder/assets/bio_population_templates/pathogen_surveillance_metadata.csv`
- `skills/onescience-coder/assets/bio_population_templates/imputation_prs_manifest.yaml`
- `skills/onescience-coder/assets/bio_population_templates/phylo_analysis_plan.yaml`
- `skills/onescience-coder/assets/bio_population_templates/gwas_qc_manifest.csv`
- `skills/onescience-coder/assets/bio_population_tools/newick_qc.py`
- `skills/onescience-coder/assets/bio_population_tools/gwas_summary_qc.py`

role 只把这些工具作为可交接实现资产，不直接运行。

`cell-imaging-cytometry` 的轻量表格/label mask QC 脚本位于 coder 资产：

- `skills/onescience-coder/assets/bio_cell_imaging_templates/segmentation_plan.yaml`
- `skills/onescience-coder/assets/bio_cell_imaging_templates/wsi_tile_plan.yaml`
- `skills/onescience-coder/assets/bio_cell_imaging_templates/flow_panel_metadata.csv`
- `skills/onescience-coder/assets/bio_cell_imaging_templates/imc_analysis_plan.yaml`
- `skills/onescience-coder/assets/bio_cell_imaging_templates/image_dataset_manifest.csv`
- `skills/onescience-coder/assets/bio_cell_imaging_tools/label_mask_measurements.py`
- `skills/onescience-coder/assets/bio_cell_imaging_tools/cytometry_table_qc.py`

`data-foundation` 与 `translational-biomarker` 的轻量表格 QC 脚本位于 coder 资产：

- `skills/onescience-coder/assets/bio_table_templates/feature_matrix_manifest.yaml`
- `skills/onescience-coder/assets/bio_table_templates/generic_samplesheet.csv`
- `skills/onescience-coder/assets/bio_table_templates/biomarker_model_card.yaml`
- `skills/onescience-coder/assets/bio_table_templates/causal_genomics_plan.yaml`
- `skills/onescience-coder/assets/bio_table_templates/variant_prioritization_schema.tsv`
- `skills/onescience-coder/assets/bio_table_templates/liquid_biopsy_panel.yaml`
- `skills/onescience-coder/assets/bio_table_templates/pharmacogenomics_handoff.yaml`
- `skills/onescience-coder/assets/bio_table_qc_tools/matrix_metadata_check.py`
- `skills/onescience-coder/assets/bio_table_qc_tools/feature_table_leakage_check.py`
- `skills/onescience-coder/assets/bio_table_qc_tools/ctdna_vaf_panel.py`

`experimental-protocol-automation` 的实验协议和自动化模板位于 coder 资产：

- `skills/onescience-coder/assets/bio_protocol_templates/blot_quantification_layout.csv`
- `skills/onescience-coder/assets/bio_protocol_templates/liquid_handler_protocol.yaml`
- `skills/onescience-coder/assets/bio_protocol_templates/protocol_record.yaml`

`knowledge-databases` 的查询结构模板位于 coder 资产：

- `skills/onescience-coder/assets/bio_knowledge_templates/omics_database_query.yaml`
- `skills/onescience-coder/assets/bio_knowledge_templates/regulatory_query.yaml`

`clinical-lab-quality/qc-reporting-reproducibility` 的报告骨架模板位于 coder 资产：

- `skills/onescience-coder/assets/bio_report_templates/report_outline.md`

`clinical-lab-quality/lab-instrument-standardization` 的 ASM 转换、展平、校验和 parser 导出工具位于 coder 资产：

- `skills/onescience-coder/assets/bio_lab_quality_tools/convert_to_asm.py`
- `skills/onescience-coder/assets/bio_lab_quality_tools/flatten_asm.py`
- `skills/onescience-coder/assets/bio_lab_quality_tools/validate_asm.py`
- `skills/onescience-coder/assets/bio_lab_quality_tools/export_parser.py`

`protein-design-structure-validation` 的 SimpleFold/ESM 离线环境准备脚本已归属 OneScience 仓库：

- `{onescience_path}/onescience/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh`

role 只把这些工具作为 OneScience 示例资产引用，不直接运行。

## 后续治理顺序

1. 继续迁移 `templates/` 到 coder/runtime/installer 或后续 support assets。
2. 判断 leaf `references/` 是否仍属于 role 判断依据；若主要服务实现或运行诊断，应迁到对应执行层。
3. 每次迁移必须同步 leaf `SKILL.md`、引用路径和 QA case。
