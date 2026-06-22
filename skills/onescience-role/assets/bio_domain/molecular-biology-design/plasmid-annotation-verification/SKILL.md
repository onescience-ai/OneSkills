---
name: bio-plasmid-annotation-verification
description: 质粒注释与构建验证 skill。用于 FASTA 或 GenBank 质粒序列的 promoter、ORF、terminator、origin、antibiotic marker、tag、fluorescent protein、restriction site 和 feature table 核对。
---

# 质粒注释与构建验证

## 使用边界

用于质粒图谱注释、构建核对、共享/提交前整理和批量质粒库检查。若用户需要酶切验证，读取 `../restriction-cloning-mapping/SKILL.md`；若需要 CRISPR 载体设计，读取 `../crispr-guide-editing/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_molecular_templates/plasmid_feature_table.tsv`：标准 feature table 字段。
- `onescience-coder/assets/bio_molecular_templates/plasmid_verification_plan.yaml`：构建验证、测序、酶切和功能元件核对模板。
- `references/plasmid_feature_qc.md`：常见质粒元件、拓扑、方向和提交前 QC。

## 推荐流程

1. 明确输入拓扑：circular plasmid、linear fragment、GenBank feature 是否可信。
2. 识别关键元件：origin、selectable marker、promoter、RBS/Kozak、ORF、tag/linker、terminator、barcode、lox/FRT、restriction/MCS。
3. 核对构建逻辑：方向、reading frame、start/stop codon、fusion junction、selection marker 与宿主兼容。
4. 输出构件交接：feature table、疑似缺失/冲突、验证 digest、Sanger primer 和共享元数据。

## 交接物

```yaml
bio_task_family: molecular-biology-design
molecular_task: plasmid-annotation-verification
plasmid_input:
topology:
host_or_expression_system:
expected_features:
detected_features:
qc_flags:
verification_plan:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在未知 circular/linear 拓扑时判断跨 origin 的 feature。
- 不要只输出“已注释”；必须列出 feature 坐标、方向、证据和 QC flag。
- 不要把 ORF 方向、fusion frame 和抗性标记兼容性留到执行层猜测。
