# 高保真汽车数据集全场与气动力联合代理工作流

## 适用范围
本卡片覆盖汽车外流场空气动力学中，从数据接入到任务验收的标准化五步工作流，适用于基于WindsorML/DrivAerStar/CarBench高保真数据集构建全场与气动力联合代理模型。工作流需同时保证全场预测精度与气动力系数回归精度，并评估物理一致性与泛化能力。

## 输入
- **数据集路径**：WindsorML/DrivAerStar/CarBench数据集目录或清单文件
- **数据集名称**：来源与数据版本标识
- **数据契约**：变量、单位、网格定义（可选）
- **切分配置**：按对象/工况切分比例与种子
- **模型配置**：框架、超参数、随机种子
- **计算设备**：CPU或CUDA设备

## 输出
- 数据清单与契约（dataset_manifest.json、data_contract.json、data_audit.md）
- 三份切分manifest与归一化统计量
- 训练好的模型权重与配置
- 测试集逐样本预测与物理恢复结果
- 评估报告与验收结论

## 流程节点
**s01 数据接入与契约核验**：
- 操作：读取数据集路径，核验样本数、变量、单位、网格坐标及许可
- 输出：dataset_manifest.json、data_contract.json、data_audit.md
- 质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- 场景需求书依据：s01 prompt

**s02 预处理与数据切分**：
- 操作：统一物理量表示，按几何/工况构造无泄漏切分（train 0.7/val 0.15/test 0.15）
- 输出：三份切分manifest、normalization.json
- 质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- 场景需求书依据：s02 prompt

**s03 模型配置与训练**：
- 操作：使用Neural CFD surrogate，加载切分数据与统计量，训练模型并记录逐轮指标
- 输出：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt
- 质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- 场景需求书依据：s03 prompt

**s04 批量推理与物理恢复**：
- 操作：在独立测试集推理，反归一化恢复物理单位、网格、边界掩膜及任务派生量
- 输出：predictions/、inference_manifest.json、timing.csv
- 质量门禁：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- 场景需求书依据：s04 prompt

**s05 任务验收与适用域判定**：
- 操作：统计误差、物理约束、泛化能力和计算收益综合评估
- 输出：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt
- 质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- 场景需求书依据：s05 prompt

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据切分比例 | train:0.7 / val:0.15 / test:0.15 | [场景s02] | 按几何或轨迹单位切分 |
| 随机种子 | 42 | [场景s02,s03] | 确保可复现 |
| 训练框架 | PyTorch | [场景s03] | 默认框架 |
| 训练轮数 | 100 | [场景s03] | 默认最大轮数 |
| 批大小 | 8 | [场景s03,s04] | 推理可调 |
| 学习率 | 0.001 | [场景s03] | 默认初始学习率 |
| 早停耐心 | 15 | [场景s03] | 验证损失不降则停 |
| 相对误差门限 | 0.1 | [场景s05] | 测试集PASS/REJECT阈值 |
| 默认设备 | cuda | [场景s04] | 推理设备 |

## 边界与分流
- 数据集缺失必填字段（坐标、目标变量、单位）→ s01返回BLOCKED，列出缺项，不编造数据
- 同一轨迹帧被打散到不同切分集 → s02不通过，需按对象/轨迹单位重新切分
- 模型权重无法重新加载 → s03不通过，需检查PyTorch版本或架构兼容性
- 推理输出含NaN/Inf → s04不通过，需回查数据预处理或模型权重
- 相对误差超过0.1 → s05 REJECT，需调整模型或扩大训练域
- 域外工况（新几何形状/新雷诺数范围）→ 触发OOD测试，不通过则标REJECT并建议CFD复核
- HPC资源不可用 → 本场景标注hpc为NULL，支持单机GPU训练

## 质量检查
- s01：检查数据完整性、变量定义、无泄漏
- s02：三集互斥性验证、归一化统计量来源验证
- s03：训练收敛曲线检查、随机种子复现验证
- s04：预测值合理性（物理单位量级）、无NaN/Inf
- s05：多指标综合判定、worst-case追溯、适用域边界明确

## 回退策略
- 数据加载失败 → 检查路径与文件权限，或降级为部分样本验证
- GPU显存不足 → 降低batch_size或切换CPU推理
- 模型不收敛 → 检查学习率、数据质量、或尝试预训练权重初始化

## 资源召回建议
当用户涉及以下任务时应召回本卡片：
- WindsorML/DrivAerStar/CarBench数据集使用
- 汽车全场流场与气动力系数联合预测工作流
- Neural CFD surrogate模型训练与评估流程
- 需要物理一致性约束的汽车CFD-ML任务
- OOD泛化与适用域评估流程

## 补充证据
（无补充通道证据）

## 证据来源
[1] WindsorML_ High-Fidelity Computational Fluid Dynamics Dataset For Automotive Aerodynamics, 2025
[2] CarBench_ A Comprehensive Benchmark for Neural Surrogates on High-Fidelity 3D Car Aerodynamics, arXiv:2512.07847, 2025
[3] DrivAerStar_ An Industrial-Grade CFD Dataset for Vehicle Aerodynamic Optimization, arXiv:2510.16857, 2025
[4] Extreme Aerodynamics _ A Data-Driven Perspective, arXiv:2511.12889, 2025