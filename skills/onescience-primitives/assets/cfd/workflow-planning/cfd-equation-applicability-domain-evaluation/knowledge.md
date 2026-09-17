# Equation Applicability Domain Evaluation

## 适用范围
面向符号与稀疏PDE发现任务的验收与适用域判定步骤。评估统计误差、关键物理约束、泛化能力和计算收益，输出PASS/REJECT/BLOCKED判定，要求同时报告统计与物理指标、最差样本和推理成本，明确适用域限制。

## 输入
- **验收指标**（必填）：统计和物理指标列表。
- **相对误差门限**（可选）：测试集放行阈值。
- **是否外推测试**（可选）：是否测试域外工况。
- **解场与残差**（来自s04）：solution_fields/、pde_residuals/、boundary_residuals.csv。

## 输出
- **evaluation.json**：逐变量误差、边界误差、守恒误差、推理成本的结构化报告。
- **worst_cases.csv**：最差样本的详细信息，含坐标、误差值、工况。
- **applicability_report.md**：适用域说明、泛化能力评估、复核建议。
- **PASS_REJECT_BLOCKED.txt**：最终判定结果。

## 流程节点
```
1. 加载{METRICS}验收指标集
2. 评估s04解场的逐变量相对L2误差
3. 评估PDE残差
4. 评估边界误差
5. 评估守恒误差或方程残差
6. 识别最差样本
7. 计算推理成本
8. 按{MAX_RELATIVE_L2}及物理门限判定
9. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试
10. 输出PASS/REJECT/BLOCKED
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 统计与物理指标同时报告 | 必须 | [场景需求书] | 不得仅凭统计指标判定 |
| 最差样本可追溯 | 必须 | [场景需求书] | 含坐标、误差、工况 |
| 适用域限制与复核建议 | 必须包含 | [场景需求书] | 结论不得省略 |
| 外推测试 | 默认执行 | [场景需求书] | 几何或工况外推 |

### 校准数值
> 以下数值来自场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | [场景需求书] | — |
| 默认相对误差门限 | 0.1 | [场景需求书] | 可按任务调整 |
| 默认外推测试 | true | [场景需求书] | — |

## 边界与分流
- **平均误差达标但最差样本超标**：不得直接通过，需报告最差样本并评估工程影响。
- **统计指标达标但物理指标超标**：判定REJECT，物理约束优先。
- **REJECT判定**：回退至s03调整超参数或回退至s02增加数据覆盖。
- **BLOCKED判定**：检查数据或模型基础问题，不得强行通过。
- **域外工况**：必须明确标注适用域边界，域外工况须经CFD复核。

## 质量检查
1. 统计与物理指标同时报告。
2. 最差样本可追溯（含坐标、误差值、工况）。
3. 结论含适用域限制与复核建议。
4. evaluation.json可被标准JSON解析。
5. PASS/REJECT/BLOCKED判定明确。

## 回退策略
- REJECT：回退至s03调整超参数，或回退至s02增加数据覆盖范围。
- 连续REJECT：切换方法族（如从符号回归切换至稀疏正则化）或寻求人工干预。
- BLOCKED：检查数据质量和模型基础配置。

## 资源召回建议
- 当需要为符号/稀疏方程发现进行验收和适用域判定时召回。
- 配套卡片：cfd-pde-residual-recovery（残差恢复）、cfd-symbolic-sparse-governing-equation-discovery（场景级）。

## 证据来源
[1] 场景需求书 CFD_S045 s05定义
[2] Understanding Generalization in Physics Informed Models through Affine Variety Dimensions, 2025
[3] Learning fluid physics from highly turbulent data using sparse physics-informed discovery of empirical relations, 2024
[4] Competitive Physics Informed Networks, 2022
