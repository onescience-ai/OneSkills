# SMILES基础模型驱动的ADMET性质预测工作流

## 适用范围

面向药物发现早期阶段的分子性质预测任务，适用于需要批量评估候选分子的吸收(Absorption)、分布(Distribution)、代谢(Metabolism)、排泄(Excretion)与毒性(Toxicity)性质的场景。本工作流基于SMILES表征的深度学习模型，支持多任务ADMET端点预测，可应用于虚拟筛选、先导化合物优化与药物设计决策。适用于输入为SMILES字符串或分子结构文件(SDF/MOL2)、需要批量预测与评估的场景；不适用于需要量子力学计算或分子动力学模拟的高精度性质预测场景。

## 输入

### 标准化SMILES列表
- **格式**: CSV文件，包含`smiles`列（SMILES字符串）和可选的`molecule_id`列
- **预处理要求**:
  - SMILES必须经过RDKit标准化处理（`Chem.MolFromSmiles` → `Chem.MolToSmiles`）
  - 去除重复分子（基于canonical SMILES）
  - 过滤无效SMILES（解析失败的分子）
- **数据源**（当本地文件缺失时的公开数据获取）:
  - MoleculeNet: https://moleculenet.org/
  - Therapeutics Data Commons (TDC): https://tdcommons.ai/
  - PubChem: https://pubchem.ncbi.nlm.nih.gov/
  - ChEMBL: https://www.ebi.ac.uk/chembl/

### 靶点条件（可选）
- **格式**: JSON或YAML文件，指定需要预测的ADMET端点
- **默认端点**: Caco-2 permeability, CYP3A4 inhibition, hERG toxicity, Ames mutagenicity, Hepatotoxicity

### 模型权重
- **格式**: PyTorch checkpoint (.pt/.pth) 或 HuggingFace模型
- **预训练模型示例**:
  - SMILES-Mamba: 基于Mamba架构的SMILES语言模型
  - ChemBERTa: 基于Transformer的化学语言模型
  - Uni-Mol: 统一分子表征模型

## 输出

### s04最终产物
1. **排序分子集**: 按预测分数排序的候选分子列表（CSV/SDF格式）
2. **AUROC明细**: 每个ADMET端点的AUROC值（JSON格式）
3. **性质多样性报告**: 预测性质分布统计与可视化

### 中间产物
- **s01输出**: 标准化SMILES列表 + 靶点条件向量
- **s02输出**: 加载的模型权重 + 编码的性质条件向量
- **s03输出**: 生成的候选分子SDF文件（默认1000个）

## 流程节点

### s01: 输入核验与数据准备
```
输入文件检查 → SMILES标准化 → 无效分子过滤 → 数据分割 → 输出标准化SMILES列表
```
- **操作**: 验证输入文件存在性，解析SMILES，调用RDKit标准化
- **参数**: `sanitize=True`, `remove_salts=True`, `disconnect_metals=True`
- **工具**: RDKit, pandas
- **质量门禁**: 有效SMILES比例 ≥ 95%；重复分子去除后数量 ≥ 原始数量的80%
- **Fallback策略**: 当本地输入文件缺失时，从公开数据源（MoleculeNet/TDC）下载示例数据

### s02: 模型权重加载与条件编码
```
模型架构实例化 → 权重加载 → 性质条件向量编码 → 模型验证
```
- **操作**: 加载预训练模型，编码目标ADMET端点条件
- **参数**: `device='cuda' if available else 'cpu'`, `batch_size=64`
- **工具**: PyTorch, HuggingFace Transformers
- **质量门禁**: 模型加载无错误；条件向量维度匹配；推理测试通过（单样本前向传播）

### s03: 候选分子生成
```
批量推理 → 分子解码 → SMILES有效性检查 → SDF格式转换 → 输出候选分子集
```
- **操作**: 使用模型批量生成候选分子
- **参数**: `num_generations=1000`, `temperature=0.8`, `top_k=50`, `top_p=0.95`
- **工具**: RDKit, PyTorch
- **质量门禁**: 生成成功率 ≥ 80%；SMILES有效性 ≥ 95%；去重后数量 ≥ 500

### s04: 性质评估与筛选
```
ADMET性质预测 → AUROC计算 → QED/SA评分 → 化学合法性校验 → 多性质筛选 → 排序输出
```
- **操作**: 对生成的分子进行多端点ADMET预测，计算AUROC，筛选优质候选
- **参数**: `qed_threshold=0.6`, `sa_threshold=6.0`, `auroc_threshold=0.7`
- **工具**: RDKit, scikit-learn, numpy
- **质量门禁**: 平均AUROC ≥ 0.7；QED≥0.6且SA≤6的分子比例 ≥ 30%

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SMILES标准化 | RDKit canonicalization | [论文1] | 确保相同分子产生相同SMILES |
| 模型推理batch_size | 32-128 | [论文3] | 根据GPU显存调整 |
| AUROC计算 | sklearn.metrics.roc_auc_score | [论文5] | 二分类任务标准指标 |
| 生成温度 | 0.5-1.0 | [论文3] | 控制生成多样性 |
| QED阈值 | ≥0.6 | [RDKit文档] | 药物样性筛选标准 |
| SA阈值 | ≤6.0 | [论文6] | 合成可及性筛选标准 |

