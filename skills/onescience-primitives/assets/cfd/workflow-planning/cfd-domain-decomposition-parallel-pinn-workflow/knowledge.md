# 区域分解并行PINN大域求解工作流

## 适用范围

**触发条件**：
- 用户提供分区PDE配点数据，需要完成区域分解PINN训练与评估
- 需要端到端执行从数据接入到适用域判定的完整工作流

**适用场景**：
- 大域PDE正/逆问题的区域分解PINN求解
- FBPINN、XPINN、Parallel PINN 三种方法的对比评估
- 需要完整可复现工作流的工程项目

**不适用场景**：
- 小域单PINN问题（无需区域分解）
- 纯数据驱动无PDE约束的问题
- 已有训练好的子域模型只需推理的场景

## 输入

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 数据集路径 | doc | 是 | 目录或清单文件 |
| 数据集名称 | str | 是 | 来源与数据版本 |
| 数据契约 | object | 否 | 变量单位网格定义 |
| 切分配置 | object | 是 | 按对象工况切分 |
| 目标变量 | list[str] | 是 | 待预测物理量 |
| 模型名称 | str | 是 | FBPINN/XPINN/Parallel PINN |
| 训练配置 | object | 是 | 超参数和随机种子 |
| 验收指标 | list[str] | 是 | 统计和物理指标 |

## 输出

| 输出 | 说明 |
|------|------|
| dataset_manifest.json | 数据清单 |
| data_contract.json | 数据契约 |
| train/validation/test_manifest.json | 切分清单 |
| normalization.json | 归一化统计量 |
| best_checkpoint.pt | 最佳权重 |
| training_metrics.csv | 训练指标 |
| solution_fields/ | 解场文件 |
| pde_residuals/ | PDE残差场 |
| boundary_residuals.csv | 边界残差 |
| evaluation.json | 评估结果 |
| worst_cases.csv | 最差样本 |
| applicability_report.md | 适用域报告 |
| PASS_REJECT_BLOCKED.txt | 结论 |

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取数据集，检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分；保存统计量与可逆变换
- **输入**：s01输出, {SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：加载s02切分与统计量，使用FBPINN/XPINN/Parallel PINN训练模型，记录逐轮指标
- **输入**：s02输出, {MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：方程求解与物理残差恢复
- **操作**：加载权重，在测试参数、边界和查询坐标上求解PDE，使用自动微分恢复导数、通量和方程残差
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：solution_fields/, pde_residuals/, boundary_residuals.csv
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照

### Step 5：任务验收与适用域判定
- **操作**：按指标评价s04结果，报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本；执行外推测试并明确适用域
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认模型 | FBPINN, XPINN, Parallel PINN | [场景需求书] | 三种区域分解PINN方法 |
| 训练轮次 | 100 | [场景需求书] | 可据收敛调整 |
| 批大小 | 8 | [场景需求书] | 按显存调整 |
| 学习率 | 0.001 | [1][场景需求书] | Adam优化器 |
| 早停耐心 | 15 | [场景需求书] | 防过拟合 |
| 相对L2门限 | 0.1 | [场景需求书] | 默认测试集放行阈值 |
| 默认设备 | cuda | [场景需求书] | 支持CPU回退 |

## 边界与分流

- **数据不可读或契约缺失**：返回BLOCKED并列出缺项，不得编造数据
- **切分泄漏**：若同一工况帧被打散到不同切分集，需重新按轨迹分组切分
- **训练不收敛**：检查PDE定义、降低学习率、增加子域重叠、尝试其他DD方法
- **验收未通过**：生成worst_cases.csv，分析最差样本位置与原因，调整子域划分或训练策略
- **域外工况**：明确标注为不适用，建议经CFD数值解复核

## 质量检查

- 每步输出文件完整性验证
- 训练指标连续性检查（无NaN/Inf）
- 解场物理量量纲一致性
- 残差场空间分布合理性
- 最差样本与平均误差差距 ≤ 5倍

## 回退策略

- FBPINN失败：尝试XPINN（界面弱约束可能更灵活）
- XPINN失败：尝试Parallel PINN（直接多GPU并行）
- 所有DD-PINN失败：回退标准PINN小域验证
- 训练时间过长：增加子域数或减小子域尺寸

## 资源召回建议

- 当用户需要端到端执行区域分解PINN工作流时召回本卡
- 配套资源：`cfd-domain-decomposition-parallel-pinn-solution`（场景方法论）、`cfd-overlapping-domain-decomposition-pinn`（子域划分技术细节）

## 证据来源

[1] B. Moseley et al., "Finite Basis Physics-Informed Neural Networks (FBPINNs): A Scalable Domain Decomposition Approach for Solving Differential Equations", Advances in Computational Mathematics, 2023, DOI: 10.1007/s10444-023-10065-9

[2] "Parallel Physics-Informed Neural Networks via Domain Decomposition", Journal of Computational Physics, 2022, DOI: 10.1016/j.jcp.2021.110683

[3] Z. Hu et al., "When Do Extended Physics-Informed Neural Networks (XPINNs) Improve Generalization", SIAM Journal on Scientific Computing, 2022, DOI: 10.1137/21M1447039
