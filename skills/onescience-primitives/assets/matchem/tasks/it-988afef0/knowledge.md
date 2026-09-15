# 实例任务：活性位与反应网络定义 @ MoS2CoSe2异质结构析氢催化设计

- domain: matchem
- 骨架: tk-matchem-bafd6a4a
- 场景: sc-864efe88 (MoS2CoSe2异质结构析氢催化设计)
- step_id: s01
- depend: []

## 场景研究主体
- MoS2CoSe2异质结构析氢催化设计
- 关联论文: An efficient molybdenum disulfide/cobalt diselenide hybrid catalyst for electrochemical hydrogen generation | doi:

## 本实例步骤描述
建立催化剂活性位、目标产物和竞争反应网络。

## 本实例执行 prompt
读取 {CATALYST_STRUCTURE} 与 {REACTION_CONDITION}，定义活性位、反应中间体和竞争路径；缺少电位或对照条件时标记 BLOCKED。

## 本实例输入槽
- {CATALYST_STRUCTURE} | required=True | type=doc | var_name=催化剂结构或制备信息 | hint=活性位、晶面、组成、缺陷或制备方法。 | default=CIF/POSCAR/制备配方
- {REACTION_CONDITION} | required=True | type=object | var_name=反应条件 | hint=目标产物、温度、压力、电位/pH、反应物 | default={'target_product': 'specified product', 'temperature_K': 298}

## 本实例产出
- 活性位模型
- 反应网络

## 本实例质量门禁
- 活性位和目标产物明确
- 竞争反应未被忽略

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
