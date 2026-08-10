# launch
GROMACS 通过一系列命令行工具完成从结构准备到结果分析的完整 MD 工作流。核心工具前缀为 `gmx`（GROMACS 5.0+）。

## 基础命令格式
```bash
gmx <module> [options]
```
- `<module>`：子命令/工具名称（如 pdb2gmx、grompp、mdrun 等）
- `[options]`：以 `-flag value` 形式传递

## 通用命令行参数
| 参数 | 说明 |
|------|------|
| `-f <file>` | 输入文件（具体含义依模块而异） |
| `-s <file>` | tpr 输入文件（拓扑 + 参数） |
| `-c <file>` | 坐标输入/输出文件（gro/pdb） |
| `-p <file>` | 拓扑文件（.top） |
| `-n <file>` | 索引文件（.ndx） |
| `-o <file>` | 输出文件 |
| `-v` | 详细输出模式 |
| `-h` | 显示帮助信息 |
| `-quiet` | 减少控制台输出 |

## 完整 MD 工作流启动命令

### 准备阶段
```bash
# 1. 生成拓扑
gmx pdb2gmx -f protein.pdb -o processed.gro -p topol.top -water spce -ff amber99sb-ildn -ignh

# 2. 定义盒子
gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt dodecahedron

# 3. 添加溶剂
gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top

# 4. 添加离子（先 grompp 生成 tpr，再 genion）
gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr -maxwarn 5
gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15
```

### 运行阶段
```bash
# 5. 能量最小化
gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em

# 6. NVT 平衡
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -v -deffnm nvt

# 7. NPT 平衡
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -v -deffnm npt

# 8. 生产 MD（GPU 加速）
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -v -deffnm md -nb gpu -pme gpu -bonded gpu -update gpu
```

### 分析阶段
```bash
# 基本分析：RMSD、RMSF、回转半径、氢键
gmx rms -s md.tpr -f md.xtc -o rmsd.xvg
gmx rmsf -s md.tpr -f md.xtc -o rmsf.xvg
gmx gyrate -s md.tpr -f md.xtc -o gyrate.xvg
gmx hbond -s md.tpr -f md.xtc -num hbond_num.xvg

# 轨迹处理
gmx trjconv -s md.tpr -f md.xtc -o md_centered.xtc -pbc mol -center -ur compact

# 提取 PDB 结构（第 0 帧 / 最后一帧）
gmx trjconv -s md.tpr -f md.xtc -o frame.pdb -dump 0
```

## mdrun 核心命令行参数

### 基础参数
| 参数 | 说明 |
|------|------|
| `-deffnm <name>` | 设置默认文件名前缀（自动关联 .tpr/.gro/.cpt 等） |
| `-s <file>` | tpr 输入文件 |
| `-c <file>` | 最终坐标输出 |
| `-x <file>` | 压缩轨迹输出（xtc） |
| `-e <file>` | 能量输出（edr） |
| `-g <file>` | 日志输出 |
| `-cpo <file>` | Checkpoint 输出 |
| `-cpi <file>` | Checkpoint 输入（断点续传） |

### GPU 加速参数
| 参数 | 说明 |
|------|------|
| `-nb gpu/cpu/auto` | 短程非键力计算位置 |
| `-pme gpu/cpu/auto` | PME 计算位置 |
| `-bonded gpu/cpu/auto` | 成键力计算位置 |
| `-update gpu/cpu/auto` | 坐标积分/约束计算位置 |
| `-gpu_id <ids>` | 指定使用的 GPU 编号（如 `01`） |
| `-gputasks <mapping>` | 每个 MPI rank 使用的 GPU（如 `00112233`） |
| `-npme <N>` | 专用于 PME 的 MPI rank 数 |
| `-ntomp <N>` | 每 MPI rank 的 OpenMP 线程数 |

