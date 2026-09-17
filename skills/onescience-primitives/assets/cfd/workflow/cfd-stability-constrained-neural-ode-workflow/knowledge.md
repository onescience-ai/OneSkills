# 稳定性约束神经微分方程动力学学习工作流

## 适用范围

本工作流覆盖从原始显式约束动力系统时序数据到物理一致性验证的完整建模闭环。适用于：
- 基于Stable Neural ODE的连续时间动力学建模
- 需要稳定性约束与物理一致性的深度学习模型
- 显式约束（守恒律、边界条件）动力系统时序数据建模

工作流包含5个串行步骤，每步有明确的输入输出契约和质量门禁。

## 输入

**前置条件**：
- 显式约束动力系统时序数据集（状态变量、控制输入、时间戳）
- 数据契约定义（变量、单位、坐标系、约束条件）
- 切分配置（比例、种子、分组策略）
- 训练配置（框架、超参数、设备）

**可选输入**：
- 预训练权重（初始checkpoint）
- 自定义评估指标

## 输出

**最终产物**：
- 训练好的Stable Neural ODE模型
- 测试集预测结果
- 评估报告与适用域报告
- 验收判定（PASS/REJECT/BLOCKED）

**中间产物**：
- 数据清单与契约（s01）
- 切分清单与归一化统计（s02）
- 训练配置与指标（s03）
- 推理清单与耗时（s04）

## 流程节点

### s01 数据接入与契约核验

**操作**：
1. 读取{DATASET_PATH}中的{DATASET_NAME}
2. 检查文件可读性、样本数、变量完整性
3. 核验单位、坐标系、网格拓扑、时间范围
4. 检测缺失值和使用许可
5. 按{DATA_CONTRACT}输出机器可读契约

**输入**：
- {DATASET_PATH}: 数据集路径（必填）
- {DATASET_NAME}: 数据集名称（必填，默认"显式约束动力系统时序数据"）
- {DATA_CONTRACT}: 数据契约模板（可选）

**输出**：
- dataset_manifest.json: 数据清单
- data_contract.json: 机器可读契约
- data_audit.md: 审计报告

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**分流条件**：
- 缺少必填输入 → 返回BLOCKED，列出缺项
- 数据格式不兼容 → 拒绝处理，要求修复

### s02 预处理与数据切分

**操作**：
1. 依据s01契约完成质控
2. 统一物理量与表示
3. 重采样或插值（时间序列对齐）
4. 归一化或无量纲化
5. 按{SPLIT_CONFIG}以几何/轨迹/工况为单位切分
6. 保存统计量与可逆变换

**输入**：
- {SPLIT_CONFIG}: 切分配置（必填，默认train:0.7/val:0.15/test:0.15, seed:42）
- {TARGET_FIELDS}: 目标变量列表（必填）
- {NONDIMENSIONALIZE}: 是否无量纲化（可选，默认true）

**输出**：
- train_manifest.json: 训练集清单
- validation_manifest.json: 验证集清单
- test_manifest.json: 测试集清单
- normalization.json: 归一化统计

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**关键约束**：
- 禁止把同一轨迹的帧随机打散
- 切分单位必须是完整轨迹或物理工况

### s03 模型配置与训练

**操作**：
1. 加载{MODEL_NAME}（默认Stable Neural ODE + Constrained Neural Process）
2. 应用{TRAIN_CONFIG}（框架、超参数、随机种子）
3. 加载s02切分与统计量
4. 执行训练，记录逐轮指标
5. 保存最佳权重与配置

**输入**：
- {MODEL_NAME}: 模型名称（必填）
- {TRAIN_CONFIG}: 训练配置（必填，默认PyTorch, epochs:100, batch:8, lr:0.001）
- {INIT_CHECKPOINT}: 初始权重（可选）

**输出**：
- best_checkpoint.pt: 最佳模型权重
- train_config.json: 训练配置
- training_metrics.csv: 训练指标
- environment.txt: 环境记录

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**关键约束**：
- 若提供{INIT_CHECKPOINT}须检查结构兼容性
- 缺少必填输入时返回BLOCKED

### s04 批量推理与物理恢复

**操作**：
1. 加载{CHECKPOINT}及训练时数据契约
2. 在s02独立测试集上推理
3. 反归一化并恢复物理单位
4. 恢复坐标网格、边界掩膜
5. 计算任务派生量
6. 保存逐样本结果和耗时

