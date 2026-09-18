# OneScience Workflow Output Contracts and Status Management

## 适用范围

本卡片面向OneScience标准工作流的输出产物契约规范与任务状态管理，提供s01（数据验证）、s04（推理输出）、s05（评估输出）三个步骤的标准文件命名、目录结构、JSON schema定义，以及execution-manifest.json的状态更新规则与一致性校验机制。适用于所有CFD/PDE问题的标准化工作流执行与产物管理。

## 输入

- 工作流步骤定义（s01-s05）
- 步骤执行产物（原始输出）
- 任务上下文信息

## 输出

- 标准化的输出文件集（符合契约规范）
- execution-manifest.json（状态更新）
- 产物一致性校验报告

## 流程节点

### 步骤1：s01数据验证步骤输出契约

**标准输出文件清单**：

| 文件名 | 格式 | 必填字段 | 说明 |
|--------|------|---------|------|
| dataset_manifest.json | JSON | dataset_path, sample_count, variables, units, coordinates, license | 数据集元数据清单 |
| data_contract.json | JSON | input_fields, target_fields, units, coordinates | 数据输入输出契约 |
| data_audit.md | Markdown | 审计结论, 变量统计, 错误检测结果 | 数据审计报告 |

**dataset_manifest.json schema**：
```json
{
  "dataset_path": "string（数据集路径）",
  "sample_count": "integer（样本数量）",
  "variables": ["string（变量名列表）"],
  "units": {"variable_name": "string（单位）"},
  "coordinates": {
    "x": {"min": "float", "max": "float", "points": "integer"},
    "t": {"min": "float", "max": "float", "points": "integer"}
  },
  "license": "string（数据许可协议）",
  "created_at": "ISO datetime",
  "source": "string（数据来源）"
}
```

**data_contract.json schema**：
```json
{
  "input_fields": [
    {"name": "string", "type": "string", "unit": "string", "range": "[min, max]"}
  ],
  "target_fields": [
    {"name": "string", "type": "string", "unit": "string", "description": "string"}
  ],
  "units": {"field_name": "string"},
  "coordinates": {"x": "float[]", "t": "float[]"}
}
```

**CFD_S039案例**：实际仅生成data_verification_report.json，未见标准三文件，导致下游步骤无法引用标准化数据契约 [报告证据]。

### 步骤2：s04推理输出步骤契约

**标准目录结构**：
```
s04_output/
├── solution_fields/          # 解场目录
│   ├── u_mean.npy           # 预测均值场（npy格式）
│   ├── u_std.npy            # 预测标准差场（npy格式）
│   └── coordinates.json     # 坐标信息
├── pde_residuals/           # PDE残差目录
│   ├── residual_mean.npy    # 残差均值场
│   └── residual_std.npy     # 残差标准差场（可选）
└── boundary_residuals.csv   # 边界残差（逐点）
```

**boundary_residuals.csv schema**：
```csv
x_coord,u_pred,u_true,residual
0.0,0.123,0.120,0.003
0.1,0.234,0.230,0.004
...
```

**CFD_S039案例**：实际产出为results/mean_prediction.csv等非标准命名，缺少独立的solution_fields/和pde_residuals/目录 [报告证据]。

### 步骤3：s05评估输出步骤契约

**标准输出文件清单**：

| 文件名 | 格式 | 必填内容 | 说明 |
|--------|------|---------|------|
| evaluation.json | JSON | 各指标计算结果 | 评估指标汇总 |
| worst_cases.csv | CSV | sample_id, relative_L2_error, PDE_residual, boundary_error | 最差案例表（按误差降序） |
| applicability_report.md | Markdown | 适用物理范围, 参数范围, 网格限制, 失效模式 | 模型适用域报告 |
| PASS_REJECT_BLOCKED.txt | Text | 判定结论, 判定依据, 指标对比表, 下一步建议 | 最终结论文件 |

**evaluation.json schema**：
```json
{
  "status": "PASS|PARTIAL|REJECT|BLOCKED",
  "metrics": {
    "relative_L2": {"value": "float", "threshold": 0.1, "pass": "boolean"},
    "MSE_PDE": {"value": "float", "threshold": 0.01, "pass": "boolean"},
    "boundary_error_left": {"value": "float", "threshold": 0.01, "pass": "boolean"},
    "boundary_error_right": {"value": "float", "threshold": 0.01, "pass": "boolean"},
    "initial_condition_error": {"value": "float", "threshold": 0.01, "pass": "boolean"},
    "avg_prediction_std": {"value": "float", "threshold": 1.0, "pass": "boolean"}
  },
  "overall_pass": "boolean",
  "rejection_reasons": ["string"]
}
```

**CFD_S039案例**：缺少worst_cases.csv、applicability_report.md和PASS_REJECT_BLOCKED.txt，且evaluation_report.json状态标注为PARTIAL而非应有的REJECT [报告证据]。

