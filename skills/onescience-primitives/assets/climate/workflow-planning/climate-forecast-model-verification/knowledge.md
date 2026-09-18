# 气象时序预报模型选择与验证规范

## 适用范围
适用于气象时序预报任务的模型选择、配置验证和性能评估环节。覆盖LSTM、Transformer、GRU等深度学习模型以及传统统计模型在气象预报中的应用。当任务涉及模型选型、输入输出契约验证、最小干运行或性能指标评估时，本卡片提供标准化的验证流程和指标体系。

## 输入
- 候选模型列表（模型类型、架构参数、训练配置）
- 输入特征矩阵（shape、变量含义、时间步长）
- 预报目标定义（目标变量、预报时效、输出shape）

## 输出
- 方法工件与配置身份报告（模型适配性评估）
- 输入输出兼容性矩阵
- 最小干运行日志（前向传播检查、梯度检查、输出范围检查）
- 性能评估报告（R2、Skill Score、RMSE、MAE）

## 流程节点
1. **方法工件身份验证** → 评估候选模型是否适配当前气象时序预报任务
2. **输入输出兼容性检查** → 验证输入特征维度与模型输入维度匹配性
3. **最小干运行** → 用小batch验证模型能正常前向传播且输出无NaN/Inf
4. **随机性控制** → 固定全局随机种子，确保CUDA确定性
5. **性能门禁检查** → 对R2、Skill Score等指标设置最低要求，不达标时自动标记REJECT
6. **性能诊断** → 对异常指标（如负R2）给出诊断和改进建议

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| R2最低要求 | >0 | [WMO-No. 1145] | 低于均值预测时自动REJECT |
| Skill Score最低要求 | >0 | [WMO-No. 1145] | 低于持续性预报基线时REJECT |
| 干运行检查 | 输出无NaN/Inf | [Pangu-Weather, 2023] | 前向传播必须产生有效数值 |
| 梯度检查 | 梯度范数非零 | [Statistical Methods, 2018] | 反向传播必须产生有效梯度 |
| 输入输出shape | 必须匹配 | [MERRA-2, 2017] | 输入特征维度与模型输入维度一致 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 温度RMSE阈值 | <3°C(短期), <5°C(中期) | [WMO-No. 1145] | 以下数值来自WMO业务预报标准，供量级校准；其他体系需以自身证据重新锚定 |
| 湿度RMSE阈值 | <15% | [WMO-No. 1145] | |
| 风速RMSE阈值 | <2m/s | [WMO-No. 1145] | |
| LSTM隐藏层 | 64-128 | [Pangu-Weather, 2023] | 气象时序预报常用配置 |

## 边界与分流
- 当干运行输出含NaN/Inf时：BLOCKED，检查模型架构和输入数据
- 当R2<0时：自动REJECT，触发模型回退或参数调整
- 当Skill Score<0时：模型性能低于持续性预报基线，建议回退到简单模型
- 当输入输出shape不匹配时：调整模型输入层或特征工程

## 质量检查
- 干运行日志必须包含前向传播检查、梯度检查、输出范围检查
- 性能报告必须包含R2、Skill Score、RMSE、MAE
- R2<0时必须有诊断记录和改进建议
- 随机种子必须固定并记录

## 回退策略
- 模型不适用时：选择替代模型架构
- 干运行失败时：检查数据预处理和模型配置
- 性能不达标时：调整超参数或选择更简单模型
- 负R2诊断：检查数据质量、特征工程、模型复杂度

## 资源召回建议
- 当任务涉及气象预报模型选择和验证时召回本卡片
- 配套资源：climate-forecast-acceptance-quality（验收标准）、climate-forecast-independent-validation（独立验证）

## 补充证据
[D1] WMO Guidelines on Verification of Numerical Weather Prediction, WMO-No. 1145, WMO（accessed_at 2026-09-18，交叉验证）

## 证据来源
[1] Accurate medium-range global weather forecasting with 3D neural networks, Bi et al., Nature, 2023, DOI: 10.1038/s41586-023-06185-3
[2] The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2), Gelaro et al., Journal of Climate, 2017, DOI: 10.1175/jcli-d-16-0758.1
[3] Statistical and Machine Learning forecasting methods: Concerns and ways forward, Makridakis et al., PLoS ONE, 2018, DOI: 10.1371/journal.pone.0194889