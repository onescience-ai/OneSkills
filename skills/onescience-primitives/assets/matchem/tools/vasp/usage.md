# VASP 使用说明

---

## #launch

### 本地或交互式运行

在已安装 VASP 的 HPC 环境中，典型的启动命令为：

```bash
# 使用 MPI 直接运行（适合交互式节点测试）
mpirun -np N vasp_std
```

其中 `N` 为 MPI 进程总数，`vasp_std` 为标准可执行文件。VASP 提供三个主要的可执行文件变体：

| 可执行文件 | 适用场景 |
|-----------|---------|
| `vasp_std` | 标准版，支持任意 k 点网格，适用绝大部分计算 |
| `vasp_gam` | 仅 Gamma 点版本，无复数运算，内存/时间约节省 50%，适用于 Gamma-only 大体系 |
| `vasp_ncl` | 非共线磁性 + 自旋轨道耦合（`LSORBIT=TRUE` 或 `LNONCOLLINEAR=TRUE`） |

### 通过作业调度系统提交

在典型的 SLURM 环境中：

```bash
#!/bin/bash
#SBATCH -J vasp_relax          # 作业名称
#SBATCH -N 1                   # 节点数
#SBATCH --ntasks-per-node=32   # 每节点 MPI 进程数
#SBATCH --cpus-per-task=1      # 每 MPI 进程的 CPU 数
#SBATCH -t 12:00:00            # 运行时限
#SBATCH -p gpu                 # 分区（CPU 或 GPU）
#SBATCH --gres=gpu:4           # GPU 资源申请（GPU 版本需要）

module load vasp/6.4.2         # 加载 VASP 模块
mpirun -np 32 vasp_std > vasp.log
```

### GPU 版本运行

VASP 6.x 提供 GPU 加速版本（CUDA），需使用 `vasp_std` 的 GPU 编译版本：

```bash
#SBATCH --gres=gpu:4
mpirun -np 4 vasp_std          # GPU 版本建议 1 进程/GPU
```

GPU 版本在大体系（> 50 原子）时加速比可达 3–8 倍。

---

## #input_schema

VASP 运行需要 4 个必备输入文件，它们必须位于同一工作目录下：

### 1. INCAR

计算参数控制文件，使用 `TAG = VALUE` 格式。所有参数均可通过该文件设定，未设置参数将使用 VASP 内部默认值。在 `mpirun` 启动目录下，VASP 会自动搜索并读取 INCAR。

**最小 INCAR 示例（结构弛豫）**：
```
SYSTEM = Si bulk relaxation
ENCUT = 520
ISIF = 3
IBRION = 2
EDIFF = 1E-6
EDIFFG = -0.01
ISMEAR = 0
SIGMA = 0.05
NSW = 100
```

### 2. POSCAR

晶体结构定义文件，包含晶格矢量、元素组成和原子位置（分数坐标或笛卡尔坐标）。

**POSCAR 示例（硅原胞，分数坐标）**：
```
Si
1.0
   5.430  0.000  0.000
   0.000  5.430  0.000
   0.000  0.000  5.430
Si
   2
Direct
  0.000  0.000  0.000
  0.250  0.250  0.250
```

### 3. POTCAR

PAW 赝势文件，需按 POSCAR 中元素**顺序**将各元素的 POTCAR 文件拼接。VASP 官方提供标准 POTCAR 库，POTCAR 文件包含元素的赝势信息、截断能推荐值（ENMAX/ENMIN）、价电子数等。

**生成方式**：
- 手动拼接：`cat pot_C/POTCAR pot_Si/POTCAR > POTCAR`
- 使用脚本：VASPKIT 的 `potcar.sh` 或 Pymatgen 的 `generate_potcar()`

**注意**：POTCAR 版本（LDA/PBE/PBEsol 等）必须与 INCAR 中使用的泛函和计算类型一致。

### 4. KPOINTS

布里渊区 k 点采样定义文件。推荐方式是在 INCAR 中设置 `KSPACING`（VASP 5.4+），让程序自动生成 k 点网格，此时 KPOINTS 文件可简化为仅含 `0` 一行。

**自动网格示例**：
```
Automatic mesh
0
Gamma
   6 6 6
   0 0 0
```
此例表示 6×6×6 的 Gamma-centered 网格。

**线模式（能带计算）**：
```
k-points along high symmetry lines
20
line-mode
reciprocal
 0.0 0.0 0.0 ! Gamma
 0.5 0.0 0.0 ! X
```

---

## #runtime_interfaces

### 标准执行

VASP 启动后按以下顺序执行：
1. 读取 INCAR、POSCAR、POTCAR、KPOINTS
2. 若存在 WAVECAR，从中读取波函数作为初始猜测
3. 进行 SCF 迭代直至收敛或达到 NELM
4. 若 NSW > 0，进行离子步更新（IBRION 指定的算法）
5. 输出 OUTCAR、OSZICAR、CONTCAR、CHGCAR 等文件

### 续算功能

