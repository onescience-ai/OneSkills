# 抗体验证工作流

## 适用范围
适用于抗体生成、预测或设计任务的结果验证，确保生成结果的可靠性、准确性和可重复性。适用于AbODE、ABlooper、AlphaFold2等抗体建模工具的输出验证。不适用于蛋白质全局结构验证或非抗体类分子验证。

## 输入
- 待验证的抗体结构/序列（生成或预测结果）
- 参考结构（实验解析结构或已知高质量模型）
- 验证参数配置（阈值、统计方法等）

## 输出
- 验证报告（包含所有验证指标和统计结果）
- 质量评分（通过/不通过判定）
- 异常项识别和分析
- 可重复性说明（代码、数据、参数记录）

## 流程节点
1. **验证数据准备** → 选择验证数据集（SAbDab/Rosetta Antibody Benchmark）
2. **指标计算** → 计算CDR-RMSD、序列一致性、结构合法性等指标
3. **统计分析** → 计算均值、标准差、分布特征，进行显著性检验
4. **阈值判定** → 根据预设标准判断验证结果
5. **报告生成** → 生成包含详细过程和结果的验证报告
6. **可重复性归档** → 保存验证代码、数据和参数配置

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验证数据集 | Rosetta Antibody Benchmark (49结构) | [1] | 标准测试集 |
| 验证数据集 | SAbDab Latest Structures (114结构) | [1] | 新发布结构验证 |
| CDR-RMSD阈值 | <2.5 Å (良好), <3.5 Å (可接受) | [1] | 结构质量判定 |
| 置信度过滤 | inter-prediction RMSD <1.5 Å | [1] | 高置信度子集 |
| 统计方法 | 均值±标准差，分布分析 | [1] | 结果可靠性评估 |
| 分辨率要求 | 参考结构<3.0 Å | [1][2] | 数据质量保证 |

## 边界与分流
- 无实验参考结构：使用同源建模结构或SAbDab同源结构
- 小样本验证：需使用Bootstrap等重采样方法评估统计显著性
- 多构象CDR：需考虑构象多样性对验证结果的影响
- 跨方法比较：需确保使用相同验证数据集和评估标准

## 质量检查
- 验证过程完整性（所有步骤均有记录）
- 统计结果合理性（均值、标准差在预期范围）
- 可重复性验证（使用相同代码和数据可复现结果）
- 报告规范性（包含所有必要信息）

## 回退策略
- 验证数据集不可用：使用替代数据集或自行构建验证集
- 统计方法受限：使用非参数检验或Bootstrap方法
- 验证失败：分析失败原因，调整模型参数后重新验证

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 抗体生成/预测结果验证
- 不同建模方法性能比较
- 生成抗体质量筛选
- 研究结果可重复性验证

配套资源：
- abode-model-deployment：生成结果需验证
- cdr-rmsd-calculation：提供验证指标计算方法
- sabdab-antibody-structure：提供验证参考数据

## 证据来源
[1] Abanades B, Georges G, Bujotzek A, et al. ABlooper: fast accurate antibody CDR loop structure prediction with accuracy estimation. Bioinformatics, 2022. DOI: 10.1093/bioinformatics/btac016
[2] Schneider C, Raybould MIJ, Deane CM. SAbDab in the age of biotherapeutics: updates including SAbDab-nano, the nanobody structure tracker. Nucleic Acids Research, 2021. DOI: 10.1093/nar/gkab1050
