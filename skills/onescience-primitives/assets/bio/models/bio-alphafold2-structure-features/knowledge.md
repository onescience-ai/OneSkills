# AlphaFold2结构特征

## 适用范围
- **触发条件**：需要从AlphaFold2预测结构中提取特征用于下游任务
- **适用场景**：多模态蛋白功能预测、结构-功能关联分析
- **不适用场景**：蛋白质结构预测本身、无结构数据场景

## 输入
- AlphaFold2预测结构文件（PDB/cif格式）
- 或UniProtKB中的AlphaFold预测链接

## 输出
- pLDDT置信度分数（0-100，per-residue）
- 结构特征向量（用于下游分类）

## pLDDT分数说明

| pLDDT范围 | 置信度 | 结构特征 |
|-----------|--------|----------|
| >90 | 高置信度 | 高度有序结构域 |
| 70-90 | 置信度较高 | 较有序结构 |
| 50-70 | 置信度较低 | 无序或柔性区域 |
| <50 | 置信度极低 | 可能为内在无序区 |

## 数据获取方式

### AlphaFold DB
- 网址：https://alphafold.ebi.ac.uk/
- 格式：PDB、cif、pLDDT文件
- 覆盖：UniProtKB中98.5%的人类蛋白

### UniProtKB集成
```python
import requests
uniprot_id = "P12345"
url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
response = requests.get(url)
alphafold_id = response.json()["uniProtKBCrossReferences"]  # AlphaFold链接
```

## 特征提取方法

### 方法1：pLDDT分数直接使用
```python
# 从PDB文件提取pLDDT
# B-factor列存储pLDDT分数
import Bio.PDB
parser = Bio.PDB.PDBParser()
structure = parser.get_structure("protein", "alphafold.pdb")
for residue in structure.get_residues():
    plddt = residue["CA"].get_bfactor()  # pLDDT值
```

### 方法2：全局统计特征
```python
# 全局pLDDT统计
plddt_mean = np.mean(plddt_scores)
plddt_std = np.std(plddt_scores)
plddt_frac_ordered = np.mean(plddt_scores > 70)  # 有序区域比例
```

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| pLDDT_threshold | 70 | [Jumper et al. 2021] | 结构置信度阈值 |
| feature_dim | 1-3 | [经验] | 特征向量维度 |
| data_source | AlphaFold DB | [AlphaFold] | 数据来源 |

## 边界与分流
- 无AlphaFold结构：仅使用序列表征
- pLDDT全<50：标记为无序蛋白，降低结构特征权重
- 结构文件损坏：从UniProtKB重新获取

## 质量检查
- pLDDT分数在0-100范围
- 特征维度匹配融合层输入
- 无NaN/Inf值

## 证据来源
[1] Jumper et al., "Highly accurate protein structure prediction with AlphaFold", Nature, 2021, DOI: 10.1038/s41586-021-03819-2
[2] Zhao et al., "PANDA-3D: protein function prediction based on AlphaFold models", NAR Genomics and Bioinformatics, 2024, DOI: 10.1093/nargab/lqae094