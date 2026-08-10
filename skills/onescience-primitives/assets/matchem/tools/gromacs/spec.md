# software_overview
GROMACS（GROningen MAchine for Chemical Simulations）是开源高性能分子动力学模拟引擎，由 Uppsala University、Royal Institute of Technology (KTH) 和 Max Planck Institute 等机构持续开发维护。自 1991 年诞生以来，已发展为生物分子模拟领域最广泛使用的软件之一。GROMACS 以极致计算性能著称——通过手工优化的汇编级 SIMD 内核、高效的域分解并行策略（DD）和原生 GPU 加速，在单节点上即可达到百微秒/天的模拟速度。核心应用场景集中在生物分子体系（蛋白质、核酸、脂质膜、糖类）和软物质体系（高分子、胶体、表面活性剂），支持全原子、联合原子（united-atom）和粗粒化（coarse-grained，如 MARTINI）等多分辨率建模。不适用第一性原理电子结构计算和材料体系的经典 MD 模拟。

# core_concepts
## 力场（Force Field）
GROMACS 支持的力场通过预定义的力场目录（`$GMXDATA/top/`）直接调用，无需手动准备参数文件。常见的力场函数形式为：

\(V_{\text{total}} = V_{\text{bonded}} + V_{\text{nonbonded}}\)

其中：
- **成键项**（bonded）：键伸缩、角弯曲、正常/异常二面角（proper/improper dihedrals）、1-4 非键相互作用
- **非键项**（nonbonded）：Lennard-Jones（LJ）范德华 + Coulomb 静电

支持的力场清单：
| 力场 | 类型 | 适用体系 | 选择命令 |
|------|------|---------|---------|
| AMBER99SB-ILDN | 全原子 | 蛋白质、核酸 | `pdb2gmx -ff amber99sb-ildn` |
| AMBER14SB | 全原子 | 蛋白质 | `pdb2gmx -ff amber14sb` |
| AMBER99SB-disp | 全原子 | 蛋白质（含无序区） | `pdb2gmx -ff amber99sb-disp` |
| CHARMM36m | 全原子 | 蛋白质、核酸、脂质 | `pdb2gmx -ff charmm36-jul2022` |
| CHARMM36 | 全原子 | 蛋白质、核酸、脂质 | `pdb2gmx -ff charmm36` |
| OPLS-AA/L | 全原子 | 有机小分子、蛋白质 | `pdb2gmx -ff oplsaa` |
| GROMOS54A7 | 联合原子 | 蛋白质、脂质、聚合物 | `pdb2gmx -ff gromos54a7` |
| MARTINI 3 | 粗粒化 | 大尺度蛋白质、膜 | 需手动准备 itp 文件 |
| GROMOS 53A6 | 联合原子 | 蛋白质 | `pdb2gmx -ff gromos53a6` |

## 拓扑系统（Topology）
GROMACS 的核心体系描述通过拓扑文件（`.top`）实现，`.top` 文件通过 `#include` 指令引用力场参数文件（`.itp`），定义分子中所有原子类型、键连关系、非键参数、约束等信息。

拓扑文件结构：
```
#include "amber99sb-ildn.ff/forcefield.itp"   # 力场参数
[ moleculetype ]                                # 分子类型定义
Protein_A           3
[ atoms ]                                       # 原子列表：编号 类型 残基编号 残基名 原子名 电荷组 电荷 质量
[ bonds ]                                       # 键列表（约束键用 constraints 段）
[ pairs ]                                       # 1-4 非键对
[ angles ]                                      # 角列表
[ dihedrals ]                                   # 二面角列表
[ system ]                                      # 体系名称
[ molecules ]                                   # 分子组成（各分子类型数量）
Protein_A    1
SOL         12000
```

## 周期性边界条件（Periodic Boundary Conditions, PBC）
所有生物分子 MD 模拟必须使用周期边界以避免表面效应，GROMACS 支持：
- `pbc = xyz`：三维周期边界（默认，最常用）
- `pbc = xy`：二维周期（适用于平板/膜体系，z 方向非周期）
- `pbc = no`：无周期边界（仅限真空模拟）
- 盒子类型：`triclinic`（三斜，可任意形状）、`cubic`（立方）、`dodecahedron`（菱形十二面体，球状蛋白最优——节省约 29% 溶剂）

