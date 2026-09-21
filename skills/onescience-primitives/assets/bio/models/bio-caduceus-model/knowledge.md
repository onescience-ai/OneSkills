# Caduceus DNA Language Model

## 适用范围
用于DNA序列分析，特别是长距离非编码变异效应预测和反向互补等变性任务。

## 输入
- DNA序列（支持染色体长度序列）
- 参考基因组版本：hg38

## 输出
- 序列表示嵌入
- 变异效应预测分数

## 流程节点
1. 模型获取：从官方GitHub或HuggingFace获取模型权重
2. 环境配置：配置GPU环境
3. 模型加载：加载Caduceus模型权重
4. 序列编码：处理DNA序列
5. 推理执行：进行变异效应预测等任务

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 架构 | BiMamba | [1] | 双向Mamba架构 |
| 等变性 | 反向互补等变 | [1] | 支持DNA反向互补对称性 |
| 上下文长度 | 染色体长度 | [1] | 支持超长序列 |

## 边界与分流
- 如果模型权重获取失败，可尝试从官方GitHub获取
- 如果GPU内存不足，可使用CPU推理

## 质量检查
- 检查模型文件是否存在
- 验证模型是否可在GPU上成功加载
- 检查模型在长距离变异效应预测任务上的性能

## 回退策略
- 官方源不可用时，可尝试从替代源获取
- GPU内存不足时，可使用CPU推理或减少批次大小

## 资源召回建议
- 当需要进行长距离DNA序列分析或变异效应预测时召回本卡片
- 配套资源：BEND_tasks数据集、分层性能评估方法

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] A comprehensive survey of genome language models in bioinformatics, Liu Shu, Jiao Tang, Xiaoyu Guan, Briefings in Bioinformatics, 2025, DOI: 10.1093/bib/bbaf724