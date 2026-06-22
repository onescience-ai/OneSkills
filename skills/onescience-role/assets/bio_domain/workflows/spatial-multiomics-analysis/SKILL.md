---
name: bio-spatial-multiomics-analysis
description: 空间组学和多模态单细胞 workflow skill。用于 spatial transcriptomics、Visium、Xenium、Slide-seq、CITE-seq、RNA+ATAC multiome、MuData、WNN、MOFA、MultiVI、totalVI、DestVI 等任务。
---

# 空间组学与多模态分析流程

## 使用边界

用于具有空间坐标、图像、蛋白标签、ATAC 或多组学同细胞测量的数据。单一 scRNA-seq 进入 `single-cell-rna-analysis`。

## 推荐流程

1. 明确模态：RNA、ATAC、ADT/protein、spatial image、morphology、metabolite。
2. 明确数据容器：AnnData、MuData、Seurat、SpatialExperiment 或平台输出目录。
3. 分模态 QC：
   - RNA：counts、genes、mito。
   - ATAC：fragments、TSS enrichment、FRiP、peak count。
   - protein：isotype/background、CLR normalization。
   - spatial：spot/cell segmentation、image alignment、坐标系。
4. 分模态降维后再整合：WNN、MOFA、MultiVI、totalVI、DestVI 或其他 deconvolution。
5. 空间分析：邻域、domain、cell-cell communication、空间差异表达、空间可视化。
6. 输出：多模态对象、UMAP/spatial plots、domain/cell type 表、deconvolution matrix、QC 报告。

## 交接物

```yaml
bio_task_family: spatial-multiomics-analysis
modalities:
input_object:
coordinate_or_image_available:
shared_cell_or_spot_index:
qc_strategy_by_modality:
integration_strategy:
spatial_analysis_goal:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要假设不同模态的 cell barcode 已完全一致，必须检查交集和顺序。
- 不要把空间 spot 当作单细胞，除非已有 segmentation 或 deconvolution 说明。
- 不要用 RNA 的归一化方法处理 ATAC peak matrix。
