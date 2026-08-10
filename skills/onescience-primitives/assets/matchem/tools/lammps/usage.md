# launch
LAMMPS 通过命令行启动，输入为脚本文件（in 文件）：

## 串行运行
```sh
lmp_serial -in input.in -log log.lammps
```

## MPI 并行运行（最常用）
```sh
mpirun -np 4 lmp_mpi -in input.in -log log.lammps
```

## MPI+OpenMP 混合并行
```sh
export OMP_NUM_THREADS=4
mpirun -np 8 lmp_mpi -in input.in -log log.lammps
```

## SLURM 作业提交
```sh
#!/bin/bash
#SBATCH -J lammps_job
#SBATCH -N 2
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH -t 24:00:00

module load lammps/2023
mpirun lmp_mpi -in input.in -log log.lammps
```

## GPU 加速运行（KOKKOS 包）
```sh
mpirun -np 4 lmp_kokkos_cuda -k on g 1 -sf kk -in input.in -log log.lammps
```
- `-k on g 1`：启用 KOKKOS，每 MPI 进程使用 1 个 GPU
- `-sf kk`：自动将支持的 pair_style/fix 替换为 KOKKOS 版本

## 命令行参数
| 参数 | 说明 |
|------|------|
| `-in filename` | 输入脚本文件（必需） |
| `-log filename` | 日志输出文件（默认 log.lammps） |
| `-screen filename` | 屏幕输出重定向文件 |
| `-echo style` | 回显模式（none/screen/log/both） |
| `-var name value` | 定义输入脚本变量 |
| `-partition NxM` | 将处理器划分为多个分区 |
| `-restart filename` | 从重启文件恢复 |
| `-r2data filename` | 从重启文件生成 data 文件 |

## 脚本分区运行
```sh
mpirun -np 16 lmp_mpi -partition 8x2 -in input.in
```
- 将 16 个处理器分为 8 个分区，每分区 2 核，每个分区独立运行输入脚本

# input_schema
LAMMPS 的输入由 in 脚本文件定义，核心输入流程图：

```
in 脚本文件 (.in)
  │
  ├── 第 1 部分：初始化
  │   ├── units metal|real|si|cgs|electron|lj
  │   ├── dimension 2|3
  │   ├── boundary p|s|f|m p|s|f|m p|s|f|m
  │   ├── atom_style atomic|charge|full|molecular|...
  │   └── newton on|off
  │
  ├── 第 2 部分：原子定义
  │   ├── lattice <style> <a0> [orient] [spacing]
  │   ├── region <id> block|sphere|cylinder|...
  │   ├── create_box <N> <region>
  │   ├── create_atoms <type> region|random|...
  │   ├── mass <type> <value>
  │   └── read_data <filename>     ← 或直接从 data 文件读取
  │
  ├── 第 3 部分：力场与系综设置
  │   ├── pair_style <style> [args]
  │   ├── pair_coeff <I> <J> [args]
  │   ├── kspace_style <style> <precision>
  │   ├── bond_style / angle_style / dihedral_style / improper_style
  │   ├── fix <id> <group> <style> [args]
  │   ├── compute <id> <group> <style> [args]
  │   ├── dump <id> <group> <style> <N> <filename> [fields...]
  │   └── neigh_modify <keyword> <value>
  │
  └── 第 4 部分：运行控制
      ├── timestep <dt>
      ├── thermo <N>
      ├── thermo_style custom|one|multi <fields...>
      ├── run <Nsteps>
      └── write_restart <filename>
```

## data 文件结构（read_data）
```
LAMMPS data file header

<Natoms> atoms
<Nbonds> bonds
<Nangles> angles
<AtomTypes> atom types
<BondTypes> bond types

0.0 <xhi> xlo xhi
0.0 <yhi> ylo yhi
0.0 <zhi> zlo zhi

Masses

1 <mass1>
2 <mass2>
...

Atoms

<id> <mol> <type> <x> <y> <z>
...
```