## PME 静电计算（Particle-Mesh Ewald）
GROMACS 使用 Smooth Particle-Mesh Ewald（SPME）处理长程静电相互作用，将静电能分解为实空间（短程）和倒空间（长程）两部分：

- **实空间截断**：`rlist` / `rcoulomb` 参数控制，典型值 1.0-1.4 nm
- **倒空间网格**：`fourierspacing` 控制网格密度，典型值 0.10-0.16 nm（越小越精确，但计算量增大）
- **插值阶数**：`pme_order = 4`（默认，平衡精度与效率）
- **VdW 截断**：`rvdw` 通常等于 `rcoulomb`，长程色散校正通过 `DispCorr = EnerPres` 启用

## 温度耦合（Temperature Coupling）
| 耦合方法 | tcoupl 值 | 说明 | 推荐场景 |
|---------|----------|------|---------|
| Velocity-rescale | `v-rescale` | 随机速度缩放，产生正确正则系综 | NVT/NPT 平衡（推荐） |
| Nose-Hoover | `nose-hoover` | 扩展拉格朗日方法，产生正确 NVT 系综 | NVT 生产运行 |
| Berendsen | `berendsen` | 弱耦合至热浴，不产生严格正则系综 | 仅用于初始粗糙平衡 |
| Langevin | `langevin` | 随机 + 摩擦力，适用于小体系或隐式溶剂 | 隐式溶剂、小体系 |
| Andersen | `andersen` | 随机碰撞恒温器 | 特定研究用途 |

时间常数 `tau_t`：典型值 0.1-1.0 ps。平衡阶段可用较小值（0.1 ps），生产阶段用较大值（1.0-2.0 ps）。

## 压力耦合（Pressure Coupling）
| 耦合方法 | pcoupl 值 | 说明 |
|---------|----------|------|
| Parrinello-Rahman | `Parrinello-Rahman` | 扩展拉格朗日恒压器，产生正确 NPT 系综（推荐生产用） |
| Berendsen | `Berendsen` | 弱耦合恒压器，速度快但不产生严格系综（仅用于初始平衡） |
| C-rescale | `C-rescale` | 随机缩放恒压器，产生正确 NPT 系综 |
| MTTK | `MTTK` | Martyna-Tuckerman-Tobias-Klein 恒压器 |

时间常数 `tau_p`：典型值 1.0-5.0 ps。压力耦合模式：
- `isotropic`：各向同性（立方盒）
- `semiisotropic`：半各向同性（xy 独立于 z，适用于膜体系）
- `anisotropic`：各向异性（三个方向独立）
- `surface-tension`：表面张力耦合（膜体系）

## 约束算法（Constraints）
GROMACS 通过 LINCS 算法约束含氢键的键长，允许更大的积分步长：
- `constraints = h-bonds`：仅约束含氢键（最常用，允许 2 fs 步长）
- `constraints = all-bonds`：约束所有键（允许更大步长，但增加计算开销）
- `constraints = none`：无约束（需 ≤ 0.5 fs 步长）
- LINCS 迭代设置：`lincs_iter = 1`，`lincs_order = 4`（默认即可）
- 虚拟位点（Virtual Sites）：`constraints = none` + `[virtual_sitesn]` 替换 H 原子，允许 ~4-5 fs 步长

# common_workflows
## 标准 MD 工作流（蛋白质在水中的模拟）

### 第 1 步：拓扑生成（pdb2gmx）
```bash
gmx pdb2gmx -f protein.pdb -o processed.gro -p topol.top -water spc -ff amber99sb-ildn -ignh
```
- `-water`：溶剂模型（spc/tip3p/tip4p/spce）
- `-ignh`：忽略输入 PDB 中的氢原子，由力场重建
- `-ff`：力场选择
- `-ter`：交互选择端基质子化状态（N 端/C 端）
- 输出：`processed.gro`（处理后的坐标）、`topol.top`（拓扑文件）、`posre.itp`（位置限制文件）

