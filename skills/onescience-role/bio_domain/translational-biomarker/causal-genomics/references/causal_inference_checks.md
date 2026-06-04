# 因果基因组学检查

## MR 三个核心假设

1. 工具变量与 exposure 相关。
2. 工具变量不与混杂因素相关。
3. 工具变量只通过 exposure 影响 outcome。

## 常见敏感性分析

- F statistic 检查弱工具变量。
- MR-Egger intercept 和 MR-PRESSO 检查水平多效性。
- Steiger filtering 检查方向性。
- Leave-one-out 检查单个 SNP 驱动。

## Colocalization

MR 指向因果关系不代表 exposure 和 outcome 在同一 locus 共享 causal variant。GWAS-QTL 共定位需要 LD reference、variant coverage 和 credible set。
