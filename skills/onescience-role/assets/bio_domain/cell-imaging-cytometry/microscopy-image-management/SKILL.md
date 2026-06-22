---
name: bio-microscopy-image-management
description: 显微和医学图像管理 skill。用于 OMERO、Bio-Formats、ImageJ/Fiji、napari、DICOM、OME-TIFF、ROI、图像元数据、批量导入导出、去标识化和审阅交接。
---

# 显微图像管理与审阅

## 使用边界

用于图像数据组织、元数据、ROI、交互审阅、服务器/本地互转和格式转换。若用户目标是算法分割，读取 `../bioimage-segmentation/SKILL.md`；若是 WSI 分析，读取 `../digital-pathology-wsi/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_cell_imaging_templates/image_dataset_manifest.csv`：图像文件、样本、通道、像素尺寸、ROI、去标识化状态模板。
- `references/image_metadata_formats.md`：OME-TIFF、DICOM、ROI、channel metadata 和审阅策略。

## 推荐流程

1. 建立 manifest：image id、sample、condition、file path、format、channels、pixel size、z/time。
2. 确认元数据：axis order、bit depth、channel names、exposure、objective、scanner、ROI。
3. 选择工作方式：本地 OME-TIFF、OMERO server、napari 审阅、Fiji macro、DICOM series。
4. 安全与合规：DICOM/临床图像去标识化，避免导出 PHI。
5. 输出：标准化文件、manifest、ROI/annotation、审阅截图和下游分析入口。

## 交接物

```yaml
bio_task_family: cell-imaging-cytometry
cell_task: microscopy-image-management
image_dataset:
metadata_fields:
storage_or_server:
format_conversion:
roi_annotations:
deidentification:
downstream_skill:
execution_entry:
```

## 禁止事项

- 不要丢失 axis order、pixel size 和 channel 名称。
- 不要把 DICOM 临床标签原样带入公开输出。
- 不要把交互式 napari/Fiji 审阅步骤伪装成全自动分析。
