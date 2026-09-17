# Model Training for Stochastic PDE

## 适用范围
本任务面向随机微分方程（SDE）与高维偏微分方程（PDE）求解的模型训练阶段，使用物理信息驱动的方法（Physics-informed stochastic solver或Gaussian process）完成从输入数据到目标物理量的映射训练。记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。适用于所有需要物理信息PDE求解的模型训练场景。

## 输入
- {MODEL_NAME}：模型名称（Physics-informed stochastic solver、Gaussian process），必填
- {TRAIN_CONFIG}：训练配置（框架、epoch、batch_size、学习率、随机种子、早停策略），必填
- {INIT_CHECKPOINT}：初始权重（可选预训练权重），可选

## 输出
- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：环境依赖

## 流程节点
```
1. 加载s02切分与统计量 → 2. 初始化模型 → 3. 检查初始权重兼容性（如提供）
→ 4. 训练循环（前向传播、损失计算、反向传播） → 5. 验证循环
→ 6. 早停判断 → 7. 保存最佳权重 → 8. 记录训练日志
```

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 判据 | 说明 |
|------|------|------|
| 训练损失收敛 | 损失为有限值且逐步下降 | NaN/Inf表示训练失败 |
| 验证损失稳定 | 验证损失不发散 | 过拟合信号 |
| 最佳权重可加载 | checkpoint可被正确加载 | 结构兼容性检查 |
| 随机种子可复现 | 相同种子产生相同结果 | 配置环境一致 |
| 代码版本记录 | 代码版本、依赖明确记录 | 支持复现 |

### 校准数值（场景专属值，供量级校准）
以下数值来自 CFD_S046 场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | 场景需求书 | 深度学习框架 |
| 默认epoch | 100 | 场景需求书 | 训练轮数 |
| 默认batch_size | 8 | 场景需求书 | 批大小 |
| 默认学习率 | 0.001 | 场景需求书 | 标准PINN学习率 |
| 默认随机种子 | 42 | 场景需求书 | 可复现性 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心轮数 |

## 边界与分流
- **训练损失为NaN/Inf**：降低学习率、检查数据归一化、增加正则化
- **过拟合**：增加早停耐心、添加dropout/正则化、增加数据增强
- **欠拟合**：增加网络容量、调整损失权重、增加训练轮数
- **初始权重不兼容**：跳过预训练权重，从头训练
- **缺少必填输入**：返回BLOCKED，列出缺失项

## 质量检查
- 训练损失曲线监控（有限值、单调下降）
- 验证损失曲线监控（不过拟合）
- 最佳权重可重新加载测试
- 训练配置完整性检查
- 环境依赖记录

## 回退策略
- 训练不收敛：降低学习率、调整网络架构、增加正则化
- 过拟合：增加数据量、调整早停策略、简化模型
- 权重保存失败：检查磁盘空间、调整保存策略

## 资源召回建议
当遇到以下需求时召回本卡片：
- Physics-informed neural network (PINN) 训练
- Gaussian process在PDE求解中的训练
- 物理信息模型的训练配置

配套卡片：cfd-sde-highdim-pde-preprocessing-split（预处理），cfd-sde-highdim-pde-equation-solve-residual（方程求解）

## 证据来源
[1] Physics-Informed Gaussians as Adaptive Parametric Mesh Representations, 2024
[2] Gaussian Process Priors for Systems of Linear Partial Differential Equations with Constant Coefficients, 2024
[3] Physics-Informed Kolmogorov-Arnold networks for viscoelastic fluid equations, arXiv:2608.29895, 2025
