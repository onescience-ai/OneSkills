---
name: bio-clinical-trial-protocol
description: 生命科学临床研究方案 skill。用于药物、器械、诊断、数字生物标志物或生信伴随诊断相关临床研究方案，包含研究目标、设计、终点、入排标准、样本量、统计分析和监管证据整理。
---

# 临床研究方案

## 使用边界

用于研究方案和文档草案，不给医疗建议或监管最终判断。若请求涉及真实患者决策，保持技术和文档层面。

## 推荐流程

1. 明确 intervention/device/diagnostic、适应症、研究阶段和目标人群。
2. 定义 endpoint：primary、secondary、exploratory、生物标志物终点。
3. 设计结构：prospective/retrospective、randomized、blinded、single-arm、observational。
4. 入排标准、访视、样本采集、实验检测、数据管理。
5. 统计计划：sample size、analysis population、missing data、interim analysis。
6. 输出 protocol outline、risk list、需要补充的法规/伦理材料。

## 交接物

```yaml
task_context: clinical-protocol
intervention_or_diagnostic:
indication:
study_design:
population:
endpoints:
assessments:
statistics_plan:
deliverable:
execution_entry:
```

## 禁止事项

- 不要给出临床诊断或治疗建议。
- 不要把检索到的相似研究当作监管批准依据。
- 不要跳过伦理、隐私和数据治理风险。
