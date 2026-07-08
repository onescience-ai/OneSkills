# description

把表格型生信和转化标志物请求转为 QC、模板化交接和临床审核边界。

# when_to_use

用于 FASTQ/BAM/VCF/BED/FASTA/公共 accession manifest、表达矩阵/metadata 对齐、samplesheet 设计、biomarker model card、ctDNA VAF panel、causal genomics plan、pharmacogenomics handoff 和 variant prioritization schema。

# inputs

- data_object、format、reference_build、path_or_accession。
- file layout、coordinate convention、accession/version、download manifest、trim/filter/merge/intersect plan。
- translational_question、cohort context、assay source、clinical endpoint。
- split、batch、missingness、external validation 和 review boundary。

# outputs

- QC 报告。
- 模板或 schema。
- 数据基础 manifest、字段校验清单和下游执行交接。
- 需要下游建模/解释的 handoff。

# procedure

1. 判断任务属于 data foundation 还是 translational biomarker。
2. 选择对应模板和轻量 QC 脚本。
3. coder 生成参数化命令或补全模板。
4. runtime 执行轻量 QC。
5. 需要建模、因果推断或临床解释时转入后续分析流程。

# constraints

- 不得把研究评分当成诊断/治疗建议。
- 不得省略 split、endpoint、follow-up、batch、missingness。
- 不得省略 reference build、坐标系统、文件格式、accession 版本、配对关系或下载许可。
- 应用卡只提供模板和脚本入口，不直接代表已执行 QC。

# next_phase_recommendation

QC 或 manifest 检查通过后，可转入剪切/比对/区间处理、机器学习、ctDNA 纵向分析、因果推断或报告生成流程。

# fallback

若列名不确定，先生成列映射模板；若缺少临床 endpoint 或审核边界，只输出数据 QC 和待补字段。
