# VASP 技术规格说明

---

## #software_overview

VASP（Vienna Ab initio Simulation Package）是由维也纳大学开发的第一性原理电子结构计算与量子力学-分子动力学模拟商业软件包。其核心方法为基于平面波基组的密度泛函理论（DFT），结合投影缀加平面波（PAW）赝势处理电子-离子相互作用。VASP 支持多种交换关联泛函（LDA、PBE、PBEsol、SCAN、HSE06、PBE0 等），并可通过 IVDW 标签引入 van der Waals 修正（DFT-D2/D3、TS、MBD 等）。除 DFT 外，VASP 也支持 Hartree-Fock（HF）、GW 近似、随机相位近似（RPA）以及 Bethe-Salpeter 方程（BSE）等更高阶方法。

核心计算能力包括：结构弛豫与离子位置优化、电子自洽场（SCF）计算、电子态密度（DOS）与能带结构、Born-Oppenheimer 分子动力学（BOMD）、过渡态搜索（NEB/CI-NEB/Dimer）、声子谱计算（有限位移法/DFPT）、光学与介电性质、力学性质（弹性常数）、STM 图像模拟、NMR 化学位移、电子局域化函数（ELF）分析等。

VASP 是 HPC 领域最广泛使用的 DFT 软件之一，其高效并行策略（NCORE/KPAR/NGZ）和成熟的 PAW 赝势库使其在大规模周期性体系计算中具有显著优势。目前最新稳定版本为 6.x 系列。

---

## #core_concepts

### 平面波基组与截断能（ENCUT）

VASP 采用周期性边界条件下的平面波基组展开 Kohn-Sham 波函数。平面波的数量由截断能 ENCUT 控制，它定义了动能上限 $E_{cut} = \\hbar^2|\\mathbf{G}|^2/(2m_e)$。典型 ENCUT 取值范围为 400–600 eV，具体取决于体系中包含的元素及 PAW 赝势的推荐值。VASP 官方推荐 ENCUT 至少为 POTCAR 中 ENMAX 的 1.3 倍（这也是 VASP 的默认行为——当 ENCUT 未显式设置时）。若要计算应力张量或弹性常数，建议 ENCUT 取 ENMAX 的 1.5 倍或更高，以抑制 Pulay 应力。

### PAW 赝势

投影缀加平面波（PAW）方法是 VASP 处理芯电子与价电子之间相互作用的核心技术。PAW 赝势将真实的全电子波函数与平滑的赝波函数线性映射，在截断半径内保留节点结构，从而兼顾计算效率与精度。VASP 提供多套 PAW 赝势库：标准版、GW 版、半芯态版（_sv / _pv）等。POTCAR 文件推荐的最低版本需与计算类型匹配（例如 PBE 计算使用 PBE 版本的 POTCAR，GW 计算使用包含更多投影通道的 GW POTCAR）。

### k 点采样

VASP 通过 KPOINTS 文件定义第一布里渊区内的 k 点网格。常用方式：
- **Monkhorst-Pack（MP）网格**：对周期性体系最常用的均匀网格采样，适合三维周期性晶体。通过 `KSPACING` 参数（0.1–0.5 Å⁻¹，典型值 0.2–0.3）自动生成网格是 VASP 5.4+ 推荐的现代做法。
- **Gamma-centered 网格**：用于表面、二维材料或 Wigner-Seitz 半径较大的体系，将 Gamma 点作为网格中心。
- **线模式 k 路径**：用于能带结构计算，需要提供高对称点间的 k 点连线。

总能量对 k 点采样收敛的判断标准：能量差 < 1 meV/atom 即可认为收敛。

### SCF 迭代过程

