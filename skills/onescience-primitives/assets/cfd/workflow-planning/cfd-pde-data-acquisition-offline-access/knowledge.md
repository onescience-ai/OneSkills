# PDE观测数据集获取与离线访问策略

## 适用范围
适用于PDE逆问题任务中需要获取训练数据的场景，特别是当网络连接受限或需要离线工作时。涵盖从公开数据集（如PDEBench、DeepXDE）下载数据、本地缓存管理以及备用下载渠道的策略。不适用于完全自定义的合成数据生成场景。

## 输入
- 任务需求：需要哪些PDE类型的观测数据（如Navier-Stokes、Diffusion等）
- 网络环境：是否可访问互联网，是否有限制
- 存储空间：本地可用磁盘空间

## 输出
- 数据集本地路径
- 数据集元数据（包含数据来源、生成参数、数据量等）
- 数据可用性评级（完整、部分、合成）
- 后续获取建议（如网络恢复后重新下载）

## 流程节点
1. 需求分析 → 确定所需PDE类型和数据格式
2. 数据源发现 → 检索PDEBench、DeepXDE等公开数据集
3. 本地缓存检查 → 检查本地是否已有缓存数据
4. 下载策略选择 → 根据网络状况选择在线下载或离线备用方案
5. 数据验证 → 验证下载数据的完整性和格式正确性
6. 元数据生成 → 记录数据来源、参数和状态

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PDEBench数据格式 | HDF5, NetCDF | [D1] | PDEBench主要提供HDF5格式数据 |
| DeepXDE数据格式 | NumPy数组 | [D2] | DeepXDE通常使用NumPy数组存储 |
| 推荐本地缓存目录 | ~/.cache/pdebench/ | [D1] | PDEBench推荐缓存位置 |
| 数据验证指标 | 文件大小、哈希校验 | 通用 | 确保数据完整性 |

## 边界与分流
- 网络完全不可用：使用本地合成数据生成，但需标注科学有效性限制
- 数据集不存在：联系数据维护者或使用替代数据集
- 存储空间不足：压缩数据或选择子集
- 数据格式不匹配：使用适配器转换格式

## 质量检查
- 检查数据文件是否完整（无损坏）
- 验证数据格式是否符合预期
- 检查数据维度是否匹配任务需求
- 确认数据值范围是否合理

## 回退策略
- 在线下载失败：使用本地合成数据生成
- 数据验证失败：尝试重新下载或使用备用数据源
- 缓存损坏：清理缓存并重新获取

## 资源召回建议
当任务涉及PDE逆问题且需要训练数据时召回本卡片。配套资源：onescience-data-standardizer（数据标准化）、onescience-trainer（模型训练）。

## 补充证据（开源文档）
[D1] PDEBench: An Extensible Benchmark for Scientific Machine Learning, PDEBench Project, 2023, URL: https://pdebench.org/（accessed_at 2026-09-17，官方文档）
[D2] DeepXDE: A Deep Learning Library for Solving Differential Equations, DeepXDE Project, 2023, URL: https://deepxde.readthedocs.io/（accessed_at 2026-09-17，官方文档）

## 证据来源
[1] PDEBench官方文档（D1）
[2] DeepXDE官方文档（D2）