WAVECAR 和 CHGCAR 支持续算，此功能对以下场景尤为重要：
- 将粗精度收敛的波函数作为高精度计算的初始猜测
- 电子步未在 NELM 内收敛时，从最新的 WAVECAR 续算
- 从 CHGCAR 读入电荷密度进行非自洽能带/DOS 计算

**启用续算**：
- 保留上一计算的 WAVECAR、CHGCAR 文件，在 INCAR 中设置 `ISTART=1`（读取 WAVECAR）或 `ICHARG=1`（读取 CHGCAR）即可。

### 输出文件

| 文件 | 内容 |
|------|------|
| OUTCAR | 主输出文件，包含能量、力、应力及各项计算细节 |
| OSZICAR | 简化的能量输出，适合快速检查收敛情况 |
| CONTCAR | 优化后的结构，可作为下一计算的 POSCAR |
| CHGCAR | 价电荷密度 + 磁化密度 |
| WAVECAR | Kohn-Sham 波函数（未格式化 Fortran 二进制） |
| vasprun.xml | XML 格式完整输出，供后处理工具（pymatgen、ASE）解析 |
| DOSCAR | 态密度原始数据 |
| EIGENVAL | 本征值数据，可用于能带展开分析 |
| XDATCAR | 分子动力学轨迹文件（NSW > 0 时） |

---

## #execution_resources

### 硬件要求

- **CPU 集群**：VASP 支持纯 CPU 的 MPI 并行，64–256 核为典型使用规模。对于 100 原子的 DFT 计算，32–64 核可满足常规需求。
- **GPU 加速**：VASP 6.x CUDA 版本支持 NVIDIA GPU（推荐 V100/A100/H100），在 50+ 原子体系上可获得 3–8× 加速比。
- **内存**：单核 ~2–8 GB 为典型消耗。GW/RPA 计算因需要大量空带，内存需求显著增加（可达 DFT 的 10 倍以上）。
- **存储**：WAVECAR 文件大小与体系规模成正比，100 原子体系约 100–500 MB，大体系可达数 GB。

### 软件依赖

- **MPI**：Intel MPI、OpenMPI、MPICH 均可
- **数学库**：BLAS/LAPACK/SCALAPACK（部分版本需 ELPA 替代 SCALAPACK 以提升对角化效率）
- **FFT**：FFTW 或 Intel MKL FFTW 接口

### 典型资源申请参考

| 体系规模 | 核数 | 内存/核 | 典型壁钟时间 |
|---------|------|---------|-------------|
| < 50 原子 | 16–32 | 2–4 GB | 0.5–2 小时 |
| 50–200 原子 | 32–128 | 4–8 GB | 2–12 小时 |
| 200–500 原子 | 64–256 | 6–12 GB | 12–48 小时 |
| > 500 原子 | 128–512+ | 8–16 GB | 48 小时+ |

---

## #operation_limits

### 许可证限制

VASP 是**商业软件**，需从维也纳大学购买许可证。主要限制条款：
- 许可证绑定到特定研究组/机构
- 禁止与未经许可的第三方共享 VASP 可执行文件
- 学术许可和工业许可价格差异较大

### 方法学限制

1. **周期性边界条件（PBC）**：VASP 仅支持三维周期性体系。对孤立分子、团簇的计算需要在三个方向设置足够大的真空层（通常 ≥ 10–15 Å）以消除周期性镜像相互作用。若需对非周期性分子进行量子化学计算，Gaussian/ORCA 等使用局域基组的软件可能更合适。

2. **平面波基组限制**：平面波方法对弥散电子态（如里德堡态、低功函数表面）描述效率较低。此外，芯电子的化学位移（NMR）计算需要 PAW 重构，精度略低于全电子方法。

3. **DFT 的固有局限**：作为 DFT 软件，VASP 受限于所选交换关联泛函的精度。半局域泛函（LDA/GGA）对强关联体系（如过渡金属氧化物、稀土材料）的描述通常不准确，需要 DFT+U 或杂化泛函修正。范德华相互作用需显式添加修正项（IVDW）。

4. **体系规模上限**：常规 DFT 计算通常限制在 500–2000 原子。更大体系建议使用机器学习势函数（如 DeepMD、MACE、DPA3）结合经典分子动力学。

### 与其他工具的边界

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 大规模经典 MD（> 10000 原子） | LAMMPS / GROMACS | VASP 的 DFT 开销对如此规模是不可行的 |
| 非周期性分子量子化学 | Gaussian / ORCA / Q-Chem | 局域基组对孤立体系更高效 |
| 高通量 DFT 筛选 | VASP + pymatgen / ASE / atomate / AiiDA | VASP 作为计算引擎，搭配工作流框架 |
| 紧束缚/半经验计算 | DFTB+ / xTB | 计算量远小于 DFT，适合超大规模预筛 |
| 机器学习势训练数据生成 | VASP | VASP 是高精度 DFT 参考数据的黄金标准来源 |
| 力场参数拟合 | VASP + MLIP 框架 | 以 VASP 计算为参考拟合 MLFF |
