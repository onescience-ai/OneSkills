# 抗体设计工作流中的工具集成、模型部署与验证方法

## 适用范围
本卡片服务于抗体设计工作流中需要集成多种工具和验证标准的任务，包括但不限于：抗体序列生成、CDR环设计、抗体骨架优化、抗体-抗原复合物建模等。适用于需要从真实数据获取、模型部署到结果验证的全流程可复现场景。

## 输入
- 抗原结构数据（PDB格式）
- 抗体序列数据（FASTA格式）
- 目标表位信息（可选）
- 计算环境（Python、PyTorch、CUDA等）

## 输出
- 编号后的抗体序列（IMGT或其他编号方案）
- 生成的抗体结构（PDB格式）
- 验证报告（包含CDR-RMSD、TM-score等指标）
- 可复现的完整工作流记录

## 流程节点
1. **数据获取与预处理** → 从SAbDab或PDB数据库获取真实抗体-抗原复合物数据
2. **抗体序列编号** → 使用ANARCI或ANARCII对输入序列进行标准化编号
3. **模型部署与推理** → 加载预训练模型（如AbODE）进行抗体生成
4. **结构验证与评估** → 计算CDR-RMSD、TM-score等指标评估生成质量
5. **结果分析与报告** → 生成完整的验证报告和可复现记录

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 编号方案 | IMGT | [论文1] | 最广泛使用的抗体编号方案，提供一致的CDR边界定义 |
| RMSD阈值（严格） | ≤2Å | [论文3,4] | 用于评估生成结构与参考结构的高精度匹配 |
| RMSD阈值（宽松） | ≤5Å | [论文4] | 考虑AlphaFold3预测误差的实用阈值 |
| 表位召回率 | >0.9 | [论文4] | 评估生成抗体对目标表位的覆盖程度 |
| 框架偏差 | <0.3Å | [论文4] | 评估生成过程中抗体框架的保持程度 |
| 空间冲突数 | <10 | [论文4] | 评估生成结构的物理合理性 |

### 校准数值（体系专属值）
以下数值来自SAbDab数据库中的抗体-抗原复合物，供量级校准；其他体系需以自身证据重新锚定：
- 平均结构分辨率：2.4Å（X射线晶体学）、3.7Å（冷冻电镜）[论文2]
- 抗体-抗原接触距离：Cα距离<7.5Å [论文2]
- VH-VL配对距离：Cys92(VH)与Cys88(VL)的Cα距离≤22Å [论文2]

## 边界与分流
- **当缺少真实抗体数据时**：转向使用模拟数据或公开数据集，但需在报告中明确标注数据来源和局限性。
- **当模型权重不可用时**：转向使用其他预训练模型或从头训练，但需验证模型性能。
- **当验证标准不适用时**：根据具体任务调整验证指标，但需记录调整原因和依据。
- **当工具安装失败时**：检查环境依赖，尝试使用替代工具（如ANARCII替代ANARCI）。

## 质量检查
- 验证编号结果：检查ANARCI/ANARCII输出是否正确识别保守残基（Cys23、Cys104、Trp41）
- 验证结构质量：检查生成结构的RMSD、TM-score、空间冲突数
- 验证表位特异性：检查生成抗体是否覆盖目标表位的关键热点残基
- 验证可复现性：确保完整工作流记录包含所有参数、代码和数据版本

## 回退策略
- 当主要工具不可用时，使用替代工具（如ANARCII替代ANARCI）
- 当验证指标不达标时，调整生成参数重新运行
- 当数据不足时，使用数据增强或迁移学习方法
- 当计算资源不足时，使用云计算或优化模型架构

## 资源召回建议
- 当需要抗体编号时，召回本卡片获取ANARCI/ANARCII使用方法
- 当需要抗体结构数据时，召回本卡片获取SAbDab数据库访问方法
- 当需要验证生成质量时，召回本卡片获取CDR-RMSD计算标准
- 当需要完整工作流设计时，召回本卡片获取工具集成方案

## 补充证据（开源文档/用户自有，可选）
[D1] ANARCII官方文档, GitHub仓库, https://github.com/oxpig/ANARCII (accessed_at: 2026-09-17)
[D2] SAbDab数据库, https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab (accessed_at: 2026-09-17)

## 证据来源
[1] Greenshields-Watson A, Agarwal P, Robinson SA, et al. ANARCII enables alignment-free antigen receptor numbering using a generalised language model. Commun Biol. 2026;9:1085. DOI: 10.1038/s42003-026-10186-z
[2] Almeida DS, Almeida MV, Sampaio JV, et al. AbSet: A Standardized Data Set of Antibody Structures for Machine Learning Applications. J Chem Inf Model. 2025. DOI: 10.1021/acs.jcim.5c00410
[3] Wei S, Zhang J, Chen Y, et al. GeoGAD: geometry-aware antibody design framework for complementarity-determining region precision engineering. Bioinformatics. 2026. DOI: 10.1093/bioinformatics/btag042
[4] Kim Y, Baek M. De novo epitope-specific antibody design via time-dependent guidance. Bioinformatics. 2026. DOI: 10.1093/bioinformatics/btag455
[5] Capel HL, Vavourakis O, Williams BH. SAbDab2: The structural antibody database in the age of machine learning. 2026. DOI: 10.64898/2026.06.16.732554