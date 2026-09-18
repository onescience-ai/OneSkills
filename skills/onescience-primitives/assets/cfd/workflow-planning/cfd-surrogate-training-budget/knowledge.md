# CFD代理模型训练时间与算力预算估算

## 适用范围

面向CFD代理模型训练任务，提供不同模型架构在不同数据规模下的训练时间预算估算方法和算力需求参考基准。适用于工作流规划阶段的时间预算设置、资源分配决策和超时风险评估。

## 输入

- 模型架构类型（MLP、GPR、神经网络、深度学习模型）
- 训练数据规模（样本数、特征维度）
- 硬件配置（GPU型号/数量、CPU核心数、内存）
- 训练超参数（epochs、batch_size、学习率）

## 输出

- 预计训练时间（小时/天）
- 算力需求估算（GPU-hours、CPU-hours）
- 资源配置建议

## 流程节点

1. **数据规模评估** → 统计训练样本数、特征维度、数据加载开销
2. **模型复杂度分析** → 评估模型参数量、计算图复杂度
3. **硬件基准测试** → 基于历史数据或快速profiling获取吞吐量参考值
4. **时间预算计算** → 结合数据规模、模型复杂度、硬件性能估算总训练时间
5. **风险缓冲设置** → 添加1.5-2x安全系数应对数据加载、IO等非计算开销

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 学习曲线幂律指数 | α ∈ [0.3, 0.8] | [1] | 性能随数据量增长的衰减速率，用于外推训练时间 |
| GPU利用率目标 | ≥70% | 经验值 | 低于此值需优化数据加载或batch_size |
| 安全系数 | 1.5-2.0x | 经验值 | 覆盖IO、内存交换、异常重试等非计算开销 |
| GPR训练复杂度 | O(n³) | [2] | 高斯过程回归对样本数敏感，1000+样本需考虑稀疏近似 |

### 校准数值（CFD代理模型场景）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MLP（100-1000样本） | 0.1-2 GPU-hours | [3] | 单层/双层MLP，CPU可完成 |
| GPR（100-500样本） | 0.01-0.5 CPU-hours | [2] | 小规模数据快速，大规模需稀疏近似 |
| 深度神经网络（1000+样本） | 2-20 GPU-hours | [3] | 需GPU加速，取决于网络深度和数据维度 |
| BlendedNet（8830 RANS cases） | 约10-50 GPU-hours | [3] | 999几何×9飞行条件，PointNet+FiLM架构 |

## 边界与分流

- **数据规模 < 100样本**：GPR等核方法更高效，避免深度学习过拟合
- **数据规模 > 10000样本**：考虑 mini-batch训练、数据并行、分布式训练
- **GPU资源不足**：降级到CPU训练，时间预算增加5-10x
- **超时风险**：设置中间checkpoint，支持断点续训

## 质量检查

- 训练时间预测误差 ≤ 30%（基于历史项目校准）
- GPU利用率监控，低于50%需排查数据加载瓶颈
- 训练曲线收敛性检查，避免无效训练

## 回退策略

- 数据规模超出预算：采用子采样或主动学习策略
- 训练时间超预期：降级到更简单模型或减少epochs
- 硬件故障：从最近checkpoint恢复训练

## 资源召回建议

- 规划CFD代理模型训练工作流时召回本卡片
- 配套资源：cfd-multifidelity-aerodynamic-dataset（数据源）、cfd-workflow-fault-recovery（异常恢复）

## 证据来源

[1] Learning Curves for Decision Making in Supervised Machine Learning: A Survey, Mohr & van Rijn, Machine Learning, 2022, DOI: 10.48550/arXiv.2201.12150
[2] Multifidelity Surrogate Models: A New Data Fusion Perspective, Wilke, SACAM2024, 2024, DOI: 10.48550/arXiv.2404.14456
[3] BlendedNet: A Blended Wing Body Aircraft Dataset and Surrogate Model for Aerodynamic Predictions, Sung et al., ASME IDETC/CIE 2025, 2025, DOI: 10.48550/arXiv.2509.07209
