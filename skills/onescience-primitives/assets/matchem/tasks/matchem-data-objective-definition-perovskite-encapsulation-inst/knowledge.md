# 实例任务：数据与目标定义 @ 钙钛矿封装层降解抑制机器学习筛选

- domain: matchem
- 骨架: matchem-data-objective-definition-task
- 场景: matchem-perovskite-encapsulation-layer-degradation-suppression-machine-scenario (钙钛矿封装层降解抑制机器学习筛选)
- step_id: s01
- depend: []

## 场景研究主体
- 钙钛矿封装层降解抑制机器学习筛选
- 关联论文: How machine learning can help select capping layers to suppress perovskite degradation | doi:

## 本实例步骤描述
清洗数据并固定预测目标、单位和约束。

## 本实例执行 prompt
读取 {DATASET}，检查重复、缺失、泄漏、单位和数据许可；定义 {TARGET}，缺失关键标签时标记 BLOCKED。

## 本实例输入槽
- {DATASET} | required=True | type=doc | var_name=训练与验证数据 | hint=包含样本来源、目标值、单位和许可信息。 | default=CSV/JSON/数据库导出
- {TARGET} | required=True | type=str | var_name=优化目标 | hint=明确目标性质、单位、方向和约束。 | default=目标材料性质

## 本实例产出
- 清洗数据表
- 目标定义
- 数据审计报告

## 本实例质量门禁
- 训练/验证/测试划分可追溯
- 无未说明的数据泄漏

## 可调资源（edge:resource，仅真实存在）
- datasets/perovskite-stability-benchmark-dataset
- datasets/xjtu-sy-rolling-bearing-accelerated-life-test-protocol-and-dataset
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/dataset-contract-auditor

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
