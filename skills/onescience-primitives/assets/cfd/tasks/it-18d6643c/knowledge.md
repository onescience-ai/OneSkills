# 实例任务：模型配置与训练 @ CFD_S052

- domain: cfd
- 骨架: tk-cfd-18078463
- 场景: sc-ae96e6d8 (CFD_S052)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S052
- 关联论文: PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations | doi:; Curvature-aware Graph Attention for PDEs on Manifolds | doi:; Neural Interpretable PDEs_ Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Di | doi:; Unisolver_ PDE-Conditional Transformers Towards Universal Neural PDE Solvers | doi:; S-Crescendo_ A Nested Transformer Weaving Framework for Scalable Nonlinear System in S-Domain Representation | doi:; FUSE_ Fast Unified Simulation and Estimation for PDEs | doi:; DPOT_ Auto-Regressive Denoising Operator Transformer for Large-Scale PDE Pre-Training | doi:; Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators | doi:; Positional Knowledge is All You Need_ Position-induced Transformer (PiT) for Operator Learning | doi:; Choose a Transformer_ Fourier or Galerkin | doi:

## 本实例步骤描述
训练PDE Transformer、Universal Physics Transformer完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认PDE Transformer、Universal Physics Transformer，和{TRAIN_CONFIG}训练“Transformer通用PDE算子预训练与微调”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=PDE Transformer、Universal Physics Transformer
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
- models/transformer

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
