# 谱增强PINN模型训练

## 适用范围

**触发条件**：
- 谱增强PINN工作流的第三步：模型训练
- 已完成数据预处理与切分

**适用场景**：
- 训练Spectral PINN（基于谱分解+Neural ODE）求解PDE
- 训练SIREN（正弦表征网络）求解PDE
- 需要克服谱偏差的高频/多尺度PDE训练

**不适用场景**：
- 非谱增强的标准MLP-PINN训练
- 无PDE物理约束的纯数据驱动训练

## 输入

- train_manifest.json、validation_manifest.json（来自s02）
- normalization.json（归一化统计量）
- MODEL_NAME：Spectral PINN或SIREN
- TRAIN_CONFIG：超参数配置
- INIT_CHECKPOINT（可选）

## 输出

- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置记录
- training_metrics.csv：逐轮训练验证指标
- environment.txt：代码版本、依赖、随机种子

## 流程节点

### Step 1：模型架构配置
- **操作**：选择谱基类型（Fourier/自定义）、配置Neural ODE或SIREN网络
- **参数**：谱截断频率、网络宽度/深度、激活函数
- **质量门禁**：模型架构可实例化；参数维度匹配数据

### Step 2：初始化策略
- **操作**：谱分解投影、线性化PDE近似、Fourier乘子初始化
- **参数**：初始化方法、epsilon扰动
- **质量门禁**：初始化权重可加载；初始损失有限

### Step 3：损失函数配置
- **操作**：配置PDE残差损失、初始条件损失、边界条件损失权重
- **参数**：损失权重、自适应权重策略
- **质量门禁**：各损失项可计算；权重合理

### Step 4：训练执行
- **操作**：执行训练循环，记录逐轮指标，保存最佳权重
- **参数**：epochs、lr、batch_size、early_stopping
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 谱基类型 | Fourier（正弦/余弦） | [1] | 全局正交基 |
| Neural ODE求解器 | 4阶Runge-Kutta | [1] | 时间积分 |
| 初始化 | 线性化PDE + Fourier乘子 | [1] | 接近目标解的初始化 |
| 优化器 | Adam | [1] | 默认优化器 |
| 损失函数 | L_PDE + L_IC + L_BC | [1] | 物理信息损失 |

### 校准数值（体系专属，以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| NeuSA默认学习率 | 0.01（可高于baseline） | [1] | 因架构先验更强 |
| baseline学习率 | 0.001 | [1] | 标准PINN常用值 |
| 训练步数（NeuSA） | 200-2000步 | [1] | 远少于baseline的10000+步 |

## 边界与分流

- **初始化失败**：无法获得线性化近似 → 退化为标准Fourier Feature PINN
- **训练不收敛**：损失震荡或发散 → 降低学习率、调整损失权重、检查谱截断频率
- **GPU显存不足**：降低batch_size或谱截断频率

## 质量检查

- 训练损失收敛性检查
- 验证损失泛化性检查
- 最佳权重可重新加载验证
- 随机种子可复现性验证

## 回退策略

- 谱增强PINN不收敛 → 退回标准PINN + Fourier Feature层
- SIREN训练不稳定 → 调整初始化带宽或学习率

## 资源召回建议

- 当需要执行谱增强PINN模型训练时召回本卡
- 配套资源：cfd-spectral-pinn-preprocessing-splitting（上游）、cfd-spectral-pinn-equation-solving-residual-recovery（下游）

## 证据来源

[1] "Neuro-Spectral Architectures for Causal Physics-Informed Networks", Bizzi et al., NeurIPS 2025, DOI: 10.48550/arXiv.2509.04966
[2] "Simple initialization and parametrization of sinusoidal networks via their kernel bandwidth", Belbute-Peres & Kolter, arXiv 2022, DOI: 10.48550/arXiv.2211.14503
