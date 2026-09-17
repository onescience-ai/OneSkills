# VASP第一性原理计算验证振动稳定性工作流

## 适用范围

**触发条件**：
- 需要精确计算材料的声子色散关系
- 需要验证ML模型预测的动力学稳定性
- 研究需要热力学性质（热容、自由能等）

**适用场景**：
- 材料稳定性验证：确认候选材料无虚频
- 热力学分析：计算有限温度下的声子性质
- ML模型验证：为ML预测提供ground truth

**不适用场景**：
- 大规模筛选（>1000个结构）：计算成本过高
- 非周期性体系（分子、团簇）
- 强关联体系需要DFT+U或更高级方法

## 输入

**数据来源**：
- 晶体结构文件：POSCAR（VASP格式）或CIF
- VASP输入文件：INCAR、KPOINTS、POTCAR
- PHONOPY配置文件：phonopy.yaml

**数据格式**：
- POSCAR：VASP标准格式，包含原子坐标和晶格矢量
- INCAR：VASP计算参数设置
- KPOINTS：k点网格设置

**预处理要求**：
- 结构优化：使用VASP进行离子弛豫到力收敛
- 超胞构建：通常使用2x2x2或3x3x3超胞
- 位移模式生成：PHONOPY自动计算

## 输出

**产物**：
- 声子色散关系图（phonon dispersion）
- 声子态密度（phonon DOS）
- 热力学性质：热容Cv、自由能F、熵S
- 动力学稳定性判据：最小频率>0 cm^-1

**验证标准**：
- 虚频检查：所有频率>0 cm^-1为动力学稳定
- 收敛性：k点和截断能收敛到0.1 meV/atom
- 力常数对称性：满足晶体对称性要求

## 流程节点

### Step 1：结构优化
- **操作**：使用VASP进行离子弛豫
- **参数**：ENCUT=520 eV, KPOINTS密度=40/Å, ISIF=3
- **工具**：VASP, pymatgen
- **质量门禁**：离子力<0.01 eV/Å，能量收敛<1e-6 eV

### Step 2：超胞构建与位移
- **操作**：使用PHONOPY生成位移结构
- **参数**：supercell_matrix=[[2,0,0],[0,2,0],[0,0,2]], displacement=0.01 Å
- **工具**：PHONOPY
- **质量门禁**：位移对称性正确，超胞大小足够

### Step 3：力常数计算
- **操作**：对每个位移结构进行VASP静态计算
- **参数**：ENCUT=520 eV, KPOINTS密度=40/Å, IBRION=-1
- **工具**：VASP, PHONOPY
- **质量门禁**：力常数收敛，对称性满足

### Step 4：声子分析
- **操作**：提取声子色散和热力学性质
- **参数**：温度范围=0-1000K, 压力=0 GPa
- **工具**：PHONOPY, phonopy-api
- **质量门禁**：无虚频（动力学稳定），热力学性质合理

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 平面波截断能 | 520 eV | [1][2] | 保证精度 |
| k点密度 | 40/Å | [1] | 足够采样布里渊区 |
| 超胞大小 | 2x2x2或3x3x3 | [1][3] | 需测试收敛性 |
| 位移幅度 | 0.01 Å | [1] | 线性响应范围内 |
| 力收敛阈值 | 0.01 eV/Å | [2] | 结构优化标准 |
| 交换关联泛函 | PBE/r2SCAN | [2] | 影响精度 |

## 边界与分流

**异常处理**：
- 虚频出现：检查结构是否真正稳定，可能需要更高精度或不同泛函
- 收敛困难：增大k点密度或截断能，或使用更严格的收敛标准
- 计算资源不足：使用PHONOPY的DFPT方法减少计算量

**降级策略**：
- VASP不可用：使用Quantum ESPRESSO或ABINIT
- 计算时间过长：使用ML势函数替代DFT力常数计算

## 质量检查

**验证点**：
- 声子色散无虚频（所有频率>0 cm^-1）
- 热力学性质在合理范围（Cv→3NkB at high T）
- 与文献值比较（如果可用）
- 力常数矩阵对称性检查

**阈值**：
- 最小频率>0 cm^-1（动力学稳定）
- 能量收敛<1e-6 eV/atom
- 力收敛<0.01 eV/Å

## 回退策略

**失败时的替代方案**：
- VASP计算失败：使用Quantum ESPRESSO + Phonopy
- 资源不足：使用ML势函数（如M3GNet）替代DFT
- 强关联体系：使用DFT+U或杂化泛函

## 资源召回建议

**何时应召回本卡片**：
- 用户需要精确验证材料振动稳定性
- 用户提到"phonon calculation"、"VASP"、"dynamical stability"
- 需要为ML模型提供ground truth数据

**配套资源**：
- matchem-vibrationally-stable-materials-ml-screening：ML预筛选工作流
- onescience-runtime：VASP作业提交和管理

## 证据来源

[1] Tee WS, Xia W, Flint R, Wang CZ. "Anharmonic effects on the dynamical stability of Ce-Co-Cu intermetallic ternary compounds." RSC Adv, 2026, 16(16): 14395-14405. DOI: 10.1039/d5ra09680d

[2] Mamabolo MS, Hlungwani D, Malatji KT, et al. "Exploiting Exchange-Correlation Functionals' Performance for Structure and Property Prediction of the NaAlP2O7 Solid Electrolyte Material." Materials, 2026, 19(9): 1673. DOI: 10.3390/ma19091673

[3] Lee H, Li Z, He J, Xia Y. "Data-Driven Exploration and Insights Into Temperature-Dependent Phonons in Inorganic Materials." Small, 2026, 22(46): e00071. DOI: 10.1002/smll.202600071
