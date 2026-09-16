# 实例任务：概率推理与不确定性校准 @ CFD_S017

- domain: cfd
- 骨架: cfd-probabilistic-reasoning-uncertainty-calibration-task
- 场景: cfd-out-of-distribution-flow-surrogate-detection-and-calibration-scenario (CFD_S017)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S017
- 关联论文: Prometheus_ Out-of-Distribution Fluid Dynamics Modeling with Disentangled Graph ODE | doi:; Using Uncertainty Quantification to Characterize and Improve Out-of-Domain Learning for PDEs | doi:; PURE_ Prompt Evolution with Graph ODE for Out-of-distribution Fluid Dynamics Modeling | doi:

## 本实例步骤描述
输出预测分布、置信区间和分布外不确定性并执行校准。

## 本实例执行 prompt
加载{CHECKPOINT}，对独立测试集及外推集执行概率推理。保存预测均值、方差或样本集合，区分认知与随机不确定性；不得用测试标签回调模型。报告覆盖率、区间宽度、NLL和校准误差。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- predictive_distribution/
- uncertainty_decomposition.json
- calibration.csv

## 本实例质量门禁
- 概率输出有限且定义清楚
- 测试集未参与校准训练
- 区间覆盖率与宽度同时报告

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