### 步骤4：execution-manifest.json状态管理

**状态枚举值定义**：

| 状态值 | 语义 | 使用场景 |
|--------|------|---------|
| completed | 阶段成功完成 | 所有产物存在且通过验证 |
| partial | 阶段部分完成 | 部分产物缺失或指标未达标 |
| failed | 阶段执行失败 | 执行过程中出现错误 |
| blocked | 阶段被阻塞 | 环境/依赖问题导致无法执行 |

**状态更新规则**：
1. **更新时机**：阶段实际完成后立即更新status字段
2. **产物一致性**：若产物存在则status必须为completed或partial，不得为blocked
3. **failure_category**：仅在真正的环境/依赖失败时使用blocked，训练产出存在时不得标记为blocked

**状态-产物校验逻辑**：
```python
def validate_manifest_status(manifest, artifact_dir):
    for phase in manifest["execution_phases"]:
        phase_name = phase["name"]
        status = phase["status"]
        artifacts_exist = check_artifacts_exist(artifact_dir, phase_name)
        
        if status == "blocked" and artifacts_exist:
            return False, f"Phase {phase_name} marked blocked but artifacts exist"
        if status == "completed" and not artifacts_exist:
            return False, f"Phase {phase_name} marked completed but artifacts missing"
    return True, "All phases consistent"
```

**CFD_S039案例**：manifest声称blocked但training_history.json和param_store.pt存在，状态与产物严重矛盾 [报告证据]。

### 步骤5：产物命名一致性校验

**校验规则**：
1. **文件名匹配**：检查实际输出文件名是否符合标准契约
2. **目录结构**：检查目录层级是否符合规范
3. **字段完整性**：检查JSON文件是否包含所有必填字段
4. **格式合规**：检查数据类型、单位、范围是否符合schema

**校验报告格式**：
```json
{
  "step": "s01|s04|s05",
  "compliance_score": "float（0-1）",
  "missing_files": ["string"],
  "extra_files": ["string"],
  "schema_violations": ["string"],
  "recommendations": ["string"]
}
```

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 标准值 | 来源 | 说明 |
|------|--------|------|------|
| dataset_manifest必填字段 | 6个 | [报告CFD_S039] | 数据集核心元数据 |
| data_contract必填字段 | 4个 | [报告CFD_S039] | 输入输出契约定义 |
| s04目录结构 | 3级 | [报告CFD_S039] | solution_fields/pde_residuals/boundary_residuals |
| s05输出文件数 | 4个 | [报告CFD_S039] | evaluation/worst_cases/applicability/PASS_REJECT |
| manifest状态枚举 | 4种 | [报告CFD_S039] | completed/partial/failed/blocked |

### 校准数值（体系专属值）

以下数值来自CFD_S039任务实测，供量级校准；其他任务需以自身证据重新锚定：

| 指标 | 实测值 | 标准值 | 偏差 | 说明 |
|------|--------|--------|------|------|
| s01输出文件数 | 1 | 3 | -2 | 缺失data_contract和data_audit |
| s04目录数 | 1（results/） | 3 | -2 | 缺失solution_fields和pde_residuals |
| s05输出文件数 | 2 | 4 | -2 | 缺失worst_cases和applicability |
| manifest状态一致性 | 不一致 | 一致 | - | blocked但产物存在 |

## 边界与分流

### 契约违反处理

| 违反类型 | 处理方案 |
|---------|---------|
| 文件缺失 | 生成缺失文件，填充默认值或从现有数据推导 |
| 字段缺失 | 补充缺失字段，标注"待填充" |
| 格式错误 | 重新格式化，保留原始数据 |
| 命名不符 | 重命名文件，更新引用路径 |

### 降级策略

1. **完全缺失**：生成最小化占位文件，标注"待补充"
2. **部分缺失**：基于现有数据推导缺失内容，标注推导依据
3. **格式冲突**：保留原始格式，添加兼容层

## 质量检查

- [ ] s01三文件均存在且必填字段完整
- [ ] s04标准目录结构正确（solution_fields/pde_residuals/boundary_residuals）
- [ ] s05四文件均存在且内容完整
- [ ] execution-manifest.json状态与实际产物一致
- [ ] 所有JSON文件可通过标准解析器解析

## 回退策略

1. **契约不明确**：参照本卡标准生成最小合规产物
2. **状态冲突**：以实际产物存在性为准，更新manifest状态
3. **格式不兼容**：生成新格式文件，保留旧文件作为备份

## 资源召回建议

- 当任务涉及OneScience工作流执行或产物管理时召回本卡
- 配套卡片：`cfd-bayesian-pinn-training-convergence`（训练收敛）、`cfd-pinn-evaluation-metrics`（评估指标）
- 当需要检查已有工作流契约定义时，检索相关任务定义文件

## 证据来源

[1] CFD_S039归因报告，执行产物分析，2026
[2] OneScience标准工作流定义（基于任务执行规范推导）
