# CFD模型评估标准规范

## 适用范围

CFD模型评估的完整指标体系规范，适用于任务验收阶段的统计误差计算、物理约束校验、泛化能力评估和计算收益分析。支持评估报告的标准格式生成、最差样本分析与PASS/REJECT/BLOCKED结论判定。

## 输入

### 评估输入数据
- **预测场数据**：模型输出的压力、速度、温度等场变量
- **参考场数据**：DNS/LES高保真解或实验测量数据
- **几何与边界条件**：模型使用的参数设置
- **计算资源信息**：GPU/CPU时间、内存使用量

### 评估任务要求
- 统计误差计算
- 物理约束校验
- 泛化能力评估
- 计算收益分析
- 最差样本识别与分析

## 输出

### 评估报告必填字段（evaluation.json）
```json
{
  "task_id": "string",
  "evaluation_timestamp": "ISO8601",
  "metrics_summary": {
    "relative_L2_error": "float",
    "rmse": "float",
    "max_error": "float",
    "conservation_residual": {
      "mass_conservation": "float",
      "momentum_conservation": "float",
      "energy_conservation": "float"
    },
    "boundary_error": {
      "wall_pressure_error": "float",
      "inlet_velocity_error": "float",
      "outlet_pressure_error": "float"
    },
    "generalization_score": "float",
    "computational_gain": "float"
  },
  "worst_cases": [
    {
      "sample_id": "string",
      "error_metrics": {},
      "failure_mode": "string",
      "root_cause": "string"
    }
  ],
  "applicability_domain": {
    "coverage": "float",
    "extrapolation_risk": "string",
    "recommended_use_cases": []
  },
  "acceptance_verdict": "PASS|REJECT|BLOCKED",
  "validation_status": "complete|incomplete",
  "execution_manifest": {
    "completed_steps": [],
    "missing_artifacts": []
  }
}
```

### 必需评估文件
- `evaluation.json`：主评估报告
- `worst_cases.csv`：最差样本详情
- `applicability_report.md`：适用域分析报告
- `PASS_REJECT_BLOCKED.txt`：验收结论文件

## 流程节点

```
统计误差计算 → 物理约束校验 → 泛化能力评估 → 计算收益分析 → 最差样本分析
     ↓              ↓              ↓              ↓              ↓
相对L2误差      守恒残差       交叉验证        GPU时间对比     敏感性分析
RMSE           边界误差       外推测试        内存使用对比     失败模式识别
最大误差       物理一致性     稳定性测试      FLOPS对比       根因分析
```

### 步骤1：统计误差计算
- 相对L2误差：`||y_pred - y_true||_2 / ||y_true||_2`
- RMSE：`sqrt(mean((y_pred - y_true)^2))`
- 最大误差：`max(|y_pred - y_true|)`
- 相关系数：Pearson/Spearman相关系数

### 步骤2：物理约束校验
- **质量守恒残差**：`|∫ρu·n dA| / (ρ_ref * U_ref * A_ref)`
- **动量守恒残差**：`|∫(ρuu - τ + pI)·n dA| / (ρ_ref * U_ref² * A_ref)`
- **能量守恒残差**：`|∫(ρeu - τu + pu - q)·n dA| / (ρ_ref * U_ref³ * A_ref)`
- **边界误差**：壁面压力、入口速度、出口压力的相对误差

### 步骤3：泛化能力评估
- 交叉验证：K折交叉验证或留一法
- 外推测试：在训练分布外数据上测试
- 稳定性测试：噪声扰动下的性能变化

### 步骤4：计算收益分析
- GPU时间对比：模型推理 vs CFD求解
- 内存使用对比
- FLOPS对比
- 加速比计算

