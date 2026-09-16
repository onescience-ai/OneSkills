# 实例任务：模型配置与训练 @ CFD_S020

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-dynamic-graph-network-and-adaptive-mesh-physics-time-series-scenario (CFD_S020)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S020
- 关联论文: EvoMesh_ Adaptive Physical Simulation with Hierarchical Graph Evolutions | doi:; Geometric and Physical Constraints Synergistically Enhance Neural PDE Surrogates | doi:; Breaking the Discretization Barrier of Continuous Physics Simulation Learning | doi:; Neural SPH_ Improved Neural Modeling of Lagrangian Fluid Dynamics | doi:; Learning 3D Garment Animation from Trajectories of A Piece of Cloth | doi:; Pluvial Flood Emulation with Hydraulics-informed Message Passing | doi:; A Stable and Scalable Method for Solving Initial Value PDEs with Neural Networks | doi:; ACMP_ Allen-Cahn Message Passing with Attractive and Repulsive Forces for Graph Neural Networks | doi:; Learning Neural PDE Solvers with Parameter-Guided Channel Attention | doi:; Newton–Cotes Graph Neural Networks_ On the Time Evolution of Dynamic Systems | doi:; Message Passing Neural PDE Solvers | doi:

## 本实例步骤描述
训练Message-passing neural PDE solver、Adaptive mesh GNN完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Message-passing neural PDE solver、Adaptive mesh GNN，和{TRAIN_CONFIG}训练“动态图网络与自适应网格物理时序模拟”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Message-passing neural PDE solver、Adaptive mesh GNN
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
- models/meshgraphnet

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
