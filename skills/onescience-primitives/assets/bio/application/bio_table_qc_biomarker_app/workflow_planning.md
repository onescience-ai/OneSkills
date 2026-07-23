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
2. 选择对应模板和最小 Python QC 脚本，并确定用户输入、输出路径和脚本参数。
3. 从用户明确提供的项目目录创建或复用 `<project_dir>/app/`；复制选中的 `.py` 入口及其本地 Python 依赖闭包并保持相对结构，目标同名文件已存在时先比较内容，未经确认不得覆盖。
4. 静态分析复制后脚本的 import，把标准库、本地模块和第三方包分开，形成所需包及版本约束清单。
5. 在当前 Python 环境检查第三方包是否已安装、已安装版本是否满足约束，并以只读依赖解析检查安装或升级是否会破坏现有包约束。
6. 若依赖均已存在且兼容，跳过安装；若有已安装但版本冲突的依赖，报告包名、当前版本、要求版本和受影响包，等待用户选择环境隔离、调整版本或停止。
7. 若依赖缺失且解析无冲突，向用户说明待安装包、版本和目标环境并询问是否安装；得到明确同意后才可安装。若缺失依赖的安装会产生冲突，报告冲突和可选方案，由用户选择，禁止自动安装。
8. 依赖门禁通过后，coder 生成指向 `<project_dir>/app/` 内复制脚本的参数化命令或补全模板；runtime 使用用户已确认的输入执行轻量 QC。需要建模、因果推断或临床解释时转入后续分析流程。

# constraints

- 不得把研究评分当成诊断/治疗建议。
- 不得省略 split、endpoint、follow-up、batch、missingness。
- 不得省略 reference build、坐标系统、文件格式、accession 版本、配对关系或下载许可。
- 应用卡只提供模板和脚本入口，不直接代表已执行 QC。

# next_phase_recommendation

QC 或 manifest 检查通过后，可转入剪切/比对/区间处理、机器学习、ctDNA 纵向分析、因果推断或报告生成流程。

# fallback

若列名不确定，先生成列映射模板；若缺少临床 endpoint 或审核边界，只输出数据 QC 和待补字段。
