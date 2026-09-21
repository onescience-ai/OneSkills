# DNABERT-2 DNA Language Model

## 适用范围
用于DNA序列分析、调控元件识别、变异效应预测等基因组学任务。

## 输入
- DNA序列（支持最长131072上下文长度）
- 参考基因组版本：hg38

## 输出
- 序列表示嵌入
- 任务特定预测结果

## 流程节点
1. 模型下载：从HuggingFace（https://huggingface.co/label-lab/DNABERT-2）获取模型权重
2. 环境配置：配置GPU环境（需要16GB+ GPU内存）
3. 模型加载：加载dnabert2.bin权重文件（约3GB）
4. 序列编码：使用BPE tokenizer进行序列编码
5. 推理执行：进行序列分类、回归等任务

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 上下文长度 | 131072 | [1] | 支持的最长序列长度 |
| 模型大小 | 约3GB | [1] | 权重文件大小 |
| GPU内存要求 | 16GB+ | [1] | 推理所需最小GPU内存 |
| Tokenizer | BPE | [1] | 字节对编码分词器 |

## 边界与分流
- 如果GPU内存不足，可使用CPU推理，但速度较慢
- 如果模型权重下载失败，可尝试从官方GitHub获取

## 质量检查
- 检查模型文件是否存在、大小是否正确（约3GB）
- 验证是否可在GPU上成功加载
- 检查模型在基准任务上的性能

## 回退策略
- HuggingFace不可用时，可尝试从官方GitHub获取
- GPU内存不足时，可使用CPU推理或减少批次大小

## 资源召回建议
- 当需要进行DNA序列分析或基因组学任务时召回本卡片
- 配套资源：BEND_tasks数据集、分层性能评估方法

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] A comprehensive survey of genome language models in bioinformatics, Liu Shu, Jiao Tang, Xiaoyu Guan, Briefings in Bioinformatics, 2025, DOI: 10.1093/bib/bbaf724