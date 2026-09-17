# RFdiffusion输入输出规范与权重约定

## 适用范围

**适用场景**：
- 功能位点约束蛋白骨架生成任务的输入准备、模型加载、参数配置和输出验证
- 修正归因报告中识别的输入文件、权重文件、生成参数和筛选指标偏离

**不适用场景**：
- 无条件蛋白生成（无基序约束）
- 蛋白序列设计（ProteinMPNN任务）
- 结构预测（AlphaFold2/ESMFold任务）

## 输入规范

### PDB输入文件要求

| 要求 | 规范 | 说明 |
|------|------|------|
| 文件格式 | PDB格式（.pdb） | 必须包含ATOM记录 |
| 原子完整性 | 所有基序残基的原子坐标完整 | 缺失原子会导致约束编码失败 |
| 链标识 | 明确指定链ID（如A） | 多链PDB需指定目标链 |
| 基序定义 | 功能位点残基坐标在文件中 | 催化残基、结合残基等 |
| 默认文件名 | motif_5tpn.pdb | 标准工作流约定名称 |

### 约束定义规范

| 约束类型 | 格式 | 示例 |
|----------|------|------|
| 固定残基索引 | list[int] | [10, 25]（1-indexed） |
| 基序区域 | 原子坐标 | 从PDB中提取 |
| 目标长度 | int | 256（范围20-1200） |
| 对称群 | str | C1（无对称）/ C2 / C3等 |

**关键约束**：
- 固定残基索引必须在目标长度范围内
- 约束变更必须记录并经用户确认
- 默认固定残基[1, 2, 3]与标准示例[10, 25]不符时需说明依据

## 模型权重约定

### 权重文件命名规范

| 权重名称 | 文件名 | 适用场景 | 说明 |
|----------|--------|----------|------|
| 基础权重 | Base_ckpt.pt | 默认功能位点约束生成 | 标准工作流指定 |
| 超电权重 | Supercharge_ckpt.pt | 高电荷蛋白设计 | 特殊场景 |
| 对称权重 | Symmetric_ckpt.pt | 对称寡聚体设计 | 对称约束 |
| 全原子权重 | AllAtom_ckpt.pt | 全原子结构生成 | 需原子坐标 |

**关键约定**：
- 任务prompt或标准工作流中指定的权重文件是权威标识
- 权重文件必须在代码中作为配置参数加载，而非任意命名
- 加载时需校验文件存在性和完整性
- 不同权重版本的约束编码方式可能不同

### 权重加载验证

```python
# 正确加载方式
checkpoint = torch.load('Base_ckpt.pt', map_location='cpu')
# 验证检查点结构
assert 'model_state_dict' in checkpoint
assert 'config' in checkpoint
```

## 命令行参数接口

### 核心生成参数

| 参数 | 命令行 | 默认值 | 范围 | 说明 |
|------|--------|--------|------|------|
| 设计数量 | `--num_designs` | 64 | 1-5000 | 生成候选数量 |
| 采样温度 | `--temperature` | 0.2 | 0.01-2 | 控制采样多样性 |
| 随机种子 | `--random_seed` | 17 | 0-2147483647 | 可复现性 |
| 输入文件 | `--input_pdb` | motif_5tpn.pdb | — | 输入PDB路径 |
| 固定残基 | `--fixed_residues` | [10, 25] | — | 固定残基索引 |
| 目标长度 | `--target_length` | 256 | 20-1200 | 骨架总长度 |

### 参数传递验证

```bash
# 标准调用示例
python scripts/run_inference.py \
    --input_pdb motif_5tpn.pdb \
    --num_designs 64 \
    --temperature 0.2 \
    --random_seed 17 \
    --fixed_residues 10,25 \
    --target_length 256
```

**验证要点**：
- 生成数量必须≥64（标准要求）
- 随机种子必须记录在生成日志中
- 采样温度必须在合理范围内

## 基序RMSD计算方法

