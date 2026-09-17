# Data-Driven LES Source Modeling for High-Fidelity Calibration

## 适用范围

**触发条件**：
- 需要从高保真DNS或精细LES参考数据中提取工程级等效源项（闭合项、应力张量或通量）
- 需要将数据驱动模型嵌入RANS或LES求解器完成后验验证
- 需要评估数据驱动湍流闭合模型的物理一致性与工程适用域

**适用场景**：
- 叶轮机械（如von Kármán流）的工程LES等效源项建模
- 高升力构型气动外形的湍流闭合模型训练与校准
- 任何需要以高保真数据为参考训练工程级湍流模型的CFD任务

**不适用场景**：
- 无高保真参考数据（DNS/LES）的纯经验建模
- 纯解析湍流模型（如k-ε、SA）的参数调优
- 无CFD求解器耦合需求的纯统计预测任务

## 输入

| 输入 | 类型 | 必需 | 说明 |
|------|------|------|------|
| {DATASET_PATH} | doc | 是 | 高保真数据集路径（DNS或精细LES快照），包含流场变量、网格坐标、时间步或工况信息 |
| {DATASET_NAME} | str | 是 | 数据集标识与版本 |
| {DATA_CONTRACT} | object | 否 | 变量-单位-网格契约模板，默认空由数据审计自动发现 |
| {SPLIT_CONFIG} | object | 否 | 切分比例与分组策略 |
| {TARGET_FIELDS} | list[str] | 是 | 待预测物理量列表（应力分量、通量、源项等） |
| {MODEL_NAME} | str | 是 | 模型实现名称，默认"Data-driven LES source model" |
| {TRAIN_CONFIG} | object | 否 | 训练超参数 |
| {CHECKPOINT} | doc | 是 | 通过训练门限的模型权重 |
| {DEVICE} | str | 否 | 推理设备，默认cuda |
| {METRICS} | list[str] | 是 | 验收指标列表 |
| {MAX_RELATIVE_L2} | float | 否 | 测试集放行阈值，默认0.1 |
| {RUN_OOD_TEST} | bool | 否 | 是否执行域外工况外推测试，默认true |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| dataset_manifest.json | JSON | 数据集清单：样本数、变量、坐标、缺失值 |
| data_contract.json | JSON | 机器可读契约：变量-单位-坐标-网格定义 |
| data_audit.md | Markdown | 数据质量审计报告 |
| train/val/test_manifest.json | JSON | 三份切分清单，含统计量与变换参数 |
| normalization.json | JSON | 归一化/无量纲化参数（可逆） |
| best_checkpoint.pt | PyTorch | 最佳模型权重 |
| train_config.json | JSON | 训练配置快照 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| environment.txt | Text | 代码版本、依赖、随机种子 |
| apriori_closure/ | Directory | 先验闭合项评估场 |
| aposteriori_fields/ | Directory | 后验求解器场数据 |
| solver_stability.csv | CSV | 求解稳定性记录 |
| evaluation.json | JSON | 综合评估指标 |
| worst_cases.csv | CSV | 最差样本追溯 |
| applicability_report.md | Markdown | 适用域报告 |
| PASS_REJECT_BLOCKED.txt | Text | 最终验收结论 |

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取高保真数据集，建立变量-单位-坐标-网格的机器可读契约，检查文件可读性、样本追溯性、输入目标变量定义完整性，排查训练测试泄漏
- **参数**：数据集路径、契约模板
- **工具**：Python (pandas/numpy/xarray), HDF5/NetCDF reader
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，执行质控、重采样或图构建、掩膜、归一化或无量纲化；按几何、完整轨迹或物理工况为单位构造无泄漏切分
- **参数**：切分比例（train/val/test）、分组策略（geometry_or_trajectory）、随机种子
- **工具**：Python (sklearn/preprocessing), 自定义切分器
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **关键约束**：不得把同一轨迹的帧随机打散

### Step 3：模型配置与训练
- **操作**：加载切分与统计量，配置并训练Data-driven LES source model，记录逐轮训练验证指标与最佳权重；若提供预训练权重须检查结构兼容性
- **参数**：框架（PyTorch）、epochs、batch_size、learning_rate、seed、early_stopping_patience
- **工具**：PyTorch, tensorboard (可选)
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：闭合项预测与后验CFD耦合
- **操作**：加载模型权重预测应力、通量或源项；在独立快照上做先验误差和可实现性检查；嵌入对应RANS或LES求解器执行后验推进
- **参数**：推理批大小、计算设备
- **工具**：PyTorch (inference), CFD求解器 (OpenFOAM/自研)
- **质量门禁**：闭合张量或通量满足约束（对称性、正定性、量纲）；后验求解无非物理解和发散；均值剖面与能谱均经验证
- **输出子目录**：apriori_closure/（先验误差场）、aposteriori_fields/（后验流场）、solver_stability.csv

