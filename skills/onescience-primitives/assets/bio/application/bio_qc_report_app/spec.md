# architecture_overview

该应用卡以报告大纲模板为核心，用于把数据处理、QC、分析结果、可复现信息、临床研究方案草案和实验设计/功效说明组织成报告交付物。任务必须明确 task context、study/lab object、required inputs、standards/constraints、deliverable 和风险字段；报告必须包含输入、软件版本、参数、QC 图、结果表、日志、可复现命令或研究设计假设。

# parameter_scale

非模型原语。规模由分析模块数、图表数、样本数、endpoint 数、设计因子数和 QC checkpoint 数决定。

# architecture_structure

- `report_outline.md`：包含 Summary、Inputs、Methods、QC、Results、Limitations、Reproducibility 等结构，也可扩展为 protocol outline、study design、power assumptions、endpoint table、visit/assay plan 和风险清单。

# input_schema

输入包括任务背景、数据对象、QC 结果、图表路径、方法参数、软件版本、样本表、失败/过滤样本、日志、checksums、限制和审核边界。临床研究方案任务需给出 intervention/device/diagnostic、indication、study design、population、endpoints、assessments 和 statistics plan；实验设计/功效任务需给出 assay、primary endpoint、groups/covariates、replicate plan、power assumptions、batch/randomization 和 contrast plan。

# output_schema

输出为 Markdown 报告大纲、protocol outline、study design summary、power/risk assumptions、章节填充计划、图表清单、表格清单、manifest 和复现记录清单。

# shape_transformations

analysis artifacts
  -> section mapping
  -> report outline
  -> final report handoff

study design inputs
  -> endpoint/contrast mapping
  -> protocol or power outline
  -> review checklist

# key_dependencies

- QC 表、图、日志和参数记录。
- 数据来源、参考版本和软件版本。
- endpoint、population、replicate、batch、randomization、effect size 和 power assumptions。
- 人工审核和风险说明。

# common_modification_points

- 报告章节结构。
- 图表清单和 caption 风格。
- 合规/复现字段。
- 临床方案章节、入排标准、endpoint 表、样本量假设和统计计划。
- 与 data-analyzer 或文档工具的衔接。

# implementation_risks

- 不可把没有执行证据的分析写成已完成。
- 不可省略失败样本、过滤样本、缺失字段和人工审核边界。
- 不可把探索性图表包装成确认性统计结论。
- 不可给出临床诊断或治疗建议，不可把方案草案写成监管最终判断。
- 不可把 technical replicate 当成 biological replicate，不可忽略多重检验、batch 混杂或功效假设来源。

# code_references

- primitive 模板目录：`assets/bio_qc_report_app/script/bio_report_templates/`
- 语义来源标签：`clinical-lab-quality`
- 语义来源标签：`clinical-trial-protocol`
- 语义来源标签：`experimental-design-power`
- 语义来源标签：`qc-reporting-reproducibility`
