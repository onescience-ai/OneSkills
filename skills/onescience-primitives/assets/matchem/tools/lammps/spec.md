# software_overview
LAMMPS（Large-scale Atomic/Molecular Massively Parallel Simulator）是开源经典分子动力学（MD）模拟代码，由 Sandia National Laboratories 开发维护。专注于材料建模，可在并行计算机上高效运行（MPI+OpenMP 混合并行，支持 GPU 加速）。输入通过脚本文件（in 文件）控制，提供丰富的单位系统（metal/real/si/cgs/electron/lj）、边界条件（p/s/f/m，分别对应周期/缩放/固定/最小）和力场库。核心应用场景涵盖晶体缺陷、表面与界面、液体/非晶态、聚合物、生物大分子等体系的经典 MD 模拟。不适用第一性原理电子结构计算和量子化学单分子计算。

# core_concepts
## 输入脚本结构（4 部分）
1. **初始化（Initialization）**：定义计算的基本参数
   - `units metal`：设置单位系统（metal 最常用于材料模拟，能量单位 eV）
   - `dimension 3`：设置维度（2D 或 3D）
   - `boundary p p p`：三个方向边界条件（p=周期，s=缩放，f=固定，m=最小）
   - `atom_style atomic`：原子类型（atomic/charge/full/molecular 等）
   - `newton on`：牛顿第三定律开关

2. **原子定义（Atom Definition）**：
   - `lattice`：晶体点阵定义（如 `lattice fcc 4.05` 对应 Al 的 FCC 晶格常数 4.05 Angstrom）
   - `region`：几何区域定义（如 `region box block 0 10 0 10 0 10`）
   - `create_box`：创建模拟盒子
   - `create_atoms`：在区域内填充原子
   - `read_data`：从 data 文件读取原子坐标

3. **力场与系综设置（Settings）**：
   - `pair_style` 与 `pair_coeff`：对势类型和参数
   - `kspace_style`：长程静电方法（pppm/ewald）
   - `fix`：系综控制（nvt/npt/nve）、约束、外场
   - `compute`：热力学/结构分析计算
   - `dump`：轨迹输出

4. **运行控制（Run）**：
   - `timestep`：积分步长（fs）
   - `thermo`：热力学输出间隔
   - `thermo_style`：热力学输出内容
   - `run`：运行步数

## 单位系统（Units）
| 单位系统 | 长度 | 时间 | 能量 | 质量 | 温度 |
|---------|------|------|------|------|------|
| metal   | Å    | ps   | eV   | amu  | K    |
| real    | Å    | fs   | kcal/mol | amu | K |
| si      | m    | s    | J    | kg   | K    |
| cgs     | cm   | s    | erg  | g    | K    |
| electron| Bohr | fs   | Hartree | amu | K |
| lj      | σ    | τ    | ε    | m    | ε/kB |

材料模拟最常用 `units metal`，生物分子常用 `units real`。

## 时间步长选择
- 典型值：0.1-2.0 fs，取决于最轻原子和最高频率振动
- 金属体系：0.5-1.0 fs
- 有机/生物分子：1.0-2.0 fs（配合 SHAKE 约束可至 2.0 fs）
- 含氢原子时需更小步长或用刚性约束
- 过大的时间步长会导致能量漂移和体系失稳

## 近邻列表（Neighbor Lists）
- `neighbor`：设置近邻列表更新策略
- `neigh_modify`：调整近邻列表参数（skin distance、更新频率等）
- skin distance 典型值为 2.0-4.0 Å
- 合理的 skin 值可平衡精度和计算效率

## 力场类型
### 对势（Pair Potentials）
- `lj/cut`：截断 Lennard-Jones
- `eam` / `eam/alloy`：嵌入原子势（金属）
- `reaxff`：反应力场（化学反应、键断裂/形成）
- `comb` / `comb3`：电荷优化多体势
- `airebo` / `airebo/morse`：碳氢体系反应经验键序势
- `tersoff`：Tersoff 键序势（半导体）
- `buck` / `buck/coul/long`：Buckingham 势（离子晶体）
- `born` / `born/coul/long`：Born-Mayer-Huggins 势

