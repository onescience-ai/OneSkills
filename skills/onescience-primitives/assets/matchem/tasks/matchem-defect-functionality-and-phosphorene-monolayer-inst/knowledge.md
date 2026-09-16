# 实例任务：缺陷功能与稳定性排序 @ 磷烯单层缺陷工程与空气稳定化

- domain: matchem
- 骨架: matchem-defect-functionality-and-stability-ranking-task
- 场景: matchem-phosphorene-monolayer-defect-engineering-air-stability-scenario (磷烯单层缺陷工程与空气稳定化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 磷烯单层缺陷工程与空气稳定化
- 关联论文: Producing air-stable monolayers of phosphorene and their defect engineering | doi:

## 本实例步骤描述
比较目标功能、副作用和环境稳定性。

## 本实例执行 prompt
对缺陷候选排序，区分热力学可行性、动力学可达性和实验可制备性。

## 本实例输入槽
- {ENVIRONMENT} | required=False | type=object | var_name=环境与表征条件 | hint=温度、气氛、电位、光照、应力或表征方案。 | default={'temperature_K': 298}

## 本实例产出
- 候选排序
- 风险与证据缺口

## 本实例质量门禁
- 不将形成能直接等同于实际浓度
- 适用域明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
