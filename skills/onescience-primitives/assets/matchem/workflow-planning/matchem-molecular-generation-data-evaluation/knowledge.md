# Molecular Generation Data Standards and Evaluation Metrics

## 适用范围
- **触发条件**：当任务需要准备分子生成训练数据、评估生成分子质量时。
- **适用场景**：分子生成模型训练、多目标筛选、药物发现流水线。
- **不适用场景**：不涉及分子数据或评估的任务。

## 输入
- **分子数据库**：ZINC、ChEMBL、PubChem 的 SMILES 文件。
- **靶点数据**：蛋白口袋 PDB 文件、参考配体构象。
- **任务配置**：生成分子数量、性质阈值（QED、SA）。

## 输出
- **预处理数据集**：标准化 SMILES 列表、3D 构象文件（SDF）。
- **评估报告**：有效性、新颖性、多样性、QED、SA 分数。
- **筛选结果**：按性质阈值过滤后的分子列表。

## 流程节点
1. **数据检索**：通过 ZINC API 或 ChEMBL API 下载类药分子 SMILES。
2. **数据清洗**：去重、去盐、标准化（RDKit Chem.MolFromSmiles + Chem.MolToSmiles）。
3. **性质过滤**：Lipinski 五规则（MW<500, LogP<5, HBD<5, HBA<10）。
4. **构象生成**：使用 RDKit AllChem.EmbedMolecule 生成三维构象。
5. **评估计算**：
   - **有效性**：SMILES 能被 RDKit 解析。
   - **QED**：RDKit QED.qed() 计算药物相似性（0-1）。
   - **SA**：RDKit rdMolDescriptors.CalcNumRotatableBonds 或 SA_Score 计算合成可及性（1-10）。
6. **多目标筛选**：先过滤有效性 → QED > 0.6 → SA < 6 → 按综合评分排序。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ZINC-250K 规模 | 250,000 分子 | [论文1] | 标准训练集规模 |
| 最小有效训练集 | >10,000 分子 | [论文1] | 保证模型学习多样性 |
| QED 阈值 | >0.5（常用0.6） | [论文3] | 药物相似性 |
| SA 阈值 | <6（常用5） | [论文3] | 合成可及性 |
| Lipinski 规则 | MW<500, LogP<5, HBD<5, HBA<10 | [论文1] | 类药性过滤 |

## 边界与分流
- **数据不足**：若本地数据集<1000 分子，需从外部数据库补充。
- **构象生成失败**：RDKit 无法生成三维构象时，使用 ETkdg 方法或增加力场优化。
- **评估指标缺失**：若 QED/SA 计算失败，回退到 Lipinski 规则和分子量分布。

## 质量检查
- **数据规模**：训练集分子数 >5000，骨架多样性 >50 种。
- **性质分布**：QED 分布覆盖 0.3-0.8，SA 分布覆盖 2-8。
- **化学合理性**：所有 SMILES 通过 RDKit SanitizeMol() 检查。

## 回退策略
- **外部数据库不可用**：使用本地缓存的 ZINC 子集。
- **QED/SA 计算库缺失**：安装 RDKit 或使用在线 API。
- **多样性不足**：增加 Murcko 骨架多样性采样。

## 资源召回建议
- **何时召回**：当任务需要数据准备、评估生成分子质量、多目标筛选时。
- **配套资源**：
  - `matchem-3d-diffusion-models`：三维扩散模型。
  - `matchem-next-mol-1d-3d-fusion-architecture`：1D-3D 融合架构。
  - `matchem-conditional-diffusion-training-inference`：条件扩散训练与推理。

## 证据来源
[1] Zeng et al., "Deep generative molecular design reshapes drug discovery", Cell Reports Medicine, 2022, DOI: 10.1016/j.xcrm.2022.100794
[2] Anstine & Isayev, "Generative Models as an Emerging Paradigm in the Chemical Sciences", Journal of the American Chemical Society, 2023, DOI: 10.1021/jacs.2c13467
[3] Alakhdar et al., "Diffusion Models in De Novo Drug Design", Journal of Chemical Information and Modeling, 2024, DOI: 10.1021/acs.jcim.4c01107