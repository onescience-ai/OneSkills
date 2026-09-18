# CFD ROM 架构选择与超参数配置

## 适用范围

面向参数化CFD降阶建模任务，根据问题特性（数据维度、几何复杂度、实时性要求、物理约束需求）选择合适的ROM架构，并确定关键超参数的配置方法。适用于从稀疏传感器数据重建全场流场、参数化预测和实时控制等场景。不适用于稳态单工况后处理或纯数值格式优化问题。

## 输入

### 架构选择判据
| 判据维度 | POD-LSTM | Autoencoder-LSTM | SHRED |
|----------|----------|------------------|-------|
| 数据维度 | 中低维（<10万自由度） | 中高维 | 高维（任意） |
| 几何复杂度 | 固定几何 | 固定/轻度变化 | 任意几何 |
| 传感器类型 | 固定位置 | 固定位置 | 移动/任意位置 |
| 实时性要求 | 中等 | 中等 | 高（毫秒级） |
| 物理约束 | 弱（需后处理） | 弱 | 强（可嵌入） |

### 超参数声明
- hidden_dim：LSTM隐藏层维度
- latent_dim：潜空间维度（编码器输出维度）
- physics_loss_weights：物理约束损失权重
- time_steps：时间序列输入长度
- n_sensors：稀疏传感器数量

## 输出

### 架构配置文件
```yaml
rom_config:
  architecture: shred | ae-lstm | pod-lstm
  encoder:
    type: linear | conv | shallow
    latent_dim: <int>
    hidden_dim: <int>
  decoder:
    type: linear | conv | shallow
    output_fields: [velocity, pressure, temperature]
  temporal:
    type: lstm | gru | transformer
    hidden_dim: <int>
    time_steps: <int>
  physics_loss:
    enabled: bool
    weights:
      continuity: <float>
      momentum: <float>
      energy: <float>
```

### 训练就绪状态
```yaml
training_readiness:
  architecture_selected: bool
  hyperparameters_configured: bool
  physics_loss_defined: bool
  data_compatibility_verified: bool
```

## 流程节点

### 节点1：问题特性分析
- 操作：分析输入数据维度、几何类型、传感器配置
- 参数：dataset_shape, geometry_type, sensor_config
- 工具：问题特性解析器
- 质量门禁：输出标准化问题描述

### 节点2：架构候选筛选
- 操作：根据判据矩阵筛选可行架构
- 参数：problem_profile, architecture_matrix
- 工具：架构匹配器
- 质量门禁：至少保留2个候选架构

### 节点3：超参数空间定义
- 操作：为每个候选架构定义超参数搜索范围
- 参数：architecture_candidates, parameter_ranges
- 工具：超参空间生成器
- 质量门禁：搜索空间维度合理（<10维）

### 节点4：物理约束配置
- 操作：根据流体类型定义物理损失函数
- 参数：physics_type (incompressible|compressible|multiphase), loss_weights
- 工具：物理约束配置器
- 质量门禁：损失权重之和归一化

### 节点5：配置输出与确认
- 操作：生成rom_config.yaml并请求用户确认
- 参数：selected_architecture, configured_hyperparameters
- 工具：配置输出器
- 质量门禁：配置文件格式正确，所有必填字段完整

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| latent_dim heuristic | sqrt(n_samples) | [1] | 潜空间维度经验公式 |
| hidden_dim/latent_dim ratio | [2, 4] | [2] | LSTM隐藏层与潜空间比例 |
| min_time_steps | 20 | [1] | 时间序列最小步长 |
| physics_loss_weight_range | [0.01, 0.1] | [5] | 物理约束损失权重范围 |
| reconstruction_error_target | <5% | [3] | 重建误差目标（相对L2） |

### 校准数值（SHRED架构）
以下数值来自SHRED在MHD液态金属流和湍流问题中的验证实验，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| latent_dim (MHD) | 16 | [1] | DEMO聚变堆包层流动重建 |
| hidden_dim (MHD) | 64 | [1] | LSTM隐藏层配置 |
| n_sensors (MHD) | 10-50 | [1] | 稀疏温度传感器数量 |
| reconstruction_error | ~5% | [1] | 温度、压力、速度平均相对误差 |
| time_steps (plasma) | 50 | [4] | 等离子体放电时间序列 |

### 校准数值（Autoencoder-LSTM）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| latent_dim (turbulent) | 16-32 | [2] | 湍流槽道流 |
| hidden_dim (turbulent) | 64-128 | [2] | LSTM配置 |
| n_shapes (generalization) | 80 | [3] | 训练几何体数量 |
| test_shapes | 20 | [3] | 测试几何体数量 |

## 边界与分流

### 前提否定即改道
| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| 数据维度已知 | 先执行数据探针获取维度信息 |
| 几何类型已声明 | 降级为通用架构（POD-LSTM） |
| 传感器配置已定义 | 使用默认均匀分布传感器 |
| 物理方程已知 | 禁用物理约束损失，纯数据驱动 |

### 架构选择决策树
1. 需要移动传感器 → SHRED
2. 需要强物理约束 → SHRED + physics_loss
3. 几何固定 + 中低维 → POD-LSTM
4. 几何固定 + 高维 → Autoencoder-LSTM
5. 实时性要求极高（<10ms） → SHRED（浅层解码器）

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 架构与数据维度匹配 | 100% | 重新选择架构 |
| 超参数在合理范围 | 100% | 调整超参数 |
| 物理损失权重归一化 | 100% | 重新归一化 |
| 配置文件格式正确 | 100% | 修复格式 |

## 回退策略

1. **架构选择不确定**：生成多个候选配置，由用户或小规模实验决定
2. **超参数搜索失败**：使用默认值（hidden_dim=64, latent_dim=16）
3. **物理约束不适用**：禁用physics_loss，仅使用重建损失
4. **计算资源不足**：降级为POD-LSTM（计算量最小）

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- CFD ROM架构设计与选型
- SHRED/SHRED-ROM超参数配置
- Autoencoder-LSTM ROM训练配置
- 物理约束损失函数设计
- 多工况ROM泛化能力评估

配套资源：
- `cfd-rom-dataset-protocol-validation`：数据集接入验证
- `cfd-transferable-rom-workflow-end-to-end`：端到端工作流

## 证据来源

[1] Tomasetto M, Williams JP, Braghin F, Manzoni A, Kutz JN. Reduced Order Modeling with Shallow Recurrent Decoder Networks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65126-y

[2] Nakamura T, Fukami K, Hasegawa K, et al. CNN-LSTM based ROM for turbulent channel flow. Physics of Fluids, 2021. DOI: 10.1063/5.0039845

[3] Hasegawa K, Fukami K, et al. ML-ROM for unsteady flows around bluff bodies of various shapes. Theoretical Computational Fluid Dynamics, 2020. DOI: 10.1007/s00162-020-00528-w

[4] Kutz JN, Reza M, Faraji F, Knoll A. SHRED for Plasma Dynamics. arXiv:2405.11955, 2024.

[5] Swischuk R, Kramer B, et al. Learning physics-based ROM for combustion. AIAA Journal, 2020. DOI: 10.2514/1.J058943
