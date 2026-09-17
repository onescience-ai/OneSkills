# VASP DFT计算工作流

## 适用范围

**触发条件**：
- 需要第一性原理精度计算材料电子结构
- 需要验证机器学习预测结果的可靠性
- 需要计算材料的光学性质、催化活性或反应能垒

**适用场景**：
- CO2光催化剂的电子结构分析
- 光催化反应机理的DFT研究
- 材料带隙、导带/价带位置的精确计算
- 催化剂表面吸附能和反应路径计算

**不适用场景**：
- 大规模高通量筛选（计算成本过高）
- 需要分子动力学模拟的场景（应使用LAMMPS）
- 需要相对论效应的重元素体系（需使用特殊处理）

## 输入

**必要输入**：
- 初始晶体结构（POSCAR格式或pymatgen Structure对象）
- VASP输入文件模板（INCAR, KPOINTS, POTCAR）
- 计算资源（HPC集群或云计算节点）

**可选输入**：
- Hubbard U参数（用于过渡金属氧化物）
- 自旋极化设置
- 光学性质计算开关

**结构要求**：
- 结构已充分弛豫（或使用Materials Project提供的弛豫结构）
- 原子位置合理，无异常键长
- 晶胞大小合适（避免周期性镜像相互作用）

## 输出

**主要输出**：
- VASP输出文件（OUTCAR, OSZICAR, CONTCAR等）
- 总能量、形成能、带隙等能量数据
- 电子结构数据（能带、态密度）
- 光学性质数据（介电函数、吸收系数）

**验证标准**：
- 能量收敛（电子步收敛<1e-4 eV）
- 力收敛（离子步收敛<0.01 eV/Å）
- 与Materials Project数据对比一致

## 流程节点

### Step 1：结构准备
- **操作**：获取或构建初始晶体结构
- **参数**：结构来源（Materials Project/ICSD/实验数据）
- **工具**：pymatgen, MPRester
- **质量门禁**：结构合理，无原子重叠

### Step 2：输入文件生成
- **操作**：生成VASP输入文件（INCAR, KPOINTS, POTCAR）
- **参数**：交换关联泛函（GGA/GGA+U/r2SCAN）、截断能、K点网格
- **工具**：pymatgen VASP input sets, atomate
- **质量门禁**：输入文件格式正确，参数合理

### Step 3：任务提交
- **操作**：将计算任务提交到HPC集群
- **参数**：队列选择、节点数、walltime
- **工具**：SLURM/PBS作业脚本, atomate workflows
- **质量门禁**：任务成功提交，无调度错误

### Step 4：计算监控
- **操作**：监控计算进度和收敛情况
- **参数**：收敛标准、最大电子步/离子步
- **工具**：VASP输出文件解析, 脚本监控
- **质量门禁**：计算正常进行，无发散

### Step 5：结果解析
- **操作**：解析VASP输出文件，提取关键数据
- **参数**：数据提取字段（能量、力、电子结构等）
- **工具**：pymatgen VASP outputs, atomate drones
- **质量门禁**：数据完整，无解析错误

### Step 6：后处理分析
- **操作**：计算衍生性质（形成能、带隙、光学性质等）
- **参数**：分析方法、参考状态
- **工具**：pymatgen analysis modules
- **质量门禁**：结果与文献对比合理

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 交换关联泛函 | GGA/PBE | [1] | Materials Project标准 |
| Hubbard U | 按元素设置 | [1] | 过渡金属氧化物修正 |
| 截断能 | 520 eV | [1] | Materials Project标准 |
| K点密度 | 40 atoms⁻¹ | [1] | 网格密度参数 |
| 电子步收敛 | 1e-4 eV | [1] | 电子结构收敛标准 |
| 离子步收敛 | 0.01 eV/Å | [1] | 离子弛豫收敛标准 |
| 自旋极化 | ON | [1] | 磁性材料计算 |
| 伪势 | PAW | [1] | 投影缀加波方法 |

## 边界与分流

**异常处理**：
- 能量不收敛 → 调整K点网格、增加电子步、检查结构
- 力不收敛 → 减小收敛阈值、检查初始结构
- 计算发散 → 降低截断能、检查输入文件
- 资源不足 → 申请更多节点或减少计算体系

**降级策略**：
- VASP不可用 → 使用Quantum ESPRESSO等替代软件
- 计算成本过高 → 使用机器学习势函数
- 精度要求不高 → 使用半经验方法

## 质量检查

**验证点**：
1. 收敛检查：能量和力达到收敛标准
2. 与Materials Project对比：带隙偏差<0.2eV
3. 物理合理性：能量为负值，带隙在合理范围
4. 数据完整性：所有必需输出文件存在

**失败处理**：
- 收敛失败 → 调整参数重试
- 数据异常 → 检查输入文件和结构
- 资源超限 → 优化计算设置

## 回退策略

**替代方案**：
1. 使用Materials Project预计算数据（如可用）
2. 采用更低精度的计算设置（如减小K点密度）
3. 使用机器学习势函数替代DFT
4. 降级为经验公式估算

## 资源召回建议

**何时召回本卡片**：
- 需要第一性原理精度验证材料性质
- 任务涉及电子结构或光学性质计算
- 需要计算催化反应能垒或吸附能
- 机器学习预测需要DFT验证

**配套资源**：
- matchem-materials-project-data-api（获取初始结构）
- matchem-co2-photocatalysis-ml-model（ML预测对比）
- matchem-data-driven-screening-workflow（筛选工作流）

## 证据来源

[1] Materials Project Documentation - Calculation Details, Materials Project, 2026, https://docs.materialsproject.org/methodology/materials-methodology/calculation-details.md
[2] Materials Project Documentation - Data Workflows, Materials Project, 2026, https://docs.materialsproject.org/data-production/data-workflows.md
[3] Materials Project Documentation - GGA/GGA+U Calculations, Materials Project, 2026, https://docs.materialsproject.org/methodology/materials-methodology/calculation-details/gga+u-calculations.md