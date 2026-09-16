# 实例任务：模型配置与训练 @ CFD_S043

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-natural-gradient-and-loss-balanced-pinn-stable-training-scenario (CFD_S043)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S043
- 关联论文: MultiAdam_ Parameter-wise Scale-invariant Optimizer for Multiscale Training of Physics-informed Neural Networks | doi:; Collapsing Taylor Mode Automatic Differentiation | doi:; FP64 is All You Need_ Rethinking Failure Modes in Physics-Informed Neural Networks | doi:; Improving Energy Natural Gradient Descent through Woodbury, Momentum, and Randomization | doi:; Challenges in Training PINNs_ A Loss Landscape Perspective | doi:; Achieving High Accuracy with PINNs via Energy Natural Gradient Descent | doi:; Gradient Descent Finds the Global Optima of Two-Layer Physics-Informed Neural Networks | doi:; Accelerated Training of Physics-Informed Neural Networks (PINNs) using Meshless Discretizations | doi:; Is L2 Physics Informed Loss Always Suitable for Training Physics Informed Neural Network | doi:; Active training of physics-informed neural networks to aggregate and interpolate parametric solutions to the | doi:; ConFIG_ Towards Conflict-free Training of Physics Informed Neural Networks | doi:; Near-optimal Sketchy Natural Gradients for Physics-Informed Neural Networks | doi:; Enhancing Stability of Physics-Informed Neural Network Training Through Saddle-Point Reformulation | doi:; Fast Convergence of Natural Gradient Descent for Over-parameterized Physics-Informed Neural Networks | doi:; Fast training of accurate physics-informed neural networks without gradient descent | doi:; Harmonized Cone for Feasible and Non-conflict Directions in Training Physics-Informed Neural Networks | doi:

## 本实例步骤描述
训练PINN、Natural-gradient optimizer完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认PINN、Natural-gradient optimizer，和{TRAIN_CONFIG}训练“自然梯度与损失平衡PINN稳定训练”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=PINN、Natural-gradient optimizer
- {TRAIN_CONFIG} | required=True | type=object | var_name=训练配置 | hint=超参数和随机种子 | default={'framework': 'PyTorch', 'epochs': 100, 'batch_size': 8, 'learning_rate': 0.001, 'seed': 42, 'early_stopping_patience': 15}
- {INIT_CHECKPOINT} | required=False | type=doc | var_name=初始权重 | hint=可选预训练权重 | default=

## 本实例产出
- best_checkpoint.pt
- train_config.json
- training_metrics.csv
- environment.txt

## 本实例质量门禁
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
