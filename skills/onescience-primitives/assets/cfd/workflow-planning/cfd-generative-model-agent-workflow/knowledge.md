# 生成模型与智能体工程外形协同设计工作流程

## 适用范围

本工作流程适用于使用生成模型与工程智能体进行车辆或软体结构外形协同设计的完整过程，从数据接入到最终验收判定，确保系统化、可复现的设计流程。

## 输入

- **数据集**：车辆或软体结构生成设计数据
- **设计目标**：美学要求、性能指标、制造约束
- **配置参数**：切分配置、训练配置、优化预算
- **工具环境**：PyTorch、CFD模拟器、可视化工具

## 输出

- **设计产物**：生成的设计候选、优化后的设计
- **评估报告**：性能评估、适用域报告、验收结论
- **模型产物**：训练好的模型、配置文件、环境依赖
- **文档产物**：数据契约、处理日志、可复现指南

## 流程节点

### 步骤1：数据接入与契约核验
**输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
**操作**：
1. 读取数据集，建立数据清单
2. 检查文件可读性、样本数、输入与目标变量
3. 验证单位、坐标系、网格拓扑、时间或工况范围
4. 检查缺失值和使用许可
5. 输出机器可读契约

**输出**：dataset_manifest.json, data_contract.json, data_audit.md
**质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### 步骤2：预处理与数据切分
**输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
**操作**：
1. 依据契约完成质控、重采样或图构建
2. 进行掩膜、归一化或无量纲化
3. 按几何、完整轨迹或物理工况为单位切分
4. 为{TARGET_FIELDS}保存统计量与可逆变换

**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
**质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### 步骤3：模型配置与训练
**输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
**操作**：
1. 使用{MODEL_NAME}和{TRAIN_CONFIG}训练模型
2. 加载切分与统计量
3. 记录代码版本、依赖、随机种子
4. 记录逐轮训练验证指标与最佳权重
5. 若提供{INIT_CHECKPOINT}须检查结构兼容性

**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
**质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### 步骤4：候选生成与约束优化
**输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
**操作**：
1. 加载{CHECKPOINT}和数据契约
2. 将{TARGET_FIELDS}解释为优化目标与约束
3. 执行可复现的候选生成和优化搜索
4. 保存每次评估、可行性、目标值及Pareto前沿

**输出**：design_candidates/, optimization_history.csv, pareto_front.json
**质量门禁**：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签

### 步骤5：任务验收与适用域判定
**输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
**操作**：
1. 按{METRICS}评价结果
2. 报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本
3. 使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
4. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域

**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
**质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | 训练/验证/测试集比例 |
| 随机种子 | 42 | [场景需求书] | 确保可复现性 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |
| 训练轮次 | 100 | [场景需求书] | 默认训练配置 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 相对误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |

## 边界与分流

- **数据缺失**：返回BLOCKED并列出缺项，不得编造数据
- **训练不收敛**：调整超参数或使用预训练权重
- **优化失败**：使用不同的随机种子或调整搜索策略
- **验收不通过**：根据错误类型选择重新训练、调整设计或CFD复核

## 质量检查

- **数据完整性**：所有必填字段完整、无缺失
- **处理可逆性**：所有变换保存统计量，确保可逆
- **模型可复现**：固定随机种子、记录环境依赖
- **设计可行性**：满足几何和物理硬约束
- **评估全面性**：统计指标与物理指标同时报告

## 回退策略

- **数据不足**：使用数据增强或迁移学习
- **模型性能差**：尝试不同的模型架构或超参数
- **优化效率低**：使用代理模型或渐进优化
- **验收不通过**：分析失败原因，选择针对性改进措施

## 资源召回建议

- **数据标准器**：用于数据预处理和契约生成
- **训练器**：用于模型训练和配置
- **推理器**：用于设计生成和性能评估
- **运行时**：用于作业提交和环境管理
- **编码器**：用于算法实现和集成

## 证据来源

[1] AI Agents in Engineering Design: A Multi-Agent Framework for Aesthetic and Aerodynamic Car Design, Mohamed Elrefaie et al., arXiv:2503.23315, 2025
[2] DiffuseBot: Breeding Soft Robots With Physics-Augmented Generative Diffusion Models, Tsun-Hsuan Wang et al., arXiv:2311.17053, 2023