# runtime_interfaces
## 核心命令接口
| 命令 | 接口说明 | 参数说明 |
|------|---------|---------|
| `units` | 设置单位系统 | metal/real/si/cgs/electron/lj |
| `dimension` | 设置模拟维度 | 2（二维）或 3（三维） |
| `boundary` | 设置边界条件 | p(周期)/s(缩放)/f(固定)/m(最小) |
| `atom_style` | 设置原子属性集 | atomic/charge/full/molecular/sphere |
| `lattice` | 定义晶体点阵 | 点阵类型 + 晶格常数 |
| `create_atoms` | 创建原子 | 类型 + 区域/随机方式 |
| `pair_style` | 选择对势类型 | 力场名 + 参数 |
| `pair_coeff` | 设置对势参数 | 原子对 I J + 参数 |
| `kspace_style` | 设置长程静电 | pppm/ewald + 精度 |
| `fix nvt` | Nose-Hoover 恒温器 | temp Tstart Tstop Tdamp |
| `fix npt` | 恒温恒压 | temp + pressure 参数 |
| `fix nve` | 微正则系综 | 无额外参数 |
| `fix deform` | 形变控制 | 方向 + 形变模式 + 速率 |
| `fix ave/time` | 时间平均 | 采样参数 + 输出文件 |
| `compute` | 计算物理量 | 计算类型 + 参数 |
| `dump` | 轨迹输出 | 输出间隔 + 格式 + 字段 |
| `thermo` | 热力学输出 | 输出频率（步数） |
| `thermo_style` | 热力学内容 | custom + 输出字段列表 |
| `timestep` | 积分步长 | 时间步长（fs 或 ps，取决于 units） |
| `run` | 运行步数 | 模拟步数 |
| `minimize` | 能量最小化 | 能量容限 + 力容限 + 最大迭代 + 最大评估次数 |
| `velocity create` | 初始化速度 | 温度 + 随机种子 + 分布类型 |
| `neigh_modify` | 近邻列表参数 | delay/every/check 等 |
| `write_restart` | 输出重启文件 | 文件名 |
| `read_restart` | 读取重启文件 | 文件名 |
| `write_data` | 输出 data 文件 | 文件名 |

## 变量和循环控制
```lammps
variable i loop 1 10                # 循环变量
variable T equal 300                 # 等式变量
variable a index 4.0 4.1 4.2 4.3   # 索引变量

label loop
  lattice fcc $a                     # 引用变量
  ...
next i                               # 循环迭代
jump SELF loop                       # 跳转
```

# main_functions
LAMMPS 输入脚本中的核心功能命令：

- `pair_style` / `pair_coeff`：力场定义
- `fix`：系综控制、约束、外场施加
- `compute`：物理量计算（热力学、结构、动力学）
- `dump`：原子轨迹和属性输出
- `run`：模拟运行
- `minimize`：能量最小化/结构弛豫
- `velocity`：速度初始化

# execution_resources
## 计算资源配置建议
| 体系规模 | 势函数类型 | 推荐配置 | 预期性能 |
|---------|----------|---------|---------|
| < 10,000 原子 | LJ/EAM | 1-4 MPI 进程 | ~ns/day |
| 10,000-100,000 原子 | LJ/EAM | 4-32 MPI 进程 | ~ns/day |
| 100,000-1,000,000 原子 | LJ/EAM | 32-256 MPI 进程 | ~0.1-1 ns/day |
| > 1,000,000 原子 | LJ/EAM | 256-1024+ MPI 进程 | ~0.01-0.1 ns/day |
| 任意规模 | ReaxFF | 上述进程数 × 2-10 | 显著更慢 |
| 任意规模 | MLIAP（MACE/DeepMD） | 上述进程数 + GPU | 取决于模型复杂度 |

## 内存需求
- 主要受原子数、势函数复杂度（近邻数、描述符维度）和轨迹输出影响
- EAM 势函数：约 1-2 KB/原子
- ReaxFF：约 10-50 KB/原子
- MLIAP + MACE：取决于网络规模，显著增加

## 磁盘存储
- 轨迹文件（dump）：约 30-100 bytes/原子/帧（取决于输出字段）
- 建议压缩策略：使用 `dump custom` + 精简字段；后处理压缩
- 生产运行建议使用 restart 文件作为断点续传点

# operation_limits
## 功能边界
- LAMMPS 不处理电子结构，不能替代 DFT 计算
- 经典 MD 结果受限于力场精度（经验势无法描述电子激发、电荷转移等）
- 时间尺度限制：MD 通常模拟 ns-μs 尺度，无法直接模拟秒级以上过程
- 空间尺度限制：通常模拟 nm-μm 尺度，原子数上限受计算资源约束

## 力场适用范围
- LJ 势：稀有气体、简单液体
- EAM：金属（fcc/bcc/hcp）
- Tersoff：半导体（Si、C、Ge 等）
- ReaxFF：化学反应体系（燃烧、催化、含能材料）
- COMB3：离子-共价混合体系
- AIREBO：碳氢体系（石墨烯、碳纳米管、金刚石）

## 常见限制
- 单个输入脚本中不能混用不同的 `atom_style`
- `pair_style` 和 `pair_coeff` 必须完整覆盖所有原子类型对
- 周期体系必须保证盒子尺寸 > 2 × 截断半径
- MLIAP 需要 LAMMPS 编译时启用对应包
- 重启文件通常不可跨版本兼容
- 含分子拓扑的体系（bonds/angles）不能使用 `fix deform` 改变盒子形状后再简单缩放坐标
