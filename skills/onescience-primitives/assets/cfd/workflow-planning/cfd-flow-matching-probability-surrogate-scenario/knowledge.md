# Flow Matching 概率代理复杂流动场景

## 适用范围

本场景面向参数条件与流场分布样本，使用 Flow matching model 构建复杂流动的概率代理模型。适用条件：已采集足够覆盖目标工况范围的参数-流场配对样本（含输入参数场与目标物理量场），且目标是生成多样的、物理一致的流场预测分布而非单一确定性解。不适用场景：纯确定性代理（回归模型即可）、无参数条件的自由演化预测、或样本量极小（<50）无法支撑概率分布学习的情形。域外工况（超出训练参数范围的几何或流动条件）需经 CFD 复核后方可使用。

## 输入

- 参数条件与流场分布样本（{DATASET_PATH}目录或清单文件）
- 数据契约（{DATA_CONTRACT}，定义变量名、单位、网格坐标系）
- 验收指标列表（{METRICS}，如 distribution_distance、diversity、physics_residual、coverage）
- 切分配置（{SPLIT_CONFIG}，默认 train/val/test = 0.7/0.15/0.15，按几何或工况分组）

## 输出

- 可复现模型 checkpoint（best_checkpoint.pt）
- 训练配置与环境记录（train_config.json、environment.txt）
- 生成样本集（generated_samples/）与物理筛选结果（physics_filter.json）
- 验收评估报告（evaluation.json、applicability_report.md）
- 最终判定（PASS / REJECT / BLOCKED）

## 流程节点

1. 数据接入与契约核验 → 2. 预处理与数据切分 → 3. 模型配置与训练 → 4. 条件采样与物理一致性筛选 → 5. 任务验收与适用域判定

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | Flow matching model | [场景需求书] | 基于 ODE 的生成式概率模型 |
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| 默认 epochs | 100 | [场景需求书] | 可根据收敛情况调整 |
| 默认 batch_size | 8 | [场景需求书] | 按显存调整 |
| 默认 learning_rate | 0.001 | [场景需求书] | 优化器默认学习率 |
| early_stopping_patience | 15 | [场景需求书] | 验证集无改善时提前停止 |
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | train/val/test |
| 相对误差门限 | 0.1 | [场景需求书] | MAX_RELATIVE_L2 |
| 采样设备 | cuda | [场景需求书] | 默认GPU推理 |

## 边界与分流

- **样本不足**（<50）：概率代理无法可靠学习分布，建议转向确定性代理或数据增强
- **域外工况**：超出训练参数范围时，模型预测不可信，必须经 CFD 复核
- **物理筛选不合格**：若物理残差超过阈值且无合理解释，返回 BLOCKED 并要求 CFD 基线验证
- **训练不收敛**：验证损失持续发散时检查数据质量、学习率和模型容量
- **单样本不代表整体**：禁止用单个漂亮样本代表整体性能，必须报告分布覆盖

## 质量检查

- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏
- 三份切分的对象轨迹互斥
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 样本条件与随机种子可追溯
- 多样性和真实性同时评价
- 物理筛选前后统计均报告
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 数据质量不达标：返回 BLOCKED，列出缺项清单
- 训练失败：检查框架版本、依赖、随机种子，必要时降低学习率或增大 batch_size
- 物理筛选通过率极低：检查物理残差计算逻辑，或放宽筛选阈值重新评估
- 适用域判定 REJECT：明确列出域外工况范围，建议 CFD 复核

## 资源召回建议

当用户需要：(1) 构建复杂流动的概率预测代理，(2) 生成多样流场样本进行不确定性量化，(3) 使用 Flow matching model 进行 CFD 替代建模时召回本卡片。配套资源：cfd-flow-matching-probability-surrogate-workflow（工作流定义）、cfd-flow-matching-model-training（训练方法）、cfd-flow-matching-conditional-sampling-physics-filter（采样与筛选）、cfd-flow-matching-task-acceptance-applicability（验收判定）。可参考 cfd-diffusion-stochastic-pde-probability-prediction-scenario 了解扩散模型同类方案的对比。

## 证据来源

[1] Switched Flow Matching: Eliminating Singularities via Switching ODEs, 2024
[2] Physics vs Distributions: Pareto Optimal Flow Matching with Physics Constraints, 2024
[3] Dflow-SUR: Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching, arXiv:2512.08336, 2025
[4] GeoFunFlow-3D: A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries, arXiv:2604.23350, 2026
[5] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
