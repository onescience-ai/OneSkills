# 报告生成工作流

## 工作流目标

整合分析结果与可视化图表，生成结构化科学报告。

## 执行步骤

### 1. 内容收集
- 收集统计分析结果
- 收集可视化图表
- 收集数据处理日志

### 2. 报告结构构建
生成标准科学报告结构：
- 摘要
- 数据概述
- 分析方法
- 结果展示（图表嵌入）
- 结论与发现

### 3. 格式化输出
根据输出格式要求：
- HTML：交互式报告，图表可缩放
- PDF：打印友好，固定布局
- Markdown：纯文本，便于版本控制

### 4. 元数据记录
- 分析时间戳
- 数据来源
- 使用的方法与参数
- 软件版本信息

## 输出内容

```json
{
  "report_path": "output/analysis_report.html",
  "format": "html",
  "sections": [
    "summary",
    "data_overview",
    "methods",
    "results",
    "conclusions"
  ],
  "assets": {
    "figures": ["fig1.png", "fig2.png"],
    "tables": ["table1.csv"]
  }
}
```
