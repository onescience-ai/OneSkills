# 无铅杂化钙钛矿稳定性数据来源

## 适用范围
适用于无铅杂化钙钛矿材料稳定性机器学习筛选任务，需要获取真实实验或计算数据而非模拟数据的场景。

## 输入
- 查询参数：材料组成、晶体结构、稳定性指标
- 数据需求：结构、稳定性、性能数据

## 输出
- 数据格式：JSON、CSV或数据库查询结果
- 数据内容：材料组成、晶体结构、形成能、分解能、带隙等
- 验证标准：数据来源可追溯、数据质量报告

## 流程节点
1. 选择数据源 → 2. 配置API访问 → 3. 下载数据 → 4. 数据清洗 → 5. 格式转换

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Materials Project API | https://materialsproject.org/api | [1] | 通过API访问材料性质数据 |
| OQMD数据库 | https://oqmd.org | [2] | 开放量子材料数据库，包含稳定性数据 |
| 数据格式 | JSON/CSV | [1] | 标准数据交换格式 |
| 数据规模 | 10万+材料 | [1] | Materials Project包含大量材料数据 |

## 边界与分流
- 如果目标材料在Materials Project中不存在，尝试OQMD或其他数据库
- 如果API访问受限，使用批量下载或镜像站点
- 如果数据不完整，使用数据增强或插值方法

## 质量检查
- 检查数据来源的可追溯性
- 验证数据完整性和一致性
- 确认数据格式符合下游任务要求

## 回退策略
- 如果主要数据库不可用，尝试替代数据库
- 如果API访问失败，使用本地缓存或预处理数据
- 如果数据质量不足，标注数据局限性

## 资源召回建议
- 当任务需要真实材料数据时召回本卡片
- 当任务涉及材料筛选、稳定性预测时召回本卡片
- 配套工具：pymatgen、matgl等材料基因组工具

## 证据来源
[1] Screening for sustainable and lead-free perovskite halide absorbers – A database collecting insight from electronic-structure calculations, Julian Gebhardt, Andrea Gassmann, Wei Wei, Materials & Design, 2023, DOI: 10.1016/j.matdes.2023.112324
[2] Machine learning stability and band gap of lead-free halide double perovskite materials for perovskite solar cells, Zongmei Guo, Bin Lin, Solar Energy, 2021, DOI: 10.1016/j.solener.2021.09.030