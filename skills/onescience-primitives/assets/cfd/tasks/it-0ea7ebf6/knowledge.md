# 实例任务：任务验收与适用域判定 @ CFD_S095

- domain: cfd
- 骨架: tk-cfd-3fb1a5d6
- 场景: sc-d9464c5e (CFD_S095)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CFD_S095
- 关联论文: M2PDE_ Compositional Generative Multiphysics and Multi-component PDE Simulation | doi:; Arbitrarily-Conditioned Multi-Functional Diffusion for Multi-Physics Emulation | doi:; Deep Sturm–Liouville_ From Sample-Based to 1D Regularization with Learnable Orthogonal Basis Functions | doi:; SING_ SDE Inference via Natural Gradients | doi:; SEA_ State-Exchange Attention for High-Fidelity Physics Based Transformers | doi:; Unifying Predictions of Deterministic and Stochastic Physics in Mesh-Reduced Space with Sequential Flow Generative Model | doi:; Neural Ordinary Differential Equations | doi:; NeuroFluid_ Fluid Dynamics Grounding with Particle-Driven Neural Radiance Fields | doi:

## 本实例步骤描述
评估统计误差、关键物理约束、泛化能力和计算收益。

## 本实例执行 prompt
按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。

## 本实例输入槽
- {METRICS} | required=True | type=list[str] | var_name=验收指标 | hint=统计和物理指标 | default=['distribution_distance', 'diversity', 'physics_residual', 'coverage']
- {MAX_RELATIVE_L2} | required=False | type=float | var_name=相对误差门限 | hint=测试集放行阈值 | default=0.1
- {RUN_OOD_TEST} | required=False | type=bool | var_name=是否外推测试 | hint=测试域外工况 | default=True

## 本实例产出
- evaluation.json
- worst_cases.csv
- applicability_report.md
- PASS_REJECT_BLOCKED.txt

## 本实例质量门禁
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
