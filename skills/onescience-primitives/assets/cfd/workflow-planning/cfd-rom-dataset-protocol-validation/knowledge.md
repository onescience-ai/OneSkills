# CFD ROM 数据集接入协议验证

## 适用范围

面向参数化CFD降阶模型（ROM）训练任务，在任务启动前对输入数据集进行完整性验证与用户确认。适用于需要从稀疏传感器数据重建全场流场的ROM训练场景，包括但不限于湍流、非定常流动、多物理场耦合问题。不适用于稳态单工况CFD后处理或纯数值模拟任务。

## 输入

### 必填字段清单
| 字段 | 类型 | 说明 | 缺失后果 |
|------|------|------|----------|
| dataset_path | string | 数据集根目录路径 | 任务无法启动 |
| geometry_params | dict | 几何参数定义（边界形状、尺寸范围） | ROM无法泛化到未见几何 |
| sensor_positions | array | 稀疏监测点坐标 | SHRED架构无法接收输入 |
| parameter_space | dict | 参数化空间范围（Reynolds数、边界条件等） | 训练数据无法覆盖设计空间 |
| time_series_length | int | 时间序列采样长度 | LSTM/时序模型输入不匹配 |

### 数据格式要求
- 流场快照：NPZ/NPY格式，shape为 `(n_samples, nx, ny, nz, n_fields)`
- 参数向量：CSV/JSON格式，每行对应一个工况的参数组合
- 传感器数据：从流场快照中按 `sensor_positions` 索引提取的子集

### 预处理要求
1. 数据归一化：推荐Z-score标准化或Min-Max缩放
2. 降维预处理：POD基函数或PCA主成分数量需在数据接入时声明
3. 时间采样：采样间隔需满足CFL条件对应的物理时间分辨率

## 输出

### 数据集验证报告
```yaml
validation_report:
  status: pass | fail | warning
  checks:
    path_exists: bool
    format_valid: bool
    parameter_range_consistent: bool
    sensor_count_adequate: bool
    temporal_resolution_sufficient: bool
  user_confirmation_required: bool
  missing_fields: [list of missing required fields]
```

### 确认后的数据集引用
```yaml
dataset_binding:
  path: <validated_path>
  format: npz | npy | csv
  n_samples: <int>
  parameter_space: <dict>
  sensor_locations: <array>
```

## 流程节点

### 节点1：必填字段完整性检查
- 操作：验证所有必填字段是否在用户输入中提供
- 参数：required_fields清单
- 工具：字段存在性验证器
- 质量门禁：所有required字段必须存在，否则阻断

### 节点2：数据格式一致性校验
- 操作：读取数据集文件头，验证维度和类型
- 参数：expected_shape, expected_dtype
- 工具：文件格式解析器
- 质量门禁：实际shape与声明shape偏差<5%

### 节点3：参数空间覆盖度评估
- 操作：检查训练数据是否覆盖目标参数空间
- 参数：target_parameter_space, actual_parameter_range
- 工具：空间覆盖度计算器
- 质量门禁：覆盖率>80%或有用户显式豁免声明

### 节点4：用户确认请求
- 操作：向用户展示验证结果，请求确认
- 参数：validation_report
- 工具：用户交互接口
- 质量门禁：用户明确确认或提供补充信息

### 节点5：数据集绑定写入
- 操作：将验证通过的数据集信息写入task_state
- 参数：dataset_binding
- 工具：状态写入器
- 质量门禁：task_state.json中包含有效dataset_binding

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| min_samples | 50 | [1] | ROM训练最少快照数，少于该值POD/PCA不稳定 |
| sensor_min_ratio | 0.01 | [2] | 稀疏传感器数与全场自由度之比下限 |
| parameter_coverage | 0.8 | 通用 | 训练集参数空间覆盖率阈值 |
| format_tolerance | 0.05 | 通用 | 维度偏差容忍度（5%） |

### 校准数值
以下数值来自SHRED架构验证实验，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| latent_dim_range | [8, 64] | [1] | SHRED默认潜空间维度范围 |
| hidden_dim_range | [32, 128] | [1] | LSTM隐藏层维度范围 |
| time_steps_min | 20 | [1] | 时间序列最小步长 |

## 边界与分流

### 前提否定即改道
| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| 数据集路径存在 | 转入数据集发现流程（自动搜索或用户指定） |
| 格式为NPZ/NPY | 启动格式转换器（需用户确认转换规则） |
| 参数空间已声明 | 降级为无参数化ROM（固定工况训练） |
| 传感器位置已定义 | 使用默认均匀分布传感器或请求用户定义 |

### 异常处理
- 数据集文件损坏：跳过损坏文件，记录warning，继续验证剩余文件
- 参数维度不匹配：列出具体不匹配项，请求用户修正
- 传感器超出几何边界：标记越界传感器，请求用户重新定义

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 必填字段完整性 | 100% | 阻断，请求用户补充 |
| 数据格式一致性 | 95% | 警告，允许部分通过 |
| 参数范围覆盖度 | 80% | 警告，请求用户确认 |
| 传感器位置有效性 | 100% | 阻断，请求用户修正 |

## 回退策略

1. **数据集缺失**：调用数据集发现模块搜索本地目录或ModelScope
2. **格式不兼容**：启动格式转换适配器（需用户确认转换参数）
3. **参数空间不足**：降级为插值ROM或请求用户提供补充数据
4. **用户无响应**：保存当前状态，标记为pending，等待用户输入

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- CFD ROM训练任务的数据准备阶段
- 稀疏传感器到全场重建的SHRED/SHRED-ROM任务
- 参数化流体力学问题的降阶建模
- 多工况CFD数据集的标准化接入

配套资源：
- `cfd-rom-architecture-selection`：ROM架构选择与超参配置
- `cfd-transferable-rom-workflow-end-to-end`：端到端可迁移ROM工作流

## 证据来源

[1] Tomasetto M, Williams JP, Braghin F, Manzoni A, Kutz JN. Reduced Order Modeling with Shallow Recurrent Decoder Networks. Nature Communications, 2025. DOI: 10.1038/s41467-025-65126-y

[2] Scardino C, Riva S, Introini C, et al. Real-Time Monitoring of MHD Liquid Metal Flows with SHRED. arXiv:2608.28366, 2026.

[3] Riva S, Introini C, Kutz JN, Cammi A. Multi-Fidelity Learning with SHRED. arXiv:2606.05202, 2026.