### 步骤5：最差样本分析
- 识别误差最大的样本
- 分析失败模式（过拟合、欠拟合、边界条件错误等）
- 根因分析（几何复杂度、流动特征、数据质量等）

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差阈值 | < 0.1 | 工程精度要求 | 超出需标记warning |
| 质量守恒残差 | < 1e-3 | 物理一致性 | 超出需标记violation |
| 动量守恒残差 | < 1e-2 | 物理一致性 | 超出需标记violation |
| 能量守恒残差 | < 1e-2 | 物理一致性 | 超出需标记violation |
| 壁面压力误差 | < 5% | 工程精度要求 | 超出需标记warning |
| 入口速度误差 | < 2% | 边界条件精度 | 超出需标记warning |
| 出口压力误差 | < 3% | 边界条件精度 | 超出需标记warning |

### 校准数值（典型CFD基准案例）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| NACA 0012 Cp RMSE | 0.05-0.1 | NASA TM 2006 | RANS模型典型值 |
| 方柱绕流Cd误差 | 5-15% | V&V Workshop | LES模型典型值 |
| 后向台阶Re分离误差 | 3-10% | 文献值 | 湍流模型典型值 |
| 质量守恒残差（RANS） | 1e-5 ~ 1e-4 | 数值精度 | 收敛标准 |

## 边界与分流

### 物理约束违反时
- **质量守恒残差 > 1e-3**：检查网格质量、数值格式、收敛标准
- **动量守恒残差 > 1e-2**：检查湍流模型、边界条件
- **能量守恒残差 > 1e-2**：检查热源项、辐射模型

### 评估指标缺失时
- **conservation_residual缺失**：重新运行物理约束计算模块
- **boundary_error缺失**：从场数据中提取边界值计算
- **worst_cases缺失**：从误差分布中自动识别最差样本

### 验证报告不完整时
- **缺少必需文件**：生成占位文件并标注`"validation_status": "incomplete"`
- **字段被截断**：修复报告生成脚本，重新执行
- **execution-manifest缺失**：补生成清单文件

## 质量检查

### 检查点1：指标完整性
- 所有必需指标已计算
- 指标数值在合理范围内
- 无NaN/Inf值

### 检查点2：物理一致性
- 守恒残差满足阈值要求
- 边界误差满足精度要求
- 无明显物理违规

### 检查点3：报告完整性
- evaluation.json格式正确
- worst_cases.csv包含所有最差样本
- applicability_report.md内容完整
- PASS_REJECT_BLOCKED.txt结论明确

### 检查点4：最差样本分析
- 最差样本已识别
- 失败模式已分类
- 根因分析已给出

### 失败处理
- 检查点1失败：重新计算缺失指标
- 检查点2失败：标记物理违规，建议重新训练
- 检查点3失败：补全报告文件
- 检查点4失败：执行最差样本分析

## 回退策略

### 策略1：指标降级计算
- 缺少conservation_residual → 使用简化版本（仅质量守恒）
- 缺少boundary_error → 使用边界层理论估算

### 策略2：报告格式降级
- evaluation.json不完整 → 生成简化版本并标注
- worst_cases.csv缺失 → 从误差分布中提取

### 策略3：验收结论降级
- 无法完整评估 → 标记`BLOCKED`并给出阻塞原因
- 部分指标不达标 → 标记`REJECT`并给出改进方向

## 资源召回建议

### 何时召回本卡片
- 任务验收阶段需要计算物理约束指标
- 评估报告生成时缺少必需字段
- 需要分析最差样本的失败模式

### 配套资源
- `cfd-airfoil-wall-pressure-shear-dataset-contract`：数据集规范
- `cfd-acceptance-validation-applicability`：验收验证流程
- `cfd-airfoil-data-intake-contract-validation`：数据接入验证

## 补充证据（权威文档）

[D1] AIAA CFD Verification and Validation Guidelines, American Institute of Aeronautics and Astronautics, 2023, URL: https://www.aiaa.org/Standards/Details/2563（accessed_at 2026-09-17，权威标准文档）
[D2] NASA CFD Best Practices Guide, NASA Langley Research Center, 2024, URL: https://turbmodels.larc.nasa.gov/best_practices.html（accessed_at 2026-09-17，权威最佳实践）

## 证据来源

[1] AIAA CFD Verification and Validation Guidelines, AIAA, 2023
[2] NASA CFD Best Practices Guide, NASA Langley Research Center, 2024
