# Physics-informed GAN 物理损失的正确计算方式

## 适用范围
面向 Physics-informed GAN（PiGAN）训练任务，确保物理约束损失（PDE 残差）正确参与梯度计算，使生成器同时优化数据匹配和物理一致性。适用于流体动力学、热传导等 PDE 约束的生成模型训练。

## 输入
- 生成器输入：坐标 (x, y, t) 需设置 `requires_grad=True` 且不 detach
- 生成器输出：速度场 (u, v)、压力场 p 等物理量
- PDE 定义：连续性方程、Navier-Stokes 方程等

## 输出
- 物理损失值：PDE 残差的均方误差
- 梯度信息：物理损失对生成器参数的非零梯度
- 训练稳定性：物理损失随 epoch 下降，不恒为零

## 流程节点
1. **坐标准备**：输入坐标设置 `requires_grad=True`，保留计算图
2. **前向传播**：生成器输出物理场 (u, v, p)
3. **自动微分**：使用 `torch.autograd.grad` 计算一阶和二阶偏导数
4. **PDE 残差计算**：代入 PDE 方程计算残差
5. **损失聚合**：物理损失 = 残差的均方误差
6. **反向传播**：物理损失对生成器参数求梯度

每步质量门禁：
- 坐标必须 `requires_grad=True`
- `autograd.grad` 输出不为 None
- 物理损失 > 0 且随训练下降

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 坐标 requires_grad | True | [D1] | 保留计算图，允许梯度回传 |
| 创建图标志 | create_graph=True | [D1] | 允许计算高阶导数 |
| 物理损失权重 | 1.0 | [D1] | 可调整以平衡数据损失和物理损失 |
| 残差计算方式 | 均方误差 | [D1] | 常用损失函数 |

## 边界与分流
- 如果物理损失恒为零：检查坐标是否 detach，检查计算图是否断开
- 如果梯度消失：调整学习率，检查激活函数
- 如果训练不稳定：降低物理损失权重，使用梯度裁剪

## 质量检查
- 验证点：物理损失 > 0
- 阈值：物理损失应随 epoch 下降
- 失败处理：重新检查计算图连通性

## 回退策略
- 如果自动微分失败：使用有限差分近似（精度较低）
- 如果训练不稳定：使用两阶段训练（先数据驱动，后物理约束）

## 资源召回建议
- 何时召回：当 Physics-informed GAN 物理损失恒为零时
- 配套资源：Physics-informed GAN 实现模板、PDE 定义规范

## 补充证据（开源文档/用户自有，可选）
[D1] PyTorch Autograd Documentation, PyTorch, v2.0.0, URL: https://pytorch.org/docs/stable/autograd.html（accessed_at 2026-09-17，交叉验证）
[D2] Physics-Informed Neural Networks: A Deep Learning Framework for Solving Forward and Inverse Problems Involving Nonlinear Partial Differential Equations, arXiv, v1, URL: https://arxiv.org/abs/1711.10561（accessed_at 2026-09-17，单源参考）

## 证据来源
[1] Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. Journal of Computational Physics, 378, 686-707. DOI: 10.1016/j.jcp.2018.10.045