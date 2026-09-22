# 预报独立验证

## 适用范围
适用于气象预报模型的独立验证任务，确保验证数据集不参与训练、调参或阈值选择过程。

## 输入
- 独立验证数据集（明确来源、时间范围、空间范围）
- 预报产品文件
- 验证指标配置

## 输出
- 验证指标计算结果（POD、FAR、CSI、Bias等）
- 验证报告（含数据来源、指标解释、性能评估）

## 流程节点
1. **验证数据集准备** → 获取独立观测数据（地面站、卫星反演等）
2. **数据匹配** → 时间匹配、空间匹配、变量匹配
3. **指标计算** → 计算二分类/连续变量验证指标
4. **结果解释** → 评估预报性能、识别系统偏差
5. **报告生成** → 生成可追溯的验证报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| POD（检测概率） | >0.8为优秀 | [1] | 命中率指标 |
| FAR（虚报率） | <0.2为优秀 | [1] | 虚报率指标 |
| CSI（临界成功指数） | >0.6为优秀 | [1] | 综合评分指标 |

## 边界与分流
- 验证数据集来源不明确 → 拒绝执行验证
- 验证指标超出合理范围 → 检查数据匹配过程

## 质量检查
- 验证数据集必须有明确的来源文档
- 验证指标计算必须可复现
- 验证报告必须包含数据时间范围

## 回退策略
- 独立验证数据不可用时，记录阻塞原因并跳过验证步骤

## 资源召回建议
- 验证步骤阶段召回本卡片
- 配套召回：convective-gust-nowcasting-workflow

## 证据来源
[1] Abi, A Nowcasting System for Hydrometeorological Hazard Assessment – Part 2: On Verification and Validation Process, Anuário do Instituto de Geociências, 2024, DOI: 10.11137/1982-3908_2024_47_62979
[2] Dorninger et al., Editorial: Forecast verification methods across time and space scales, Meteorologische Zeitschrift, 2018, DOI: 10.1127/metz/2018/0955
