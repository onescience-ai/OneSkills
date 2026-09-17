# 高超声速与跨声速边界层湍流代理工作流

## 适用范围

本工作流描述从高保真CFD数据构建数据驱动湍流代理模型的完整流程，适用于高超声速冷壁边界层与跨声速机翼场景。工作流包含五个核心步骤，从数据接入到适用域判定，确保模型的可复现性和物理一致性。

## 输入

- **高超声速冷壁CFD数据**：边界层速度剖面、温度剖面、湍流量
- **跨声速机翼CFD数据**：压力分布、激波位置、分离区域信息
- **数据契约**：变量定义、单位、坐标系、网格拓扑
- **物理约束**：湍流可实现性、能量守恒、边界条件

## 输出

- **可复现模型**：训练好的代理模型权重和配置
- **任务结果**：闭合项预测、后验流场
- **物理一致性评估**：统计误差、物理约束满足度
- **适用域报告**：模型泛化能力、域外工况说明

## 流程节点

```
s01: 数据接入与契约核验 → s02: 预处理与数据切分 → s03: 模型配置与训练 → s04: 闭合项预测与后验CFD耦合 → s05: 任务验收与适用域判定
```

### s01: 数据接入与契约核验

**操作**：接入高超声速冷壁与跨声速机翼CFD数据，核验样本、变量、单位、网格坐标及许可

**输入**：
- {DATASET_PATH}: 数据集路径（必填）
- {DATASET_NAME}: 数据集名称（必填，默认"高超声速冷壁与跨声速机翼CFD数据"）
- {DATA_CONTRACT}: 数据契约（可选，默认空契约）

**输出**：
- dataset_manifest.json
- data_contract.json
- data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**依赖**：无（起始步骤）

### s02: 预处理与数据切分

**操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分

**输入**：
- {SPLIT_CONFIG}: 切分配置（必填，默认train:0.7, val:0.15, test:0.15, seed:42, group_by: geometry_or_trajectory）
- {TARGET_FIELDS}: 目标变量（必填）
- {NONDIMENSIONALIZE}: 是否无量纲化（可选，默认true）

**输出**：
- train_manifest.json
- validation_manifest.json
- test_manifest.json
- normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**依赖**：s01

### s03: 模型配置与训练

**操作**：训练Transformer aerodynamic surrogate、Neural turbulence model完成指定输入到目标物理量的映射

**输入**：
- {MODEL_NAME}: 模型名称（必填，默认"Transformer aerodynamic surrogate、Neural turbulence model"）
- {TRAIN_CONFIG}: 训练配置（必填，默认framework: PyTorch, epochs: 100, batch_size: 8, learning_rate: 0.001, seed: 42, early_stopping_patience: 15）
- {INIT_CHECKPOINT}: 初始权重（可选）

**输出**：
- best_checkpoint.pt
- train_config.json
- training_metrics.csv
- environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**依赖**：s02

### s04: 闭合项预测与后验CFD耦合

**操作**：先验评估闭合项，再嵌入RANS或LES执行稳定后验推进

**输入**：
- {CHECKPOINT}: 模型权重（必填，默认best_checkpoint.pt）
- {DEVICE}: 计算设备（必填，默认cuda）
- {BATCH_SIZE}: 推理批大小（可选，默认8）

**输出**：
- apriori_closure/
- aposteriori_fields/
- solver_stability.csv

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

**依赖**：s03

### s05: 任务验收与适用域判定

**操作**：评估统计误差、关键物理约束、泛化能力和计算收益

**输入**：
- {METRICS}: 验收指标（必填，默认["closure_RMSE", "mean_profile_error", "spectrum_error", "stability_horizon"]）
- {MAX_RELATIVE_L2}: 相对误差门限（可选，默认0.1）
- {RUN_OOD_TEST}: 是否外推测试（可选，默认true）

**输出**：
- evaluation.json
- worst_cases.csv
- applicability_report.md
- PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**依赖**：s04

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
- 用户需要执行数据驱动湍流代理模型的完整工作流
- 场景涉及高超声速或跨声速边界层CFD
- 需要从数据接入到适用域判定的端到端流程

**配套资源**：
- cfd-hypersonic-transonic-turbulence-surrogate-scenario: 场景级概述
- cfd-hypersonic-transonic-data-integration-task: 数据接入与核验
- cfd-hypersonic-transonic-preprocessing-task: 预处理与切分
- cfd-hypersonic-transonic-model-training-task: 模型配置与训练
- cfd-hypersonic-transonic-posteriori-validation-task: 后验耦合验证
- cfd-hypersonic-transonic-acceptance-task: 任务验收与适用域判定

## 证据来源

[1] Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers, arXiv:2406.17446, 2024
[2] Scalable Transformer for PDE Surrogate Modeling, arXiv:2209.04934, 2022
