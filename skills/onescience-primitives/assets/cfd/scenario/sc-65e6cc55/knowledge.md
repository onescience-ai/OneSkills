# 场景：CFD_S043

- domain: cfd
- type: paper_scenario
- 算力: ['NULL'] (is_one_hpc=[False])
- 模型: ['PINN', 'Natural-gradient optimizer']
- 工具: []

## 研究意图（agent_task_prompt）
（源场景未提供）

## 客户端请求
- task_title: 
- request: 
- scientific_context: 
- desired_outcome: 
- executor_role: 

## 问题与适用性
面向PINN基准方程与训练诊断数据完成自然梯度与损失平衡PINN稳定训练。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流步骤（→workflow/→tasks）
- s01 数据接入与契约核验
- s02 预处理与数据切分
- s03 模型配置与训练
- s04 方程求解与物理残差恢复
- s05 任务验收与适用域判定

## 关联论文
- MultiAdam_ Parameter-wise Scale-invariant Optimizer for Multiscale Training of Physics-informed Neural Networks | doi:
- Collapsing Taylor Mode Automatic Differentiation | doi:
- FP64 is All You Need_ Rethinking Failure Modes in Physics-Informed Neural Networks | doi:
- Improving Energy Natural Gradient Descent through Woodbury, Momentum, and Randomization | doi:
- Challenges in Training PINNs_ A Loss Landscape Perspective | doi:
- Achieving High Accuracy with PINNs via Energy Natural Gradient Descent | doi:
- Gradient Descent Finds the Global Optima of Two-Layer Physics-Informed Neural Networks | doi:
- Accelerated Training of Physics-Informed Neural Networks (PINNs) using Meshless Discretizations | doi:
- Is L2 Physics Informed Loss Always Suitable for Training Physics Informed Neural Network | doi:
- Active training of physics-informed neural networks to aggregate and interpolate parametric solutions to the | doi:
- ConFIG_ Towards Conflict-free Training of Physics Informed Neural Networks | doi:
- Near-optimal Sketchy Natural Gradients for Physics-Informed Neural Networks | doi:
- Enhancing Stability of Physics-Informed Neural Network Training Through Saddle-Point Reformulation | doi:
- Fast Convergence of Natural Gradient Descent for Over-parameterized Physics-Informed Neural Networks | doi:
- Fast training of accurate physics-informed neural networks without gradient descent | doi:
- Harmonized Cone for Feasible and Non-conflict Directions in Training Physics-Informed Neural Networks | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