### 长程静电
- `kspace_style pppm`：粒子-粒子-粒子-网格法（推荐）
- `kspace_style ewald`：Ewald 求和
- 精度由 tolerance 参数控制（典型值 1.0e-4 至 1.0e-6）

## 系综控制
| 系综 | fix 命令 | 说明 |
|------|---------|------|
| NVE | `fix 1 all nve` | 微正则系综，能量守恒 |
| NVT | `fix 1 all nvt temp Tstart Tstop Tdamp` | Nose-Hoover 恒温器 |
| NVT | `fix 1 all langevin Tstart Tstop Tdamp seed` | Langevin 恒温器 |
| NVT | `fix 1 all temp/berendsen Tstart Tstop Tdamp` | Berendsen 恒温器 |
| NPT | `fix 1 all npt temp Tstart Tstop Tdamp iso/aniso Pstart Pstop Pdamp` | Nose-Hoover 恒温恒压 |
| NPH | `fix 1 all nph iso/aniso Pstart Pstop Pdamp` | 恒焓恒压 |

关键参数说明：
- `Tstart` / `Tstop`：起始和目标温度（K）
- `Tdamp`：温度阻尼参数（ps），典型值 100 × timestep 至 1000 × timestep
- `Pstart` / `Pstop`：起始和目标压力（bar 或 atmosphere 取决于 units）
- `Pdamp`：压力阻尼参数（ps），典型值 1000 × timestep
- `iso`：各向同性压力耦合，`aniso`：各向异性压力耦合

## ML 势函数接口（MLIAP）
- `pair_style mliap`：ML-IAP 接口，支持 MACE、DeepMD、SNAP 等 ML 势函数
- 需要在 LAMMPS 编译时启用 MLIAP 包和对应的 Python/ML 接口
- 典型用法：`pair_style mliap model mliapmodel.pt descriptor sna ...`
- 相关原语：`mace`、`deepmd`、`uma_escn_md`

# common_workflows
## 1. 能量最小化（结构弛豫）
```
min_style cg                    # 共轭梯度法
minimize 1.0e-10 1.0e-10 10000 100000  # 能量容限 力容限 最大迭代 最大评估
```
- `min_style`：可选择 `cg`（共轭梯度）、`sd`（最速下降）、`quickmin`、`fire`
- 弛豫目标：力容限通常设为 1.0e-8 至 1.0e-10 eV/Å
- 通常作为 MD 模拟的前处理步骤

## 2. NVT 平衡（控温预平衡）
```
velocity all create 300 12345 dist gaussian  # 初始化速度
fix 1 all nvt temp 300 300 0.1              # NVT 恒温，Tdamp=0.1 ps
run 50000                                    # 运行 50000 步
unfix 1                                      # 解除 fix
```
- 目的：消除初始结构应力，使体系达到目标温度
- 典型运行步数：10000-100000 步

## 3. NPT 平衡（控温控压预平衡）
```
fix 1 all npt temp 300 300 0.1 iso 0 0 1.0  # NPT，目标 P=0 bar
run 50000
unfix 1
```
- 目的：调整晶格常数或密度至平衡值
- 压力目标通常为 0 bar（零压）或大气压 1.01325 bar
- 各向同性（iso）适用于立方晶体，各向异性（aniso）适用于非立方晶体

## 4. 生产运行 MD（数据采集）
```
fix 1 all nvt temp 300 300 0.1              # 或 nve
thermo 100                                   # 每 100 步输出热力学量
thermo_style custom step temp press pe ke etotal vol
dump 1 all custom 1000 trajectory.lammpstrj id type x y z
dump_modify 1 sort id
compute rdf all rdf 200 1 1                 # 径向分布函数
fix rdf_ave all ave/time 100 10 1000 c_rdf[*] file rdf.dat mode vector
run 1000000
```
- 生产运行通常使用 NVE 或 NVT 系综
- `thermo` 输出间隔和 `dump` 轨迹间隔根据模拟长度和磁盘空间设置
- 数据分析（RDF、MSD、VACF 等）通过 `compute` + `fix ave/time` 实现

