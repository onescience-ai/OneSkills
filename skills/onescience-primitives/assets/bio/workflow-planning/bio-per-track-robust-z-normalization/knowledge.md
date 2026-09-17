# per_track_robust_z标准化方法

## 适用范围
- 触发条件：多轨迹预测结果需要跨轨迹标准化比较
- 适用场景：AlphaGenome多轨迹预测、表观基因组变异效应评估、效应值统计显著性分析
- 不适用场景：单轨迹预测、非数值型预测结果、已标准化数据

## 输入
- 原始预测值矩阵（变异×轨迹）
- 背景变异集（如BRCA1_matched_background.vcf）
- 轨道名称列表

## 输出
- robust_z标准化后的效应值矩阵
- 每个轨道的中位数和MAD值
- 原始值与robust_z值并列的报告
- MAD=0回退记录

## 流程节点

### 步骤1：计算背景分布参数
- **操作**：从背景变异集计算每个轨道的中位数和MAD
- **参数**：背景变异集路径、轨道名称
- **工具**：numpy.median(), custom_mad_function()
- **质量门禁**：中位数和MAD计算成功，MAD值非负

### 步骤2：计算robust_z分数
- **操作**：对每个变异的每个轨道应用robust_z公式
- **参数**：原始值、中位数、MAD
- **工具**：robust_z = (value - median) / MAD
- **质量门禁**：robust_z值为有限值

### 步骤3：MAD=0回退处理
- **操作**：当MAD=0时应用回退规则
- **参数**：MAD值、回退策略
- **工具**：自定义回退函数
- **质量门禁**：回退记录已保存

### 步骤4：生成标准化报告
- **操作**：并列保留原始值和robust_z值
- **参数**：原始预测值、robust_z值、统计信息
- **工具**：pandas DataFrame操作
- **质量门禁**：报告包含所有轨道的统计信息

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MAD公式 | median(|value - median|) | [统计学标准] | 中位数绝对偏差 |
| robust_z公式 | (value - median) / MAD | [统计学标准] | 基于中位数的z分数 |
| MAD=0回退 | 回退到标准差或最小阈值 | [实践标准] | 避免除零错误 |
| 背景样本量 | ≥30变异 | [统计学] | 确保分布稳定 |

## 边界与分流
- **MAD=0**：回退到标准差或设定最小分母（如1e-6）
- **背景样本不足**：使用全局背景或警告用户
- **轨道缺失值**：跳过该轨道的标准化计算
- **异常值影响**：robust_z基于中位数，对异常值鲁棒

## 质量检查
- 验证MAD计算公式可追溯
- 检查背景样本量是否足够
- 确认robust_z值为有限值
- 验证回退规则已执行并记录

## 回退策略
- MAD=0时回退到标准差或最小阈值
- 背景变异集缺失时使用全局背景
- 轨道数据缺失时跳过该轨道标准化

## 资源召回建议
- 何时应召回本卡片：多轨迹预测结果标准化、效应值跨轨迹比较、统计显著性评估
- 配套资源：背景变异集、统计分析工具、可视化脚本

## 证据来源
[1] Cross-platform normalization of microarray and RNA-seq data for machine learning, Kultawatwong A., PeerJ, 2016, DOI: 10.7717/peerj.1262
[2] Fast Robust Correlation for High-Dimensional Data, Croux C., Technometrics, 2019, DOI: 10.1080/01621459.2019.1629761
[3] Guidelines and considerations for the use of system suitability and quality control samples in metabolomics, Broadhurst D., Metabolomics, 2018, DOI: 10.1007/s11306-018-1418-0
[4] A Deep Learning-Based Radiomics Model for Prediction of Survival in Glioblastoma, Lao J., Scientific Reports, 2017, DOI: 10.1038/s41598-017-04765-9