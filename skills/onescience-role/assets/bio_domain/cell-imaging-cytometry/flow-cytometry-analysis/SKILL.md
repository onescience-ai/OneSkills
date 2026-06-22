---
name: bio-flow-cytometry-analysis
description: 流式和质谱流式分析 skill。用于 FCS 文件读取、通道元数据、补偿矩阵、arcsinh/logicle 转换、QC、doublet/dead cell 过滤、手动或自动门控、聚类表型和差异丰度分析。
---

# 流式与质谱流式分析

## 使用边界

用于 FCS/CyTOF 数据预处理、门控、表型聚类和条件比较。若输入是显微成像或 IMC 图像，读取 `../imaging-mass-cytometry/SKILL.md` 或 `../bioimage-segmentation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_cell_imaging_templates/flow_panel_metadata.csv`：样本、marker、channel、fluorophore、spillover、cofactor 和 gating 层级模板。
- `references/flow_analysis_qc.md`：FCS 读取、补偿、转换、QC、门控和统计比较边界。
- `onescience-coder/assets/bio_cell_imaging_tools/cytometry_table_qc.py`：对已导出的 event table 或 marker intensity CSV 做基础 QC 汇总。

## 推荐流程

1. 明确平台：conventional flow、spectral flow、CyTOF、FACS sorting 或 bead assay。
2. 读取 FCS 元数据：sample id、channel、marker、spillover、acquisition time、event count。
3. 做 QC：flow rate、margin events、signal drift、bead normalization、dead cell、doublet。
4. 补偿与转换：fluorescence compensation、arcsinh/logicle，记录 cofactor。
5. 分析策略：层级门控、FlowSOM/Phenograph、marker-based annotation、差异丰度和 marker state。
6. 输出：gating tree、population frequency、marker intensity、QC plots、统计比较表。

## 交接物

```yaml
bio_task_family: cell-imaging-cytometry
cell_task: flow-cytometry-analysis
input_fcs_or_table:
panel_metadata:
compensation:
transformation:
qc_filters:
gating_or_clustering_strategy:
statistical_comparison:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在未说明补偿和转换参数时比较 marker intensity。
- 不要把 FMO/isotype/unstained control 混作同一种门控依据。
- 不要把自动聚类 label 当成已验证细胞类型；需 marker 解释和人工复核。
