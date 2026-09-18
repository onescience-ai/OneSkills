# CFD多物理算子迁移工作流

## 适用范围
本卡片服务的通用问题类是：将预训练的神经算子或PDE基础模型迁移到新的CFD多物理系统，包括数据准备、模型选型配置、训练微调和推理后处理全流程。适用于Navier-Stokes方程、湍流模拟、多相流、流固耦合等CFD场景的模型迁移任务。

## 输入
- 目标CFD系统的PDE定义和边界条件
- 预训练数据集（如有）或合成数据生成脚本
- 计算资源规格（GPU型号、显存、集群配置）
- 迁移学习目标（精度要求、推理速度约束）

## 输出
- 迁移后的模型检查点（best_checkpoint.pt）
- 训练配置文件（train_config.json）
- 训练指标日志（training_metrics.csv）
- 推理结果（predictions/目录、inference_manifest.json）
- 模型性能评估报告

## 流程节点

### 1. 预训练数据获取与验证
**操作**：从权威数据集库获取多物理预训练数据
**数据集来源**：
- **BubbleML**：NeurIPS 2023 Spotlight，多相沸腾过程数据集，包含流场、温度场、相变数据
- **RealPDEBench**：ICLR 2026 Oral，首个带有真实世界测量数据的科学ML基准，包含cylinder、fsi、foil、combustion等场景
- **Navier-Stokes Dataset**：HuggingFace上的NS方程求解数据

**数据格式要求**：
- HDF5或Arrow格式存储
- 包含速度场(u, v, p)、压力场、温度场等物理量
- 时间序列数据，支持自回归训练
- 网格信息和归一化参数

**质量门禁**：
- 检查数据完整性（无NaN/Inf值）
- 验证物理量单位一致性
- 确认边界条件定义正确

### 2. 模型选型与配置
**可用神经算子架构**：
- **FNO (Fourier Neural Operator)**：官方实现见neuraloperator库（3.9k stars），支持PyTorch生态系统
- **DeepONet**：基于通用逼近定理的算子网络
- **CoDA-NO**：NeurIPS 2024，用于单到多物理PDE适配的神经算子
- **SFNO (Spatiotemporal FNO)**：时空傅里叶神经算子，适用于时间序列CFD问题

**模型配置参数**：
| 参数 | 典型值 | 说明 |
|------|--------|------|
| n_modes | (64, 64) | 傅里叶模式数量 |
| hidden_channels | 64-128 | 隐藏层通道数 |
| in_channels | 2-5 | 输入通道数（取决于物理量） |
| out_channels | 1-3 | 输出通道数 |
| factorization | tucker | 权重分解方式 |
| rank | 0.1 | 分解秩 |

**计算资源需求**：
- 最低配置：单卡GPU（≥16GB显存）
- 推荐配置：多卡GPU并行（Pipeline Parallelism + Tensor Parallelism）
- 内存需求：取决于模型大小和批处理大小

### 3. 迁移学习训练
**训练策略**：
1. **预训练权重加载**：从官方库或HuggingFace加载预训练权重
2. **微调超参数**：
   - 学习率：1e-4 到 1e-5
   - 批大小：16-64（根据显存调整）
   - 训练轮数：50-200 epochs
   - 优化器：AdamW
3. **训练监控**：
   - 损失函数：MSE或相对L2误差
   - 验证间隔：每个epoch
   - 早停策略：验证损失连续10个epoch不下降则停止

**质量检查点**：
- 损失曲线收敛
- 验证误差低于阈值（如1e-2）
- 模型检查点保存

### 4. 推理与后处理
**推理流程**：
1. 加载最佳检查点和测试数据
2. 执行模型推理
3. 后处理：单位恢复、网格映射、物理量派生

**后处理工具链**：
- **单位恢复**：使用保存的normalization.json进行逆归一化
- **网格映射**：利用CFD求解器输出格式进行网格坐标转换
- **物理量派生**：
  - 涡量计算：ω = ∂v/∂x - ∂u/∂y
  - 压力场重构
  - 边界层分析

