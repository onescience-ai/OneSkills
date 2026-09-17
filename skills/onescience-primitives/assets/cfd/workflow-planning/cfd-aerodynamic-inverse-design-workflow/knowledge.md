# 生成模型气动外形与流场联合逆向设计工作流

## 适用范围

**触发条件**：
- 已有翼型几何-流场-性能联合数据，需要端到端训练生成模型完成逆向设计
- 需要一个结构化的五步工作流来组织从数据接入到适用域判定的完整流程
- 需要确保每个步骤有明确的质量门禁和输出产物

**适用场景**：
- 基于潜空间扩散模型的翼型逆向设计项目
- 生成模型气动设计方法的标准化实施
- 需要可复现、可追溯的气动设计工作流管理

**不适用场景**：
- 仅需单步操作（如仅训练或仅推理）的场景
- 数据已预处理完毕无需契约核验的场景

## 输入

- 翼型几何-流场-性能联合数据集路径
- 数据契约定义（变量、单位、坐标系）
- 切分配置（比例、种子、分组策略）
- 训练配置（框架、超参数）
- 验收指标与误差门限

## 输出

- 五个步骤的产物：dataset_manifest.json → train/val/test_manifest.json → best_checkpoint.pt → generated_samples/ → evaluation.json + applicability_report.md
- 每步质量门禁验证结果
- PASS/REJECT/BLOCKED 判定

## 流程节点

### s01 数据接入与契约核验
- **操作**：读取数据集，检查文件可读性、样本数、变量、单位、坐标系、网格拓扑、时间/工况范围、缺失值、使用许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### s02 预处理与数据切分
- **操作**：质控、重采样或图构建、掩膜、归一化或无量纲化；按几何、完整轨迹或物理工况为单位切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **依赖**：s01

### s03 模型配置与训练
- **操作**：使用Latent diffusion model、Generative design model训练，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **依赖**：s02

### s04 条件采样与物理一致性筛选
- **操作**：对每个测试条件生成多随机种子样本，恢复物理量后计算边界、守恒与方程残差，剔除不合格样本并评估分布覆盖
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：generated_samples/, physics_filter.json, distribution_metrics.json
- **质量门禁**：样本条件与随机种子可追溯；多样性和真实性同时评价；物理筛选前后统计均报告
- **依赖**：s03

### s05 任务验收与适用域判定
- **操作**：按指标评价s04结果，报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本；执行几何或工况外推测试并明确适用域
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **依赖**：s04

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| s01 数据契约 | input_fields/target_fields/units/coordinates | [1] | 核验基础 |
| s02 切分比例 | 0.7/0.15/0.15 | [1] | 防泄漏 |
| s02 切分单位 | geometry_or_trajectory | [1] | 不打散同一轨迹 |
| s03 框架 | PyTorch | [1] | 默认 |
| s03 epochs | 100 | [1] | 默认 |
| s03 batch_size | 8 | [1] | 按显存调整 |
| s03 learning_rate | 0.001 | [1] | 默认 |
| s03 early_stopping | 15 | [1] | 耐心值 |
| s04 推理批大小 | 8 | [1] | 按显存调整 |
| s05 验收指标 | distribution_distance, diversity, physics_residual, coverage | [1] | 四维度 |
| s05 误差门限 | 0.1 | [1] | 相对L2 |
| s05 OOD测试 | true | [1] | 默认开启 |

## 边界与分流

- **s01 数据缺失**：返回BLOCKED，列出缺项，不编造数据
- **s02 切分后统计量泄露**：仅用训练集计算归一化统计量，验证集和测试集使用训练集统计量
- **s03 训练不收敛**：检查超参数和数据质量，必要时调整学习率或引入预训练权重
- **s04 物理筛选通过率极低**：降低物理约束权重，排查数据质量问题
- **s05 判定为BLOCKED**：停止自动流程，转人工CFD复核
- **s05 判定为REJECT**：分析失败原因，回退到s03调整模型或s02调整数据

## 质量检查

- 每步产物文件完整且可读
- 质量门禁逐项验证通过
- 全流程可复现（随机种子、环境、配置均有记录）
- 最差样本可追溯
- 适用域报告含复核建议

## 回退策略

- 任一步骤BLOCKED：停在该步骤，列出缺项和建议
- 训练失败：回退到传统优化方法
- 适用域过窄：补充数据或缩小应用范围

## 资源召回建议

- 当需要端到端执行气动逆向设计完整流程时召回
- 配套资源：cfd-aerodynamic-joint-inverse-design（场景级）、各步骤task卡
- 若仅需训练步骤：召回 cfd-latent-diffusion-aerodynamic-training
- 若仅需验收评估：召回 cfd-aerodynamic-applicability-domain-evaluation

## 证据来源

[1] 场景需求书 CFD_S094：生成模型气动外形与流场联合逆向设计，scenario_catalogs/fluid/CFD_S094_生成模型气动外形与流场联合逆向设计.json
[2] "Aerodynamic Shape Design Space Exploration with Deep Latent Diffusion Model", arXiv:2609.00812
[3] "Diffusion Model Driven Airfoil Design_ From Geometry Encoding to Practical Applications", arXiv:2601.16228
