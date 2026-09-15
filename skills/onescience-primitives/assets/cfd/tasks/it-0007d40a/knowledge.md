# 实例任务：方程求解与物理残差恢复 @ CFD_S045

- domain: cfd
- 骨架: tk-cfd-ebecc632
- 场景: sc-100c0711 (CFD_S045)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S045
- 关联论文: Universal Physics-Informed Neural Networks_ Symbolic Differential Operator Discovery with Sparse Data | doi:; Sub-Sequential Physics-Informed Learning with State Space Model | doi:; Understanding Generalization in Physics Informed Models through Affine Variety Dimensions | doi:; Competitive Physics Informed Networks | doi:; D-CIPHER_ Discovery of Closed-form Partial Differential Equations | doi:; Homotopy-based training of NeuralODEs for accurate dynamics discovery | doi:; Learning Neural Constitutive Laws from Motion Observations for Generalizable PDE Dynamics | doi:; Symbolic Physics Learner_ Discovering governing equations via Monte Carlo tree search | doi:; Deep hidden physics models_ Deep learning of nonlinear partial differential equations | doi:; Physics informed deep learning (Part II)_ Data-driven discovery of nonlinear partial differential equations | doi:; Learning fluid physics from highly turbulent data using sparse physics-informed discovery of empirical relat | doi:

## 本实例步骤描述
在查询配点或网格上恢复解场、导数、边界值与方程残差。

## 本实例执行 prompt
加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差。保存解场与残差场；禁止只依据训练损失判定方程已求解。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- solution_fields/
- pde_residuals/
- boundary_residuals.csv

## 本实例质量门禁
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
