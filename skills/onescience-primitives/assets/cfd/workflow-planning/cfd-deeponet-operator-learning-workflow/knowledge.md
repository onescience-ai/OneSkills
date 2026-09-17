# DeepONet算子学习工作流

## 适用范围

**触发条件**：
- 需要执行完整的DeepONet或Neural Green function训练流程
- 有函数输入到解函数配对数据集
- 需要系统化的数据处理、模型训练和评估流程

**适用场景**：
- CFD代理模型开发项目
- 参数化PDE快速求解器构建
- 物理场预测模型训练
- 算子学习方法对比实验

**不适用场景**：
- 单步模型推理（无训练需求）
- 纯数据探索或可视化
- 非算子学习的通用机器学习任务

## 输入

**数据要求**：
- 函数输入到解函数的配对数据集
- 数据路径与名称指定
- 可选的数据契约定义（变量、单位、坐标系）

**配置要求**：
- 切分配置（比例、分组策略、随机种子）
- 训练配置（框架、epochs、batch_size、学习率等）
- 评估指标与门限配置

## 输出

**产物清单**：
- 数据清单与契约：dataset_manifest.json, data_contract.json, data_audit.md
- 切分结果：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- 训练产物：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- 推理结果：predictions/, inference_manifest.json, timing.csv
- 评估报告：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

## 流程节点

### Step 1：数据接入与契约核验（s01）
- **操作**：接入函数输入到解函数配对数据，核验样本、变量、单位、网格坐标及许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **依赖**：无前置步骤

### Step 2：预处理与数据切分（s02）
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **依赖**：s01

### Step 3：模型配置与训练（s03）
- **操作**：训练DeepONet或Neural Green function完成指定输入到目标物理量的映射
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **依赖**：s02

### Step 4：批量推理与物理恢复（s04）
- **操作**：在独立测试集推理，恢复原始单位、网格和物理派生量
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：predictions/, inference_manifest.json, timing.csv
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- **依赖**：s03

### Step 5：任务验收与适用域判定（s05）
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **依赖**：s04

## 关键参数

**流程控制参数**：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7:0.15:0.15 | 场景需求书 | 训练:验证:测试标准比例 |
| 分组策略 | geometry_or_trajectory | 场景需求书 | 按几何或轨迹分组避免泄漏 |
| 无量纲化 | true | 场景需求书 | 统一跨工况量纲 |
| 训练框架 | PyTorch | 场景需求书 | 深度学习框架 |
| 默认epochs | 100 | 场景需求书 | 训练轮数 |
| 默认batch_size | 8 | 场景需求书 | 批处理大小 |
| 默认learning_rate | 0.001 | 场景需求书 | 学习率 |
| 默认seed | 42 | 场景需求书 | 随机种子 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合 |
| 相对误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |

**验收指标**：

| 指标 | 用途 | 来源 |
|------|------|------|
| relative_L2 | 相对L2误差 | 场景需求书 |
| RMSE | 均方根误差 | 场景需求书 |
| conservation_residual | 守恒残差 | 场景需求书 |
| boundary_error | 边界误差 | 场景需求书 |

## 边界与分流

**步骤级分流**：

1. **s01数据不可读** → 返回BLOCKED，列出缺项，不进入后续步骤
2. **s02切分泄漏** → 重新设计分组策略，重新切分
3. **s03训练不收敛** → 调整超参数或模型架构，重新训练
4. **s04推理异常** → 检查checkpoint兼容性，修复后重新推理
5. **s05验收不通过** → 进入REJECT流程，需CFD复核或调整适用域

**降级策略**：
- 数据不足 → 合成数据增强或迁移学习
- 训练失败 → 尝试不同模型架构
- 物理约束不满足 → 添加物理正则化
- 域外性能差 → 降低适用域范围

## 质量检查

**过程检查点**：
- s01：数据完整性、单位一致性、无泄漏
- s02：切分互斥性、统计量仅用训练集、语义完整性
- s03：损失收敛性、权重可加载性、可复现性
- s04：预测正确性、样本唯一性、无标签泄露
- s05：指标完整性、样本可追溯性、结论明确性

**最终验收标准**：
- 统计指标（relative_L2, RMSE）满足门限
- 物理指标（conservation_residual, boundary_error）满足物理允许值
- 最差样本可追溯
- 适用域报告明确

## 资源召回建议

**何时应召回本卡片**：
- 用户需要执行完整的DeepONet训练流程
- 用户需要系统化的算子学习工作流指导
- 用户需要数据处理、训练、评估的标准流程

**配套资源**：
- cfd-deeponet-neural-green-operator-learning：场景级概览卡
- cfd-operator-data-validation：数据核验任务卡
- cfd-operator-data-preprocessing：预处理切分任务卡
- cfd-deeponet-training：模型训练任务卡
- cfd-operator-inference-physical-recovery：推理恢复任务卡
- cfd-operator-evaluation-applicability：验收评估任务卡

## 证据来源

[1] "Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators", Lu Lu et al., Nature Machine Intelligence, 2021, URL: https://arxiv.org/abs/1910.03193
