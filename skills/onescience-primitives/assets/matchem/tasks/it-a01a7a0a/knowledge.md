# 实例任务：参考数据审计与覆盖定义 @ 缺陷势能面机器学习势探索

- domain: matchem
- 骨架: tk-matchem-8c781538
- 场景: sc-e5b3557e (缺陷势能面机器学习势探索)
- step_id: s01
- depend: []

## 场景研究主体
- 缺陷势能面机器学习势探索
- 关联论文: Machine learning potential assisted exploration of complex defect potential energy surfaces | doi:

## 本实例步骤描述
审计结构、能量、力和目标状态的覆盖范围。

## 本实例执行 prompt
读取 {REFERENCE_DATA}，检查重复、异常、化学空间和高温/缺陷/界面覆盖；缺少目标状态时标记 BLOCKED。

## 本实例输入槽
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | hint=结构、能量、力、应力、计算设置和数据许可 | default=extxyz/npz/数据库导出

## 本实例产出
- 数据审计
- 训练验证划分

## 本实例质量门禁
- 训练验证测试严格隔离
- 标签计算设置可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
