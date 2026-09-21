# ANARCI抗体编号工具

## 适用范围
适用于需要对抗体序列进行标准化编号的任务，包括CDR区域定义、序列比对、突变位点定位、结构注释等免疫信息学分析场景。不适用于蛋白质全局结构预测或非免疫球蛋白序列分析。

## 输入
- 抗体氨基酸序列（FASTA格式或单行序列）
- 重链（VH）和/或轻链（VL）序列
- 可选：指定编号方案（IMGT/AHoT/Kabat/Chothia）

## 输出
- 编号后的抗体序列（带位置编号）
- CDR区域标注（CDR1/CDR2/CDR3边界）
- 框架区（FR）和互补决定区（CDR）分段信息
- 基因型推断（V/D/J基因）

## 流程节点
1. **安装ANARCI** → `pip install anarci` 或conda安装
2. **序列准备** → 格式化输入序列（FASTA或列表）
3. **执行编号** → 调用ANARCI API或命令行
4. **解析输出** → 提取编号结果和CDR区域信息
5. **结果验证** → 检查编号一致性和CDR边界合理性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 安装命令 | `pip install anarci` | [1] | Python包安装 |
| 编号方案 | IMGT（推荐） | [1][2] | 国际标准化编号 |
| 输入格式 | FASTA/序列列表 | [1] | 支持批量处理 |
| 输出格式 | JSON/CSV | [1] | 结构化数据 |
| HMM模型 | 预训练germline模型 | [1] | 隐马尔可夫模型 |

## 边界与分流
- 非抗体序列：ANARCI会返回低置信度或失败，需先确认输入为免疫球蛋白可变区
- 截断序列：可能无法完整编号，需提供完整VH/VL序列
- 罕见序列：IMGT编号可能不准确，可尝试AHoT方案作为备选

## 质量检查
- 编号覆盖率检查（残基编号完整性）
- CDR区域长度验证（CDR-H3通常6-25残基）
- 与已知抗体结构比对验证编号一致性

## 回退策略
- ANARCI安装失败：使用AbRSA工具作为替代
- 编号结果异常：尝试不同编号方案（Kabat/Chothia）对比验证

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 抗体序列标准化编号
- CDR区域定义和提取
- 抗体结构预测前处理
- 免疫信息学序列分析

配套资源：
- abode-model-deployment：生成抗体后需编号验证
- cdr-rmsd-calculation：基于编号的结构验证
- sabdab-antibody-structure：提供编号参考标准

## 证据来源
[1] Raybould MIJ, Marks C, Lewis AP, et al. Thera-SAbDab: the Therapeutic Structural Antibody Database. Nucleic Acids Research, 2019. DOI: 10.1093/nar/gkz827
[2] Zhu Z, Ashrafian H, Mohammadian Tabrizi N. Antibody numbering schemes: advances, comparisons and tools for antibody engineering. Protein Engineering, Design and Selection, 2025. DOI: 10.1093/protein/gzaf005
[3] Li L, Chen S, Miao Z, et al. AbRSA: A robust tool for antibody numbering. Protein Science, 2019. DOI: 10.1002/pro.3633
