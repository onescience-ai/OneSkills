# 引物与探针设计约束

## 基础约束

- 标准 PCR 引物通常 18-25 nt，Tm 57-63 C，左右引物 Tm 差异不超过 2 C。
- qPCR amplicon 通常 70-200 bp，优先跨 exon junction 或跨内含子以区分 gDNA。
- GC 建议 40-60 percent，避免 3' 端连续 G/C 过强或连续相同碱基超过 4 个。
- 避开 common SNP、低复杂度、重复序列和同源基因保守区。

## 探针约束

- 水解探针 Tm 通常比 primer 高 5-10 C。
- 探针不应与任一 primer 明显重叠，避免 5' 端 G，避免长 G-run。
- 分子信标需要额外检查 stem 互补、loop 靶区和背景荧光风险。

## 特异性检查

优先使用目标物种参考基因组或转录组做 BLAST/in silico PCR。若只有短模板序列，交接物必须标注“未完成全基因组特异性验证”。

## 常见失败点

- Amplicon 覆盖了未预期 isoform 或 pseudogene。
- primer 位于高 GC 或二级结构强区域，导致扩增效率差。
- qPCR primer 没有跨 exon junction，gDNA contamination 造成假阳性。
- probe 覆盖常见 SNP 或 indel，导致不同样本信号偏差。
