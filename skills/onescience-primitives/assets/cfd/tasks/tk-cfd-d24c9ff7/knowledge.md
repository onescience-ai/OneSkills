# 骨架任务：概率推理与不确定性校准

- domain: cfd
- 复用场景数: 3
- 实例任务数: 3

## 步骤描述（跨场景聚合去重）
- 输出预测分布、置信区间和分布外不确定性并执行校准。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，对独立测试集及外推集执行概率推理。保存预测均值、方差或样本集合，区分认知与随机不确定性；不得用测试标签回调模型。报告覆盖率、区间宽度、NLL和校准误差。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- calibration.csv
- predictive_distribution/
- uncertainty_decomposition.json

## 质量门禁 quality_gate
- 区间覆盖率与宽度同时报告
- 概率输出有限且定义清楚
- 测试集未参与校准训练

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-6417a2e6
- it-ba2e0e3c
- it-bf1dc304

## 复用场景
- CFD_S015
- CFD_S016
- CFD_S017
