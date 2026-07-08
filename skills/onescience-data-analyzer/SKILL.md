---
name: onescience-data-analyzer
description: OneScience 数据分析执行技能（type=executor）。负责数据分析、可视化与报告输出，不涉及任务规划。接收规划好的任务，调用工作流执行统计分析、可视化生成和报告输出，根据领域自动匹配可视化规范（气象、生信、流体、材料等）。
type: executor
---

# onescience-data-analyzer

数据分析执行技能，负责数据分析、可视化与报告输出。

## 职责

本技能为执行器（executor），专注于执行数据分析任务，不涉及任务规划。规划由其他技能完成后传递给本技能执行。

## 核心能力

1. **数据分析**：统计分析、趋势分析、相关性分析
2. **数据可视化**：图表生成、多维展示、交互式可视化
3. **报告生成**：结构化报告、图文结合、结果导出

## 工作流调用

根据任务类型调用对应工作流：

- **统计分析**：`{{workflow:references/statistical_analysis.md}}`
- **可视化生成**：`{{workflow:references/visualization.md}}`
- **报告输出**：`{{workflow:references/report_generation.md}}`

## 领域知识

工作流执行时会根据数据领域自动匹配 `assets/` 目录中的领域知识：

- 气象数据可视化：`assets/meteorology_viz.md`
- 生物信息学可视化：`assets/bioinformatics_viz.md`
- 流体力学可视化：`assets/fluid_dynamics_viz.md`
- 材料科学可视化：`assets/materials_science_viz.md`

## 使用方式

接收来自规划技能的任务描述，按照以下流程执行：

1. 识别任务类型（分析/可视化/报告）
2. 加载对应工作流
3. 匹配领域知识（如果需要）
4. 执行分析与生成
5. 输出结果

## 输入格式

```json
{
  "task_type": "visualization|analysis|report",
  "data_path": "数据文件路径",
  "domain": "meteorology|bioinformatics|fluid_dynamics|materials_science|general",
  "requirements": {
    "viz_type": "line|scatter|heatmap|contour|3d|...",
    "analysis_methods": ["correlation", "trend", "distribution"],
    "output_format": "png|svg|pdf|html"
  }
}
```

## 输出格式

```json
{
  "status": "success|failed",
  "outputs": {
    "figures": ["path/to/fig1.png", "path/to/fig2.svg"],
    "report": "path/to/report.html",
    "data": "path/to/processed_data.csv"
  },
  "summary": "分析与可视化完成概要"
}
```
