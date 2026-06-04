---
name: bio-multiomics-systems-biology
description: 多组学整合、通路富集、系统生物学和代谢模型 workflow skill。用于 transcriptome/proteome/metabolome integration、GO/KEGG/Reactome/GSEA、MOFA、network、CellChat、COBRApy、SBML、flux balance 等任务。
---

# 多组学与系统生物学流程

## 使用边界

用于整合多个组学层或把结果映射到 pathway/network/model。若只是单一 RNA-seq 差异表达，先走 `rnaseq-differential-expression`。

## 推荐流程

1. 明确组学层：RNA、protein、metabolite、methylation、ATAC、single-cell、phenotype。
2. 统一样本、ID、批次、缺失值和 scale；记录 ID 映射规则。
3. 富集分析：选择背景集、ID 类型、ontology/pathway 数据库、方向性和多重检验。
4. 多组学模型：MOFA/DIABLO/similarity network 或 graph integration。
5. 系统生物：SBML/COBRA model、gene-protein-reaction、objective、constraints、FBA/FVA。
6. 输出：integrated matrix、factor/network/pathway result、model change set、figures。

## 交接物

```yaml
bio_task_family: multiomics-systems-biology
omics_layers:
sample_alignment:
id_mapping:
analysis_goal:
background_set:
database_or_model:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在没有背景基因集时解释富集 p 值。
- 不要混合不同 ID 空间而不记录映射损失。
- 代谢模型必须说明 objective 和约束来源。
