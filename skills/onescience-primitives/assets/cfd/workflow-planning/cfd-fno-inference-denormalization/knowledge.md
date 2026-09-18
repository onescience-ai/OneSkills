# FNO推理阶段物理量反归一化与恢复

## 适用范围

适用于FNO算子学习模型推理阶段的后处理，将无量纲化的预测值恢复为具有物理意义的原始单位值。包括反归一化公式、网格坐标恢复和物理派生量计算。适用于Darcy流和Navier-Stokes等规则网格PDE算子学习任务。

## 输入

- **模型预测值**：无量纲化的预测场 $u_{pred,normalized} \in \mathbb{R}^{H \times W}$
- **归一化统计量**：训练集的均值 $\mu$ 和标准差 $\sigma$（保存在 normalization.json 中）
- **网格信息**：原始网格分辨率、物理域范围、坐标系定义
- **物理常数**：问题相关的物理常数（如粘性系数、特征长度等）

## 输出

- **恢复后的物理量**：具有物理单位的预测场 $u_{pred,physical} \in \mathbb{R}^{H \times W}$
- **网格坐标**：恢复后的物理坐标网格
- **物理派生量**：从基本场计算的派生物理量（如涡量、压力梯度等）
- **推理清单**：inference_manifest.json（记录每个样本的恢复结果）

## 流程节点

### 1. 反归一化公式

**标准反归一化**（线性缩放）：
$$x_{original} = x_{normalized} \times \sigma + \mu$$

其中：
- $x_{normalized}$：模型输出的无量纲预测值
- $\sigma$：训练集标准差（从 normalization.json 读取）
- $\mu$：训练集均值（从 normalization.json 读取）
- $x_{original}$：恢复后的物理量值

**多通道反归一化**：
对每个输出通道独立应用反归一化：
$$x_{original}^{(c)} = x_{normalized}^{(c)} \times \sigma^{(c)} + \mu^{(c)}$$

### 2. 网格坐标恢复

**坐标映射公式**：
$$x_{physical} = x_{normalized} \times L + x_{min}$$

其中：
- $x_{normalized} \in [0, 1]$：归一化坐标
- $L$：物理域长度（如 $L = 2\pi$ 对于 NS 问题，$L = 1$ 对于 Darcy 问题）
- $x_{min}$：物理域起始坐标

**网格构造**：
```python
import numpy as np
x = np.linspace(x_min, x_max, W)
y = np.linspace(y_min, y_max, H)
X, Y = np.meshgrid(x, y, indexing='ij')
```

### 3. 物理派生量计算

**Darcy流**：
- 压力梯度：$\nabla p = (\frac{\partial p}{\partial x}, \frac{\partial p}{\partial y})$
- 通量：$q = -a(x) \nabla p$

**Navier-Stokes**：
- 涡量（从速度场）：$\omega = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$
- 应变率：$\varepsilon_{ij} = \frac{1}{2}(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i})$
- 压力梯度：$\nabla p$

**数值微分方法**（规则网格）：
- 中心差分：$\frac{\partial f}{\partial x} \approx \frac{f_{i+1,j} - f_{i-1,j}}{2\Delta x}$
- 谱方法（推荐）：使用FFT计算导数，精度更高

### 4. 推理结果验证

- **操作**：检查反归一化后的值是否在物理合理范围内
- **参数**：物理量的合理范围
- **质量门禁**：无NaN或Inf；值在物理合理范围内；形状和单位正确

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 反归一化公式 | 线性缩放 | [1] | 标准做法 |
| 数值微分方法 | 谱方法/中心差分 | [1] | 谱方法精度更高 |
| 结果验证 | 必须执行 | [1] | 确保物理合理性 |

### 校准数值（体系专属）

| 参数 | Darcy流 | Navier-Stokes | 来源 | 说明 |
|------|---------|---------------|------|------|
| 物理域长度L | 1 | 2π | [1][2] | 标准无量纲化域 |
| 坐标范围 | [0,1]² | [0,2π]² | [1][2] | 标准配置 |
| 典型输出量 | 压力场 | 涡度/速度场 | [1] | 问题相关 |

## 边界与分流

**关键前提不成立时的改道方案**：
1. **归一化统计量缺失**：需重新计算或使用默认值
2. **非线性归一化**：需使用对应的反函数
3. **多物理场耦合**：需对每个物理量独立反归一化
4. **坐标系非笛卡尔**：需使用相应的坐标变换

## 质量检查

- 反归一化后值在物理合理范围内
- 无NaN或Inf值
- 网格坐标与原始数据一致
- 物理派生量计算正确
- 每个测试样本有唯一结果

## 回退策略

- 归一化统计量不匹配：使用训练集统计量重新计算
- 数值微分不稳定：降低微分阶数或使用滤波
- 结果异常：检查归一化流程和模型输出

## 资源召回建议

- 本卡片适用于FNO算子学习任务的批量推理与物理恢复步骤
- 配套卡片：`cfd-fno-evaluation-metrics-formulas`（评估指标）
- 配套卡片：`cfd-fno-regular-grid-pde-operator-learning-workflow`（完整工作流）

## 证据来源

[1] Duruisseaux, V., Kossaifi, J., & Anandkumar, A. (2025). Fourier Neural Operators Explained: A Practical Perspective. arXiv:2512.01421.

[2] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.
