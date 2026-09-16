# 实例任务：模型配置与训练 @ CFD_S037

- domain: cfd
- 骨架: cfd-model-configuration-training-task
- 场景: cfd-pinn-turbulence-rans-mean-flow-closure-scenario (CFD_S037)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- CFD_S037
- 关联论文: Generalizable turbulence closures across bluff-body shapes by PINN-based solver-agnostic training | doi:; Physics-informed neural networks for solving Reynolds-averaged Navier–Stokes equations | doi:; Physics-informed data based neural networks for two-dimensional turbulence | doi:; Evolution of inertial particle clustering in decaying turbulence | doi:

## 本实例步骤描述
训练Turbulence-augmented PINN完成指定输入到目标物理量的映射。

## 本实例执行 prompt
使用{MODEL_NAME}，默认Turbulence-augmented PINN，和{TRAIN_CONFIG}训练“PINN湍流RANS均值流求解与闭合”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

## 本实例输入槽
- {MODEL_NAME} | required=True | type=str | var_name=模型名称 | hint=实现或模型注册名 | default=Turbulence-augmented PINN
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
