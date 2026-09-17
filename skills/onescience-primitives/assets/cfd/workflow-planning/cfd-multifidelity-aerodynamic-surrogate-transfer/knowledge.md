# 多保真气动代理迁移建模

## 适用范围

**触发条件**：
- 需要将已在源几何族（如某一车型系列）上训练的气动代理模型迁移到拓扑结构不同的新几何族
- 高保真（HF）RANS/LES 数据在目标几何族上极为稀缺（通常少于 50 个工况）
- 需要同时利用低保真（LF）廉价数据提升预测精度并量化不确定性

**适用场景**：
- 汽车外部空气动力学：跨车型系列的力/力矩与表面压力预测
- 航空翼型/机身设计：从已有翼型族迁移到新翼型族
- 多保真数据融合：结合 RANS 与 LES 或风洞实验数据
- 域外工况检测与适用域报告生成

**不适用场景**：
- 单一几何族内工况外推（无几何拓扑变化）
- 纯数据驱动、无物理约束的黑盒代理（缺少闭合项校验）
- 实时在线学习场景（本框架面向离线训练与部署）

## 输入

- **数据集**：跨几何族多保真 RANS 数据，包含几何参数、流场变量（速度、压力、湍流量）、网格坐标、工况条件
- **数据契约**：变量名、单位、坐标系定义（dataset_native 或标准化坐标）、网格拓扑类型
- **预处理要求**：按几何族/轨迹/工况无泄漏切分；统计量仅从训练集计算；边界与掩膜语义保持完整
- **可选预训练权重**：源几何族上已训练的代理模型 checkpoint

## 输出

- **可复现模型**：最优权重文件（best_checkpoint.pt）、训练配置（train_config.json）、训练指标（training_metrics.csv）
- **预测结果**：闭合项先验评估（apriori_closure/）、后验流场（aposteriori_fields/）
- **评估报告**：逐变量误差（evaluation.json）、最差样本追溯（worst_cases.csv）、适用域报告（applicability_report.md）
- **验收结论**：PASS / REJECT / BLOCKED 判定

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取数据集，核验文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、缺失值与使用许可
- **参数**：DATASET_PATH, DATASET_NAME, DATA_CONTRACT（变量/单位/网格定义）
- **工具**：数据清单生成脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，按几何族/轨迹/工况构造无泄漏切分，执行归一化或无量纲化
- **参数**：SPLIT_CONFIG（train/val/test 比例、group_by 策略）、TARGET_FIELDS、NONDIMENSIONALIZE
- **工具**：数据预处理脚本
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：加载预训练权重（可选），配置迁移学习策略（LoRA / 全量微调 / 轻量微调），训练代理模型
- **参数**：MODEL_NAME（Transfer-learning surrogate / Gaussian functional regressor）、TRAIN_CONFIG（框架/轮次/批大小/学习率/随机种子/早停）
- **工具**：PyTorch 训练框架
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：闭合项预测与后验 CFD 耦合
- **操作**：加载最优权重预测应力/通量/源项，先在独立快照上做先验误差和可实现性检查，再嵌入 RANS 或 LES 求解器执行后验推进
- **参数**：CHECKPOINT, DEVICE, BATCH_SIZE
- **工具**：RANS/LES 求解器（如 OpenFOAM）
- **质量门禁**：闭合张量或通量满足约束；后验求解无非物理解和发散；均值剖面与能谱均经验证

### Step 5：任务验收与适用域判定
- **操作**：按验收指标（closure_RMSE、mean_profile_error、spectrum_error、stability_horizon）评价结果，执行几何或工况外推测试
- **参数**：METRICS, MAX_RELATIVE_L2（默认 0.1）、RUN_OOD_TEST
- **工具**：评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 迁移学习策略 | LoRA 优于 FFT 和 LFT | [1] | LoRA 在几何迁移中收敛性最优，R²=0.85±0.02 |
| 目标域最小样本 | 20–50 个工况 | [1] | LoRA 从 20 样本即可达到可接受精度 |
| 相对误差门限 | L₂ < 0.1（PASS） | [5] | 表面压力相对 L₂ 误差 0.089 为可接受水平 |
| 不确定性覆盖率 | >95% | [2] | Multi-Split Conformal Prediction 逐点覆盖 |
| 闭合张量约束 | 物理可实现性检查 | [4] | 应力/通量须满足正定性或散度约束 |
| 后验稳定性 | 无发散、残差收敛 | [3] | 嵌入求解器后须验证统计稳定 |

