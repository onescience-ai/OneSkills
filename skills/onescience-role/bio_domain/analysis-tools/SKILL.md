---
name: bio-analysis-tools
description: 生物信息分析工具箱范畴路由。用于 Biopython/pysam/Scanpy/scvi-tools/R/Bioconductor/RDKit/质谱工具/统计可视化等工具型请求，选择具体工具 skill，明确输入格式、API 边界和下游交接。
---

# 生信分析工具箱范畴路由

当用户主要在问“用什么工具、怎么解析、怎么写某个库的分析逻辑”时，使用本范畴。若任务是端到端分析链，先回到 `../workflows/SKILL.md`。

## 具体 skill 路由

- Python 生信基础库、序列/结构/NCBI、BAM/VCF 编程：读取 `./python-bio-toolkit/SKILL.md`
- R/Bioconductor、DESeq2、edgeR、Seurat、GenomicRanges：读取 `./r-bioconductor-toolkit/SKILL.md`
- Scanpy、AnnData、scvi-tools、cell type annotation：读取 `./single-cell-toolkit/SKILL.md`
- RDKit、SMILES/SDF、fingerprint、descriptor、similarity：读取 `./cheminformatics-toolkit/SKILL.md`
- PyOpenMS、matchms、mzML、feature detection、spectral matching：读取 `./mass-spectrometry-toolkit/SKILL.md`
- 统计建模、可视化、报告图：读取 `./statistics-visualization/SKILL.md`

## 交接规则

输出时至少整理：

- `tool_family`
- `input_format`
- `operation`
- `data_size`
- `expected_output`
- `version_or_api_risk`
- `execution_entry`
