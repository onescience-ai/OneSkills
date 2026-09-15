# 实例任务：模型配置与训练 @ CFD_S087

- domain: cfd
- 骨架: tk-cfd-18078463
- 场景: sc-46ac5b2d (CFD_S087)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S087
- 关联论文: Reduced-Order Modeling of Advection-Dominated Systems with Recurrent Neural Networks and Convolutional Autoencoders | doi:; β-Variational autoencoders and transformers for reduced-order modeling of fluid flows | doi:; GyroSwin_ 5D Surrogates for Gyrokinetic Plasma Turbulence Simulations | doi:; SINGER_ Stochastic Network Graph Evolving Operator for High Dimensional PDEs | doi:; Observable-augmented manifold learning for multi-source turbulent flow data | doi:; Slim multi-scale convolutional autoencoder-based reduced-order models for interpretable features of a complex dy | doi:; Evolve Smoothly, Fit Consistently_ Learning Smooth Latent Dynamics For Advection-Dominated Systems | doi:; Neural Lad_ A Neural Latent Dynamics Framework for Times Series Modeling | doi:; Cost function for low-dimensional manifold topology assessment | doi:; Time-series learning of latent-space dynamics for reduced-order model closure | doi:

## 本实例步骤描述
训练Convolutional autoencoder、Latent dynamics model完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Convolutional autoencoder、Latent dynamics model，和{TRAIN_CONFIG}训练“自编码器潜空间流动降阶时序预测”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Convolutional autoencoder、Latent dynamics model
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
