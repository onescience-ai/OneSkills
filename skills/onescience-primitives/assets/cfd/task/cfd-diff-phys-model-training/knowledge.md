# 模型配置与训练

## 适用范围

本任务为可微分物理求解工作流的核心训练阶段，支持Differentiable simulator（可微分模拟器）和Mechanistic PDE network（机理PDE网络）两类模型的配置与训练。适用于需要从可微轨迹数据中学习物理规律并同时发现控制方程的场景。当训练发散或收敛失败时，应停止并报告原因，提供诊断信息供后续调整。

## 输入

### 必需输入
| 变量 | 类型 | 说明 |
|------|------|------|
| `{MODEL_NAME}` | str | 模型类型：Differentiable simulator或Mechanistic PDE network |
| `{TRAIN_CONFIG}` | object | 训练超参数配置 |

### 可选输入
| 变量 | 类型 | 说明 |
|------|------|------|
| `{INIT_CHECKPOINT}` | doc | 预训练权重路径（可选） |

### 训练配置模板
```json
{
  "framework": "PyTorch",
  "epochs": 100,
  "batch_size": 8,
  "learning_rate": 0.001,
  "seed": 42,
  "early_stopping_patience": 15
}
```

## 输出

### 产物清单
| 文件 | 格式 | 说明 |
|------|------|------|
| `best_checkpoint.pt` | PyTorch | 最佳模型权重 |
| `train_config.json` | JSON | 实际使用的训练配置 |
| `training_metrics.csv` | CSV | 逐轮训练验证指标 |
| `environment.txt` | Text | 代码版本、依赖、随机种子 |

### 质量门禁
- [ ] 训练验证损失均为有限值
- [ ] 最佳权重可重新加载
- [ ] 配置环境随机种子可复现

## 流程节点

```
1. 加载s02切分数据与normalization.json
   ↓
2. 初始化模型（Differentiable simulator或Mechanistic PDE network）
   ↓
3. 若提供INIT_CHECKPOINT，检查结构兼容性并加载
   ↓
4. 配置优化器（Adam默认，lr=0.001）
   ↓
5. 训练循环：前向→计算损失→反向→更新
   ↓
6. 验证评估：记录验证损失
   ↓
7. 早停判断：耐心耗尽或无改善则停止
   ↓
8. 保存best_checkpoint.pt与训练日志
```

## 关键参数

### 模型类型对比
| 模型 | 特点 | 适用场景 |
|------|------|----------|
| Differentiable simulator | 基于可微分物理模拟器，端到端可微 | 已有物理模拟器框架 |
| Mechananistic PDE network | 嵌入PDE结构的神经网络，自动发现方程 | 需要方程发现 |

### 超参数调优建议
| 参数 | 默认值 | 调优方向 |
|------|--------|----------|
| learning_rate | 0.001 | 过大→发散，过小→收敛慢 |
| batch_size | 8 | 过大→内存不足，过小→梯度噪声 |
| early_stopping_patience | 15 | 过大→过拟合，过小→欠拟合 |
| epochs | 100 | 根据收敛速度调整 |

## 边界与分流

### 正常流
数据加载 → 模型初始化 → 训练循环 → 保存最佳权重

### 异常分支
| 条件 | 处理 |
|------|------|
| 训练损失为NaN/Inf | 停止训练，报告发散 |
| 验证损失持续上升 | 早停，保存当前最佳 |
| 权重加载失败 | 检查结构兼容性，重新初始化 |
| GPU内存不足 | 降低batch_size或使用混合精度 |

### 降级策略
- 若Differentiable simulator训练失败，可尝试Mechanistic PDE network
- 若全批量训练失败，可尝试小批量+梯度累积

## 质量检查

### 训练过程
- [ ] 损失曲线平滑下降
- [ ] 验证损失与训练损失差距合理
- [ ] 无梯度爆炸/消失

### 权重验证
- [ ] checkpoint可完整加载
- [ ] 模型结构与配置一致
- [ ] 随机种子已记录

## 回退策略

| 失败原因 | 回退方案 |
|----------|----------|
| 训练发散 | 降低学习率，添加正则化 |
| 过拟合 | 增加数据、减小模型、早停 |
| 欠拟合 | 增加模型容量、延长训练 |
| 内存不足 | 减小batch_size，使用梯度检查点 |

## 资源召回建议

### 触发条件
- 需要训练可微分物理模型
- 需要PDE方程发现
- 需要可复现的训练流程

### 配套任务
- `cfd-diff-phys-data-preprocessing`：前置数据准备
- `cfd-diff-phys-coupled-solving`：后续耦合求解

## 证据来源

[1] Mechanistic PDE Networks for Discovery of Governing Equations
[2] Hamiltonian Neural PDE Solvers through Functional Approximation, arXiv:2505.13275
[7] ΦFlow_ Differentiable Simulations for PyTorch, TensorFlow and Jax
