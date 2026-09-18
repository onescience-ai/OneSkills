# DeepONet算子学习实现架构与数据契约

## 适用范围

面向参数化偏微分方程（PDE）求解、实时优化控制、代理建模等场景，需要从头实现或调用DeepONet进行算子学习的任务。适用于涉及函数输入-解函数输出映射的科学计算问题，不适用于特定领域模型训练或数据预处理任务。

## 输入

- **参数场/函数输入**：离散化的参数场数据，通常为网格点上的函数值向量 $\mathbf{m} \in \mathbb{R}^{p_m}$
- **空间坐标**：用于Trunk网络的查询点坐标 $\mathbf{y} \in D_u$
- **边界条件**：可选的边界函数值
- **源项**：可选的源函数值

## 输出

- **解函数输出**：对应的PDE解离散化表示 $\mathbf{u} \in \mathbb{R}^{p_u}$
- **前向传播接口**：符合PyTorch标准的 `forward()` 方法

## 流程节点

### 1. DeepONet标准架构构建

**Branch网络**：
- 输入：参数场/函数的离散化表示
- 结构：全连接神经网络
- 输出：编码输入函数空间的潜在表示

**Trunk网络**：
- 输入：空间坐标或时间变量
- 结构：全连接神经网络
- 输出：表示解空间基函数的坐标相关分量

**输出融合**：
- 使用Hadamard积（逐元素乘积）融合Branch和Trunk输出
- 对于多输出情况，省略求和步骤

### 2. 数据格式契约

**训练数据组织**：
```
输入数据 X ∈ ℝ^{N × p_m}  # N个样本，每个样本p_m维参数向量
输出数据 Y ∈ ℝ^{N × p_u}  # N个样本，每个样本p_u维解向量
Trunk输入 X_tr ∈ ℝ^{N × N_tr × q_m}  # N个样本，每个样本N_tr个查询点
```

**数据对格式**：
- 每对数据包含：(参数场样本, 对应的解场样本)
- 参数场和解场需在相同网格或可转换的表示上

### 3. PyTorch实现模板

```python
import torch
import torch.nn as nn

class DeepONet(nn.Module):
    def __init__(self, branch_in_dim, branch_hidden_dims, trunk_in_dim, trunk_hidden_dims, output_dim):
        super(DeepONet, self).__init__()
        
        # Branch网络
        branch_layers = []
        in_dim = branch_in_dim
        for hidden_dim in branch_hidden_dims:
            branch_layers.extend([nn.Linear(in_dim, hidden_dim), nn.ReLU()])
            in_dim = hidden_dim
        branch_layers.append(nn.Linear(in_dim, output_dim))
        self.branch = nn.Sequential(*branch_layers)
        
        # Trunk网络
        trunk_layers = []
        in_dim = trunk_in_dim
        for hidden_dim in trunk_hidden_dims:
            trunk_layers.extend([nn.Linear(in_dim, hidden_dim), nn.ReLU()])
            in_dim = hidden_dim
        trunk_layers.append(nn.Linear(in_dim, output_dim))
        self.trunk = nn.Sequential(*trunk_layers)
    
    def forward(self, x_branch, x_trunk):
        # Branch网络处理输入函数
        branch_out = self.branch(x_branch)
        
        # Trunk网络处理空间坐标
        trunk_out = self.trunk(x_trunk)
        
        # Hadamard积融合
        output = branch_out * trunk_out
        
        return output
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Branch网络层数 | 3-8层 | [1] | 根据输入复杂度调整 |
| Trunk网络层数 | 3-8层 | [1] | 根据空间维度调整 |
| 隐藏层维度 | 64-256 | [1] | 典型值128或256 |
| 激活函数 | ReLU | [1] | 标准选择 |
| 输出维度 | 1或p_u | [1] | 单输出或多输出 |

## 边界与分流

- **不适用场景**：非线性PDE、高维参数空间（>1000维）可能需要修改架构
- **降级策略**：当Branch网络过拟合时，可减少网络深度或添加正则化
- **分支条件**：对于多物理场问题，可使用多分支DeepONet

## 质量检查

- **导入验证**：模型代码应可通过 `import` 导入
- **实例化测试**：实例化对象应具备符合契约的 `forward` 方法
- **前向传播测试**：使用随机输入数据进行前向传播测试
- **梯度检查**：验证反向传播可正常工作

## 回退策略

- **简化架构**：当完整DeepONet训练困难时，可使用浅层网络或随机投影方法
- **预训练特征**：使用预训练的特征提取器替代Branch网络
- **混合方法**：结合PINN和DeepONet的混合架构

## 资源召回建议

- 当任务涉及函数到函数的映射学习时召回本卡片
- 配套资源：算子学习数据生成、PDE求解器、训练流水线
- 相关卡片：神经Green函数算子学习（实例级）

## 证据来源

[1] Jha, P.K., "From Theory to Application: A Practical Introduction to Neural Operators in Scientific Computing", arXiv:2503.05598, 2025
[2] de Jong, T.O. et al., "Deep Operator Neural Network Model Predictive Control", arXiv:2505.18008, 2025
[3] Jani, A. et al., "PDEFlow: Autonomous Agentic PDE Pipelines for Neural Operator Learning and Solver-Free Inference", arXiv:2607.05134, 2026