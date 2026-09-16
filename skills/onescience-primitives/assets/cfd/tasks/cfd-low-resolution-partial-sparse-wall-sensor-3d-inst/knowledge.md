# 实例任务：低分辨或部分观测流场重构 @ CFD_S096

- domain: cfd
- 骨架: cfd-low-resolution-partial-observation-flow-reconstruction-task
- 场景: cfd-sparse-wall-sensor-3d-turbulence-full-field-reconstruction-scenario (CFD_S096)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S096
- 关联论文: Sparse sensor reconstruction of vortex-impinged airfoil wake with machine learning | doi:; From coarse wall measurements to turbulent velocity fields with deep learning | doi:; Three-dimensional generative adversarial networks for turbulent flow estimation from wall measurements | doi:; Reconstruction of three-dimensional turbulent flow structures using surface measurements for free-surface flows | doi:

## 本实例步骤描述
从低分辨、稀疏或缺损输入恢复完整高分辨率流场。

## 本实例执行 prompt
加载{CHECKPOINT}，对测试集构造与真实采集一致的低分辨、稀疏或缺损输入并执行重构。恢复物理单位和边界，保存逐样本重构、误差场、频谱与统计剖面；禁止通过测试真值调节掩膜或超参数。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- reconstructed_fields/
- error_fields/
- spectral_statistics.json

## 本实例质量门禁
- 观测掩膜与训练测试协议一致
- 小尺度频谱与统计量得到验证
- 边界守恒误差不因超分辨恶化

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
