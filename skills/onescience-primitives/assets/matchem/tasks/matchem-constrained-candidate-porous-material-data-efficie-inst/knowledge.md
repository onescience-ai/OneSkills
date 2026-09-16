# 实例任务：约束候选生成与排序 @ 多孔材料数据高效基础模型构建

- domain: matchem
- 骨架: matchem-constrained-candidate-generation-and-ranking-task
- 场景: matchem-porous-material-data-efficient-foundation-model-construction-scenario (多孔材料数据高效基础模型构建)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 多孔材料数据高效基础模型构建
- 关联论文: A data-efficient foundation model for porous materials based on expert-guided supervised learning | doi:

## 本实例步骤描述
在定义的成分或工艺空间内生成候选并按目标排序。

## 本实例执行 prompt
在 {TARGET} 的约束内生成候选；同时报告预测值、不确定性和适用域标记。

## 本实例输入槽
- {TARGET} | required=True | type=str | var_name=优化目标 | hint=明确目标性质、单位、方向和约束。 | default=目标材料性质

## 本实例产出
- 候选排序
- 预测值与不确定性

## 本实例质量门禁
- 所有候选满足硬约束
- 适用域外候选单独标识

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
