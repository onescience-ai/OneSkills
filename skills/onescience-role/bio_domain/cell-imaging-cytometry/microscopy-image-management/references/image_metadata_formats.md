# 图像元数据与格式

## OME-TIFF

适合显微图像交换，需保留 channel name、axis order、physical pixel size、z/time 和 acquisition metadata。

## DICOM

适合临床影像。导出前必须检查 PHI 标签、series/study 层级、spacing、orientation、windowing 和 modality。

## ROI 与审阅

ROI 可来自 OMERO、napari shapes、ImageJ ROI、GeoJSON 或 mask。交接时应写明坐标系、scale、是否相对原图、是否跨 pyramid level。

## 批量管理

大规模图像数据应使用 manifest 管理，不要把样本分组、通道含义和像素大小只放在文件名里。
