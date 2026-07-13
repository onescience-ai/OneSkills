# 生信领域 Profile

本文档用于辅助 `skills/onescience-primitives/SKILL.md` 处理生信领域的知识检索与资源召回。它合并了生信工作流索引与资源路由提示，但只提供语义线索和候选资源建议。
最终是否命中、返回哪些内容，仍以 `assets/bio/**/metadata.json` 及对应资源文件为准。

## 使用原则

- 仅在 `detected_domain` 或调用方 `filters.domain` 明确指向生信领域时使用本文档；跨领域或领域不明时先按 `domain_profile.md` 完成领域判定。
- 本文档是召回提示，不是硬性规则。若用户请求、`metadata.json.description`、资源文件内容与本文档提示不一致，应优先相信实际资源证据。
- 单模型、单数据管线、单应用模板或单组件需求，优先直接在对应 category 下召回资源。
- 端到端、多步骤、需要任务分流或跨节点交接的需求，可结合 `workflow-planning` 资源与本文档的工作流提示进行召回。
- 涉及临床、用药、诊断、肿瘤或药物基因组时，只返回技术证据、候选优先级、质量记录和人工复核项，不给临床结论。
- 不要虚构不存在的 primitive。若需要的工具或模型不在 `assets/bio` 中，将其标记为外部依赖或资源缺口。

## 资源类型召回提示

- 需要模型推理、生成、打分或验证时，通常建议召回 `models` 下的 `model` primitive。
- 需要模型输入准备、数据标准、tokenization、feature pipeline、dataset adapter 时，通常建议召回 `datapipes` 下的资源。
- 需要模板、轻量脚本、QC 检查、报告骨架、交接文件或可复用小工具时，通常建议召回 `application` 下的资源。
- 需要实现细节、组件改造、调试、接口契约或模型内部结构时，通常建议召回 `components` 下的资源。
- 需要完整科研流程规划、节点依赖、质量检查和回退策略时，通常建议召回 `workflow-planning` 下的工作流资源。

## 通用应用资源提示

| 用户需求或任务信号 | 建议优先考虑的资源 |
|---|---|
| 样本表、contrast、long-read run plan、screen plan、通用流程模板 | `bio_workflow_template_app` |
| 单细胞 QC、整合、聚类、差异分析、标签迁移脚本 | `bio_single_cell_analysis_app` |
| feature matrix QC、biomarker model card、variant prioritization、ctDNA 或药物基因组交接 | `bio_table_qc_biomarker_app` |
| primer、CRISPR、plasmid、restriction map、RNA structure 设计与检查 | `bio_molecular_design_app` |
| cytometry、microscopy、WSI、IMC 模板和测量脚本 | `bio_cell_imaging_cytometry_app` |
| 文献、序列、通路、PPI、调控、结构、化合物或 atlas 数据库查询 | `bio_knowledge_query_app` |
| GWAS、PRS、phasing、pathogen surveillance、phylogeny、comparative genomics | `bio_population_phylo_app` |
| liquid handling、assay image quantification、protocol registry 或 ELN 交接 | `bio_protocol_automation_app` |
| ASM 风格实验室质量转换、验证、展平、导出解析 | `bio_lab_quality_asm_app` |
| 质量报告、复现报告和结果打包 | `bio_qc_report_app` |
| Python/R/Bioconductor、cheminformatics、mass spectrometry、统计可视化交接 | `bio_analysis_toolkit_app` |

## 模型资源边界

