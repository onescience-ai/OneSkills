# 实例任务：任务验收与适用域判定 @ CFD_S061

- domain: cfd
- 骨架: tk-cfd-3fb1a5d6
- 场景: sc-f3b2361b (CFD_S061)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CFD_S061
- 关联论文: Riemann Tensor Neural Networks_ Learning Conservative Systems with Physics-Constrained Networks | doi:; Graph Neural PDE Solvers with Conservation and Similarity-Equivariance | doi:; Keep the Momentum_ Conservation Laws beyond Euclidean Gradient Flows | doi:; Neural Conservation Laws_ A Divergence-Free Perspective | doi:; PDE-GCN_ Novel Architectures for Graph Neural Networks Motivated by Partial Differential Equations | doi:; Guaranteed Conservation of Momentum for Learning Particle-based Fluid Dynamics | doi:; Hyperbolic-PDE GNN_ Spectral Graph Neural Networks in the Perspective of A System of Hyperbolic Partial Diff | doi:

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