### 并行与资源控制
| 参数 | 说明 |
|------|------|
| `-nt <N>` | 总线程数（自动检测） |
| `-ntmpi <N>` | MPI rank 数（自动检测） |
| `-dd <nx> <ny> <nz>` | 手动域分解网格 |
| `-maxh <hours>` | 最大运行时间，时间到前自动写 checkpoint |
| `-nsteps <N>` | 覆盖 tpr 中的 nsteps（用于基准测试） |
| `-append` | 追加模式（将新数据附加到已有文件） |
| `-norestart` | 不使用 checkpoint 文件 |

## 多 GPU / 多节点运行示例

### 单节点多 GPU
```bash
gmx mdrun -v -deffnm md -nb gpu -pme gpu -bonded gpu -update gpu -gpu_id 0123
```

### 多节点 MPI + GPU
```bash
# SLURM 环境下
export OMP_NUM_THREADS=4
mpirun -np 16 gmx_mpi mdrun -v -deffnm md \
    -nb gpu -pme gpu -bonded gpu -update gpu \
    -gputasks 0000111122223333 \
    -npme 4 -maxh 72
```
- `-npme 4`：将 4 个 rank 专用于 PME 计算（推荐秩数 ~1/3 至 1/4 的 MPI 总数）

# input_schema
## 完整输入文件流程图
```
PDB 坐标文件 (protein.pdb)
  │
  ├── [pdb2gmx] ─── 选择力场 + 水模型
  │     ├── 输出：processed.gro（处理后的坐标）
  │     ├── 输出：topol.top（体系拓扑）
  │     └── 输出：posre.itp（位置限制参数）
  │
  ├── [editconf] ── 定义盒子大小和形状
  │     └── 输出：boxed.gro
  │
  ├── [solvate] ─── 溶剂化
  │     ├── 输出：solvated.gro
  │     └── 更新：topol.top（添加溶剂分子数）
  │
  ├── [grompp + genion] ── 添加离子
  │     ├── 输出：neutralized.gro
  │     └── 更新：topol.top（添加离子分子数）
  │
  ├── [grompp] ──── 生成 em.tpr（能量最小化）
  │     └── 输入：em.mdp + neutralized.gro + topol.top
  │
  ├── [mdrun] ──── 运行 EM
  │     └── 输出：em.gro / em.cpt / em.edr / em.log
  │
  ├── [grompp] ──── 生成 nvt.tpr
  │     └── 输入：nvt.mdp + em.gro + topol.top
  │
  ├── [mdrun] ──── 运行 NVT
  │     └── 输出：nvt.gro / nvt.cpt / nvt.edr / nvt.xtc
  │
  ├── [grompp] ──── 生成 npt.tpr
  │     └── 输入：npt.mdp + nvt.gro + topol.top
  │
  ├── [mdrun] ──── 运行 NPT
  │     └── 输出：npt.gro / npt.cpt / npt.edr / npt.xtc
  │
  ├── [grompp] ──── 生成 md.tpr
  │     └── 输入：md.mdp + npt.gro + topol.top
  │
  └── [mdrun] ──── 运行生产 MD
        └── 输出：md.gro / md.cpt / md.edr / md.xtc / md.log
```

## mdp 文件结构
mdp 文件使用 `;` 作为注释符，按功能分为以下段：

### 运行控制段
```
integrator = md        ; md(生产) / steep(最速下降) / cg(共轭梯度)
dt = 0.002             ; 积分步长 (ps)，0.002 = 2 fs
nsteps = 50000000      ; 运行步数，总时间 = nsteps × dt
```

### 输出控制段
```
nstxout-compressed = 5000    ; 压缩轨迹输出频率
nstenergy = 5000             ; 能量输出频率
nstlog = 5000                ; 日志写入频率
nstvout = 0                  ; 速度输出频率 (0 = 不输出)
nstfout = 0                  ; 力输出频率 (0 = 不输出)
```

### 近邻列表段
```
cutoff-scheme = Verlet
rlist = 1.0                  ; 近邻列表截断 (nm)
verlet-buffer-tolerance = 0.005  ; 缓冲容差 (kJ/mol/ps)
```

