# DiffDock盲对接坐标变换与置信度排序

## 适用范围

**触发条件**：使用DiffDock或类似扩散生成模型进行盲对接任务，需要理解其坐标变换机制和置信度评估方法时召回本卡片。

**适用场景**：
- DiffDock盲对接任务的坐标后处理
- 扩散对接模型输出姿态的置信度评估
- 对接姿态的坐标系变换与RMSD计算前置处理

**不适用场景**：
- 传统对接程序（如AutoDock Vina、GOLD）的输出处理
- 已知口袋位点的对接任务（DiffDock专为盲对接设计）

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| DiffDock输出姿态 | 含translation/rotation/torsion | 模型采样的配体位姿参数 |
| 蛋白坐标系原点 | PDB坐标 | 用于坐标变换的参考 |
| 初始配体构象 | SDF/MOL2 | 配体的初始3D坐标 |
| 置信度分数 | float | DiffDock confidence model输出 |

**关键概念**：
- **局部坐标系**：配体初始构象的坐标系（通常以配体质心或特定原子为原点）
- **全局坐标系**：蛋白质/PDB坐标系
- **DiffDock参数**：translation(3D), rotation(3D), torsion(n维)

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| 变换后配体坐标 | numpy array | 在蛋白质坐标系中的原子坐标 |
| 置信度排名 | int | 基于confidence model的姿态排名 |
| 最终对接构象 | SDF/PDB | 可用于后续分析的标准格式 |

## 流程节点

### 1. DiffDock输出参数解析

**DiffDock采样输出**：
每个姿态由以下参数描述：
- **translation**：配体在蛋白质坐标系中的平移向量 (x, y, z) ∈ R³
- **rotation**：配体的旋转矩阵或四元数表示 SE(3)
- **torsion**：配体可旋转键的二面角 ∈ [0, 2π]^n

**坐标变换公式**：
$$x_{global} = R \cdot x_{local} + t$$

其中：
- $x_{global}$：蛋白质坐标系中的原子坐标
- $x_{local}$：配体局部坐标系中的原子坐标
- $R$：旋转矩阵（由rotation参数计算）
- $t$：平移向量（translation参数）

### 2. Translation/Rotation/Torsion到原子坐标变换

**完整变换流程**：

```python
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

def diffdock_to_cartesian(initial_coords, translation, rotation, torsion, rotatable_bonds):
    """
    将DiffDock参数转换为笛卡尔坐标
    
    参数:
        initial_coords: 初始配体坐标 (N_atoms, 3)
        translation: 平移向量 (3,)
        rotation: 旋转矩阵 (3, 3) 或 四元数
        torsion: 可旋转键二面角 (N_rotatable,)
        rotatable_bonds: 可旋转键列表
    
    返回:
        final_coords: 变换后的坐标 (N_atoms, 3)
    """
    coords = initial_coords.copy()
    
    # 步骤1: 应用扭转角变换（绕可旋转键旋转）
    for bond_idx, angle in zip(rotatable_bonds, torsion):
        coords = apply_torsion(coords, bond_idx, angle)
    
    # 步骤2: 计算配体质心
    centroid = np.mean(coords, axis=0)
    
    # 步骤3: 平移至原点
    coords -= centroid
    
    # 步骤4: 应用旋转
    if isinstance(rotation, np.ndarray) and rotation.shape == (3, 3):
        coords = coords @ rotation.T
    else:
        # 处理四元数情况
        R = quaternion_to_rotation_matrix(rotation)
        coords = coords @ R.T
    
    # 步骤5: 应用平移
    coords += translation
    
    return coords

def apply_torsion(coords, bond_idx, angle):
    """应用扭转角变换"""
    atom_i, atom_j = bond_idx
    # 计算旋转轴（bond direction）
    axis = coords[atom_j] - coords[atom_i]
    axis = axis / np.linalg.norm(axis)
    
    # 绕轴旋转angle弧度
    rotation_matrix = rotation_matrix_from_axis_angle(axis, angle)
    
    # 旋转bond_j之后的所有原子
    mask = get_atoms_after_bond(coords, atom_i, atom_j)
    coords[mask] = coords[mask] @ rotation_matrix.T
    
    return coords
```

