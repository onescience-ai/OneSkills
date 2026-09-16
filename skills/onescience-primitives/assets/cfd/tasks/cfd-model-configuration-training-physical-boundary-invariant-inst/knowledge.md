# 实例任务：模型配置与训练 @ CFD_S059

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-physical-boundary-invariant-constrained-neural-operator-learning-scenario (CFD_S059)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S059
- 关联论文: Guiding Continuous Operator Learning through Physics-Based Boundary Constraints | doi:; Holistic Physics Solver_ Learning PDEs in a Unified Spectral-Physical Space | doi:; Learn Singularly Perturbed Solutions via Homotopy Dynamics | doi:; A Physics-preserved Transfer Learning Method for Differential Equations | doi:; Nonlocal Attention Operator_ Materializing Hidden Knowledge Towards Interpretable Physics Discovery | doi:; PAPM_ A Physics-aware Proxy Model for Process Systems | doi:; Training neural operators to preserve invariant measures of chaotic attractors | doi:; Generic bounds on the approximation error for physics-informed (and) operator learning | doi:; Buckingham $_pi$-Invariant Test‐Time Projection for Robust PDE Surrogate Modeling | doi:; Towards Generalizable PDE Dynamics Forecasting via Physics-Guided Invariant Learning | doi:; WAN3DNS_ Weak Adversarial Networks for Solving 3D Incompressible Navier-Stokes Equations | doi:; Wrong-Physics Backdoors in Neural PDE Operators | doi:

## 本实例步骤描述
训练Physics-constrained neural operator完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Physics-constrained neural operator，和{TRAIN_CONFIG}训练“物理边界与不变量约束神经算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Physics-constrained neural operator
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
- models/fno

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
