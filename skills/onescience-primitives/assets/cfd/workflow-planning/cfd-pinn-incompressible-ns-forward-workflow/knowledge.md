# PINN 不可压缩 Navier-Stokes 正问题工作流

## 适用范围

本工作流覆盖从数据接入到适用域判定的完整 PINN 不可压缩 NS 正问题求解链路。每步有明确的输入契约、质量门禁和产出物，支持可复现、可回退的闭环执行。

**触发条件**：
- 用户提供不可压层流 NS 配置与配点数据
- 需要端到端完成 PINN 模型训练和解场恢复

**不适用场景**：
- 逆问题（参数辨识）——需额外的参数反演步骤
- 多物理场耦合（热-流、流-固）——需扩展损失项

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取数据集，核验文件可读性、样本数、输入与目标变量定义、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：
  - 数据文件可读且样本可追溯
  - 输入目标变量单位坐标定义完整
  - 不存在训练测试泄漏
- **工具**：文件解析器、契约验证脚本
- **关键检查**：若缺少必填输入返回 BLOCKED 并列出缺项，不得编造数据 [场景需求书 s01]

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分。完成质控、重采样或图构建、掩膜、归一化或无量纲化
- **输入**：{SPLIT_CONFIG}（默认 train=0.7, val=0.15, test=0.15, seed=42, group_by=geometry_or_trajectory）, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：
  - 三份切分的对象轨迹互斥
  - 仅用训练集计算变换统计量
  - 边界与掩膜语义未破坏
- **关键参数**：无量纲化推荐使用 Re 数作为特征量，统一跨工况量纲 [场景需求书 s02]

### Step 3：模型配置与训练
- **操作**：加载切分数据与统计量，配置 PINN/NSFnet 模型，执行两阶段训练（Adam 初训 + L-BFGS 精调）
- **输入**：{MODEL_NAME}（默认 PINN、NSFnet）, {TRAIN_CONFIG}（默认 epochs=100, batch_size=8, lr=0.001, seed=42, early_stopping_patience=15）, {INIT_CHECKPOINT}（可选）
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：
  - 训练验证损失均为有限值
  - 最佳权重可重新加载
  - 配置环境随机种子可复现
- **关键检查**：若提供初始权重须检查结构兼容性；缺少必填输入返回 BLOCKED [1][2][场景需求书 s03]

### Step 4：方程求解与物理残差恢复
- **操作**：加载最佳权重，在测试参数、边界和查询坐标上求解目标 PDE，使用自动微分恢复导数、通量和方程残差
- **输入**：{CHECKPOINT}（默认 best_checkpoint.pt）, {DEVICE}（默认 cuda）, {BATCH_SIZE}（默认 8）
- **输出**：solution_fields/, pde_residuals/, boundary_residuals.csv
- **质量门禁**：
  - 解场导数与残差均为有限值
  - 边初值逐项满足门限
  - 独立数值解或解析解可对照
- **关键约束**：禁止只依据训练损失判定方程已求解，必须在独立配点上计算 PDE 残差 [场景需求书 s04]

### Step 5：任务验收与适用域判定
- **操作**：按验收指标评价解场结果，报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本
- **输入**：{METRICS}（默认 relative_L2, PDE_residual, boundary_error, conservation_error）, {MAX_RELATIVE_L2}（默认 0.1）, {RUN_OOD_TEST}（默认 true）
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：
  - 统计与物理指标同时报告
  - 最差样本可追溯
  - 结论含适用域限制与复核建议
- **关键检查**：若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用 [场景需求书 s05]

## 关键参数

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| 训练/验证/测试比例 | 0.7/0.15/0.15 | [场景需求书] | 可按几何/工况调整 |
| 切分种子 | 42 | [场景需求书] | 保证可复现 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |
| 优化器 | Adam + L-BFGS | [1][2] | 两阶段混合 |
| 学习率 | 0.001 | [场景需求书] | Adam 阶段 |
| 早停耐心 | 15 epochs | [场景需求书] | 防过拟合 |
| 推理设备 | CUDA | [场景需求书] | CPU 可选但慢 |
| 相对误差门限 | 0.1 | [场景需求书] | PASS/REJECT 判据 |

## 边界与分流

| 条件 | 行动 |
|------|------|
| 数据文件不可读或格式不符 | 返回 BLOCKED，列出缺项 |
| 训练损失不收敛 | 降低学习率或减少网络复杂度 |
| 边界误差超限 | 增加边界配点权重或改硬边界 |
| 外推测试失败 | 缩小适用域报告范围，标注需 CFD 复核 |

## 质量检查

- 每步质量门禁必须独立通过才能进入下一步
- Step 5 的适用域判定必须包含 worst-case 分析
- PASS/REJECT/BLOCKED 三态结论必须附带物理门限依据

## 资源召回建议

- 本卡为工作流编排主卡，具体方法细节参见：
  - 损失权重策略：`cfd-pinn-loss-weighting-strategies`
  - NS 方程表述：`cfd-pinn-ns-formulation-selection`
  - 边界条件处理：`cfd-pinn-boundary-condition-enforcement`
  - 结果验证：`cfd-pinn-solution-validation`

## 证据来源

[1] Jin X, Cai S, Li H, Karniadakis GE. "NSFnets", JCP, 2020, DOI: 10.1016/j.jcp.2020.109951
[2] Xiang Z et al. "Self-adaptive loss balanced PINNs", Neurocomputing, 2022, DOI: 10.1016/j.neucom.2022.05.015
[场景需求书] CFD_S036_PINN不可压Navier-Stokes正问题求解.json
