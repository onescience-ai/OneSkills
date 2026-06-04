---
name: bio-epigenomics-regulation
description: 表观组学与调控分析 workflow skill。用于 ATAC-seq、ChIP-seq、CUT&Tag、methylation、Hi-C、CLIP-seq、motif、peak calling、differential binding、TAD、loop、GRN/SCENIC 等任务。
---

# 表观组学与调控流程

## 使用边界

用于调控元件、染色质可及性、组蛋白/TF binding、甲基化、3D genome 和调控网络任务。

## 推荐流程

1. 明确 assay：ATAC、ChIP、CUT&Tag、methylation、Hi-C、CLIP、Perturb-seq/GRN。
2. 明确参考版本、blacklist、control/input、replicate、paired-end。
3. 预处理：QC、trimming、alignment、dedup、filter mitochondrial/low MAPQ。
4. 核心分析：
   - peak：MACS3/SEACR、FRiP、peak annotation、motif。
   - differential binding：consensus peak、count matrix、design formula。
   - methylation：conversion rate、CpG coverage、DMR。
   - Hi-C：pairs/matrix、normalization、TAD/loop。
   - GRN：TF list、motif evidence、coexpression/perturbation support。
5. 输出：peak/DMR/loop/regulon 表、bigWig、plots、QC 报告。

## 交接物

```yaml
bio_task_family: epigenomics-regulation
assay:
reference_build:
controls:
replicates:
core_tools:
qc_checkpoints:
analysis_outputs:
downstream_links:
execution_entry:
```

## 禁止事项

- 不要在没有 control/input 或 replicate 信息时夸大 binding 结论。
- 不要混用 peak 坐标和不同 genome build 的注释。
- Hi-C 的 bin size、normalization 和 resolution 必须写清。
