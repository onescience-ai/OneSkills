# 边界嵌入与任意阶硬约束神经场求解——完整工作流

## 适用范围

**触发条件**：
- 需要在复杂几何边界上用神经算子求解PDE，且要求精确满足边界条件（Dirichlet、Neumann、Robin或混合边界）
- 已有混合边界与复杂域PDE数据，需要学习算子映射并保持物理一致性

**适用场景**：
- 计算流体力学中复杂几何边界的Navier-Stokes方程求解
- 非结构化网格或无网格点云上的PDE神经算子学习
- 需要在推理阶段精确满足任意阶边界条件的物理一致性预测
- 跨几何形状的流场泛化预测（外推需CFD复核）

**不适用场景**：
- 规则网格上的简单PDE问题（应使用FNO等标准算子）
- 仅关注统计误差、不要求精确边界满足的纯数据驱动回归
- 边界条件随时间剧烈变化的瞬态问题（需特殊处理）

## 输入

- 混合边界与复杂域PDE数据：几何坐标、边界条件类型、PDE方程、初始条件
- 数据契约：变量单位、网格拓扑、时间或工况范围、使用许可
- 目标变量：待预测的物理量（压力、速度、温度等）

## 输出

- dataset_manifest.json、data_contract.json、data_audit.md（数据接入阶段）
- train/validation/test manifest、normalization.json（预处理阶段）
- best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt（训练阶段）
- predictions/、inference_manifest.json、timing.csv（推理阶段）
- evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt（验收阶段）

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取混合边界与复杂域PDE数据，检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可
- **参数**：数据集路径、数据集名称、数据契约模板
- **工具**：Python文件I/O、JSON解析
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **缺项处理**：缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，按几何、工况或时间构造无泄漏切分，保存统计量与可逆变换
- **参数**：切分配置（train/val/test比例、种子、分组方式）、目标变量列表、是否无量纲化
- **工具**：归一化工具、数据切分工具
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：加载切分数据与统计量，配置并训练Boundary-embedded neural operator、Hard-constraint neural field，记录训练过程
- **参数**：模型名称、训练配置（框架、epochs、batch_size、learning_rate、seed、early_stopping_patience）、可选初始权重
- **工具**：PyTorch、神经算子库
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：批量推理与物理恢复
- **操作**：在独立测试集上推理，反归一化恢复物理单位、坐标网格、边界掩膜及任务派生量
- **参数**：模型权重路径、计算设备、推理批大小
- **工具**：PyTorch推理、数据逆变换
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### Step 5：任务验收与适用域判定
- **操作**：按验收指标评价结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本；执行几何或工况外推测试并明确适用域
- **参数**：验收指标列表、相对误差门限、是否外推测试
- **工具**：误差计算、边界误差计算、可视化工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | Boundary-Embedded Neural Operator, Hard-Constraint Neural Field | [场景需求书] | 要求精确满足边界条件，支持任意阶微分约束 |
| 数据格式 | 混合边界与复杂域PDE数据 | [场景需求书] | 包含几何坐标、边界条件类型、PDE方程 |
| 边界约束 | 硬约束（精确满足） | [场景需求书] | 非软约束近似，边界条件必须精确满足 |
| 切分方式 | 按几何、工况或时间为单位 | [场景需求书] | 不得把同一轨迹的帧随机打散 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书] | 统计和物理指标联合评估 |
| 外推测试 | 几何或工况外推 | [场景需求书] | 不得仅凭平均误差宣称工程可用 |

### 校准数值（体系专属）

> 以下数值来自CFD_S064场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| epochs | 100 | 场景需求书 | 默认训练轮数 |
| batch_size | 8 | 场景需求书 | 默认批量大小 |
| learning_rate | 0.001 | 场景需求书 | 默认学习率 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| train比例 | 0.7 | 场景需求书 | 默认训练集比例 |
| validation比例 | 0.15 | 场景需求书 | 默认验证集比例 |
| test比例 | 0.15 | 场景需求书 | 默认测试集比例 |
| random_seed | 42 | 场景需求书 | 随机种子 |
| MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 默认相对误差门限 |

## 边界与分流

- **数据不可读或不完整**：返回BLOCKED并列出缺项，不得编造数据；补充数据后重试
- **边界条件难以硬约束**：检查边界嵌入机制设计，必要时调整网络架构或使用软约束作为对比
- **训练不收敛**：调整学习率、批量大小或网络容量；考虑预训练权重初始化
- **域外工况预测偏差大**：明确标注适用域限制，建议CFD复核；不扩大适用范围
- **计算资源不足**：降低批量大小或使用混合精度训练

## 质量检查

- **数据接入阶段**：数据文件可读、样本可追溯、变量单位完整、无训练测试泄漏
- **预处理阶段**：切分互斥、变换统计量仅来自训练集、边界语义完整
- **训练阶段**：损失有限、权重可加载、可复现
- **推理阶段**：预测无异常值、形状正确、未使用测试标签
- **验收阶段**：统计与物理指标同时报告、最差样本可追溯、结论含适用域与复核建议

## 回退策略

- **数据接入失败**：请求用户提供完整数据或补充信息
- **边界约束设计困难**：参考BENO或Hard-Constraint Neural Field的边界嵌入构造方法
- **训练失败**：使用简化网络架构或标准神经算子作为baseline对比
- **评估不通过**：重新审查数据质量、模型架构或超参数配置

## 资源召回建议

- 当用户需要在复杂几何边界上用神经算子求解PDE且要求精确满足边界条件时召回本卡
- 配套资源：
  - `cfd-boundary-embedded-arbitrary-order-hard-constraint-neural-field-workflow`：完整工作流卡片
  - `cfd-boundary-embedded-neural-operator-data-intake-contract-validation`：数据接入任务卡
  - `cfd-boundary-embedded-neural-operator-preprocessing-data-splitting`：预处理任务卡
  - `cfd-boundary-embedded-neural-operator-model-training`：模型训练任务卡
  - `cfd-boundary-embedded-neural-operator-batch-inference-physical-recovery`：推理任务卡
  - `cfd-boundary-embedded-neural-operator-acceptance-applicability`：验收任务卡

## 证据来源

[1] BENO: Boundary-Embedded Neural Operators for PDEs, 2024
[2] Harnessing the Power of Neural Operators with Automatically Encoded Conservation Laws, 2024
[3] Scaling Physics-Informed Hard Constraints with Mixture-of-Experts, 2024
[4] Neural Fields with Hard Constraints of Arbitrary Differential Order, 2024
[5] Physics-Embedded Neural Networks: Graph Neural PDE Solvers with Mixed Boundary Conditions, 2024
[6] 场景需求书CFD_S064：边界嵌入与任意阶硬约束神经场求解，workflow步骤定义