自洽场（SCF）迭代是 VASP 求解 Kohn-Sham 方程的核心循环：构建初始电荷密度 → 求解 Kohn-Sham 方程 → 计算新电荷密度 → 混合新旧电荷密度 → 判断收敛。关键收敛控制参数：
- **EDIFF**：全局能量收敛标准，取值通常在 10⁻⁵–10⁻⁷ eV。对结构弛豫要求较高的计算（如声子谱），需取 10⁻⁷–10⁻⁸。
- **NELM**：最大电子步迭代次数，默认 60。对带隙较小或金属体系可能需要增大至 100–200。
- **NELMIN**：最小电子步数，默认 0（VASP 5.x）/ 2（VASP 6.x）。
- **混合方案**：ALGO 控制电荷密度混合策略——Normal（Kerker 混合，默认）、Fast（更激进的混合）、VeryFast、All（原子轨道线性组合方法）、Damped 等。对难收敛体系（如过渡金属氧化物、磁矩翻转），可换用 AMIX/BMIX 手动控制线性混合参数。

### 结构优化（ISIF / IBRION）

结构优化分为离子位置弛豫和晶胞参数优化：
- **IBRION**：控制离子更新算法。`IBRION=1` 为 RMM-DIIS（准牛顿法，最快收敛），`IBRION=2` 为共轭梯度法（更稳健，默认推荐），`IBRION=3` 为阻尼分子动力学（适合远离平衡态的结构）。
- **ISIF**：控制弛豫自由度。`ISIF=2` 仅弛豫离子位置（固定晶胞），`ISIF=3` 同时弛豫离子位置、晶胞形状和体积，`ISIF=4` 弛豫离子位置和晶胞形状但固定体积。
- **EDIFFG**：力收敛标准。正值表示以能量为收敛判据（eV），负值表示以力为收敛判据（eV/Å）。典型值 `EDIFFG=-0.01`（0.01 eV/Å）即可获得可靠结构，声子谱计算建议 `EDIFFG=-0.001` 或更低。
- **NSW**：最大离子步数，典型值 50–200。

建议流程：先用 `ISIF=3, IBRION=2` 优化晶胞和原子位置，再用 `ISIF=2, IBRION=2` 在固定晶胞下精修原子位置。

### 展宽方法（ISMEAR / SIGMA）

对于金属或窄带隙体系，Kohn-Sham 轨道在费米面附近的占据数需要使用展宽（smearing）平滑处理：
- **ISMEAR=0**：Methfessel-Paxton（MP）方法，一阶展宽。适合金属体系，可得到准确的能量和力。需配合合适的 SIGMA（0.05–0.2 eV）。
- **ISMEAR=1**：MP 方法的高斯展宽极限。
- **ISMEAR=-1**：Fermi-Dirac 展宽，模拟有限温度电子占据，适合金属分子动力学。
- **ISMEAR=-5**：四面体方法（Blöchl 修正），适合半导体和绝缘体的静态总能量和 DOS 计算。**这是能带结构/态密度计算的首选**，不引入任何展宽误差，但不适用于结构弛豫（会导致力不准确）。
- **ISMEAR=-4**：四面体方法（无 Blöchl 修正），已较少使用。

σ 值经验选取：
- 半导体/绝缘体（`ISMEAR=-5`）：SIGMA 设置无实际影响，通常取 0.05。
- 金属（`ISMEAR=0/1`）：SIGMA = 0.1–0.2 eV，越大收敛越快但引入更大的展宽误差。通常用 `SIGMA=0.1` 作为安全起步值。

### 自旋极化与磁性

通过 `ISPIN=2` 开启自旋极化计算，可获取磁矩信息。`MAGMOM` 标签设置初始磁矩，`LNONCOLLINEAR=TRUE` 开启非共线磁性（含自旋-轨道耦合，需配合 `LSORBIT=TRUE`）。

---

## #common_workflows

### 工作流 1：结构弛豫（Structure Relaxation）

**目标**：获得体系的基态几何结构。

**推荐参数**：
```
ENCUT = 520           # 或 POTCAR ENMAX 的 1.3 倍
ISIF = 3              # 全自由度优化
IBRION = 2            # 共轭梯度
EDIFF = 1E-6          # 电子步收敛标准
EDIFFG = -0.01        # 力收敛标准 0.01 eV/Å
ISMEAR = 0 (金属) / -5 (绝缘体，但对力不准，可先 MP 弛豫再四面体)
SIGMA = 0.05
NSW = 100
```

