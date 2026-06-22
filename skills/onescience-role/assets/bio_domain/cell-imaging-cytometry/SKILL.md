---
name: bio-cell-imaging-cytometry
description: 细胞图像、流式与空间表型范畴路由。用于 FCS 流式或质谱流式、门控、补偿、CyTOF/IMC、显微图像分割、全切片病理图像、OMERO 或 Bio-Formats 图像管理、细胞表型和空间邻域分析。
---

# 细胞图像、流式与空间表型范畴路由

当用户处理细胞层面的表型测量、显微图像、流式数据或空间组织图像时，使用本范畴。若输入是单细胞转录组矩阵，优先回到 `../workflows/single-cell-rna-analysis/SKILL.md` 或 `../analysis-tools/single-cell-toolkit/SKILL.md`。

## 具体 skill 路由

- FCS 文件、补偿矩阵、转换、手动/自动门控、doublet/dead cell 过滤、FlowSOM/Phenograph：读取 `./flow-cytometry-analysis/SKILL.md`
- Imaging mass cytometry、MIBI、CyTOF 成像、通道 QC、细胞分割、表型、空间邻域/相互作用：读取 `./imaging-mass-cytometry/SKILL.md`
- 荧光/明场显微图像、Cellpose、scikit-image、OpenCV、3D stack、mask 和 regionprops：读取 `./bioimage-segmentation/SKILL.md`
- WSI、H&E/IHC、tile extraction、stain normalization、病理图像 QC 和 tile-level ML：读取 `./digital-pathology-wsi/SKILL.md`
- OMERO、DICOM、Bio-Formats、napari、ImageJ/Fiji、图像元数据、ROI 和批量导出：读取 `./microscopy-image-management/SKILL.md`

## 交接规则

输出时至少整理：

- `assay_or_image_type`
- `input_format`
- `channel_or_marker_panel`
- `preprocessing`
- `segmentation_or_gating_strategy`
- `qc_checkpoints`
- `quantitative_outputs`
- `review_artifacts`
- `execution_entry`

## 禁止事项

- 不要把图像文件当普通矩阵处理；必须说明像素尺度、通道、tile 或 z/time 维度。
- 不要跳过 compensation、transformation、stain normalization、mask QC 等会影响定量结论的步骤。
- 不要在没有人工审阅或 QC 图的情况下把自动门控/自动分割结论当作最终生物结论。
