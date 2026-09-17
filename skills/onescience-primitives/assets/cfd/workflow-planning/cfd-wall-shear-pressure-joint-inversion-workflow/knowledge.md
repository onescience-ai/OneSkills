# 壁面压力剪切与积分气动力联合反演工作流

## 适用范围
本工作流适用于从翼型壁面压力剪切及速度测量数据联合反演壁面压力剪切分布与积分气动力的完整流程。适用于需要基于壁面测量数据快速预测气动力载荷的工程场景。

## 输入
翼型壁面压力剪切及速度测量数据，包含压力系数、剪切应力、速度场等变量。数据需满足数据契约要求。

## 输出
反演的壁面压力剪切分布、积分气动力（升力、阻力、力矩）、物理一致性评估报告、适用域报告。

## 流程节点
数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 批量推理与物理恢复 → 任务验收与适用域判定。

### 步骤1：数据接入与契约核验（s01）
- 目的：建立数据清单，核验数据质量。
- 输入：数据集路径、数据集名称、数据契约。
- 输出：dataset_manifest.json, data_contract.json, data_audit.md。
- 质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏。
- 依赖：无。

### 步骤2：预处理与数据切分（s02）
- 目的：统一物理量与表示，构造无泄漏切分。
- 输入：切分配置、目标变量、是否无量纲化。
- 输出：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json。
- 质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏。
- 依赖：s01。

### 步骤3：模型配置与训练（s03）
- 目的：训练CNN、Aerodynamic foundation model完成指定输入到目标物理量的映射。
- 输入：模型名称、训练配置、初始权重。
- 输出：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt。
- 质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现。
- 依赖：s02。

### 步骤4：批量推理与物理恢复（s04）
- 目的：在独立测试集推理，恢复原始单位、网格和物理派生量。
- 输入：模型权重、计算设备、推理批大小。
- 输出：predictions/, inference_manifest.json, timing.csv。
- 质量门禁：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正。
- 依赖：s03。

### 步骤5：任务验收与适用域判定（s05）
- 目的：评估统计误差、关键物理约束、泛化能力和计算收益。
- 输入：验收指标、相对误差门限、是否外推测试。
- 输出：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt。
- 质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议。
- 依赖：s04。

## 关键参数
### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train 0.7, validation 0.15, test 0.15 | 场景需求书 | 标准切分比例 |
| 随机种子 | 42 | 场景需求书 | 可复现性保证 |
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计和物理指标 |

### 校准数值（体系专属值）
以下数值来自翼型壁面压力剪切与积分气动力联合反演场景，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | CNN、Aerodynamic foundation model | 场景需求书 | 默认模型 |
| 框架 | PyTorch | 场景需求书 | 训练框架 |
| 批大小 | 8 | 场景需求书 | 默认批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合 |

## 边界与分流
- 当数据缺少必填输入时返回BLOCKED并列出缺项。
- 当数据不满足质量门禁时，需返回预处理步骤修正。
- 当域外工况超出适用域时，需经CFD复核。
- 当模型性能不足时，需调整模型架构、增加数据量或使用迁移学习。

## 质量检查
- 每个步骤均有明确的质量门禁，需全部通过才能进入下一步。
- 最终验收需同时报告统计与物理指标，最差样本可追溯，结论含适用域限制与复核建议。

## 回退策略
- 若步骤失败，可返回前一步骤修正。
- 若模型性能不足，可尝试增加数据量、调整模型架构或使用迁移学习。
- 若数据质量不佳，可尝试数据清洗、异常值处理。

## 资源召回建议
当需要执行壁面压力剪切与积分气动力联合反演的完整工作流时召回本卡片。可配合以下卡片使用：
- cfd-data-acquisition-task：数据接入与契约核验。
- cfd-data-preprocessing-task：预处理与数据切分。
- cfd-model-training-task：模型配置与训练。
- cfd-inference-task：批量推理与物理恢复。
- cfd-evaluation-task：任务验收与适用域判定。

## 证据来源
[1] Predicting the wall-shear stress and wall pressure through convolutional neural networks, Arivazhagan G. Balasubramanian, Luca Guastoni, Philipp Schlatter, Hossein Azizpour, Ricardo Vinuesa, 2023, DOI: 10.48550/arXiv.2303.00706
[2] Towards a Foundation-Model Paradigm for Aerodynamic Prediction in Three-dimensional Design, Yunjia Yang, Babak Gholami, Caglar Gurbuz, Mohammad Rashed, Nils Thuerey, 2026, DOI: 10.48550/arXiv.2604.18062