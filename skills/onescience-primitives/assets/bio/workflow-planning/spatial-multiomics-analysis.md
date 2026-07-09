# 空间组学与多模态分析工作流

- workflow_id: `spatial-multiomics-analysis`

## 适用范围

用于 spatial transcriptomics、Visium、Xenium、Slide-seq、MERFISH、CITE-seq、RNA+ATAC multiome、MuData、WNN、MOFA、MultiVI、totalVI、DestVI、spatial domain 和 deconvolution 规划。

## 输入

- 必需：空间或多模态矩阵；sample metadata；平台信息；modality 列表。
- 空间分支：坐标、组织图像或平台输出目录。
- 多模态分支：RNA、ATAC、protein、image 或其他 modality 矩阵。
- 可选：matched scRNA reference、histology annotation、segmentation mask、marker gene set。

## 输出

- 空间/多模态对象。
- modality-specific QC 表。
- UMAP、spatial plot、domain/cell type 表。
- deconvolution matrix、integrated latent space。
- spatially variable feature、marker/spatial DE、cell-cell communication 或 multimodal result。

## 流程节点

1. 判定平台和模态：Visium、Xenium、Slide-seq、MERFISH、CITE-seq、multiome、MuData 等。
2. 校验 barcode、坐标、图像路径、feature ID、sample metadata 和 modality alignment。
3. 分模态执行 QC：RNA、ATAC、protein、image 分开检查。
4. 根据参考和模态选择 integration、deconvolution、WNN、MOFA、MultiVI、totalVI 或 DestVI 分支。
5. 执行 spatial domain、spatial variable feature、neighborhood 或 cell communication 分析。
6. 输出对象、图、矩阵和报告。

## 边界与分流

- image-only segmentation 或 cytometry measurement 转到 `bio_cell_imaging_cytometry_app`。
- scRNA-only 转到 `single-cell-rna-analysis`。
- bulk 多组学整合转到 `multiomics-systems-biology`。
- 不把空间 spot 默认当作单细胞，除非已有 segmentation/deconvolution 依据。

## 模型与工具选择边界

- RNA+protein CITE-seq 且有 raw counts：可选 totalVI。
- RNA+ATAC multiome：可选 MultiVI。
- 有可靠 scRNA reference：可选 DestVI/deconvolution。
- Seurat 风格 multimodal：可选 WNN。
- 无参考时优先 unsupervised spatial domain 和 marker 分析。

## 质量检查

- 坐标和组织图像对齐。
- 各 modality barcode 交集和顺序正确。
- RNA、ATAC、protein、image QC 分开记录。
- reference 与目标组织/物种/平台兼容。
- batch、section、slide 和平台效应有检查。

## 回退策略

- 无 reference：跳过 deconvolution，做 unsupervised spatial/domain 分析。
- modality 不对齐：先输出对齐问题和可用交集。
- 图像缺失：限制空间可视化和组织结构解释。

## 资源召回建议

- 单细胞/AnnData/MuData 分析：`bio_single_cell_analysis_app`。
- 成像/空间图像模板和测量：`bio_cell_imaging_cytometry_app`。
- 多模态工具交接：`bio_analysis_toolkit_app`。
