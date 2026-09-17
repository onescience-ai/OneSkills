# 神经多重网格与预条件线性PDE求解工作流

## 适用范围
本工作流适用于使用神经网络加速稀疏线性系统求解的完整项目流程，覆盖从数据准备到验收评估的全生命周期。每个步骤有明确的输入输出契约和质量门禁，可独立执行或按依赖顺序串行执行。

## 输入
- **数据集**：PDE系数矩阵、右端向量、网格信息（结构化/非结构化）
- **任务配置**：模型类型（神经多重网格/学习预条件器）、训练参数、验收指标
- **计算资源**：CPU/GPU设备、内存限制

## 输出
- **训练产物**：最佳模型权重、训练配置、训练指标
- **求解结果**：PDE数值解、残差历史、求解时间
- **验收报告**：评估指标、最差样本、适用域报告、PASS/REJECT/BLOCKED判定

## 流程节点

### Step 1: 数据接入与契约核验 (s01)
```
依赖：无
输入：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
输出：dataset_manifest.json, data_contract.json, data_audit.md
质量门禁：
  - 数据文件可读且样本可追溯
  - 输入目标变量单位坐标定义完整
  - 不存在训练测试泄漏
```

**操作要点**：
- 检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑
- 核验时间或工况范围、缺失值和使用许可
- 输出机器可读契约，缺少必填输入时返回BLOCKED

### Step 2: 预处理与数据切分 (s02)
```
依赖：s01
输入：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
输出：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
质量门禁：
  - 三份切分的对象轨迹互斥
  - 仅用训练集计算变换统计量
  - 边界与掩膜语义未破坏
```

**操作要点**：
- 依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化
- 按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分
- 不得把同一轨迹的帧随机打散
- 为{TARGET_FIELDS}保存统计量与可逆变换

### Step 3: 模型配置与训练 (s03)
```
依赖：s02
输入：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
输出：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
质量门禁：
  - 训练验证损失均为有限值
  - 最佳权重可重新加载
  - 配置环境随机种子可复现
```

**操作要点**：
- 使用{MODEL_NAME}（默认Neural multigrid、Learned preconditioner）
- 加载s02切分与统计量
- 记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重
- 若提供{INIT_CHECKPOINT}须检查结构兼容性

### Step 4: 神经数值耦合求解 (s04)
```
依赖：s03
输入：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
输出：coupled_solution/, residual_history.csv, solver_timing.json
质量门禁：
  - 耦合接口变量单位一致
  - 残差达到数值收敛门限
  - 相对原求解器误差和加速比均报告
```

**操作要点**：
- 加载{CHECKPOINT}，按数据契约把神经校正、网格移动、预条件或代理模块嵌入原数值求解器
- 执行端到端迭代，保存每步残差、守恒量、收敛状态和耗时
- 发散时停止并输出最后稳定状态

### Step 5: 任务验收与适用域判定 (s05)
```
依赖：s04
输入：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
输出：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
质量门禁：
  - 统计与物理指标同时报告
  - 最差样本可追溯
  - 结论含适用域限制与复核建议
```

**操作要点**：
- 按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本
- 使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
- 若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域
- 不得仅凭平均误差宣称工程可用

## 关键参数

### 通用判据
| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| 切分比例 | 0.7/0.15/0.15 | 场景需求书 | 训练/验证/测试集比例 |
| 批大小 | 8-32 | 场景需求书 | 训练批大小 |
| 学习率 | 0.001 | 场景需求书 | 初始学习率 |
| 早停耐心 | 15 | 场景需求书 | 验证损失不改善轮数 |
| 收敛容差 | 1e-6 | [1][3] | 残差范数容差 |
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |

### 校准数值（来自具体论文体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| UGrid训练 epochs | 100 | [1] | Poisson方程训练轮数 |
| MGCNN网格泛化范围 | 31×31至4095×4095 | [3] | 结构化网格泛化 |
| 加速比范围 | 1.2-8x | [1][3][5] | 相对经典方法加速 |

## 边界与分流
- **数据不完整**：返回BLOCKED，列出缺项，不得编造数据
- **训练发散**：降低学习率、增加正则化、简化网络结构
- **求解发散**：增加迭代次数、调整预条件器参数、切换Krylov方法
- **泛化失败**：扩大训练数据、使用域适应、增加正则化
- **资源不足**：使用混合精度、模型压缩、分布式计算

## 质量检查
- **每步门禁**：每个步骤必须通过质量门禁才能进入下一步
- **中间产物验证**：检查JSON格式正确性、文件完整性
- **随机种子追踪**：确保实验可复现
- **日志记录**：记录每步执行参数、耗时、关键指标

## 回退策略
- **步骤失败**：记录失败原因，回退到上一步骤，调整参数后重试
- **整体失败**：输出诊断报告，建议替代方案（如传统方法、简化模型）
- **资源耗尽**：保存中间结果，支持断点续训或续算

## 资源召回建议
- **何时召回本卡片**：当需要执行完整的神经PDE求解项目时
- **配套资源**：
  - cfd-neural-multigrid-preconditioned-pde-solver（场景级卡片）
  - cfd-neural-multigrid-smoother-learning（平滑器学习任务卡）
  - cfd-learned-preconditioner-design（预条件器设计任务卡）
  - cfd-neural-numerical-coupled-solver（耦合求解任务卡）
  - cfd-physics-consistency-validation（物理一致性验证任务卡）

## 证据来源
[1] UGrid: An Efficient-And-Rigorous Neural Multigrid Solver for Linear PDEs, Xi Han et al., ICML 2024, DOI: 10.48550/arXiv.2408.04846
[2] Learning Preconditioner for Conjugate Gradient PDE Solvers, Yichen Li et al., 2023, DOI: 10.48550/arXiv.2305.16432
[3] MGCNN: a learnable multigrid solver for sparse linear systems from PDEs on structured grids, Yan Xie et al., 2023, DOI: 10.48550/arXiv.2312.11093