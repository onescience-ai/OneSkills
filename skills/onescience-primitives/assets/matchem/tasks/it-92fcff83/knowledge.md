# 实例任务：约束候选生成与排序 @ 卤化物钙钛矿兼容分子数据驱动优化

- domain: matchem
- 骨架: tk-matchem-0ab57b24
- 场景: sc-5bd05055 (卤化物钙钛矿兼容分子数据驱动优化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 卤化物钙钛矿兼容分子数据驱动优化
- 关联论文: Data-driven optimization and machine learning analysis of compatible molecules for halide perovskite material | doi:

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
