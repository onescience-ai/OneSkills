# PDE神经算子预测工作流

## 适用范围

**触发条件**：
- 需要端到端完成PDE神经算子的训练与评估
- 从原始PDE分布数据到可部署模型的完整流程

**适用场景**：
- 连续时间PDE动力学的算子学习
- 随机PDE分布的统计矩预测与采样
- 需要物理一致性验证的工程预测模型构建

**不适用场景**：
- 仅需单一步骤执行（应召回对应task卡片）
- 已有成熟模型仅需推理（跳过训练阶段）
- 纯理论分析无需实验验证

## 输入

- PDE分布数据集路径与名称
- 可选数据契约定义
- 可选预训练权重

## 输出

- 数据清单与契约（dataset_manifest.json, data_contract.json, data_audit.md）
- 训练/验证/测试切分清单与归一化参数
- 训练完成的模型权重与训练日志
- 独立测试集预测结果
- 验收评估报告与适用域判定

## 流程节点

### Step 1：数据接入与契约核验（s01）
- **操作**：接入PDE分布数据，建立机器可读契约
- **参数**：DATASET_PATH, DATASET_NAME, DATA_CONTRACT
- **工具**：Python数据处理库（numpy/pandas/xarray）
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **产出**：dataset_manifest.json, data_contract.json, data_audit.md

### Step 2：预处理与数据切分（s02）
- **操作**：统一物理量表示，按几何/工况/轨迹无泄漏切分
- **参数**：SPLIT_CONFIG (train/val/test比例, seed, group_by), TARGET_FIELDS, NONDIMENSIONALIZE
- **工具**：Python数据处理库
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **产出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **依赖**：s01

### Step 3：模型配置与训练（s03）
- **操作**：配置并训练Continuous-time neural operator和Stochastic neural operator
- **参数**：MODEL_NAME, TRAIN_CONFIG (framework, epochs, batch_size, learning_rate, seed, early_stopping_patience), INIT_CHECKPOINT
- **工具**：PyTorch, 自定义神经算子实现
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **产出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **依赖**：s02

### Step 4：批量推理与物理恢复（s04）
- **操作**：加载checkpoint在测试集推理，反归一化恢复物理单位
- **参数**：CHECKPOINT, DEVICE, BATCH_SIZE
- **工具**：PyTorch推理
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- **产出**：predictions/, inference_manifest.json, timing.csv
- **依赖**：s03

### Step 5：任务验收与适用域判定（s05）
- **操作**：评估统计误差、物理约束、泛化能力和计算收益
- **参数**：METRICS, MAX_RELATIVE_L2, RUN_OOD_TEST
- **工具**：评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **产出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **依赖**：s04

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认切分比 | 0.7/0.15/0.15 | 场景需求书 | train/val/test |
| 切分分组依据 | geometry_or_trajectory | 场景需求书 | 按几何或轨迹切分，防泄漏 |
| 默认无量纲化 | true | 场景需求书 | 统一跨工况量纲 |
| 默认框架 | PyTorch | 场景需求书 | 训练框架 |
| 默认轮数 | 100 epochs | 场景需求书 | 可据早停调整 |
| 默认批大小 | 8 | 场景需求书 | 按显存调整 |
| 默认学习率 | 0.001 | 场景需求书 | 优化器学习率 |
| 默认种子 | 42 | 场景需求书 | 可复现性 |
| 早停耐心 | 15 epochs | 场景需求书 | 验证损失不改善等待 |
| 默认验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计+物理 |
| 默认误差门限 | 0.1 | 场景需求书 | relative_L2放行阈值 |
| 默认外推测试 | true | 场景需求书 | 测试域外工况 |

## 边界与分流

- **数据缺失**：s01返回BLOCKED，列出缺项
- **s01失败**：流程中断，不进入s02
- **s02切分异常（轨迹泄漏）**：终止并报告
- **s03训练异常（损失非有限）**：检查数据与超参数后重试
- **s04推理异常（NaN/Inf）**：检查checkpoint与数据契约
- **s05验收REJECT**：标注适用域限制，建议CFD复核或重训

## 质量检查

- 每个阶段产出机器可读的质量门禁报告
- 阶段间通过manifest文件传递状态
- 最终验收同时覆盖统计误差与物理约束
- 最差样本可追溯到具体输入

## 回退策略

- 数据质量不足：增加数据清洗与增强
- 训练不收敛：调整超参数、更换模型架构
- 推理异常：降低批大小、检查设备兼容性
- 验收不达标：分析最差样本、调整训练策略或扩大适用域标注

## 资源召回建议

- 本卡片提供PDE神经算子预测的完整工作流框架
- 需要具体步骤执行时，召回对应task卡片：
  - cfd-pde-data-ingestion-contract-validation（s01）
  - cfd-pde-data-preprocessing-split（s02）
  - cfd-neural-operator-model-training（s03）
  - cfd-neural-operator-inference-physics-recovery（s04）
  - cfd-neural-operator-validation-applicability（s05）

## 证据来源

[1] CFO: Learning Continuous-Time PDE Dynamics via Flow-Matched Neural Operators, arXiv:2303.08797, 2023
[2] Wavelet Diffusion Neural Operator, 2024
[3] Neural Stochastic PDEs: Resolution-Invariant Learning of Continuous Spatiotemporal Dynamics, 2023
