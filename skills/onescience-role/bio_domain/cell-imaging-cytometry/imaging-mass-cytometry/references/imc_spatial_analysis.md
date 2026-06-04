# IMC 空间表型分析参考

## 数据层

- ROI 级图像：保留 ROI、sample、condition、batch、antibody panel 和 acquisition metadata。
- Channel QC：检查空通道、过饱和、背景高、hot pixel、通道串扰和组织破损。
- Cell table：每行一个细胞，至少包含 cell id、ROI、centroid、area、marker intensity、cell type。

## 分割与表型

分割质量决定空间统计可靠性。每个 ROI 需要 overlay QC、cell count、area distribution 和异常对象比例。表型可用规则门控、聚类或监督分类，但最终必须由 marker 逻辑解释。

## 空间统计

- Neighborhood enrichment：比较不同 cell type 邻接是否高于随机。
- Nearest neighbor distance：检查特定细胞间距离分布。
- Spatial graph：以半径或 kNN 建图，报告参数。
- Region comparison：按 ROI/sample 聚合后进行统计，不要把同一 ROI 的所有 cell 当独立生物重复。
