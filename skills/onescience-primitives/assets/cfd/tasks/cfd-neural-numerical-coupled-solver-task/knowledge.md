# 骨架任务：神经数值耦合求解

- domain: cfd
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 将网络嵌入数值求解器并执行完整收敛流程。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，按数据契约把神经校正、网格移动、预条件或代理模块嵌入原数值求解器。执行端到端迭代，保存每步残差、守恒量、收敛状态和耗时；发散时停止并输出最后稳定状态。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- coupled_solution/
- residual_history.csv
- solver_timing.json

## 质量门禁 quality_gate
- 残差达到数值收敛门限
- 相对原求解器误差和加速比均报告
- 耦合接口变量单位一致

## 可调资源（edge:resource，仅真实存在）
- tools/fluidsim

## 实例任务（本骨架在各场景的实例化）
- cfd-neural-numerical-coupled-differentiable-physics-inst
- cfd-neural-numerical-coupled-learned-mesh-movement-inst
- cfd-neural-numerical-coupled-llm-agent-auto-config-cfd-inst
- cfd-neural-numerical-coupled-neural-corrector-coarse-inst
- cfd-neural-numerical-coupled-neural-finite-volume-domain-inst
- cfd-neural-numerical-coupled-neural-multigrid-preconditio-inst

## 复用场景
- CFD_S067
- CFD_S068
- CFD_S069
- CFD_S070
- CFD_S071
- CFD_S072
