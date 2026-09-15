# 实例任务：闭合项预测与后验CFD耦合 @ CFD_S079

- domain: cfd
- 骨架: tk-cfd-2c407cc9
- 场景: sc-0c3968af (CFD_S079)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S079
- 关联论文: A physics-aware, probabilistic machine learning framework for coarse-graining high-dimensional systems in the Sm | doi:; Neural Ideal Large Eddy Simulation_ Modeling Turbulence with Neural Stochastic Differential Equations | doi:; Learning Stochastic Multiscale Models | doi:; Echo state network for two-dimensional turbulent moist Rayleigh-Bénard convection | doi:; Machine-learning energy-preserving nonlocal closures for turbulent fluid flows and inertial tracers | doi:

## 本实例步骤描述
先验评估闭合项，再嵌入RANS或LES执行稳定后验推进。

## 本实例执行 prompt
加载{CHECKPOINT}预测应力、通量或源项，先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- apriori_closure/
- aposteriori_fields/
- solver_stability.csv

## 本实例质量门禁
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

## 可调资源（edge:resource，仅真实存在）
- tools/fluidsim

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
