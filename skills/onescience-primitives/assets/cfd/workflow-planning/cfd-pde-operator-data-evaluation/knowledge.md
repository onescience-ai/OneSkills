# PDE算子学习数据处理与评估

## 适用范围

适用于规则网格PDE算子学习任务的数据准备、切分、后处理和评估阶段。覆盖Darcy流（稳态椭圆PDE）和Navier-Stokes方程（非定常不可压流体）两种典型场景。为数据契约定义、无泄漏切分、反归一化、物理派生量计算和多维度评估提供标准化规范。

## 输入

- 原始PDE求解器输出数据（规则网格上的场量）
- 网格分辨率信息（如241×241、64×64等）
- 物理参数范围（如粘性系数、渗透率范围）
- 训练/验证/测试集划分比例（典型值：70%/15%/15%或80%/10%/10%）

## 输出

- 标准化数据契约文档（data_contract.json）
- 无泄漏切分产物（train_manifest.json、validation_manifest.json、test_manifest.json）
- 归一化统计量（normalization.json）
- 反归一化后的预测结果
- 评估指标报告（evaluation.json）

## 流程节点

### 1. 数据契约定义

#### Darcy流数据契约

| 字段 | 类型 | 单位 | 坐标系 | 说明 |
|------|------|------|--------|------|
| input.permeability | float32[H,W] | 无量纲（归一化后） | 笛卡尔坐标，原点在左下角 | 渗透率场 $a(x)$ |
| output.pressure | float32[H,W] | 无量纲（归一化后） | 同上 | 压力场 $u(x)$ |
| grid.resolution | int[2] | - | - | 网格分辨率 [H, W] |
| grid.domain | float32[2,2] | 物理单位 | - | 物理域范围 [[x_min,y_min],[x_max,y_max]] |

标准数据集参考：
- **Darcy_241**：241×241网格，1000训练/200测试样本，输入为渗透率场，输出为压力场 [1]
- 网格间距：$\Delta x = 1/240$（单位正方形域）

#### Navier-Stokes数据契约

| 字段 | 类型 | 单位 | 坐标系 | 说明 |
|------|------|------|--------|------|
| input.vorticity | float32[H,W,T_in] | 无量纲（归一化后） | 笛卡尔坐标，周期边界 | 初始涡度场序列 |
| output.vorticity | float32[H,W,T_out] | 无量纲（归一化后） | 同上 | 目标涡度场序列 |
| velocity.u | float32[H,W,2,T] | 无量纲 | 同上 | 速度场（由涡度推导） |
| viscosity.nu | float32 | 无量纲 | - | 粘性系数 |
| grid.resolution | int[2] | - | - | 网格分辨率 [H, W] |

标准配置：
- 粘性系数 $\nu = 10^{-3}, 10^{-4}, 10^{-5}$
- 训练分辨率：64×64×20（时空）
- 最终时间 $T$ 随 $\nu$ 减小而减小（$\nu=10^{-3}$时$T=50$，$\nu=10^{-5}$时$T=20$）

### 2. 无泄漏切分策略

#### Darcy流（静态问题）

- **切分维度**：按样本ID切分
- **约束条件**：不同几何域的样本不跨集
- **实现方法**：
  ```python
  # 假设样本ID为0到N-1
  indices = np.random.permutation(N)
  train_idx = indices[:int(0.7*N)]
  val_idx = indices[int(0.7*N):int(0.85*N)]
  test_idx = indices[int(0.85*N):]
  ```

#### Navier-Stokes（时序问题）

- **切分维度**：按时间轨迹（模拟实例）切分
- **约束条件**：同一模拟的不同时间步不跨集
- **实现方法**：
  ```python
  # 假设有M个模拟实例，每个实例有T个时间步
  sim_indices = np.random.permutation(M)
  train_sims = sim_indices[:int(0.7*M)]
  # 训练集包含这些模拟的所有时间步
  ```

#### 无量纲化统计量计算

- **计算范围**：仅从训练集计算均值和标准差
- **公式**：$\text{mean} = \frac{1}{N_{train}} \sum_{i=1}^{N_{train}} x_i$，$\text{std} = \sqrt{\frac{1}{N_{train}} \sum_{i=1}^{N_{train}} (x_i - \text{mean})^2}$
- **保存位置**：normalization.json，包含每个字段的mean和std

### 3. 反归一化流程

#### 标准反归一化公式

$$x_{\text{original}} = x_{\text{normalized}} \times \text{std} + \text{mean}$$

#### 实现代码模板

```python
import json
import numpy as np

def denormalize(pred_normalized, field_name, norm_path='normalization.json'):
    with open(norm_path) as f:
        norms = json.load(f)
    mean = norms[field_name]['mean']
    std = norms[field_name]['std']
    return pred_normalized * std + mean
```