**流程说明**：
1. 先用 `ISMEAR=0, SIGMA=0.1` 进行粗精度弛豫（EDIFF=1E-5）
2. 再用 `ISMEAR=-5` (或对金属用 `ISMEAR=0, SIGMA=0.05`) 进行精精度弛豫（EDIFF=1E-7, EDIFFG=-0.005）
3. 对于晶胞变化敏感的体系（如相变研究），建议多步弛豫：先 `ISIF=2` 松弛离子，再 `ISIF=3` 优化晶胞，最后 `ISIF=2` 精修离子

### 工作流 2：静态自洽计算（Static SCF）

**目标**：在弛豫后的结构上计算精确的电荷密度和总能量。

**推荐参数**：
```
ENCUT = 520
ISIF = 2              # 不弛豫
NSW = 0               # 不移动离子
IBRION = -1           # 不进行离子更新
EDIFF = 1E-7
ISMEAR = -5           # 四面体方法
LORBIT = 11           # 输出原子投影态密度
LCHARG = T            # 保存 CHGCAR
LWAVE = T             # 保存 WAVECAR
```

### 工作流 3：态密度（DOS）计算

**目标**：计算电子态密度。

**推荐参数**：
```
ICHARG = 11           # 从 CHGCAR 读取电荷密度进行非自洽计算
ISMEAR = -5           # 四面体方法，对 DOS 最准确
LORBIT = 11           # 输出分轨道投影 DOS
NEDOS = 2000          # DOS 的能量网格点数
EMIN / EMAX           # 能量范围
```

**流程说明**：
1. 完成静态 SCF 计算（生成 CHGCAR）
2. 使用更密集的 k 点网格（通常为 SCF 的 2–3 倍）进行非自洽 DOS 计算
3. 使用 VASPKIT (`task 111` 或 `511`) 或 pymatgen 提取 PDOS

### 工作流 4：能带结构（Band Structure）

**目标**：计算电子能带沿高对称 k 路径的色散关系。

**流程说明**：
1. 完成静态 SCF 计算（生成 CHGCAR）
2. 确定高对称 k 点路径（推荐使用 SeeK-path、AFLOW 或 VASPKIT 的 `task 302` 自动生成）
3. 修改 KPOINTS 为线模式（每段 20–40 个 k 点），设置 `ICHARG=11` 进行非自洽能带计算
4. 使用 VASPKIT (`task 211`) 或 sumo/pymatgen 绘制能带图并标注高对称点

**KPOINTS 线模式示例**：
```
k-points along high symmetry lines
20
line-mode
reciprocal
 0.0 0.0 0.0 ! Γ
 0.5 0.0 0.0 ! X
 0.5 0.0 0.0 ! X
 0.5 0.5 0.0 ! M
 0.5 0.5 0.0 ! M
 0.0 0.0 0.0 ! Γ
```

### 工作流 5：过渡态搜索（NEB / CI-NEB）

**目标**：找到最小能量路径（MEP）和鞍点。

**推荐参数**：
```
IMAGES = 5-9          # 中间镜像数
SPRING = -5           # 弹簧常数，负值表示使用 NEB 默认值
ICHAIN = 0            # 标准 NEB，ICHAIN=1 为 CI-NEB
IOPT = 1              # 离子更新使用 LBFGS（推荐）
EDIFFG = -0.02        # 对过渡态可稍宽松
```

**流程说明**：
1. 分别弛豫初态（IS）和末态（FS）结构
2. 使用 `nebmake.pl`（VASP VTST 工具）或 pymatgen 线性插值生成中间镜像
3. 先跑标准 NEB（`ICHAIN=0`），收敛后再跑 CI-NEB（`ICHAIN=1`）精确定位鞍点
4. 使用 VTST 脚本 `nebbarrier.pl` 分析能垒

