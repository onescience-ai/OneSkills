---
name: bio-r-bioconductor-toolkit
description: R 与 Bioconductor 生信工具 skill。用于 DESeq2、edgeR、limma、tximport、Seurat、SingleCellExperiment、GenomicRanges、clusterProfiler、ComplexHeatmap、RMarkdown/Quarto 等 R 生信分析设计。
---

# R / Bioconductor 工具

## 使用边界

用于 R 生态的统计、生信对象和可视化。若用户明确要 Python 实现，转到对应 Python tool skill。

## 工具选择

- bulk RNA-seq：DESeq2、edgeR、limma-voom、tximport。
- 单细胞：Seurat、SingleCellExperiment、scDblFinder、SingleR。
- 区间：GenomicRanges、rtracklayer、AnnotationHub。
- 富集：clusterProfiler、fgsea、ReactomePA。
- 可视化：ggplot2、ComplexHeatmap、pheatmap、EnhancedVolcano。
- 报告：RMarkdown、Quarto。

## 交接物

```yaml
tool_family: r-bioconductor
packages:
input_object:
design_formula:
contrast_or_grouping:
annotation_source:
expected_outputs:
execution_entry:
```

## 禁止事项

- DESeq2 输入必须是 raw integer counts。
- Seurat 对象的 assay/layer/slot 要说明清楚。
- 不要在未确认 Bioconductor 版本时依赖新版参数。