### 3. 坐标系对齐策略

**问题**：DiffDock采样生成的pose坐标系可能与实验参考坐标系不一致

**解决方案**：

#### 方案A：Kabsch对齐（已知参考构象）
```python
from scipy.spatial.transform import Rotation

def kabsch_alignment(pred_coords, ref_coords):
    """
    Kabsch算法最优对齐
    返回: 对齐后的坐标, RMSD
    """
    # 中心化
    pred_centered = pred_coords - np.mean(pred_coords, axis=0)
    ref_centered = ref_coords - np.mean(ref_coords, axis=0)
    
    # SVD分解
    H = pred_centered.T @ ref_centered
    U, S, Vt = np.linalg.svd(H)
    
    # 计算旋转矩阵
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    
    # 对齐
    aligned = pred_centered @ R.T
    
    # 计算RMSD
    rmsd = np.sqrt(np.mean(np.sum((aligned - ref_centered)**2, axis=1)))
    
    return aligned + np.mean(ref_coords, axis=0), rmsd
```

#### 方案B：Self-RMSD（无实验参考）
```python
def self_rmsd(poses, n_samples=100):
    """
    计算姿态间的self-RMSD
    用于评估采样多样性
    """
    rmsd_matrix = np.zeros((len(poses), len(poses)))
    for i in range(len(poses)):
        for j in range(i+1, len(poses)):
            _, rmsd = kabsch_alignment(poses[i], poses[j])
            rmsd_matrix[i, j] = rmsd
            rmsd_matrix[j, i] = rmsd
    
    return rmsd_matrix.mean()
```

### 4. DiffDock置信度模型训练机制

**训练目标**：
- 二分类模型：预测姿态是否 RMSD ≤ 2Å（正样本）或 > 2Å（负样本）
- 输入：蛋白质-配体复合物的图表示 + 预测姿态的几何特征
- 输出：置信度分数 ∈ [0, 1]

**训练数据**：
- 正样本：RMSD ≤ 2Å的对接姿态（从PDBbind训练集采样）
- 负样本：随机打乱或错误对接的姿态

**推理流程**：
```
DiffDock采样40个姿态 → 每个姿态计算confidence score → 按score排名 → 选择top-k
```

### 5. NMDN置信度校准方法

**背景**：DiffDock原始confidence model存在校准不足问题

**NMDN方法**（Normalized Mixture Density Network）：

**核心思想**：
$$NMDN\_score = -\sum_{i,j} \log \frac{P(d_{ij} | \mu_{ij}, \sigma_{ij}, \rho_{ij})}{P_{ref}(d_{ij})}$$

其中：
- $d_{ij}$：蛋白残基i与配体原子j的最小距离
- $P(d_{ij} | ...)$：预测的距离概率密度
- $P_{ref}(d_{ij})$：参考概率（在截止距离处采样）

**实现要点**：
```python
def compute_nmdn_score(protein_embeddings, ligand_embeddings, distances, nmdn_model):
    """
    计算NMDN置信度分数
    
    参数:
        protein_embeddings: ESM-2蛋白残基嵌入
        ligand_embeddings: 配体原子嵌入
        distances: 蛋白-配体原子对距离矩阵
        nmdn_model: 预训练的NMDN模型
    
    返回:
        nmdn_score: 负对数似然分数（越高越好）
    """
    # 预测距离分布参数
    mu, sigma, rho = nmdn_model(protein_embeddings, ligand_embeddings)
    
    # 计算每个原子对的概率密度
    prob_density = mixture_density(distances, mu, sigma, rho)
    
    # 计算参考概率（截止距离处）
    ref_distance = 9.0  # Å
    ref_prob = compute_reference_prob(ref_distance, nmdn_model)
    
    # NMDN score = -log(P/Pref)
    nmdn_score = -np.sum(np.log(prob_density / ref_prob))
    
    return nmdn_score
```

