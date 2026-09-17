# 蛋白口袋PDB文件格式与获取

## 适用范围
- 触发条件：执行靶标特异性分子生成（SBDD）任务时
- 适用场景：需要准备真实蛋白口袋结构作为生成模型输入
- 不适用场景：蛋白质结构预测、蛋白质纯分析任务

## 输入
- 目标蛋白PDB ID（如1ABC）
- 或已知的蛋白结构文件（.pdb/.cif）
- 结合口袋残基列表（可选）

## 输出
- 符合SBDD要求的蛋白口袋PDB文件
- 包含完整原子坐标和残基信息

## 流程节点

### 1. 从PDB数据库下载
- 操作：使用RCSB PDB API或wget下载
- 命令：
```bash
# 下载完整蛋白结构
wget https://files.rcsb.org/download/1ABC.pdb
# 或使用API
curl -o 1ABC.pdb "https://files.rcsb.org/download/1ABC.pdb"
```
- 质量门禁：PDB文件包含ATOM记录和坐标信息

### 2. 结合口袋提取
- 操作：基于配体位置或已知位点提取口袋
- 工具：PyMOL、Chimera、CB-Dock2
- PyMOL命令：
```python
# 加载蛋白
load 1ABC.pdb
# 选择配体周围5Å内的残基
select pocket, ligand around 5
# 导出口袋
save pocket.pdb, pocket
```
- 质量门禁：提取的口袋包含合理的原子坐标范围

### 3. PDB格式验证
- 操作：检查PDB文件格式规范
- 关键字段：
  - ATOM记录：原子序号、原子名称、残基名称、链ID、残基序号、坐标(x,y,z)
  - HETATM记录：配体/水分子
  - END记录：文件结束
- 验证命令：
```python
from rdkit import Chem
mol = Chem.MolFromPDBFile('pocket.pdb')
assert mol is not None, "PDB解析失败"
```
- 质量门禁：所有原子坐标在合理范围内（无NaN或极端值）

### 4. 口袋预处理
- 操作：清理、加氢、能量最小化
- 步骤：
  1. 移除水分子和非必需配体
  2. 添加氢原子
  3. 能量最小化（可选）
- 工具：OpenBabel、RDKit
- 质量门禁：预处理后原子数合理，无立体冲突

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PDB格式版本 | 3.3 | [PDB标准] | 当前通用格式 |
| ATOM记录长度 | 80字符 | [PDB标准] | 固定宽度格式 |
| 坐标精度 | 3位小数 | [PDB标准] | 埃为单位 |
| 口袋半径 | 5-10Å | [论文1] | 围绕配体的搜索范围 |
| CrossDocked2020过滤 | RMSD<1Å | [论文1] | 对接姿态质量 |

## 边界与分流
- **PDB文件不存在**：检查PDB ID是否正确，或蛋白结构尚未解析
- **配体缺失**：HETATM记录中无配体，需手动定义口袋中心
- **多链蛋白**：明确指定目标链（如链A）
- **缺失原子**：使用Modeller或AlphaFold补全

## 质量检查
- 验证PDB文件可被RDKit/PyMOL正常解析
- 验证原子坐标范围合理（通常-1000到1000Å）
- 验证残基完整性（无缺失原子）
- 验证口袋几何（与配体距离合理）

## 回退策略
- 如PDB数据库无法访问：使用AlphaFold预测结构（AlphaFold DB）
- 如口袋提取失败：使用盲对接工具（如CB-Dock2）自动识别口袋
- 如格式不兼容：使用OpenBabel转换格式

## 资源召回建议
- 何时召回：执行SBDD任务、准备生成模型输入时
- 配套资源：bokdiff-model-weights-setup、rdkit-molecular-dependency

## 证据来源
[1] Khodabandeh Yalabadi A, Yazdani-Jahromi M, Garibay OO. BoKDiff: best-of-K diffusion alignment for target-specific 3D molecule generation. Bioinformatics Advances. 2025;5(1):vbaf137. DOI: 10.1093/bioadv/vbaf137
[2] Eberhardt J, Santos-Martins D, Tillack AF, Forli S. AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. J Chem Inf Model. 2021;61(8):3891-3898. DOI: 10.1021/acs.jcim.1c00203
[3] Liu Y, Grimm M, Dai WT, et al. CB-Dock2: improved protein-ligand blind docking by integrating cavity detection, docking and homologous template fitting. Nucleic Acids Res. 2022;50(W1):W159-W164. DOI: 10.1093/nar/gkac394