- `rfdiffusion` 更适合 backbone 生成、motif scaffolding、binder scaffold 和约束结构生成；最终序列设计通常还需要其他资源配合。
- `proteinmpnn` 更适合从 backbone 和固定位置约束设计蛋白序列；它不是结构预测模型。
- `alphafold`、`openfold`、`simplefold` 更适合蛋白序列到结构预测，或用于设计序列的回折叠验证。需要 PyTorch 训练或改造时可优先考虑 `openfold`；轻量实现或指定 SimpleFold 语境时考虑 `simplefold`。
- `alphafold3`、`protenix` 更适合蛋白-配体、蛋白-核酸、多分子复合物预测；不要默认套用 AF2/OpenFold 的输入协议。
- `evo2` 更适合长上下文 DNA/RNA/蛋白序列语言建模、序列生成、补全或变异效应辅助判断；它不是 variant caller、aligner 或结构验证器。
- `esm` 更适合蛋白序列 embedding、representation、head/transformer 特征提取；不能替代需要 3D 坐标的结构预测。
- `alphagenome` 仅在任务明确是 genome sequence-to-function 或 regulatory effect modeling，且资源召回证据匹配时考虑；不替代 read processing、variant calling 或临床解释。
- `molsculptor`、`pt_dit`、`protoken` 更适合用户明确请求对应分子或蛋白生成模型族，或资源内容确认接口匹配的场景。
- `diffdock`、`targetdiff`、`genscore` 等分子/结构相关模型应结合用户是否要求 docking、target-aware generation、scoring 或对应数据管线来判断。

## 数据管线资源提示

| 用户需求或任务信号 | 建议优先考虑的资源 |
|---|---|
| 基因组序列、变异、注释任务的数据基础 | `biology_genome_dataset` |
| 蛋白序列或结构任务的数据基础 | `biology_protein_dataset` |
| AlphaFold/OpenFold 风格特征准备 | `openfold_data_pipeline`、`biology_protein_dataset` |
| Protenix 或复合物推理输入准备 | `protenix_data_pipeline`、`biology_protenix_infer_adapter` |
| Boltz 兼容数据处理 | `boltz_data_pipeline` |
| ESM 序列 batching/tokenization | `esm_sequence_batch_converter` |
| SimpleFold 兼容数据准备 | `simplefold_data_pipeline` |
| DiffDock、TargetDiff、GenScore 等分子模型输入准备 | `biology_diffdock_dataset`、`biology_targetdiff_dataset`、`biology_genscore_dataset` |

## 工作流需求召回提示

以下内容来自工作流索引，但表达为软性召回建议。若用户只问某个单点模型、脚本或数据接口，不必强行召回完整工作流资源。

### `rnaseq-differential-expression`

Bulk RNA-seq、FASTQ/count matrix、DESeq2/edgeR/PyDESeq2、contrast、火山图、MA 图或热图需求，通常建议考虑召回 `rnaseq-differential-expression` 工作流资源。若用户需要样本表、contrast 或模板，可考虑 `bio_workflow_template_app`；若需要 Python/R/Bioconductor 交接或统计可视化，可考虑 `bio_analysis_toolkit_app`；若需要交付报告，可考虑 `bio_qc_report_app`。

边界提示：不要把 TPM/FPKM 当作 count 模型的原始输入；单细胞表达分析应转向单细胞相关资源。

### `variant-calling-interpretation`

Germline/somatic SNP/indel、CNV、SV、VCF 过滤注释、ClinVar/gnomAD/COSMIC 证据整理需求，通常建议考虑召回 `variant-calling-interpretation` 工作流资源。基因组数据基础可考虑 `biology_genome_dataset`；候选优先级、表格 QC、ctDNA 或药物基因组交接可考虑 `bio_table_qc_biomarker_app`；证据数据库查询可考虑 `bio_knowledge_query_app`；报告交付可考虑 `bio_qc_report_app`。

边界提示：不输出临床诊断；长读长变异任务通常先考虑长读长工作流或相关数据基础。

### `long-read-sequencing-analysis`

Nanopore/PacBio basecalling、read QC、long-read alignment、SV、Iso-Seq、direct RNA、methylation、phasing 需求，通常建议考虑召回 `long-read-sequencing-analysis` 工作流资源。运行计划或样本表可考虑 `bio_workflow_template_app`；基因组数据基础可考虑 `biology_genome_dataset`；若进入群体遗传、病原监测或系统发育分支，可考虑 `bio_population_phylo_app`。

边界提示：ONT raw signal、ONT FASTQ 和 PacBio HiFi 的质量指标不要混用。