### 静电段
```
coulombtype = PME            ; PME / Cut-off / Reaction-Field
rcoulomb = 1.0               ; 库仑截断 (nm)
fourierspacing = 0.12        ; PME 网格间距 (nm)
pme_order = 4                ; PME 插值阶数
```

### 范德华段
```
vdwtype = Cut-off
rvdw = 1.0                   ; 范德华截断 (nm)
DispCorr = EnerPres          ; 长程色散校正 (EnerPres / no)
```

### 温度耦合段
```
tcoupl = v-rescale           ; v-rescale / nose-hoover / berendsen / langevin
tc-grps = Protein Non-Protein  ; 温度耦合组
tau_t = 0.1 0.1              ; 时间常数 (ps)
ref_t = 300 300              ; 参考温度 (K)
```

### 压力耦合段
```
pcoupl = Parrinello-Rahman   ; Parrinello-Rahman / Berendsen / C-rescale
pcoupltype = isotropic       ; isotropic / semiisotropic / anisotropic / surface-tension
tau_p = 2.0                  ; 时间常数 (ps)
ref_p = 1.0 1.0              ; 参考压力 (bar)
compressibility = 4.5e-5     ; 压缩系数 (bar⁻¹)
```

### 约束段
```
constraints = h-bonds        ; h-bonds / all-bonds / none
constraint-algorithm = LINCS ; LINCS (默认)
lincs_iter = 1               ; LINCS 迭代次数
lincs_order = 4              ; LINCS 展开阶数
```

### 周期边界段
```
pbc = xyz                    ; xyz / xy / no
```

### 初始速度段
```
gen-vel = yes                ; 生成初始速度
gen-temp = 300               ; 初始温度 (K)
gen-seed = -1                ; 随机种子 (-1 = 系统熵)
```

## 关键模块速查
| 模块 | 功能 | 典型用法 |
|------|------|---------|
| `pdb2gmx` | PDB → GROMACS 拓扑 + 坐标 | `gmx pdb2gmx -f in.pdb -o out.gro -p topol.top -water spce -ff amber99sb-ildn` |
| `editconf` | 定义盒子 | `gmx editconf -f in.gro -o out.gro -c -d 1.0 -bt dodecahedron` |
| `solvate` | 添加溶剂 | `gmx solvate -cp solute.gro -cs spc216.gro -o solvated.gro -p topol.top` |
| `genion` | 添加离子 | `gmx genion -s ions.tpr -o neutral.gro -p topol.top -pname NA -nname CL -neutral` |
| `grompp` | 预处理（生成 tpr） | `gmx grompp -f input.mdp -c coord.gro -p topol.top -o output.tpr` |
| `mdrun` | 运行 MD | `gmx mdrun -v -deffnm md -nb gpu -pme gpu` |
| `trjconv` | 轨迹处理 | `gmx trjconv -s ref.tpr -f traj.xtc -o centered.xtc -pbc mol -center` |
| `rms` | RMSD 分析 | `gmx rms -s ref.tpr -f traj.xtc -o rmsd.xvg` |
| `rmsf` | RMSF 分析 | `gmx rmsf -s ref.tpr -f traj.xtc -o rmsf.xvg` |
| `gyrate` | 回转半径 | `gmx gyrate -s ref.tpr -f traj.xtc -o gyrate.xvg` |
| `hbond` | 氢键分析 | `gmx hbond -s ref.tpr -f traj.xtc -num hbnum.xvg` |
| `sasa` | 溶剂可及表面积 | `gmx sasa -s ref.tpr -f traj.xtc -o sasa.xvg` |
| `cluster` | 构象聚类 | `gmx cluster -s ref.tpr -f traj.xtc -method gromos -cutoff 0.2` |
| `covar` | 协方差矩阵（PCA） | `gmx covar -s ref.tpr -f traj.xtc -o eigenval.xvg -v eigenvec.trr` |
| `anaeig` | PCA 投影分析 | `gmx anaeig -s ref.tpr -f traj.xtc -v eigenvec.trr -proj proj.xvg` |
| `energy` | 提取能量数据 | `gmx energy -f ener.edr -o potential.xvg` |
| `mindist` | 最小距离计算 | `gmx mindist -s ref.tpr -f traj.xtc -od mindist.xvg` |
| `wham` | WHAM 分析 | `gmx wham -it tpr.list -if force.list -o profile.xvg` |
| `bar` | BAR 自由能分析 | `gmx bar -f dhdl_*.xvg -o bar_results.xvg` |

