---
name: bio-qc-reporting-reproducibility
description: 生信 QC 报告和可复现交付 skill。用于 MultiQC、Jupyter、Quarto、RMarkdown、HTML/PDF 报告、figure export、run manifest、方法记录、参数记录、结果包和可复现分析说明。
---

# QC 报告与可复现交付

## 可复用资源

- `onescience-coder/assets/bio_report_templates/report_outline.md`：通用分析报告骨架，包含 Summary、Inputs、Methods、QC、Results、Limitations、Reproducibility。

当用户要报告或交付包时，优先用该模板组织内容，再按具体 assay 增减章节。

## 推荐流程

1. 汇总输入、软件版本、参数、参考版本、样本表和运行环境。
2. 为每个阶段定义 QC 图和阈值说明。
3. 输出结果表、图、日志和可复现命令。
4. 生成 report：HTML/PDF/notebook/markdown，包含方法、结果、限制和 next step。
5. 组织交付包：manifest、checksums、README、figures、tables、objects。

## 交接物

```yaml
task_context: qc-reporting
workflow_or_assay:
input_manifest:
software_versions:
qc_sections:
figures_and_tables:
reproducibility_assets:
deliverable:
execution_entry:
```

## 禁止事项

- 不要只交结果表而无参数和版本。
- 不要隐藏失败样本或过滤样本。
- 不要把探索性图表包装成确认性统计结论。