### Step 5：任务验收与适用域判定
- **操作**：按验收指标评价统计误差、关键物理约束、泛化能力和计算收益；若执行外推测试则明确适用域边界
- **参数**：验收指标列表、相对误差门限、是否外推测试
- **工具**：Python (numpy/scipy), 自定义评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **关键约束**：不得仅凭平均误差宣称工程可用，必须报告最差样本和边界工况表现

## 关键参数

### 通用判据

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 数据泄漏检查 | 同一几何/轨迹/工况的帧不得跨切分集 | 场景需求书 s01/s02 | 流体时序数据的常见陷阱 |
| 切分策略 | 按几何、完整轨迹或物理工况为单位 | 场景需求书 s02 | 保证训练/测试独立性 |
| 无量纲化 | 跨工况统一量纲时仅用训练集统计量 | 场景需求书 s02 | 防止信息泄漏 |
| 求解稳定性 | 后验推进无非物理解和发散 | 场景需求书 s04 | 闭合模型嵌入求解器的基本要求 |
| 验收门限 | 相对L2误差 ≤ 0.1（可调） | 场景需求书 s05 | 工程可用性的量化判据 |
| 外推测试 | 几何或工况外推需单独评估 | 场景需求书 s05 | 适用域判定的必要条件 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认切分比例 | train=0.7, val=0.15, test=0.15 | 场景需求书 s02 | 供量级校准；其他体系需以自身证据重新锚定 |
| 默认训练epochs | 100 | 场景需求书 s03 | 默认值，视收敛情况调整 |
| 默认batch_size | 8 | 场景需求书 s03 | 视显存调整 |
| 默认学习率 | 0.001 | 场景需求书 s03 | PyTorch Adam默认量级 |
| 早停耐心 | 15 | 场景需求书 s03 | 防止过拟合 |
| 默认随机种子 | 42 | 场景需求书 s02/s03 | 可复现性 |

## 边界与分流

| 前提 | 不成立时的改道 |
|------|---------------|
| 高保真参考数据（DNS/LES）不可用 | 转向纯经验建模或文献参数化模型，不走数据驱动路线 |
| 数据量不足以支撑深度学习 | 转向浅层模型（随机森林、高斯过程回归）或迁移学习 |
| CFD求解器不可耦合 | 仅做先验评估，不执行后验验证，结论限定为先验级 |
| 域外工况超出训练分布 | 不得宣称工程可用，需回退到原体系校准或扩展训练数据 |
| 闭合项不满足物理约束 | 在后验推进前施加约束投影（如对称化、正定化），或回退到传统模型 |

## 质量检查

| 检查点 | 通过标准 | 失败处理 |
|--------|---------|---------|
| 数据可读性 | 所有文件成功加载，样本数与预期一致 | 排查格式/路径问题，返回BLOCKED |
| 切分互斥性 | train/val/test无几何/轨迹/工况重叠 | 重新执行切分，检查分组键 |
| 训练收敛 | val_loss为有限值且无NaN | 调整学习率或batch_size重训 |
| 权重可加载 | checkpoint加载后推理结果一致 | 重新保存权重或排查框架版本 |
| 先验闭合约束 | 张量对称性、正定性、量纲检查通过 | 施加约束投影或回退 |
| 后验求解稳定 | 残差单调下降，无非物理振荡 | 缩小时间步或增加松弛 |
| 最差样本可追溯 | worst_cases.csv记录具体工况和误差 | 补充最差样本分析 |
| 适用域报告 | 含明确的工况/几何边界与复核建议 | 补充外推测试 |

## 回退策略

- 训练不收敛：回退到更浅层模型或增大数据增强
- 后验推进发散：回退到先验评估，仅报告闭合项统计误差
- 适用域判定REJECT：回退到原体系校准，不输出工程可用结论
- 数据契约不满足：返回BLOCKED并列出缺项，不编造数据

## 资源召回建议

- 何时召回：用户需要训练数据驱动湍流闭合模型、校准工程LES源项、评估DNS-to-LES模型迁移
- 配套资源：cfd-les-data-driven-pipeline-workflow（详细流程卡）、cfd-les-a-priori-a-posteriori-coupling-validation（先验后验耦合验证卡）

## 证据来源

[1] "Data-driven impeller model for efficient large eddy simulations of metastable von Kármán flows", arXiv:2607.25048, 2026
[2] "Deep learning observables in computational fluid dynamics", arXiv:1903.03040, 2019
[3] "Learning to Estimate and Refine Fluid Motion with Physical Dynamics", 无DOI
[4] "Bayesian optimization and topographic exploration of drag-reducing dimples for aerodynamic surfaces", arXiv:2608.12826, 2026
[5] "HiLiftAeroML: High-Fidelity Computational Fluid Dynamics Dataset for High-Lift Aircraft Aerodynamics", arXiv:2605.19565, 2026
