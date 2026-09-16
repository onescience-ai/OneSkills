# 气象时序预报模型选择与验证

## 适用范围
适用于earth域时序预报任务（24-72h温湿风预报）的模型选择、配置验证和最小干运行。

## 输入
- 模型架构定义（LSTM/Transformer/GRU等）
- 训练数据（经时空对齐的气象数据）
- 模型配置参数

## 输出
- 方法工件与配置身份报告
- 输入输出兼容性矩阵
- 最小干运行日志
- 随机性控制记录

## 流程节点

### 1. 模型适用性评估
- 操作：根据数据特征选择模型架构
- 参数：序列长度、多变量交互程度、长期依赖需求
- 质量门禁：模型需适配气象时序预报任务

### 2. 输入输出契约验证
- 操作：检查输入特征维度与模型输入维度匹配性
- 参数：输入shape、输出shape、目标变量对应关系
- 质量门禁：维度不匹配 → BLOCKED

### 3. 最小干运行
- 操作：用小batch验证模型能正常前向传播
- 参数：batch_size=2、检查输出无NaN/Inf
- 质量门禁：干运行失败 → BLOCKED

### 4. 随机性控制
- 操作：设置全局随机种子、CUDA确定性
- 参数：torch.manual_seed、torch.cuda.manual_seed_all
- 质量门禁：种子未设置 → 警告

## 关键参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| LSTM适用序列长度 | >24h | [1] | 短期依赖建模 |
| Transformer适用场景 | 多变量交互 | [2] | 全局依赖捕捉 |
| GRU适用场景 | 轻量级快速训练 | [1] | 资源受限时 |
| 干运行batch_size | 2 | [1] | 最小验证 |
| 随机种子 | 42 | [1] | 可复现性 |

## 边界与分流
- 干运行输出NaN → 检查输入数据和模型初始化
- 维度不匹配 → 调整模型配置或数据预处理
- 模型不适用 → 更换架构

## 质量检查
- 验证干运行日志包含前向传播检查
- 确认输出无NaN/Inf
- 检查输入输出shape匹配

## 回退策略
- 干运行失败时：检查数据归一化、模型初始化
- 模型不适用时：尝试替代架构

## 资源召回建议
- 需召回：climate-forecast-data-validation-workflow（数据验证）
- 配套任务：climate-forecast-performance-evaluation

## 证据来源
[1] Bi K, Xie L, Zhang H, et al. Accurate medium-range global weather forecasting with 3D neural networks. Nature, 2023, 619: 533-538. DOI: 10.1038/s41586-023-06185-3
[2] Price I, Sanchez-Gonzalez A, Alet F, et al. Probabilistic weather forecasting with machine learning. Nature, 2025, 637: 84-90. DOI: 10.1038/s41586-024-08252-9
