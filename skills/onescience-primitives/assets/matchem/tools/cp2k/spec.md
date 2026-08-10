# software_overview
CP2K 是面向大体系量子化学和分子动力学的开源模拟软件包。其核心设计理念是将高效 DFT 计算（通过 Quickstep 模块）与经典/第一性原理 MD 深度整合，使数千原子的体系可在 DFT 精度级别下进行从头算分子动力学（AIMD）模拟。

软件定位：

- 输入对象：嵌套层次化的文本输入文件，由 `&SECTION ... &END SECTION` 结构组织。
- 核心模块：Quickstep（电子结构计算）、FIST（经典力场 MD）、QM/MM（混合量子/经典计算）。
- 关键原理：混合 Gaussian 与平面波（GPW/GAPW）方法、DBCSR 稀疏矩阵代数、OT（Orbital Transformation）与 DA（Direct All-atom）自洽场求解。
- 基础文件：输入脚本（`.inp`）、基组文件（`BASIS_SET`）、赝势文件（`POTENTIAL`/`GTH_POTENTIALS`）、坐标文件（`.xyz`/`.pdb`）。

# core_concepts

## GPW 方法（Gaussian and Plane Waves）
CP2K 标志性方法，将 Gaussian 型原子轨道用于描述波函数（保留 Kohn-Sham 矩阵的稀疏性），同时利用平面波辅助基组展开电子密度。相比纯平面波方法（如 VASP），GPW 可大幅降低大体系 DFT 的标度，使数千原子的计算变得可行。GAPW（Gaussian and Augmented Plane Waves）是 GPW 的扩展，通过引入 augmented 区域处理全电子计算。

典型配置位于 `&DFT` 段内：
- `QS/METHOD GPW`：选择 GPW 方法。
- `MGRID/CUTOFF`：控制平面波展开的截断能（单位 Ry），典型值 200–600 Ry。
- `MGRID/REL_CUTOFF`：相对截断能（单位 Ry），典型值 40–60 Ry，控制多极展开与映射精度。

## DBCSR 稀疏矩阵
CP2K 使用 Distributed Block Compressed Sparse Row（DBCSR）格式存储和操作 Kohn-Sham 矩阵，利用大体系下矩阵的天然稀疏性。DBCSR 将矩阵按块划分并分配给 MPI 进程，大幅降低内存和通信开销。影响 DBCSR 行为的参数主要在 `&GLOBAL` 段：
- `PREFERRED_DIAG_LIBRARY SL`：选择 ScaLAPACK 对角化库（小体系）。
- `PREFERRED_DIAG_LIBRARY ELPA`：选择 ELPA 对角化库（大体系/多节点推荐）。
- `EPS_DEFAULT`：矩阵过滤阈值，低于此值的矩阵元被忽略，直接影响稀疏度与精度。

## Quickstep 模块
cp2k 的 DFT 核心引擎，实现 GPW/GAPW 方法。关键子段：
- `&QS`：Quickstep 方法设置，指定 METHOD（GPW/LRIGPW 等）、EXTRAPOLATION（波函数外推）和 EPS_DEFAULT。
- `&SCF`：自洽场收敛控制，含 MAX_SCF（最大迭代步数）、EPS_SCF（收敛判据）、OT（Orbital Transformation 求解器）或 DIAGONALIZATION、MIXING 策略。
- `&XC` + `&XC_FUNCTIONAL`：交换关联泛函选择（PBE、BLYP、B3LYP 等）及 vdW 修正（D3/D4/DFT-D3(BJ)）。
- `&MGRID`：实空间格点截断控制。

## OT 与对角化
CP2K 支持两种 SCF 求解策略：
- **传统对角化**：适用于气相分子和小体系（< 100 原子），使用 ScaLAPACK 或 ELPA。
- **Orbital Transformation（OT）**：适用于大体系（> 100 原子）、带隙体系，通过直接最小化能量泛函替代对角化，标度更优且收敛更稳定。使用 OT 时需设置 `&SCF/OT` 子段（MINIMIZER、PRECONDITIONER、ENERGY_GAP 等）。

