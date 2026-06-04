# CRISPR 设计规则

## 任务到靶区

- Knockout：优先早期 constitutive coding exon，避开 alternative first exon 和低表达 isoform 专属区域。
- CRISPRa：通常在 TSS 上游约 50-300 bp 区间筛 guide。
- CRISPRi：通常覆盖 TSS 附近和 5' UTR，需结合启动子注释。
- Base editing：确认目标碱基位于编辑窗口内，并列出同窗口旁观者碱基。
- Prime editing：需要 spacer、PBS、RT template、nick guide 选择和预期 edit 序列。
- HDR knock-in：需要 donor 类型、左右同源臂、silent PAM-blocking mutation 和筛选策略。

## 常用过滤

- SpCas9 guide GC 40-70 percent 通常更稳。
- 避免 `TTTT`，它可能终止 U6/Pol III 转录。
- 避开 common SNP、segmental duplication、repeat、低复杂度区域。
- 若目标是人类细胞系，记录参考 build 和细胞系变异背景。

## Off-target 交接

本 skill 可做候选初筛，但 off-target 合格结论必须来自指定参考基因组的全基因组扫描或可信数据库。交接物要包括 mismatch 阈值、PAM 模型、是否考虑 DNA/RNA bulge、是否过滤编码区或调控区 off-target。
