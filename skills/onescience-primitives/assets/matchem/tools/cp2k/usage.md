# launch
CP2K 通过命令行启动，输入文件为主要配置入口。基本启动方式：

## 本地/工作站运行
```sh
# 串行运行
cp2k.sopt input.inp > output.out

# MPI 并行运行（4 进程）
mpiexec -np 4 cp2k.popt input.inp > output.out

# MPI+OpenMP 混合并行（每节点 16 进程，每进程 2 线程）
export OMP_NUM_THREADS=2
mpiexec -np 16 cp2k.psmp input.inp > output.out
```

可执行文件命名约定：
- `cp2k.sopt`：串行单线程版本。
- `cp2k.popt`：纯 MPI 版本。
- `cp2k.psmp`：MPI+OpenMP 混合版本。
- `cp2k.psmp_cuda` / `cp2k.psmp_hip`：GPU 加速版本。

## HPC 集群 Slurm 提交
典型 Slurm 作业提交脚本（`submit_cp2k.sh`）：
```sh
#!/bin/bash
#SBATCH --job-name=cp2k_aimd
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=2
#SBATCH --time=48:00:00
#SBATCH --partition=normal
#SBATCH --output=cp2k_%j.out
#SBATCH --error=cp2k_%j.err

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

mpiexec -np $((SLURM_NNODES * SLURM_NTASKS_PER_NODE)) \
  cp2k.psmp input.inp > output.log
```
提交：`sbatch submit_cp2k.sh`

## 输入文件准备
最低可运行 CP2K 输入文件结构：
- 必须包含 `&GLOBAL` 段（`PROJECT`、`RUN_TYPE`）。
- 必须包含 `&FORCE_EVAL` 段（至少包含 `METHOD Quickstep`、`&DFT`、`&SUBSYS` 及坐标、基组信息）。
- 必须提供基组文件（`BASIS_SET`）和赝势文件（`POTENTIAL` 或 `GTH_POTENTIALS`），默认在运行目录或 `CP2K_DATA_DIR` 路径下查找。

## 常用环境变量
| 变量 | 说明 |
|------|------|
| `CP2K_DATA_DIR` | CP2K 数据文件目录（含基组、赝势文件） |
| `OMP_NUM_THREADS` | OpenMP 线程数 |
| `OMP_STACKSIZE` | OpenMP 栈大小，大体系建议 `512M` 或更高 |

# input_schema
CP2K 输入文件（`.inp`）使用 `&SECTION ... &END SECTION` 的嵌套层次结构。参数值按以下规则书写：

- 关键字大小写不敏感，值大小写通常不敏感。
- 逻辑值：`.TRUE.` / `.FALSE.`、`ON` / `OFF`、`YES` / `NO`。
- 字符串值：单引号或双引号包裹，或不含特殊字符时直接书写。
- 整数值/浮点值：直接书写。
- 注释以 `!` 开头至行尾。

## 核心输入段结构

```
&GLOBAL
  PROJECT <name>             ! 输出文件前缀
  RUN_TYPE <type>            ! 运行类型
  PRINT_LEVEL <level>        ! 输出级别
&END GLOBAL

&FORCE_EVAL                  ! 可重复多次（混合方法）
  METHOD <method>            ! Quickstep / FIST / QMMM / MIXED
  &DFT
    BASIS_SET_FILE_NAME <file>
    POTENTIAL_FILE_NAME <file>
    &MGRID
      CUTOFF <real>          ! 平面波截断能 (Ry)
      REL_CUTOFF <real>      ! 相对截断能 (Ry)
    &END MGRID
    &QS
      METHOD GPW
      EPS_DEFAULT <real>     ! 默认数值精度
    &END QS
    &SCF
      MAX_SCF <int>          ! 最大 SCF 步数
      EPS_SCF <real>         ! SCF 收敛判据
      &OT ... &END OT        ! (大体系) 或去掉 OT 用对角化
    &END SCF
    &XC
      &XC_FUNCTIONAL <name> &END XC_FUNCTIONAL
    &END XC
  &END DFT
  &SUBSYS
    &CELL ABC <a> <b> <c> &END CELL
    &COORD
      <element> <x> <y> <z>
    &END COORD
    &KIND <element>
      BASIS_SET <name>
      POTENTIAL <name>
    &END KIND
  &END SUBSYS
&END FORCE_EVAL

&MOTION                      ! 可选，几何优化/MD/NEB
  &GEO_OPT ... &END GEO_OPT
  &MD ... &END MD
  &BAND ... &END BAND
&END MOTION
```

## 外部文件引用
- 输入文件不可直接包含分子坐标文件，坐标必须内嵌在 `&COORD` 段中。
- 可通过 `@SET VAR VALUE` 定义变量，`${VAR}` 引用。
- 可通过 `@INCLUDE 'filename'` 引入外部输入片段。

