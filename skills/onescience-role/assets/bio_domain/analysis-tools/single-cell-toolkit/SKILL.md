---
name: bio-single-cell-toolkit
description: 单细胞工具 skill。用于 Scanpy、AnnData、scvi-tools、scANVI、totalVI、PeakVI、MultiVI、DestVI、cell type annotation、cellxgene、MuData、scvelo 等工具选择和 API 交接。
---

# 单细胞工具箱

## 可复用资源

- `onescience-coder/assets/bio_single_cell_tools/validate_adata.py`：检查 AnnData 是否满足 batch、label、counts layer 等需求。
- `onescience-coder/assets/bio_single_cell_tools/prepare_data.py`：scvi-tools 前的数据准备、QC、HVG 和 layer 设置。
- `onescience-coder/assets/bio_single_cell_tools/train_model.py`：训练 scVI/scANVI/totalVI/PeakVI/MultiVI 等模型的入口。
- `onescience-coder/assets/bio_single_cell_tools/cluster_embed.py`：邻域图、UMAP、Leiden 聚类。
- `onescience-coder/assets/bio_single_cell_tools/differential_expression.py`：基于训练模型或对象的差异分析。
- `onescience-coder/assets/bio_single_cell_tools/transfer_labels.py`：scANVI/scArches 风格 label transfer。
- `onescience-coder/assets/bio_single_cell_tools/integrate_datasets.py`、`model_utils.py`：多数据集整合和可导入工具函数。
- `references/*.md`：环境、数据准备、scRNA integration、ATAC、CITE-seq、multiome、spatial、label transfer、troubleshooting 等细分说明。

用户明确提到 scVI/scANVI/totalVI/PeakVI/MultiVI/DestVI/veloVI 时，先读取对应 reference，再把 coder 资产路径写入 `handoff_artifacts`；role 层不直接运行脚本。

## 工具选择

- AnnData：h5ad 数据结构、layers/raw/obs/var/obsm。
- Scanpy：QC、normalization、PCA/UMAP、Leiden、marker。
- scvi-tools：scVI/scANVI/totalVI/PeakVI/MultiVI/DestVI/veloVI。
- MuData/muon：多模态容器、WNN、RNA+ATAC/protein。
- cell annotation：marker-based、reference mapping、celltypist/popV 风格。
- velocity：spliced/unspliced layer、veloVI/scvelo。

## 关键要求

- scvi-tools 模型需要 raw counts layer。
- integration 需要 batch key；label transfer 需要 label key。
- multiome 需要模态间 cell index 对齐。
- spatial deconvolution 需要空间对象和 scRNA reference。

## 交接物

```yaml
tool_family: single-cell
input_object:
modality:
raw_counts_layer:
batch_key:
label_key:
model_or_method:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 log-normalized data 当 raw counts。
- 不要只根据聚类编号给细胞类型命名。
- 不要把 ATAC peak matrix 当 RNA counts 处理。