## 5. 形变模拟
```
fix 1 all npt temp 300 300 0.1 aniso 0 0 1.0  # NPT 平衡
run 50000
unfix 1
fix 2 all deform 1 x erate 0.001 units box     # x 方向拉伸，应变率 0.001/ps
fix 3 all nvt temp 300 300 0.1
run 100000
```
- `fix deform` 支持各种形变模式（拉伸、压缩、剪切）
- 应变率典型值：10^8-10^10 s^-1（MD 时间尺度远快于实验）

## 6. 热导率计算
```
fix langevin_hot all langevin Thot Thot Tdamp seed1
fix langevin_cold all langevin Tcold Tcold Tdamp seed2
fix heat all heat 1 hot cold                # 热流分区
compute ke all ke/atom
compute pe all pe/atom
compute stress all stress/atom NULL virial
compute flux all heat/flux ke pe stress
fix ave all ave/time 100 10 1000 c_flux[*] file flux.dat mode vector
run 1000000
```
- 非平衡分子动力学（NEMD）方法
- 需要合理设置热源/热汇区域和温度梯度

# key_parameters
## 核心参数速查
| 参数 | 典型值/选项 | 说明 |
|------|------------|------|
| `timestep` | 0.1-2.0 fs | 积分步长，取决于最轻原子 |
| `units` | metal/real/si/cgs/electron/lj | 单位系统 |
| `pair_style` | lj/cut, eam, eam/alloy, reaxff, tersoff, airebo | 对势类型 |
| `kspace_style` | pppm, ewald, none | 长程静电方法 |
| `fix nvt` | `temp Tstart Tstop Tdamp` | Nose-Hoover 恒温器参数 |
| `fix npt` | `temp Tstart Tstop Tdamp iso/aniso Pstart Pstop Pdamp` | 恒温恒压参数 |
| `Tdamp` | 0.01-1.0 ps | 温度阻尼，典型 ~100×timestep |
| `Pdamp` | 0.1-10.0 ps | 压力阻尼，典型 ~1000×timestep |
| `thermo` | 10-10000 | 热力学输出频率（步数） |
| `neigh_modify delay` | 0-10 | 近邻列表重建延迟 |
| `neigh_modify every` | 1-10 | 近邻列表重建频率 |
| `min_style` | cg/sd/quickmin/fire | 能量最小化算法 |
| `minimize tol` | 1.0e-8 至 1.0e-10 (能量), 1.0e-8 至 1.0e-10 (力) | 最小化容差 |

## 热力学输出字段
常用 `thermo_style custom` 字段：
- `step`：模拟步数
- `temp`：瞬时温度
- `press`：瞬时压力
- `pe`：总势能
- `ke`：总动能
- `etotal`：总能量（pe + ke）
- `vol`：体积
- `lx ly lz`：盒子三边长度
- `density`：密度
- `cpu`：CPU 时间

# input_script_structure
## 完整示例：Al 晶体的 NPT 平衡 + NVE 生产运行
```lammps
# ===== 第 1 部分：初始化 =====
units metal
dimension 3
boundary p p p
atom_style atomic
newton on

# ===== 第 2 部分：原子定义 =====
lattice fcc 4.05
region box block 0 10 0 10 0 10 units lattice
create_box 1 box
create_atoms 1 box
mass 1 26.98

# ===== 第 3 部分：力场设置 =====
pair_style eam/alloy
pair_coeff * * Al.eam.alloy Al
neighbor 2.0 bin
neigh_modify every 1 delay 0 check yes

# ===== 第 4 部分：弛豫与平衡 =====
# 能量最小化
min_style cg
minimize 1.0e-12 1.0e-12 10000 10000

# 设定初始速度
velocity all create 300 12345 dist gaussian

# NPT 平衡
fix 1 all npt temp 300 300 0.1 iso 0 0 1.0
thermo 100
thermo_style custom step temp press pe ke etotal vol lx
run 50000
unfix 1

# NVE 生产运行
fix 2 all nve
dump 1 all custom 1000 traj.lammpstrj id type x y z
run 100000
```