---

## #key_parameters

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| **ENCUT** | 平面波截断能 (eV) | 400–600 | 默认取 POTCAR ENMAX 的 1.3 倍；应力计算建议 1.5 倍 |
| **ISIF** | 自由度控制 | 2 / 3 / 4 | 2=仅弛豫离子，3=弛豫离子+晶胞+体积，4=弛豫离子+晶胞(固定体积) |
| **IBRION** | 离子更新算法 | -1 / 1 / 2 / 3 | -1=不移动，1=RMM-DIIS，2=Conjugate Gradient（默认推荐），3=Damped MD |
| **ISMEAR** | 占据数展宽方法 | -5 / 0 / 1 | -5=四面体(半导体DOS首选)，0=MP(金属弛豫推荐)，1=MP with Gaussian |
| **SIGMA** | 展宽宽度 (eV) | 0.05–0.2 | 金属取 0.1–0.2，该值越大收敛越快但引入误差越大 |
| **EDIFF** | 电子步能量收敛标准 (eV) | 1E-5 ~ 1E-7 | 一般弛豫取 1E-5~1E-6，声子计算建议 1E-7~1E-8 |
| **EDIFFG** | 离子步收敛标准 | -0.01 ~ -0.001 | 负值表示力判据 (eV/Å)，正值表示能量判据 (eV) |
| **NSW** | 最大离子步数 | 50–200 | 见 ISIF/IBRION |
| **NELM** | 最大电子步数 | 60–200 | 金属/难收敛体系建议 100+ |
| **NELMIN** | 最小电子步数 | 2–5 | 防止假收敛 |
| **KSPACING** | k 点间距 (Å⁻¹) | 0.1–0.5 | VASP 5.4+ 推荐方式，替代手动 KPOINTS 网格 |
| **NCORE** | 单 k 点内部并行核数 | ~4 | 控制 bands 对角化并行度 |
| **KPAR** | k 点并行组数 | =总核数/(NCORE) | 跨 k 点并行，需 ≤ k 点数量 |
| **ALGO** | 电子步算法 | Normal / Fast / VeryFast | Normal 最稳健，Fast 对大部分体系更快 |
| **LREAL** | 实空间投影 | Auto / T / F | Auto 自动选择，大体系 T 可加速 |
| **PREC** | 精度等级 | Normal / Accurate / High | Accurate 增大 FFT 网格，力更准确 |
| **ADDGRID** | 附加支持网格 | .TRUE. | 增强数值精度（增加约 20% 计算量） |
| **IVDW** | van der Waals 修正 | 11 / 12 / 21 / 202 | 11=DFT-D3(Zero)，12=DFT-D3(BJ)，21=TS，202=MBD |
| **LOPTICS** | 光学计算开关 | .TRUE. | 计算介电函数，需配合 CSHIFT |

---

## #input_files

### INCAR — 计算参数控制文件

INCAR 是 VASP 计算的主控制文件，采用 `TAG = VALUE` 的 Fortran 风格键值对格式。除少数必备标签外，大多数参数均有合理默认值。在结构优化中，`ISIF`、`IBRION`、`EDIFF`、`EDIFFG`、`NSW` 是最关键的几个设置。对静态计算，`NSW=0`、`IBRION=-1` 冻结离子位置。

### POSCAR — 晶体结构文件

POSCAR 定义晶体结构和原子位置：

```
System Name
1.0                    # 全局缩放因子
a11 a12 a13            # 晶格矢量 a
a21 a22 a23            # 晶格矢量 b
a31 a32 a33            # 晶格矢量 c
Element1 Element2 ...  # 元素符号（VASP 5.1+）
N1 N2 ...              # 各元素原子数
Selective dynamics     # （可选）选择性动力学
Cartesian / Direct     # 坐标类型
x1 y1 z1 [T T T]       # 原子坐标（及可选动力学标志）
```

