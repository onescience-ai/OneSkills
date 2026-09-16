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
- cfd-batch-inference-physics-3d-turbulence-transformer-inst
- cfd-batch-inference-physics-aeroelasticity-unsteady-inst
- cfd-batch-inference-physics-autoencoder-latent-space-inst
- cfd-batch-inference-physics-autoregressive-network-inst
- cfd-batch-inference-physics-boundary-embedding-and-inst
- cfd-batch-inference-physics-conservative-graph-network-inst
- cfd-batch-inference-physics-continuous-time-and-stochast-inst
- cfd-batch-inference-physics-convective-scalar-mixed-inst
- cfd-batch-inference-physics-deeponet-neural-green-inst
- cfd-batch-inference-physics-differentiable-pde-solver-inst
- cfd-batch-inference-physics-diffusion-stochastic-process-inst
- cfd-batch-inference-physics-domain-decomposition-and-inst
- cfd-batch-inference-physics-drivaernet-vehicle-geometry-inst
- cfd-batch-inference-physics-dynamic-graph-network-and-inst
- cfd-batch-inference-physics-e3-equivariant-particle-inst
- cfd-batch-inference-physics-equivariant-spherical-and-inst
- cfd-batch-inference-physics-factorization-multigrid-fno-inst
- cfd-batch-inference-physics-fluid-solid-coupling-moving-inst
- cfd-batch-inference-physics-fno-regular-grid-parameteriz-inst
- cfd-batch-inference-physics-foundation-model-cross-pde-inst
- cfd-batch-inference-physics-geometric-encoding-network-inst
- cfd-batch-inference-physics-graph-network-airfoil-inst
- cfd-batch-inference-physics-graph-neural-operator-inst
- cfd-batch-inference-physics-graph-neural-operator-inst-2
- cfd-batch-inference-physics-high-fidelity-vehicle-inst
- cfd-batch-inference-physics-implicit-neural-field-inst
- cfd-batch-inference-physics-kernel-method-generative-inst
- cfd-batch-inference-physics-lagrangian-deep-network-inst
- cfd-batch-inference-physics-large-scale-mesh-transformer-inst
- cfd-batch-inference-physics-latent-space-neural-field-inst
- cfd-batch-inference-physics-latent-space-neural-ode-inst
- cfd-batch-inference-physics-lie-group-equivariant-inst
- cfd-batch-inference-physics-mamba-state-space-neural-inst
- cfd-batch-inference-physics-multi-scale-transformer-inst
- cfd-batch-inference-physics-non-cartesian-lattice-and-inst
- cfd-batch-inference-physics-physical-boundary-invariant-inst
- cfd-batch-inference-physics-physical-network-compressibl-inst
- cfd-batch-inference-physics-pod-modal-decomposition-inst
- cfd-batch-inference-physics-point-cloud-meshless-network-inst
- cfd-batch-inference-physics-regular-grid-cnn-airfoil-inst
- cfd-batch-inference-physics-scientific-foundation-model-inst
- cfd-batch-inference-physics-stability-constrained-inst
- cfd-batch-inference-physics-time-parallel-multitemporal-inst
- cfd-batch-inference-physics-transfer-and-uncertainty-inst
- cfd-batch-inference-physics-transferable-parameterized-inst
- cfd-batch-inference-physics-transformer-general-pde-inst
- cfd-batch-inference-physics-transonic-aeroelasticity-inst
- cfd-batch-inference-physics-wall-pressure-shear-and-inst
- cfd-batch-inference-physics-wavelet-local-spectral-inst

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
