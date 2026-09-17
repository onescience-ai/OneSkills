# Symbolic and Sparse Equation Discovery Workflow

## 适用范围
面向从稀疏状态轨迹与导数观测中发现控制偏微分方程的完整工作流。定义五个串行步骤的依赖关系、输入输出契约和质量门禁，适用于任何使用符号回归或稀疏PDE发现方法的CFD方程发现任务。

## 输入
- **稀疏状态轨迹数据**：空间-时间域上的物理量采样。
- **导数观测**（可选）：通过自动微分或有限差分获得的导数信息。
- **数据契约**：变量、单位、网格的结构化定义。

## 输出
- **发现的控制方程**：符号形式的PDE表达式。
- **验收报告**：evaluation.json、worst_cases.csv、applicability_report.md。
- **通过/拒绝判定**：PASS_REJECT_BLOCKED.txt。

## 流程节点
```
s01: 数据接入与契约核验
  → 输出: dataset_manifest.json, data_contract.json, data_audit.md
  → 质量门禁: 数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

s02: 预处理与数据切分（依赖s01）
  → 输出: train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
  → 质量门禁: 三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

s03: 模型配置与训练（依赖s02）
  → 输出: best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
  → 质量门禁: 训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

s04: 方程求解与物理残差恢复（依赖s03）
  → 输出: solution_fields/, pde_residuals/, boundary_residuals.csv
  → 质量门禁: 解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照

s05: 任务验收与适用域判定（依赖s04）
  → 输出: evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
  → 质量门禁: 统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| s01数据契约完整性 | 必须含变量、单位、坐标定义 | [场景需求书] | 缺少任一项返回BLOCKED |
| s02切分互斥性 | 按轨迹/工况分组，帧不随机打散 | [场景需求书] | 防止训练测试泄漏 |
| s03训练收敛 | 损失为有限值且可复现 | [场景需求书] | 非有限值触发回退 |
| s04残差有限性 | 解场、导数、残差均为有限值 | [场景需求书] | 否则回退检查自动微分 |
| s05多维验收 | 统计+物理指标同时报告 | [场景需求书] | 不得仅凭平均误差判定 |

### 校准数值
> 以下数值来自场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | train/val/test |
| 默认框架 | PyTorch | [场景需求书] | — |
| 默认轮数 | 100 | [场景需求书] | 受早停控制 |
| 默认批大小 | 8 | [场景需求书] | — |
| 默认学习率 | 0.001 | [场景需求书] | — |
| 早停耐心 | 15轮 | [场景需求书] | — |
| 默认种子 | 42 | [场景需求书] | — |
| 相对误差门限 | 0.1 | [场景需求书] | 可按任务调整 |

## 边界与分流
- **s01 BLOCKED**：缺少必填数据输入时停在s01，不得编造数据跳过。
- **s02 切分失败**：轨迹互斥性不满足时调整group_by策略。
- **s03 训练异常**：非有限损失触发回退至s02检查数据预处理。
- **s04 恢复异常**：残差非有限值时检查自动微分或切换离散算子。
- **s05 REJECT/BLOCKED**：增加数据覆盖或调整正则化策略后重试，域外工况须经CFD复核。

## 质量检查
每个步骤必须通过其质量门禁才能进入下一步。最终验收需同时满足统计指标和物理指标。

## 回退策略
- 任一步骤失败可回退至前一步骤重新执行。
- 最终验收REJECT时：回退至s03调整超参数或回退至s02调整数据策略。
- 连续三次验收REJECT：建议切换方法族或寻求人工干预。

## 资源召回建议
- 当需要编排符号/稀疏方程发现的完整流程时召回。
- 配套卡片：cfd-symbolic-sparse-governing-equation-discovery（场景级）、各步骤任务卡。

## 证据来源
[1] 场景需求书 CFD_S045 workflow定义
[2] Universal Physics-Informed Neural Networks: Symbolic Differential Operator Discovery with Sparse Data, 2022
[3] Symbolic Physics Learner: Discovering governing equations via Monte Carlo tree search, 2022
