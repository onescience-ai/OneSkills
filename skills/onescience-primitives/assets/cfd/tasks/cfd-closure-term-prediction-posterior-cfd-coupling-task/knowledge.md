# 骨架任务：闭合项预测与后验CFD耦合

- domain: cfd
- 复用场景数: 8
- 实例任务数: 8

## 步骤描述（跨场景聚合去重）
- 先验评估闭合项，再嵌入RANS或LES执行稳定后验推进。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}预测应力、通量或源项，先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- aposteriori_fields/
- apriori_closure/
- solver_stability.csv

## 质量门禁 quality_gate
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证
- 闭合张量或通量满足约束

## 可调资源（edge:resource，仅真实存在）
- tools/fluidsim

## 实例任务（本骨架在各场景的实例化）
- cfd-closure-term-prediction-convolution-network-2d-inst
- cfd-closure-term-prediction-data-driven-porous-complex-inst
- cfd-closure-term-prediction-data-driven-rans-reynolds-inst
- cfd-closure-term-prediction-engineering-les-equivalent-inst
- cfd-closure-term-prediction-hypersonic-transonic-boundar-inst
- cfd-closure-term-prediction-pinn-joint-inversion-closure-inst
- cfd-closure-term-prediction-stochastic-differential-and-inst
- cfd-closure-term-prediction-transfer-and-multi-fidelity-inst

## 复用场景
- CFD_S073
- CFD_S074
- CFD_S075
- CFD_S076
- CFD_S077
- CFD_S078
- CFD_S079
- CFD_S080
