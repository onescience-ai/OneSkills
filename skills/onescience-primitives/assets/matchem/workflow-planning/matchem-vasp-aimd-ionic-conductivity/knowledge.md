# VASP DFT+AIMD 计算固态电解质离子电导率

## 适用范围

**触发条件**：
- 需要计算固态锂离子导体的离子电导率
- 需要预测离子迁移能垒和扩散系数
- 需要进行从头算分子动力学（AIMD）模拟

**适用场景**：
- 固态电解质材料的离子传导性能评估
- 离子迁移路径和能垒的精确计算
- 新型SSLC候选的AIMD验证

**不适用场景**：
- 经典分子动力学模拟（应使用GROMACS/LAMMPS）
- 经验力场MD（非第一性原理）
- 大尺度长时间模拟（>10 ns，计算成本过高）

## 输入

- **晶体结构**：VASP格式（POSCAR）或CIF文件
- **计算参数**：INCAR参数设置
- **K点网格**：KPOINTS文件
- **赝势**：PAW赝势（Materials Project标准）

## 输出

- **离子电导率**：室温离子电导率 σRT (S/cm)
- **激活能**：离子迁移激活能 Ea (eV)
- **扩散系数**：Li离子扩散系数 D (cm²/s)
- **轨迹文件**：AIMD模拟轨迹（XDATCAR）

## 流程节点

### Step 1：DFT结构优化
- **操作**：对初始晶体结构进行静态DFT弛豫
- **参数**：PBE GGA泛函，PAW赝势，Materials Project标准参数
- **工具**：VASP
- **质量门禁**：力收敛 < 0.01 eV/Å，能量收敛 < 10⁻⁶ eV

### Step 2：AIMD模拟设置
- **操作**：构建超胞模型，设置AIMD参数
- **参数**：
  - 系综：NVT（恒温恒体积）
  - 热浴：Nosé-Hoover
  - 时间步长：2 fs
  - 温度：300 K（室温）
- **工具**：VASP
- **质量门禁**：超胞足够大（避免周期性镜像相互作用）

### Step 3：AIMD模拟执行
- **操作**：运行AIMD模拟直至扩散系数收敛
- **参数**：
  - 总模拟时间：100-1000 ps
  - 初始加热：100 K → 300 K，2 ps速度缩放
  - 能量输出间隔：每步
- **工具**：VASP
- **质量门禁**：扩散系数收敛（误差 < 20%）

### Step 4：扩散系数计算
- **操作**：从AIMD轨迹计算Li离子均方位移（MSD）
- **参数**：Einstein关系 D = MSD/(2dT)
- **工具**：Python/NumPy，pymatgen
- **质量门禁**：MSD曲线线性良好，R² > 0.95

### Step 5：离子电导率计算
- **操作**：从扩散系数计算离子电导率
- **参数**：Nernst-Einstein关系 σ = nq²D/(kT)
- **工具**：Python
- **质量门禁**：σRT > 10⁻⁴ S/cm视为合格SSLC

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| DFT泛函 | PBE GGA | [1] | Materials Project标准 |
| 赝势 | PAW | [1] | 投影缀加波方法 |
| 系综 | NVT | [1] | 恒温恒体积 |
| 热浴 | Nosé-Hoover | [1] | 恒温器方法 |
| 时间步长 | 2 fs | [1] | AIMD标准设置 |
| 模拟时间 | 100-1000 ps | [1] | 直至扩散收敛 |
| 初始温度 | 100 K | [1] | 加热至300 K |
| 离子电导率阈值 | > 10⁻⁴ S/cm | [1] | SSLC最低要求 |
| 高导电阈值 | > 10⁻² S/cm | [1] | 与最佳SSLC相当 |

## 边界与分流

**VASP vs GROMACS适用场景区分**：
- **VASP**：DFT/AIMD，量子力学计算，电子结构、离子迁移能垒、相稳定性
- **GROMACS**：经典MD，经验力场，原子运动轨迹、扩散系数（非第一性原理）
- **固态电解质**：优先使用VASP进行AIMD，GROMACS仅适用于已有力场的经典MD

**异常处理**：
- 若AIMD不收敛，延长模拟时间或增大超胞
- 若能量发散，减小时间步长至1 fs
- 若扩散系数异常，检查轨迹是否有Li离子逃逸

## 质量检查

- **结构优化收敛**：力 < 0.01 eV/Å
- **AIMD能量守恒**：总能量波动 < 1 meV/atom
- **MSD线性度**：R² > 0.95
- **扩散收敛**：误差 < 20%

## 回退策略

- 若VASP不可用，考虑CP2K进行AIMD
- 若AIMD资源不足，使用NEB方法计算迁移能垒
- 若无法进行DFT，使用机器学习势函数（MLP）加速

## 资源召回建议

**何时应召回本卡片**：
- 任务需要计算固态电解质的离子电导率
- 场景HPC指定VASP进行DFT/AIMD计算
- 需要验证无监督发现的SSLC候选

**配套资源**：
- `matchem-sslcs-unsupervised-discovery`：无监督发现流程
- `matchem-materials-project-api`：结构数据获取
- `matchem-blocked-trigger-rules`：输入缺失处理

## 证据来源

[1] "Unsupervised discovery of solid-state lithium ion conductors", Ying Zhang et al., Nature Communications, 2019, DOI: 10.1038/s41467-019-13214-1

[2] "Machine Learning Interatomic Potentials as Emerging Tools for Materials Science", Volker L. Deringer et al., Advanced Materials, 2019, DOI: 10.1002/adma.201904782