## 数据文件
CP2K 官方提供以下数据文件（位于 `CP2K_DATA_DIR`）：
- `BASIS_SET`：基组定义，含 `DZVP-MOLOPT-SR-GTH`、`TZVP-MOLOPT-GTH`、`TZV2P-MOLOPT-GTH` 等。
- `POTENTIAL` / `GTH_POTENTIALS`：Goedecker-Teter-Hutter（GTH）赝势参数。
- `dftd3.dat`：DFT-D3 色散修正参数。
- `dftd4.dat`：DFT-D4 色散修正参数。

基组选择原则：
- 单点能/快速测试：`DZVP-MOLOPT-SR-GTH`（双ζ 价层 + 极化，短程变体）。
- 生产级计算：`TZVP-MOLOPT-GTH` / `TZV2P-MOLOPT-GTH`（三ζ 价层 + 极化）。
- 高精度 benchmark：`TZV2PX-MOLOPT-GTH` 或更大基组。

# runtime_interfaces

## 主要可执行文件
| 文件 | 说明 | 适用场景 |
|------|------|----------|
| `cp2k.sopt` | 串行版本 | 小体系测试、输入文件语法检查 |
| `cp2k.popt` | 纯 MPI 版本 | 中大规模 MPI 并行 |
| `cp2k.psmp` | MPI+OpenMP 混合版本 | 大体系高性能计算 |
| `cp2k.psmp_cuda` | GPU 加速版本 | 含 GPU 节点的 HPC 集群 |

## 输出文件
| 扩展名/文件 | 说明 |
|-------------|------|
| `.out` | 主输出文件（标准输出重定向），含能量、力、SCF 收敛历程 |
| `*-1.restart` / `*-1.restart.bak` | 波函数重启文件（二进制） |
| `*.wfn` | 波函数文件 |
| `*-pos-1.xyz` | 几何优化/MD 轨迹文件 |
| `*-1.ener` | 能量文件 |

## 重启与续算
- 波函数重启：`&DFT/SCF/SCF_GUESS RESTART` + `&GLOBAL/WFN_RESTART_FILE_NAME <file>`。
- 几何优化重启：先前运行的 `*-1.restart` 文件存在时，`RUN_TYPE GEO_OPT` 会自动检测并继续。
- MD 重启：前一次运行的 restart 文件存在时自动检测并继续。

## 作业状态检查
- 标准输出中搜索 `SCF run converged` 确认 SCF 收敛。
- `ENERGY| Total FORCE_EVAL` 行提供体系总能量。
- `MAX F` 和 `RMS F` 行提供力收敛状态。
- `GEOMETRY OPTIMIZATION COMPLETED` 确认优化完成。

# execution_resources

## 计算资源需求
| 体系规模 | 推荐资源 | 备注 |
|----------|----------|------|
| < 50 原子（小分子） | 1–4 核，1–4 GB/核 | 串行或小规模 MPI 即可 |
| 50–200 原子（中等） | 4–32 核，2–8 GB/核 | 纯 MPI 或混合模式 |
| 200–1000 原子（大） | 32–256 核，4–16 GB/核 | 建议 ELPA + OT 方法 |
| > 1000 原子（超大） | 128–1024+ 核，8–64 GB/核 | 必须使用 ELPA + OT，考虑 GPU 加速 |

## 硬件要求
- **CPU**：支持 AVX2/AVX-512 指令集的 x86_64 处理器可获得最佳性能。ARM（如鲲鹏）需特定编译。
- **内存**：与原子数、基组大小近似线性关系，与 MPI 进程数反比。
- **存储**：波函数文件和 restart 文件占用较大空间（>1000 原子波函数可达数十 GB），需快速并行文件系统。
- **GPU**：NVIDIA GPU（CUDA）或 AMD GPU（HIP），主要用于 DBCSR 矩阵乘法和 COSMA 库。

## 软件依赖
- MPI 库（OpenMPI / MPICH / Intel MPI）。
- 数学库：BLAS/LAPACK、ScaLAPACK、ELPA（推荐）、FFTW3。
- 可选库：libint（HF 交换）、libxc（扩展泛函）、COSMA（GPU 矩阵乘法）、libvdwxc（vdW 泛函）。

# operation_limits
- 使用 OT 方法时体系必须有非零带隙（绝缘体/半导体），金属体系应使用对角化 + smearing。
- `CUTOFF` 和 `REL_CUTOFF` 必须进行收敛性测试，默认值通常不足以得到可靠结果。
- 基组文件必须为 CP2K 格式，不能直接使用 Gaussian 或 ORCA 格式基组。
- 赝势文件必须与基组配套（通常 GTH 赝势配 MOLOPT 基组）。
- AIMD 中 H 含原子的时间步长不超过 1.0 fs（推荐 0.5 fs），否则能量严重漂移。
- 混合泛函（如 HSE06、PBE0）在小体系可行，但标度比纯 GGA 高 1–2 个数量级，大体系应谨慎使用。
- QM/MM 计算要求用户手动定义 QM/MM 边界和链接原子（LINK），无自动分区功能。
- NEB 过渡态搜索需要输入初始态和终态几何，且两个构型的原子顺序和数量必须一致。
- metadynamics 的自由能面收敛取决于 CV 选择和山参数，不当选择可能导致不收敛或错误的能面。
