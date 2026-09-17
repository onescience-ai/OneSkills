# 批量推理与物理恢复（Neural ODE动力学学习）

## 适用范围

稳定性约束神经微分方程建模流程的第四步：在独立测试集推理，恢复原始单位、网格和物理派生量。适用于将模型预测从归一化空间转换回物理空间，确保预测结果可用于工程评估。

## 输入

- {CHECKPOINT}: 模型权重（必填），通过训练门限权重
- {DEVICE}: 计算设备（必填），默认cuda
- {BATCH_SIZE}: 推理批大小（可选），默认8

## 输出

- predictions/: 预测结果目录（逐样本）
- inference_manifest.json: 推理清单
- timing.csv: 耗时记录

## 流程节点

```
加载checkpoint与数据契约 → 测试集推理 → 反归一化恢复物理单位 → 恢复坐标网格/边界掩膜 → 计算任务派生量 → 保存逐样本结果与耗时
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 推理设备 | cuda | [场景需求书s04] | 默认GPU，可降级CPU |
| 推理批大小 | 8 | [场景需求书s04] | 按显存调整 |
| 反归一化 | 必需 | [场景需求书s04] | 恢复原始物理单位 |

## 边界与分流

- GPU不可用 → 降级到CPU推理（耗时增加）
- 显存不足 → 减小batch_size
- checkpoint不可加载 → 检查模型架构版本兼容性
- 反归一化失败 → 检查normalization.json完整性

## 质量检查

- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正（禁止用测试标签修正预测）

## 回退策略

- GPU不可用 → 降级到CPU推理
- 显存不足 → 减小batch_size
- 反归一化失败 → 保留归一化空间结果，标注警告

## 资源召回建议

- 本卡片为任务级卡片，对应工作流s04步骤
- 配套场景卡：cfd-stability-constrained-neural-ode-dynamics-learning
- 配套工作流卡：cfd-stability-constrained-neural-ode-workflow

## 证据来源

[1] CFD_S065场景需求书, scenario_catalogs/fluid/, 2026