**输入**：
- {CHECKPOINT}: 模型权重（必填，默认best_checkpoint.pt）
- {DEVICE}: 计算设备（必填，默认cuda）
- {BATCH_SIZE}: 推理批大小（可选，默认8）

**输出**：
- predictions/: 预测结果目录
- inference_manifest.json: 推理清单
- timing.csv: 耗时记录

**质量门禁**：
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

**关键约束**：
- 禁止用测试标签修正预测
- 必须反归一化恢复原始物理单位

### s05 任务验收与适用域判定

**操作**：
1. 按{METRICS}评价s04结果
2. 报告逐变量误差、边界误差、守恒/方程残差
3. 分析最差样本和推理成本
4. 使用{MAX_RELATIVE_L2}及任务物理门限判定
5. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试
6. 明确适用域限制与复核建议

**输入**：
- {METRICS}: 验收指标列表（必填，默认relative_L2, RMSE, conservation_residual, boundary_error）
- {MAX_RELATIVE_L2}: 相对误差门限（可选，默认0.1）
- {RUN_OOD_TEST}: 是否外推测试（可选，默认true）

**输出**：
- evaluation.json: 评估结果
- worst_cases.csv: 最差样本
- applicability_report.md: 适用域报告
- PASS_REJECT_BLOCKED.txt: 验收判定

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**分流条件**：
- 相对L2误差超门限 → REJECT
- 物理约束违反严重 → REJECT
- 域外工况测试失败 → 明确适用域限制

## 关键参数

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| 切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书] | 标准三分 |
| 随机种子 | 42 | [场景需求书] | 可复现性 |
| 切分单位 | geometry_or_trajectory | [场景需求书] | 禁止帧打散 |
| 无量纲化 | true | [场景需求书] | 统一量纲 |
| 训练框架 | PyTorch | [场景需求书] | 默认实现 |
| Epochs | 100 | [场景需求书] | 可配置 |
| Batch size | 8 | [场景需求书] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书] | 默认配置 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 相对误差门限 | 0.1 | [场景需求书] | 放行阈值 |
| 推理设备 | cuda | [场景需求书] | 默认GPU |

## 边界与分流

**步骤间依赖**：
- s02依赖s01输出（data_contract.json）
- s03依赖s02输出（切分清单、归一化统计）
- s04依赖s03输出（checkpoint）
- s05依赖s04输出（predictions）

**异常处理**：
- 任一步骤失败 → 阻塞后续步骤，返回BLOCKED
- 质量门禁不通过 → 该步骤返回REJECT
- 数据/模型不兼容 → 明确错误信息，指导修复

**降级策略**：
- GPU不可用 → 降级到CPU推理（耗时增加）
- 数据量不足 → 调整切分比例或使用数据增强
- 训练不收敛 → 调整超参数或模型复杂度

## 质量检查

**每步检查点**：
- s01: 数据完整性、契约合规性
- s02: 切分互斥性、统计量正确性
- s03: 损失收敛性、权重可加载性
- s04: 预测有效性、物理恢复正确性
- s05: 误差合规性、适用域明确性

**端到端检查**：
- 从数据到验收的完整追溯链
- 所有中间产物可复现
- 最终判定有充分证据支持

## 回退策略

**数据层面回退**：
- 格式不兼容 → 转换为标准格式
- 数据量不足 → 扩充数据或迁移学习
- 物理量缺失 → 调整预测目标

**模型层面回退**：
- 训练不收敛 → 降低学习率、增加正则化
- 过拟合 → 数据增强、调整复杂度
- 显存不足 → 减小batch_size、梯度累积

**验收层面回退**：
- 误差超标 → 分析误差来源、针对性优化
- 物理违反 → 增加物理约束损失
- 域外失败 → 缩小适用域、增加域外数据

## 资源召回建议

**何时召回本卡片**：
- 需要完整的Stable Neural ODE建模流程
- 需要从数据到验收的端到端工作流
- 需要物理一致性验证的深度学习动力学模型

**配套资源**：
- 场景卡：cfd-stability-constrained-neural-ode-dynamics-learning
- 任务卡：cfd-neural-ode-data-intake-contract-validation
- 任务卡：cfd-neural-ode-preprocessing-data-splitting
- 任务卡：cfd-stable-neural-ode-model-training
- 任务卡：cfd-neural-ode-batch-inference-physical-recovery
- 任务卡：cfd-neural-ode-acceptance-applicability

## 证据来源

[1] Stabilized Neural Differential Equations for Learning Dynamics with Explicit Constraints, [场景需求书related_papers]
[2] Neural Processes with Stability, [场景需求书related_papers]
