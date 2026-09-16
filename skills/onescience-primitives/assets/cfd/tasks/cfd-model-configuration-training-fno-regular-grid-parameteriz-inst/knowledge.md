# 实例任务：模型配置与训练 @ CFD_S048

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-fno-regular-grid-parameterized-pde-operator-learning-scenario (CFD_S048)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S048
- 关联论文: Tucker-FNO_ Tensor Tucker-Fourier Neural Operator and its Universal Approximation Theory | doi:; Fourier Neural Operator for Parametric Partial Differential Equations | doi:; Factorized Fourier Neural Operators | doi:; Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for Fourier Neural Operators | doi:; Sensitivity-Constrained Fourier Neural Operators for Forward and Inverse Problems in Parametric Differential Equations | doi:; Beyond Regular Grids_ Fourier-Based Neural Operators on Arbitrary Domains | doi:; Domain Agnostic Fourier Neural Operators | doi:; U-FNO_ An Enhanced Fourier Neural Operator-Based Deep-Learning Model for Multiphase Flow | doi:; Understanding the Expressivity and Trainability of Fourier Neural Operator_ A Mean-Field Perspective | doi:; Spectral-Refiner_ Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows | doi:; Extending Fourier Neural Operators for Modeling Parameterized and Coupled PDEs | doi:; Evaluation of State-of-the-Art Deep Learning Architectures for Aerodynamical Predictions | doi:

## 本实例步骤描述
训练Fourier Neural Operator完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Fourier Neural Operator，和{TRAIN_CONFIG}训练“FNO规则网格参数化PDE算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Fourier Neural Operator
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