### 第 2 步：模拟盒子定义（editconf）
```bash
gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt dodecahedron
```
- `-c`：蛋白质居中
- `-d 1.0`：蛋白质到盒子边缘最小距离 1.0 nm
- `-bt`：盒子类型（cubic/triclinic/dodecahedron），菱形十二面体对球状蛋白最节省溶剂

### 第 3 步：溶剂化（solvate）
```bash
gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top
```
- `-cs`：溶剂坐标模板（通常为内建的 `spc216.gro`）
- `-p`：更新拓扑文件中的溶剂分子数量

### 第 4 步：添加离子（genion）
```bash
gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr
gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral
```
- 先运行 `grompp` 生成 tpr，再运行 `genion`
- `-neutral`：添加足够离子中和体系电荷
- `-conc 0.15`：指定离子浓度（mol/L），常见生理盐浓度

### 第 5 步：能量最小化（Energy Minimization, EM）
```bash
gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em
```
- em.mdp 关键参数：
```
integrator = steep        # 最速下降法
emtol = 1000.0            # 力容限（kJ/mol/nm），< 1000 时收敛
emstep = 0.01             # 初始位移步长 (nm)
nsteps = 50000            # 最大步数
cutoff-scheme = Verlet
rcoulomb = 1.0
rvdw = 1.0
pbc = xyz
```
- 目标：消除原子重叠，最大力 < 1000 kJ/mol/nm
- 如 steepest descent 不收敛，改用 `integrator = cg`（共轭梯度）

### 第 6 步：NVT 平衡（等温平衡）
```bash
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -v -deffnm nvt
```
- nvt.mdp 关键参数：
```
integrator = md           # 分子动力学
dt = 0.002                # 2 fs 步长
nsteps = 50000            # 100 ps
tcoupl = v-rescale        # velocity-rescale 恒温器
tc-grps = Protein Non-Protein  # 温度耦合组
tau_t = 0.1 0.1           # 时间常数 (ps)
ref_t = 300 300           # 参考温度 (K)
pcoupl = no               # 无压力耦合
constraints = h-bonds     # LINCS 约束
rlist = 1.0
rcoulomb = 1.0
rvdw = 1.0
```
- `-r em.gro`：位置限制参考坐标（与 `define = -DPOSRES` 配合）

### 第 7 步：NPT 平衡（等温等压平衡）
```bash
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -v -deffnm npt
```
- npt.mdp 关键参数：
```
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
ref_p = 1.0 1.0
compressibility = 4.5e-5
```
- `-t nvt.cpt`：从 NVT 的 checkpoint 文件继续（保持速度分布）

### 第 8 步：生产 MD（Production MD）
```bash
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -v -deffnm md
```
- md.mdp 关键参数：
```
nsteps = 50000000         # 100 ns
tcoupl = nose-hoover      # Nose-Hoover（生产推荐）
tau_t = 2.0 2.0
nstxout = 0               # 不输出全精度轨迹（节省空间）
nstvout = 0               # 不输出速度
nstenergy = 5000          # 每 10 ps 输出能量
nstlog = 5000             # 每 10 ps 写日志
nstxout-compressed = 5000 # 每 10 ps 输出压缩轨迹（xtc）
```

## 自由能计算工作流

### FEP（自由能微扰）——配体结合自由能
```bash
# 需准备各 lambda 窗口的 mdp 文件
gmx grompp -f fep_0.mdp -c equil.gro -p topol.top -o fep_0.tpr
gmx mdrun -v -deffnm fep_0
gmx bar -f fep_*.xvg -o bar_results.xvg  # Bennett Acceptance Ratio 分析
```

