# 实例任务：方程求解与物理残差恢复 @ CFD_S043

- domain: cfd
- 骨架: cfd-equation-solving-physics-residual-restoration-task
- 场景: cfd-natural-gradient-and-loss-balanced-pinn-stable-training-scenario (CFD_S043)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S043
- 关联论文: MultiAdam_ Parameter-wise Scale-invariant Optimizer for Multiscale Training of Physics-informed Neural Networks | doi:; Collapsing Taylor Mode Automatic Differentiation | doi:; FP64 is All You Need_ Rethinking Failure Modes in Physics-Informed Neural Networks | doi:; Improving Energy Natural Gradient Descent through Woodbury, Momentum, and Randomization | doi:; Challenges in Training PINNs_ A Loss Landscape Perspective | doi:; Achieving High Accuracy with PINNs via Energy Natural Gradient Descent | doi:; Gradient Descent Finds the Global Optima of Two-Layer Physics-Informed Neural Networks | doi:; Accelerated Training of Physics-Informed Neural Networks (PINNs) using Meshless Discretizations | doi:; Is L2 Physics Informed Loss Always Suitable for Training Physics Informed Neural Network | doi:; Active training of physics-informed neural networks to aggregate and interpolate parametric solutions to the | doi:; ConFIG_ Towards Conflict-free Training of Physics Informed Neural Networks | doi:; Near-optimal Sketchy Natural Gradients for Physics-Informed Neural Networks | doi:; Enhancing Stability of Physics-Informed Neural Network Training Through Saddle-Point Reformulation | doi:; Fast Convergence of Natural Gradient Descent for Over-parameterized Physics-Informed Neural Networks | doi:; Fast training of accurate physics-informed neural networks without gradient descent | doi:; Harmonized Cone for Feasible and Non-conflict Directions in Training Physics-Informed Neural Networks | doi:

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
