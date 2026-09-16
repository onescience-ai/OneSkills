# 实例任务：任务验收与适用域判定 @ CFD_S038

- domain: cfd
- 骨架: cfd-task-acceptance-domain-determination-task
- 场景: cfd-physics-informed-network-sparse-observation-parameter-inversion-scenario (CFD_S038)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CFD_S038
- 关联论文: Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral n | doi:; CoPINN_ Cognitive Physics-Informed Neural Networks | doi:; Parameterized Physics-Informed Neural Networks for Parameterized PDEs | doi:; RoPINN_ Region Optimized Physics-Informed Neural Networks | doi:; Multi-output physics-informed neural networks for forward and inverse PDE problems with uncertainties | doi:; Physics-informed learning of governing equations from scarce data | doi:; Surrogate modeling for fluid flows based on physics-constrained deep learning without simulation data | doi:; Physics informed deep learning (Part I)_ Data-driven solutions of nonlinear partial differential equations | doi:; Causal-PIK_ Causality-based Physical Reasoning with a Physics-Informed Kernel | doi:; DiffWind_ Physics-Informed Differentiable Modeling of Wind-Driven Object Dynamics | doi:; Physics-informed learning under mixing_ How physical knowledge speeds up learning | doi:

## 本实例步骤描述
评估统计误差、关键物理约束、泛化能力和计算收益。

## 本实例执行 prompt
按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。

## 本实例输入槽
- {METRICS} | required=True | type=list[str] | var_name=验收指标 | hint=统计和物理指标 | default=['relative_L2', 'PDE_residual', 'boundary_error', 'conservation_error']
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
