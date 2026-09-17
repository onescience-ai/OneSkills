# 随机微分与概率粗粒化湍流闭合 — 工作流

## 适用范围

本工作流描述从多尺度湍流数据到可复现闭合模型的完整建模管线。适用于需要为LES/RANS求解器提供子网格尺度闭合项、或从DNS/实验数据学习随机闭合映射的场景。工作流覆盖数据验证、切分、训练、耦合与验收五个阶段。

## 流程节点

### s01 数据接入与契约核验
- **操作**：读取数据集，核验样本数、变量、单位、网格坐标、时间/工况范围、缺失值与使用许可
- **输入**：DATASET_PATH, DATASET_NAME, DATA_CONTRACT
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：文件可读且样本可追溯；输入目标变量单位坐标定义完整；无训练测试泄漏
- **工具**：Python数据读取库（h5py/xarray/numpy）

### s02 预处理与数据切分
- **操作**：统一物理量表示，无量纲化，按几何/工况/时间构造无泄漏切分
- **输入**：SPLIT_CONFIG, TARGET_FIELDS, NONDIMENSIONALIZE
- **输出**：train/val/test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **关键约束**：不得把同一轨迹的帧随机打散

### s03 模型配置与训练
- **操作**：加载数据与统计量，配置Neural SDE closure与Probabilistic coarse-graining model，执行训练
- **输入**：MODEL_NAME, TRAIN_CONFIG, INIT_CHECKPOINT（可选）
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **关键方法**：
  - Neural SDE：学习耦合SDE系统 f_θ(ζ,φ(η))dt + L_θ(t)dβ [2]
  - 概率粗粒化：编码器-粗粒化模型-解码器三步架构 [1]

### s04 闭合项预测与后验CFD耦合
- **操作**：加载权重预测应力/通量/源项，先验误差检查，嵌入RANS/LES求解器后验推进
- **输入**：CHECKPOINT, DEVICE, BATCH_SIZE
- **输出**：apriori_closure/, aposteriori_fields/, solver_stability.csv
- **质量门禁**：闭合张量或通量满足约束；后验求解无非物理解和发散；均值剖面与能谱经验证

### s05 任务验收与适用域判定
- **操作**：按验收指标评价，报告误差、约束残差、最差样本与推理成本
- **输入**：METRICS, MAX_RELATIVE_L2, RUN_OOD_TEST
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | 场景需求书 | train/val/test |
| 无量纲化 | true | 场景需求书 | 默认启用 |
| 框架 | PyTorch | 场景需求书 | 深度学习框架 |
| epochs | 100 | 场景需求书 | 默认训练轮数 |
| batch_size | 8 | 场景需求书 | 默认批大小 |
| learning_rate | 0.001 | 场景需求书 | 默认学习率 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 默认相对误差门限 |
| seed | 42 | 场景需求书 | 随机种子 |

## 边界与分流

- 数据不可读或缺项 → BLOCKED
- 训练损失非有限值 → 检查数据与模型配置
- 闭合项不满足约束 → 调整模型架构
- 后验求解发散 → 降级为先验评估
- 域外工况测试失败 → 标注适用域限制，建议CFD复核

## 质量检查

每个阶段均含质量门禁，详见各节点描述。总体验收要求：
- 统计误差（RMSE、相对L2）与物理约束（能谱、守恒性）同时报告
- 最差样本可追溯至原始数据
- 结论明确标注适用域与复核建议

## 回退策略

- s01失败 → 补齐数据或更换数据源
- s02失败 → 调整切分策略，确保无泄漏
- s03失败 → 调整超参数、更换模型架构、增加数据
- s04失败 → 降级为先验评估
- s05失败 → 标记REJECT，建议重新训练或更换方法

## 资源召回建议

- 需要了解整体流程时召回本卡
- 需要了解具体步骤时召回对应任务卡
- 需要了解方法原理时召回Neural SDE或多尺度建模方法卡

## 证据来源

[1] Grigo, C., Koutsourelakis, P.-S. (2019). Journal of Computational Physics, 397, 108842.
[2] Ilersich, A.F., Nair, P.B. (2025). Learning Stochastic Multiscale Models. arXiv:2506.22655.
