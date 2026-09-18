# Normalizing Flow 湍流降阶任务训练配置与实现细节

## 适用范围
本规范适用于湍流降阶任务中 Normalizing Flow 模型的训练配置与实现，包括模型架构选择、损失函数设计、训练策略、超参数设置等。适用于需要训练 Normalizing Flow 模型以生成湍流场降阶表示的场景。不适用于其他生成模型（如 GAN、VAE）的训练。

## 输入
- 湍流场降阶表示数据（如本征正交分解系数、潜在向量）
- 模型架构配置（层数、隐藏单元数、激活函数等）
- 训练超参数（学习率、批大小、迭代次数等）

## 输出
- 训练好的 Normalizing Flow 模型检查点
- 训练配置文件（`train_config.json`）
- 训练指标文件（`training_metrics.csv`）
- 环境信息文件（`environment.txt`）

## 流程节点
1. **架构选择** → 选择适合湍流数据的 Normalizing Flow 架构（如 RealNVP、Glow、Masked Autoregressive Flow）
2. **数据预处理** → 对降阶表示数据进行标准化，使其均值为0、方差为1
3. **损失函数设计** → 使用负对数似然损失，可加入正则化项（如权重衰减）
4. **训练循环** → 优化损失函数，监控训练损失和验证损失
5. **模型评估** → 生成样本，计算统计指标（如均值、方差、功率谱）
6. **检查点保存** → 保存最佳模型检查点和训练配置

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 架构 | RealNVP 或 Masked Autoregressive Flow | 领域知识 | 适合高维连续数据 |
| 层数 | 4-8 | 领域知识 | 平衡表达能力与训练难度 |
| 隐藏单元数 | 128-256 | 领域知识 | 根据数据维度调整 |
| 学习率 | 1e-4 到 1e-3 | [D1] | 使用学习率调度 |
| 批大小 | 64-256 | 领域知识 | 根据GPU内存调整 |
| 迭代次数 | 1000-5000 | 领域知识 | 监控验证损失早停 |

## 边界与分流
- **数据维度不匹配**：若降阶表示维度与模型架构不匹配，需调整网络结构或进行额外降维
- **训练不收敛**：若训练损失不下降，尝试降低学习率、增加正则化或调整架构
- **生成样本质量差**：若生成样本统计特性与真实数据不符，增加训练数据或调整模型复杂度

## 质量检查
- 验证训练损失收敛（下降后趋于稳定）
- 检查生成样本的统计特性（均值、方差）与真实数据一致
- 确保模型检查点文件完整（包含模型参数和优化器状态）
- 验证训练配置文件包含所有超参数

## 回退策略
- 若 Normalizing Flow 训练失败，可尝试使用 GAN 模型作为替代
- 若生成样本质量差，可尝试使用更简单的降阶方法（如线性降维）
- 若计算资源不足，可减少模型规模或使用混合精度训练

## 资源召回建议
当任务涉及湍流生成模型训练、Normalizing Flow 实现、降阶模型评估时，应召回本卡片。配套资源：`cfd-turbulence-data-contract-specification`（数据契约生成）、`cfd-gan-turbulence-training`（GAN 模型训练）。

## 补充证据（开源文档/用户自有，可选）
[D1] Free energy calculation of crystalline solids using normalizing flow, Ahmad et al., Model. Simul. Mater. Sci. Eng., 2022, URL: https://arxiv.org/abs/2111.01292v2（accessed_at: 2026-09-17，论文证据）

## 证据来源
[1] Free energy calculation of crystalline solids using normalizing flow, Ahmad et al., arXiv:2111.01292, 2021