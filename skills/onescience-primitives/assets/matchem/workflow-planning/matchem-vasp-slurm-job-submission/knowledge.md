# VASP计算执行流程与SLURM作业提交规范

## 适用范围

**触发条件**：
- 需要执行VASP DFT计算并确保计算任务成功完成
- 需要将VASP计算任务提交到HPC集群
- 需要验证VASP计算输入文件和输出文件

**适用场景**：
- CO2RR吸附能计算
- 催化剂表面反应能垒计算
- 材料电子结构计算
- 需要HPC资源的DFT计算任务

**不适用场景**：
- 本地小规模计算（<100原子）
- 不需要HPC资源的计算
- 使用其他DFT软件（如Quantum ESPRESSO）的场景

## 输入

**必要输入**：
- VASP输入文件（INCAR, KPOINTS, POTCAR, POSCAR）
- HPC集群访问权限
- SLURM作业脚本

**可选输入**：
- 作业提交参数（队列、节点数、walltime）
- 计算监控配置
- 输出文件解析脚本

**结构要求**：
- 输入文件格式正确，无语法错误
- 结构文件（POSCAR）原子位置合理
- POTCAR文件与体系元素匹配

## 输出

**主要输出**：
- VASP输出文件（OUTCAR, OSZICAR, CONTCAR, DOSCAR等）
- 作业状态信息（完成/失败/取消）
- 收敛判断结果
- 提取的能量和力数据

**验证标准**：
- 作业成功提交并完成
- 计算收敛（SCF收敛、离子步收敛）
- 输出文件完整且可解析

## 流程节点

### Step 1：输入文件校验
- **操作**：检查VASP输入文件的完整性和正确性
- **参数**：文件格式、参数合理性、结构完整性
- **工具**：pymatgen VASP input set检查、自定义验证脚本
- **质量门禁**：所有输入文件存在且格式正确
- **关键检查点**：
  1. INCAR文件：参数设置合理，无重复定义
  2. KPOINTS文件：K点网格密度适当
  3. POTCAR文件：伪势与体系元素匹配
  4. POSCAR文件：原子位置合理，无异常键长

### Step 2：SLURM作业脚本编写
- **操作**：创建SLURM作业提交脚本
- **参数**：队列选择、节点数、walltime、内存请求
- **工具**：文本编辑器、模板生成
- **质量门禁**：作业脚本语法正确，参数合理
- **关键参数**：
  ```
  #!/bin/bash
  #SBATCH --job-name=vasp_calc
  #SBATCH --partition=normal
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=32
  #SBATCH --time=24:00:00
  #SBATCH --mem=64G
  #SBATCH --output=vasp_%j.out
  #SBATCH --error=vasp_%j.err
  
  module load vasp/6.3.0
  mpirun vasp_std
  ```

### Step 3：任务提交
- **操作**：将作业提交到SLURM调度系统
- **参数**：作业脚本路径、资源请求
- **工具**：sbatch命令
- **质量门禁**：作业成功提交，获得作业ID
- **提交命令**：`sbatch job_script.sh`
- **验证**：检查作业状态 `squeue -j <job_id>`

### Step 4：计算监控
- **操作**：监控计算进度和收敛情况
- **参数**：检查频率、告警阈值
- **工具**：squeue、sacct、自定义监控脚本
- **质量门禁**：计算正常进行，无发散或挂起
- **监控命令**：
  1. `squeue -j <job_id>` - 查看作业状态
  2. `tail -f vasp_<job_id>.out` - 实时查看输出
  3. `grep "SCF" OSZICAR` - 检查SCF收敛

### Step 5：输出文件解析
- **操作**：解析VASP输出文件，提取关键数据
- **参数**：数据提取字段（能量、力、电子结构等）
- **工具**：pymatgen VASP outputs、自定义解析脚本
- **质量门禁**：数据完整，无解析错误
- **关键输出文件**：
  1. OUTCAR：总能量、力、应力、收敛信息
  2. OSZICAR：SCF收敛过程、电子步信息
  3. CONTCAR：弛豫后的结构
  4. DOSCAR：态密度数据

### Step 6：收敛判断
- **操作**：判断计算是否收敛
- **参数**：收敛标准（电子步、离子步）
- **工具**：解析OUTCAR中的收敛信息
- **质量门禁**：计算收敛，数据可靠
- **收敛标准**：
  1. 电子步收敛：能量变化 < 1e-4 eV
  2. 离子步收敛：力 < 0.01 eV/Å
  3. 应力收敛：应力变化 < 1e-3 eV/Å³

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 电子步收敛标准 | 1e-4 eV | [1] | SCF收敛标准 |
| 离子步收敛标准 | 0.01 eV/Å | [1] | 结构弛豫收敛 |
| 截断能 | 520 eV | [2] | 平面波基组截断 |
| K点密度 | 40 atoms⁻¹ | [2] | 网格密度参数 |
| 伪势 | PAW | [1] | 投影缀加波方法 |
| 交换关联泛函 | GGA/PBE | [2] | Materials Project标准 |
| Hubbard U | 按元素设置 | [2] | 过渡金属氧化物修正 |
| 自旋极化 | ON/OFF | [1] | 磁性材料计算 |

## 边界与分流

**异常处理**：
- 作业提交失败 → 检查队列状态、资源限制、脚本语法
- 计算不收敛 → 调整K点网格、增加电子步、检查结构
- 计算发散 → 降低截断能、检查输入文件
- 资源不足 → 申请更多节点或减少计算体系
- 输出文件损坏 → 重新提交计算或检查存储空间

**降级策略**：
- VASP不可用 → 使用Quantum ESPRESSO等替代软件
- 计算成本过高 → 使用机器学习势函数
- 精度要求不高 → 使用半经验方法
- HPC资源紧张 → 调整walltime或队列

## 质量检查

**验证点**：
1. 输入文件校验：所有文件存在且格式正确
2. 作业提交验证：作业成功提交，获得作业ID
3. 计算收敛验证：能量和力达到收敛标准
4. 输出文件验证：所有必需输出文件存在且完整
5. 数据提取验证：提取的数据与预期一致

**失败处理**：
- 输入文件错误 → 修正后重新提交
- 作业失败 → 检查错误日志，调整参数重试
- 计算不收敛 → 调整计算设置，重新计算
- 数据异常 → 检查输入文件和结构

## 回退策略

**替代方案**：
1. 使用Materials Project预计算数据（如可用）
2. 采用更低精度的计算设置（如减小K点密度）
3. 使用机器学习势函数替代DFT
4. 降级为经验公式估算

## 资源召回建议

**何时召回本卡片**：
- 需要执行VASP DFT计算并提交到HPC集群
- 需要验证VASP计算输入文件和输出文件
- 需要监控计算进度和收敛情况
- 需要解析VASP输出文件并提取数据

**配套资源**：
- matchem-vasp-dft-workflow（VASP计算工作流）
- matchem-data-driven-screening-workflow（数据驱动筛选工作流）
- matchem-co2-photocatalysis-ml-model（CO2光催化ML模型）

## 证据来源

[1] VASP Manual - Vienna Ab initio Simulation Package, VASP Software, 2026, https://www.vasp.at/wiki/index.php/The_VASP_Manual
[2] Materials Project - VASP Calculation Details, Materials Project, 2026, https://docs.materialsproject.org/methodology/materials-methodology/calculation-details.md
[3] SLURM Workload Manager Documentation, SchedMD, 2026, https://slurm.schedmd.com/documentation.html