### Umbrella Sampling（伞形采样）——PMF 计算
```bash
# 1. 生成牵引构型
gmx grompp -f pull.mdp -c equil.gro -p topol.top -o pull.tpr
gmx mdrun -v -deffnm pull -pf pullf.xvg -px pullx.xvg
# 2. 提取窗口构型
gmx trjconv -f pull.xtc -s pull.tpr -o confs.gro -sep
# 3. 对每个窗口独立运行
gmx grompp -f us_window.mdp -c confs0.gro -p topol.top -o us0.tpr
gmx mdrun -v -deffnm us0
# 4. WHAM 分析
gmx wham -it tpr_files.dat -if pullf_files.dat -o profile.xvg -unit kCal
```

# key_parameters
## 核心 mdp 参数速查
| 参数 | 典型值/选项 | 说明 |
|------|------------|------|
| `integrator` | md/steep/cg | 算法类型：MD、最速下降、共轭梯度 |
| `dt` | 0.001-0.005 ps | 积分步长（0.001 ps = 1 fs, 0.002 ps = 2 fs） |
| `nsteps` | 5000-50000000 | 运行步数（总时间 = nsteps × dt） |
| `tcoupl` | v-rescale/nose-hoover/berendsen | 温度耦合方法 |
| `ref_t` | 300-310 K | 参考温度 |
| `tau_t` | 0.1-2.0 ps | 温度耦合时间常数 |
| `pcoupl` | Parrinello-Rahman/Berendsen/C-rescale | 压力耦合方法 |
| `ref_p` | 1.0 bar | 参考压力 |
| `tau_p` | 1.0-5.0 ps | 压力耦合时间常数 |
| `compressibility` | 4.5e-5 bar⁻¹ | 水的等温压缩系数 |
| `constraints` | h-bonds/all-bonds/none | 键长约束 |
| `constraint-algorithm` | LINCS | LINCS 约束算法（默认） |
| `rlist` | 0.9-1.4 nm | 近邻列表截断 |
| `rcoulomb` | 0.9-1.4 nm | 库仑截断 |
| `rvdw` | 0.9-1.4 nm | 范德华截断 |
| `fourierspacing` | 0.10-0.16 nm | PME 网格间距 |
| `pme_order` | 4 | PME 插值阶数 |
| `DispCorr` | EnerPres/no | 长程色散校正 |
| `cutoff-scheme` | Verlet | 截断方案（推荐 Verlet） |
| `vdwtype` | Cut-off/PME/Switch/Shift | VdW 处理方式 |
| `coulombtype` | PME/Cut-off/Reaction-Field | 静电处理方法 |
| `pbc` | xyz/xy/no | 周期边界条件 |
| `nstxout-compressed` | 500-10000 | 压缩轨迹 (xtc) 输出间隔 |
| `nstenergy` | 500-10000 | 能量输出间隔 |
| `nstlog` | 500-10000 | 日志写入间隔 |
| `gen-vel` | yes/no | 是否生成初始速度 |
| `gen-temp` | 300 | 初始 Maxwell-Boltzmann 分布温度 |
| `gen-seed` | -1 | 随机数种子（-1 使用系统熵） |
| `verlet-buffer-tolerance` | 0.005 kJ/mol/ps | Verlet 缓冲区容差 |

## 能量最小化参数
| 参数 | 典型值 | 说明 |
|------|-------|------|
| `integrator` | steep | 最速下降法（粗收敛） |
| `integrator` | cg | 共轭梯度（精细收敛） |
| `emtol` | 100-1000 kJ/mol/nm | 力容限收敛标准 |
| `emstep` | 0.01 nm | 初始位移步长 |
| `nsteps` | 5000-50000 | 最大最小化步数 |
| `nstcgsteep` | 1000 | CG 每 N 步混合一次 steepest descent |

## 增强采样参数（Pull Code）
| 参数 | 说明 |
|------|------|
| `pull = yes` | 启用牵引 |
| `pull-ngroups` | 牵引组数量 |
| `pull-ncoords` | 牵引坐标数量 |
| `pull-coord1-type` | umbrella/constant-force/flat-bottom |
| `pull-coord1-rate` | 牵引速率 (nm/ps) |
| `pull-coord1-k` | 力常数 (kJ/mol/nm²) |
| `pull-coord1-geometry` | distance/direction/cylinder/position |

