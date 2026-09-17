# Deep Ritz与弱形式神经变分PDE求解工作流

## 适用范围

**触发条件**：
- 用户需要求解椭圆或演化方程的变分问题
- 已有变分积分数据或可推导变分形式
- 需要端到端的可复现工作流

**适用场景**：
- 椭圆方程（Poisson、Laplace等）的变分求解
- 演化方程（热传导、对流扩散等）的弱形式求解
- 高维PDE的神经网络求解
- 流体力学相关椭圆/抛物型子问题

**不适用场景**：
- 强间断/激波主导的双曲型方程
- 变分形式未知的PDE
- 要求严格守恒律保证的工程仿真（需CFD复核）

## 输入

- PDE变分积分形式（能量泛函或弱形式残差）
- 计算域几何定义
- 边界条件和初始条件（演化方程）
- 方程参数

## 输出

- 训练好的模型checkpoint
- 解场与残差场
- 物理一致性评估报告
- 适用域判定结果（PASS/REJECT/BLOCKED）

## 流程节点

### Step 1：数据接入与契约核验（s01）
- **操作**：接入椭圆与演化方程变分积分数据，核验样本、变量、单位、网格坐标及许可
- **输入**：DATASET_PATH, DATASET_NAME, DATA_CONTRACT
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **工具**：文件系统、JSON schema校验
- **对应task卡**：cfd-deep-ritz-data-ingestion-contract-validation

### Step 2：预处理与数据切分（s02）
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **依赖**：s01
- **输入**：SPLIT_CONFIG, TARGET_FIELDS, NONDIMENSIONALIZE
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **工具**：数据处理框架、归一化工具
- **对应task卡**：cfd-deep-ritz-preprocessing-data-split

### Step 3：模型配置与训练（s03）
- **操作**：训练Deep Ritz network、Weak-form neural solver完成指定输入到目标物理量的映射
- **依赖**：s02
- **输入**：MODEL_NAME, TRAIN_CONFIG, INIT_CHECKPOINT
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **工具**：PyTorch, 深度学习训练框架
- **对应task卡**：cfd-deep-ritz-model-training

### Step 4：方程求解与物理残差恢复（s04）
- **操作**：在查询配点或网格上恢复解场、导数、边界值与方程残差
- **依赖**：s03
- **输入**：CHECKPOINT, DEVICE, BATCH_SIZE
- **输出**：solution_fields/, pde_residuals/, boundary_residuals.csv
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照
- **工具**：自动微分、PyTorch推理
- **对应task卡**：cfd-deep-ritz-equation-solving-residual-recovery

### Step 5：任务验收与适用域判定（s05）
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **依赖**：s04
- **输入**：METRICS, MAX_RELATIVE_L2, RUN_OOD_TEST
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **工具**：评估脚本、可视化工具
- **对应task卡**：cfd-deep-ritz-acceptance-applicability-assessment

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [1] | 默认实现框架 |
| 默认epochs | 100 | [1] | 可按收敛情况调整 |
| 默认batch_size | 8 | [1] | 按显存调整 |
| 默认learning_rate | 0.001 | [1] | 需根据问题调整 |
| 早停patience | 15 | [1] | 防止过拟合 |
| 切分比例 | train:0.7, val:0.15, test:0.15 | [2] | 标准三份切分 |
| 随机种子 | 42 | [1] | 可复现性 |
| 相对误差门限 | 0.1 | [3] | 默认放行阈值 |
| 验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | [3] | 多维度验证 |

## 边界与分流

- **数据缺失**：若缺少必填输入（数据集路径、变量定义），返回BLOCKED并列出缺项
- **变分形式不可得**：转向强形式PINN求解
- **训练不收敛**：检查变分形式推导、网络架构、学习率调度
- **物理一致性不足**：增加配点密度、调整网络、引入自适应采样
- **域外工况**：必须经CFD复核

## 质量检查

每步均有独立质量门禁：
- s01：数据完整性与可追溯性
- s02：切分无泄漏、统计量仅来自训练集
- s03：训练收敛性与可复现性
- s04：解场有限性与边界满足
- s05：多维度指标、最差样本追溯、适用域明确

## 回退策略

- 单步失败可回退到上一步检查
- 训练失败可调整超参数重试
- 物理一致性不足可增加网络复杂度
- 最终验收不通过需CFD复核

## 资源召回建议

当需要执行Deep Ritz或弱形式神经变分求解的完整工作流时召回本卡。配套资源：
- 场景卡 `cfd-deep-ritz-weak-form-neural-variational-solver`（场景定义）
- 5个task卡（各步骤详细操作）
- onescience-runtime（执行环境）
- onescience-coder（代码生成）

## 证据来源

[1] "The Deep Ritz Method: A Deep Learning-Based Numerical Algorithm for Solving Variational Problems", E and Yu, 2017
[2] "Error Analysis of Deep Ritz Methods for Elliptic Equations", 2021
[3] "Learning from Integral Losses in Physics-Informed Neural Networks", 2024
[4] "Weak adversarial networks for high-dimensional partial differential equations", 2019
[5] "Characterizing possible failure modes in physics-informed neural networks", 2021
[6] "Efficient Error Certification for Physics-Informed Neural Networks", 2024
