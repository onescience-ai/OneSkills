# 学习型网格移动与自适应有限元优化

## 适用范围

**触发条件**：
- 拥有自适应有限元网格误差数据（网格坐标、单元误差指示器、物理量分布）
- 需要利用数据驱动方法学习网格移动策略以优化网格质量
- 目标是构建可复现的学习型网格移动模型，替代或加速传统自适应有限元网格重定位

**适用场景**：
- 基于图神经网络的有限元网格重定位优化（G-Adaptivity范式）
- 通用网格移动网络（Universal Mesh Movement Network）的训练与评估
- 自适应有限元方法中需要学习误差驱动网格调整策略的研究
- 非结构化网格上的物理一致性网格优化

**不适用场景**：
- 规则结构化网格上的标准AMR（自适应网格细化）——本场景针对学习型网格移动
- 无误差数据的纯几何网格生成
- 网格拓扑固定的稳态求解问题

## 输入

- **自适应有限元网格误差数据**：包含网格节点坐标、单元连接关系、误差指示器（如后验误差估计）、物理量分布（速度、压力等）
- **数据契约**：变量名、单位、坐标系、网格拓扑定义
- **可选预训练权重**：已有Mesh movement network或Graph mesh optimizer权重

## 输出

- **可复现模型**：训练好的Mesh movement network和/或Graph mesh optimizer权重（best_checkpoint.pt）
- **任务结果**：测试集上的网格移动预测结果、优化后网格质量指标
- **物理一致性评估**：网格移动后的物理约束满足度（守恒残差、边界误差）
- **适用域报告**：模型在训练域内和域外工况的性能边界，标注哪些工况需要CFD复核

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入自适应有限元网格误差数据，核验样本、变量、单位、网格坐标及许可
- **参数**：数据集路径、数据集名称、数据契约
- **工具**：文件系统读取、JSON解析、数据审计脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **输出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：切分配置、目标变量列表、是否无量纲化
- **工具**：归一化计算器、切分工具、图构建器
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### Step 3：模型配置与训练
- **操作**：训练Mesh movement network和/或Graph mesh optimizer完成指定输入到目标物理量的映射
- **参数**：模型名称、训练配置（框架、epochs、batch_size、学习率、种子、早停）、可选预训练权重
- **工具**：PyTorch、GNN库（如PyG、DGL）、训练监控脚本
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：候选生成与约束优化
- **操作**：围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹
- **参数**：模型权重路径、计算设备、推理批大小
- **工具**：模型加载器、优化搜索脚本、Pareto前沿提取器
- **质量门禁**：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签
- **输出**：design_candidates/、optimization_history.csv、pareto_front.json

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED结论
- **参数**：验收指标列表、相对误差门限、是否执行外推测试
- **工具**：误差计算脚本、物理约束检查器、可视化工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Mesh movement network, Graph mesh optimizer | [场景CFD_S030] | 两种互补的网格移动学习架构 |
| 默认框架 | PyTorch | [场景CFD_S030] | 训练与推理框架 |
| 默认epochs | 100 | [场景CFD_S030] | 训练轮数，可通过早停提前终止 |
| 默认batch_size | 8 | [场景CFD_S030] | 训练批大小，需适配显存 |
| 默认学习率 | 0.001 | [场景CFD_S030] | Adam优化器默认学习率 |
| 早停耐心 | 15 | [场景CFD_S030] | 验证集loss不下降的最大容忍轮数 |
| 相对误差门限 | 0.1 | [场景CFD_S030] | 测试集PASS/REJECT判定阈值 |
| 默认切分比 | 0.7/0.15/0.15 | [场景CFD_S030] | 训练/验证/测试比例 |
| 默认随机种子 | 42 | [场景CFD_S030] | 确保可复现性 |
| 验收指标 | objective_improvement, constraint_violation, CFD_validation_error | [场景CFD_S030] | 统计与物理约束双重评估 |

## 边界与分流

- **数据格式不兼容**：网格误差数据格式与图神经网络输入不匹配时，先执行图格式转换（如DGL↔PyG适配），再进入Step 2
- **网格拓扑不稳定**：自适应网格演化导致拓扑剧变时，降级为固定网格GNN或回退到拉格朗日粒子表示
- **物理约束违反**：守恒残差超出阈值时，在损失函数中添加物理约束正则项重新训练
- **域外工况检测**：外推测试显示性能骤降时，在适用域报告中标注需要CFD复核的工况范围
- **训练不收敛**：损失曲线振荡或发散时，降低学习率、增大早停耐心或检查数据质量

## 质量检查

- 数据审计：每个变量的统计分布合理性、缺失值比例、坐标系一致性
- 训练过程：损失曲线平滑性、验证集泛化间隙、梯度爆炸检测
- 推理结果：网格移动预测的物理合理性（网格不自交、边界保持、质量指标改善）
- 物理一致性：守恒方程残差量级、边界条件满足度、时间演化稳定性
- 适用域：训练分布覆盖度、OOD样本比例、最差样本的物理特征分析

## 回退策略

- 图神经网络不适用时：退化为传统CFD求解器（如OpenFOAM）的自适应网格移动模块
- 消息传递不稳定时：改用注意力机制（如Graph Attention Network）或增加消息传递轮数
- 网格移动开销过大时：使用多尺度图表示或分层图网络降低计算复杂度
- 训练数据不足时：采用迁移学习从预训练网格移动模型微调

## 资源召回建议

- 当用户提及"学习型网格移动""自适应有限元优化""Mesh movement network""Graph mesh optimizer""G-Adaptivity"时召回本卡
- 配套资源：cfd-learning-mesh-adaptive-fem-workflow（完整工作流）、cfd-mesh-data-intake-contract-validation（数据接入）、cfd-mesh-model-training-optimization（模型训练）
- 相关领域卡：cfd-dynamic-graph-adaptive-mesh-physics-simulation（动态图自适应网格模拟）、cfd-adaptive-mesh-inference（自适应网格推理）

## 证据来源

[1] "G-Adaptivity: optimised graph-based mesh relocation for finite element methods", 2024
[2] "Towards Universal Mesh Movement Networks", 2024
[3] 场景CFD_S030需求书定义