# workflow_pipeline
## 标准蛋白质 MD 工作流（端到端）

```
┌─────────────┐
│ 1. 体系准备  │  PDB 获取 → pdb2gmx → editconf → solvate → genion
└──────┬──────┘
       │ processed.gro + topol.top + ions.mdp
       ▼
┌─────────────┐
│ 2. 能量最小化│  grompp → mdrun (steepest descent / CG)
└──────┬──────┘
       │ em.gro
       ▼
┌─────────────┐
│ 3. NVT 平衡  │  grompp → mdrun (velocity-rescale, 无压耦合)
└──────┬──────┘
       │ nvt.gro + nvt.cpt
       ▼
┌─────────────┐
│ 4. NPT 平衡  │  grompp → mdrun (Parrinello-Rahman, 恒温恒压)
└──────┬──────┘
       │ npt.gro + npt.cpt
       ▼
┌─────────────┐
│ 5. 生产 MD   │  grompp → mdrun (Nose-Hoover / Parrinello-Rahman)
└──────┬──────┘
       │ md.xtc + md.edr
       ▼
┌─────────────┐
│ 6. 分析      │  trjconv → rms/rmsf/gyrate/hbond/sasa/cluster/covar
└─────────────┘
```

## 各阶段 mdp 关键差异对比
| 参数 | EM | NVT 平衡 | NPT 平衡 | 生产 MD |
|------|-----|---------|---------|--------|
| `integrator` | steep | md | md | md |
| `dt` (ps) | N/A | 0.002 | 0.002 | 0.002 |
| `nsteps` | 50000 | 50000 | 50000 | 50000000 |
| `tcoupl` | N/A | v-rescale | v-rescale | nose-hoover |
| `tau_t` (ps) | N/A | 0.1 | 0.1 | 2.0 |
| `pcoupl` | no | no | Parrinello-Rahman | Parrinello-Rahman |
| `ref_p` (bar) | N/A | N/A | 1.0 | 1.0 |
| `gen-vel` | no | yes | no | no |
| `constraints` | none | h-bonds | h-bonds | h-bonds |
| `define` | N/A | -DPOSRES | -DPOSRES | 无（或注释掉） |

## 特殊工作流管道

### 配体-蛋白结合自由能（FEP）
```
体系准备 → EM → NVT → NPT
  → 创建 lambda 窗口（0...1, 20-40 步）
  → 对每个 lambda 窗口：grompp → mdrun
  → gmx bar 分析
```

### 伞形采样（PMF 计算）
```
体系准备 → EM → NVT → NPT
  → 牵拉 MD（pull code）
  → trjconv 提取窗口构型（-sep）
  → 对每个窗口：grompp → mdrun
  → gmx wham 分析
```

### 膜蛋白模拟
```
体系准备 → pdb2gmx → editconf（注意 z 方向留膜空间）
  → 插入膜 → solvate → genion
  → EM → NVT（tc-grps 分离脂质与其他）
  → NPT（semiisotropic，xy 独立于 z）
  → 生产 MD
```

### 粗粒化（MARTINI）模拟
```
全原子 PDB → martinize2.py（转换为 CG 拓扑 + 坐标）
  → editconf → solvate（MARTINI 水珠子）
  → genion（添加粗粒化离子）
  → EM → NVT/NPT（时间步长可达 20-40 fs）
  → 生产 MD（可达微秒-毫秒级模拟）
```

