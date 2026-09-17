# 方程求解与物理残差恢复

## 适用范围

**触发条件**：
- 已完成模型训练（s03），持有best_checkpoint
- 需要在查询点上恢复解场和计算物理残差

**适用场景**：
- Deep Ritz网络推理与残差评估
- 弱形式神经求解器推理与残差评估
- 需要验证物理一致性的场景

**不适用场景**：
- 模型尚未训练完成
- 需要快速近似解（可用简化方法）

## 输入

- **CHECKPOINT**（必需）：模型权重文件路径
- **DEVICE**（必需）：计算设备（CPU或CUDA）
- **BATCH_SIZE**（可选）：推理批大小，默认8
- 查询配点或网格坐标

## 输出

- **solution_fields/**：解场文件目录，含各变量的场数据
- **pde_residuals/**：PDE残差场文件目录
- **boundary_residuals.csv**：边界残差汇总

## 流程节点

### 1. 模型加载与初始化
- 加载checkpoint到指定设备
- 验证模型结构完整性
- 设置为eval模式

### 2. 解场计算
- 在查询点上进行前向传播
- 使用自动微分计算导数
- 保存解场各分量

### 3. PDE残差计算
- 基于解场和导数计算PDE残差
- 逐点计算残差值
- 保存残差场

### 4. 边界残差计算
- 在边界点上评估解
- 计算边界条件满足程度
- 汇总边界残差

### 5. 结果验证
- 检查解场导数是否有限
- 检查残差是否有限
- 标记异常区域

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 计算设备 | cuda | [1] | 默认使用GPU |
| 推理批大小 | 8 | [1] | 按显存调整 |
| 自动微分 | torch.autograd | [2] | 用于导数计算 |
| 残差计算 | 基于PDE定义 | [1] | 逐点计算 |

## 边界与分流

- **解场为NaN/Inf**：标记该区域为"解异常"，检查模型训练
- **残差过大**：标记为"残差异常"，可能需要重新训练
- **边界不满足**：检查边界条件实现
- **内存不足**：减小BATCH_SIZE分批计算

## 质量检查

- [ ] 解场导数与残差均为有限值
- [ ] 边初值逐项满足门限
- [ ] 独立数值解或解析解可对照（如有）

## 回退策略

- 解场异常 → 检查模型权重和输入数据
- 残差过大 → 检查PDE实现和变分形式
- 内存不足 → 减小批大小或使用混合精度

## 资源召回建议

本卡是Deep Ritz工作流的第四步。完成后进入任务验收与适用域判定步骤（cfd-deep-ritz-acceptance-applicability-assessment）。

## 证据来源

[1] "The Deep Ritz Method: A Deep Learning-Based Numerical Algorithm for Solving Variational Problems", E and Yu, 2017
[2] "Error Analysis of Deep Ritz Methods for Elliptic Equations", 2021
[3] "Learning from Integral Losses in Physics-Informed Neural Networks", 2024
