# 实例任务：任务验收与适用域判定 @ CFD_S059

- domain: cfd
- 骨架: tk-cfd-3fb1a5d6
- 场景: sc-13bf824c (CFD_S059)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CFD_S059
- 关联论文: Guiding Continuous Operator Learning through Physics-Based Boundary Constraints | doi:; Holistic Physics Solver_ Learning PDEs in a Unified Spectral-Physical Space | doi:; Learn Singularly Perturbed Solutions via Homotopy Dynamics | doi:; A Physics-preserved Transfer Learning Method for Differential Equations | doi:; Nonlocal Attention Operator_ Materializing Hidden Knowledge Towards Interpretable Physics Discovery | doi:; PAPM_ A Physics-aware Proxy Model for Process Systems | doi:; Training neural operators to preserve invariant measures of chaotic attractors | doi:; Generic bounds on the approximation error for physics-informed (and) operator learning | doi:; Buckingham $_pi$-Invariant Test‐Time Projection for Robust PDE Surrogate Modeling | doi:; Towards Generalizable PDE Dynamics Forecasting via Physics-Guided Invariant Learning | doi:; WAN3DNS_ Weak Adversarial Networks for Solving 3D Incompressible Navier-Stokes Equations | doi:; Wrong-Physics Backdoors in Neural PDE Operators | doi:

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
