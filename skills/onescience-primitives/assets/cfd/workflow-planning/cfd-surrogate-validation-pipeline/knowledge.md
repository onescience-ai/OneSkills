# 气动代理模型端到端验证工作流

## 适用范围

**触发条件**：
- 需要对已训练或待训练的 CFD 代理模型执行完整验证流程
- 需要从数据接入到适用域判定的结构化质量保障
- 代理模型输出需与物理约束（守恒律、闭合项可实现性）进行交叉校验

**适用场景**：
- 汽车/航空外部空气动力学代理的训练与验证
- 多保真数据融合后模型的端到端评估
- 迁移学习后目标域代理的验收评估
- 代理模型部署前的适用域边界划定

**不适用场景**：
- 纯数值实验后处理（不涉及代理训练）
- 实时在线学习与自适应更新
- 无需物理耦合验证的纯数据驱动回归任务

## 输入

- **数据集**：已通过数据契约核验的结构化流场数据（含几何参数、流场变量、网格信息、工况条件）
- **数据契约**：变量名、单位、坐标系、网格拓扑定义
- **切分配置**：train/val/test 比例、group_by 策略（按几何族/轨迹/工况分组）
- **训练配置**：框架、轮次、批大小、学习率、随机种子、早停策略
- **可选预训练权重**：源域 checkpoint

## 输出

- **训练产物**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt
- **预测产物**：apriori_closure/（先验闭合项）、aposteriori_fields/（后验流场）、solver_stability.csv
- **评估产物**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取数据集路径，生成数据清单（dataset_manifest.json），输出机器可读契约（data_contract.json），生成审计报告（data_audit.md）
- **参数**：DATASET_PATH, DATASET_NAME, DATA_CONTRACT
- **工具**：数据清单生成脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **BLOCKED 条件**：缺少必填输入时返回 BLOCKED 并列出缺项

### Step 2：预处理与数据切分
- **操作**：依据数据契约完成质控、重采样或图构建、掩膜、归一化或无量纲化；按 group_by 策略构造无泄漏切分
- **参数**：SPLIT_CONFIG（train=0.7, val=0.15, test=0.15, seed=42, group_by=geometry_or_trajectory）、TARGET_FIELDS、NONDIMENSIONALIZE
- **工具**：数据预处理脚本
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：加载切分数据与统计量，配置模型超参数，执行训练并记录逐轮指标，保存最佳权重
- **参数**：MODEL_NAME, TRAIN_CONFIG（PyTorch, epochs=100, batch_size=8, lr=0.001, seed=42, early_stopping_patience=15）、INIT_CHECKPOINT（可选）
- **工具**：PyTorch 训练框架
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：闭合项预测与后验 CFD 耦合
- **操作**：加载最优权重预测应力/通量/源项；在独立快照上执行先验误差和可实现性检查；嵌入 RANS 或 LES 求解器执行后验推进；保存残差、能谱、统计剖面与稳定性记录
- **参数**：CHECKPOINT, DEVICE, BATCH_SIZE
- **工具**：RANS/LES 求解器
- **质量门禁**：闭合张量或通量满足约束；后验求解无非物理解和发散；均值剖面与能谱均经验证

### Step 5：任务验收与适用域判定
- **操作**：按验收指标（closure_RMSE、mean_profile_error、spectrum_error、stability_horizon）逐变量评估；执行几何或工况外推测试；输出 PASS/REJECT/BLOCKED 结论
- **参数**：METRICS, MAX_RELATIVE_L2=0.1, RUN_OOD_TEST=true
- **工具**：评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:val:test = 70:15:15 | 场景契约 | 标准比例，可按数据量调整 |
| 分组策略 | 按几何族或轨迹分组 | [1] | 防止同一对象帧泄漏 |
| 相对 L₂ 门限 | < 0.1（PASS） | [5] | DrivAerML 基准上可接受水平 |
| 不确定性覆盖率 | > 95% | [2] | MSCP 逐点覆盖保证 |
| 早停耐心 | 15 轮 | 场景契约 | 防止过拟合 |
| 随机种子 | 42 | 场景契约 | 保证可复现性 |

### 校准数值（特定体系参考值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ShapeNet RETO L₂ | 0.063 | [5] | 表面压力相对误差 |
| DrivAerML RETO 压力 L₂ | 0.089 | [5] | 表面压力预测 |
| DrivAerML RETO 速度 L₂ | 0.097 | [5] | 速度场预测 |
| AB-UPT FFT R² | 0.40 | [1] | 全量微调 20 样本过拟合 |
| AB-UPT LoRA R² | 0.85±0.02 | [1] | LoRA 迁移最优 |
| NACA 2D MF 覆盖率 | > 95% | [2] | 自编码器融合 + MSCP |

## 边界与分流

- **数据契约不完整**：返回 BLOCKED，列出缺失字段（变量名、单位、坐标系），不得编造数据
- **切分泄漏检测失败**：回退到更保守的分组策略（如按完整轨迹分组而非按帧）
- **训练损失非有限值**：检查数值稳定性（梯度爆炸/NaN），调整学习率或增加正则化
- **后验 CFD 发散**：检查闭合项约束 → 调整求解器参数 → 回退到仅先验评估
- **域外测试误差超标**：在适用域报告中明确标注域外边界，建议 CFD 复核而非直接部署

## 质量检查

- **数据完整性**：样本可追溯、变量完整、无泄漏
- **训练稳定性**：损失收敛、权重可加载、随机种子可复现
- **物理一致性**：闭合项约束、能谱匹配、边界层剖面
- **泛化能力**：几何外推、工况外推、最差样本分析
- **计算效率**：推理加速比、训练时间

## 回退策略

- 训练失败 → 增加数据量或降低模型复杂度
- 后验耦合不稳定 → 仅提供先验评估 + 适用域声明
- 物理约束不满足 → 调整闭合项裁剪/投影策略
- 所有路径失败 → BLOCKED + 数据缺口清单

## 资源召回建议

- 当用户需要验证 CFD 代理模型时召回本卡
- 配套资源：cfd-multifidelity-aerodynamic-surrogate-transfer（场景级迁移框架）、cfd-surrogate-transfer-learning-adaptation（迁移学习策略）

## 证据来源

[1] Keum, Warey, "Adapting Automotive Aerodynamics Surrogates to New Vehicle Families via Transfer Learning", arXiv:2605.27968, 2026
[2] Nieto-Centenero, Andrés, Castellanos, "Multi-fidelity aerodynamic data fusion by autoencoder transfer learning", arXiv:2512.13069, 2025
[3] Lao, Scott, Bui-Thanh, Laiu, Bement, "Dimension Bridging for 3D RANS with Neural Network Accelerated Gaussian Functional Regression", arXiv:2608.27639, 2026
[4] Zhang, Yang, Wang, Chen, Bin, Zhang, Wang, "RETO: A Rotary-Enhanced Transformer Operator for High-Fidelity Prediction of Automotive Aerodynamics", arXiv:2605.00062, 2026
