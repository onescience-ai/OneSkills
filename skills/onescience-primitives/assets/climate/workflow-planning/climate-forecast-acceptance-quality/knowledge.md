# 气象预报任务验收门限与质量标志规范

## 适用范围
适用于气象预报任务的验收判定和产品质量标志生成环节。覆盖短期（24h）、中期（48-72h）和延伸期预报的性能评估。当任务涉及验收门限设定、性能指标判定或产品质量标志编码时，本卡片提供标准化的验收流程和质量标志体系。

## 输入
- 预报结果（逐时预报值序列）
- 观测/再分析参考值
- 验收门限定义（可由用户提供或由agent提出并等待确认）

## 输出
- 性能评估报告（R2、Skill Score、RMSE、MAE）
- 质量标志文件（逐时逐站的质量等级）
- 产品元数据（坐标系统、时间基准、单位信息）
- 验收判定（PASS/REJECT/BLOCKED）

## 流程节点
1. **验收门限确认** → 在task_understanding阶段明确列出验收门限需求并向场景确认
2. **性能指标计算** → 计算R2、Skill Score、RMSE、MAE等指标
3. **性能门禁检查** → 对比验收门限，判定是否达标
4. **质量标志生成** → 根据预报质量和不确定性生成质量标志等级
5. **产品元数据生成** → 生成符合CF约定的产品元数据
6. **验收判定** → 综合各项指标给出最终验收判定

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| R2基本要求 | >0 | [WMO-No. 1145] | 低于均值预测时自动REJECT |
| Skill Score基本要求 | >0 | [WMO-No. 1145] | 低于持续性预报基线时REJECT |
| 门限确认 | 必须在task_understanding阶段 | [WMO-No. 1145] | 门限未确认前所有交付项标记BLOCKED |
| 质量标志 | 必须关联不确定性 | [CF Conventions] | 每个质量等级对应不同的不确定性范围 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 温度RMSE(短期24h) | <3°C | [WMO-No. 1145] | 以下数值来自WMO业务预报标准，供量级校准；其他体系需以自身证据重新锚定 |
| 温度RMSE(中期48-72h) | <5°C | [WMO-No. 1145] | |
| 湿度RMSE | <15% | [WMO-No. 1145] | |
| 风速RMSE | <2m/s | [WMO-No. 1145] | |
| R2良好标准 | >0.5 | [Pangu-Weather, 2023] | |
| 质量等级 | good/fair/poor | [CF Conventions] | good: RMSE<阈值×0.5, fair: RMSE<阈值, poor: RMSE≥阈值 |

## 边界与分流
- 当验收门限未确认时：所有交付项标记BLOCKED，不得自行判定PASS
- 当R2<0时：自动REJECT，无需等待其他指标
- 当Skill Score<0时：模型性能低于基线，建议回退
- 当质量标志分布不合理时（如poor_pct>50%）：检查预报质量，可能需要重新建模

## 质量检查
- 验收门限必须经场景确认并记录
- 性能报告必须包含R2、Skill Score、RMSE、MAE
- 质量标志必须使用气象标准编码
- 产品元数据必须包含坐标系统、时间基准、单位信息
- R2<0时必须自动标记REJECT

## 回退策略
- 门限缺失时：提出建议门限并等待确认，不自行判定
- 性能不达标时：诊断原因，调整模型或特征工程
- 质量标志不合理时：检查质量标志编码逻辑

## 资源召回建议
- 当任务涉及气象预报验收和质量标志时召回本卡片
- 配套资源：climate-forecast-model-verification（模型验证）、climate-forecast-independent-validation（独立验证）

## 补充证据
[D1] WMO Guidelines on Verification of Numerical Weather Prediction, WMO-No. 1145, WMO（accessed_at 2026-09-18，交叉验证）

## 证据来源
[1] Accurate medium-range global weather forecasting with 3D neural networks, Bi et al., Nature, 2023, DOI: 10.1038/s41586-023-06185-3
[2] Statistical and Machine Learning forecasting methods: Concerns and ways forward, Makridakis et al., PLoS ONE, 2018, DOI: 10.1371/journal.pone.0194889
[3] The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2), Gelaro et al., Journal of Climate, 2017, DOI: 10.1175/jcli-d-16-0758.1