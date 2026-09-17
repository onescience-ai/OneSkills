# 谱增强PINN高频多尺度PDE求解工作流

## 适用范围

**触发条件**：
- 需要执行谱增强PINN求解高频/多尺度PDE的完整工作流
- 已有PDE配点数据，需要系统化从数据到评估的全流程
- 需要确保每步质量门禁通过后推进下一步

**适用场景**：
- 流体动力学中激波捕获、声波传播等高频问题
- 地震波在非均匀介质中的传播模拟
- 可压缩流体的高超声速流动求解
- 需要物理一致性评估的PDE求解项目

**不适用场景**：
- 仅需单步操作（如仅训练或仅评估）
- 无配点数据的纯理论分析

## 输入

- PDE配点数据集路径（{DATASET_PATH}）
- 数据集名称与来源（{DATASET_NAME}）
- 数据契约（{DATA_CONTRACT}，可选）
- 切分配置（{SPLIT_CONFIG}）
- 模型名称（{MODEL_NAME}，默认Spectral PINN、SIREN）
- 训练配置（{TRAIN_CONFIG}）
- 验收指标（{METRICS}）

## 输出

- dataset_manifest.json、data_contract.json、data_audit.md
- train/val/test_manifest.json、normalization.json
- best_checkpoint.pt、train_config.json、training_metrics.csv
- solution_fields/、pde_residuals/、boundary_residuals.csv
- evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 流程节点

### Step 1：数据接入与契约核验（s01）
- **操作**：接入高频与多尺度PDE配点，核验样本、变量、单位、网格坐标及许可
- **依赖**：无（起始步骤）
- **输出**：dataset_manifest.json、data_contract.json、data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **分支**：缺少必填输入时返回BLOCKED并列出缺项

### Step 2：预处理与数据切分（s02）
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **依赖**：s01
- **输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练（s03）
- **操作**：训练Spectral PINN、SIREN完成指定输入到目标物理量的映射
- **依赖**：s02
- **输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **分支**：若提供{INIT_CHECKPOINT}须检查结构兼容性

### Step 4：方程求解与物理残差恢复（s04）
- **操作**：在查询配点或网格上恢复解场、导数、边界值与方程残差
- **依赖**：s03
- **输出**：solution_fields/、pde_residuals/、boundary_residuals.csv
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照
- **分支**：禁止只依据训练损失判定方程已求解

### Step 5：任务验收与适用域判定（s05）
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **依赖**：s04
- **输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **分支**：{RUN_OOD_TEST}为true时执行几何或工况外推测试

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认模型 | Spectral PINN、SIREN | 场景需求书 | 核心模型选择 |
| 训练框架 | PyTorch | [1] | 默认框架 |
| 默认epochs | 100 | 场景需求书 | 训练轮数 |
| 默认batch_size | 8 | 场景需求书 | 批量大小 |
| 默认learning_rate | 0.001 | 场景需求书 | 学习率 |
| 默认seed | 42 | 场景需求书 | 随机种子 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心 |
| 相对误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 切分比例 | 0.7/0.15/0.15 | 场景需求书 | 训练/验证/测试 |

## 边界与分流

- **s01 BLOCKED**：缺少必填输入 → 列出缺项，不编造数据
- **s03 训练不收敛**：损失非有限值 → 检查学习率、谱截断频率、初始化策略
- **s04 残差异常**：解场导数非有限 → 检查自动微分精度、谱截断是否过高
- **s05 REJECT**：误差超门限 → 分析最差样本，调整模型或配点策略
- **s05 OOD测试**：域外工况误差恶化 → 明确适用域边界，建议CFD复核

## 质量检查

- 每步输出文件完整性检查
- 质量门禁逐项验证
- 数据泄漏检测（时间/空间/工况维度）
- 物理量纲一致性检查
- 外推能力验证

## 回退策略

- 工作流某步失败 → 分析失败原因，调整参数后从失败步重启
- 全流程不通过 → 考虑更换模型架构或增加配点密度
- OOD测试失败 → 降低适用域声明，增加工况覆盖训练

## 资源召回建议

- 当需要执行谱增强PINN完整工作流时召回本卡
- 配套资源：cfd-spectral-pinn-multiscale-pde-solution（场景卡）、各步骤任务卡
- 与 cfd-pde-data-intake-contract-validation、cfd-pde-preprocessing-data-splitting、cfd-pde-model-training 互补

## 证据来源

[1] "Neuro-Spectral Architectures for Causal Physics-Informed Networks", Bizzi et al., NeurIPS 2025, DOI: 10.48550/arXiv.2509.04966
[2] "Data-Free PINNs for Compressible Flows: Mitigating Spectral Bias and Gradient Pathologies via Mach-Guided Scaling and Hybrid Convolutions", Yano, arXiv 2026, DOI: 10.48550/arXiv.2603.01001
