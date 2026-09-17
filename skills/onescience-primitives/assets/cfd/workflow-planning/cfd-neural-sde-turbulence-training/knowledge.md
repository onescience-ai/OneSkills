# Neural SDE与概率粗粒化模型训练

## 适用范围

适用于训练Neural SDE closure和Probabilistic coarse-graining model两类湍流闭合模型。当需要从多尺度湍流数据学习随机闭合映射时，执行本步骤。

## 输入

- MODEL_NAME：模型名称（Neural SDE closure / Probabilistic coarse-graining model）
- TRAIN_CONFIG：训练配置（框架、超参数、随机种子）
- INIT_CHECKPOINT：可选预训练权重

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本与依赖信息

## 流程节点

1. 加载s02切分数据与统计量
2. 配置模型架构：
   - Neural SDE：学习耦合SDE系统 dz = γ_θ(z)dt + L_θ(t)dβ，其中宏/微尺度状态分别由f_θ和g_θ驱动 [2]
   - 概率粗粒化：编码器-粗粒化模型(CGM)-解码器三步架构，使用随机变分推断训练 [1]
3. 设置训练循环：前向传播→损失计算→反向传播→参数更新
4. 记录逐轮训练验证指标
5. 早停策略：验证损失连续patience轮未改善时停止
6. 保存最佳权重与训练配置

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景需求书 | 深度学习框架 |
| epochs | 100 | 场景需求书 | 默认训练轮数 |
| batch_size | 8 | 场景需求书 | 默认批大小 |
| learning_rate | 0.001 | 场景需求书 | 默认学习率 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| seed | 42 | 场景需求书 | 随机种子 |

## 方法细节

### Neural SDE Closure [2]
- 宏观尺度状态ζ在粗网格上演化
- 微观尺度状态η显式建模未解析动力学
- 耦合SDE系统：d[ζ;η] = [f_θ(ζ,φ(η)); g_θ(η,ψ(ζ))]dt + L_θ(t)dβ
- 使用Product of Experts似然强制尺度分离
- 模拟器免费的变分推断训练

### 概率粗粒化模型 [1]
- 编码器：从高维微结构λ_f映射到低维潜变量λ_c
- 粗粒化模型：以λ_c为输入的简化物理模型（如Darcy方程）
- 解码器：从CGM输出重建FGM响应
- 全贝叶斯训练：自动相关性确定(ARD)先验控制复杂度
- 适用于小数据 regime（N≤100训练样本）

## 边界与分流

- 缺少必填输入 → 返回BLOCKED
- 初始权重结构不兼容 → 拒绝加载，从头训练
- 训练损失出现NaN/Inf → 检查数据、调整学习率

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 回退策略

- 训练不收敛 → 调整学习率、批大小、模型架构
- 过拟合 → 增加正则化、减少模型复杂度、增加数据
- 欠拟合 → 增加模型容量、调整训练轮数

## 资源召回建议

- 需要了解Neural SDE架构时召回本卡
- 需要了解概率粗粒化方法时召回本卡
- 需要了解训练策略时召回本卡

## 证据来源

[1] Grigo, C., Koutsourelakis, P.-S. (2019). A physics-aware, probabilistic machine learning framework for coarse-graining. Journal of Computational Physics, 397, 108842.
[2] Ilersich, A.F., Nair, P.B. (2025). Learning Stochastic Multiscale Models. arXiv:2506.22655.