# common_pitfalls
## 时间步长过大
- **现象**：能量快速漂移、原子飞出模拟盒子、"Lost atoms" 错误
- **原因**：timestep 超过最高频振动周期的 1/10-1/20
- **解决**：减小 timestep；对含氢键体系使用 SHAKE 约束

## 平衡不充分
- **现象**：生产数据中能量/温度/压力持续漂移
- **诊断**：检查 `thermo` 输出中温度、压力、势能是否收敛至稳定值
- **解决**：增加平衡步数；检查系综参数合理性

## 忘记设置 pair_coeff
- **现象**：`ERROR: All pair coeffs are not set`
- **解决**：确保对所有原子类型设置了 `pair_coeff`

## 单位系统不匹配
- **现象**：晶格常数、能量、温度等物理量数值异常
- **典型错误**：使用 `units metal` 但力场参数来自 `units real` 文献
- **解决**：明确力场参数的单位系统并保持一致；必要时进行单位转换

## 周期性边界条件伪影
- **现象**：小体系中原子与其镜像相互作用
- **解决**：确保模拟盒子在三个方向至少为截断半径的 2 倍；检查 `boundary` 设置

## 近邻列表更新不及时
- **现象**：原子穿透、非物理的高能量
- **解决**：减小 `neigh_modify every` 和 `neigh_modify delay`；增大 skin distance

## MLIAP 使用注意
- LAMMPS 版本需支持 MLIAP 包（编译时启用 `-D PKG_ML-IAP=yes`）
- ML 模型文件路径需在计算节点上可访问
- ML 势函数的截断半径需与 LAMMPS 近邻列表设置一致
- 大批量 MLIAP 模拟需关注 Python 接口的通信开销

# hpc_considerations
## 并行策略
- **MPI**：默认并行方式，通过空间域分解（domain decomposition）实现
- **OpenMP**：在 MPI 进程内通过线程并行加速 pair force 计算
- **GPU 加速**：通过 KOKKOS 或 GPU 包支持 NVIDIA/AMD GPU
- 推荐配置：每节点 MPI 进程数 × 每进程线程数 = 物理核心数

## 负载均衡
- `balance` / `fix balance`：动态负载均衡
- 适用于非均匀密度体系（如表面、界面、气-液共存）
- 频率建议：每 1000-10000 步检查并重新分配

## 性能优化要点
- `processors`：手动设置域分解网格（如 `processors 2 2 2`）
- 原子数较多时优先使用 `kspace_style pppm`（比 ewald 更高效）
- 选择合适的近邻列表 bin 大小和 skin distance
- 对大体系（>1M 原子），检查域分解效率

# mlip_interface
## MLIAP 框架
LAMMPS 通过 MLIAP（Machine-Learning Interatomic Potential）框架支持多种 ML 势函数：
- **SNAP**：Spectral Neighbor Analysis Potential，原生支持
- **MACE**：通过 MLIAP Python 接口调用，需安装对应 Python 包
- **DeepMD**：通过 `pair_style deepmd` 或 MLIAP 接口
- **NequIP**：等变神经网络势函数
- **GAP**：Gaussian Approximation Potential

## 典型 MLIAP 输入示例
```
pair_style mliap model mliapmodel.pt descriptor sna 1.0
pair_coeff * *
```

## 约束条件
- ML 势函数截断半径必须与 `neighbor` 设置一致
- 原子序数映射需在 ML 模型配置和 LAMMPS 输入中保持一致
- 计算性能取决于 ML 模型复杂度（网络规模、等变阶数等）

# source_references
- LAMMPS 官方文档：https://docs.lammps.org/Manual.html
- LAMMPS GitHub 仓库：https://github.com/lammps/lammps
- LAMMPS 输入脚本命令参考：https://docs.lammps.org/Commands_all.html
- MLIAP 使用指南：https://docs.lammps.org/pair_mliap.html
