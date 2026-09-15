# 实例任务：根源模型训练与适用域评估 @ 半赫斯勒热电材料无监督发现

- domain: matchem
- 骨架: tk-matchem-61a3bb1e
- 场景: sc-85c55ae3 (半赫斯勒热电材料无监督发现)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 半赫斯勒热电材料无监督发现
- 关联论文: Unsupervised machine learning for discovery of promising half-Heusler thermoelectric materials | doi:

## 本实例步骤描述
按记录的根源模型训练并评估泛化和适用域。

## 本实例执行 prompt
使用 {MODEL_CONFIG} 训练模型，保留随机种子、特征和版本；报告交叉验证、外部测试与适用域。

## 本实例输入槽
- {MODEL_CONFIG} | required=True | type=object | var_name=模型配置 | hint=模型根源、版本、特征、随机种子和超参数必 | default={'model': '按论文或用户配置', 'seed': 42}

## 本实例产出
- 模型检查点
- 性能指标
- 适用域报告

## 本实例质量门禁
- 外部测试与训练数据隔离
- 不能以训练误差替代泛化性能

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