### 校准数值（ADMET任务专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Caco-2 AUROC基准 | 0.75-0.85 | [论文7] | 肠道渗透性预测 |
| CYP3A4抑制AUROC | 0.80-0.90 | [论文7] | 代谢酶抑制预测 |
| hERG毒性AUROC | 0.70-0.80 | [论文7] | 心脏毒性预测 |
| Ames致突变AUROC | 0.75-0.85 | [论文7] | 基因毒性预测 |
| 平均AUROC目标 | ≥0.70 | [任务要求] | 整体预测性能阈值 |

## 边界与分流

### 异常处理
1. **输入文件缺失**: 自动从MoleculeNet/TDC下载示例数据集（需网络连接）
2. **模型权重不可用**: 使用HuggingFace预训练模型作为替代
3. **GPU显存不足**: 降低batch_size至16或8，启用梯度累积
4. **生成失败率过高**: 降低temperature，增加top_k过滤

### 降级策略
- 当完整工作流无法执行时，可跳过s03（分子生成），仅对输入分子进行s04（性质预测）
- 当AUROC计算失败时，改用精度(Precision)/召回率(Recall)/F1作为替代指标

### 分支条件
- 若输入为已知活性分子集 → 直接进入s04性质预测
- 若输入为随机分子集 → 需先执行s03生成候选分子
- 若需要分子优化 → 在s04后增加强化学习迭代环节

## 质量检查

### 验证点
1. **s01验证**: SMILES解析成功率、重复分子比例、数据集统计
2. **s02验证**: 模型加载完整性、推理速度、内存占用
3. **s03验证**: 生成分子SMILES有效性、多样性指标、去重率
4. **s04验证**: AUROC值范围、QED/SA分布、筛选后分子数量

### 阈值
- SMILES有效性: ≥95%
- 生成成功率: ≥80%
- 平均AUROC: ≥0.70
- QED≥0.6且SA≤6比例: ≥30%

### 失败处理
- 任何步骤失败时记录详细错误日志
- 可从失败步骤重新开始，无需重跑全流程
- 生成中间产物备份，支持断点续跑

## 回退策略

1. **数据回退**: 本地文件缺失 → 公开数据源下载 → 使用合成数据
2. **模型回退**: 自定义模型 → HuggingFace预训练 → 简基线模型（随机森林）
3. **计算回退**: GPU推理 → CPU推理 → 批量子采样
4. **指标回退**: AUROC → Precision-Recall AUC → F1-score

## 资源召回建议

当以下场景出现时应召回本卡片：
- 需要执行SMILES基础的ADMET性质预测任务
- 需要了解ADMET预测工作流的完整步骤
- 需要AUROC/QED/SA评分的具体计算方法
- 需要公开ADMET数据源的获取方式
- 需要SMILES-Mamba或类似模型的使用指南

配套资源建议：
- **模型**: SMILES-Mamba, ChemBERTa, Uni-Mol
- **数据集**: MoleculeNet, TDC, ADME datasets
- **工具**: RDKit, DeepChem, PyTorch Geometric

## 补充证据（开源文档）

[D1] RDKit QED Module Documentation, RDKit, version 2026.03.6, URL: https://www.rdkit.org/docs/source/rdkit.Chem.QED.html (accessed_at 2026-09-21, 交叉验证)
[D2] Therapeutics Data Commons Documentation, TDC, URL: https://tdcommons.ai/ (accessed_at 2026-09-21, 单源参考)

## 证据来源

[1] A compact review of molecular property prediction with graph neural networks, Vayer et al., Drug Discovery Today: Technologies, 2020, DOI: 10.1016/j.ddtec.2020.11.009
[2] Deep learning methods for molecular representation and property prediction, Vamathevan et al., Drug Discovery Today, 2022, DOI: 10.1016/j.drudis.2025.104487
[3] MultiGran-SMILES: multi-granularity SMILES learning for molecular property prediction, Wang et al., Bioinformatics, 2022, DOI: 10.1093/bioinformatics/btac550
[4] SimSon: simple contrastive learning of SMILES for molecular property prediction, 2025, DOI: 10.1093/bioinformatics/btaf275
[5] An End-User Audit of Reproducibility, Data Leakage, and Overfitting of the Top-Ranked ADMET Prediction, 2026, DOI: 10.1021/acs.jcim.6c00819
[6] Bridging data and drug development: Machine learning approaches for next-generation ADMET prediction, 2025, DOI: 10.1016/j.drudis.2025.104487
[7] DCPM-ADMET: fusion of dual-component pre-trained model and molecular fingerprints to enhance drug ADMET properties prediction, Zhang et al., J Cheminform, 2026, DOI: 10.1186/s13321-026-01244-z
[8] ADMET-XSpec: A Tool for Systematic Cross-Species Data Integration in ADMET Prediction, 2026, DOI: 10.1021/acs.chemrestox.5c00562
