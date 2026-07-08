# description

把分析结果和 QC 证据组织为可复现报告交付结构。

# when_to_use

用于 QC 报告、可复现分析报告、实验室质量交付、临床研究方案草案、实验设计/功效说明、Jupyter/Quarto/RMarkdown 报告规划。

# inputs

- task_context、study_or_lab_object。
- QC artifacts、figures、methods、versions。
- intervention_or_diagnostic、study_design、population、endpoints、replicate_plan、power_assumptions、batch_randomization、statistics_plan。
- standards_or_constraints、deliverable、risk_or_missing_fields。

# outputs

- 报告大纲。
- 方案草案、设计矩阵或功效假设清单。
- 图表、表格、日志和命令映射。
- 风险和复现 checklist。

# procedure

1. 确认报告或方案目标和受众。
2. 收集已有执行证据。
3. 选择 report outline 模板。
4. coder 或 data-analyzer 填充章节，研究设计任务需保留假设、限制和待审核项。
5. 需要正式文档时交给文档工具。

# constraints

- 不得编造未执行结果。
- 不得省略失败和限制。
- 不得把研究报告写成临床建议。
- 不得把方案草案、样本量估计或统计计划写成伦理/监管/临床最终结论。
- 不得混淆 technical replicate 和 biological replicate。

# next_phase_recommendation

可交给 data-analyzer 生成图表和结果描述，再交给文档工具排版。

# fallback

若证据不足，只输出报告骨架、方案骨架或缺失证据清单。
