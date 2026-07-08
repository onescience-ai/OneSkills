# architecture_overview

该应用卡负责把生命科学表格数据和数据基础对象转为可校验的 manifest、样本表、模型卡、panel 或优先级 schema，并提供矩阵/metadata 一致性、特征泄漏和 ctDNA VAF 轻量检查。任务必须明确数据对象、格式、参考、下游分析、临床审核边界、队列划分、endpoint 和偏倚控制。

# parameter_scale

非固定模型规模。处理对象为 FASTQ/BAM/VCF/BED/FASTA/公共 accession 清单、samples x features、variants x annotations、timepoints x target loci 或 cohort x clinical endpoints 的二维表。

# architecture_structure

- `matrix_metadata_check.py`：检查 feature matrix 与 metadata 的样本 ID 对齐。
- `feature_table_leakage_check.py`：检查重复 ID、split 泄漏和 endpoint 缺失。
- `ctdna_vaf_panel.py`：根据 read count 计算 VAF 并生成低深度/低 alt count flag。
- `feature_matrix_manifest.yaml`、`generic_samplesheet.csv`：数据基础模板。
- `biomarker_model_card.yaml`、`liquid_biopsy_panel.yaml`、`causal_genomics_plan.yaml`、`pharmacogenomics_handoff.yaml`、`variant_prioritization_schema.tsv`：转化标志物模板。
- read-qc、alignment/BAM、public data ingestion、sequence IO、variant/interval 文件等数据基础任务在本卡中以 manifest、字段约束、QC checklist 和下游执行交接表示；实际剪切、比对、下载、坐标转换或文件重写由后续执行流程完成。

# input_schema

输入包括 data_object、file_formats、path_or_accession、reference_build、coordinate_convention、feature matrix、metadata、sample ID、endpoint、split、target loci read counts、panel 定义、clinical context、variant annotation 和 review boundary。FASTQ 任务需记录 read layout、adapter、UMI/barcode、trim strategy 和 QC reports；BAM/CRAM 任务需记录 aligner、sort/index 状态、read group、filter rules 和 mapping QC；公共数据接入需记录 accession、data type、sample metadata、download manifest、license/access 和 storage plan；序列读写需记录 input/output format、sequence type、operation、ID mapping 和 validation checks；VCF/BED/GFF 任务需记录 coordinate convention、normalization、merge/intersect/filter 操作和 genome build 一致性。

# output_schema

输出包括一致性 QC 报告、泄漏风险报告、VAF 表、data manifest、samplesheet、feature matrix manifest、文件处理 checklist、biomarker model card、liquid biopsy panel、causal genomics plan、pharmacogenomics handoff 和 variant prioritization schema。

# shape_transformations

metadata: samples x attributes
feature matrix: samples x features
  -> sample ID join/check
  -> split/endpoints validation
  -> QC flags

ctDNA counts: samples/timepoints x loci x counts
  -> VAF calculation
  -> depth/alt-count flags
  -> panel summary

data foundation objects: files/accessions x metadata
  -> manifest and validation checklist
  -> downstream execution handoff

# key_dependencies

- pandas 风格表格处理。
- 样本 ID、endpoint、split 和 batch 字段约定。
- reference build、coordinate system、accession/version、file format 和 storage/license 边界。
- read depth、alt count、VAF 的计算语义。
- 临床/研究边界说明。

# common_modification_points

- 样本 ID 列名、matrix orientation 和 feature ID 类型。
- data manifest 列、FASTQ/BAM/VCF/BED/FASTA 字段、坐标系统和 accession 映射。
- leakage 规则、split 级别和 endpoint 定义。
- ctDNA panel 阈值、纵向采样字段和 MRD 输出字段。
- biomarker model card 的指标、验证集和解释字段。

# implementation_risks

- 不可把研究型预测分数写成诊断或治疗建议。
- 不可忽略队列划分、事件定义、随访时间、批次、缺失值和外部验证。
- 不可混用 germline、somatic、cfDNA、bulk tumor 和 single-cell 证据层级。
- 不可混用不同 reference build、坐标系统、accession 版本或 FASTQ 配对关系。
- 不可把 manifest/checklist 生成等同于已经完成下载、剪切、比对、坐标转换或文件改写。

# code_references

- primitive 脚本目录：`assets/bio_table_qc_biomarker_app/script/`
- 模板资源目录：`assets/bio_table_qc_biomarker_app/script/bio_table_templates/`
- 脚本资源目录：`assets/bio_table_qc_biomarker_app/script/bio_table_qc_tools/`
- 语义来源标签：`data-foundation`
- 语义来源标签：`alignment-bam-processing`
- 语义来源标签：`expression-matrix-feature-tables`
- 语义来源标签：`public-data-ingestion`
- 语义来源标签：`read-qc-trimming`
- 语义来源标签：`samplesheet-metadata-design`
- 语义来源标签：`sequence-io-manipulation`
- 语义来源标签：`variant-interval-files`
- 语义来源标签：`translational-biomarker`
