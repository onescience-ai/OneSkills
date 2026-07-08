# launch

该卡以模板启用为主：

```sh
cp script/bio_report_templates/report_outline.md ./report_outline.md
```

# input_schema

需要提供 `assay_or_study`、`input_manifest`、`software_versions`、`qc_sections`、`figures_and_tables`、`reproducibility_assets`、`deliverable`、失败样本和限制说明。研究方案或实验设计任务还需提供 `study_design`、`population`、`endpoints`、`replicate_plan`、`power_assumptions`、`batch_randomization` 和 `statistics_plan`。

# runtime_interfaces

- 模板入口：`report_outline.md`
- 适用任务标签：`clinical-trial-protocol`、`experimental-design-power`、`qc-reporting-reproducibility`
- execution_kind：template_only

# main_functions

- emit QC report outline
- map artifacts to report sections
- emit protocol outline and study design summary
- emit power assumptions and statistical risk checklist
- define reproducibility checklist

# execution_resources

无计算资源要求。生成正式 PDF/DOCX/幻灯片时交给相应文档或报告执行能力。

# operation_limits

该卡只提供报告结构和方案/设计草案，不自动生成经过验证的科学结论，不运行 notebook，不渲染报告，也不替代伦理、监管、统计或临床审核。