### 校准数值（特定体系参考值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AB-UPT 模型参数量 | 61.47M | [1] | Transformer 代理，4 家族 411 工况预训练 |
| LoRA 迁移 R² | 0.85±0.02 | [1] | 5 家族 leave-one-out 实验 |
| LoRA vs FFT 力 RMSE 改善 | 50% | [1] | 相对全量微调降低力预测误差 |
| LoRA vs FFT 场误差改善 | 28% | [1] | 逐点流场预测改善 |
| RETO DrivAerML 表面压力 L₂ | 0.089 | [5] | Rotary-enhanced transformer 基准值 |
| RETO DrivAerML 速度 L₂ | 0.097 | [5] | 速度场预测基准值 |
| 2D→3D GFR 适应加速 | 百万倍 | [3] | 神经网络加速核 vs 标准核 |

## 边界与分流

- **源域与目标域几何拓扑差异过大**：LoRA 等参数高效微调仍无法收敛时，需回退到多保真数据融合路径（自编码器潜空间对齐 + 少量 HF 样本微调解码器）[2]
- **高保真数据完全缺失**：仅能执行先验闭合项评估（Step 4 的 apriori 部分），跳过后验 CFD 耦合，结论标记为 BLOCKED
- **后验 CFD 求解发散**：检查闭合项可实现性约束，回退到纯数据驱动代理（无物理耦合）或调整求解器时间步/松弛因子
- **域外工况误差超标**：在适用域报告中明确标注域外边界，建议对该区域进行 CFD 复核而非直接工程部署
- **模型结构不兼容预训练权重**：结构检查失败时从头训练，但需更多目标域数据

## 质量检查

- **统计指标**：逐变量 RMSE、相对 L₂ 误差、最差样本误差
- **物理指标**：闭合张量正定性/散度约束、能谱匹配度、边界层剖面一致性
- **泛化评估**：几何外推（新车型/翼型族）、工况外推（新雷诺数/攻角范围）
- **计算效率**：推理时间与 CFD 直接求解的加速比
- **可复现性**：随机种子、依赖版本、训练配置全部记录

## 回退策略

- 迁移学习失败 → 多保真融合（自编码器 + 少量 HF 微调）
- 多保真融合失败 → 纯数据驱动代理（增加训练数据采集）
- 后验耦合不稳定 → 仅提供先验评估 + 适用域声明
- 所有路径失败 → 输出 BLOCKED 并列出数据缺口

## 资源召回建议

- 当用户需要跨几何族构建气动代理时召回本卡
- 配套资源：cfd-surrogate-validation-pipeline（完整验证工作流）、cfd-surrogate-transfer-learning-adaptation（迁移学习策略细节）
- 当数据为单一几何族时，参考 cfd-surrogate-validation-pipeline 中不涉及迁移的部分

## 证据来源

[1] Keum, Warey, "Adapting Automotive Aerodynamics Surrogates to New Vehicle Families via Transfer Learning", arXiv:2605.27968, 2026
[2] Nieto-Centenero, Andrés, Castellanos, "Multi-fidelity aerodynamic data fusion by autoencoder transfer learning", arXiv:2512.13069, 2025
[3] Lao, Scott, Bui-Thanh, Laiu, Bement, "Dimension Bridging for 3D RANS with Neural Network Accelerated Gaussian Functional Regression", arXiv:2608.27639, 2026
[4] Li, Chen, Gao, Zhou, Sun, Xiang, Huang, "From Fixed Grids to Moving Particles: A Transferable Latent Operator for Fluid Dynamics", arXiv:2608.14120, 2026
[5] Zhang, Yang, Wang, Chen, Bin, Zhang, Wang, "RETO: A Rotary-Enhanced Transformer Operator for High-Fidelity Prediction of Automotive Aerodynamics", arXiv:2605.00062, 2026
