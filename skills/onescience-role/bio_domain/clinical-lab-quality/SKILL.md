---
name: bio-clinical-lab-quality
description: 生物信息临床、实验室与质量范畴路由。用于实验设计、样本量和功效、临床试验方案、实验仪器数据标准化、LIMS/ELN 交接、QC 报告、可复现报告和科研问题选择等生命科学邻域任务。
---

# 临床、实验室与质量范畴路由

当用户任务不属于模型或传统生信分析，但仍围绕生命科学研究设计、实验室数据、临床研究文档或质量交付时，使用本范畴。

## 具体 skill 路由

- 实验设计、样本量、功效、多重检验、批次设计：读取 `./experimental-design-power/SKILL.md`
- 临床试验方案、研究设计、终点、入排标准：读取 `./clinical-trial-protocol/SKILL.md`
- 仪器输出、LIMS/ELN、Allotrope/ASM、数据标准化：读取 `./lab-instrument-standardization/SKILL.md`
- QC 报告、可复现交付、Jupyter/Quarto/RMarkdown：读取 `./qc-reporting-reproducibility/SKILL.md`

## 交接规则

输出时至少整理：

- `task_context`
- `study_or_lab_object`
- `required_inputs`
- `standards_or_constraints`
- `deliverable`
- `risk_or_missing_fields`
- `execution_entry`
