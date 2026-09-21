# OpenFold 计算资源需求与 GPU 依赖

## 适用范围

面向 OpenFold/AlphaFold2 风格蛋白质结构预测模型的计算资源规划与 GPU 环境配置。涵盖训练与推理阶段的硬件需求、显存预算、CUDA 兼容性要求，以及无 GPU 环境下的降级策略。适用于在部署 OpenFold 前评估计算资源是否满足需求的场景。

## 输入

- 目标蛋白质序列（FASTA 格式）
- 模型权重文件（.pt 或 .npz 格式）
- 训练数据集（OpenProteinSet，用于从零训练）
- 硬件环境信息（GPU 型号、显存、CUDA 版本）

## 输出

- 资源需求评估报告
- GPU 配置建议
- 降级策略方案（如适用）

## 流程节点

### 节点 1：GPU 可用性检查

操作：检测系统 GPU 环境

检查项：
- `torch.cuda.is_available()` 返回 True
- CUDA 版本与 PyTorch 兼容
- GPU 显存容量 ≥ 16GB（推荐 A100 40GB 或更高）

工具：PyTorch CUDA 检测

质量门禁：GPU 可用且显存充足

### 节点 2：显存预算评估

操作：评估模型所需的显存

关键数值（来自 OpenFold 论文 [1]）：
| 场景 | 显存需求 | 说明 |
|------|----------|------|
| 推理（单序列） | ~8-16GB | 取决于序列长度 |
| 训练（从零） | ~32-80GB | 需要多卡或大显存 GPU |
| DeepSpeed 推理 | 显存降低 13x | 峰值显存 |
| 长序列（>4000 残基） | 需 A100 80GB | 单卡最大长度 |

工具：显存估算脚本

质量门禁：显存预算充足，预留 20% 余量

### 节点 3：CUDA 兼容性验证

操作：验证 CUDA 与 PyTorch 版本兼容

检查项：
- CUDA 版本 ≥ 11.6（推荐 11.8 或 12.x）
- PyTorch 版本与 CUDA 版本匹配
- cuDNN 版本兼容

工具：`nvcc --version`、`python -c "import torch; print(torch.version.cuda)"`

质量门禁：所有版本兼容

### 节点 4：降级策略评估

操作：当 GPU 不可用时的替代方案

降级选项：
1. **CPU 推理**：性能下降 10-100x，仅适用于小规模测试
2. **DeepSpeed ZeRO-Inference**：降低显存需求
3. **云 GPU 服务**：使用 AWS/GCP/Azure GPU 实例
4. **混合精度训练**：使用 bf16/fp16 降低显存

工具：环境配置脚本

质量门禁：降级方案可执行

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最低 GPU 显存 | 16GB | [1] | 推理最低要求 |
| 推荐 GPU | NVIDIA A100 40GB | [1] | 训练和推理 |
| CUDA 最低版本 | 11.6 | [1] | PyTorch 兼容 |
| 长序列 GPU | A100 80GB | [1] | >4000 残基 |
| DeepSpeed 加速 | 2-3x | [1] | 推理加速 |
| DeepSpeed 显存降低 | 13x | [1] | 峰值显存 |

### 校准数值

以下数值来自 OpenFold 实践，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| OpenFold vs AlphaFold 推理速度 | 最快 2x | [1] | Ampere GPU |
| FlashAttention 加速 | 2-4x | [1] | 注意力计算 |
| 训练 batch size | 1-4 | [1] | 取决于显存 |
| 梯度累积步数 | 1-16 | [1] | 有效 batch size |

## 边界与分流

- **前提 1**：GPU 可用且 CUDA 兼容 → 否则进入降级策略评估
- **前提 2**：显存 ≥ 16GB → 否则考虑 DeepSpeed 或云 GPU
- **前提 3**：训练场景需 ≥ 32GB 显存 → 否则仅支持推理

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| GPU 可用性 | True | 启用 CPU 降级 |
| CUDA 版本 | ≥ 11.6 | 升级 CUDA |
| 显存容量 | ≥ 16GB | 使用 DeepSpeed 或云 GPU |
| 推理完成 | 无 OOM 错误 | 减小 batch size |

## 回退策略

1. GPU 不可用 → 使用 CPU 模式（性能下降，仅测试用）
2. 显存不足 → 启用 DeepSpeed ZeRO-Inference
3. CUDA 版本不兼容 → 使用 Docker 容器（nvidia/cuda 镜像）
4. 无本地 GPU → 使用 Google Colab（免费 T4 GPU）或云服务

## 资源召回建议

- 当用户提到 OpenFold 安装、环境配置时召回本卡
- 当需要评估 GPU 资源是否满足 OpenFold 需求时召回本卡
- 配套资源：
  - `bio-openfold-standard-workflow`（标准工作流）
  - `bio-openfold-offline-environment-setup`（离线环境配置）

## 证据来源

[1] Ahdritz G, Bouatta N, Floristean C, et al. OpenFold: retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization. *Nature Methods*, 2024, 21(8): 1514-1524. DOI: 10.1038/s41592-024-02272-z