## QM/MM
CP2K 原生支持 QM/MM 混合计算，通过 `&QMMM` 段将体系划分为 QM 区域（高精度 DFT/半经验）和 MM 区域（经典力场）。关键参数：
- `&QMMM/CELL`、`&QMMM/MM_KIND`、`&QMMM/LINK`：定义 QM/MM 分区和链接原子。
- 力场通过 `&MM` 段配合 `&FORCE_EVAL/METHOD FIST` 定义。

## 增强采样
CP2K 内置 metadynamics（Well-Tempered、Multi-Walker）和 umbrella sampling 等增强采样方法，通过 `&FREE_ENERGY` 段控制。关键参数：
- `METHOD METADYN` 或 `METHOD UMBRELLA`。
- `&METADYN/COLVAR`：定义集合变量（CV），如距离、角度、配位数。
- `&METADYN/HILLS`：设置山高（`HEIGHT`）、山宽（`SCALE`）和步长（`DELTA_T` for well-tempered）。

# common_workflows

## 结构优化（Geometry Optimization）
目标：寻找势能面上的极小值点（稳定构型/过渡态初始猜测）。

典型输入结构：
```
&GLOBAL
  PROJECT my_opt
  RUN_TYPE GEO_OPT
&END GLOBAL
&FORCE_EVAL
  METHOD Quickstep
  &DFT
    BASIS_SET_FILE_NAME BASIS_SET
    POTENTIAL_FILE_NAME POTENTIAL
    &MGRID CUTOFF 400 REL_CUTOFF 50 &END MGRID
    &SCF MAX_SCF 50 EPS_SCF 1.0E-6 &OT ... &END OT &END SCF
    &XC &XC_FUNCTIONAL PBE &END XC_FUNCTIONAL &END XC
  &END DFT
  &SUBSYS
    &CELL ABC 10.0 10.0 10.0 &END CELL
    &COORD ... &END COORD
    &KIND H BASIS_SET DZVP-MOLOPT-GTH POTENTIAL GTH-PBE &END KIND
  &END SUBSYS
&END FORCE_EVAL
&MOTION
  &GEO_OPT
    TYPE MINIMIZATION
    MAX_ITER 200
    OPTIMIZER BFGS
  &END GEO_OPT
&END MOTION
```

关键点：
- `RUN_TYPE GEO_OPT`：声明运行类型为几何优化。
- `OPTIMIZER BFGS`/`CG`/`LBFGS`：优化算法选择；BFGS 是默认且最常用的。
- `MAX_DR`、`MAX_FORCE`、`RMS_DR`、`RMS_FORCE`：收敛判据。

## 从头算分子动力学（AIMD / BOMD）
目标：在 DFT 精度下模拟原子核的经典运动轨迹。

典型输入结构：
```
&GLOBAL
  PROJECT my_aimd
  RUN_TYPE MD
&END GLOBAL
&MOTION
  &MD
    ENSEMBLE NVT
    STEPS 10000
    TIMESTEP 0.5          ! fs
    TEMPERATURE 300.0     ! K
    &THERMOSTAT
      TYPE CSVR
      &CSVR TIMECON 100 &END CSVR
    &END THERMOSTAT
  &END MD
&END MOTION
```

关键点：
- `ENSEMBLE NVE`/`NVT`/`NPT`/`NVT_ADIABATIC`。
- `TIMESTEP` 单位飞秒（fs），对 H 含体系通常 0.5–1.0 fs。
- BCWF 波函数外推（`&MD/EXTRA_EXTRA_LAST` 或 `&QS/EXTRAPOLATION`）可显著减少每步 SCF 迭代。

## 过渡态搜索（NEB / DIMER）
目标：定位反应路径上的鞍点（过渡态）。

- NEB (Nudged Elastic Band)：需准备初始态和终态结构，CP2K 在中间自动插值。
  - `RUN_TYPE BAND` 在 `&GLOBAL`。
  - `&BAND/NPROC_REP 8`：使用 8 个副本并行计算。
  - `&BAND/BAND_TYPE CI-NEB`：使用 Climbing Image NEB。
- DIMER：仅需一个初始猜测，适合鞍点局部搜索。
  - `RUN_TYPE GEO_OPT` + `&MOTION/GEO_OPT/TYPE TRANSITION_STATE` + `&MOTION/GEO_OPT/&DIMER ... &END DIMER`。

## 振动分析与光谱
目标：计算简正模式频率、IR/Raman 强度。

