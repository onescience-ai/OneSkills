# architecture_overview

该应用卡负责把通用生信工具请求转为明确的工具族、输入格式、操作目标、依赖边界和预期输出。适用于脚本级或包级任务，例如 Biopython/pysam/cyvcf2/scikit-bio/Bio.PDB、R/Bioconductor、RDKit/Datamol、PyOpenMS/OpenMS/matchms、统计检验和可视化方案；端到端科研流程由 research-workflow 编排。

# parameter_scale

非模型原语。规模由输入文件数量、数据矩阵大小、分子数量、质谱峰/feature 数、统计比较数量和图表数量决定。

# architecture_structure

- `bio_tool_handoff.yaml`：通用工具选择和执行交接模板，用于记录 tool_family、packages、input_format、operation、quality_checks、expected_outputs 和 execution_boundary。
- Python 生信工具分支：面向 FASTA/FASTQ/GenBank/PDB/BAM/VCF、Entrez/BLAST、Bio.PDB、pysam、cyvcf2、scikit-bio 等脚本设计。
- R/Bioconductor 分支：面向 DESeq2、edgeR、limma、tximport、Seurat、SingleCellExperiment、GenomicRanges、clusterProfiler、ComplexHeatmap、RMarkdown/Quarto 等工具选择。
- 化学信息学分支：面向 RDKit、Datamol、SMILES/SDF/MOL2 标准化、descriptor、fingerprint、Tanimoto、SMARTS、Lipinski、反应枚举和分子可视化。
- 质谱工具分支：面向 mzML/mzXML/mzTab/idXML/featureXML、feature detection、RT alignment、spectral similarity、peptide/protein identification 和 metabolite annotation。
- 统计可视化分支：面向多重检验、PCA/UMAP、volcano、MA、heatmap、survival、regression、batch correction、SHAP 和 QC dashboard。

# input_schema

输入包括 tool_family、packages、input_format、operation、data_size、reference_or_database、statistical_design、visualization_type、quality_checks、expected_outputs 和 execution_boundary。Python 生信任务需记录文件格式、索引/流式读取需求和外部 API/工具限制；R/Bioconductor 任务需记录输入对象、design formula、contrast、annotation source 和 Bioconductor 版本；化学信息学任务需记录 standardization rules、descriptor/fingerprint、filter rules 和 reference compound；质谱任务需记录 MS level、search/library database、feature/identification strategy 和 FDR/annotation level；统计可视化任务需记录 data matrix、grouping/covariates、statistical test、multiple testing 和 interpretation limits。

# output_schema

输出为工具选择 YAML、脚本/API 设计说明、输入输出字段契约、质量检查清单、图表规格、统计解释边界和后续执行建议。

# shape_transformations

natural language tool request
  -> tool family selection
  -> package/API or CLI interface contract
  -> quality checks and expected output schema
  -> coder/runtime handoff

# key_dependencies

- 输入格式、数据规模和索引能力。
- Python/R/化学/质谱/统计工具包及其版本。
- 外部数据库、API key、rate limit、reference build 或 library database。
- 统计设计、分组/contrast、批次和多重检验方法。

# common_modification_points

- 新增工具包或 API 接口。
- 扩展输入格式、输出字段和质量检查。
- 将常用片段沉淀为可运行脚本。
- 与单细胞、表格 QC、知识库查询、报告应用卡建立交接。

# implementation_risks

- 不可用手写正则解析复杂生物格式，优先使用结构化解析库。
- 不可把 log-normalized data 当 raw counts，不可把相关性或相似性解释成因果或药效。
- 不可在缺少 FDR、annotation level、Bioconductor 版本、NCBI rate limit 或 reference build 时给出强结论。
- 不可把工具选择模板当成已经完成端到端分析或正式统计验证。

# code_references

- primitive 模板目录：`assets/bio_analysis_toolkit_app/script/bio_analysis_toolkit_templates/`
- 语义来源标签：`analysis-tools`
- 语义来源标签：`python-bio-toolkit`
- 语义来源标签：`r-bioconductor-toolkit`
- 语义来源标签：`cheminformatics-toolkit`
- 语义来源标签：`mass-spectrometry-toolkit`
- 语义来源标签：`statistics-visualization`
- 关联应用标签：`single-cell-toolkit-down`
