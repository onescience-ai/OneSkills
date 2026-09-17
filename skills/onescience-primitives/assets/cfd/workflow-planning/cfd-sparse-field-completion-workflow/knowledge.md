# 稀疏CFD流场缺失区补全端到端工作流

## 适用范围

**触发条件**：
- 拥有稀疏或缺损的CFD流场数据，需要恢复完整高保真场
- 需要完成从数据准备到模型验收的完整任务链
- 采用隐式神经表示或扩散桥方法进行场补全

**适用场景**：
- PIV实验稀疏采样点的流场重构
- CFD模拟数据损坏或丢失后的场恢复
- 超分辨率重建：低分辨率→高分辨率流场
- 湍流场压缩存储与重建
- 需要端到端可复现的工程任务

**不适用场景**：
- 仅需快速原型验证、不要求端到端可追溯的场景
- 需要纯物理求解器（不使用深度学习）的场景

## 输入

| 输入项 | 格式 | 说明 |
|--------|------|------|
| 稀疏/缺损CFD场 | NetCDF/HDF5/CSV | 含坐标和物理量 |
| 数据契约 | JSON | 变量、单位、坐标系定义 |
| 切分配置 | JSON | train/val/test比例与切分策略 |
| 训练配置 | JSON | 超参数、框架、种子 |
| 验收指标 | 列表 | 统计与物理指标 |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 数据清单 | dataset_manifest.json | 可追溯的数据清单 |
| 数据契约 | data_contract.json | 机器可读契约 |
| 切分清单 | train/val/test_manifest.json | 三份互斥切分 |
| 模型权重 | best_checkpoint.pt | 通过训练门限的最佳权重 |
| 重构场 | reconstructed_fields/ | 逐样本重构结果 |
| 评估报告 | evaluation.json + applicability_report.md | 综合验收与适用域 |

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入稀疏或缺损CFD场与坐标查询，核验文件可读性、样本数、变量、单位、网格拓扑、时间范围、缺失值和使用许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **降级**：缺少必填输入时返回BLOCKED并列出缺项

### Step 2：预处理与数据切分
- **操作**：统一物理量表示与单位，执行归一化或无量纲化，按几何/工况/时间以对象为单位切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train/val/test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **关键约束**：不得把同一轨迹的帧随机打散

### Step 3：模型配置与训练
- **操作**：加载切分数据与统计量，训练INR和扩散桥模型，记录逐轮指标与最佳权重
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：低分辨或部分观测流场重构
- **操作**：加载模型权重，构造与真实采集一致的低分辨/稀疏/缺损输入，执行重构，恢复物理单位和边界
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：reconstructed_fields/, error_fields/, spectral_statistics.json
- **质量门禁**：观测掩膜与训练测试协议一致；小尺度频谱与统计量得到验证；边界守恒误差不因超分辨恶化

### Step 5：任务验收与适用域判定
- **操作**：按多维指标评估重构质量，执行几何或工况外推测试，明确适用域边界
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认训练框架 | PyTorch | [场景需求书] | 可替换为其他框架 |
| 默认训练轮数 | 100 epochs | [场景需求书] | 可按实际调整 |
| 默认批大小 | 8 | [场景需求书] | 可按显存调整 |
| 默认学习率 | 0.001 | [场景需求书] | 可按模型调整 |
| 默认早停耐心 | 15 epochs | [场景需求书] | 防止过拟合 |
| 切分比例 | train=0.7, val=0.15, test=0.15 | [场景需求书] | 默认配置 |
| 切分种子 | 42 | [场景需求书] | 可复现性 |
| 切分策略 | geometry_or_trajectory | [场景需求书] | 以几何或轨迹为单位 |
| 相对L2误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |
| 验收指标 | relative_L2, spectrum_error, gradient_error, conservation_error | [场景需求书] | 多维度评估 |

## 边界与分流

- **数据不可读/缺项**：Step 1 返回BLOCKED，列出所有缺失项
- **切分泄漏**：若检测到轨迹交叉切分，REJECT并要求重新配置
- **训练发散**：损失为NaN/Inf时，检查数据→降低学习率→简化网络→增加数据
- **掩膜不一致**：推断掩膜与训练不一致时REJECT
- **域外工况**：外推测试失败，结论须含适用域限制，建议CFD复核
- **守恒恶化**：超分辨导致守恒误差增大，评估是否接受或回退

## 质量检查

- Step 1：数据清单完整性、契约字段覆盖率
- Step 2：切分互斥性、变换统计量来源正确性
- Step 3：损失曲线收敛性、权重可加载性
- Step 4：重构场物理合理性、频谱匹配度
- Step 5：多指标综合评估、最差样本追溯

## 回退策略

- 数据质量差 → 回到数据源重新采集或清洗
- 模型训练失败 → 简化网络、调整超参、增加数据
- 重构质量不足 → 增加物理约束、调整模型架构
- 泛化能力不足 → 收集更多数据、使用域适应技术

## 资源召回建议

- 当需要执行CFD流场补全的完整端到端任务时召回
- 配套资源：cfd-missing-region-completion-implicit-neural-representation（场景级方法卡）
- 各步骤可单独召回对应task卡获取详细操作指南

## 证据来源

[1] PEINR: A Physics-enhanced Implicit Neural Representation for High-Fidelity Flow Field Reconstruction, 2024
[2] Physics-aligned field reconstruction with diffusion bridge, 2024
[3] Inpainting Computational Fluid Dynamics with Deep Learning, arXiv:2402.17185, 2024
[4] SCoReT: Super-Resolution Compression and Reconstruction of Turbulent Flows, arXiv:2607.03683, 2026
