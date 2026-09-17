# 调控DNA序列设计任务输入数据契约

## 适用范围
适用于需要生成满足目标活性的调控DNA序列的生物信息学任务，特别是单纯形流匹配（Simplex Flow Matching）模型在离散单纯形上生成增强子或启动子序列的场景。

## 输入数据格式
### enhancer_activity.csv 字段规范
| 字段名 | 类型 | 描述 | 必填 | 示例 |
|--------|------|------|------|------|
| chr | string | 染色体名称 | 是 | "chr1", "chrX" |
| start | integer | 起始位置（0-based或1-based） | 是 | 1000000 |
| end | integer | 结束位置 | 是 | 1000500 |
| strand | string | 链方向 | 否 | "+", "-", "." |
| allele | string | 等位基因序列 | 是 | "ATCGATCG" |
| activity | float | 活性标签（归一化信号值） | 是 | 0.85 |
| cell_type | string | 细胞类型 | 是 | "K562", "HepG2" |
| experiment_id | string | 实验标识 | 否 | "ENCSR000AAA" |
| signal_value | float | 原始信号值 | 否 | 125.5 |
| p_value | float | 统计显著性 | 否 | 0.001 |

### 数据格式要求
- 文件格式：CSV（逗号分隔值）或 TSV（制表符分隔值）
- 编码：UTF-8
- 表头：第一行为字段名
- 缺失值：使用空字符串或NA表示

## 数据来源与获取
### 主要公开数据库
1. **ENCODE Project**
   - 网址：https://www.encodeproject.org/
   - 数据类型：ChIP-seq、DNase-seq、ATAC-seq、RNA-seq
   - 下载方式：REST API 或 FTP 下载
   - 示例端点：`https://www.encodeproject.org/experiments/{experiment_id}/`

2. **Roadmap Epigenomics**
   - 网址：http://egg2.wust.edu/roadmap/
   - 数据类型：111种参考表观基因组
   - 下载方式：FTP 下载
   - 数据格式：bedGraph、bigWig、h5

3. **其他来源**
   - GEO (Gene Expression Omnibus)
   - UCSC Genome Browser
   - FANTOM5 增强子数据库

### 数据获取流程
1. 确定目标细胞类型和实验条件
2. 从数据库下载原始数据（BED、bigWig、H5AD格式）
3. 使用工具（如bedtools、pybedtools）提取目标区域
4. 标准化信号值（RPKM、TPM或Z-score）
5. 转换为CSV格式并添加等位基因信息

## 输出数据契约
### 标准化输出格式
```csv
chr,start,end,strand,allele,activity,cell_type
chr1,1000000,1000500,+,ATCGATCG,0.85,K562
chr2,2000000,2000500,-,GCTAGCT,0.72,HepG2
```

### 数据验证标准
1. 坐标有效性：start < end，坐标在染色体长度范围内
2. 等位基因有效性：仅包含ATCG字符
3. 活性值范围：[0, 1] 或标准化后的合理范围
4. 细胞类型一致性：与实验条件匹配

## 流程节点
1. **数据发现** → 2. **数据下载** → 3. **数据预处理** → 4. **数据标准化** → 5. **格式转换** → 6. **质量验证**

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参考基因组 | GRCh38/hg38 | [ENCODE] | 人类基因组参考版本 |
| 信号标准化方法 | TPM/RPKM | [Roadmap] | 表达量标准化方法 |
| 活性阈值 | 0.5 | [设计规范] | 高活性区域筛选阈值 |
| 数据格式 | CSV/TSV | [通用] | 通用数据交换格式 |

## 边界与分流
### 异常处理
- 数据缺失：使用公开数据库补充或提示用户提供
- 格式错误：自动转换格式并验证
- 坐标错误：基于参考基因组校正

### 降级策略
- 无完整数据时：使用模拟数据或公开数据集子集
- 无等位基因信息时：使用参考序列作为默认等位基因

## 质量检查
1. 数据完整性检查：所有必填字段非空
2. 数据一致性检查：坐标与参考基因组一致
3. 数据有效性检查：活性值在合理范围内
4. 数据唯一性检查：无重复记录

## 回退策略
1. 无本地数据时：从ENCODE/Roadmap下载示例数据
2. 数据格式不匹配时：提供数据转换工具
3. 数据量不足时：使用公开基准数据集

## 资源召回建议
- 需要数据预处理工具时：召回 `bio-datapipes` 类资源
- 需要可视化验证时：召回 `bio-visualization` 类资源
- 需要工作流规划时：召回 `bio-workflow-planning` 类资源

## 证据来源
[1] ENCODE Project Consortium. (2012). An integrated encyclopedia of DNA elements in the human genome. Nature, 489(7414), 57-74. DOI: 10.1038/nature11247
[2] Roadmap Epigenomics Consortium. (2015). Integrative analysis of 111 reference human epigenomes. Nature, 518(7539), 317-330. DOI: 10.1038/nature14248