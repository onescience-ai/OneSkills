# 高超声速与跨声速边界层湍流代理场景

## 适用范围

本卡片描述数据驱动湍流代理模型的构建流程，适用于高超声速冷壁边界层与跨声速机翼CFD场景。目标是从高保真CFD数据（DNS/LES）中学习湍流闭合项映射，构建可嵌入RANS/LES求解器的代理模型，实现湍流效应的快速预测。

**适用场景**：
- 高超声速冷壁边界层湍流建模
- 跨声速机翼CFD数据驱动设计
- 湍流闭合项数据驱动替代
- 需要物理一致性约束的代理模型构建

**不适用场景**：
- 低速不可压缩流动（需重新定义变量和约束）
- 完全发展的各向同性湍流（无边界层效应）
- 域外工况需经CFD复核验证

## 输入

- **高超声速冷壁CFD数据**：包含边界层速度剖面、温度剖面、湍流量（k, ε, ω等）
- **跨声速机翼CFD数据**：包含压力分布、激波位置、分离区域信息
- **数据契约**：变量定义、单位、坐标系、网格拓扑
- **物理约束**：湍流可实现性、能量守恒、边界条件

## 输出

- **可复现模型**：训练好的代理模型权重和配置
- **任务结果**：闭合项预测、后验流场
- **物理一致性评估**：统计误差、物理约束满足度
- **适用域报告**：模型泛化能力、域外工况说明

## 流程节点

```
数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 闭合项预测与后验CFD耦合 → 任务验收与适用域判定
```

### 流程节点 1: 数据接入与契约核验

**操作**：接入高超声速冷壁与跨声速机翼CFD数据，核验样本、变量、单位、网格坐标及许可

**参数**：
- {DATASET_PATH}: 数据集路径
- {DATASET_NAME}: 数据集名称
- {DATA_CONTRACT}: 数据契约（变量、单位、网格定义）

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

### 流程节点 2: 预处理与数据切分

**操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分

**参数**：
- {SPLIT_CONFIG}: 切分配置（train/val/test比例，按对象工况切分）
- {TARGET_FIELDS}: 目标变量
- {NONDIMENSIONALIZE}: 是否无量纲化

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

### 流程节点 3: 模型配置与训练

**操作**：训练Transformer aerodynamic surrogate、Neural turbulence model完成指定输入到目标物理量的映射

**参数**：
- {MODEL_NAME}: 模型名称（默认Transformer aerodynamic surrogate、Neural turbulence model）
- {TRAIN_CONFIG}: 训练配置（框架、epochs、batch_size、learning_rate、seed）
- {INIT_CHECKPOINT}: 初始权重（可选）

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

### 流程节点 4: 闭合项预测与后验CFD耦合

**操作**：先验评估闭合项，再嵌入RANS或LES执行稳定后验推进

**参数**：
- {CHECKPOINT}: 模型权重
- {DEVICE}: 计算设备（CPU/CUDA）
- {BATCH_SIZE}: 推理批大小

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

### 流程节点 5: 任务验收与适用域判定

**操作**：评估统计误差、关键物理约束、泛化能力和计算收益

**参数**：
- {METRICS}: 验收指标（closure_RMSE、mean_profile_error、spectrum_error、stability_horizon）
- {MAX_RELATIVE_L2}: 相对误差门限（默认0.1）
- {RUN_OOD_TEST}: 是否外推测试

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书s02] | 按对象工况切分，无泄漏 |
| 无量纲化 | true | [场景需求书s02] | 统一跨工况量纲 |
| 训练框架 | PyTorch | [场景需求书s03] | 默认框架 |
| 相对误差门限 | 0.1 | [场景需求书s05] | 测试集放行阈值 |
| 验收指标 | closure_RMSE, mean_profile_error, spectrum_error, stability_horizon | [场景需求书s05] | 统计与物理指标 |

### 校准数值（体系专属值）

以下数值来自高超声速冷壁与跨声速机翼CFD体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Transformer aerodynamic surrogate, Neural turbulence model | [场景需求书s03] | 数据驱动湍流代理模型 |
| 训练轮数 | 100 | [场景需求书s03] | 默认epochs |
| 批大小 | 8 | [场景需求书s03] | 默认batch_size |
| 学习率 | 0.001 | [场景需求书s03] | 默认learning_rate |
| 早停耐心 | 15 | [场景需求书s03] | early_stopping_patience |

## 边界与分流

**关键前提与分流策略**：

1. **前提：数据可用性**
   - 不成立时：若缺少高保真CFD数据，需降级为经验模型或文献数据合成
   - 分流目标：使用DNS/LES公开数据集或文献报告的统计剖面

2. **前提：物理约束可定义**
   - 不成立时：若湍流可实现性约束难以形式化，需简化约束或采用软约束
   - 分流目标：使用物理信息神经网络（PINN）的软约束方法

3. **前提：域外工况可识别**
   - 不成立时：若无法准确定义适用域边界，需增加安全裕度
   - 分流目标：在适用域报告中明确标注复核建议

4. **前提：后验耦合稳定性**
   - 不成立时：若代理模型导致求解器发散，需回退为先验评估
   - 分流目标：仅报告先验误差和可实现性检查结果

## 质量检查

**验证点**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散

**阈值**：
- 相对误差门限：0.1（测试集放行）
- 物理约束：湍流可实现性、能量守恒

**失败处理**：
- 数据质量问题：返回BLOCKED并列出缺项
- 训练失败：检查配置、数据、模型结构
- 后验发散：回退为先验评估

## 回退策略

1. **数据不足**：使用公开DNS/LES数据集或文献统计剖面
2. **模型不收敛**：调整超参数、检查数据质量、简化模型结构
3. **后验不稳定**：仅报告先验误差，不进行耦合验证
4. **适用域不明**：增加安全裕度，明确标注复核建议

## 资源召回建议

**何时应召回本卡片**：
- 用户需要构建数据驱动的湍流代理模型
- 场景涉及高超声速或跨声速边界层CFD
- 需要物理一致性约束的代理模型
- 需要评估模型泛化能力和适用域

**配套资源**：
- cfd-hypersonic-transonic-turbulence-surrogate-workflow: 工作流详细步骤
- cfd-hypersonic-transonic-data-integration-task: 数据接入与核验
- cfd-hypersonic-transonic-preprocessing-task: 预处理与切分
- cfd-hypersonic-transonic-model-training-task: 模型配置与训练
- cfd-hypersonic-transonic-posteriori-validation-task: 后验耦合验证
- cfd-hypersonic-transonic-acceptance-task: 任务验收与适用域判定

## 证据来源

[1] Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers, arXiv:2406.17446, 2024
[2] Scalable Transformer for PDE Surrogate Modeling, arXiv:2209.04934, 2022
[3] SuperWing_ a comprehensive transonic wing dataset for data-driven aerodynamic design, arXiv:2512.14397, 2025
[4] SMART_ Scalable Mesh-free Aerodynamic Simulations from Raw Geometries using a Transformer-based Surrogate Model, arXiv:2601.18707, 2026
[5] Gaussian processes at the Helm(holtz)_ A more fluid model for ocean currents (参考)
[6] Aeroelastic Reduced-Order Model Differential Equations in Transonic Buffeting Flow, arXiv:2510.22216, 2025
[7] Compact representation of transonic airfoil buffet flows with observable-augmented machine learning, arXiv:2509.17306, 2025
[8] Neural Differential Equations for Oscillatory Flows in Aeroelasticity Applied to Transonic Buffet, arXiv:2607.22402, 2026
