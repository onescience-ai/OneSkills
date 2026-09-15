# 实例任务：数据接入与契约核验 @ CFD_S043

- domain: cfd
- 骨架: tk-cfd-54dc529a
- 场景: sc-65e6cc55 (CFD_S043)
- step_id: s01
- depend: []

## 场景研究主体
- CFD_S043
- 关联论文: MultiAdam_ Parameter-wise Scale-invariant Optimizer for Multiscale Training of Physics-informed Neural Networks | doi:; Collapsing Taylor Mode Automatic Differentiation | doi:; FP64 is All You Need_ Rethinking Failure Modes in Physics-Informed Neural Networks | doi:; Improving Energy Natural Gradient Descent through Woodbury, Momentum, and Randomization | doi:; Challenges in Training PINNs_ A Loss Landscape Perspective | doi:; Achieving High Accuracy with PINNs via Energy Natural Gradient Descent | doi:; Gradient Descent Finds the Global Optima of Two-Layer Physics-Informed Neural Networks | doi:; Accelerated Training of Physics-Informed Neural Networks (PINNs) using Meshless Discretizations | doi:; Is L2 Physics Informed Loss Always Suitable for Training Physics Informed Neural Network | doi:; Active training of physics-informed neural networks to aggregate and interpolate parametric solutions to the | doi:; ConFIG_ Towards Conflict-free Training of Physics Informed Neural Networks | doi:; Near-optimal Sketchy Natural Gradients for Physics-Informed Neural Networks | doi:; Enhancing Stability of Physics-Informed Neural Network Training Through Saddle-Point Reformulation | doi:; Fast Convergence of Natural Gradient Descent for Over-parameterized Physics-Informed Neural Networks | doi:; Fast training of accurate physics-informed neural networks without gradient descent | doi:; Harmonized Cone for Feasible and Non-conflict Directions in Training Physics-Informed Neural Networks | doi:

## 本实例步骤描述
接入PINN基准方程与训练诊断数据，核验样本、变量、单位、网格坐标及许可。

## 本实例执行 prompt
读取{DATASET_PATH}中的{DATASET_NAME}，为“自然梯度与损失平衡PINN稳定训练”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {DATASET_PATH} | required=True | type=doc | var_name=数据集路径 | hint=目录或清单文件 | default=
- {DATASET_NAME} | required=True | type=str | var_name=数据集名称 | hint=来源与数据版本 | default=PINN基准方程与训练诊断数据
- {DATA_CONTRACT} | required=False | type=object | var_name=数据契约 | hint=变量单位网格定义 | default={'input_fields': [], 'target_fields': [], 'units': {}, 'coordinates': 'dataset_native'}

## 本实例产出
- dataset_manifest.json
- data_contract.json
- data_audit.md

## 本实例质量门禁
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
