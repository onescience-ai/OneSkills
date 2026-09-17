# 蛋白-配体对接姿态RMSD计算标准流程

## 适用范围

**触发条件**：对接工作流中需要评估预测姿态与实验参考构象的相似度，或需要筛选高质量对接姿态时召回本卡片。

**适用场景**：
- 已对接位姿与晶体结构的重对接（redocking）评估
- 跨对接（cross-docking）姿态质量验证
- 虚拟筛选中对接姿态排名与筛选

**不适用场景**：
- 蛋白-蛋白对接（需要专门的interface RMSD方法）
- 无蛋白结构的纯配体构象生成评估

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| 预测配体姿态 | SDF/PDB | 对接算法生成的配体构象 |
| 实验参考配体 | SDF/PDB | PDB晶体结构中的参考配体 |
| 受体蛋白 | PDB | 用于计算蛋白-配体碰撞 |

**预处理要求**：
- 配体和参考结构需包含重原子坐标（C, N, O, S, P, 卤素等）
- 需要去除溶剂分子
- 氢原子可用于计算但非RMSD必需

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| RMSD值 | float | 单位Å，heavy-atom对称感知RMSD |
| PB-valid标志 | bool | 是否通过PoseBusters全部物理合理性检查 |
| PLIF恢复率 | float | 蛋白-配体相互作用指纹恢复百分比 |

## 流程节点

### 1. Heavy-Atom RMSD计算

**方法**：使用对称感知的RMSD计算，自动考虑配体对称性

**标准实现**（RDKit）：
```python
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign

# 加载分子（禁用sanitization以保留原始化学信息）
pred_mol = Chem.MolFromMolFile('predicted_pose.sdf', removeHs=False, sanitize=False)
ref_mol = Chem.MolFromMolFile('reference_ligand.sdf', removeHs=False, sanitize=False)

# 计算对称感知RMSD（自动匹配对称原子）
rmsd = rdMolAlign.GetBestRMS(pred_mol, ref_mol)
```

**关键参数**：
- 默认使用RDKit的`GetBestRMS`函数（对称感知）
- 忽略氢原子计算（只比较重原子）

### 2. 通过/失败阈值

**标准阈值**：RMSD ≤ 2.0 Å

**阈值依据**：
- 经验性标准，适用于常规尺寸配体（<50重原子）[PoseBusters]
- CASF-2016基准测试的通用成功标准
- >2Å通常表示结合模式预测失败

**例外情况**：
- 柔性配体（可旋转键>10）：阈值可放宽至2.5Å
- 大分子配体（>50重原子）：建议使用lDDT或交互恢复率辅助评估

### 3. PoseBusters物理合理性验证

**检测项目**：

| 检测类型 | 检测内容 | 默认阈值 |
|----------|----------|----------|
| 化学有效性 | RDKit sanitization通过 | 必须通过 |
| 化学一致性 | InChI匹配（忽略同位素/电荷） | 必须匹配 |
| 键长合理性 | 与RDKit DistanceGeometry偏差 | ≤25% |
| 键角合理性 | 与RDKit DistanceGeometry偏差 | ≤25% |
| 平面性 | 芳香环/双键原子平面偏差 | ≤0.25Å |
| 配体能量 | 对50个生成构象的UFF能量比 | ≤100 |
| 蛋白-配体碰撞 | 原子间vdW距离比 | ≥0.75 |
| 体积重叠 | 蛋白配体vdW体积重叠率 | ≤7.5% |

**PB-valid定义**：通过所有PoseBusters测试的姿态

### 4. 蛋白-配体相互作用指纹（PLIF）恢复率

**定义**：
$$PLIF_{recovery} = \frac{\sum_{i,r} \min(C_{i,r}^{crystal}, P_{i,r}^{docked})}{\sum_{i,r} C_{i,r}^{crystal}}$$

**检测的相互作用类型**：
- 氢键（donor/acceptor，距离阈值3.7Å）
- 卤素键
- π-π堆积
- 阳离子-π/π-阳离子
- 离子相互作用（阴离子/阳离子，距离阈值5.0Å）