**Python库推荐**：
- NumPy/SciPy：数值计算
- xarray：多维数组处理
- matplotlib/plotly：可视化
- h5py/h5md：数据I/O

**质量门禁**：
- 检查预测场无NaN/Inf值
- 验证物理量范围合理性
- 确认网格分辨率正确

### 5. 评估与验证
**评估指标**：
- RMSE（均方根误差）
- MAE（平均绝对误差）
- 相对L2误差
- R²（决定系数）
- 能量谱误差（对湍流问题）

**对比基准**：
- 传统CFD求解器结果
- 其他神经算子模型
- 真实世界测量数据（如有）

## 关键参数

### 通用判据（方法层）
| 参数 | 判据值 | 来源 | 说明 |
|------|--------|------|------|
| 数据完整性 | 无NaN/Inf | [1][2] | 数据质量的基本要求 |
| 物理量单位 | SI制或一致单位 | [1][2] | 确保物理意义正确 |
| 网格分辨率 | ≥64×64 | [3][4] | FNO等模型的最低要求 |
| 训练收敛 | 损失下降>90% | [3][4] | 训练充分性指标 |
| 推理精度 | 相对误差<1e-2 | [3][5] | 科学计算级精度要求 |

### 校准数值（体系专属）
以下数值来自具体CFD系统，供量级校准；其他体系需以自身证据重新锚定。

**BubbleML数据集**：
- 流体：水、FC-72、HFE-7100
- 温度范围：25-200°C
- 网格分辨率：128×128
- 时间步长：0.01-0.1s

**RealPDEBench数据集**：
- 场景：cylinder、fsi、foil、combustion
- 真实数据轨迹：30-98条
- 模拟数据轨迹：30-99条
- 评估指标：RMSE、MAE、R²等9项

## 边界与分流

**前提1：预训练数据可获取**
- 若BubbleML/RealPDEBench等公开数据集不满足需求，转向合成数据生成（使用CFD求解器生成训练数据）
- 若数据格式不匹配，使用数据适配器进行格式转换

**前提2：计算资源充足**
- 若单卡GPU显存不足，启用混合精度训练或模型并行
- 若本地算力不足，考虑云GPU服务或超算平台（如SCNet）

**前提3：模型架构适配**
- 若FNO不适用于目标PDE，尝试DeepONet或其他算子网络
- 若需要多物理耦合，使用CoDA-NO等专门设计的架构

## 质量检查
1. **数据质量检查**：完整性、一致性、物理合理性
2. **模型训练检查**：收敛性、过拟合检测、梯度稳定性
3. **推理结果检查**：精度、物理一致性、边界条件满足
4. **性能对比检查**：与基准方法的定量比较

## 回退策略
1. **数据不足**：使用数据增强或迁移学习减少数据需求
2. **算力不足**：降低模型复杂度或使用模型压缩技术
3. **精度不达标**：调整超参数或尝试不同模型架构
4. **训练失败**：检查数据质量、降低学习率、增加正则化

## 资源召回建议
**何时召回本卡片**：
- 用户需要将预训练CFD模型迁移到新系统
- 需要获取多物理预训练数据集
- 需要配置神经算子训练流程
- 需要科学计算模型的推理后处理指导

**配套资源**：
- `neuraloperator`库：FNO等模型的官方实现
- `BubbleML`数据集：多相流预训练数据
- `RealPDEBench`：带有真实世界数据的基准
- `CoDA-NO`：多物理PDE适配的神经算子
- `torch-cfd`：PyTorch中的CFD求解器

## 证据来源
[1] BubbleML: A Multi-Physics Dataset and Benchmarks for Machine Learning, Hassan et al., NeurIPS 2023
[2] RealPDEBench: A Benchmark for Complex Physical Systems with Paired Real-World and Simulated Data, Hu et al., ICLR 2026
[3] Pretraining Codomain Attention Neural Operators for Solving Multiphysics PDEs, Rahman et al., NeurIPS 2024
[4] A Library for Learning Neural Operators, Kossaifi et al., arXiv 2025
[5] Spectral-Refiner: Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows, Cao et al., ICLR 2025
