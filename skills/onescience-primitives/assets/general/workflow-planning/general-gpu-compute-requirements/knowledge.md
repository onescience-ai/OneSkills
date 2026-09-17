# 蛋白质结构预测模型 GPU 计算需求

## 适用范围

面向蛋白质结构预测（AlphaFold2/OpenFold 风格）任务的 GPU 资源评估与配置。覆盖单体/多聚体推理、长序列处理、不同精度模式下的显存需求估算，以及 DeepSpeed/FlashAttention 等加速技术的选型。同类任务如分子动力学模拟、蛋白质折叠训练亦可参考本卡的显存估算方法。

## 输入

- 目标蛋白质序列长度（残基数）
- 推理/训练模式选择
- 可用 GPU 型号与数量
- 精度要求（FP32/TF32/BF16/FP16）

## 输出

- GPU 显存需求估算
- 推荐精度配置
- 加速技术选型建议
- 性能基准数据

## 流程节点

### 1. 序列长度与显存关系评估

操作：根据输入序列长度估算基础显存需求

参数：
- 序列长度 L（残基数）
- MSA 深度（序列数）
- 模板数量

工具：经验公式 + 历史数据

质量门禁：确认估算值不超过目标 GPU 的可用显存

### 2. 精度模式选择

操作：根据精度-性能权衡选择合适模式

| 精度模式 | 显存占用 | 速度 | 适用场景 |
|----------|----------|------|----------|
| FP32 | 1.0x | 基准 | 训练、高精度推理 |
| TF32 | ~0.75x | 1.3x加速 | Ampere+ GPU 推理 |
| BF16 | ~0.5x | 1.5x加速 | 大批量推理 |
| FP16 | ~0.5x | 1.5x加速 | 不推荐（数值不稳定） |

工具：`--precision` 参数

质量门禁：验证精度选择不影响结果质量

### 3. 显存优化技术选型

操作：选择合适的显存优化技术

技术选项：
- **DeepSpeed DS4Sci**: 显存峰值降低 13x，推理加速 2-3x
- **FlashAttention**: 适合 <1000 残基序列
- **cuEquivariance**: 适合 >1000 残基，显存更低
- **低显存注意力 (LMA)**: 速度换显存
- **CPU Offloading**: 极端长序列的最后手段

工具：`--use_deepspeed_inference`, `--use_flash`, `--long_sequence_inference`

质量门禁：确认优化后显存低于 GPU 限制

### 4. 多卡并行评估

操作：评估是否需要多卡并行

参数：
- 单卡显存容量
- 序列长度
- 批量大小

工具：Pipeline Parallelism / Tensor Parallelism

质量门禁：验证多卡通信开销可接受

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| FP32→TF32 显存节省 | ~25% | [D1] | Ampere+ GPU |
| FP32→BF16 显存节省 | ~50% | [D1] | 需要 BF16 支持 |
| DeepSpeed 显存降低 | 13x | [D1] | 峰值显存 |
| DeepSpeed 推理加速 | 2-3x | [D1] | 无显著额外显存 |
| FlashAttention 适用阈值 | <1000 残基 | [D1] | 长序列不稳定 |
| cuEquivariance 加速 | 1.2-1.5x | [D1] | 在 DeepSpeed 基础上 |

### 校准数值

以下数值来自 OpenFold 实践，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 松源 | 说明 |
|------|-----|------|------|
| A100 单卡最大序列长度 | ~4600 残基 | [D1] | 使用所有优化 |
| 长序列优化组合 | average_templates + LMA + offload | [D1] | 最保守设置 |
| 推荐 GPU 架构 | Ampere (A100) 或更新 | [D1] | TF32/BF16 支持 |
| 推荐显存 | ≥24GB | [D1] | 单卡推理 |

## 边界与分流

- **前提 1**：GPU 支持 CUDA 12+ → 否则需降级 PyTorch 版本
- **前提 2**：序列长度 <4000 残基 → 否则需要 CPU Offloading
- **前提 3**：有 NVIDIA GPU → 否则考虑 CPU-only 模式（性能极低）

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| `torch.cuda.is_available()` | True | 安装 CUDA 版 PyTorch |
| 显存峰值 | < GPU 可用显存 | 启用更多优化技术 |
| 推理时间 | 在可接受范围内 | 调整批量大小或精度 |

## 回退策略

1. 单卡显存不足 → 启用 DeepSpeed + CPU Offloading
2. 仍不足 → 减小批量大小或序列长度
3. 无 GPU → 使用 CPU-only 模式（性能极低，仅用于测试）
4. 多卡通信瓶颈 → 调整并行策略

## 资源召回建议

- 当任务涉及 GPU 环境配置时召回本卡
- 当 preflight 检查显示 CUDA 不可用时召回本卡
- 配套资源：`general-scientific-computing-offline-installation`（环境安装）

## 补充证据

[D1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html (accessed_at, 官方文档)

## 证据来源

[1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html
[2] OpenFold README - Features Section, aqlaboratory, GitHub, 2024, URL: https://github.com/aqlaboratory/openfold