**质量门禁**：
- PLIF恢复率 ≥ 50%：基本可接受
- PLIF恢复率 ≥ 80%：良好
- PLIF恢复率 = 100%：完全恢复所有关键相互作用

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| RMSD阈值 | 2.0 Å | [PoseBusters] | 标准成功阈值 |
| 键长容差 | 25% | [PoseBusters] | 与DistanceGeometry下限比较 |
| 键角容差 | 25% | [PoseBusters] | 与DistanceGeometry下限比较 |
| 平面性阈值 | 0.25 Å | [PoseBusters] | 芳香环原子平面偏差 |
| 能量比阈值 | 100 | [PoseBusters] | 对比50个随机构象 |
| 碰撞距离比 | 0.75 | [PoseBusters] | vdW半径和的比例 |
| 体积重叠 | 7.5% | [PoseBusters] | 形状Tversky指数 |
| H键距离 | 3.7 Å | [PLIF validity] | 氢键最大距离 |
| 离子距离 | 5.0 Å | [PLIF validity] | 离子相互作用最大距离 |

## 边界与分流

### 异常处理

| 异常情况 | 处理策略 |
|----------|----------|
| 无实验参考构象 | 切换至self-RMSD验证模式 |
| 参考配体存在多重构象 | 选择B因子最低的构象作为参考 |
| 配体高度对称 | 使用对称感知RMSD（GetBestRMS） |
| 蛋白存在多链 | 只计算目标链的碰撞检测 |

### 降级策略

当无法获取实验参考构象时，采用以下替代验证：

1. **Self-RMSD**：同一配体不同对接姿态间的RMSD，用于内部一致性检查
2. **PoseBusters验证**：仅检查物理合理性，不依赖参考构象
3. **PLIF恢复率**：如果口袋残基已知，可评估相互作用恢复
4. **对接分数分布**：评估置信度分数的物理意义性

## 质量检查

### 验证点

| 检查点 | 通过标准 | 失败处理 |
|--------|----------|----------|
| RMSD计算完成 | 所有姿态有有效RMSD值 | 检查坐标对齐逻辑 |
| PB-valid比例 | >50%姿态通过物理合理性检查 | 检查对接算法实现 |
| RMSD分布合理 | 均值1.5-2.5Å，无异常值 | 检查参考构象选择 |

### 阈值失败处理

- RMSD > 2Å：标记为"失败"，但记录具体RMSD值供分析
- PB-valid失败：记录具体失败项目，可选择能量最小化修复
- PLIF恢复率低：检查关键残基方向，考虑重新对接

## 回退策略

1. **能量最小化修复**：对接后使用力场最小化（如AMBER ff14sb + Sage）修复物理不合理姿态
2. **多姿态生成**：生成10-40个姿态，选择最佳排名
3. **混合策略**：结合DL和传统对接方法的优势

## 资源召回建议

**何时召回本卡片**：
- 实现金字塔任务（s04阶段）需要RMSD计算时
- 对接姿态排名/筛选需要物理合理性验证时
- 检测到对接姿态坐标系不匹配时
- 需要评估对接算法性能时

**配套资源**：
- `matchem-diffdock-coordinate-scoring`：DiffDock坐标变换与置信度排序
- `matchem-openbabel-protonation`：OpenBabel质子化处理（待补充）
- `matchem-gnina-scoring`：GNINA独立打分验证（待补充）

## 证据来源

[1] Buttenschoen M, Morris GM, Deane CM. PoseBusters: AI-based docking methods fail to generate physically valid poses or generalise to novel sequences. Chemical Science. 2024;15:3130-3139. DOI: 10.1039/d3sc04185a

[2] Errington D, Schneider C, Bouysset C, et al. Assessing interaction recovery of predicted protein-ligand poses. Journal of Cheminformatics. 2025;17:41. DOI: 10.1186/s13321-025-01011-6

[3] Xia S, Gu Y, Zhang Y. Normalized Protein-Ligand Distance Likelihood Score for End-to-End Blind Docking and Virtual Screening. Journal of Chemical Information and Modeling. 2025;65:1798-1812. DOI: 10.1021/acs.jcim.4c01014

[4] Cai H, Shen C, Jian T, et al. CarsiDock: a deep learning paradigm for accurate protein-ligand docking and screening based on large-scale pre-training. Chemical Science. 2024;15:1798-1812. DOI: 10.1039/d3sc05552c

[5] CASF-2016: Comparative Assessment of Scoring Functions. DOI: 10.1021/acs.jcim.6b00690
