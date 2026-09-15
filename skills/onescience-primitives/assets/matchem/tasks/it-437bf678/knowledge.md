# 实例任务：活性选择性稳定性联评 @ CuSn原子界面CO2到CO选择性优化

- domain: matchem
- 骨架: tk-matchem-33569753
- 场景: sc-449525cd (CuSn原子界面CO2到CO选择性优化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CuSn原子界面CO2到CO选择性优化
- 关联论文: Isolated copper–tin atomic interfaces tuning electrocatalytic CO2 conversion | doi:

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
