# 骨架任务：参考数据审计与覆盖定义

- domain: matchem
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 审计结构、能量、力和目标状态的覆盖范围。

## 执行 prompt（跨场景聚合去重）
- 读取 {REFERENCE_DATA}，检查重复、异常、化学空间和高温/缺陷/界面覆盖；缺少目标状态时标记 BLOCKED。

## 输入槽（var/hint/default）
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | hint=结构、能量、力、应力、计算设置和数据许可 | default=extxyz/npz/数据库导出

## 产出
- 数据审计
- 训练验证划分

## 质量门禁 quality_gate
- 标签计算设置可追溯
- 训练验证测试严格隔离

## 可调资源（edge:resource，仅真实存在）
- models/data-efficient-machine-learning-potentials-modeling-catalytic

## 实例任务（本骨架在各场景的实例化）
- matchem-reference-data-audit-coverage-catalytic-reaction-ml-inst
- matchem-reference-data-audit-coverage-defective-potential-energy-inst
- matchem-reference-data-audit-coverage-hfo2-amorphous-liquid-ml-inst
- matchem-reference-data-audit-coverage-layered-material-transferabl-inst
- matchem-reference-data-audit-coverage-mof-quantum-ml-potential-inst
- matchem-reference-data-audit-coverage-neural-network-potential-inst
- matchem-reference-data-audit-coverage-polarizable-long-range-inst

## 复用场景
- HfO2非晶液相机器学习势主动学习
- MOF量子精度机器学习势温度主动学习
- 催化反应机器学习势主动学习与增强采样
- 可极化长程相互作用基础机器学习势
- 层状材料可迁移机器学习原子势验证
- 神经网络势长程静电自洽训练
- 缺陷势能面机器学习势探索
