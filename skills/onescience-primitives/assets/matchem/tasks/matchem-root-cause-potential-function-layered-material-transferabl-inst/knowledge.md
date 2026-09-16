# 实例任务：根源势函数训练 @ 层状材料可迁移机器学习原子势验证

- domain: matchem
- 骨架: matchem-root-cause-potential-function-training-task
- 场景: matchem-layered-material-transferable-ml-atomic-potential-validation-scenario (层状材料可迁移机器学习原子势验证)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 层状材料可迁移机器学习原子势验证
- 关联论文: Accurate, transferable, and verifiable machine-learned interatomic potentials for layered materials | doi:

## 本实例步骤描述
按已声明的根源模型训练机器学习势。

## 本实例执行 prompt
使用 {POTENTIAL_CONFIG} 训练势函数，记录模型根源、版本、随机种子和所有超参数。

## 本实例输入槽
- {POTENTIAL_CONFIG} | required=True | type=object | var_name=势函数根源模型配置 | hint=模型根源、截断、特征、训练种子和版本。 | default={'model': 'specified root potential', 'seed': 42}

## 本实例产出
- 模型检查点
- 训练日志

## 本实例质量门禁
- 模型名称不以变体替代根源
- 训练过程可复现

## 可调资源（edge:resource，仅真实存在）
- models/mace
- tools/reaxnet-polarizable-long-range-neural-network-potential

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
