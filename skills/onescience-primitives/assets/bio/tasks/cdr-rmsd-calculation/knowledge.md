# CDR-RMSD计算与验证

## 适用范围
适用于评估抗体CDR环结构预测或生成质量的任务，包括模型输出验证、生成抗体质量评估、不同方法性能比较等场景。不适用于全局蛋白质RMSD计算或非CDR区域结构分析。

## 输入
- 预测/生成的抗体3D结构（PDB/mmCIF格式）
- 参考晶体结构（实验解析结构）
- CDR区域定义（基于ANARCI编号）

## 输出
- 每个CDR环的RMSD值（Å）
- 整体CDR-RMSD均值和标准差
- 阈值判定结果（通过/不通过）
- 异常CDR识别

## 流程节点
1. **结构准备** → 加载预测结构和参考结构，提取CDR区域原子坐标
2. **CDR区域定义** → 基于Chothia或IMGT编号确定CDR边界
3. **结构比对** → 对齐骨架区域，计算CDR区域原子坐标偏差
4. **RMSD计算** → 计算CDR主链原子（Cα-N-C-Cβ）的RMSD
5. **阈值判定** → 根据预设标准判断CDR质量
6. **报告生成** → 输出详细验证报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| RMSD计算原子 | Cα-N-C-Cβ主链原子 | [1] | 标准CDR评估原子集 |
| 优秀阈值 | <2.0 Å | [1] | 高置信度预测 |
| 良好阈值 | <2.5 Å | [1] | 可接受预测 |
| 一般阈值 | <3.5 Å | [1] | 需谨慎使用 |
| 高变阈值 | >3.5 Å | [1] | 低置信度/多构象 |
| 比对方法 | 骨架对齐后CDR计算 | [1] | 减少框架误差影响 |

## 边界与分流
- CDR-H3长环（>20残基）：RMSD阈值应放宽，结构多样性增加
- 多构象CDR：RMSD可能偏高，需结合置信度评估
- 缺少参考结构：可使用SAbDab中同源结构作为替代参考
- 序列一致性<95%：RMSD比较意义有限，需谨慎解释

## 质量检查
- RMSD值在合理范围内（CDR-H3通常<3.5 Å）
- 所有CDR环均完成计算，无遗漏
- 阈值判定与置信度评估一致

## 回退策略
- 无参考结构：使用同源建模结构或SAbDab数据库结构作为参考
- RMSD异常高：检查CDR编号是否正确，或考虑该CDR可能具有多构象特性

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 抗体结构预测/生成质量评估
- CDR环建模精度验证
- 不同抗体建模方法性能比较
- 生成抗体筛选和优化

配套资源：
- abode-model-deployment：生成抗体后需CDR-RMSD验证
- anarci-antibody-numbering：提供CDR区域定义
- sabdab-antibody-structure：提供参考结构数据

## 证据来源
[1] Abanades B, Georges G, Bujotzek A, et al. ABlooper: fast accurate antibody CDR loop structure prediction with accuracy estimation. Bioinformatics, 2022. DOI: 10.1093/bioinformatics/btac016
[2] Greenshields-Watson A, Abanades B, Deane CM. Investigating the ability of deep learning-based structure prediction to extrapolate and/or enrich the set of antibody CDR canonical forms. Frontiers in Immunology, 2024. DOI: 10.3389/fimmu.2024.1352703
