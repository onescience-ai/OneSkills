# 方法配置与输入输出契约验证的具体执行要求

## 适用范围
适用于遥感制图任务中方法配置验证场景。在核心计算前，必须执行输入输出契约验证，确保方法工件版本与运行环境兼容、目标变量与输出结构一致。

## 输入
- 方法配置：随机森林参数（n_estimators, max_depth）、随机种子等。
- 输入数据：小样本输入，用于干运行验证。

## 输出
- 方法工件身份报告：`method_identity_report.json`
- 输入输出兼容性矩阵：`io_compatibility_matrix.json`
- 最小干运行日志：`dry_run_log.json`

## 流程节点
1. 方法配置检查 → 2. 输入输出兼容性验证 → 3. 最小干运行执行 → 4. 验证报告生成

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| dry_run_sample_size | 小样本（如100个像元） | [论文1] | 用于快速验证，不执行全量计算 |
| io_compatibility_matrix | 输入输出维度、类型、范围 | [论文1] | 确保输入输出结构一致 |
| random_seed_freeze | 固定随机种子 | [论文1] | 确保结果可复现 |
| method_identity | 算法版本、参数配置 | [论文1] | 记录方法工件身份 |

## 边界与分流
- 当使用合成数据时：仍需执行干运行验证，确保管线逻辑正确。
- 当验证失败时：阻塞任务，不进入核心计算。

## 质量检查
- 检查是否产出 `method_identity_report.json`、`io_compatibility_matrix.json` 和 `dry_run_log.json`。
- 验证干运行无 NaN/Inf 值。

## 回退策略
- 如果干运行失败，记录失败原因并阻塞任务。

## 资源召回建议
- 当任务涉及方法配置验证时召回本卡片。
- 配套资源：数据真实性验收标准、预处理工作流、输出格式规范。

## 证据来源
[1] Validation of the Sentinel Simplified Level 2 Product Prototype Processor (SL2P) for mapping cropland biophysical variables using Sentinel-2/MSI and Landsat-8/OLI data, Djamai et al., Remote Sensing of Environment, 2019, DOI: 10.1016/j.rse.2019.03.020