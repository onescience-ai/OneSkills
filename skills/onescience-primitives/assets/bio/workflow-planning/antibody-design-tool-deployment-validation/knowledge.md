# 抗体设计工具部署与验证

## 适用范围

**触发条件**：
- 需要实际部署AbODE模型进行抗体序列结构联合生成
- 需要使用ANARCI对抗体序列进行标准化编号
- 需要从SAbDab数据库获取真实抗原-抗体复合物数据
- 需要执行CDR-RMSD验证评估生成抗体质量

**适用场景**：
- 从头抗体候选设计工作流中工具链部署
- 抗体编号与CDR区域标注
- 结构抗体数据库数据获取与预处理
- 生成抗体与参考结构的CDR-RMSD计算与验证

**不适用场景**：
- 非抗体类蛋白质设计任务
- 无需结构验证的纯序列预测任务
- 不涉及抗原-抗体复合物的蛋白质工程

## 输入

| 输入项 | 说明 |
|---|---|
| 抗体序列 | FASTA格式或单条氨基酸序列 |
| 抗原结构 | PDB/mmCIF格式结构文件 |
| 参考结构 | 用于CDR-RMSD计算的参考抗体结构 |
| 编号方案 | IMGT、Chothia、Kabat、Martin、AHo或Wolfguy |

**预处理要求**：
- 序列需为标准20种氨基酸字符
- PDB文件需包含完整的CDR区域原子坐标
- 参考结构与待评估结构需使用相同编号方案

## 输出

| 输出项 | 格式 | 说明 |
|---|---|---|
| ANARCI编号结果 | 文本/CSV | 标准化抗体编号、物种鉴定、链类型 |
| AbODE生成结果 | JSON/PDB | 生成的抗体序列和3D结构 |
| CDR-RMSD报告 | JSON | 每个CDR区域的RMSD值和统计信息 |
| 验证报告 | JSON | 完整的验证状态和指标汇总 |

## 流程节点

### Step 1：环境准备与工具安装

- **操作**：安装AbODE模型依赖和ANARCI工具
- **参数**：Python >= 3.8, PyTorch, biopython, hmmer=3.3.2
- **工具**：pip, conda
- **质量门禁**：
  - `import torch` 成功
  - `ANARCI --help` 可执行
  - AbODE权重文件abode.ckpt存在且可加载

**AbODE安装**：
```bash
# AbODE基于PyTorch，需确保PyTorch已安装
pip install torch torchvision
# 从论文附录或GitHub获取AbODE代码和权重
# 权重文件：abode.ckpt
```

**ANARCI安装**：
```bash
# 方式一：pip安装（推荐）
pip install ANARCI

# 方式二：conda从源码安装
conda install -c conda-forge biopython -y
conda install -c bioconda hmmer=3.3.2 -y
git clone https://github.com/oxpig/ANARCI.git
cd ANARCI
python setup.py install
```

### Step 2：ANARCI抗体编号

- **操作**：对抗体序列进行标准化编号，获取CDR区域定义
- **参数**：scheme=IMGT, species=human/mouse
- **工具**：ANARCI
- **质量门禁**：
  - 编号成功（非"-"输出）
  - CDR区域位置正确标注
  - 链类型（H/L）正确识别

**调用方式**：
```bash
# 单条序列编号
ANARCI -i EVQLQQSGAEVVRSGASVKLSCTASGFNIKDYYIHWVKQRPEKGLEWIGWIDPEIGDTEYVPKFQGKATMTADTSSNTAYLQLSSLTSEDTAVYYCNAGHDYDRGRFPYWGQGTLVTVSA --scheme imgt

# FASTA文件批量编号
ANARCI -i input.fasta --scheme imgt --outfile output_numbering.txt

# CSV格式输出
ANARCI -i input.fasta --scheme imgt --csv
```

**输出解析**：
- 物种鉴定：`#|species|chain_type|e-value|score|seqstart_index|seqend_index|`
- 编号结果：`H 1 Q`（链类型 位置 氨基酸）
- CDR区域：根据编号方案自动标注（如IMGT的CDR-H1: 26-34, CDR-H2: 56-65, CDR-H3: 105-117）

### Step 3：SAbDab数据获取

- **操作**：从结构抗体数据库获取真实抗原-抗体复合物数据
- **参数**：PDB ID或查询条件
- **工具**：SAbDab Web API, requests
- **质量门禁**：
  - 数据获取成功（HTTP 200）
  - 结构文件完整（含CDR区域原子坐标）
  - 元数据完整（物种、链类型、CDR编号）

**数据获取方式**：
```python
import requests

# SAbDab API查询
url = "https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab/api/"
params = {"pdb_id": "1IGT"}  # 示例PDB ID
response = requests.get(url, params=params)
data = response.json()
```

**数据来源**：
- SAbDab: https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab/
- 参考文献：Dunbar et al. (2014), Nucleic Acids Research

### Step 4：AbODE模型推理

- **操作**：加载AbODE权重，执行抗体序列结构联合生成
- **参数**：checkpoint=abode.ckpt, num_candidates=50, temperature=0.3
- **工具**：PyTorch, AbODE
- **质量门禁**：
  - 模型加载成功（无CUDA/权重错误）
  - 推理完成（生成候选数量达标）
  - 输出序列合法（标准氨基酸字符）

**模型架构**（来自论文[1]）：
- 3层Transformer卷积网络
- 嵌入维度：128-256-64
- 优化器：Adam
- 训练轮次：5000 epochs
- 批大小：300

