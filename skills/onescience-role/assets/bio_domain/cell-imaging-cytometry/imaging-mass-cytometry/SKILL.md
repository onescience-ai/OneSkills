---
name: bio-imaging-mass-cytometry
description: Imaging mass cytometry 与多重组织空间表型 skill。用于 IMC、MIBI、CODEX 或多重 IF 的通道 QC、热像素处理、细胞分割、marker 表型、邻域图、空间相互作用和 ROI 级报告。
---

# Imaging Mass Cytometry 与空间表型

## 使用边界

用于多重组织成像中的细胞级表型和空间关系。若任务只是通用显微图像分割，读取 `../bioimage-segmentation/SKILL.md`；若是 WSI tile 级病理分析，读取 `../digital-pathology-wsi/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_cell_imaging_templates/imc_analysis_plan.yaml`：ROI、marker panel、preprocessing、segmentation、phenotyping 和 spatial tests 模板。
- `references/imc_spatial_analysis.md`：IMC/MIBI 预处理、QC、分割、表型和空间统计方法。

## 推荐流程

1. 明确图像来源：MCD/TIFF/OME-TIFF、ROI、像素大小、channel-marker 映射。
2. 预处理：hot pixel、spillover/crosstalk 检查、background、normalization、tissue mask。
3. 分割：nuclear/cytoplasm membrane marker、Cellpose/Mesmer/classical watershed，输出 cell mask。
4. 表型：按 marker panel 聚类或规则赋型，记录 marker thresholds 和 cell type confidence。
5. 空间分析：邻域图、cell-cell adjacency、Ripley/nearest neighbor、neighborhood enrichment、区域比较。
6. 输出：cell table、mask、ROI QC、phenotype table、spatial interaction table 和可审阅图。

## 交接物

```yaml
bio_task_family: cell-imaging-cytometry
cell_task: imaging-mass-cytometry
image_inputs:
marker_panel:
roi_metadata:
preprocessing:
segmentation:
phenotyping:
spatial_statistics:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在没有 cell mask QC 的情况下解释空间邻域。
- 不要把 marker spillover 或背景高通道当作真实表达。
- 不要忽略 ROI、batch、抗体 panel 版本对空间统计的影响。
