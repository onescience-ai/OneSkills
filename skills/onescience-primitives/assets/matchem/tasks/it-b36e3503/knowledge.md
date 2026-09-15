# 实例任务：能量力应力与外推验证 @ MOF量子精度机器学习势温度主动学习

- domain: matchem
- 骨架: tk-matchem-03396a62
- 场景: sc-4dcd5267 (MOF量子精度机器学习势温度主动学习)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- MOF量子精度机器学习势温度主动学习
- 关联论文: Quantum-accurate machine learning potentials for metal-organic frameworks using temperature driven active learning | doi:

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
