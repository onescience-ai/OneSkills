# 实例任务：活性选择性稳定性联评 @ Fe单原子催化硝酸盐还原制氨

- domain: matchem
- 骨架: matchem-activity-selectivity-stability-joint-evaluation-task
- 场景: matchem-fe-single-atom-nitrate-reduction-ammonia-synthesis-scenario (Fe单原子催化硝酸盐还原制氨)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- Fe单原子催化硝酸盐还原制氨
- 关联论文: Electrochemical ammonia synthesis via nitrate reduction on Fe single atom catalyst | doi:

## 本实例步骤描述
比较目标产物、竞争反应和结构稳定性。

## 本实例执行 prompt
在 {REACTION_CONDITION} 下联评活性、选择性、稳定性和副反应，输出限制步骤或证据缺口。

## 本实例输入槽
- {REACTION_CONDITION} | required=True | type=object | var_name=反应条件 | hint=目标产物、温度、压力、电位/pH、反应物 | default={'target_product': 'specified product', 'temperature_K': 298}

## 本实例产出
- 综合性能表
- 限制步骤分析

## 本实例质量门禁
- 不以单一描述符替代完整选择性分析
- 长期稳定性不由短时数据替代

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
