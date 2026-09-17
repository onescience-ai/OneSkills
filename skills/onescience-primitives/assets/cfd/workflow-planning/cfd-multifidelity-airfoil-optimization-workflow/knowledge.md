# 多保真代理辅助翼型外形优化工作流

## 适用范围

**触发条件**：
- 已有多工况翼型几何与气动力数据，需要完成参数化外形优化
- 需要从数据接入到模型验收的完整端到端工作流
- 需要可复现的优化流程与物理一致性评估

**适用场景**：
- 翼型气动外形优化（升阻比最大化、力矩约束等）
- 多工况/多设计点联合优化
- 代理模型辅助的约束优化与Pareto前沿搜索
- 需要物理一致性评估与适用域报告的工程设计

**不适用场景**：
- 单一工况、单一目标的简单优化（无需多保真代理）
- 无物理约束的数据驱动优化
- 需要实时响应的在线优化（代理训练成本高）

## 输入

**必需输入**：
- 多工况翼型几何参数化数据（如CST参数、FFD控制点等）
- 对应工况的气动力数据（升力系数、阻力系数、力矩系数等）
- 设计空间边界与几何约束定义

**可选输入**：
- 高保真CFD计算结果（用于代理模型校准）
- 低保真快速评估数据（用于多保真建模）
- 物理约束方程或经验公式

**预处理要求**：
- 几何参数统一（无量纲化或归一化）
- 工况条件标准化（马赫数、雷诺数、攻角范围）
- 数据质量检查（缺失值、异常值、物理合理性）

## 输出

**核心产物**：
- 优化后的设计候选集（Pareto前沿解）
- 多保真代理模型权重与训练配置
- 优化历史记录（每次评估的可行性、目标值）
- 适用域报告与域外工况识别

**验证标准**：
- 代理模型预测误差在可接受范围内（逐变量误差、最差样本可追溯）
- 优化候选满足几何与物理硬约束
- 物理一致性评估通过（守恒律、方程残差等）

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入多工况翼型几何与气动力数据，核验样本、变量、单位、网格坐标及许可
- **参数**：数据集路径、数据集名称、数据契约（变量单位网格定义）
- **工具**：数据加载库、契约验证脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **产出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：切分配置（train/val/test比例、种子、分组依据）、目标变量、是否无量纲化
- **工具**：数据预处理库、归一化工具
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **产出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### Step 3：模型配置与训练
- **操作**：训练Multi-fidelity surrogate、Bayesian optimizer完成指定输入到目标物理量的映射
- **参数**：模型名称、训练配置（框架、epochs、batch_size、学习率、种子、早停）
- **工具**：PyTorch、多保真建模框架、贝叶斯优化库
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **产出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：候选生成与约束优化
- **操作**：围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹
- **参数**：模型权重、计算设备、推理批大小
- **工具**：优化器、Pareto前沿提取工具
- **质量门禁**：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签
- **产出**：design_candidates/、optimization_history.csv、pareto_front.json

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **参数**：验收指标、相对误差门限、是否外推测试
- **工具**：评估脚本、适用域分析工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **产出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据切分策略 | 按几何/轨迹/工况分组 | [场景JSON] | 避免数据泄漏，保证切分互斥 |
| 早停机制 | patience=15 | [场景JSON] | 防止过拟合，保存最佳权重 |
| 验收指标 | objective_improvement, constraint_violation, CFD_validation_error | [场景JSON] | 统计误差与物理一致性同时评估 |
| 适用域判定 | PASS/REJECT/BLOCKED | [场景JSON] | 含域外工况CFD复核建议 |

### 校准数值（体系专属值，供量级校准）

以下数值来自多工况翼型几何与气动力数据体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认epochs | 100 | [场景JSON] | 训练轮数 |
| 默认batch_size | 8 | [场景JSON] | 批量大小 |
| 默认学习率 | 0.001 | [场景JSON] | 优化器学习率 |
| 相对误差门限 | 0.1 | [场景JSON] | 测试集放行阈值 |
| 默认train比例 | 0.7 | [场景JSON] | 训练集占比 |
| 默认val比例 | 0.15 | [场景JSON] | 验证集占比 |
| 默认test比例 | 0.15 | [场景JSON] | 测试集占比 |

## 边界与分流

**数据不足时的改道**：
- 低保真数据充足但高保真数据极少 → 考虑迁移学习或多保真元建模方法族
- 高保真数据充足但无低保真数据 → 回退到单保真代理优化方法族

**优化目标不可行时的改道**：
- 约束过于严格导致可行域为空 → 放宽约束或引入松弛变量
- Pareto前沿退化为单点 → 简化为单目标优化问题

**代理模型精度不足时的改道**：
- 误差超过阈值且物理约束违反频繁 → 增加训练数据或调整模型结构
- 域外工况预测不稳定 → 标记为需CFD复核，不进入优化流程

## 质量检查

| 检查项 | 阈值/判据 | 失败处理 |
|--------|-----------|----------|
| 数据可读性 | 100%文件可读 | 返回BLOCKED，列出不可读文件 |
| 变量完整性 | 所有必需字段非空 | 返回BLOCKED，列出缺失字段 |
| 训练收敛 | 损失为有限值且下降 | 调整超参数重新训练 |
| 权重可加载 | checkpoint可重新加载 | 检查版本兼容性 |
| 约束满足 | 0个硬约束违反 | 过滤不可行候选 |
| 最差样本可追溯 | 逐样本误差可查 | 生成worst_cases.csv |
| 适用域报告 | 含域外工况识别 | 补充OOD测试 |

## 回退策略

- 代理模型训练失败 → 检查数据质量、调整超参数、尝试简化模型
- 优化搜索陷入局部最优 → 增加采样点、调整贝叶斯优化探索参数
- 适用域判定为REJECT → 标记需CFD复核的工况范围，不宣称工程可用

## 资源召回建议

**何时应召回本卡片**：
- 需要了解多保真代理辅助翼型优化的完整工作流程
- 需要按步骤执行翼型优化任务
- 需要了解每步的输入输出与质量门禁

**配套资源**：
- `cfd-multifidelity-surrogate-bayesian-airfoil-optimization`：场景级方法论卡片
- `cfd-multifidelity-airfoil-data-ingestion-contract`：数据接入与契约核验方法卡
- `cfd-multifidelity-airfoil-data-preprocessing-splitting`：预处理与数据切分方法卡
- `cfd-multifidelity-surrogate-bayesian-model-training`：模型训练方法卡
- `cfd-multifidelity-airfoil-candidate-constrained-optimization`：候选生成与约束优化方法卡
- `cfd-multifidelity-airfoil-acceptance-applicability-domain`：任务验收与适用域判定方法卡

## 证据来源

[1] "Optimization-Embedded Active Multi-Fidelity Surrogate Learning for Multi-Condition Airfoil Shape Optimization", arXiv:2603.17057, 2026
[2] "Surrogate-Based Aerodynamic Shape Optimization in Multiscale Flows via the Implicit Unified Gas-Kinetic Scheme", arXiv:2606.00645, 2025
[3] "ShapeBench: A Scalable Benchmark and Diagnostic Suite for Standardized Evaluation in Aerodynamic Shape Optimization", arXiv:2605.20763, 2025