- `RUN_TYPE VIBRATIONAL_ANALYSIS` 或 `RUN_TYPE NORMAL_MODES`。
- `&VIBRATIONAL_ANALYSIS` 段控制位移步长和模式计算。
- IR 强度通过 Born 有效电荷（`&PROPERTIES/&LINRES`）或 dipole 数值微分获得。
- Raman 强度需 `&PROPERTIES/&POLARIZABILITY` 或使用有限差分 Raman 模块。

## metadynamics 自由能面计算
目标：通过增强采样重建高维自由能面。

关键配置：
```
&FREE_ENERGY
  METHOD METADYN
  &METADYN
    DO_HILLS .TRUE.
    ! Well-Tempered Metadynamics
    WW 1.0
    &METAVAR
      WIDTH 0.05
      SCALE 0.5
      COLVAR 1
    &END METAVAR
  &END METADYN
&END FREE_ENERGY
```
配合 `&MOTION/MD` 运行，`&COLVAR` 定义集合变量，`&SUBSYS/&COLVAR` 定义 CV 的原子组合。

# key_parameters

## &GLOBAL 段
| 参数 | 说明 | 典型值 |
|------|------|--------|
| `PROJECT` | 项目名，输出文件前缀 | 自定义 |
| `RUN_TYPE` | 运行类型 | `ENERGY` / `ENERGY_FORCE` / `GEO_OPT` / `MD` / `BAND` / `VIBRATIONAL_ANALYSIS` / `NONE` |
| `PRINT_LEVEL` | 输出详细程度 | `LOW` / `MEDIUM` / `HIGH` |
| `PREFERRED_DIAG_LIBRARY` | 对角化库 | `SL` (ScaLAPACK) / `ELPA` |
| `PREFERRED_FFT_LIBRARY` | FFT 库 | `FFTW3` |

## &FORCE_EVAL 段
| 参数 | 说明 | 典型值 |
|------|------|--------|
| `METHOD` | 力评估方法 | `Quickstep` (DFT) / `FIST` (MM) / `QMMM` / `MIXED` |
| `STRESS_TENSOR` | 是否计算应力 | `ANALYTICAL` / `NUMERICAL` / `NONE` |

### &DFT 子段
| 参数 | 说明 | 典型值 |
|------|------|--------|
| `BASIS_SET_FILE_NAME` | 基组文件路径 | `BASIS_SET` |
| `POTENTIAL_FILE_NAME` | 赝势文件路径 | `POTENTIAL` / `GTH_POTENTIALS` |
| `CHARGE` | 体系总电荷 | 整数 |
| `MULTIPLICITY` | 自旋多重度 | `1` (单重态), `2` (二重态) |
| `UKS` | 非限制 Kohn-Sham | `.TRUE.` / `.FALSE.` |
| `MGRID/CUTOFF` | 平面波截断能 (Ry) | `300`–`600` |
| `MGRID/REL_CUTOFF` | 相对截断能 (Ry) | `40`–`60` |
| `SCF/MAX_SCF` | SCF 最大迭代步数 | `50`–`200` |
| `SCF/EPS_SCF` | SCF 收敛判据 (a.u.) | `1.0E-6`–`1.0E-7` |
| `SCF/OT/MINIMIZER` | OT 最小化器 | `CG` / `DIIS` / `BROYDEN` |
| `SCF/OT/PRECONDITIONER` | OT 预条件子 | `FULL_ALL` / `FULL_SINGLE_INVERSE` / `FULL_KINETIC` |
| `SCF/OT/ENERGY_GAP` | 带隙预条件子参数 (a.u.) | `0.1`–`0.2` |
| `QS/METHOD` | Quickstep 方法 | `GPW` / `GAPW` / `LRIGPW` |
| `QS/EPS_DEFAULT` | 默认数值精度 (a.u.) | `1.0E-10`–`1.0E-14` |
| `QS/EXTRAPOLATION` | 波函数外推 | `ASPC` / `PS` / `LINEAR_PS` |
| `XC/XC_FUNCTIONAL` | 交换关联泛函 | `PBE` / `BLYP` / `B3LYP` / `HSE06` / `PBE0` |
| `XC/VDW_POTENTIAL` | vdW 修正 | `PAIR_POTENTIAL` 等 |
| `XC/VDW_POTENTIAL/&PAIR_POTENTIAL/TYPE` | vdW 类型 | `DFTD3` / `DFTD3(BJ)` / `DFTD4` |

