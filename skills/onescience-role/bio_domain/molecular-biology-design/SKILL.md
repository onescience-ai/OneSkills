---
name: bio-molecular-biology-design
description: 分子生物学设计与验证范畴路由。用于 PCR/qPCR 引物探针、CRISPR sgRNA pegRNA donor、限制性酶切和克隆图谱、质粒注释、RNA 二级结构和结构探针等实验设计任务，选择具体 skill 并生成可执行交接物。
---

# 分子生物学设计与验证范畴路由

当用户目标是设计或验证湿实验中的核酸构件、克隆方案或 RNA 结构时，使用本范畴。若任务转为模型训练、蛋白/小分子生成或 OneScience 模型推理，回到 `../onescience-models/SKILL.md`。

## 具体 skill 路由

- PCR、qPCR、测序引物、TaqMan/分子信标探针、引物二聚体和特异性检查：读取 `./primer-probe-design/SKILL.md`
- CRISPR knockout、CRISPRa/i、Cas9/Cas12a、base editing、prime editing、HDR donor 和 off-target 评估：读取 `./crispr-guide-editing/SKILL.md`
- 限制性酶切位点、单/双酶切片段、克隆酶选择、质粒消化图谱：读取 `./restriction-cloning-mapping/SKILL.md`
- 质粒 FASTA/GenBank 注释、功能元件核对、构建验证、提交或共享前的 feature table：读取 `./plasmid-annotation-verification/SKILL.md`
- RNA MFE/partition function、dot-bracket、RNA-RNA interaction、SHAPE/DMS 约束、ncRNA 家族检索：读取 `./rna-structure-design/SKILL.md`

## 交接规则

输出时至少整理：

- `molecular_task`
- `input_sequence_or_locus`
- `organism_or_reference`
- `assay_context`
- `design_constraints`
- `screening_filters`
- `validation_plan`
- `expected_outputs`
- `execution_entry`

## 禁止事项

- 不要在没有目标序列、物种或参考版本时直接给最终引物或 guide。
- 不要把 off-target、SNP/repeat 避让、isoform 选择和质粒拓扑当成可选细节。
- 不要把实验设计 skill 写成外部网页检索清单；必须形成本地可交接的设计约束和结果表结构。
