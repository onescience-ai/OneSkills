# 实例任务：活性位与反应网络定义 @ 氧化衍生铜CO2电还原活性位分析

- domain: matchem
- 骨架: matchem-active-site-reaction-network-definition-task
- 场景: matchem-oxidation-derived-copper-co2-electroreduction-active-site-scenario (氧化衍生铜CO2电还原活性位分析)
- step_id: s01
- depend: []

## 场景研究主体
- 氧化衍生铜CO2电还原活性位分析
- 关联论文: The nature of active sites for carbon dioxide electroreduction over oxide-derived copper catalysts | doi:

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
- tools/molecular-structure-preparation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
