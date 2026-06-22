---
name: bio-expression-matrix-feature-tables
description: 表达矩阵、特征表和稀疏组学矩阵基础 skill。用于 count matrix、TPM/CPM、feature x sample 表、gene ID mapping、metadata join、sparse Matrix Market、AnnData h5ad、loom、zarr 和下游 workflow 输入检查。
---

# 表达矩阵与特征表基础

## 使用边界

用于整理和验证以 feature x sample 或 observation x feature 形式存在的组学矩阵。若任务已经进入差异表达、单细胞聚类或标志物建模，分别读取 `../../workflows/rnaseq-differential-expression/SKILL.md`、`../../workflows/single-cell-rna-analysis/SKILL.md` 或 `../../translational-biomarker/biomarker-machine-learning/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/feature_matrix_manifest.yaml`：矩阵、feature 注释、样本元数据、ID 映射和下游入口模板。
- `references/matrix_format_rules.md`：count/normalized matrix、稀疏格式、ID 映射、metadata join 和常见风险。
- `onescience-coder/assets/bio_table_qc_tools/matrix_metadata_check.py`：检查 CSV/TSV 矩阵与 metadata 样本列是否一致。

## 推荐流程

1. 明确矩阵方向：feature x sample、sample x feature、cell x gene 或 long table。
2. 明确数值类型：raw counts、normalized counts、TPM/CPM、log scale、intensity、relative abundance。
3. 检查 ID：gene symbol、Ensembl、Entrez、protein accession、metabolite ID、重复 feature。
4. 连接 metadata：sample id 完全一致，保留 condition、batch、replicate、subject、timepoint。
5. 稀疏/容器：Matrix Market、h5ad、loom、zarr 需记录 layers、obs/var、counts 是否保留。
6. 输出：validated matrix、feature annotation、metadata、mapping report 和下游 workflow。

## 交接物

```yaml
bio_task_family: data-foundation
data_object: expression-matrix-feature-tables
matrix_path:
matrix_orientation:
value_type:
feature_id_type:
sample_metadata:
normalization_state:
validation_checks:
downstream_workflow:
execution_entry:
```

## 禁止事项

- 不要把 raw counts 和 log-normalized matrix 混用。
- 不要在 metadata join 后默默丢样本或重排样本。
- 不要用 gene symbol 直接合并跨物种或跨版本数据而不处理别名和重复。
