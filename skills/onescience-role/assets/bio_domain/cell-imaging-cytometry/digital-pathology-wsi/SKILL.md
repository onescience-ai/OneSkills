---
name: bio-digital-pathology-wsi
description: 全切片病理图像 WSI 处理 skill。用于 H&E/IHC/mIF whole-slide image 的组织检测、tile extraction、stain normalization、slide QC、tile-level 特征、病理 ML 数据集准备和报告交接。
---

# 全切片病理图像处理

## 使用边界

用于 SVS/NDPI/MRXS/OME-TIFF 等 WSI 的 tile 提取、组织 mask、颜色标准化、QC 和病理图像机器学习交接。若是单张显微图像或细胞核分割，读取 `../bioimage-segmentation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_cell_imaging_templates/wsi_tile_plan.yaml`：slide manifest、tile size、magnification、tissue filter、stain normalization 和 QC 模板。
- `references/wsi_processing_qc.md`：WSI 维度、level、MPP、tile 策略、颜色和数据泄漏风险。

## 推荐流程

1. 建 slide manifest：case、slide id、stain、scanner、MPP、label、split。
2. Slide QC：空白、模糊、折叠、pen mark、组织比例、扫描 level。
3. Tissue mask：低倍图阈值或模型，确定 tile inclusion rule。
4. Tile extraction：tile size、overlap、magnification、背景过滤、坐标记录。
5. 预处理：stain normalization、颜色增强、artifact filter。
6. 输出：tile manifest、QC report、thumbnail overlay、case-level split 和 ML 交接。

## 交接物

```yaml
bio_task_family: cell-imaging-cytometry
cell_task: digital-pathology-wsi
slide_manifest:
stain_and_scanner:
tile_strategy:
tissue_detection:
stain_normalization:
qc_filters:
case_split:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要按 tile 随机划分训练/测试；必须按 patient/case/slide 防泄漏。
- 不要在未固定 magnification/MPP 时比较 morphology feature。
- 不要丢失 tile 到 slide/case 的坐标和层级映射。
