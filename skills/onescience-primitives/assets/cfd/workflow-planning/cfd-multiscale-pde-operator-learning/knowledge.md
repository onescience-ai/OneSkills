# 多尺度PDE场数据算子学习

## 适用范围

**触发条件**：
- 需要从多尺度高频PDE场数据学习输入到输出的映射关系
- 需要构建PDE系统的神经算子代理模型
- 需要处理包含多尺度特征的物理场数据（如湍流、多相流、波动问题）

**适用场景**：
- 流体动力学中的湍流模拟与预测
- 多相流界面追踪与演化模拟
- 电磁场、弹性场等多物理场耦合问题
- 高频振荡PDE场的快速求解
- 需要物理一致性保证的工程代理建模

**不适用场景**：
- 低频光滑PDE场（传统数值方法更高效）
- 无空间/时间结构的纯代数问题
- 纯数据驱动无物理约束的回归任务
- 域外工况未经CFD复核直接工程应用

## 输入

**数据格式**：
- 多尺度PDE场数据：包含空间坐标(x,y,z)、时间(t)、物理量场(u,v,w,p,T等)
- 支持结构化网格（规则网格）与非结构化网格（图构建）
- 输入字段与目标字段需明确定义，单位统一

**预处理要求**：
- 单位统一与无量纲化处理
- 几何/工况/时间序列切分，避免训练测试泄漏
- 边界掩膜与缺失值处理
- 归一化统计量仅从训练集计算

## 输出

**产物清单**：
- 可复现模型权重（best_checkpoint.pt）
- 训练配置与环境记录（train_config.json, environment.txt）
- 逐轮训练验证指标（training_metrics.csv）
- 测试集推理结果与物理恢复产物（predictions/, inference_manifest.json）
- 统计误差与物理约束评估报告（evaluation.json, applicability_report.md）
- 适用域判定与复核建议（PASS_REJECT_BLOCKED.txt）

**验证标准**：
- 相对L2误差 ≤ 0.1（默认门限）
- 守恒残差与边界误差满足物理约束
- 最差样本可追溯
- 域外工况需经CFD复核

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取多尺度PDE场数据，建立数据清单，核验样本、变量、单位、网格坐标及许可
- **输入**：数据集路径、数据集名称、数据契约
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **输入**：切分配置、目标变量、是否无量纲化
- **输出**：train/val/test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：训练Wavelet Neural Operator、Localized-kernel operator完成指定输入到目标物理量的映射
- **输入**：模型名称、训练配置、可选初始权重
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：批量推理与物理恢复
- **操作**：在独立测试集推理，恢复原始单位、网格和物理派生量
- **输入**：模型权重、计算设备、推理批大小
- **输出**：predictions/, inference_manifest.json, timing.csv
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **输入**：验收指标、相对误差门限、是否外推测试
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差门限 | ≤ 0.1 | [场景S055] | 测试集放行阈值 |
| 守恒残差 | 满足物理方程约束 | [场景S055] | 方程残差评估 |
| 边界误差 | 满足边界条件约束 | [场景S055] | 边界条件一致性 |
| 训练框架 | PyTorch | [场景S055] | 默认深度学习框架 |

### 校准数值（场景S055专属，其他体系需重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认epochs | 100 | [场景S055] | 训练轮数 |
| 默认batch_size | 8 | [场景S055] | 批大小 |
| 默认learning_rate | 0.001 | [场景S055] | 学习率 |
| 默认early_stopping_patience | 15 | [场景S055] | 早停耐心 |
| 数据切分比例 | train:0.7, val:0.15, test:0.15 | [场景S055] | 数据集划分 |

## 边界与分流

**关键前提与改道**：
1. 若数据非多尺度高频PDE场 → 转向传统数值方法或浅层模型
2. 若缺乏物理约束需求 → 转向纯数据驱动的神经网络
3. 若计算资源有限 → 降级为简化模型或小规模数据实验
4. 若域外工况无法CFD复核 → 限制适用范围，标注不确定性

## 质量检查

**验证点**：
- 数据完整性：样本数、变量、单位、坐标定义完整
- 切分有效性：训练/验证/测试集无泄漏
- 模型收敛性：训练验证损失有限且可复现
- 物理一致性：守恒残差、边界误差满足约束
- 适用域明确：最差样本可追溯，结论含限制说明

## 回退策略

**失败替代方案**：
- 数据质量不足 → 降级为小规模实验或合成数据验证
- 模型不收敛 → 调整超参数或更换模型架构
- 物理约束不满足 → 增加物理正则化项或调整损失函数
- 适用域过窄 → 明确标注限制，建议CFD复核

## 资源召回建议

**何时召回**：
- 需要构建PDE系统的神经算子代理模型时
- 面对多尺度高频PDE场数据需要快速求解时
- 需要物理一致性保证的工程代理建模场景

**配套资源**：
- Wavelet Neural Operator实现
- Localized-kernel Operator实现
- 数据预处理与切分工具
- 物理一致性评估工具

## 证据来源

[1] Multiwavelet-based Operator Learning for Differential Equations, arXiv:2109.13459, 2021
[2] DRIFT-Net: A Spectral-Coupled Neural Operator for PDEs Learning, 2024
[3] Neural Operators with Localized Integral and Differential Kernels, 2023
[4] Gaussian Plane-Wave Neural Operator for Electron Density Estimation, 2024
[5] Learning High-Frequency Functions Made Easy with Sinusoidal Positional Encoding, 2023
[6] Spectral-Embedded Operator Learning for Three-Phase Interfacial Flow, arXiv:2608.29069, 2026