### 计算原理

基序RMSD（Motif RMSD）衡量生成骨架中基序区域原子坐标与输入基序的偏差：

```
RMSD = sqrt(1/N * sum_i ||x_i^gen - x_i^ref||^2)
```

其中：
- N：基序原子数量
- x_i^gen：生成结构中第i个原子坐标
- x_i^ref：参考基序中第i个原子坐标

### 计算步骤

1. 从生成PDB中提取基序区域原子坐标
2. 从输入PDB中提取参考基序原子坐标
3. 最小二乘叠合（superposition）
4. 计算RMSD值

### 阈值含义

| 阈值范围 | 含义 | 处理建议 |
|----------|------|----------|
| ≤0.6Å | 合格 | 入选候选 |
| 0.6-1.0Å | 边缘 | 需人工审核 |
| >1.0Å | 不合格 | 淘汰 |

**关键约定**：
- 基序RMSD是核心筛选指标（非sc/ptm）
- 阈值0.6Å是默认标准，可按任务调整
- sc/ptm可作为辅助指标，但不能替代基序RMSD

### 计算脚本示例

```python
import numpy as np
from Bio.PDB import PDBParser, Superimposer

def calculate_motif_rmsd(gen_pdb, ref_pdb, motif_residues):
    parser = PDBParser(QUIET=True)
    gen_structure = parser.get_structure('gen', gen_pdb)
    ref_structure = parser.get_structure('ref', ref_pdb)
    
    gen_atoms = [res['CA'] for res in gen_structure[0].get_residues() 
                 if res.get_id()[1] in motif_residues]
    ref_atoms = [res['CA'] for res in ref_structure[0].get_residues() 
                 if res.get_id()[1] in motif_residues]
    
    sup = Superimposer()
    sup.set_atoms(ref_atoms, gen_atoms)
    sup.apply(gen_atoms)
    
    return sup.rms
```

## 工具链依赖

### 必需工具

| 工具 | 用途 | 安装方式 | 验证方法 |
|------|------|----------|----------|
| PyMOL | 结构可视化、RMSD计算 | conda install -c conda-forge pymol | `pymol -c -d "version"` |
| ProteinMPNN | 序列设计 | pip install proteinmpnn | `python -c "import proteinmpnn"` |
| AlphaFold2/ESMFold | 回折叠验证 | 见官方文档 | 模型文件存在性检查 |

### 工具依赖链

```
RFdiffusion（生成骨架）
    ↓
ProteinMPNN（设计序列）
    ↓
AlphaFold2/ESMFold（回折叠验证）
    ↓
PyMOL（结构可视化、RMSD计算）
```

### 预检验证步骤

1. **PyMOL验证**：检查PyMOL是否可用，失败时给出安装指引
2. **模型权重验证**：检查权重文件是否存在且完整
3. **依赖包验证**：检查numpy、scipy、torch等是否安装

**预检失败处理**：
- 记录失败原因（如"missing required software: pymol"）
- 提供明确的安装指引
- 不得跳过预检直接执行

## 质量检查

### 输入验证

- [ ] PDB文件格式正确（ATOM记录完整）
- [ ] 基序残基原子坐标无缺失
- [ ] 固定残基索引在目标长度范围内
- [ ] 约束变更已记录并确认

### 模型加载验证

- [ ] 权重文件名与标准一致（Base_ckpt.pt）
- [ ] 权重文件完整（无损坏）
- [ ] 模型配置与任务匹配

### 生成验证

- [ ] 生成数量≥64
- [ ] 随机种子已记录
- [ ] 采样温度在合理范围

### 筛选验证

- [ ] 基序RMSD已计算
- [ ] 阈值≤0.6Å
- [ ] 汇总表和质控报告已生成

## 证据来源

[1] Watson JL, et al. De novo design of protein structure and function with RFdiffusion. Nature, 2023, 620:1089-1100. DOI: 10.1038/s41586-023-06415-8
