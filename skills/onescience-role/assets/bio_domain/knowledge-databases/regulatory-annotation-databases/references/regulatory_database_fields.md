# 调控注释字段

## 坐标

始终记录 genome build、0/1-based、closed/open interval。BED 通常是 0-based half-open。

## 证据类型

- Peak evidence：assay、cell type、replicate、signal、IDR/q-value。
- Motif evidence：matrix id、relative score、strand、background model。
- Variant regulatory evidence：overlap peak、motif disruption、QTL、chromatin state。

## 解释边界

Motif overlap 不代表真实 binding；开放染色质不代表目标基因调控；enhancer-gene link 需要距离、3D contact、QTL 或扰动证据支持。
