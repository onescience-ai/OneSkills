# 1D-3D Fusion Architectures for Molecular Generation

## 适用范围
- **触发条件**：当任务需要生成三维分子结构，同时利用一维SMILES序列的化学语法先验和三维空间信息时。
- **适用场景**：基于结构的药物设计（SBDD）、分子链接设计、构象生成、多目标分子优化。
- **不适用场景**：纯二维分子图生成、不涉及三维坐标的任务。

## 输入
- **1D表示**：SMILES字符串或SELFIES字符串，表示分子的线性语法。
- **3D表示**：原子坐标（x, y, z）和原子类型（元素符号）。
- **靶点条件**：蛋白口袋的三维结构（PDB格式）、口袋残基列表、参考配体构象。
- **性质条件**：目标QED、SA、对接分数等数值。

## 输出
- **生成的分子**：包含三维坐标的分子结构（SDF格式）和对应的SMILES。
- **评估指标**：有效性、新颖性、多样性、QED、SA、对接分数。
- **训练检查点**：模型权重文件（PyTorch checkpoint）。

## 流程节点
1. **数据预处理**：SMILES编码为token序列，三维构象通过RDKit AllChem.EmbedMolecule生成。
2. **模型编码**：1D语言模型（Transformer/LSTM）处理SMILES序列，3D扩散模型（EGNN/E3NN）处理原子坐标。
3. **融合机制**：通过交叉注意力（cross-attention）或潜在空间拼接（latent concatenation）融合1D和3D表示。
4. **扩散过程**：前向扩散添加噪声，反向去噪网络（EGNN）逐步恢复分子结构。
5. **条件注入**：靶点口袋特征通过条件向量（condition vector）注入到扩散过程中。
6. **采样推理**：从高斯噪声开始，通过反向扩散生成多样化分子。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 噪声调度 β_t | 余弦调度或线性调度 | [论文2] | 控制前向扩散的噪声强度 |
| EGNN层数 | 4-6层 | [论文2] | 等变图神经网络的深度 |
| 隐藏维度 | 128-256 | [论文2] | 节点特征维度 |
| 交叉注意力头数 | 8 | [论文1] | 融合1D和3D表示的注意力机制 |
| 温度参数 τ | 0.8-1.2 | [论文3] | 控制采样多样性的缩放因子 |

## 边界与分流
- **手性处理**：标准E(3)等变模型对手性不敏感，需要额外模块（如GCDM）处理手性中心。
- **原子价态验证**：生成后需用RDKit Chem.SanitizeMol()验证化学价合法性。
- **构象稳定性**：使用力场优化（如MMFF94）确保三维构象合理。

## 质量检查
- **有效性**：生成的SMILES能被RDKit解析为有效分子。
- **三维合理性**：原子间距离在范德华半径之和的0.5-2.0倍之间。
- **多样性**：Tanimoto相似度阈值<0.5的分子比例。
- **药物相似性**：QED > 0.5，SA < 6。

## 回退策略
- **融合失败**：若1D-3D融合模型不收敛，回退到纯3D扩散模型（如EDM）。
- **数据不足**：使用ZINC-250K或ChEMBL预训练，再微调。
- **计算资源不足**：使用潜在扩散（latent diffusion）降低计算复杂度。

## 资源召回建议
- **何时召回**：当任务涉及三维分子生成、基于结构的药物设计、多目标优化时。
- **配套资源**：
  - `matchem-3d-diffusion-models`：三维扩散模型实现细节。
  - `matchem-smiles-transformer-language-model`：SMILES序列建模。
  - `matchem-molecular-generation-data-evaluation`：数据标准和评估指标。

## 证据来源
[1] Zeng et al., "Deep generative molecular design reshapes drug discovery", Cell Reports Medicine, 2022, DOI: 10.1016/j.xcrm.2022.100794
[2] Alakhdar et al., "Diffusion Models in De Novo Drug Design", Journal of Chemical Information and Modeling, 2024, DOI: 10.1021/acs.jcim.4c01107
[3] Anstine & Isayev, "Generative Models as an Emerging Paradigm in the Chemical Sciences", Journal of the American Chemical Society, 2023, DOI: 10.1021/jacs.2c13467