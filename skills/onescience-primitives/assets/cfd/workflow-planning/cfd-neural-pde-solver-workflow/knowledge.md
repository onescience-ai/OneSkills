# 神经PDE求解器端到端工作流

## 适用范围

**触发条件**：
- 需要从原始动态图或拉格朗日粒子时序数据出发，构建可复现的神经PDE求解器
- 已有物理模拟数据集，需要完成从数据接入到适用域报告的完整流水线
- 需要标准化的工作流模板来组织多阶段的模型开发流程

**适用场景**：
- 消息传递神经PDE求解器的开发与验证
- 自适应网格GNN的训练与评估
- 物理场预测模型的工程化交付

**不适用场景**：
- 仅需训练或仅需推理的单阶段任务（对应单步task卡）
- 已有预训练模型只需微调的场景

## 输入

- **数据集路径**：包含动态图或拉格朗日粒子时序数据的目录
- **数据契约**：变量名、单位、坐标系、网格拓扑的结构化定义（可选，缺省时按数据集原生格式）
- **模型名称**：Message-passing neural PDE solver 或 Adaptive mesh GNN
- **训练配置**：超参数、随机种子、设备信息
- **验收指标**：统计与物理约束指标列表

## 输出

- **best_checkpoint.pt**：通过训练门限的最佳模型权重
- **train_config.json**：训练配置快照
- **training_metrics.csv**：逐轮训练验证指标
- **environment.txt**：代码版本与依赖信息
- **predictions/**：测试集逐样本预测结果
- **evaluation.json**：验收评估结果
- **worst_cases.csv**：最差样本详情
- **applicability_report.md**：适用域边界报告
- **PASS_REJECT_BLOCKED.txt**：最终验收结论

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取数据，核验样本数、变量、单位、坐标系、网格拓扑、时间范围、缺失值和使用许可
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **产出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分，完成归一化或无量纲化
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **产出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### Step 3：模型配置与训练
- **操作**：加载切分与统计量，训练消息传递PDE求解器或自适应网格GNN，记录逐轮指标与最佳权重
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **产出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：批量推理与物理恢复
- **操作**：在独立测试集上推理，反归一化并恢复原始单位、网格和物理派生量
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- **产出**：predictions/、inference_manifest.json、timing.csv

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益，执行外推测试并明确适用域
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **产出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Step依赖链 | s01→s02→s03→s04→s05 | [场景CFD_S020] | 线性依赖，每步依赖前一步产出 |
| 切分比例 | 0.7/0.15/0.15 | [场景CFD_S020] | 训练/验证/测试默认比例 |
| 分组策略 | geometry_or_trajectory | [场景CFD_S020] | 按几何或轨迹分组防泄漏 |
| 训练框架 | PyTorch | [场景CFD_S020] | 默认框架 |
| 默认epochs | 100 | [场景CFD_S020] | 最大训练轮数 |
| 默认batch_size | 8 | [场景CFD_S020] | 训练批大小 |
| 默认学习率 | 0.001 | [场景CFD_S020] | Adam优化器学习率 |
| 早停耐心 | 15 | [场景CFD_S020] | 验证loss不降的最大容忍轮数 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景CFD_S020] | 四项指标覆盖统计与物理约束 |
| 相对误差门限 | 0.1 | [场景CFD_S020] | 测试集PASS/REJECT阈值 |

## 边界与分流

- **数据缺失**：缺少必填输入时返回BLOCKED并列出缺项，不得编造数据
- **训练不收敛**：损失发散时回退检查数据质量和超参数配置
- **推理异常**：预测含NaN/Inf时排查数值稳定性问题（梯度爆炸、输入异常）
- **验收不通过**：REJECT时分析最差样本原因，决定是否需要重新训练或调整模型架构
- **域外工况**：外推测试性能骤降时明确适用域边界，标注需CFD复核的工况范围

## 质量检查

- 每个Step产出必须通过对应quality_gate才能进入下一步
- Step间数据契约传递的完整性校验
- 训练过程的梯度监控和数值稳定性检查
- 推理结果的物理合理性抽检
- 适用域报告的覆盖度验证

## 回退策略

- 数据质量不达标时回退到Step 1重新审计
- 训练失败时回退到Step 2检查切分和预处理
- 推理失败时回退到Step 3检查模型权重
- 验收失败时根据原因回退到对应步骤

## 资源召回建议

- 当用户需要从头构建神经PDE求解器完整流水线时召回本卡
- 配套单步任务卡：cfd-dynamic-graph-data-ingestion、cfd-lagrangian-particle-preprocessing、cfd-message-passing-pde-training、cfd-adaptive-mesh-inference、cfd-physics-consistency-validation
- 场景级卡：cfd-dynamic-graph-adaptive-mesh-physics-simulation

## 证据来源

[1] "EvoMesh: Adaptive Physical Simulation with Hierarchical Graph Evolutions", 2024
[2] "Message Passing Neural PDE Solvers", arXiv:2202.03376, 2022
[3] "Breaking the Discretization Barrier of Continuous Physics Simulation Learning", arXiv:2509.17955, 2025
