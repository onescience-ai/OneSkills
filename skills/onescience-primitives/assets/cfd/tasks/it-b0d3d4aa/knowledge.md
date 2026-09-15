# 实例任务：预处理与数据切分 @ CFD_S036

- domain: cfd
- 骨架: tk-cfd-446c2dc0
- 场景: sc-51daab37 (CFD_S036)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- CFD_S036
- 关联论文: NSFnets (Navier–Stokes Flow Nets): Physics-Informed Neural Networks for the Incompressible Navier–Stokes Equations | doi:; Physics-informed deep learning for incompressible laminar flows | doi:; Self-adaptive loss balanced Physics-informed neural networks for the incompressible Navier-Stokes equations | doi:; Complementary, Not Cumulative_ Interaction Effects in Physics-Informed Neural Networks for Navier - Stokes Vortex Shedding | doi:; NeuralFlowNet_ Towards Data-Free Physics-Informed Neural Network Solutions of Navier-Stokes Equations Across Low and High Reynolds Numbers | doi:

## 本实例步骤描述
统一物理量与表示，按几何、工况或时间构造无泄漏切分。

## 本实例执行 prompt
依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。

## 本实例输入槽
- {SPLIT_CONFIG} | required=True | type=object | var_name=切分配置 | hint=按对象工况切分 | default={'train': 0.7, 'validation': 0.15, 'test': 0.15, 'seed': 42, 'group_by': 'geometry_or_trajectory'}
- {TARGET_FIELDS} | required=True | type=list[str] | var_name=目标变量 | hint=待预测物理量 | default=['按data_contract.json填写']
- {NONDIMENSIONALIZE} | required=False | type=bool | var_name=是否无量纲化 | hint=统一跨工况量纲 | default=True

## 本实例产出
- train_manifest.json
- validation_manifest.json
- test_manifest.json
- normalization.json

## 本实例质量门禁
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
