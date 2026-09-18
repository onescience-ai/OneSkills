# ANARCI工具在抗体反向折叠中的应用

## 适用范围
适用于需要对抗体序列进行标准编号的场景，包括抗体反向折叠、CDR区域定义、界面特征构建等。ANARCI（Antibody Numbering And Receptor Classification）是常用的抗体编号工具，支持IMGT、Chothia、Kabat等多种编号方案。

## 输入
- 抗体序列：FASTA格式或PDB格式的抗体序列（重链和轻链）。
- 编号方案：指定使用的编号方案（如Chothia、Kabat、IMGT等）。

## 输出
- 编号后的序列：带标准编号的抗体序列。
- CDR区域标注：根据编号方案定义的CDR区域（如CDR-H1、CDR-H2、CDR-H3等）。
- 结构掩码：用于反向折叠模型的CDR掩码文件。

## 流程节点
1. **序列准备**：从PDB文件中提取抗体序列（重链和轻链）。
2. **ANARCI调用**：使用ANARCI工具对序列进行编号。
3. **CDR区域提取**：根据编号方案提取CDR区域坐标。
4. **掩码生成**：生成CDR区域的掩码文件，用于反向折叠模型的条件输入。
5. **集成到工作流**：在反向折叠模型加载权重前执行ANARCI编号。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 编号方案 | Chothia | [1] | 用于CDR区域定义，与AbNumber工具一致 |
| 输入格式 | PDB/FASTA | [1,2] | 支持PDB文件和FASTA序列文件 |
| 输出格式 | CSV/JSON | [2] | 包含编号、CDR区域、残基属性等 |
| CDR定义 | Chothia方案 | [1] | CDR-H1: 26-32, CDR-H2: 52-56, CDR-H3: 95-102 |
| 运行环境 | Python 3.x | [2] | 需要安装ANARCI包（pip install anarci） |

## 边界与分流
- **编号方案选择**：不同模型可能要求不同的编号方案（如AntiFold使用Chothia方案），需根据模型要求选择。
- **序列质量**：低质量或不完整的序列可能导致编号错误，需进行序列质量检查。
- **多链处理**：对于Fab抗体，需分别对重链和轻链进行编号。
- **工具替代**：若ANARCI不可用，可使用AbNumber或ABYSIS等替代工具。

## 质量检查
- **编号完整性**：检查所有残基是否都已编号，无遗漏。
- **CDR区域验证**：验证提取的CDR区域是否与已知结构一致。
- **掩码合理性**：检查生成的掩码是否覆盖了所有CDR残基。
- **与模型兼容性**：确认编号方案与反向折叠模型的要求一致。

## 回退策略
- **替代编号工具**：若ANARCI安装失败，可使用在线服务ABYSIS（https://www.hlimmab.org/abysis/）。
- **手动编号**：对于特殊抗体（如纳米抗体），可手动定义CDR区域。
- **跳过编号**：若任务不依赖精确编号，可跳过此步骤，但可能影响CDR特征构建。

## 资源召回建议
- 当任务涉及抗体反向折叠、CDR设计、抗体编号时，应召回本卡片。
- 配套资源：bio-antibody-inverse-folding-model-weights（模型权重获取）、bio-antibody-inverse-folding-workflow-dependencies（工作流依赖管理）。

## 证据来源
[1] Benchmarking inverse folding models for antibody CDR sequence design, Yifan Li et al., PLoS ONE, 2025, DOI: 10.1371/journal.pone.0324566
[2] AntiFold: improved structure-based antibody design using inverse folding, Magnus Haraldson Høie et al., Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae202