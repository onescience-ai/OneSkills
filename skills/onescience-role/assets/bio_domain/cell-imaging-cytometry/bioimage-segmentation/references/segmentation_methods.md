# 生物图像分割方法选择

## 方法选择

- Threshold + watershed：适合背景稳定、对象分离较好、形态简单的图像。
- Cellpose：适合细胞/细胞核形态多样、强度变化明显、需要快速泛化的 2D/3D 图像。
- nnU-Net：适合有标注训练数据且需要医学/显微 3D 高精度分割。
- OpenCV：适合高速视频、轮廓、blob、形态学和工程化实时处理。
- Fiji/ImageJ plugin：适合已有宏、TrackMate 或 Bio-Formats 依赖流程。

## QC 必查

- 空 mask 或全图一个 mask。
- 过分割、欠分割、边缘对象、碎片对象。
- object size 和 intensity 分布是否符合生物预期。
- mask 与原图 overlay 是否覆盖真实对象边界。
