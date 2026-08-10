# description
`gromacs` 工具原语的规划重点是为生物分子和软物质体系的分子动力学模拟任务设计完整的 GROMACS 工作流：根据体系类型（蛋白质/DNA/脂质膜/高分子/粗粒化）确定力场、水模型、系综序列、模拟参数和计算资源需求，输出可执行的 mdp 配置组合、提交脚本模板和风险清单。

# when_to_use
## 生物分子类（核心场景）
- 蛋白质折叠/构象动力学模拟（折叠态稳定性、domain 运动、无序蛋白 ensemble）
- 蛋白质-配体结合模拟（药物设计、虚拟筛选验证）
- 蛋白质-蛋白质相互作用（PPI，复合体稳定性和结合自由能）
- 核酸模拟（DNA 双螺旋稳定性、RNA 折叠、DNA-蛋白质复合体）
- 膜蛋白模拟（跨膜通道、GPCR 激活机制、离子通道通透性）
- 脂质膜/脂双层模拟（膜流动性、相变、脂筏形成）
- 糖类/糖蛋白模拟（糖基化对蛋白稳定性的影响）

## 软物质类
- 高分子溶液/熔体模拟（聚合度、链构象、自组装）
- 表面活性剂/胶束/囊泡自组装
- 离子液体模拟
- 纳米粒子在生物界面的行为

## 特殊方法类
- 自由能计算：配体结合自由能（FEP）、小分子溶剂化自由能、pKa 计算
- 增强采样：伞形采样（umbrella sampling）、拉伸动力学（steered MD）、元动力学（metadynamics，通过 PLUMED 插件）
- 构象分析：主成分分析（PCA）、聚类分析、Markov 状态模型（MSM）构建
- 氢键/二级结构/溶剂可及表面（SASA）等经典分析

## 粗粒化模拟类
- 使用 MARTINI 力场的大尺度膜/蛋白质/纳米粒子体系
- 时间尺度可达 μs-ms 级别，空间尺度可达 ~10⁷ CG 珠子

# when_not_to_use
- 需要第一性原理电子结构计算 → 应使用 VASP、CP2K、Quantum ESPRESSO
- 材料体系（金属、半导体、陶瓷、合金）的经典 MD → LAMMPS 更合适（力场更丰富，材料建模更灵活）
- 含化学反应（键断裂/形成）的模拟 → 使用 ReaxFF（LAMMPS/AMS）、CP2K、DFTB 或 AIMD
- 量子化学单分子计算 → 使用 Gaussian、ORCA 等
- 仅需要分子对接（快速配体筛选）→ 使用 AutoDock Vina、Glide 等对接软件
- 仅需要同源建模（初始结构预测）→ 使用 Modeller、AlphaFold、Swiss-Model
- 长时间尺度（ms-s）蛋白折叠模拟 → 考虑使用 Folding@home（专用分布式计算）或 AlphaFold 等 AI 预测
- 非平衡态方法论要求的电子激发/光化学/辐射过程 → 量子化学/非绝热动力学方法

# inputs
- **体系信息**：分子类型（蛋白质/DNA/RNA/脂质/高分子/配体）、残基数/原子数（大致规模）、是否有非标准残基/配体/辅因子、翻译后修饰（PTM）情况
- **结构来源**：实验结构（X-ray/NMR/cryo-EM PDB）、同源建模（Modeller/Swiss-Model）、AI 预测（AlphaFold/ESMFold）
- **模拟目标**：构象稳定性评估、平衡态采样、自由能计算、机理探索、验证/发现
- **精度要求**：力场级别（AMBER/CHARMM/OPLS/GROMOS/MARTINI）、水模型选择、截断半径、PME 精度
- **时间尺度**：期望模拟时间（如 100 ns / 1 μs）、是否有特殊加速需求
- **资源约束**：可用计算节点数、每节点 GPU 数量和型号、运行时间限制、磁盘空间配额
- **输出需求**：轨迹保存间隔、分析指标（RMSD/RMSF/Rg/SASA/氢键/cluster/PCA/PMF）、是否需要中间 checkpoint
- **特殊需求**：是否需要自由能计算、增强采样、可调力常数、配体参数化方法

