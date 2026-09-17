# 钝体尾迹闭环减阻控制工作流

## 适用范围

**触发条件**：
- 需要端到端完成从数据到策略再到验收的 DRL 闭环减阻控制全流程
- 已有或可获取圆柱/钝体的 OpenFOAM 传感器-执行器轨迹数据

**适用场景**：
- 圆柱绕流 DRL 减阻控制的完整研究项目
- 钝体尾迹主动控制策略的开发与验证
- 需要输出可复现模型和适用域报告的研究任务

**不适用场景**：
- 仅需其中某一步骤的局部任务（应使用对应 task 卡片）
- 非 CFD 环境的控制问题

## 输入

- 圆柱与钝体 OpenFOAM 传感动作轨迹数据集路径
- 数据契约（变量定义、单位、网格坐标）
- 训练配置（框架、超参数、随机种子）
- 计算设备（CPU/CUDA）
- 验收指标与门限配置

## 输出

- 训练好的 DRL 模型 checkpoint（best_checkpoint.pt）
- 训练配置与环境信息（train_config.json, environment.txt）
- 训练指标记录（training_metrics.csv）
- 闭环仿真轨迹与控制动作（closed_loop_trajectories/, control_actions.csv）
- 基线对比结果（baseline_comparison.json）
- 验收评估报告（evaluation.json, worst_cases.csv, applicability_report.md）
- 通过/拒绝/阻塞判定（PASS_REJECT_BLOCKED.txt）

## 流程节点

### s01 数据接入与契约核验
- **操作**：读取数据集，建立数据清单，检查可读性、样本数、变量、单位、坐标、时间范围、缺失值和许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### s02 预处理与数据切分
- **操作**：依据 s01 契约完成质控、重采样、归一化或无量纲化；按几何、完整轨迹或物理工况为单位切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **依赖**：s01

### s03 模型配置与训练
- **操作**：加载 s02 切分与统计量，使用 DRL 训练策略网络，记录代码版本、依赖、随机种子、逐轮指标与最佳权重
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **依赖**：s02

### s04 闭环策略部署与滚动仿真
- **操作**：加载 checkpoint 作为控制策略，在独立初值和工况上执行闭环滚动，记录观测、动作、载荷、控制能耗及约束违例
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：closed_loop_trajectories/, control_actions.csv, baseline_comparison.json
- **质量门禁**：动作满足幅值频率安全约束；闭环过程稳定无数值发散；收益扣除控制能耗后仍成立
- **依赖**：s03

### s05 任务验收与适用域判定
- **操作**：按验收指标评价 s04 结果，报告逐变量误差、边界误差、守恒残差、最差样本和推理成本；执行几何或工况外推测试
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **依赖**：s04

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train: 0.7, val: 0.15, test: 0.15 | 场景需求书 s02 | 标准三切分，按几何或轨迹分组 |
| 切分种子 | 42 | 场景需求书 s02 | 可复现切分 |
| 早停耐心 | 15 epochs | 场景需求书 s03 | 防止过拟合 |
| 随机种子 | 42 | 场景需求书 s03 | 训练可复现性 |
| 相对误差门限 | 0.1 | 场景需求书 s05 | 测试集放行阈值 |
| 外推测试 | true（默认） | 场景需求书 s05 | 需评估域外工况 |

### 校准数值

以下数值来自圆柱与钝体 OpenFOAM 传感动作轨迹体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | 场景需求书 s03 | 默认框架 |
| epochs | 100 | 场景需求书 s03 | 训练轮次 |
| batch_size | 8 | 场景需求书 s03 | 训练批大小 |
| learning_rate | 0.001 | 场景需求书 s03 | 学习率 |
| 默认模型 | Deep reinforcement learning | 场景需求书 s03 | 方法名 |
| 推理批大小 | 8 | 场景需求书 s04 | 推理时批大小 |
| 默认设备 | cuda | 场景需求书 s04 | 推理设备 |
| 验收指标集 | drag_or_load_reduction, control_energy, stability, constraint_violations | 场景需求书 s05 | 四维联合验收 |

## 边界与分流

- **s01 缺少必填输入**：返回 BLOCKED，列出缺项，不得编造数据、权重、工况或结果
- **s02 切分泄漏风险**：若同一轨迹帧被随机打散到不同切分集，需按完整轨迹或工况为单位重新切分
- **s03 训练不收敛**：若损失为 NaN 或 Inf，需检查数据预处理、学习率或奖励函数设计
- **s04 闭环发散**：若仿真出现数值发散，需检查时间步长、边界条件或执行器幅值约束
- **s05 域外工况不通过**：需扩大训练数据覆盖范围或重新设计观测空间，域外工况需 CFD 复核

## 质量检查

- 每步输出文件完整且格式正确
- 数据切分无泄漏（轨迹互斥）
- 训练过程可复现（种子+环境）
- 闭环仿真稳定（无数值发散）
- 验收报告含统计与物理双维度
- 最差样本可追溯
- 适用域报告含限制与复核建议

## 回退策略

- 数据不足时可先用合成数据或文献公开数据补充
- 训练失败时可降低网络复杂度或调整超参数
- 闭环仿真失败时可回退到经典控制方法作为基线
- 适用域不满足时需扩大训练数据范围或降低部署要求

## 资源召回建议

- 需要 CFD 环境安装时，召回 CFD 环境配置相关卡片
- 需要数据处理细节时，召回数据预处理与切分 task 卡片
- 需要 DRL 训练细节时，召回模型训练 task 卡片
- 需要闭环部署细节时，召回闭环部署 task 卡片
- 需要验收评估细节时，召回任务验收 task 卡片

## 证据来源

[1] "Active flow control for bluff body drag reduction using reinforcement learning with partial measurements", arXiv:2307.12650, 2023
[2] "DRLinFluids: An open-source Python platform of coupling deep reinforcement learning and OpenFOAM", arXiv:2205.12699, 2022
[3] "Artificial neural networks trained through deep reinforcement learning discover control strategies for active flow control", arXiv:1808.07664, 2018
