# 平均精度(AUPRC)定义与评估格式

## 适用范围

**触发条件**：
- 需要评估DNA语言模型在基因组功能预测任务上的性能
- 需要计算平均精度(AUPRC)而非多指标简单平均
- 需要导出区间层/碱基层/变异层结果

**适用场景**：
- 增强子/启动子活性预测
- 变异效应预测和优先级排序
- 基因组功能元件注释
- 模型性能对比和基准测试

**不适用场景**：
- 回归任务的评估（应使用MSE/MAE等指标）
- 无需区分参考/替代等位基因的简单分类
- 非基因组序列的功能预测

## 输入
- 预测分数：模型输出的概率或分数
- 真实标签：实验验证的功能标签
- 基因组坐标：区间/碱基/变异位置
- 等位基因信息：参考/替代等位基因

## 输出
- AUPRC分数：PR曲线下面积
- 分层性能报告：按区间/碱基/变异分层
- 结果文件：VCF/BED/tabular格式
- 可视化：PR曲线图

## 流程节点
1. 指标定义 → 2. 分层计算 → 3. 结果导出 → 4. 可视化

### 步骤1：指标定义
- **操作**：明确定义AUPRC的计算方式
- **参数**：metric_type, averaging_method
- **工具**：sklearn.metrics.average_precision_score
- **质量门禁**：使用PR曲线面积而非多指标平均

### 步骤2：分层计算
- **操作**：按区间/碱基/变异分层计算性能
- **参数**：stratification_level, reference_alternative
- **工具**：pandas分组计算
- **质量门禁**：分层完整，参考/替代等位基因可区分

### 步骤3：结果导出
- **操作**：将结果导出为标准格式
- **参数**：output_format, coordinate_system
- **工具**：pandas, pyvcf
- **质量门禁**：格式正确，坐标有效

### 步骤4：可视化
- **操作**：生成PR曲线和性能对比图
- **参数**：visualization_type, comparison_baselines
- **工具**：matplotlib, seaborn
- **质量门禁**：图表清晰，信息完整

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 平均精度定义 | PR曲线下面积(AUPRC) | [1] | 标准定义 |
| 计算函数 | sklearn.metrics.average_precision_score | [1] | 官方实现 |
| 分层方式 | 区间/碱基/变异 | [1] | 多粒度评估 |
| 等位基因区分 | 参考/替代 | [1] | 必须区分 |

### 校准数值
以下数值来自BEND基准测试，供量级校准；其他任务需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| BEND任务数 | 8个 | [1] | 基准测试任务 |
| 最佳模型AUPRC | ~0.7-0.9 | [1] | 高性能模型范围 |
| 随机基线AUPRC | ~0.5 | [1] | 随机分类器性能 |
| 输出格式 | VCF/BED/tabular | [1] | 标准基因组格式 |

## 边界与分流

**关键前提不成立时的改道方案**：
- **前提1：类别极度不平衡**
  - 改道方案：使用加权AUPRC或分层采样
- **前提2：数据量不足**
  - 改道方案：使用交叉验证或bootstrap重采样
- **前提3：坐标系统不一致**
  - 改道方案：统一坐标系统后再评估

## 质量检查
- **验证点**：AUPRC计算正确、分层完整、格式规范、可视化清晰
- **阈值**：AUPRC值在合理范围内（0-1），格式解析成功率100%
- **失败处理**：重新检查标签定义或调整评估参数

## 回退策略
- AUPRC计算错误时：检查标签定义和预测分数格式
- 分层不完整时：补充缺失的分层统计
- 格式错误时：使用标准格式转换工具

## 资源召回建议
- 当需要评估DNA语言模型性能时召回本卡片
- 配套资源：Caduceus模型、BEND基准测试数据集、基因组数据获取

## 证据来源
[1] Frederikke Isa Marin, Felix Teufel, Marc Horlacher, et al. BEND: Benchmarking DNA Language Models on biologically meaningful tasks. ICLR 2024. arXiv:2311.12570.
[2] Yair Schiff, Chia-Hsiang Kao, Aaron Gokaslan, Tri Dao, Albert Gu, Volodymyr Kuleshov. Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling. ICML 2024. arXiv:2403.03234.