## 时间规划指南
| 阶段 | 典型时间 | 步数（2 fs 步长） |
|------|---------|-----------------|
| 能量最小化 | 收敛即止 | ~500-50000（无固定时间） |
| NVT 平衡 | 50-500 ps | 25000-250000 |
| NPT 平衡 | 50-500 ps | 25000-250000 |
| 生产 MD | 10 ns - 1 μs | 5000000-500000000 |
| 输出频率 | 10-100 ps/帧 | 5000-50000 步/帧 |

# input_files
## 文件类型总览
| 扩展名 | 类型 | 说明 | 来源 |
|--------|------|------|------|
| `.pdb` | 文本 | 蛋白质数据银行格式坐标 | 实验/建模 |
| `.gro` | 文本 | GROMACS 坐标格式（固定列宽） | pdb2gmx/editconf |
| `.top` | 文本 | 体系拓扑（分子定义 + 分子数量） | pdb2gmx + 手动编辑 |
| `.itp` | 文本 | 分子/力场参数（被 .top #include） | 力场内建/自定义 |
| `.mdp` | 文本 | 模拟参数文件 | 用户编写 |
| `.tpr` | 二进制 | 完整模拟输入（拓扑 + 坐标 + 参数） | grompp 生成 |
| `.cpt` | 二进制 | Checkpoint 文件（断点续传） | mdrun 自动生成 |
| `.xtc` | 二进制 | 压缩轨迹（坐标，默认精度） | mdrun 输出 |
| `.trr` | 二进制 | 全精度轨迹（坐标 + 速度 + 力） | mdrun 输出 |
| `.edr` | 二进制 | 能量数据文件 | mdrun 输出 |
| `.log` | 文本 | 运行日志 | mdrun 输出 |
| `.xvg` | 文本 | 二维数据（xmgrace 格式） | 各分析工具输出 |
| `.tng` | 二进制 | 下一代轨迹格式（高压缩比） | mdrun 输出（可选） |

## pdb2gmx 输入输出流
```
输入：protein.pdb（PDB 格式坐标）
  │
  ├── pdb2gmx（选择力场、水模型）
  │
  ├── 输出：processed.gro（处理后的 GROMACS 坐标）
  │         topol.top（体系拓扑）
  │         posre.itp（位置限制参数，用于平衡阶段约束重原子）
  │
  └── 力场目录参考：$GMXDATA/top/<forcefield>.ff/
```

## mdp 文件关键块
```
; 运行控制
integrator = md
dt = 0.002
nsteps = 50000000

; 输出控制
nstxout-compressed = 5000
nstenergy = 5000
nstlog = 5000

; 近邻列表
cutoff-scheme = Verlet
rlist = 1.0
verlet-buffer-tolerance = 0.005

; 静电
coulombtype = PME
rcoulomb = 1.0
fourierspacing = 0.12
pme_order = 4

; 范德华
vdwtype = Cut-off
rvdw = 1.0
DispCorr = EnerPres

; 温度耦合
tcoupl = v-rescale
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
ref_t = 300 300

; 压力耦合
pcoupl = no

; 约束
constraints = h-bonds

; 周期边界
pbc = xyz

; 初始速度
gen-vel = yes
gen-temp = 300
gen-seed = -1
```
- 注释以 `;` 开头
- 参数不区分大小写
- 多温度耦合组（`tc-grps`）各自使用独立的 tau_t 和 ref_t

# common_pitfalls
## 力场与水模型不匹配
- **现象**：结构在模拟中迅速失稳、二级结构快速loss
- **原因**：每个力场针对特定水模型参数化，混用会产生不平衡作用力
- **正确搭配**：
  - AMBER 家族 → TIP3P（`-water tip3p`）
  - CHARMM36 → CHARMM TIP3P（`-water tip3p`，水模型内建于力场）
  - OPLS-AA → TIP4P 或 SPC/E
  - GROMOS → SPC 或 SPC/E
  - MARTINI → 标准 MARTINI 水（粗粒化水珠子）

## 缺少中和离子
- **现象**：PME 计算报错或体系总电荷非零警告
- **原因**：PME 要求体系总电荷为零，否则会产生虚假背景电荷
- **解决**：使用 `genion -neutral` 添加抗衡离子中和体系

