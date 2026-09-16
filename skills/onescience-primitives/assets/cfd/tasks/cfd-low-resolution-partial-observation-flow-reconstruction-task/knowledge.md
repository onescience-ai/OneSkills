# 骨架任务：低分辨或部分观测流场重构

- domain: cfd
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 从低分辨、稀疏或缺损输入恢复完整高分辨率流场。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，对测试集构造与真实采集一致的低分辨、稀疏或缺损输入并执行重构。恢复物理单位和边界，保存逐样本重构、误差场、频谱与统计剖面；禁止通过测试真值调节掩膜或超参数。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- error_fields/
- reconstructed_fields/
- spectral_statistics.json

## 质量门禁 quality_gate
- 小尺度频谱与统计量得到验证
- 观测掩膜与训练测试协议一致
- 边界守恒误差不因超分辨恶化

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- cfd-low-resolution-partial-cyclegan-unpaired-les-to-inst
- cfd-low-resolution-partial-implicit-representation-and-inst
- cfd-low-resolution-partial-partial-observation-diffusio-inst
- cfd-low-resolution-partial-sparse-wall-sensor-3d-inst
- cfd-low-resolution-partial-supervised-learning-turbulen-inst

## 复用场景
- CFD_S096
- CFD_S097
- CFD_S098
- CFD_S099
- CFD_S100
