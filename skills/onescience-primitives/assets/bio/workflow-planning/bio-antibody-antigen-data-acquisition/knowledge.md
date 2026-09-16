# 抗体抗原结合位点预测的真实数据获取知识

## 适用范围
本知识适用于抗体抗原结合位点预测任务，特别是需要真实实验测定的抗体-抗原复合物数据时。不适用于合成数据或模拟数据的场景。

## 输入
- 任务需求：需要真实抗体-抗原复合物数据进行结合位点预测
- 数据来源：SAbDab数据库、PDB数据库、IEDB数据库等
- 数据格式：FASTA格式（序列）、PDB格式（结构）、JSON格式（注释）

## 输出
- 真实抗体-抗原复合物数据集
- 标准化的FASTA文件（包含重链/轻链序列）
- PDB结构文件（包含原子坐标）
- 结合位点标注信息

## 流程节点
1. **数据需求分析** → 确定所需数据类型、数量和质量标准
2. **数据库选择** → 选择合适的数据源（SAbDab、PDB、IEDB等）
3. **数据获取** → 从数据库下载或API获取数据
4. **数据解析** → 解析FASTA/PDB格式，提取序列和结构信息
5. **数据验证** → 验证数据完整性和准确性
6. **数据预处理** → 标准化序列格式、结构坐标

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据库类型 | SAbDab | [论文1] | 专门的抗体结构数据库 |
| 数据格式 | FASTA | [论文2] | 标准序列格式 |
| 结构格式 | PDB | [论文3] | 蛋白质结构数据库格式 |
| 序列长度 | 可变 | [论文4] | 抗体序列长度可变 |
| 注释信息 | CDR区域、表位位置 | [论文1] | 关键功能区域标注 |

## 边界与分流
- **数据不可用**：当SAbDab/PDB无法访问时，可尝试其他数据库或公开数据集
- **数据质量不足**：过滤低质量结构（分辨率>2.5Å）
- **格式不兼容**：使用转换工具进行格式转换
- **数据量过大**：采样或分批处理

## 质量检查
- 验证序列完整性（无未知残基）
- 检查结构完整性（无缺失原子）
- 确认结合位点标注准确性
- 检查数据来源可靠性

## 回退策略
1. 尝试备用数据库（如IEDB、ABDb）
2. 使用公开数据集（如OAS数据库）
3. 联系数据提供者获取数据
4. 使用合成数据作为临时替代（需注明）

## 资源召回建议
- 当任务需要真实抗体-抗原数据时召回本卡片
- 当需要了解数据获取方法时召回本卡片
- 当需要验证数据质量时召回本卡片
- 配套资源：bio-bioinformatics-resource-access、bio-protein-ligand-docking-workflow

## 证据来源
[1] Accurate structure prediction of biomolecular interactions with AlphaFold 3, Josh Abramson et al., Nature, 2024, DOI: 10.1038/s41586-024-07487-w
[2] The antigenic anatomy of SARS-CoV-2 receptor binding domain, Jiahui Chen et al., Cell, 2021, DOI: 10.1016/j.cell.2021.02.032
[3] Structures of Human Antibodies Bound to SARS-CoV-2 Spike Reveal Common Epitopes and Recurrent Features of Antibodies, Joshua Tan et al., Cell, 2020, DOI: 10.1016/j.cell.2020.06.025
[4] Fast, accurate antibody structure prediction from deep learning on massive set of natural antibodies, Jeffrey A. Ruffolo et al., Nature Communications, 2023, DOI: 10.1038/s41467-023-38063-x