### `genome-assembly-annotation`

Genome assembly、polishing、scaffolding、BUSCO、contamination、Prokka/eukaryotic annotation、ortholog 或 synteny 需求，通常建议考虑召回 `genome-assembly-annotation` 工作流资源。数据基础可考虑 `biology_genome_dataset`；比较基因组或系统发育后续分析可考虑 `bio_population_phylo_app`；质量报告可考虑 `bio_qc_report_app`。

边界提示：不要只用 N50 判断 assembly 质量；原核和真核注释分支需要区分。

### `epigenomics-regulation`

ATAC-seq、ChIP-seq、CUT&Tag、methylation、Hi-C、CLIP-seq、motif、peak、TAD/loop、GRN 需求，通常建议考虑召回 `epigenomics-regulation` 工作流资源。流程模板可考虑 `bio_workflow_template_app`；调控、通路或数据库查询可考虑 `bio_knowledge_query_app`；统计与可视化交接可考虑 `bio_analysis_toolkit_app`。仅当任务明确是 regulatory sequence-to-function 或 effect modeling 时，再考虑 `alphagenome`。

边界提示：单细胞 ATAC、空间调控或 multiome 任务可能需要联动空间多组学资源。

### `post-transcriptional-regulation`

Alternative splicing、Ribo-seq、small RNA/miRNA、CLIP/RBP、m6A、RNA modification 需求，通常建议考虑召回 `post-transcriptional-regulation` 工作流资源。流程模板可考虑 `bio_workflow_template_app`；基因组或注释数据基础可考虑 `biology_genome_dataset`；统计分析交接可考虑 `bio_analysis_toolkit_app`。

边界提示：不要把表达差异直接解释为剪接或翻译差异。

### `single-cell-rna-analysis`

10x、h5ad、Seurat、loom、scRNA/snRNA QC、整合、聚类、marker、注释、轨迹、scVI/scANVI 需求，通常建议考虑召回 `single-cell-rna-analysis` 工作流资源。脚本和模板可考虑 `bio_single_cell_analysis_app`；矩阵或元数据检查可考虑 `bio_table_qc_biomarker_app`；报告阶段可考虑 `bio_qc_report_app`。

边界提示：空间坐标、ATAC、CITE-seq 或 multiome 需求通常更适合空间多组学资源。

### `spatial-multiomics-analysis`

Visium、Xenium、Slide-seq、CITE-seq、RNA+ATAC multiome、MuData、WNN/MOFA/MultiVI/totalVI/DestVI 需求，通常建议考虑召回 `spatial-multiomics-analysis` 工作流资源。单细胞分析基础可考虑 `bio_single_cell_analysis_app`；图像、cytometry、WSI 或 IMC 相关部分可考虑 `bio_cell_imaging_cytometry_app`；多模态统计交接可考虑 `bio_analysis_toolkit_app`。

边界提示：图像分割本身可单独走成像应用；scRNA-only 任务通常走单细胞工作流。

### `functional-genomics-screens`

Pooled CRISPR/RNAi screen、Perturb-seq、DepMap、sgRNA count、MAGeCK/RRA、library QC 需求，通常建议考虑召回 `functional-genomics-screens` 工作流资源。Screen plan 或通用模板可考虑 `bio_workflow_template_app`；Perturb-seq 或单细胞分支可考虑 `bio_single_cell_analysis_app`；hit 表格、feature matrix 或 biomarker 交接可考虑 `bio_table_qc_biomarker_app`。

边界提示：screen hit 是候选，不等于机制证明。

### `protein-design-structure-validation`

RFdiffusion、ProteinMPNN、SimpleFold/OpenFold/AlphaFold/Protenix/AlphaFold3 验证、binder design、candidate ranking 需求，通常建议考虑召回 `protein-design-structure-validation` 工作流资源。按节点可考虑 `rfdiffusion`、`proteinmpnn`、`alphafold`、`openfold`、`simplefold`、`alphafold3`、`protenix` 以及对应数据管线。若需求是 primer、CRISPR、plasmid 或 RNA 结构设计，才考虑 `bio_molecular_design_app`；不要用它替代结构模型。

边界提示：RFdiffusion、ProteinMPNN 和 folding/complex prediction 模型角色不同，不要互换。

### `proteomics-metabolomics`

mzML/mzXML、DDA/DIA、peptide/protein inference、PTM、XCMS、MS-DIAL、metabolite annotation 需求，通常建议考虑召回 `proteomics-metabolomics` 工作流资源。质谱、统计或可视化交接可考虑 `bio_analysis_toolkit_app`；数据库查询可考虑 `bio_knowledge_query_app`；质量与复现报告可考虑 `bio_qc_report_app`。

边界提示：质谱差异丰度不等同于 RNA-seq 差异表达。

### `microbiome-metagenomics`

16S/ITS、shotgun metagenomics、eDNA、Kraken、MetaPhlAn、QIIME2、HUMAnN、AMR、strain tracking 需求，通常建议考虑召回 `microbiome-metagenomics` 工作流资源。分析工具交接可考虑 `bio_analysis_toolkit_app`；数据库查询可考虑 `bio_knowledge_query_app`；病原监测、系统发育或群体分支可考虑 `bio_population_phylo_app`；报告可考虑 `bio_qc_report_app`。

边界提示：低生物量、污染或数据库版本不明时，不应给强结论。

### `multiomics-systems-biology`

Transcriptome/proteome/metabolome integration、GSEA、MOFA、network、CellChat、COBRApy/SBML/FBA 需求，通常建议考虑召回 `multiomics-systems-biology` 工作流资源。Feature matrix、biomarker card 或整合表格 QC 可考虑 `bio_table_qc_biomarker_app`；通路、互作或数据库查询可考虑 `bio_knowledge_query_app`；各模态的前置处理应按实际数据类型召回对应工作流资源。

边界提示：整合前先完成各模态 QC；相关性不等于因果。

### `immune-repertoire-neoantigen`

TCR/BCR repertoire、VDJ、clonotype、scirpy/MIXCR、neoantigen、HLA/MHC binding、epitope ranking 需求，通常建议考虑召回 `immune-repertoire-neoantigen` 工作流资源。文献、序列、结构或免疫相关数据库查询可考虑 `bio_knowledge_query_app`；候选优先级和表格交接可考虑 `bio_table_qc_biomarker_app`；报告可考虑 `bio_qc_report_app`。若需要上游可信变异，通常应来自 `variant-calling-interpretation` 相关资源。

边界提示：binding score 不等于免疫原性或临床有效性。

## 跨工作流交接提示

- 长读长分析结果可交接到变异解释、基因组组装注释、转录后调控等需求。
- 变异解释结果可交接到免疫组库/新抗原、转化生物标志物、群体遗传或进化应用。
- 单细胞分析结果可交接到空间多组学、功能基因组筛选或多组学系统生物学。
- 表观调控分析可向多组学系统生物学交接 motif、peak-gene link、regulon 或其他调控特征。
- 蛋白设计与结构验证可消费分子设计、序列生成、结构生成和复合物预测资源的中间产物，并负责候选排序与质量记录。

## 检索质量检查

- 先确认请求已路由到生信领域，再选择 category scope；不要直接做全局模糊搜索。
- 若用户明确请求某个 primitive 名称，优先检查该资源是否真实存在，并读取其 `metadata.json` 判断语义是否匹配。
- 若本文档建议多个候选资源，先用用户请求中的对象、输入数据、交付物和当前任务阶段缩小范围。
- 若命中模型类资源且需要规格或使用说明，按 `SKILL.md` 的规则继续检查依赖组件和相关 `components`。
- `why_matched` 应说明用户需求与资源 `description`、category 或工作流语义之间的对应关系，避免只复述资源名。
- `limitations` 应来自资源文件中的约束、本文档边界提示或缺失文件说明；不确定时说明需要人工复核或外部依赖。
