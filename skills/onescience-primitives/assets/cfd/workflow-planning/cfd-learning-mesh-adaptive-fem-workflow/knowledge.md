# 学习型网格移动与自适应有限元优化工作流

## 适用范围

**触发条件**：
- 拥有自适应有限元网格误差数据，需要构建端到端的数据驱动网格移动流水线
- 目标是从误差数据中学习网格移动策略，优化网格质量并保持物理一致性
- 需要完整的训练-推理-评估-验收闭环

**适用场景**：
- 基于G-Adaptivity范式的图网格优化器训练与评估
- 通用网格移动网络（Universal Mesh Movement Network）的端到端开发
- 自适应有限元方法中数据驱动网格调整的全流程管理

**不适用场景**：
- 仅需单步推理（应使用cfd-mesh-candidate-generation-constraint-optimization）
- 仅需数据预处理（应使用cfd-mesh-data-intake-contract-validation或cfd-mesh-preprocessing-data-splitting）

## 输入

- **自适应有限元网格误差数据**：网格坐标、单元连接、误差指示器、物理量分布
- **数据契约**：变量名、单位、坐标系、网格拓扑定义（可选，默认为dataset_native）
- **模型名称**：Mesh movement network、Graph mesh optimizer或两者组合
- **训练配置**：框架、epochs、batch_size、学习率、随机种子、早停耐心

## 输出

- **可复现模型**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt
- **任务结果**：optimization_history.csv、pareto_front.json、design_candidates/
- **物理一致性评估**：evaluation.json、worst_cases.csv
- **适用域报告**：applicability_report.md、PASS_REJECT_BLOCKED.txt

## 流程节点

### s01 数据接入与契约核验
- **操作**：读取自适应有限元网格误差数据，建立数据清单，核验样本、变量、单位、网格坐标及许可
- **参数**：{DATASET_PATH}、{DATASET_NAME}、{DATA_CONTRACT}
- **工具**：文件系统读取、JSON解析、数据审计脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **输出**：dataset_manifest.json、data_contract.json、data_audit.md
- **提示词**：读取{DATASET_PATH}中的{DATASET_NAME}，为"学习型网格移动与自适应有限元优化"建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

### s02 预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：{SPLIT_CONFIG}、{TARGET_FIELDS}、{NONDIMENSIONALIZE}
- **工具**：归一化计算器、切分工具、图构建器
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json
- **提示词**：依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。

### s03 模型配置与训练
- **操作**：训练Mesh movement network、Graph mesh optimizer完成指定输入到目标物理量的映射
- **参数**：{MODEL_NAME}、{TRAIN_CONFIG}、{INIT_CHECKPOINT}
- **工具**：PyTorch、GNN库（如PyG、DGL）、训练监控脚本
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt
- **提示词**：使用{MODEL_NAME}，默认Mesh movement network、Graph mesh optimizer，和{TRAIN_CONFIG}训练"学习型网格移动与自适应有限元优化"模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。

### s04 候选生成与约束优化
- **操作**：围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹
- **参数**：{CHECKPOINT}、{DEVICE}、{BATCH_SIZE}
- **工具**：模型加载器、优化搜索脚本、Pareto前沿提取器
- **质量门禁**：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签
- **输出**：design_candidates/、optimization_history.csv、pareto_front.json
- **提示词**：加载{CHECKPOINT}和数据契约，将{TARGET_FIELDS}解释为优化目标与约束，执行可复现的候选生成和优化搜索。保存每次评估、可行性、目标值及Pareto前沿；不得把代理预测直接当作高保真认证结果。

### s05 任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED结论
- **参数**：{METRICS}、{MAX_RELATIVE_L2}、{RUN_OOD_TEST}
- **工具**：误差计算脚本、物理约束检查器、可视化工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt
- **提示词**：按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景CFD_S030] | 训练与推理框架 |
| 默认epochs | 100 | [场景CFD_S030] | 训练轮数，可通过早停提前终止 |
| 默认batch_size | 8 | [场景CFD_S030] | 训练批大小，需适配显存 |
| 默认学习率 | 0.001 | [场景CFD_S030] | Adam优化器默认学习率 |
| 早停耐心 | 15 | [场景CFD_S030] | 验证集loss不下降的最大容忍轮数 |
| 相对误差门限 | 0.1 | [场景CFD_S030] | 测试集PASS/REJECT判定阈值 |
| 默认切分比 | 0.7/0.15/0.15 | [场景CFD_S030] | 训练/验证/测试比例 |
| 默认随机种子 | 42 | [场景CFD_S030] | 确保可复现性 |
| 验收指标 | objective_improvement, constraint_violation, CFD_validation_error | [场景CFD_S030] | 统计与物理约束双重评估 |
| 默认设备 | cuda | [场景CFD_S030] | GPU推理，CPU作为备选 |

### 校准数值

以下数值来自CFD_S030场景定义，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认切分group_by | geometry_or_trajectory | [场景CFD_S030] | 按几何或轨迹切分，防止泄漏 |
| 数据坐标系 | dataset_native | [场景CFD_S030] | 默认使用数据集原生坐标系 |

## 边界与分流

- **数据格式不兼容**：网格误差数据格式与图神经网络输入不匹配时，先执行图格式转换，再进入s02
- **网格拓扑不稳定**：自适应网格演化导致拓扑剧变时，降级为固定网格GNN或回退到拉格朗日粒子表示
- **物理约束违反**：守恒残差超出阈值时，在损失函数中添加物理约束正则项重新训练
- **域外工况检测**：外推测试显示性能骤降时，在适用域报告中标注需要CFD复核的工况范围
- **训练不收敛**：损失曲线振荡或发散时，降低学习率、增大早停耐心或检查数据质量
- **权重加载失败**：检查权重文件完整性和模型结构兼容性，报错并停止

## 质量检查

- 数据审计：每个变量的统计分布合理性、缺失值比例、坐标系一致性
- 训练过程：损失曲线平滑性、验证集泛化间隙、梯度爆炸检测
- 推理结果：网格移动预测的物理合理性（网格不自交、边界保持、质量指标改善）
- 物理一致性：守恒方程残差量级、边界条件满足度、时间演化稳定性
- 适用域：训练分布覆盖度、OOD样本比例、最差样本的物理特征分析

## 回退策略

- 图神经网络不适用时：退化为传统CFD求解器的自适应网格移动模块
- 消息传递不稳定时：改用注意力机制或增加消息传递轮数
- 网格移动开销过大时：使用多尺度图表示或分层图网络降低计算复杂度
- 训练数据不足时：采用迁移学习从预训练网格移动模型微调

## 资源召回建议

- 当用户需要执行学习型网格移动的完整端到端工作流时召回本卡
- 配套任务卡：cfd-mesh-data-intake-contract-validation（s01）、cfd-mesh-preprocessing-data-splitting（s02）、cfd-mesh-model-training-optimization（s03）、cfd-mesh-candidate-generation-constraint-optimization（s04）、cfd-mesh-acceptance-applicability-domain（s05）
- 场景卡：cfd-learning-based-mesh-movement-optimization（场景定义）

## 证据来源

[1] "G-Adaptivity: optimised graph-based mesh relocation for finite element methods", 2024
[2] "Towards Universal Mesh Movement Networks", 2024
[3] 场景CFD_S030需求书定义