支持分数坐标（Direct）和笛卡尔坐标（Cartesian）。VASP 5.x+ 建议在 POTCAR 前添加元素符号行。

### POTCAR — 赝势文件

POTCAR 包含每种元素的 PAW 赝势数据，需要按 POSCAR 中元素顺序将对应的原子 POTCAR 文件拼接。推荐使用 `potcar.sh`（来自 VASPKIT）或 `generate_potcar()`（pymatgen）自动生成。**POTCAR 版本必须与计算所用的泛函一致**（例如 PBE 泛函 → PBE 赝势，不能混用 LDA 赝势）。

常用赝势类型：
- `_GW`：适用于 GW/BSE 计算，包含更多投影通道
- `_sv / _pv`：半芯态赝势，处理外层半芯态为价电子
- 标准版：不带后缀，适合常规 DFT

### KPOINTS — k 点网格文件

定义布里渊区积分用 k 点：
- **自动网格模式**：提供网格维度和偏移（Monkhorst-Pack 或 Gamma-centered）
- **线模式**：用于能带结构计算
- **显式列表模式**：提供所有 k 点及权重

VASP 5.4+ 推荐在 INCAR 中设置 `KSPACING` 参数，让 VASP 根据倒格矢自动生成合适的 k 点网格，此时 KPOINTS 文件只需包含一行 `0`（表示自动模式）。

### WAVECAR / CHGCAR — 续算文件

- **WAVECAR**：存储 Kohn-Sham 波函数，可用于续算和能带展开分析。设置 `LWAVE = .TRUE.` 保存。
- **CHGCAR**：存储价电荷密度和磁化密度，可用于 DOS/能带非自洽计算（`ICHARG=11`）及 NEB 初猜。设置 `LCHARGE = .TRUE.` 或 `LCHARG = .TRUE.` 保存。与 WAVECAR 不同，CHGCAR 支持通过 `ICHARG=11` 方式续算而不需保留完整波函数。
- **CHG**：精简版电荷密度文件，仅存储价电荷密度。

---

## #common_pitfalls

1. **Pulay 应力问题**：当 ENCUT 不够高时，晶胞体积优化会引入虚假的 "Pulay 应力"（基组不完整导致的应力误差），导致晶格常数偏低。缓解措施：取 ENCUT ≥ ENMAX × 1.5，或在每个体积点使用相同 ENCUT 做 E-V 曲线拟合（BM-EOS）。

2. **金属体系的展宽选择不当**：
   - 半导体/绝缘体：使用 `ISMEAR=0` 或 `ISMEAR=1` 会导致占据数非整数的物理错误，总能量和力都会失准。结构弛豫后务必换用 `ISMEAR=-5` 进行精确能量计算。
   - 金属体系：使用 `ISMEAR=-5` 会导致严重的数值不稳定和收敛失败。必须使用 MP 或 FD 展宽。

3. **POTCAR 版本与泛函不匹配**：使用 PBE 泛函计算时，若 POTCAR 是 LDA 版本，结果无物理意义。VASP 虽然会给出警告但不会拒绝运行。务必显式检查 POTCAR 文件头部 `LEXCH` 标签。

4. **能带计算忘记 SCF 前序步骤**：能带结构需在高对称 k 路径上做非自洽计算（`ICHARG=11`），不能直接从随机初始电荷密度开始。必须先完成静态 SCF 生成收敛的 CHGCAR。

5. **声子计算精度不足**：声子频率对力的精度极其敏感。有限位移法（phonopy + VASP）建议 `EDIFF=1E-8`, `EDIFFG=-1E-4`, `ENCUT` 取 ENMAX 的 1.5 倍，并使用 `ADDGRID=.TRUE.` 增强数值精度。DFPT 方法（`IBRION=7` 或 `8`）对超胞大小要求更严格。

6. **k 点收敛未做系统测试**：不要仅凭经验设 k 点密度。应针对目标体系做 k 点收敛测试：逐步增大 k 点网格，当总能量变化 < 1 meV/atom 时认为收敛。

