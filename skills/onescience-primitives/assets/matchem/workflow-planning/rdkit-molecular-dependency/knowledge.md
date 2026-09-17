# RDKit 分子生成依赖管理

## 适用范围
- 触发条件：执行任何涉及分子化学计算的任务时
- 适用场景：分子生成、分子验证、SMILES解析、3D构象生成、QED/SA评分计算
- 不适用场景：纯蛋白质结构分析（不涉及小分子）

## 输入
- Python环境（推荐3.8-3.11）
- 网络连接（在线安装）或预下载的wheel包（离线安装）

## 输出
- 可导入的RDKit模块
- 分子化学合法性验证结果

## 流程节点

### 1. 在线安装（推荐）
- 操作：使用pip安装rdkit-pypi
- 命令：`pip install rdkit-pypi`
- 质量门禁：`python -c "from rdkit import Chem; print('rdkit available')"`

### 2. Conda安装（备选）
- 操作：使用conda-forge频道安装
- 命令：`conda install -c conda-forge rdkit`
- 优势：依赖管理更完整，适合复杂科研环境

### 3. 离线安装
- 操作：下载预编译wheel包，本地安装
- 来源：PyPI镜像或 Christoph Gohlke 的非官方wheel
- 命令：`pip install --no-index --find-links=/path/to/wheels rdkit-pypi`
- 质量门禁：同在线安装验证

### 4. 功能验证
- 操作：测试核心功能
- 命令：
```python
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
mol = Chem.MolFromSmiles('CCO')
mol = Chem.AddHs(mol)
AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
print(f"QED: {Descriptors.qed(mol):.3f}")
```
- 质量门禁：成功解析SMILES、生成3D构象、计算QED

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 推荐版本 | 2023.03+ | [通用知识] | 支持最新分子描述符 |
| Python兼容性 | 3.8-3.11 | [RDKit文档] | 3.12+可能存在兼容性问题 |
| 核心功能 | Chem, AllChem, Descriptors | [论文1] | 分子生成任务必需 |
| QED计算 | Descriptors.qed() | [论文1] | 药物相似性评分 |
| SA计算 | rdMolDescriptors.CalcSAChepip() | [论文1] | 合成可及性评分 |

## 边界与分流
- **版本冲突**：RDKit与其他化学计算包（如OpenBabel）可能存在版本冲突
- **平台差异**：Windows安装可能需要Visual C++ Redistributable
- **功能限制**：RDKit开源版不包含所有商业功能

## 质量检查
- 验证模块导入：`from rdkit import Chem`
- 验证SMILES解析：`Chem.MolFromSmiles('CCO')` 返回非None对象
- 验证3D生成：`AllChem.EmbedMolecule()` 无异常
- 验证评分计算：QED、SA值在合理范围内

## 回退策略
- 如pip安装失败：尝试conda安装
- 如网络受限：使用离线wheel包
- 如版本不兼容：指定版本号安装（如`rdkit-pypi==2023.3.1`）

## 资源召回建议
- 何时召回：执行分子生成、分子验证、评分计算相关任务时
- 配套资源：bokdiff-model-weights-setup、protein-pocket-pdb-format

## 证据来源
[1] Khodabandeh Yalabadi A, Yazdani-Jahromi M, Garibay OO. BoKDiff: best-of-K diffusion alignment for target-specific 3D molecule generation. Bioinformatics Advances. 2025;5(1):vbaf137. DOI: 10.1093/bioadv/vbaf137
[2] Bran AM, Cox S, Schilter O, et al. Augmenting large language models with chemistry tools. Nature. 2024;630:164-171. DOI: 10.1038/s42256-024-00832-8