## 位置限制未去除
- **现象**：生产 MD 中蛋白质似乎"冻结"
- **原因**：生产 mdp 文件中仍定义了 `define = -DPOSRES`
- **解决**：在生产 mdp 中删除 `define = -DPOSRES` 或注释掉

## 溶剂盒子不够大
- **现象**：蛋白质与其周期镜像发生非物理相互作用（周期性伪影）
- **诊断**：检查最小镜像距离是否大于 2 × rlist
- **解决**：增加 `editconf -d` 值（推荐 ≥ 1.0 nm），或增大盒子

## 步长过大 / 约束不足
- **现象**：体系崩溃、LINCS 警告（" relative constraint deviation exceeds limit "）
- **原因**：2 fs 步长但未约束含氢键，或步长设为 4-5 fs 但未使用虚拟位点
- **解决**：2 fs → 使用 `constraints = h-bonds`；4-5 fs → 使用氢原子虚拟位点 + `constraints = all-bonds`

## 温度耦合组分离不当
- **现象**：溶剂与溶质之间出现"热浴-冷浴"效应（hot solvent - cold solute）
- **原因**：不同分子种类（蛋白质/溶剂/离子）在不同 tc-grps 中，恒温器移除它们之间的动能交换
- **解决**：平衡后生产阶段将全部体系作为单一温度耦合组，或使用 `tc-grps = System`

## NPT 平衡时盒子剧烈振荡
- **现象**：初始 NPT 阶段盒子尺寸剧烈变化甚至盒子崩溃
- **原因**：初始结构偏离平衡密度，直接使用 Parrinello-Rahman 恒压器导致振荡
- **解决**：先用 Berendsen 恒压器做短平衡（~100 ps），再切换到 Parrinello-Rahman；或减小 `tau_p`

## 轨迹文件过大
- **现象**：磁盘空间迅速耗尽
- **解决**：
  - 使用 `.xtc` 代替 `.trr`（压缩比 ~10×）
  - 增大 `nstxout-compressed`（如 10000 步 = 20 ps/帧）
  - 使用 `.tng` 格式（更高压缩比）
  - 不要输出速度和力（`nstvout = 0`，`nstfout = 0`）

## 周期性分子断裂
- **现象**：PBC 导致分子跨越盒子边界被"撕裂"
- **解决**：
  - 使用 `gmx trjconv -pbc mol -center` 后处理轨迹
  - 确保分子完整（`gmx trjconv -pbc whole`）

# hpc_considerations
## GPU 加速策略
GROMACS 采用 CUDA/SYCL/OpenCL 混合加速架构，将短程非键力计算卸载到 GPU，PME 和 bonded 力留在 CPU：

### GPU 任务分配
```
                 CPU                           GPU
     ┌───────────────────────┐    ┌───────────────────────┐
     │ PME 网格求解           │    │ 短程非键力（LJ+Coulomb）│
     │ 成键力计算             │    │ （主导计算，>80% 耗时） │
     │ 域分解与通信           │    │                       │
     │ 约束 (LINCS/SHAKE)     │    │ 约束也可部分卸载        │
     │ 积分与坐标更新         │    │                       │
     └───────────────────────┘    └───────────────────────┘
```

### GPU 性能因素
- **体系规模**：< 20000 原子时，GPU 加速比约为 2-5×；> 100000 原子时可达 10-50×
- **多 GPU**：通过 `-gpu_id 0123` 指定 GPU，GROMACS 支持一个模拟跨多个 GPU
- **GPU 选择**：NVIDIA GPU（CUDA）性能最优，AMD GPU（HIP/SYCL）和 Intel GPU（SYCL）也有良好支持
- `-nb gpu`：强制短程非键力在 GPU 计算（默认自动选择）
- `-pme gpu`：将 PME 也卸载到 GPU（大体系推荐）
- `-bonded gpu`：将成键力也卸载到 GPU
- `-update gpu`：将积分/约束在 GPU 计算（减少 CPU-GPU 数据传输）
- **建议配置**：`gmx mdrun -nb gpu -pme gpu -bonded gpu -update gpu`