**推理接口**：
```python
# AbODE推理伪代码（基于论文描述）
import torch
from abode import AbODE  # 假设的模块导入

# 加载模型
model = AbODE.load_checkpoint("abode.ckpt")
model.eval()

# 准备输入（抗原-抗体复合物图）
antibody_graph = prepare_graph(antibody_sequence, antigen_structure)

# 推理
with torch.no_grad():
    generated_sequence, generated_structure = model(antibody_graph, temperature=0.3)
```

### Step 5：CDR-RMSD计算

- **操作**：计算生成抗体CDR区域与参考结构的RMSD
- **参数**：algorithm=Kabsch, atoms=Cα
- **工具**：BioPython, PyMOL, NumPy
- **质量门禁**：
  - 结构比对成功
  - RMSD值在合理范围（通常 < 3Å为优秀）
  - 每个CDR区域独立计算

**计算方法**（来自论文[1]）：
```python
import numpy as np
from Bio.PDB import Superimposer, PDBParser

def calculate_cdr_rmsd(generated_struct, reference_struct, cdr_residues):
    """
    使用Kabsch算法计算CDR区域RMSD
    基于Cα原子空间坐标
    """
    sup = Superimposer()
    
    # 提取CDR区域Cα原子
    gen_atoms = [res['CA'] for res in cdr_residues if 'CA' in res]
    ref_atoms = [res['CA'] for res in cdr_residues if 'CA' in res]
    
    # Kabsch算法对齐
    sup.set_atoms(ref_atoms, gen_atoms)
    rmsd = sup.rms
    
    return rmsd
```

**CDR区域定义**（IMGT方案）：
| CDR | 位置范围 | 长度变化 |
|-----|----------|----------|
| CDR-H1 | 26-34 | 8-12 |
| CDR-H2 | 56-65 | 8-12 |
| CDR-H3 | 105-117 | 10-20+ |
| CDR-L1 | 24-34 | 10-17 |
| CDR-L2 | 50-56 | 6-8 |
| CDR-L3 | 89-97 | 8-12 |

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AbODE嵌入维度 | 128-256-64 | [1] | 3层Transformer卷积网络 |
| AbODE优化器 | Adam | [1] | 默认学习率 |
| AbODE训练轮次 | 5000 | [1] | 完整训练周期 |
| AbODE批大小 | 300 | [1] | 训练批大小 |
| ANARCI编号方案 | IMGT | [D1] | 推荐方案，128个位置 |
| ANARCI依赖 | biopython, hmmer=3.3.2 | [D1] | 必需依赖包 |
| CDR-RMSD算法 | Kabsch | [1] | 基于Cα原子的刚体对齐 |
| CDR-RMSD阈值 | < 3Å（优秀） | [1] | 参考值，需根据任务调整 |
| SAbDab数据集 | 结构抗体数据库 | [2] | 包含PDB结构和抗体注释 |

## 边界与分流

**AbODE模型不可用时**：
- 降级方案：使用替代抗体生成模型（如RefineGNN、MEAN）
- 验证要求：需证明替代模型在目标任务上性能相当

**ANARCI安装失败时**：
- 降级方案：使用手动编号或其他编号工具
- 验证要求：需确认编号方案一致性

**SAbDab数据获取失败时**：
- 降级方案：使用本地抗体数据集或PDB直接下载
- 验证要求：需确认数据质量和完整性

**CDR-RMSD计算异常时**：
- 降级方案：使用其他结构比对指标（如GDT-TS、TM-score）
- 验证要求：需说明指标选择理由

## 质量检查

| 检查项 | 标准 | 失败处理 |
|--------|------|----------|
| 模型加载 | 无错误，权重完整 | 重新下载权重或使用替代模型 |
| ANARCI编号 | 编号成功，CDR标注正确 | 检查序列格式或更换编号方案 |
| 数据获取 | HTTP 200，结构完整 | 尝试其他PDB ID或本地数据 |
| 推理输出 | 候选数量达标，序列合法 | 调整温度参数或检查输入 |
| RMSD计算 | 值在合理范围 | 检查结构对齐或更换参考 |

## 回退策略

1. **AbODE不可用**：使用RefineGNN或MEAN作为替代生成模型
2. **ANARCI不可用**：使用IgBLAST或手动编号，但需验证一致性
3. **SAbDab不可用**：从PDB直接下载抗体结构，手动提取CDR区域
4. **计算资源不足**：减少候选数量或使用CPU推理（性能下降）

## 资源召回建议

**何时召回本卡片**：
- 需要部署AbODE模型进行抗体设计
- 需要使用ANARCI进行抗体编号
- 需要从SAbDab获取抗体数据
- 需要计算CDR-RMSD验证生成结果

**配套资源**：
- `cdr-loop-antibody-backbone-co-generation`：CDR环与抗体骨架联合生成工作流
- `antibody-antigen-paratope-epitope-prediction`：抗体-抗原相互作用预测
- `structure-retrieval-augmented-antibody-design`：结构检索增强的抗体设计

## 补充证据

[D1] ANARCI GitHub仓库, Oxford Protein Informatics Group (OPIG), version 2026.2.13.2, URL: https://github.com/oxpig/ANARCI（accessed 2026-09-16，官方文档）
[D2] ANARCI PyPI包, Python Package Index, version 2026.2.13.2, URL: https://pypi.org/project/ANARCI/（accessed 2026-09-16，安装文档）

## 证据来源

[1] Verma Y, Heinonen M, Garg V. "AbODE: Ab Initio Antibody Design using Conjoined ODEs", ICML 2023, arXiv:2306.01005
[2] Dunbar J, Krawczyk K, Leem J, et al. "SAbDab: the structural antibody database", Nucleic Acids Research, 2014, DOI: 10.1093/nar/gkt1043
