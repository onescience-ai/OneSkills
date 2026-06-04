# 病原基因组监测流程参考

## 元数据

至少保留 sample id、采样日期、地点、宿主、样本来源、测序批次、coverage、低质量比例和 lineage。公共卫生报告需去标识化。

## 分析层级

- 样本 QC：coverage、Ns、contamination、mixed infection。
- Lineage/clade：使用固定版本 scheme。
- Cluster：SNP distance 或 tree-based cluster 需说明阈值。
- Time-resolved tree：需要足够时间信号和采样时间质量。

## 解释边界

系统发育接近不等于直接传播。传播推断必须结合流行病学接触、采样时间和地点。