### &SUBSYS 子段
| 参数 | 说明 |
|------|------|
| `&CELL` | 晶胞参数（`ABC`、`ALPHA_BETA_GAMMA`）或 `&CELL_REF` |
| `&COORD` | 原子坐标（格式：元素名 x y z） |
| `&KIND` | 元素种类定义，含 `BASIS_SET`、`POTENTIAL`、`MAGNETIZATION` 等 |
| `&TOPOLOGY` | 分子拓扑（用于力场计算） |

## &MOTION 段
| 参数 | 说明 | 典型值 |
|------|------|--------|
| `&GEO_OPT/TYPE` | 优化类型 | `MINIMIZATION` / `TRANSITION_STATE` |
| `&GEO_OPT/MAX_ITER` | 最大优化步数 | `200`–`500` |
| `&GEO_OPT/OPTIMIZER` | 优化算法 | `BFGS` / `CG` / `LBFGS` |
| `&GEO_OPT/MAX_DR` | 最大位移收敛判据 (Bohr) | `3.0E-3` |
| `&GEO_OPT/MAX_FORCE` | 最大力收敛判据 (a.u.) | `4.5E-4` |
| `&MD/ENSEMBLE` | 系综 | `NVE` / `NVT` / `NPT` / `NVT_ADIABATIC` |
| `&MD/STEPS` | MD 步数 | `1000`–`1000000` |
| `&MD/TIMESTEP` | 时间步长 (fs) | `0.5` |
| `&MD/TEMPERATURE` | 目标温度 (K) | `300.0` |

# input_file_hierarchy
CP2K 输入文件使用严格的嵌套 `&SECTION ... &END SECTION` 结构，允许通过 `@INCLUDE` 或 `@SET` 指令引入外部文件和变量。

顶层结构：
```
&GLOBAL          ! 项目名、运行类型
&FORCE_EVAL      ! 方法和体系定义（可重复多次用于混合方法）
  METHOD ...
  &DFT ... &END DFT
  &MM ... &END MM
  &SUBSYS
    &CELL ... &END CELL
    &COORD ... &END COORD
    &KIND ... &END KIND
    &TOPOLOGY ... &END TOPOLOGY
  &END SUBSYS
  &PRINT ... &END PRINT
&END FORCE_EVAL

&MOTION          ! 几何优化 / MD / NEB 等控制
  &GEO_OPT ... &END GEO_OPT
  &MD ... &END MD
  &BAND ... &END BAND
  &PRINT ... &END PRINT
&END MOTION

&VIBRATIONAL_ANALYSIS ... &END VIBRATIONAL_ANALYSIS  ! 振动分析（独立）
&FREE_ENERGY ... &END FREE_ENERGY                    ! 自由能计算（独立，通常配合 MD）
```

`@SET` 变量替换示例：
```
@SET CUTOFF 400
&FORCE_EVAL
  &DFT
    &MGRID
      CUTOFF ${CUTOFF}
    &END MGRID
  &END DFT
&END FORCE_EVAL
```

`@INCLUDE` 文件包含：
```
@INCLUDE 'common_settings.inc'
```

# common_pitfalls

1. **截断能不足导致 Eggbox 效应**：平面波截断能（`CUTOFF`）或相对截断能（`REL_CUTOFF`）设置过低时，随原子移动会出现能量不连续震荡（Eggbox 效应）。对 AIMD 和几何优化，建议 `CUTOFF >= 400 Ry`，`REL_CUTOFF >= 50 Ry`，并进行收敛性测试。

2. **OT 方法对金属体系不适用**：Orbital Transformation 方法依赖带隙进行预条件，对金属体系（零带隙）收敛困难或发散。金属体系应使用传统对角化（`&SCF` 下不设 `&OT`）并启用 smearing（`&SCF/ADDED_MOS` 和 `&SCF/SMEAR`）。

3. **基组/赝势文件路径错误**：CP2K 默认在运行目录查找 `BASIS_SET` 和 `POTENTIAL`（或 `GTH_POTENTIALS`），路径错误导致 `KIND` 段无法匹配基组。可通过环境变量 `CP2K_DATA_DIR` 或绝对路径解决。

