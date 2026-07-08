# architecture_overview

该应用卡聚合湿实验核酸构件设计中的模板和轻量检查工具，覆盖 primer/probe、CRISPR 编辑、限制性酶切与克隆、质粒注释验证和 RNA 结构设计五类任务。应用层必须形成本地可交接的设计约束、候选表、检查结果和验证计划，不把任务降级成外部网页检索清单；涉及模型训练、蛋白/小分子生成或 OneScience 模型推理时应转入对应模型原语。

# parameter_scale

非固定模型规模。处理规模通常由 DNA/RNA 序列数、候选 primer/guide/enzyme 数量、质粒 feature 数、donor/amplicon 设计数量、RNA dot-bracket 或结构约束数量决定。

# architecture_structure

- `primer_request.yaml`：记录 PCR、qPCR、测序引物、TaqMan probe、molecular beacon、amplicon、Tm/GC、dimer/hairpin、SNP/repeat 避让和特异性检查约束。
- `crispr_design_request.yaml`：记录 sgRNA、Cas9/Cas12a、CRISPRa/i、base editing、prime editing、HDR donor、编辑窗口、off-target 过滤和验证引物交接字段。
- `restriction_map_request.yaml`：记录线性/环状拓扑、酶集合、单酶切/双酶切、兼容粘性末端、插入片段方向、模拟凝胶和克隆方案约束。
- `plasmid_feature_table.tsv`、`plasmid_verification_plan.yaml`：记录 promoter、ORF、terminator、origin、antibiotic marker、tag、fluorescent protein、restriction site、feature table 和测序/酶切验证计划。
- `rna_structure_request.yaml`：记录 RNA 序列、温度、盐条件、MFE、partition function、dot-bracket、base-pair probability、RNAcofold、SHAPE/DMS 约束、ncRNA 家族检索、sgRNA 可及性评估和 pseudoknot/modification/protein-binding 解释边界。
- `sequence_design_checks.py`、`pam_scan.py`、`restriction_digest_report.py`、`dotbracket_stats.py`：执行 GC/Tm/poly-X/PAM/酶切/dot-bracket 等轻量检查。

# input_schema

输入包括序列或 locus、物种或参考版本、assay context、目标区域、设计约束、筛选过滤器、验证计划和期望输出。CRISPR 任务必须给出 Cas 系统、编辑类型、PAM、编辑窗口和 off-target 策略；质粒/克隆任务必须给出拓扑、feature、酶集合和插入片段；RNA 结构任务必须给出序列、温度/盐条件和结构约束。禁止在没有目标序列、物种或参考版本时直接给最终 primer、probe 或 guide。

# output_schema

输出为候选 primer/probe/guide 表、筛选标记、PAM 位点表、off-target 待检查字段、酶切位点和片段报告、模拟凝胶字段、质粒 feature 与验证计划、RNA dot-bracket 摘要、RNA 结构工具交接字段以及下游实验验证 handoff。

# shape_transformations

FASTA/sequence records
  -> per-sequence candidate scan
  -> per-candidate metrics table
  -> filter flags and ranked candidates
  -> design handoff table or YAML request

# key_dependencies

- 标准核酸序列字符串和 FASTA/TSV/YAML 表示。
- 常见 Cas PAM 规则、常见限制性内切酶识别序列。
- 简化 Tm/GC/poly-X 规则和 dot-bracket 字符统计。

# common_modification_points

- Cas 系统和 PAM 规则扩展。
- primer/probe/guide 长度、GC、Tm、重复序列、dimer/hairpin、SNP/repeat 避让。
- base editing、prime editing、HDR donor、CRISPRa/i 和验证引物字段。
- 质粒 feature 字段、酶切/测序验证策略、插入方向和模拟凝胶字段。
- RNA 结构工具从轻量统计升级到 ViennaRNA、RNAcofold、SHAPE/DMS 约束或 ncRNA 家族检索。

# implementation_risks

- 轻量脚本不是完整 off-target 搜索或实验验证。
- 不可忽略 isoform、SNP、repeat、编辑窗口、donor 设计、质粒拓扑和目标区域版本。
- 不可把 dot-bracket 字符统计当作完整 RNA 热力学折叠或 RNA-RNA interaction 结果。
- 不可在未说明温度、约束来源、pseudoknot、RNA modification 或蛋白结合影响时比较 RNA 结构能量或可及性。
- 不可把自动筛选候选直接写成实验成功保证。

# code_references

- primitive 脚本目录：`assets/bio_molecular_design_app/script/`
- 模板资源目录：`assets/bio_molecular_design_app/script/bio_molecular_templates/`
- 脚本资源目录：`assets/bio_molecular_design_app/script/bio_molecular_tools/`
- 语义来源标签：`molecular-biology-design`
- 语义来源标签：`primer-probe-design`
- 语义来源标签：`crispr-guide-editing`
- 语义来源标签：`restriction-cloning-mapping`
- 语义来源标签：`plasmid-annotation-verification`
- 语义来源标签：`rna-structure-design`
