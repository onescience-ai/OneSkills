---
name: bio-single-cell-rna-analysis
description: 单细胞 RNA-seq 分析 workflow skill。用于 10x/h5ad/Seurat 对象的 QC、过滤、归一化、批次整合、聚类、marker、细胞类型注释、轨迹和 scVI/scANVI 等单细胞任务。
---

# 单细胞 RNA 分析流程

## 使用边界

用于 scRNA-seq 或 snRNA-seq。若用户有空间坐标、ATAC、蛋白标签或 multiome，转到 `spatial-multiomics-analysis`。若只是工具包 API 问题，可转到 `analysis-tools/single-cell-toolkit`。

## 可复用资源

- `onescience-coder/assets/bio_single_cell_tools/qc_analysis.py`：标准 scRNA-seq QC 命令行脚本，支持 h5ad 和 10x h5 输入。
- `onescience-coder/assets/bio_single_cell_tools/qc_core.py`：QC 指标计算、MAD outlier、过滤等可导入函数。
- `onescience-coder/assets/bio_single_cell_tools/qc_plotting.py`：QC 分布、阈值和过滤前后图。
- `references/scverse_qc_guidelines.md`：QC 指标解释、阈值策略、物种/组织注意事项。

标准 QC 请求把 `qc_analysis.py` 的 coder 资产路径写入 `handoff_artifacts`；需要自定义阈值或整合到更大流程时同时交接 `qc_core.py` 和 `qc_plotting.py`。role 层不直接运行脚本。

## 推荐流程

1. 明确输入格式：10x matrix/h5、h5ad、Seurat RDS、loom。
2. 计算 QC：n_genes、total_counts、pct_mito、pct_ribo、ambient RNA、doublet score。
3. 过滤：按组织/物种选择阈值；优先保守过滤，保留稀有细胞可能性。
4. 归一化与 HVG：Scanpy/Seurat 标准路线或 SCTransform。
5. 批次整合：Harmony、scVI、scANVI、scArches 等；明确 batch key 和 label key。
6. 降维聚类：PCA、neighbors、UMAP、Leiden，多分辨率比较。
7. marker 和注释：rank genes、参考图谱映射、人工 marker 复核。
8. 输出：过滤后对象、QC 图、UMAP、marker 表、注释表、方法记录。

## QC 检查点

- 过滤前后细胞数和基因数。
- 线粒体比例阈值是否符合组织特性。
- doublet 率是否符合平台和上样量。
- 聚类是否由 batch、library size 或细胞周期主导。

## 交接物

```yaml
bio_task_family: single-cell-analysis
input_object:
organism_or_taxon:
raw_counts_available:
batch_key:
label_key:
qc_strategy:
integration_strategy:
annotation_strategy:
expected_outputs:
execution_entry:
```

## 禁止事项

- scVI/scANVI 需要 raw integer counts；不要用已 log-normalized 的 X 直接训练。
- 不要只凭 UMAP 位置命名细胞类型；必须结合 marker 或 reference。
- 不要用固定 mito 阈值处理所有组织。