#### 物理派生量计算

**涡量（从速度场）**：
$$\omega = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$$

**压力梯度（从压力场）**：
$$\nabla p = \left(\frac{\partial p}{\partial x}, \frac{\partial p}{\partial y}\right)$$

**速度散度（不可压验证）**：
$$\nabla \cdot u = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} \approx 0$$

**注意**：所有物理派生量必须在恢复原始单位后计算。

### 4. 评估指标体系

#### 统计误差指标

| 指标 | 公式 | 验收门限 | 说明 |
|------|------|----------|------|
| 相对L2误差 | $\frac{\|u_{\text{pred}} - u_{\text{true}}\|_2}{\|u_{\text{true}}\|_2}$ | < 0.1 (10%) | 主要精度指标 |
| RMSE | $\sqrt{\text{mean}((u_{\text{pred}} - u_{\text{true}})^2)}$ | 依赖量级 | 绝对误差度量 |
| 最大绝对误差 | $\max|u_{\text{pred}} - u_{\text{true}}|$ | 依赖应用 | 局部极端误差 |

#### 物理约束指标

| 指标 | 计算方法 | 验收门限 | 说明 |
|------|----------|----------|------|
| 连续性方程残差 | 离散散度算子作用于预测速度场 | < 1e-4 | 不可压流体质量守恒 |
| 动量方程残差 | 离散NS方程残差 | < 1e-3 | 动量守恒验证 |
| 边界误差 | 边界区域预测值与真实值差异 | < 0.05 | 边界条件满足程度 |

#### 泛化能力指标

| 指标 | 计算方法 | 说明 |
|------|----------|------|
| 分辨率不变性 | 不同分辨率下的误差稳定性 | FNO核心优势 |
| 零样本超分辨率 | 低分辨率训练→高分辨率测试 | 误差应保持稳定 |
| 参数外推能力 | 训练参数范围外的预测精度 | 需明确报告外推范围 |

#### worst_cases可追溯实现

```python
def find_worst_cases(predictions, ground_truth, sample_ids, top_k=10):
    errors = []
    for pred, gt, sid in zip(predictions, ground_truth, sample_ids):
        rel_l2 = np.linalg.norm(pred - gt) / np.linalg.norm(gt)
        errors.append({'sample_id': sid, 'rel_l2': rel_l2})
    errors.sort(key=lambda x: x['rel_l2'], reverse=True)
    return errors[:top_k]
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Darcy_241网格分辨率 | 241×241 | [1] | 标准Darcy流数据集 |
| NS训练分辨率 | 64×64×20 | [1] | 时空分辨率 |
| NS粘性系数 | 1e-3, 1e-4, 1e-5 | [1] | 不同湍流强度 |
| 相对L2门限 | < 0.1 | [1] | 主要精度标准 |
| 训练样本数 | 1000（标准）/10000（高精度） | [1] | 数据量配置 |
| 切分比例 | 70%/15%/15% 或 80%/10%/10% | 通用惯例 | 训练/验证/测试 |

## 边界与分流

- **非周期边界**：若PDE为非周期边界，需在数据契约中明确边界类型，并在评估时单独计算边界误差
- **多物理量输出**：若输出包含多个物理量（如速度+压力），需为每个字段分别定义归一化统计量
- **时序数据**：Navier-Stokes时序数据需按轨迹切分，不能按时间步随机切分
- **数据量不足**：若训练样本<500，需报告数据量限制对泛化能力的影响

## 质量检查

- 数据契约完整性：检查所有必需字段是否定义
- 切分无泄漏验证：确认训练集、验证集、测试集样本ID无交集
- 归一化统计量范围：确认统计量仅从训练集计算
- 反归一化一致性：确认预测值反归一化后与原始数据单位一致
- 评估指标完备性：确认包含统计误差、物理约束和泛化能力三类指标

## 回退策略

- 若数据契约定义不完整，参考标准数据集（Darcy_241、NS数据集）的格式
- 若切分出现泄漏，重新执行切分并验证样本ID无交集
- 若评估指标计算失败，检查归一化统计量文件是否存在且格式正确

## 资源召回建议

- 本卡片适用于PDE算子学习的数据准备、后处理和评估阶段
- 配套资源：`cfd-fno-model-architecture-training`（模型架构与训练）
- 配套工具：`neuralop` 数据加载器和评估工具

## 证据来源

[1] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.

[2] Mishra, N. and Molinaro, R. (2023). Learning to Solve PDEs with Little Data: A Comparative Study. arXiv:2301.09410.
