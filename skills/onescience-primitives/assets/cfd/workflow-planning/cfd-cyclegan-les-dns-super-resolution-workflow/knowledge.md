# CycleGAN无配对LES到DNS超分辨率重建工作流

## 适用范围

**触发条件**：
- 拥有非配对LES与DNS湍流数据集
- 需要一个端到端可复现的流水线，覆盖从数据接入到验收的全生命周期
- 需要可追溯的质量门禁体系确保每步产出可验证

**适用场景**：
- 湍流超分辨率重建：从工程LES粗网格结果恢复DNS精细流场细节
- CFD后处理增强：提升模拟结果的时空分辨率
- 无配对流场数据的跨分辨率域映射
- 物理一致性评估与适用域判定

**不适用场景**：
- LES与DNS数据完全配对的监督学习超分辨率
- 单步模型调优（不走完整流水线）
- 纯后处理分析（不涉及模型训练）

## 输入

核心输入由场景需求书的 `workflow[].step_input` 定义，包含：

1. **数据集路径与契约**（s01）：{DATASET_PATH}、{DATASET_NAME}、{DATA_CONTRACT}
2. **切分配置**（s02）：{SPLIT_CONFIG}、{TARGET_FIELDS}、{NONDIMENSIONALIZE}
3. **模型与训练配置**（s03）：{MODEL_NAME}、{TRAIN_CONFIG}、{INIT_CHECKPOINT}
4. **推理配置**（s04）：{CHECKPOINT}、{DEVICE}、{BATCH_SIZE}
5. **验收配置**（s05）：{METRICS}、{MAX_RELATIVE_L2}、{RUN_OOD_TEST}

## 输出

每步产出见下表：

| 步骤 | 产物 | 格式 |
|------|------|------|
| s01 数据接入 | dataset_manifest.json, data_contract.json, data_audit.md | JSON/MD |
| s02 预处理 | train/val/test_manifest.json, normalization.json | JSON |
| s03 训练 | best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt | PT/JSON/CSV/TXT |
| s04 重构 | reconstructed_fields/, error_fields/, spectral_statistics.json | DIR/JSON |
| s05 验收 | evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt | JSON/CSV/MD/TXT |

## 流程节点

### s01：数据接入与契约核验
- **操作**：接入非配对LES与DNS湍流数据，核验样本、变量、单位、网格坐标及许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **关键输出**：data_contract.json（机器可读契约）

### s02：预处理与数据切分
- **操作**：统一物理量表示，执行质控与归一化，按几何/轨迹/工况无泄漏切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **质量门禁**：三份切分对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **关键约束**：同一轨迹的帧不得随机打散

### s03：模型配置与训练
- **操作**：加载切分与统计量，训练CycleGAN完成LES到DNS无配对映射
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **关键约束**：必须记录代码版本、依赖、随机种子以保证可复现性

### s04：低分辨或部分观测流场重构
- **操作**：加载checkpoint，对测试集构造低分辨输入并执行高分辨重构
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **质量门禁**：观测掩膜与训练测试协议一致；小尺度频谱与统计量得到验证；边界守恒误差不因超分辨恶化
- **关键约束**：禁止通过测试真值调节掩膜或超参数

### s05：任务验收与适用域判定
- **操作**：评价统计误差、物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **关键约束**：不得仅凭平均误差宣称工程可用

## 关键参数

### 通用判据

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 数据泄漏 | 同一几何/轨迹/工况帧不跨切分集 | 场景需求书 s01/s02 | 时序流体数据核心约束 |
| 切分单位 | 按几何、完整轨迹或物理工况 | 场景需求书 s02 | 保证训练/测试独立性 |
| 统计量来源 | 仅用训练集计算 | 场景需求书 s02 | 防止信息泄漏 |
| 掩膜一致性 | 训练与测试使用相同观测协议 | 场景需求书 s04 | 保证评估公平性 |
| 验收门限 | 相对L2误差 ≤ 0.1（可调） | 场景需求书 s05 | 量化工程可用性判据 |
| 外推测试 | 几何/工况外推需单独评估 | 场景需求书 s05 | 适用域判定必要条件 |

### 校准数值

以下数值来自场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| 切分比例 | train=0.7, val=0.15, test=0.15 | 场景需求书 s02 | 典型比例 |
| 切分种子 | 42 | 场景需求书 s02 | 可复现性 |
| 训练epochs | 100 | 场景需求书 s03 | 默认上限 |
| batch_size | 8 | 场景需求书 s03 | 视显存调整 |
| 学习率 | 0.001 | 场景需求书 s03 | Adam默认量级 |
| 早停耐心 | 15 | 场景需求书 s03 | 防止过拟合 |
| 推理批大小 | 8 | 场景需求书 s04 | 视显存调整 |
| 默认设备 | cuda | 场景需求书 s04 | GPU推理 |
| 相对L2门限 | 0.1 | 场景需求书 s05 | 放行阈值 |

## 边界与分流

| 前提 | 不成立时的改道 |
|------|---------------|
| 数据集文件不可读或缺失 | 返回BLOCKED并列出缺项，不编造数据 |
| 数据契约字段不完整 | 补充缺失字段定义或拒绝执行 |
| 同一轨迹帧被打散 | 重新执行切分，修正分组键 |
| CycleGAN训练不收敛 | 调整超参数或回退到监督超分辨模型 |
| 重构频谱严重偏离DNS | 增加频谱损失项或调整网络架构 |
| 域外工况超出分布 | 不宣称工程可用，需CFD复核 |
| 边界守恒误差恶化 | 施加守恒约束后处理 |

## 质量检查

| 检查点 | 通过标准 | 失败处理 |
|--------|---------|---------|
| 数据可读性 | 文件加载成功，样本数一致 | 返回BLOCKED |
| 切分互斥性 | train/val/test无重叠 | 重新切分 |
| 训练收敛 | val_loss有限且无NaN | 调参重训 |
| 权重可加载 | checkpoint加载一致 | 重新保存 |
| 掩膜一致 | 训练测试观测协议相同 | 修正掩膜 |
| 频谱验证 | 小尺度能谱偏差可接受 | 增加频谱损失 |
| 边界守恒 | 守恒误差不超限 | 施加约束后处理 |
| 最差样本 | worst_cases.csv可追溯 | 补充分析 |
| 适用域 | 含边界与复核建议 | 补充外推 |

## 回退策略

- 数据不可用：返回BLOCKED
- CycleGAN训练不收敛：回退到监督超分辨模型（若有配对数据）
- 重构物理不一致：回退到传统插值方法作为基线对比
- 验收REJECT：不输出工程可用结论，需CFD复核

## 资源召回建议

- 何时召回：用户需要执行端到端CycleGAN无配对超分辨率重建流水线，或需要核对某一步骤的输入输出契约
- 配套资源：cfd-cyclegan-les-to-dns-super-resolution-scenario（场景总卡）、cfd-cyclegan-acceptance-applicability（验收评估卡）

## 证据来源

[1] "Unsupervised deep learning for super-resolution reconstruction of turbulence", arXiv:2007.15324, 2020
[2] "A neural network approach for the blind deconvolution of turbulent flows", arXiv:1706.00912, 2017