# execution_resources
## 计算资源配置建议
| 体系规模 | 硬件配置 | 预期性能 | 100 ns 所需时间 |
|---------|---------|---------|---------------|
| ~25K 原子（溶菌酶+水） | 1×V100 GPU + 8 cores | ~1.5 μs/day | ~1.6 小时 |
| ~100K 原子（膜蛋白+水） | 1×A100 GPU + 16 cores | ~600 ns/day | ~4 小时 |
| ~500K 原子 | 2×A100 GPU + 32 cores | ~300 ns/day | ~8 小时 |
| ~1M 原子 | 4×A100 GPU + 64 cores | ~150 ns/day | ~16 小时 |

## 内存需求估算
- 基础内存：每 1000 原子约占用 1-2 MB（拓扑 + 近邻列表）
- GPU 显存：短程非键力计算的原子对缓存（~100K 原子约需 2-4 GB 显存）
- 如果有 PME offload 到 GPU，需额外 ~1 GB 显存
- 磁盘存储：轨迹（.xtc）约 50-200 KB/帧（取决于体系大小和输出精度）

## 磁盘空间估算
| 阶段 | 输出文件 | 典型大小 |
|------|---------|---------|
| pdb2gmx | processed.gro, topol.top, posre.itp | ~1-10 MB |
| solvate | solvated.gro, spc216.gro | ~1-10 MB |
| EM | em.gro, em.edr, em.log | ~5-20 MB |
| NVT/NPT | .gro, .cpt, .edr, .xtc | ~50-500 MB |
| 生产 MD (100 ns) | .xtc, .edr, .cpt | ~2-20 GB（取决于输出频率） |

## 输出频率对磁盘占用的影响
```
nstxout-compressed = 5000  (10 ps/帧)  → ~2 GB / 100 ns（~100K 原子体系）
nstxout-compressed = 1000  (2 ps/帧)   → ~10 GB / 100 ns
nstxout-compressed = 100   (0.2 ps/帧) → ~100 GB / 100 ns
```

# operation_limits
## 功能边界
- GROMACS 不处理电子结构，不能替代 DFT 计算
- 经典力场无法描述键断裂/形成（除非使用包特殊参数化的反应性力场）
- 标准全原子模拟时间尺度通常为 ns-μs 级，无法模拟秒级以上过程
- 非标准残基（配体、修饰氨基酸、辅因子）需要额外准备力场参数
- 显式溶剂模拟的盒子尺寸受计算资源约束（通常 < 10⁷ 原子）

## 力场适用范围
| 力场 | 适用体系 | 不适用 |
|------|---------|-------|
| AMBER | 蛋白质、核酸 | 含过渡金属的金属蛋白（需额外参数） |
| CHARMM | 蛋白质、核酸、脂质、糖类 | 非标准小分子（需 CGenFF 参数化） |
| OPLS-AA | 有机小分子、蛋白质 | 核酸模拟不如 AMBER/CHARMM |
| GROMOS | 蛋白质、聚合物、膜 | 折叠后蛋白（联合原子精度有限） |
| MARTINI | 膜蛋白、大规模自组装 | 蛋白质二级结构变化、精细构象 |

## 常见限制与解决
- **非标准残基/配体参数缺失**：使用 `acpype`（Antechamber Python Parser）从 GAFF 力场生成 GROMACS 参数，或使用 CGenFF（CHARMM General Force Field）生成 CHARMM 兼容参数
- **力场无法描述金属配位**：需额外添加键连参数或使用 dummy model + 限制势
- **pdb2gmx 报缺失原子**：修复 PDB 中缺失的残基或原子（使用 Modeller、Swiss-Model 等）
- **跨版本 tpr 不兼容**：不同 GROMACS 主版本（如 2022 vs 2024）的 tpr 通常不兼容，需用同一版本重新 grompp
- **大体系内存不足**：减少近邻列表缓冲区 (`verlet-buffer-tolerance` 增大)；使用更短的 `rlist`
- **非水溶剂（如甲醇、DMSO）**：GROMACS 自带部分有机溶剂拓扑（$GMXDATA/top/），如需更复杂溶剂需手动参数化
