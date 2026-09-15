# 实例任务：模型配置与训练 @ CFD_S092

- domain: cfd
- 骨架: tk-cfd-18078463
- 场景: sc-66583cbe (CFD_S092)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S092
- 关联论文: Switched Flow Matching_ Eliminating Singularities via Switching ODEs | doi:; Physics vs Distributions_ Pareto Optimal Flow Matching with Physics Constraints | doi:; Dflow-SUR_ Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching | doi:; GeoFunFlow-3D_ A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries | doi:; Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders_ A Pipeline-Level Study of Flow Matching and Diffusion | doi:

## 本实例步骤描述
训练Flow matching model完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Flow matching model，和{TRAIN_CONFIG}训练“流匹配网络复杂流动概率代理”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Flow matching model
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
