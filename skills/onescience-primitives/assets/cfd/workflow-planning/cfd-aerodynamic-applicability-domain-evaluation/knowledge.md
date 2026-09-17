# 气动逆向设计任务验收与适用域判定

## 适用范围

**触发条件**：
- 已完成条件采样与物理筛选（s04），需要对生成模型进行最终验收评估
- 需要评估统计误差、物理约束满足度、泛化能力和计算收益
- 需要判定适用域并给出PASS/REJECT/BLOCKED结论

**适用场景**：
- 气动逆向设计生成模型的最终验收
- 需要明确适用域限制和CFD复核建议的场景
- 需要可追溯的最差样本分析

**不适用场景**：
- 中间训练阶段的快速验证（使用训练指标即可）
- 无物理约束要求的纯数据驱动评估
- 域外工况未经CFD复核直接工程应用

## 输入

- 生成样本与物理筛选结果（s04输出的 generated_samples/、physics_filter.json）
- 验收指标列表（{METRICS}：默认distribution_distance, diversity, physics_residual, coverage）
- 相对误差门限（{MAX_RELATIVE_L2}：默认0.1）
- 是否外推测试（{RUN_OOD_TEST}：默认true）

## 输出

- evaluation.json：综合评估结果（逐变量误差、边界误差、守恒残差、推理成本）
- worst_cases.csv：最差样本清单（可追溯）
- applicability_report.md：适用域报告（含复核建议）
- PASS_REJECT_BLOCKED.txt：最终判定

## 流程节点

### Step 1：统计误差评估
- **操作**：计算逐变量相对L2误差、分布距离（如Wasserstein距离）
- **参数**：MAX_RELATIVE_L2=0.1
- **质量门禁**：误差值为有限值；最差样本可追溯

### Step 2：物理约束评估
- **操作**：评估边界误差、守恒残差、方程残差
- **质量门禁**：物理指标与统计指标同时报告

### Step 3：多样性与覆盖率评估
- **操作**：评估生成样本的多样性和分布覆盖
- **质量门禁**：多样性指标合理；覆盖率满足要求

### Step 4：最差样本分析
- **操作**：识别并分析最差样本，记录失败模式
- **质量门禁**：最差样本可追溯；失败模式可解释

### Step 5：外推测试（OOD）
- **操作**：对几何或工况域外样本进行测试，明确适用域边界
- **参数**：RUN_OOD_TEST=true
- **质量门禁**：适用域限制明确；域外工况标注需CFD复核

### Step 6：综合判定
- **操作**：根据所有指标给出PASS/REJECT/BLOCKED判定
- **判定标准**：
  - PASS：所有指标满足门限，适用域明确
  - REJECT：关键指标不满足门限
  - BLOCKED：数据或模型问题导致无法评估
- **质量门禁**：结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | distribution_distance, diversity, physics_residual, coverage | [1] | 四维度 |
| 误差门限 | MAX_RELATIVE_L2 ≤ 0.1 | [1] | 相对L2 |
| OOD测试 | true | [1] | 默认开启 |
| 判定标准 | PASS/REJECT/BLOCKED | [1] | 三态 |
| 最差样本 | 必须报告 | [1] | 可追溯 |
| 适用域 | 必须报告 | [1] | 含复核建议 |

## 边界与分流

- **判定为BLOCKED**：停止自动流程，转人工CFD复核；列出所有阻塞原因
- **判定为REJECT**：分析失败原因，回退到s03调整模型或s02调整数据
- **判定为PASS但适用域窄**：明确标注适用范围，域外工况必须经CFD复核
- **外推测试失败**：缩小适用域，增加域内验证强度
- **平均误差满足但最差样本不满足**：不得仅凭平均误差宣称工程可用

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议
- 不得仅凭平均误差宣称工程可用
- PASS/REJECT/BLOCKED 判定明确

## 回退策略

- REJECT：回退到训练阶段（s03）调整超参数或模型架构
- BLOCKED：回退到数据阶段（s01/s02）排查数据质量问题
- 适用域过窄：补充数据或缩小应用范围
- 计算成本过高：评估是否可接受，必要时使用简化模型

## 资源召回建议

- 当需要对气动逆向设计生成模型进行最终验收时召回
- 配套资源：cfd-aerodynamic-physics-consistent-sampling（上游）、cfd-aerodynamic-joint-inverse-design（场景级）
- 若仅需中间评估：使用训练指标（training_metrics.csv）
- 若需域外复核：使用CFD软件进行高保真验证

## 证据来源

[1] 场景需求书 CFD_S094：生成模型气动外形与流场联合逆向设计，scenario_catalogs/fluid/CFD_S094_生成模型气动外形与流场联合逆向设计.json
[2] "Aerodynamic Shape Design Space Exploration with Deep Latent Diffusion Model", arXiv:2609.00812
[3] "Diffusion Model Driven Airfoil Design_ From Geometry Encoding to Practical Applications", arXiv:2601.16228
