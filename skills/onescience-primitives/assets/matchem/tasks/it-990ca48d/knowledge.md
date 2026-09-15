# 实例任务：材料与对照方案定义 @ CrCoNi中高熵合金低温断裂韧性分析

- domain: matchem
- 骨架: tk-matchem-aa2bf571
- 场景: sc-8daa397c (CrCoNi中高熵合金低温断裂韧性分析)
- step_id: s01
- depend: []

## 场景研究主体
- CrCoNi中高熵合金低温断裂韧性分析
- 关联论文: Exceptional fracture toughness of CrCoNi-based medium- and high-entropy alloys at 20 kelvin | doi:

## 本实例步骤描述
固定成分、工艺、微结构和对照样。

## 本实例执行 prompt
读取 {MATERIAL_AND_PROCESS} 与 {LOAD_OR_REACTION_CONDITION}，定义变量、对照和失效/性能判据。

## 本实例输入槽
- {MATERIAL_AND_PROCESS} | required=True | type=object | var_name=材料与工艺参数 | hint=成分、微结构、制备或加工路径及对照样。 | default={'composition': 'specified', 'process': 'specified'}
- {LOAD_OR_REACTION_CONDITION} | required=True | type=object | var_name=载荷或反应条件 | hint=温度、应变率、环境、反应时间或电化学条件 | default={'temperature_K': 298}

## 本实例产出
- 试样或模型清单
- 对照方案

## 本实例质量门禁
- 变量单一可追溯
- 工况与单位明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
