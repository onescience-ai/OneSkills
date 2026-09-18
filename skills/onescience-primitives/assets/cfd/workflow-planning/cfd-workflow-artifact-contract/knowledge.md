# CFD工作流产物契约规范

## 适用范围
本卡适用于CFD神经PDE求解器工作流的每个步骤，定义必填输出文件名、格式和内容要求，确保工作流可复现、可验证、可追溯。覆盖数据处理、模型训练、推理、评估等全流程。

## 输入
- 工作流步骤：s01-s05（数据处理、模型训练、推理、评估等）
- 任务配置：参数、超参数、资源约束
- 验收标准：通过/拒绝/阻塞条件

## 输出
- 产物清单：每个步骤的必填输出文件
- 格式规范：JSON、CSV、Markdown等格式要求
- 内容要求：每个文件的具体字段和验证标准

## 流程节点

### 1. 数据处理阶段（s01）
**必填产物**：
- **dataset_manifest.json**：数据集元信息，包含样本数量、特征维度、数据来源
- **data_contract.json**：数据契约，定义输入输出格式、变量名、单位、范围
- **data_audit.md**：数据审计报告，包含质量检查、异常值处理、统计摘要

**格式要求**：
```json
{
  "dataset_name": "string",
  "num_samples": "integer",
  "feature_dimensions": ["list of strings"],
  "data_source": "string",
  "license": "string",
  "created_at": "ISO date"
}
```

### 2. 数据切分阶段（s02）
**必填产物**：
- **train_manifest.json**：训练集清单，包含样本索引、参数范围、数据来源
- **validation_manifest.json**：验证集清单，同上格式
- **test_manifest.json**：测试集清单，同上格式
- **normalization.json**：归一化参数，包含均值、标准差、最小值、最大值

**格式要求**：
```json
{
  "split_name": "train|validation|test",
  "num_samples": "integer",
  "sample_indices": ["list of integers"],
  "parameter_ranges": {"param1": {"min": "float", "max": "float"}},
  "normalization": {
    "method": "minmax|zscore",
    "mean": ["list of floats"],
    "std": ["list of floats"]
  }
}
```

### 3. 模型训练阶段（s03）
**必填产物**：
- **best_checkpoint.pt**：最优模型权重（PyTorch格式）
- **train_config.json**：训练配置，包含超参数、优化器、学习率调度
- **training_metrics.csv**：训练指标，包含损失曲线、验证指标、学习率
- **environment.txt**：环境信息，包含Python版本、库版本、GPU信息

**格式要求**：
```json
{
  "model_name": "string",
  "architecture": {"type": "string", "params": "integer"},
  "optimizer": {"type": "string", "lr": "float"},
  "training": {"epochs": "integer", "batch_size": "integer"},
  "best_metric": {"name": "string", "value": "float"}
}
```

### 4. 推理阶段（s04）
**必填产物**：
- **predictions/**：预测结果目录，包含每个测试样本的预测文件
- **inference_manifest.json**：推理清单，包含预测文件路径、计算时间、内存使用
- **timing.csv**：时序数据，包含每个样本的推理时间、总时间、加速比

**格式要求**：
```json
{
  "num_predictions": "integer",
  "prediction_files": ["list of file paths"],
  "total_time_seconds": "float",
  "avg_time_per_sample": "float",
  "speedup_vs_baseline": "float"
}
```

### 5. 评估阶段（s05）
**必填产物**：
- **evaluation.json**：评估结果，包含精度指标、物理一致性指标、计算效率指标
- **worst_cases.csv**：最差案例，包含性能最差的样本索引、误差分析
- **applicability_report.md**：适用性报告，包含模型适用域、泛化能力、风险评估
- **PASS_REJECT_BLOCKED.txt**：验收结论，明确通过/拒绝/阻塞状态

**格式要求**：
```json
{
  "accuracy_metrics": {"rel_l2_error": "float", "mse": "float"},
  "physics_consistency": {"mass_conservation_error": "float", "energy_conservation_error": "float"},
  "computational_efficiency": {"training_time": "float", "inference_time": "float"},
  "acceptance": "PASS|REJECT|BLOCKED",
  "reason": "string"
}
```

## 关键参数

### 通用判据（方法层）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 数据审计覆盖率 | 100% | [通用] | 所有样本必须经过质量检查 |
| 归一化方法 | min-max或z-score | [通用] | 根据数据分布选择 |
| 训练验证测试比例 | 80:10:10 | [论文1] | 标准切分比例 |
| 检查点保存频率 | 每epoch或每N步 | [通用] | 根据训练时长调整 |
| 评估指标完整性 | 覆盖精度、物理、效率 | [通用] | 全面评估模型性能 |

### 校准数值（具体案例参考）
| 参数 | 数值 | 来源 | 说明 |
|------|------|------|------|
| 相对L2误差阈值 | <0.1 | [通用] | 通过标准 |
| 质量守恒误差阈值 | <0.05 | [通用] | 通过标准 |
| 能量守恒误差阈值 | <0.05 | [通用] | 通过标准 |
| 推理加速比 | >10倍 | [论文1] | 相比传统方法 |

## 边界与分流

### 产物缺失
当必填产物缺失时：
- 工作流状态设为BLOCKED
- 记录缺失产物名称和原因
- 提供补全建议或替代方案

### 格式不兼容
当产物格式不符合规范时：
- 自动转换格式（如CSV到JSON）
- 记录转换日志和原始格式
- 验证转换后数据完整性

### 验收不通过
当评估结果不满足阈值时：
- 工作流状态设为REJECT
- 记录具体失败指标和原因
- 提供改进建议（如调整超参数、增加数据）

## 质量检查
1. **完整性检查**：验证所有必填产物是否存在
2. **格式检查**：验证JSON、CSV等格式是否正确
3. **内容检查**：验证字段是否完整、值是否在合理范围
4. **一致性检查**：验证不同产物间的数据是否一致
5. **可追溯性检查**：验证是否有足够的日志和元数据

## 回退策略
1. **产物缺失**：重新运行缺失步骤或使用默认值
2. **格式错误**：编写格式转换脚本或使用验证工具
3. **验收失败**：分析失败原因，调整参数或数据后重试
4. **环境问题**：检查依赖版本，使用容器化环境

## 资源召回建议
- **何时召回**：当需要定义或验证工作流产物规范时
- **配套资源**：cfd-physics-constrained-loss-design（物理约束损失）、cfd-public-datasets（公开CFD数据集）

## 证据来源
[1] Physics-Informed Machine Learning in Biomedical Science and Engineering, Annual Review of Biomedical Engineering, 2026, DOI: 10.1146/annurev-bioeng-110824-124907