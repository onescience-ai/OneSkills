# 实例任务：弛豫与稳定性排序 @ 图神经网络晶体结构预测与优化

- domain: matchem
- 骨架: tk-matchem-856f4df0
- 场景: sc-d6eba2e8 (图神经网络晶体结构预测与优化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 图神经网络晶体结构预测与优化
- 关联论文: Crystal structure prediction by combining graph network and optimization algorithm | doi:

## 本实例步骤描述
对候选结构统一弛豫并计算稳定性指标。

## 本实例执行 prompt
按 {RELAX_CONFIG} 弛豫候选，比较能量、体积和稳定性；不同设置的结果不得直接排序。

## 本实例输入槽
- {RELAX_CONFIG} | required=False | type=object | var_name=弛豫设置 | hint=如采用第一性原理计算，必须写明软件、泛函 | default={'method': 'user-confirmed'}

## 本实例产出
- 弛豫结构
- 稳定性排序

## 本实例质量门禁
- 收敛标准统一
- 参考态定义明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
