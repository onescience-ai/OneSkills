# 实例任务：选择性稳定性与能耗分析 @ MOF燃烧前CO2捕集遗传算法筛选

- domain: matchem
- 骨架: tk-matchem-edbfdf30
- 场景: sc-d9f04a1d (MOF燃烧前CO2捕集遗传算法筛选)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- MOF燃烧前CO2捕集遗传算法筛选
- 关联论文: In silico discovery of metal-organic frameworks for precombustion CO 2 capture using a genetic algorithm | doi:

## 本实例步骤描述
在真实进料约束下比较选择性、通量、循环稳定性和能耗。

## 本实例执行 prompt
根据 {FEED_AND_OPERATION} 分析竞争吸附、污染、湿度或机械稳定性，输出权衡关系。

## 本实例输入槽
- {FEED_AND_OPERATION} | required=True | type=object | var_name=进料与运行条件 | hint=组分、浓度、湿度、压力、温度、流量或电场 | default={'feed': 'specified mixture', 'temperature_K': 298}

## 本实例产出
- 性能权衡图
- 失效风险清单

## 本实例质量门禁
- 不将单组分吸附直接等同于混合物分离
- 未测稳定性明确标注

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
