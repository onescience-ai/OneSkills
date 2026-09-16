# 实例任务：任务验收与适用域判定 @ CFD_S089

- domain: cfd
- 骨架: cfd-task-acceptance-domain-determination-task
- 场景: cfd-aeroelasticity-unsteady-load-reduced-order-response-prediction-scenario (CFD_S089)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CFD_S089
- 关联论文: Modeling Unsteady Aircraft Aerodynamics Using Lorenz Attractor_ A Reduced-Order Approach for Wing Rock | doi:; Deep Learning-Based Reduced Order Model for Three-Dimensional Unsteady Flow Using Mesh Transformation and Stitching | doi:; Stable Port-Hamiltonian Neural Networks | doi:; Convolutional neural network and long short-term memory based reduced order surrogate for minimal turbulent chan | doi:; A deep learning enabler for nonintrusive reduced order modeling of fluid flows | doi:; Validation and parameterization of a novel physics-constrained neural dynamics model applied to turbulent fl | doi:; Amortized Inference for Model Rocket Aerodynamics _ Learning to Estimate Physical Parameters from Simulation | doi:; A Residual Learning Approach for Unsteady Aerodynamic Load Prediction | doi:; Kolmogorov Arnold networks (KAN) for aerodynamic prediction_ a comparison with MLPs and GNNs | doi:; Neural-Network and Reduced-order Modeling Workflows for AI-Driven CFD_ Fast Response Surfaces, Reduced Dynamics and Jet in Cross-flow Examples | doi:; Nonlinear Model Order Reduction for Coupled Aeroelastic-Flight Dynamic Systems | doi:

## 本实例步骤描述
评估统计误差、关键物理约束、泛化能力和计算收益。

## 本实例执行 prompt
按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。

## 本实例输入槽
- {METRICS} | required=True | type=list[str] | var_name=验收指标 | hint=统计和物理指标 | default=['relative_L2', 'RMSE', 'conservation_residual', 'boundary_error']
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
