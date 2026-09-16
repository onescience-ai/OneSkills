# 实例任务：能量力应力与外推验证 @ 层状材料可迁移机器学习原子势验证

- domain: matchem
- 骨架: matchem-energy-force-stress-and-extrapolation-validation-task
- 场景: matchem-layered-material-transferable-ml-atomic-potential-validation-scenario (层状材料可迁移机器学习原子势验证)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 层状材料可迁移机器学习原子势验证
- 关联论文: Accurate, transferable, and verifiable machine-learned interatomic potentials for layered materials | doi:

## 本实例步骤描述
评估预测误差、外推和物理一致性。

## 本实例执行 prompt
在独立集上报告能量、力、应力误差和外推检测，不以训练误差代替泛化。

## 本实例输入槽
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | hint=结构、能量、力、应力、计算设置和数据许可 | default=extxyz/npz/数据库导出

## 本实例产出
- 验证报告
- 失败构型清单

## 本实例质量门禁
- 独立集不参与调参
- 外推构型单独标记

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