# outputs
- 完整的阶段 mdp 文件组合（em.mdp, nvt.mdp, npt.mdp, md.mdp）及各阶段的参数说明
- 力场/水模型选择建议及对应的 pdb2gmx 命令
- 体系准备步骤说明（pdb2gmx → editconf → solvate → genion 完整命令）
- GPU/多节点资源使用建议及 SLURM 作业提交脚本模板
- 模拟参数推荐表：时间步长、系综类型、耦合方法、截断半径、PME 参数、约束方案
- 分析流程建议：推荐的 GROMACS 分析命令及外部工具（VMD/PyMOL/MDAnalysis/mdtraj）
- 风险清单：力场/水模型不匹配、参数缺失、盒子尺寸不足、步长稳定性、平衡充分性、磁盘空间

# procedure
1. **体系分析**：确认分子类型（蛋白/核酸/脂质/复合体）、残基/原子数、是否有非标准残基、PTM 位点
2. **结构准备评估**：
   - 检查 PDB 完整性（缺失残基/原子/loop 区）
   - 判断是否需要结构修复（Modeller/Swiss-Model 补全缺失 loop）
   - 确定质子化状态（HIS 异构体、CYS 二硫键、ASP/GLU/LYS 在特定 pH 下的带电状态）
3. **力场选型**：
   - 蛋白质主流（无特殊要求）→ AMBER99SB-ILDN 或 AMBER14SB + TIP3P
   - 蛋白质+核酸 → CHARMM36m + CHARMM TIP3P
   - 含无序区蛋白 → AMBER99SB-disp 或 CHARMM36m
   - 含小分子配体 → GAFF2（acpype）或 CGenFF
   - 膜蛋白 → CHARMM36m（脂质参数完善）或 MARTINI（粗粒化大尺度）
   - 粗粒化 → MARTINI 3
   - 联合原子（快速扫描）→ GROMOS54A7
4. **水模型选型**：与力场严格匹配：
   - AMBER 家族 → TIP3P
   - CHARMM → CHARMM TIP3P（力场内建）
   - OPLS-AA → SPC/E 或 TIP4P
   - GROMOS → SPC 或 SPC/E
5. **盒子设计**：
   - 球状蛋白 → 菱形十二面体（`-bt dodecahedron`, 节省 29% 溶剂）
   - 膜蛋白 → 三斜或长方形（z 轴留膜空间）
   - 纤维状蛋白/DNA → 立方或长方形（匹配形状）
   - 最小溶剂距离 `-d` → 1.0-1.5 nm（确保 > 2×切截半径）
6. **离子环境设置**：
   - 体系电荷中和（`genion -neutral`）
   - 生理离子浓度（`-conc 0.15`，对应 ~150 mM NaCl）
   - 离子种类选择（Na⁺/Cl⁻ 通用，K⁺ 用于胞内环境，Mg²⁺ 用于核酸）
7. **系综序列设计**：
   - 能量最小化 → steepest descent（Fmax < 1000 kJ/mol/nm，最多 50000 步）
   - NVT 平衡 → v-rescale 恒温器，50-500 ps，位置限制重原子
   - NPT 平衡 → 先 Berendsen（100 ps，稳定密度），再 Parrinello-Rahman（100-500 ps）
   - 生产 MD → Nose-Hoover + Parrinello-Rahman，时长依研究目标而定
8. **时间步长与约束设定**：
   - 标准：`dt = 0.002 ps`（2 fs）+ `constraints = h-bonds`（LINCS）
   - 加速：氢虚拟位点 + `constraints = all-bonds`，`dt = 0.004-0.005 ps`（4-5 fs）
   - 粗粒化：`dt = 0.02-0.04 ps`（20-40 fs）
9. **输出配置**：
   - 压缩轨迹（xtc）：每 10-50 ps 一帧
   - 能量（edr）：每 10 ps 一次
   - 日志（log）：每 10 ps 一次
   - 不输出速度和力以节省空间
   - 对于长模拟（>500 ns），适当增大输出间隔
10. **资源估算**：
    - 根据原子数和参考文献经验值估算 ns/day 性能
    - 确定所需 GPU 数量和节点数
    - 计算总模拟时间对作业墙钟时间的比例
11. **脚本输出**：
    - 生成所有 mdp 文件（em/nvt/npt/md）
    - 生成体系准备命令集合
    - 生成 SLURM 提交脚本（含 `-maxh` 和断点续传逻辑）
    - 输出分析命令模板

