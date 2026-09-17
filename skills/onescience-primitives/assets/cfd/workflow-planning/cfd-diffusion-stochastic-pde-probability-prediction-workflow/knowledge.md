# 扩散与随机过程时空场概率预测工作流

## 适用范围

本卡定义随机或混沌PDE时空数据概率预测的标准工作流，适用于使用Diffusion model与Stochastic process model进行时空场概率预测的任务。工作流覆盖从数据接入到适用域判定的完整生命周期，确保可复现性、物理一致性与工程可用性判定。不适用于确定性PDE求解、无概率输出需求的场景。

## 输入

- 随机或混沌PDE时空数据集（目录或清单文件）
- 数据集名称与来源版本
- 可选：数据契约定义（变量、单位、网格坐标）

## 输出

- 可复现模型（best_checkpoint.pt）
- 推理结果（predictions/）
- 评估报告（evaluation.json, applicability_report.md）
- 适用域判定（PASS/REJECT/BLOCKED）

## 流程节点

```
s01 数据接入与契约核验
  ↓ (dataset_manifest.json, data_contract.json, data_audit.md)
s02 预处理与数据切分
  ↓ (train/val/test manifests, normalization.json)
s03 模型配置与训练
  ↓ (best_checkpoint.pt, train_config.json, training_metrics.csv)
s04 批量推理与物理恢复
  ↓ (predictions/, inference_manifest.json, timing.csv)
s05 任务验收与适用域判定
  ↓ (evaluation.json, applicability_report.md, PASS_REJECT_BLOCKED.txt)
```

### s01 → s02 流转条件
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 无训练测试泄漏

### s02 → s03 流转条件
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

### s03 → s04 流转条件
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

### s04 → s05 流转条件
- 预测无NaN/Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景需求书CFD_S021] | 训练推理框架 |
| 默认模型 | Diffusion model, Stochastic process model | [场景需求书CFD_S021] | 双模型并行 |
| 相对L2门限 | 0.1 | [场景需求书CFD_S021] | 测试集放行阈值 |
| 切分比例 | 70/15/15 | [场景需求书CFD_S021] | train/val/test |
| 随机种子 | 42 | [场景需求书CFD_S021] | 可复现性 |
| 早停耐心 | 15 | [场景需求书CFD_S021] | early_stopping_patience |

## 边界与分流

- 任一阶段输入缺失 → 返回BLOCKED，列出缺项
- s01数据不可读 → BLOCKED，检查路径与格式
- s02切分泄漏 → 强制止止，重新切分
- s03训练不收敛 → 调整超参或架构，记录失败原因
- s04推理异常 → 检查预处理一致性
- s05 OOD测试 → 必须执行几何/工况外推测试

## 质量检查

各阶段质量门禁详见配套任务卡：
- s01: 数据可读、变量完整、无泄漏
- s02: 切分互斥、统计量来源正确、掩膜完整
- s03: 损失有限、权重可加载、种子可复现
- s04: 无NaN/Inf、单位正确、未用测试标签
- s05: 物理统计双报告、最差可追溯、适用域明确

## 回退策略

- 数据层失败 → 补充元数据重试
- 训练层失败 → 超参搜索+架构调整
- 推理层失败 → 预处理一致性检查
- 验收失败 → 失败模式分析+域外复核方案

## 资源召回建议

当任务涉及以下关键词时召回本卡：
- 扩散模型 + PDE + 概率预测工作流
- 随机过程 + 时空场 + 预测工作流
- Diffusion model + spatiotemporal workflow

配套任务卡：
- [cfd-pde-data-intake-contract-validation](../../task/cfd-pde-data-intake-contract-validation/)
- [cfd-pde-preprocessing-data-splitting](../../task/cfd-pde-preprocessing-data-splitting/)
- [cfd-diffusion-stochastic-model-training](../../task/cfd-diffusion-stochastic-model-training/)
- [cfd-pde-batch-inference-physical-recovery](../../task/cfd-pde-batch-inference-physical-recovery/)
- [cfd-probabilistic-prediction-acceptance-applicability](../../task/cfd-probabilistic-prediction-acceptance-applicability/)

## 证据来源

[1] 场景需求书 CFD_S021：扩散与随机过程时空场概率预测（workflow字段完整定义）
[2] DYffusion: A Dynamics-informed Diffusion Model for Spatiotemporal Forecasting（场景需求书引用）
[3] Deep learning for physical processes: Incorporating prior scientific knowledge, arXiv:1711.07970（场景需求书引用）
