# 骨架任务：分子动力学或结构探索验证

- domain: matchem
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 在目标条件下进行短程验证和失效分析。

## 执行 prompt（跨场景聚合去重）
- 按 {MD_CONFIG} 进行验证；将势函数不稳定、非物理结构或适用域外结果标记 REJECT/BLOCKED。

## 输入槽（var/hint/default）
- {MD_CONFIG} | required=False | type=object | var_name=分子动力学验证配置 | hint=温度、压力、时间步、体系尺寸和参考计算。 | default={'temperature_K': 300, 'steps': 10000}

## 产出
- MD/探索轨迹
- PASS/REJECT/BLOCKED
- 适用域结论

## 质量门禁 quality_gate
- 不把势函数置信度当作量子或实验验证
- 软件版本和命令完整

## 可调资源（edge:resource，仅真实存在）
- models/mace

## 实例任务（本骨架在各场景的实例化）
- it-5dab6943
- it-8302be42
- it-84bf4812
- it-889639ad
- it-b9089ef1
- it-cf2a255c
- it-d3517cfa

## 复用场景
- HfO2非晶液相机器学习势主动学习
- MOF量子精度机器学习势温度主动学习
- 催化反应机器学习势主动学习与增强采样
- 可极化长程相互作用基础机器学习势
- 层状材料可迁移机器学习原子势验证
- 神经网络势长程静电自洽训练
- 缺陷势能面机器学习势探索
