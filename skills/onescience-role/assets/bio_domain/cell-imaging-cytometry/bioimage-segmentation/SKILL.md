---
name: bio-bioimage-segmentation
description: 生物显微图像分割与定量 skill。用于荧光、明场、相差、3D z-stack 或 time-lapse 图像的 Cellpose、scikit-image、OpenCV、napari 审阅、mask 生成、regionprops 和细胞追踪交接。
---

# 生物图像分割与定量

## 使用边界

用于 microscopy image 到 mask、object table 和 QC overlay 的任务。若是病理 WSI tile pipeline，读取 `../digital-pathology-wsi/SKILL.md`；若是 FCS event table，读取 `../flow-cytometry-analysis/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_cell_imaging_templates/segmentation_plan.yaml`：图像维度、通道、模型、阈值、QC 和输出路径模板。
- `references/segmentation_methods.md`：Cellpose、watershed、OpenCV、3D stack、追踪和 QC 选择规则。
- `onescience-coder/assets/bio_cell_imaging_tools/label_mask_measurements.py`：对整数 label mask CSV/TSV 和强度表做基础面积/强度汇总的轻量脚本。

## 推荐流程

1. 明确图像：文件格式、维度、像素尺寸、通道含义、z/time、bit depth。
2. 选择方法：rule-based threshold/watershed、Cellpose/nnU-Net、OpenCV contour、Fiji plugin。
3. 生成 mask：保存整数 label mask，不要只保存彩色 overlay。
4. QC：原图+边界 overlay、object size distribution、空 mask、merged/split errors、边缘对象。
5. 量化：area、centroid、shape、mean/max intensity、多通道 marker、track id。
6. 输出：mask、measurement table、QC figures、参数记录和人工审阅点。

## 交接物

```yaml
bio_task_family: cell-imaging-cytometry
cell_task: bioimage-segmentation
image_inputs:
channel_map:
pixel_size:
segmentation_method:
parameters:
qc_review:
measurements:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要只输出 PNG overlay 而不输出可计算的 label mask。
- 不要在没有像素尺度时解释真实面积或距离。
- 不要忽略 3D stack、time-lapse 和多通道图像的轴顺序。
