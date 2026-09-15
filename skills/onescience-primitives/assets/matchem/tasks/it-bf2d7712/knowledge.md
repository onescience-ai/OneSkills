# 实例任务：传质或吸附性能获取 @ MOF分子扩散增强CO2捕集性能评估

- domain: matchem
- 骨架: tk-matchem-b70feeee
- 场景: sc-1ac80f69 (MOF分子扩散增强CO2捕集性能评估)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- MOF分子扩散增强CO2捕集性能评估
- 关联论文: Molecular diffusion enhanced performance evaluation of metal-organic frameworks for CO2 capture | doi:

## 本实例步骤描述
计算或测量吸附、扩散、渗透和选择性。

## 本实例执行 prompt
按 {EVALUATION_CONFIG} 获取原始性能数据，记录模型、仪器、平衡时间和对照。

## 本实例输入槽
- {EVALUATION_CONFIG} | required=False | type=object | var_name=评价方法 | hint=说明吸附、扩散、渗透、分离或实验测试方法 | default={'method': 'user-confirmed'}

## 本实例产出
- 原始性能数据
- 方法日志

## 本实例质量门禁
- 平衡与稳态判据明确
- 空白和对照样可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