4. **MD 时间步长过大引起能量漂移**：含 H 原子体系 AIMD 时间步长不应超过 1.0 fs，建议 0.5 fs；重元素体系可适当放宽至 1.0–2.0 fs。能量漂移测试是验证时间步长合理性的基本手段。

5. **WFN 外推设置不当**：AIMD 中未启用波函数外推（`QS/EXTRAPOLATION ASPC`）会导致每步 SCF 迭代数过高（10–20+），显著增加计算开销。正确的外推策略可将 SCF 迭代降至 3–6 步。

6. **SCF 收敛失败的原因排查**：
   - 初始猜测不合理：使用 `&SCF/SCF_GUESS RESTART` 从之前的波函数重启。
   - 带隙预条件子 `ENERGY_GAP` 设置不当：金属体系应使用对角化替代 OT。
   - `MIXING` 参数不适合：尝试调整 `ALPHA`（默认 0.4–0.6）或使用 `BROYDEN_MIXING`。
   - 自旋极化设置遗漏：开壳层体系需 `UKS .TRUE.` 和正确 `MULTIPLICITY`。

7. **NEB 收敛困难**：CI-NEB 可能卡在中间路径，常见对策包括：(a) 增加图像数量（`NUMBER_OF_REPLICA`），(b) 先对所有图像做单独优化再启动 NEB，(c) 降低弹簧常数（`K_SPRING`），(d) 改用 DIMER 方法精确定位鞍点。

8. **并行效率低下**：大体系 DFT 计算在多节点运行时，若 `PREFERRED_DIAG_LIBRARY` 仍使用 SL（ScaLAPACK），对角化会成为瓶颈。切换至 ELPA 可大幅改善万原子级体系的墙钟时间。同时注意 MPI 进程数应与体系大小匹配，过多进程增加通信开销。

# hpc_considerations

## MPI 并行
CP2K 主要通过 MPI 进行分布式内存并行，支持：
- **进程网格**：通过 `-np` 指定总 MPI 进程数。可结合 `mpiexec` / `mpirun` / `srun` 启动。
- **混合并行**：支持 MPI+OpenMP 混合模式，通过 `OMP_NUM_THREADS` 控制每进程内线程数。
- **负载均衡**：COORD 数据、DBCSR 矩阵块、FFT 格点分发到 MPI 进程。

典型 Slurm 作业脚本：
```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=2
export OMP_NUM_THREADS=2
mpiexec -np 128 cp2k.psmp input.inp > output.out
```

## GPU 加速
CP2K 支持通过 DBCSR、COSMA（矩阵乘法）和 grid 相关子程序使用 GPU 加速：
- 编译时启用 `-D__DBCSR_ACC -D__ACC` 和相关 CUDA/HIP 后端。
- `cp2k.popt`（纯 MPI）vs `cp2k.psmp`（MPI+OpenMP）vs GPU 版本（如 `cp2k.psmp_cuda`）。
- GPU 加速受益最大的场景：大基组 DFT 计算，特别是 DBCSR 稀疏矩阵乘法和 FFT 格点操作。

## 文件 I/O 与存储
- 波函数文件（`.wfn`）动辄数 GB 至数十 GB，建议使用高速并行文件系统（如 Lustre、GPFS）。
- `&GLOBAL/WFN_RESTART_FILE_NAME` 指定波函数重启文件。
- 大 MD 轨迹建议周期性保存 restart（`&MD/&PRINT/&RESTART`），避免从头重启的巨大计算开销。
- 可通过 `&MOTION/&PRINT/&TRAJECTORY` 控制轨迹输出频率（`EACH/MD 10` 表示每 10 步输出一次）。

## 资源估算
- **内存**：
  - 小体系（<100 原子）：每 MPI 进程 1–4 GB。
  - 中等体系（100–1000 原子）：每 MPI 进程 4–16 GB。
  - 大体系（>1000 原子）：每 MPI 进程 16–64 GB，建议配合 DBCSR 和 ELPA。
- **计算时间**：
  - 单点能计算：数秒（小体系）到数分钟（大体系）。
  - 几何优化：根据体系大小和收敛路径，数十步到数百步 SCF。
  - AIMD：每步 10–60 秒（随体系和并行规模变化），10000 步可能需要数天。
- **扩展性**：CP2K 在数百至数千核心上表现出良好扩展性，具体取决于体系大小和 FFT/对角化算法选择。
