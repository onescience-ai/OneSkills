# 实例任务：参考数据审计与覆盖定义 @ MOF量子精度机器学习势温度主动学习

- domain: matchem
- 骨架: matchem-reference-data-audit-coverage-definition-task
- 场景: matchem-mof-quantum-ml-potential-temperature-active-learning-scenario (MOF量子精度机器学习势温度主动学习)
- step_id: s01
- depend: []

## 场景研究主体
- MOF量子精度机器学习势温度主动学习
- 关联论文: Quantum-accurate machine learning potentials for metal-organic frameworks using temperature driven active learning | doi:

## 本实例步骤描述
审计结构、能量、力和目标状态的覆盖范围。

## 本实例执行 prompt
读取 {REFERENCE_DATA}，检查重复、异常、化学空间和高温/缺陷/界面覆盖；缺少目标状态时标记 BLOCKED。

## 本实例输入槽
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | hint=结构、能量、力、应力、计算设置和数据许可 | default=extxyz/npz/数据库导出

## 本实例产出
- 数据审计
- 训练验证划分

## 本实例质量门禁
- 训练验证测试严格隔离
- 标签计算设置可追溯

## 可调资源（edge:resource，仅真实存在）
- models/data-efficient-machine-learning-potentials-modeling-catalytic

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
