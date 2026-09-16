# 实例任务：结构电子或功能响应获取 @ 磷烯单层缺陷工程与空气稳定化

- domain: matchem
- 骨架: matchem-structure-electronic-or-functional-response-acquisition-task
- 场景: matchem-phosphorene-monolayer-defect-engineering-air-stability-scenario (磷烯单层缺陷工程与空气稳定化)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 磷烯单层缺陷工程与空气稳定化
- 关联论文: Producing air-stable monolayers of phosphorene and their defect engineering | doi:

## 本实例步骤描述
计算或测量缺陷形成、迁移、光学或催化响应。

## 本实例执行 prompt
在 {ENVIRONMENT} 下获取响应数据，保留软件/仪器、参数和原始文件。

## 本实例输入槽
- {ENVIRONMENT} | required=False | type=object | var_name=环境与表征条件 | hint=温度、气氛、电位、光照、应力或表征方案。 | default={'temperature_K': 298}

## 本实例产出
- 原始响应数据
- 缺陷特征

## 本实例质量门禁
- 参考态和校正项记录
- 对照样齐全

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
