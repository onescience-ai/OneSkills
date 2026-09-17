# 高精度蛋白配体对接场景

## 适用范围

**触发条件**：
- 需要预测小分子配体与蛋白质靶标的结合姿态
- 需要评估化合物库对特定靶标的结合亲和力
- 需要对对接结果进行几何修正和物理有效性验证

**适用场景**：
- 基于结构的虚拟筛选（SBVS）
- 先导化合物优化（lead optimization）
- 结合模式分析和作用机制研究
- 跨对接（cross-docking）评估

**不适用场景**：
- 无蛋白质三维结构的同源建模任务（需先完成结构预测）
- 蛋白-蛋白对接（PPI docking）
- 共价对接（需专门的共价对接工具）

## 输入

- 蛋白质三维结构（PDB 格式，来自 X 射线晶体学、cryo-EM 或 AlphaFold 预测）
- 配体三维结构或 SMILES 字符串
- 结合口袋定义（已知配体位置或预测口袋）
- 数据集文件（如 CrossDocked CSV、PDBbind 数据集）

## 输出

- 蛋白-配体复合物三维结构（PDB/MOL2 格式）
- 结合姿态打分（kcal/mol）
- 几何修正后的有效姿态集合
- 性能评估指标（RMSD、富集因子 EF、AUC）

## 流程节点

### Step 1：数据准备与标准化
- **操作**：获取蛋白质结构和配体库，进行质子化、加氢、能量最小化
- **参数**：力场=AMBER/OPLS，pH=7.4，温度=298K
- **工具**：Open Babel, RDKit, MGLTools
- **质量门禁**：结构完整性检查（缺失残基<5%），配体构象合理性

### Step 2：口袋定义与受体准备
- **操作**：定义结合口袋边界，准备受体蛋白（去水、加氢、分配电荷）
- **参数**：网格盒子大小通常为 20-30 Å³，中心位于共结晶配体重心
- **工具**：AutoDock Tools, PDB2PQR
- **质量门禁**：口袋体积与已知配体体积匹配

### Step 3：姿态采样（对接执行）
- **操作**：在定义的搜索空间内采样配体结合姿态
- **参数**：采样次数=100-10000，exhaustiveness=8-32
- **工具**：AutoDock Vina, GNINA, DiffDock, Uni-Dock
- **质量门禁**：收敛性检查（多次运行 RMSD<2 Å）

### Step 4：打分与筛选
- **操作**：对采样姿态进行打分排序，筛选候选化合物
- **参数**：打分函数类型（经验/力场/知识型），富集因子 EF@1%>5
- **工具**：Vina scoring, CNN scoring (GNINA), PLIP interaction fingerprints
- **质量门禁**：ROC AUC>0.7, Spearman 相关性>0.3

### Step 5：几何修正与验证
- **操作**：对低质量姿态进行几何修正，检查物理有效性
- **参数**：PoseBusters 检查（键长、键角、二面角、立体冲突）
- **工具**：PoseBusters, Open Babel, MD relaxation
- **质量门禁**：PoseBusters 通过率>80%，无严重立体冲突

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 对接引擎 | AutoDock Vina/GNINA/DiffDock | [1][2] | 物理型/深度学习型/扩散模型 |
| 搜索空间 | 20-30 Å³ 网格盒子 | [1] | 覆盖整个结合口袋 |
| 采样穷举度 | exhaustiveness=8-32 | [1] | 影响采样充分性 |
| 打分函数 | Vina/CNN/共识打分 | [1][2] | 多函数共识提升鲁棒性 |
| RMSD 阈值 | <2 Å（redock）, <4 Å（cross-dock） | [3] | 姿态质量判定标准 |
| 富集因子 | EF@1% > 5 | [2] | 虚拟筛选性能指标 |
| PoseBusters | 物理有效性检查 | [3] | 几何修正后验证 |

## 边界与分流

- **redocking vs cross-docking**：redocking 使用共结晶配体结构，性能较高；cross-docking 使用不同晶体结构的蛋白，难度更大 [3]
- **刚性 vs 柔性对接**：刚性对接速度快但可能漏掉诱导契合效应；柔性对接计算量大但更准确 [3]
- **物理型 vs AI型方法**：物理型方法（Vina）在 redocking 中表现良好，AI 型方法（AlphaFold 3, DiffDock）在 cross-docking 中更鲁棒 [3]

## 质量检查

- 姿态 RMSD < 2 Å（相对于晶体结构）
- PoseBusters 物理有效性检查通过
- 无立体原子冲突（clash score < 0.1）
- 打分收敛性（多次运行标准差 < 1.0 kcal/mol）
- 蛋白-配体相互作用指纹一致性

## 回退策略

- 若默认对接工具失败，尝试替代工具（Vina → GNINA → DiffDock）
- 若蛋白结构质量差，使用 AlphaFold 预测结构或 NMR ensemble
- 若数据集不可用，使用公开 PDB 结构构建测试集
- 若计算资源不足，降低采样穷举度或使用 GPU 加速版本

## 资源召回建议

- 对接工作流知识：召回 `bio-protein-ligand-docking-workflow`
- 数据准备任务：召回 `bio-protein-ligand-docking-data-preparation`
- 几何修正任务：召回 `bio-protein-ligand-docking-geometric-refinement`
- 资源检索任务：召回 `bio-protein-ligand-docking-resource-retrieval`

## 证据来源

[1] Azam F, Almahmoud SA. "Open-Source Molecular Docking and AI-Augmented Structure-Based Drug Design: Current Workflows, Challenges, and Opportunities." Int J Mol Sci, 2026, 27(7):3302. DOI: 10.3390/ijms27073302
[2] Agha H, Ibrahim Y, et al. "Data driven selection of consensus docking pipelines for structure based hit identification." npj Drug Discov, 2026, 3:37. DOI: 10.1038/s44386-026-00063-4
[3] Suri K, Yadav A, et al. "Cross-docking and redocking reveal distinct determinants of success in physics-based and AI-driven binding pose prediction." RSC Adv, 2026. DOI: 10.1039/d6ra05440d
