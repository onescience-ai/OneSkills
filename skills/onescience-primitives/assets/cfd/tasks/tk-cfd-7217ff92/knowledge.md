# 骨架任务：批量推理与物理恢复

- domain: cfd
- 复用场景数: 49
- 实例任务数: 49

## 步骤描述（跨场景聚合去重）
- 在独立测试集推理，恢复原始单位、网格和物理派生量。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}及训练时数据契约，在s02独立测试集上以{DEVICE}和{BATCH_SIZE}推理。反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量，保存逐样本结果和耗时，禁止用测试标签修正预测。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- inference_manifest.json
- predictions/
- timing.csv

## 质量门禁 quality_gate
- 推理未使用测试目标校正
- 每个测试样本有唯一结果
- 预测无NaN或Inf且形状单位正确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-077d4e95
- it-0a68c40e
- it-11c1812d
- it-13594568
- it-157db995
- it-19a464d7
- it-1a8215c0
- it-1b297191
- it-1bcd1947
- it-243014c7
- it-26b8dafe
- it-3c9721aa
- it-3d5b06f0
- it-42ff8895
- it-4877c91d
- it-493d8fbd
- it-4be9baa5
- it-57671ca1
- it-5c978a0b
- it-5e3f17f1
- it-628cf8a4
- it-6c96a2d9
- it-7479962a
- it-78665579
- it-7a5aea44
- it-7be6a79a
- it-816ce07b
- it-856278a0
- it-888747f2
- it-88f3066b
- it-89c49673
- it-9dfe0b08
- it-ad1faadb
- it-b00b0b5b
- it-b5ae7bae
- it-b9692541
- it-bb4a068b
- it-c19f1bad
- it-c347b827
- it-c6fa2814
- it-c88a5c97
- it-cad478ee
- it-cd678548
- it-d561d985
- it-da366986
- it-e9ee0016
- it-ef8c4971
- it-effe0f70
- it-fa840f8a

## 复用场景
- CFD_S001
- CFD_S002
- CFD_S003
- CFD_S004
- CFD_S005
- CFD_S006
- CFD_S007
- CFD_S008
- CFD_S009
- CFD_S010
- CFD_S011
- CFD_S012
- CFD_S013
- CFD_S014
- CFD_S018
- CFD_S019
- CFD_S020
- CFD_S021
- CFD_S022
- CFD_S023
- CFD_S024
- CFD_S025
- CFD_S026
- CFD_S027
- CFD_S028
- CFD_S048
- CFD_S049
- CFD_S050
- CFD_S051
- CFD_S052
- CFD_S053
- CFD_S054
- CFD_S055
- CFD_S056
- CFD_S057
- CFD_S058
- CFD_S059
- CFD_S060
- CFD_S061
- CFD_S062
- CFD_S063
- CFD_S064
- CFD_S065
- CFD_S066
- CFD_S086
- CFD_S087
- CFD_S088
- CFD_S089
- CFD_S090
