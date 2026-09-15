# 实例任务：神经数值耦合求解 @ CFD_S071

- domain: cfd
- 骨架: tk-cfd-9be5f617
- 场景: sc-a65ec683 (CFD_S071)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S071
- 关联论文: Mechanistic PDE Networks for Discovery of Governing Equations | doi:; Hamiltonian Neural PDE Solvers through Functional Approximation | doi:; PhysPDE_ Rethinking PDE Discovery and a Physical HYpothesis Selection Benchmark | doi:; Neural Stochastic Flows_ Solver-Free Modelling and Inference for SDE Solutions | doi:; Accelerating PDE Data Generation via Differential Operator Action in Solution Space | doi:; Stochastic Taylor Derivative Estimator_ Efficient Amortization for Arbitrary Differential Operators | doi:; ΦFlow_ Differentiable Simulations for PyTorch, TensorFlow and Jax | doi:

## 本实例步骤描述
将网络嵌入数值求解器并执行完整收敛流程。

## 本实例执行 prompt
加载{CHECKPOINT}，按数据契约把神经校正、网格移动、预条件或代理模块嵌入原数值求解器。执行端到端迭代，保存每步残差、守恒量、收敛状态和耗时；发散时停止并输出最后稳定状态。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- coupled_solution/
- residual_history.csv
- solver_timing.json

## 本实例质量门禁
- 耦合接口变量单位一致
- 残差达到数值收敛门限
- 相对原求解器误差和加速比均报告

## 可调资源（edge:resource，仅真实存在）
- tools/fluidsim

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
