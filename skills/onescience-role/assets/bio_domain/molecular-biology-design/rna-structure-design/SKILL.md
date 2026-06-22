---
name: bio-rna-structure-design
description: RNA 二级结构、RNA-RNA interaction 和结构探针分析 skill。用于 ViennaRNA 风格 MFE、partition function、dot-bracket、base-pair probability、RNAcofold、SHAPE/DMS 约束、ncRNA 家族检索和 sgRNA 可及性评估。
---

# RNA 结构设计与分析

## 使用边界

用于 RNA folding、ncRNA 结构、sgRNA/siRNA accessibility、RNA-RNA interaction、ribozyme 或 aptamer 设计，以及 SHAPE/DMS 结构探针结果解释。若用户请求蛋白结构预测，回到 `../../onescience-models/protein-structure-prediction/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_molecular_templates/rna_structure_request.yaml`：记录 RNA 序列、温度、盐条件、约束和输出类型。
- `references/rna_structure_methods.md`：MFE、partition function、cofold、consensus folding、SHAPE/DMS 约束和解释边界。
- `onescience-coder/assets/bio_molecular_tools/dotbracket_stats.py`：统计 dot-bracket 长度、配对数、茎区和未配对比例。

## 推荐流程

1. 明确 RNA 类型：mRNA UTR、ncRNA、sgRNA、siRNA、ribozyme、aptamer、viral RNA 或 RNA pair。
2. 明确输入：序列、alignment、约束、温度、是否需要互作或保守结构。
3. 分析层级：MFE 结构、ensemble/partition、base-pair probability、accessibility、cofold interaction。
4. 如果有 SHAPE/DMS，先做 reactivity QC，再作为 soft/hard constraints。
5. 输出：dot-bracket、MFE、paired/unpaired summary、关键区域可及性、候选结构和限制说明。

## 交接物

```yaml
bio_task_family: molecular-biology-design
molecular_task: rna-structure-design
rna_input:
analysis_mode:
constraints:
temperature_or_conditions:
candidate_structures:
accessibility_regions:
validation_data:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把单个 MFE 结构当成唯一真实构象；需要说明 ensemble 不确定性。
- 不要在未说明温度和约束来源时比较能量差。
- 不要忽略 pseudoknot、RNA modification 和蛋白结合对结构的影响。