### 单节点 vs 多节点
GROMACS 使用域分解（Domain Decomposition, DD）进行并行，每个域分配给一个 MPI rank：
- **单节点单 GPU 配置**：
```bash
gmx mdrun -v -deffnm md -nb gpu -pme gpu -bonded gpu -update gpu
```
- **单节点多 GPU**：
```bash
gmx mdrun -v -deffnm md -nb gpu -pme gpu -bonded gpu -update gpu -gpu_id 01
```
- **多节点 MPI + GPU**：
```bash
mpirun -np 8 gmx_mpi mdrun -v -deffnm md -nb gpu -pme gpu -bonded gpu -update gpu -gputasks 00112233
```
`-gputasks`：指定每个 MPI rank 使用的 GPU ID

## 域分解（Domain Decomposition）
GROMACS 自动将模拟盒子划分为 3D 网格，每个网格分配给一个 MPI rank。域分解的关键约束：
- 每个域的最小尺寸必须大于 `rlist`（否则需要更多的通信）
- 原子数较多的体系（>1M 原子）域分解效率高
- `-dd` 参数手动设置分解网格：`-dd 2 2 2`（x×y×z）
- GROMACS 自动进行动态负载均衡（DLB），处理非均匀密度体系

## 性能基准参考
| 体系规模 | 硬件配置 | 典型性能 |
|---------|---------|---------|
| ~25K 原子（溶菌酶+水） | 1×V100 GPU + 8 CPU cores | ~1-2 μs/day |
| ~100K 原子（膜蛋白+膜+水） | 1×A100 GPU + 16 cores | ~500-800 ns/day |
| ~500K 原子（大型复合体） | 2×A100 GPU + 32 cores | ~200-400 ns/day |
| ~1M 原子（病毒衣壳） | 4×A100 GPU + 64 cores | ~100-200 ns/day |
| ~10M 原子（粗粒化） | 8×A100 GPU + 128 cores | ~50-100 ns/day |

## SLURM 提交脚本模板
```bash
#!/bin/bash
#SBATCH -J gmx_md
#SBATCH -N 2
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:4
#SBATCH -t 72:00:00
#SBATCH --partition=gpu

module load gromacs/2024

export OMP_NUM_THREADS=4

mpirun -np 16 gmx_mpi mdrun -v -deffnm md \
    -nb gpu -pme gpu -bonded gpu -update gpu \
    -gputasks 0000111122223333 \
    -maxh 72
```
- `-maxh`：最大运行时间（小时），与作业分配时间匹配，GROMACS 会在时间结束前自动写 checkpoint

## 断点续传
```bash
# 从 checkpoint 继续
gmx mdrun -v -deffnm md -cpi md.cpt

# 追加模式（将新模拟数据附加到已有输出文件）
gmx mdrun -v -deffnm md -cpi md.cpt -append
```
- `.cpt` 文件在 mdrun 运行期间自动每 15 分钟写入一次
- 如集群有作业时间限制，使用 `-maxh` 参数确保 checkpoint 在作业结束前写入

## 性能分析工具
```bash
# 运行性能报告
gmx mdrun -v -deffnm md -nsteps 10000 -resetstep 5000

# 分析性能日志
gmx check -f md.tpr 2>&1 | grep -A 20 "Performance"

# 详细性能输出（在 md.log 中）
# 关注 Dt 和 Day 列来评估性能瓶颈
```

# source_references
- GROMACS 官方手册：https://manual.gromacs.org/current/
- GROMACS 官方下载：https://www.gromacs.org/Downloads
- GROMACS 用户指南（Tutorials）：http://www.mdtutorials.com/gmx/
- GROMACS 论文引用：Abraham et al., SoftwareX 1-2, 19-25 (2015). DOI: 10.1016/j.softx.2015.06.001
- MARTINI 力场：http://cgmartini.nl/
- AMBER 力场：https://ambermd.org/AmberModels.php
- CHARMM 力场：https://mackerell.umaryland.edu/charmm_ff.shtml
