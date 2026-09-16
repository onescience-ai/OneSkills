# 实例任务：模型配置与训练 @ CFD_S073

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-data-driven-rans-reynolds-stress-eddy-viscosity-closure-scenario (CFD_S073)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S073
- 关联论文: Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks | doi:; Machine learning for RANS turbulence modeling of variable property flows | doi:; Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows | doi:; Data-driven nonlinear turbulent flow scaling with Buckingham Pi variables | doi:; Turbulence model augmented physics-informed neural networks for mean-flow reconstruction | doi:; Predictions of turbulent shear flows using deep neural networks | doi:; Machine-Learning-Augmented Predictive Modeling of Turbulent Separated Flows over Airfoils | doi:; Physics-informed machine learning approach for augmenting turbulence models_ A comprehensive framework | doi:; RANS turbulence model development using CFD-driven machine learning | doi:; From Bypass Transition to Flow Control and Data-Driven Turbulence Modeling_ An Input–Output Viewpoint | doi:; Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence | doi:; Discovering explicit Reynolds-averaged turbulence closures for turbulent separated flows through deep learni | doi:; FoilDiff_ A Hybrid Transformer Backbone for Diffusion-based Modelling of 2D Airfoil Flow Fields | doi:; A Symplectic Theory of Turbulence Closure_ Hidden Reservoir Dynamics, Endogenous Stochastic Transport, and Kraichnan Dual Cascades | doi:; A high-fidelity numerical database for free-stream transition | doi:; Learning Turbulence Closures with Physics-Informed Neural Networks for the Rayleigh-Taylor Transition to Turbulence | doi:; Towards bridging the gap between data-driven and theoretical turbulence closures in stratified flows | doi:; VATO_ A Vortex-Force-Aware Transformer Operator for Unsteady Separated Aerofoil Flows | doi:

## 本实例步骤描述
训练Tensor-basis neural network、Symbolic closure model完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Tensor-basis neural network、Symbolic closure model，和{TRAIN_CONFIG}训练“数据驱动RANS雷诺应力与涡黏闭合”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Tensor-basis neural network、Symbolic closure model
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