7. **NCORE/KPAR 设置不当导致性能低下**：`KPAR` 必须能整除 k 点总数，否则浪费计算资源。`NCORE` 应设置为每个计算节点的物理核心数（而非线程数）。`NCORE × KPAR = 总 MPI 进程数` 且 `KPAR ≤ k 点数`。

8. **DFT+U 计算中的元稳定态**：使用 `LDAU=.TRUE.` 时，不同的初始磁矩配置可能收敛到不同的电子态。务必对磁矩初猜 `MAGMOM` 做敏感性测试。

---

## #hpc_considerations

### 并行策略

VASP 使用三层 MPI 并行：
- **跨 k 点并行（KPAR）**：最有效的并行层，几乎线性 scaling。将 k 点分配给不同 MPI 通信组。
- **bands 对角化并行（NCORE）**：对单个 k 点内的 bands 进行并行化，scaling 效率次之。
- **FFT 并行（NGX/NGY/NGZ）**：对平面波 FFT 网格分解，通常由 VASP 自动优化。

推荐配置：`NCORE ≈ 4-8`（取决于节点架构），`KPAR` 尽可能大（≤ k 点数量且能整除 k 点数），NCORE × KPAR = 总核数。

### 内存需求

VASP 的内存消耗主要取决于：
- 平面波数量（∝ ENCUT × 体积）
- 能带数（∝ 电子数 × 2，含空带因子 NBANDS）
- k 点数（每个 KPAR 组内独立）
- FFT 网格尺寸

典型内存：普通 100 原子体系 ~ 2–8 GB/core。GW 和 RPA 计算因需要大量非占据轨道，内存需求可达到 DFT 的 10–50 倍。

### 低精度预优化策略

大规模体系（> 200 原子）建议采用多级精度策略：
1. **粗算**：ENCUT=350, KSPACING=0.5, EDIFF=1E-4, ISMEAR=0/SIGMA=0.2
2. **中等**：ENCUT=450, KSPACING=0.3, EDIFF=1E-5, ISMEAR=0/SIGMA=0.1
3. **精算**：ENCUT=550, KSPACING=0.2, EDIFF=1E-6, ISMEAR=-5, ADDGRID=T

### 作业调度

VASP 在典型 SLURM 调度系统上的提交示例：

```bash
#!/bin/bash
#SBATCH -J vasp_job
#SBATCH -N 2                 # 2 个节点
#SBATCH --ntasks-per-node=32 # 每节点 32 核
#SBATCH --cpus-per-task=1
#SBATCH -t 24:00:00

mpirun -np 64 vasp_std
```

注意：`vasp_std`（标准版）、`vasp_gam`（仅 Gamma 点）、`vasp_ncl`（非共线磁性+自旋轨道耦合）三个可执行文件分别对应不同物理场景，Gamma-only 计算用 `vasp_gam` 可节省约 50% 的时间和内存。

---

## #source_references

- [VASP 官方 Wiki 主页](https://vasp.at/wiki/index.php/The_VASP_Manual)
- [INCAR 参数列表](https://vasp.at/wiki/index.php/Category:INCAR_tag)
- [POTCAR 赝势库说明](https://vasp.at/wiki/index.php/Available_PAW_potentials)
- [KPOINTS 说明](https://vasp.at/wiki/index.php/KPOINTS)
- [结构优化策略](https://vasp.at/wiki/index.php/Structure_optimization)
- [能带结构计算](https://vasp.at/wiki/index.php/Band_structure_using_hybrid_functionals)
- [NEB 过渡态搜索](https://vasp.at/wiki/index.php/Transition_state_using_the_Nudged_Elastic_Band_method)
- [并行效率调优](https://vasp.at/wiki/index.php/Parallelization)
- [VASPKIT 后处理工具](https://vaspkit.com/)
- [Phonopy + VASP 声子谱计算](https://phonopy.github.io/phonopy/vasp.html)
