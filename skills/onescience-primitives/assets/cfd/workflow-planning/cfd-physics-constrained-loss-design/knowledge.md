# CFD神经PDE求解器物理约束损失函数设计

## 适用范围
本卡适用于设计和实现神经PDE求解器（如PINN、神经算子等）中的物理约束损失函数，确保模型在训练过程中遵守质量守恒、能量守恒和PDE残差等物理约束。适用于不可压缩/可压缩流动、多相流、湍流等CFD场景。

## 输入
- 控制方程：Navier-Stokes方程、Euler方程、扩散方程等PDE形式
- 边界条件：Dirichlet、Neumann、Robin或周期性边界条件
- 初始条件：初始场分布
- 训练数据：稀疏或密集的观测数据（可选）

## 输出
- 损失函数设计规范：包含各损失项的权重设置策略
- 物理约束实现代码：梯度加权、自适应权重、硬约束嵌入等
- 训练监控指标：PDE残差、守恒误差、边界误差等

## 流程节点

### 1. 损失函数组件识别
识别并定义损失函数中的各个组件：
- **数据损失**：预测值与观测数据的偏差
- **PDE残差损失**：控制方程在训练点上的残差
- **边界条件损失**：边界条件满足程度
- **初始条件损失**：初始条件满足程度
- **物理守恒损失**：质量、动量、能量守恒约束

### 2. 权重平衡策略
**固定权重**：手动设置各损失项权重，适用于简单问题
**自适应权重**：动态调整权重以平衡各损失项贡献
- ReLoBRaLo（Relative Loss Balancing with Random loopback）[论文1]
- AW-PINN（Adaptive Weighted PINN）[论文1]
- 梯度归一化（GradNorm）[论文1]

### 3. 梯度加权方法
针对高梯度区域（如激波、间断面）的特殊处理：
- 基于速度梯度的压缩梯度权重：$\lambda = \frac{1}{\epsilon_1 + |\nabla \cdot \vec{u}|}$ [论文1]
- 权重系数$\epsilon_1$的经验值：Burgers方程取0.01，Euler方程取0.2 [论文1]
- 作用：减少不连续区域对训练的负面影响，优先学习光滑区域

### 4. 硬约束嵌入
将边界条件精确嵌入网络架构，而非通过损失函数惩罚：
- **Dirichlet边界**：$u(x) = g(x) + \ell(x) \cdot N(x;\theta)$，其中$\ell(x)$在边界处为0 [论文1]
- **压力硬约束**：在收敛-扩张喷管问题中，仅对压力变量施加硬约束，保持其他变量自由度 [论文1]
- **优势**：确保边界条件精确满足，避免软约束的权重依赖问题

### 5. 物理守恒约束
添加全局守恒约束作为软约束：
- 质量守恒：$\int_{\Omega} \rho dV = constant$ [论文1]
- 动量守恒：$\int_{\Omega} \rho \vec{u} dV = constant$ [论文1]
- 能量守恒：$\int_{\Omega} E dV = constant$ [论文1]
- 在入口和出口边界上评估守恒项 [论文1]

## 关键参数

### 通用判据（方法层）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| PDE损失权重 $w_{PDE}$ | 1-10 | [论文1] | 根据问题复杂度调整 |
| 边界条件权重 $w_{BC}$ | 1-10 | [论文1] | 与PDE权重平衡 |
| 初始条件权重 $w_{IC}$ | 1-10 | [论文1] | 在间断问题中可增大 |
| 守恒约束权重 $w_{CONS}$ | 0.1-1 | [论文1] | 通常较小，避免干扰主损失 |
| 梯度加权参数 $\epsilon_1$ | 0.01-0.2 | [论文1] | Burgers方程0.01，Euler方程0.2 |
| 自适应权重学习率 | 1e-3-1e-2 | [论文1] | 根据优化器调整 |

### 校准数值（具体案例参考）
| 参数 | 数值 | 来源 | 说明 |
|------|------|------|------|
| Burgers方程梯度加权 $\epsilon_1$ | 0.01 | [论文1] | 经验值 |
| Euler方程梯度加权 $\epsilon_1$ | 0.2 | [论文1] | 经验值 |
| 6层网络（50神经元） | 最优架构 | [论文1] | 收敛-扩张喷管问题 |
| Adam迭代次数 | 20,000 | [论文1] | 初始训练阶段 |
| L-BFGS迭代次数 | 3,000 | [论文1] | 精细化阶段 |

## 边界与分流

### 高梯度区域处理
当问题包含激波、接触间断等高梯度区域时：
- 启用梯度加权方法，降低不连续区域权重
- 增加PDE损失权重以确保整体精度
- 考虑使用自适应配点移动策略 [论文1]

### 多尺度问题
当问题包含多个时间/空间尺度时：
- 采用课程学习策略，先学习低频分量
- 使用多尺度特征扩展（如Fourier特征）[论文3]
- 考虑域分解方法，分离不同尺度区域 [论文3]

### 复杂几何
当计算域几何复杂时：
- 使用硬约束嵌入边界条件
- 考虑符号距离函数（SDF）表示复杂边界 [论文1]
- 域分解辅助并行训练 [论文3]

## 质量检查
1. **PDE残差监控**：训练过程中监控PDE残差是否持续下降
2. **守恒误差检查**：验证质量、能量守恒误差是否在可接受范围内（<5%）
3. **边界条件满足度**：检查边界条件是否精确满足（硬约束）或接近满足（软约束）
4. **梯度稳定性**：确保梯度加权不会导致训练不稳定
5. **过拟合检测**：监控验证集损失，防止过拟合

## 回退策略
1. **权重自动调整失败**：回退到手动权重调优，使用网格搜索确定最优权重
2. **梯度加权不收敛**：减少梯度加权强度或禁用该策略
3. **硬约束导致欠拟合**：改用软约束或减少硬约束变量数量
4. **守恒约束冲突**：调整守恒约束权重或仅在关键区域应用

## 资源召回建议
- **何时召回**：当需要设计或优化神经PDE求解器的损失函数时
- **配套资源**：cfd-neural-operator-architecture（神经算子架构）、cfd-public-datasets（公开CFD数据集）

## 证据来源
[1] Physics-informed neural network with weighted loss and hard constraints for hyperbolic conservation laws, Nature Communications, 2025, DOI: 10.1038/s41598-025-34263-1
[2] A Second-Order Network Structure Based on Gradient-Enhanced Physics-Informed Neural Networks for Solving Parabolic Partial Differential Equations, Entropy, 2023, DOI: 10.3390/e25040674
[3] Physics-Informed Machine Learning in Biomedical Science and Engineering, Annual Review of Biomedical Engineering, 2026, DOI: 10.1146/annurev-bioeng-110824-124907
[4] Fast-forward prediction of lattice Boltzmann dynamics with physics-informed neural operators, Nature Communications, 2026, DOI: 10.1038/s41467-026-75730-1