# constraints
- 不在 GROMACS 工作流中进行力场参数拟合/参数化——这需要外部工具（如 GAFF/acpype、CGenFF、ATB、SwissParam）
- pdb2gmx 要求输入 PDB 中不含非标准残基（或需要手动力场参数 `[atomtypes]` / `[bonded]` 定义在 itp 文件中）
- PME 要求体系总电荷为零（`genion -neutral` 或手动添加抗衡离子）
- 模拟盒子所有方向尺寸必须 > 2 × 截断半径（`rlist`），否则触发 GROMACS 运行时错误
- 单次 grompp 后不更改拓扑文件中的分子数（否则需重新 grompp）
- mdp 中 `tc-grps` 需与索引文件一致：如果使用 `Protein Non-Protein` 分离耦合，确保蛋白质的 ndx 组正确
- 位置限制（`-DPOSRES`）仅用于平衡阶段，生产阶段必须注释掉
- 力场与水模型必须严格匹配——混用会导致非物理结果
- 初始速度随机种子建议显式设置（非 `-1`）以确保可复现性
- 对于含配位键/二硫键的体系，在 pdb2gmx 前确认连接信息（`specbond.dat`）
- 仅在所有重原子力 < 1000 kJ/mol/nm 后才可进入温度平衡
- 运行期间保留所有 checkpoint 文件（.cpt），直至最终结构确认无误
- 轨迹文件（.xtc）的精度和输出频率在事先确定，避免后期因轨迹精度不足需重新模拟

# next_phase_recommendation
- **力场参数库建设**：记录常用非标准残基/配体的参数化流程和已验证的参数文件路径
- **模拟模板库**：按体系类型（可溶蛋白/膜蛋白/DNA/RNA/复合体/粗粒化）归档验证过的 mdp 文件集
- **分析管道集成**：将 GROMACS 分析输出与 Python 分析框架（MDAnalysis/mdtraj/pyemma）连接，形成自动化分析管道
- **增强采样集成**：建立 PLUMED 插件的标准调用模板，覆盖 metadynamics/umbrella sampling/OPES 等常用方法
- **配体参数化自动化**：建立 acpype/CGenFF 的参数化脚本，实现配体 PDB → GROMACS ITP 的自动化流程
- **数据管理规范**：建立轨迹文件的压缩、归档和元数据记录规范

# fallback
- **力场不适用（非标准体系）**：切换至 GAFF2（通过 acpype）+ AMBER 力场格式，适用于绝大多数有机小分子；或使用 CGenFF 生成 CHARMM 兼容参数
- **pdb2gmx 失败（缺失原子/残基）**：使用 AlphaFill 或 Modeller 补全缺失原子；如仍失败，移除缺失残基（仅限非关键区域）；或手动编辑 PDB 补全原子
- **模拟不稳定（崩溃/LINCS 警告）**：减小时间步长（2 fs → 1 fs 或 0.5 fs）；增加 EM 迭代步数或降低 EM 收敛容限；降低初始温度（从 300 K 降至 100 K，逐步升温）
- **平衡不收敛**：延长 NVT/NPT 平衡时间（如从 100 ps 至 500 ps）；降低温度耦合时间常数 tau_t（更紧的耦合）；先使用 Berendsen 恒压器再切换至 Parrinello-Rahman
- **计算速度过慢**：减小截断半径（1.2 nm → 1.0 nm）；降低 PME 精度（fourierspacing 从 0.10 增至 0.14 nm）；使用氢虚拟位点 + 增大 dt；减少轨迹输出频率；启用 `-update gpu` 减少 CPU-GPU 传输
- **磁盘空间不足**：增大 xtc 输出间隔；使用压缩轨迹（xtc 而非 trr）；不输出速度和力；模拟结束后使用 `gmx trjconv -dump` 提取关键帧删除完整轨迹
- **内存不足**：减少 MPI rank 数（释放冗余缓存）；增加 `verlet-buffer-tolerance` 以减少近邻列表大小；减少 `rlist`；如必要，缩减体系规模（如减小溶剂盒子）
- **GPU 显存不足**：将 PME 保持在 CPU（不使用 `-pme gpu`）；减少原子数（缩小盒子）；使用更低精度的 GPU 计算模式
- **跨版本兼容性问题**：确认集群中 GROMACS 版本；如需要不同版本，使用 singularity/docker 容器提供特定 GROMACS 版本环境
