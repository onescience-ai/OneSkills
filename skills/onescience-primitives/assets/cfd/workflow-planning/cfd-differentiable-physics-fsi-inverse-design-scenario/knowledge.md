# 可微物理流固耦合逆向设计场景

## 适用范围
面向流固耦合轨迹与目标响应数据，完成可微物理流固耦合逆向设计的端到端场景。适用于采用可微物理（Differentiable Physics）或图模拟器（Graph Simulator）模型，从流固耦合轨迹数据中学习物理规律，并通过逆向优化生成满足目标性能的设计方案。该场景产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 输入
- 流固耦合轨迹数据（位移、速度、压力、应力等时间序列）
- 目标响应数据（目标性能指标、约束条件）
- 数据契约（变量、单位、网格拓扑、坐标系定义）

## 输出
- 可复现模型（可微物理模型或图模拟器）
- 逆向设计结果（候选设计方案、Pareto前沿）
- 物理一致性评估（误差分析、守恒性验证）
- 适用域报告（几何或工况外推测试结果）
- 验收结论（PASS/REJECT/BLOCKED）

## 流程节点
```
s01 数据接入与契约核验
  │  核验样本、变量、单位、网格坐标及许可
  │  输出：dataset_manifest.json, data_contract.json, data_audit.md
  │  质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
  ▼
s02 预处理与数据切分
  │  统一物理量与表示，按几何、工况或时间构造无泄漏切分
  │  输出：train/validation/test_manifest.json, normalization.json
  │  质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
  ▼
s03 模型配置与训练
  │  训练Differentiable physics、Graph simulator完成指定输入到目标物理量的映射
  │  输出：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
  │  质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
  ▼
s04 候选生成与约束优化
  │  围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹
  │  输出：design_candidates/, optimization_history.csv, pareto_front.json
  │  质量门禁：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签
  ▼
s05 任务验收与适用域判定
     评估统计误差、关键物理约束、泛化能力和计算收益
     输出：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
     质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分方式 | 按几何、完整轨迹或物理工况为单位 | 场景需求书s02 | 不得把同一轨迹的帧随机打散 |
| 验收指标 | objective_improvement, constraint_violation, CFD_validation_error | 场景需求书s05 | 统计与物理指标必须同时报告 |
| 外推测试 | 需要（默认true） | 场景需求书s05 | 几何或工况外推测试决定适用域边界 |
| 逆向优化 | 需要保留完整搜索轨迹 | 场景需求书s04 | 不得把代理预测直接当作高保真认证结果 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train/val/test比例 | 0.7/0.15/0.15 | 场景需求书s02 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 随机种子 | 42 | 场景需求书 | |
| 相对误差门限 | 0.1 | 场景需求书s05 | |
| 训练轮次 | 100 | 场景需求书s03 | |
| 批大小 | 8 | 场景需求书s03/s04 | |
| 学习率 | 0.001 | 场景需求书s03 | |

## 边界与分流
- s01 缺少必填输入时返回BLOCKED并列出缺项
- s02 切分配置无效时回退到默认比例（0.7/0.15/0.15）
- s03 训练损失为NaN/Inf时REJECT并检查数据或模型配置
- s04 候选不满足几何和物理硬约束时重新生成
- s05 未通过验收时输出REJECT并附详细原因，域外工况需CFD复核

## 质量检查
- 每步有独立质量门禁，未通过则阻断后续步骤
- 全流程随机种子可复现
- 所有中间产物可追溯
- 候选生成与优化需保留完整搜索轨迹
- 物理一致性评估需包含守恒性验证

## 回退策略
- 任一步骤BLOCKED/REJECT时，定位具体缺项或失败原因后重试
- 模型训练不收敛时调整超参数或检查数据质量
- 优化搜索失败时调整约束条件或搜索策略
- 适用域判定不通过时扩大训练数据范围或简化模型

## 资源召回建议
- 本卡片为场景级卡片，可被以下需求召回：可微物理逆向设计、流固耦合逆向优化、Differentiable physics inverse design
- 配套工作流卡片：cfd-differentiable-physics-fsi-inverse-design-workflow
- 配套任务卡片：各步骤独立任务卡片

## 证据来源
[1] PRDP_ Progressively Refined Differentiable Physics
[2] PETAL_ Physics Emulation Through Averaged Linearizations for Solving Inverse Problems