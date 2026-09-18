# 神经Green函数算子学习

## 适用范围

面向线性偏微分方程（PDE）求解，特别是具有特征分解性质的算子（如Poisson方程、双调和方程、Stokes方程），需要在不同几何形状和边界/源函数间泛化的场景。适用于稳态热分析、弹性力学、流体力学等问题，不适用于高度非线性PDE或需要实时训练的任务。

## 输入

- **几何表示**：体积点云或网格表示的计算域 $\mathbf{D} = (\mathbf{V}, \mathbf{T})$
- **边界条件**：边界函数值 $\mathbf{h} \in \mathbb{R}^{N_b}$
- **源项**：源函数值 $\mathbf{f} \in \mathbb{R}^{N_v}$

## 输出

- **解场预测**：PDE解在查询点上的值 $\mathbf{u}_\theta$
- **Green函数近似**：学习到的Green函数矩阵 $\mathbf{G}_\theta$

## 流程节点

### 1. Neural Green's Function框架

**特征提取**：
- 从体积点云提取每点特征 $\boldsymbol{\Phi}_\theta \in \mathbb{R}^{|\mathbf{Q}| \times d}$
- 特征仅依赖于域几何，与源/边界函数无关

**Green函数构建**：
$$\mathbf{G}_\theta = (\mathbf{K}\boldsymbol{\Phi}_\theta)(\mathbf{K}\boldsymbol{\Phi}_\theta)^T$$

**辅助量预测**：
- 质量矩阵 $\mathbf{M}_\theta$
- 边界项子矩阵 $\tilde{\mathbf{L}}_\theta = (\mathbf{K}\boldsymbol{\Psi}_\theta)(\mathbf{S}\boldsymbol{\Psi}_\theta)^T$

**解计算**：
$$\mathbf{u}_\theta = \mathbf{K}^T\{\mathbf{G}_\theta(\mathbf{K}\mathbf{M}_\theta\mathbf{f} - \tilde{\mathbf{L}}_\theta\mathbf{h})\} + \mathbf{S}^T\mathbf{h}$$

### 2. GreensONet框架

**Trunk网络**：
- 输入：空间坐标 $(\mathbf{x}, \boldsymbol{\xi})$
- 输出：Green函数 $G(\mathbf{x}, \boldsymbol{\xi})$

**Branch网络**：
- 输入：空间坐标 $(\mathbf{x}, \boldsymbol{\xi})$
- 输出：Green函数梯度 $\nabla G(\mathbf{x}, \boldsymbol{\xi})$

**数值积分**：
- 使用高斯积分计算体积分和面积分
- 4点高斯积分用于四面体单元
- 3点高斯积分用于三角形边界面

### 3. 数据格式契约

**训练数据组织**：
```
输入：{(域几何_i, 源函数_i, 边界函数_i)}_{i=1}^N
输出：{解函数_i}_{i=1}^N
```

**数据生成**：
- 使用高斯随机场生成多样化的源/边界函数
- 使用FEM求解器生成对应的解

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 特征维度 d | 64-256 | [1] | 典型值128 |
| 高斯积分点数 | 4点(体), 3点(面) | [2] | 平衡精度与效率 |
| 训练轮数 | 40-200 | [1] | 取决于问题复杂度 |
| 质量正则化权重 λ | 1 | [1] | 确保质量预测稳定性 |

## 边界与分流

- **不适用场景**：高度非线性PDE、需要实时训练的任务
- **降级策略**：对于简单几何，可省略Branch网络，使用自动微分计算梯度
- **分支条件**：对于多物理场问题，可学习Green函数矩阵的每行

## 质量检查

- **泛化测试**：在训练时未见过的源/边界函数上测试
- **几何泛化**：在训练时未见过的几何形状上测试
- **误差评估**：使用相对L2误差 $e(\mathbf{u}, \mathbf{u}_\theta) = \frac{\|\mathbf{u}_\theta - \mathbf{u}\|_2}{\|\mathbf{u}\|_2}$
- **运行时间**：相比FEM求解器的加速比（可达350倍）

## 回退策略

- **简化几何**：对于复杂几何，可使用粗网格或简化表示
- **减少特征维度**：当训练不稳定时，可降低特征维度
- **混合方法**：结合传统数值方法和神经算子

## 资源召回建议

- 当任务涉及线性PDE求解且需要跨几何泛化时召回本卡片
- 配套资源：DeepONet架构卡片、FEM求解器、网格生成工具
- 相关卡片：DeepONet算子学习实现架构（通用类）

## 证据来源

[1] Yoo, S. et al., "Neural Green's Functions", NeurIPS 2025, arXiv:2511.01924, 2025
[2] Gu, J. et al., "An explainable operator approximation framework under the guideline of Green's function", Computer Methods in Applied Mechanics and Engineering, arXiv:2412.16644, 2024