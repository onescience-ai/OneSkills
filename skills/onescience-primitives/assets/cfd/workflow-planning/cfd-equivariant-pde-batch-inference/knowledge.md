# 等变PDE批量推理与物理恢复

## 适用范围

本卡片服务于等变PDE模型的推理阶段。在模型训练完成后，需要在独立测试集上进行批量推理，将模型输出反归一化恢复为物理单位，并保存逐样本预测结果。适用于任何需要在测试集上评估等变网络PDE预测性能的场景。不适用于：在线实时推理（需额外部署流程）；仅需单样本快速测试（可简化流程）。

## 输入

- 模型检查点（{CHECKPOINT}）：通过训练门限的best权重
- 计算设备（{DEVICE}）：CPU或CUDA设备
- 推理批大小（{BATCH_SIZE}）：按显存调整
- s02输出的test_manifest.json与normalization.json

## 输出

- predictions/：逐样本预测结果目录
- inference_manifest.json：推理结果清单
- timing.csv：逐样本推理耗时

## 流程节点

1. **模型加载** → 加载{CHECKPOINT}，设置为eval模式
2. **数据加载** → 基于test_manifest.json构建DataLoader
3. **批量推理** → 前向传播，收集模型输出
4. **反归一化** → 使用normalization.json恢复物理单位
5. **物理量恢复** → 恢复坐标网格、边界掩膜、任务派生量
6. **结果保存** → 逐样本保存预测结果和耗时

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 无NaN/Inf | 预测结果无NaN或Inf | 场景JSON s04 quality_gate | 强制门禁 |
| 形状单位正确 | 预测形状与输入匹配，单位已恢复 | 场景JSON s04 quality_gate | 强制门禁 |
| 唯一结果 | 每个测试样本有唯一结果 | 场景JSON s04 quality_gate | 强制门禁 |
| 无标签泄露 | 推理未使用测试目标校正 | 场景JSON s04 quality_gate | 强制门禁 |
| 反归一化可逆 | 使用训练时保存的变换参数 | 场景JSON s04 prompt | 禁止重新计算 |

### 校准数值（来自CFD_S063场景）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认设备 | cuda | 场景JSON s04 default | |
| 默认批大小 | 8 | 场景JSON s04 default | |

## 边界与分流

- **显存不足**：减小BATCH_SIZE或使用推理模式梯度关闭
- **反归一化参数缺失**：BLOCKED，需返回s02重新生成normalization.json
- **预测出现NaN/Inf**：记录具体样本，报告为推理失败，不参与后续评估

## 质量检查

- 预测无NaN或Inf且形状单位正确（质量门禁）
- 每个测试样本有唯一结果（质量门禁）
- 推理未使用测试目标校正（质量门禁）
- timing.csv记录完整推理耗时

## 回退策略

- 检查点损坏：返回s03重新训练
- 推理结果全部异常：检查数据契约一致性与模型加载是否正确

## 资源召回建议

当用户任务涉及以下场景时召回：
- "PDE推理"、"等变网络推理"、"批量推理"、"物理量恢复"
- 配套卡片：cfd-equivariant-pde-model-training（前一步训练）、cfd-symmetric-pde-acceptance-applicability（下一步验收）

## 证据来源

场景CFD_S063 workflow step s04定义。