**优势**：
- 对蛋白-配体截止距离变化更鲁棒
- 训练时不需要实验结合亲和力数据
- 可与pKd预测模型结合进行虚拟筛选

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| RMSD成功阈值 | 2.0 Å | [DiffDock] | confidence model训练标签 |
| DiffDock采样数 | 40 | [DiffDock] | 默认每蛋白-配体对采样数 |
| NMDN截止距离 | 9.0 Å | [DiffDock-NMDN] | 蛋白-配体对计算范围 |
| NMDN参考点 | 6个 (8.5-9.0Å) | [DiffDock-NMDN] | 数值稳定性 |
| 配体初始构象 | RDKit ETKDGv3 | [CarsiDock] | 生成10个随机构象 |
| 旋转矩阵表示 | 四元数/矩阵 | [DiffDock] | 避免万向锁 |

## 边界与分流

### 异常处理

| 异常情况 | 处理策略 |
|----------|----------|
| Translation超出蛋白范围 | 检查搜索空间定义，限制在口袋内 |
| Rotation产生非物理构象 | 使用PoseBusters验证后剔除 |
| Torsion导致键长异常 | 应用RDKit DistanceGeometry约束 |
| Confidence score全为低分 | 检查输入蛋白-配体格式，确认ESM-2嵌入 |

### 降级策略

当DiffDock模型不可用或输出异常时：

1. **切换至传统对接**：使用AutoDock Vina或GOLD生成姿态
2. **使用CarsiDock**：基于距离矩阵预测的替代DL方法
3. **混合策略**：DiffDock采样 + NMDN/RTMScore重排序

## 质量检查

### 验证点

| 检查点 | 通过标准 | 失败处理 |
|--------|----------|----------|
| 坐标变换完成 | 所有原子坐标有效 | 检查rotation/translation维度 |
| 置信度分数分布 | 符合预期范围 | 校准模型或切换评分函数 |
| RMSD计算成功 | 无NaN/Inf | 检查坐标对齐逻辑 |

### 阈值失败处理

- Confidence score < 0.5：标记为低置信度姿态
- NMDN score异常高：检查距离计算是否有误
- RMSD > 5Å：可能坐标变换错误，重新检查变换流程

## 回退策略

1. **能量最小化修复**：使用OpenMM/AMBER力场最小化修复物理不合理姿态
2. **多方法集成**：结合DiffDock + CarsiDock + 传统对接结果
3. **后期重排序**：使用RTMScore或GNINA对DiffDock输出重排序

## 资源召回建议

**何时召回本卡片**：
- 任务涉及DiffDock盲对接时
- 需要将DiffDock输出转换为标准坐标时
- 需要评估DiffDock置信度分数可靠性时
- 检测到坐标系不匹配导致RMSD计算失败时

**配套资源**：
- `matchem-docking-rmsd-evaluation`：RMSD计算标准流程
- `matchem-openbabel-protonation`：OpenBabel质子化处理（待补充）
- `matchem-gnina-scoring`：GNINA独立打分验证（待补充）

## 证据来源

[1] Xia S, Gu Y, Zhang Y. Normalized Protein-Ligand Distance Likelihood Score for End-to-End Blind Docking and Virtual Screening. Journal of Chemical Information and Modeling. 2025;65:1798-1812. DOI: 10.1021/acs.jcim.4c01014

[2] Cai H, Shen C, Jian T, et al. CarsiDock: a deep learning paradigm for accurate protein-ligand docking and screening based on large-scale pre-training. Chemical Science. 2024;15:1798-1812. DOI: 10.1039/d3sc05552c

[3] Buttenschoen M, Morris GM, Deane CM. PoseBusters: AI-based docking methods fail to generate physically valid poses or generalise to novel sequences. Chemical Science. 2024;15:3130-3139. DOI: 10.1039/d3sc04185a

[4] Alakhdar AA, Póczos B, Washburn NR. Diffusion Models in De Novo Drug Design. Journal of Chemical Information and Modeling. 2024;64:5289-5303. DOI: 10.1021/acs.jcim.4c01107

[5] Corso G, Stärk H, Jing B, et al. DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking. arXiv:2210.01776. 2022.
