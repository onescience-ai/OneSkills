# 骨架任务：根源势函数训练

- domain: matchem
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 按已声明的根源模型训练机器学习势。

## 执行 prompt（跨场景聚合去重）
- 使用 {POTENTIAL_CONFIG} 训练势函数，记录模型根源、版本、随机种子和所有超参数。

## 输入槽（var/hint/default）
- {POTENTIAL_CONFIG} | required=True | type=object | var_name=势函数根源模型配置 | hint=模型根源、截断、特征、训练种子和版本。 | default={'model': 'specified root potential', 'seed': 42}

## 产出
- 模型检查点
- 训练日志

## 质量门禁 quality_gate
- 模型名称不以变体替代根源
- 训练过程可复现

## 可调资源（edge:resource，仅真实存在）
- models/mace

## 实例任务（本骨架在各场景的实例化）
- it-080df366
- it-1141680f
- it-1e04d9e3
- it-6c805e1b
- it-98891d79
- it-a5cf5b54
- it-b23583d0

## 复用场景
- HfO2非晶液相机器学习势主动学习
- MOF量子精度机器学习势温度主动学习
- 催化反应机器学习势主动学习与增强采样
- 可极化长程相互作用基础机器学习势
- 层状材料可迁移机器学习原子势验证
- 神经网络势长程静电自洽训练
- 缺陷势能面机器学习势探索
