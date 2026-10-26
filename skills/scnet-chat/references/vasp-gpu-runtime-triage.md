# VASP on SCNet DCU(GPU) 运行时排障 Playbook

> 适用范围:SCNet(scnet-infinity,海光 DCU/ROCm 栈)上 VASP **运行时/环境层**的崩溃、挂死与资源拒绝。
> 建模门限类失败(ENCUT/K 点/结构合理性)见 `onescience-dft-model-gate/references/failure_playbook.md`,本文件只管"跑不起来/跑起来就崩"。

## 0. 两条门禁铁律

1. **先跑极简对照,再分支修复。**
   任何 `ZPOTRF` / `ZHEGV` / `Orbital orthonormalization failed`,先提交一个"注定健康"的对照:
   2 原子 bulk Si(金刚石)、`ENCUT=520`、`ISMEAR=0 SIGMA=0.05`、`LREAL=.FALSE.`、`NSW=0`、Gamma `6 6 6`。
   用它把病因二分为「库/构建/平台坏」vs「体系病态」。**禁止**在真实体系上扫 INCAR/赝势/DTK 组合——失败结果不含信息量。
2. **分层归因,不跨层下结论。**
   启动层(命令/动态库/MPI)→ 资源层(内存配额/设备分配)→ 数值层(求解器)。
   先看退出码类别与 `OSZICAR` 是否为空,确认程序真的进入执行后,才解读其内部报错。

## 1. 启动层剥洋葱清单(实测顺序与修复)

| 症状 | 根因 | 修复 |
|---|---|---|
| `ExitCode 127:0` + `Elapsed 00:00:00` | batch 环境无 `mpirun` / 二进制不在 PATH | 改 `srun -n 1 <全路径 vasp_std>`,或 source 正确 env.sh |
| `error while loading shared libraries: libomp.so` | DTK 的 llvm lib 不在 `LD_LIBRARY_PATH` | 前置 `$DTK/llvm/lib`(及 `llvm/lib/clang/*/lib/linux/x86_64`) |
| `libamd_comgr.so ... cannot open shared object` | ROCm comgr 目录缺失 | 前置 `$DTK/lib`(或 comgr 所在目录) |
| `MPI_Init_thread failed ... MPIDI_OFI_mpi_init_hook` + SIGSEGV(174) | Intel MPI 在 `srun` 下初始化 OFI/libfabric 失败 | 单节点加 `export I_MPI_FABRICS=shm` |
| `HIP ERROR: Error code = 100` | 在**登录节点**直接跑 GPU-only 二进制(无设备) | 红鲱鱼;必须提交到计算节点,登录节点结果无效 |
| `Out Of Memory` / `oom_kill` | 队列按 **每 CPU** 授内存(`DefMemPerCPU`),1 CPU 仅 ~3.8G | **删掉 `--mem`**,改 `-c 8`(配额=8×3800MB≈30G);勿写 `--mem=32G` 配 1 CPU(提交端直接拒绝) |

预检三件套:
```bash
ldd $(which vasp_std) 2>&1 | grep -i "not found"          # 缺哪些 .so
scontrol show partition <q> | grep -iE "MaxMemPerCPU|DefMemPerCPU"   # 内存策略
scontrol show node <n>     | grep -iE "RealMemory|AllocMem|FreeMem"  # 物理内存(区分策略 vs 硬件)
```

## 2. 日志命名随提交通路变化(易误判)

- 登录节点直接 `sbatch` → slurm 原生 `slurm-<jobid>.out`。
- 走 scnet-chat REST API(`scripts/job.py --submit`)→ `std.out.<jobid>` / `std.err.<jobid>`。
- 按其中一种命名去 grep 另一种通路的产物会得到空输出,被误读成"作业没跑出结果"。**先 `ls -la` 确认真实文件名。**

## 3. 数值层判读

- **健康 Si 对照也报** `LAPACK: Routine ZPOTRF failed! kpoint: 2 spin: 1`,且 `OSZICAR/CHG/CHGCAR/WAVECAR` 全 0 字节(死在首正交化、未进任何 SCF)→
  **平台 GPU 稠密 LAPACK(rocSOLVER)缺陷**,不是体系病态、不是单节点硬件。**不要改输入**,转第 5 节升级/兜底。
- **对照收敛、仅真实体系报同类错** → 体系病态,走 failure_playbook 的输入修法(ENCUT↑、K_pv、`LREAL=.FALSE.`、换 PAW 等)。

## 4. 已排除矩阵(SCNet hx1hdnormal01,2026-10 实测)

| 构建 | DTK 运行时 | 关键 env | 结果 |
|---|---|---|---|
| v2 `allSol++`(build 2026-07) | 25.04.1 | 默认 | ZPOTRF kpoint2 spin1(节点 a01r3n07) |
| v2 `allSol++` | 25.04.1 | +`HSA_FORCE_FINE_GRAIN_PCIE=1`、`ulimit -s unlimited`、`NCCL_IB_HCA` | ZPOTRF(节点 a01r3n03)→ fine-grain 假设死 |
| 旧 `cpvasp`(build 2024-11) | 26.04(env.sh 硬编码,23.10 已下架) | 默认 | 挂死 rocFFT/HIP,10min 超时,拆栈 SIGSEGV |
| 旧 `cpvasp` | 26.04 | +fine-grain | 待测(v9b) |
| 旧 `cpvasp` | 24.04.2(现存最老) | 默认 | 待测 |
| 历史 job 749842 | 当年 | `case/vasp.sh` | **numactl permission denied,非成功参照** |

结论:跨 ≥3 节点、2 构建、≥2 个 DTK、±fine-grain 全败 → **平台级 GPU 栈缺陷**,非单节点/单构建/单个 env 旋钮可修。

## 5. 升级与兜底(干净 BLOCKED 规范)

- 报 SCNet 支持时附:对照输入全文 + 逐字报错 + 第 4 节矩阵 + 明确诉求
  (提供 host-LAPACK/CPU-MKL 构建,或恢复历史可用构建/DTK 组合)。
- 兜底顺序:① host-LAPACK 重编;② CPU 分区;③ NVIDIA 分区;④ 换 QE/CP2K。
- **禁止**在未取得成功参照时自动生成"看似合理"的结果;应输出干净 BLOCKED + 证据矩阵 + 升级建议。

## 6. DCU 必备环境(启动层修好后仍建议保留)

```bash
ulimit -s unlimited
export HSA_ENABLE_SDMA=0
export I_MPI_FABRICS=shm            # 单节点单进程,绕开 OFI/libfabric
export HSA_FORCE_FINE_GRAIN_PCIE=1  # 海光 DCU 宿主-设备一致性(官方脚本携带)
export NCCL_IB_HCA="shca_1_0"
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK   # 与 -c 对齐
```
