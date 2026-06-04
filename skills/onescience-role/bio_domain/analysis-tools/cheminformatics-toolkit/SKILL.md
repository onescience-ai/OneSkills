---
name: bio-cheminformatics-toolkit
description: 化学信息学工具 skill。用于 RDKit、Datamol、SMILES/SDF/MOL2、分子标准化、descriptor、fingerprint、Tanimoto、SMARTS 子结构、Lipinski、反应枚举、药物样库过滤和分子可视化。
---

# 化学信息学工具箱

## 使用边界

用于小分子数据处理和筛选。若用户要 OneScience 小分子生成或优化模型，进入 `onescience-models/molecular-design`。

## 推荐流程

1. 明确输入：SMILES、SDF、MOL、CSV、compound ID。
2. 标准化：sanitize、largest fragment、charge neutralization、canonical SMILES、dedup。
3. 描述符：MW、LogP、TPSA、HBD/HBA、rotatable bonds、ring count。
4. 指纹与相似性：Morgan/ECFP、MACCS、Tanimoto。
5. 过滤：Lipinski、PAINS、SMARTS、custom substructure。
6. 输出：cleaned SMILES、descriptor table、similarity hits、images。

## 交接物

```yaml
tool_family: cheminformatics
input_format:
standardization_rules:
descriptor_or_fingerprint:
filter_rules:
reference_compound:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要忽略盐、互变异构、电荷和无效 SMILES。
- 不要把 docking score 或相似性直接解释为药效。
