# 生物分子分子动力学模拟 (biomolecular-md-simulation)

## 任务目标
基于 OpenMM 与 MDAnalysis，从清理后的 PDB 出发搭建溶剂化体系，跑能量最小化 + NVT/NPT 平衡 + 生产 MD，再对轨迹做 RMSD、RMSF、蛋白-配体接触等分析。目标问题包括蛋白稳定性/突变影响、配体结合模式与驻留、构象采样、蛋白-蛋白界面、膜体系、IDR 集合、结合或构象自由能估算。

## 适用范围 / 不适用场景
适用：可溶蛋白、蛋白-配体复合物、蛋白-蛋白、膜蛋白（配 CHARMM36m）、核酸（AMBER99-bsc1 或 AMBER14）、内在无序蛋白（ff19SB 或 CHARMM36m）；小分子配体经 OpenFF Toolkit / GAFF2 参数化后并入体系；轨迹分析支持 DCD、XTC、TRR 等主流格式。
不适用：源文件未覆盖 QM/MM、增强采样（metadynamics、umbrella sampling 等）具体实现，也未给出生产级结合自由能脚本；此类需求需外接专门工具，本卡仅提供 OpenMM+MDAnalysis 常规路线。

## 实体槽（Entity Slots）
- slot:system_type:protein / protein-ligand / membrane / nucleic-acid / idr
- slot:forcefield:amber14-all.xml / charmm36m / amber99-bsc1 / ff19sb
- slot:water_model:amber14-tip3pfb / tip3p
- slot:platform:cuda / opencl / cpu（自动降级）
- slot:timestep:2fs-hbonds / 4fs-hmr
- slot:ensemble:nvt / npt
- slot:ligand_ff:openff-2.0.0 / gaff2-acpype

## 输入输出契约
输入：清理后的 PDB（原始 PDB 先经 PDBFixer 补缺失残基/原子、替换非标准残基、按 pH 加氢）；配体经 SMILES → OpenFF Toolkit 生成 conformer 与 Interchange。
输出：`minimized.pdb`（最小化后结构）；`{prefix}_log.txt`（StateDataReporter：step、potentialEnergy、kineticEnergy、temperature、volume、density、speed）；`{prefix}_traj.dcd`（DCDReporter）；`npt_checkpoint.chk`（CheckpointReporter，每 50000 步）；分析产物如 `rmsd.png`（matplotlib，dpi=150）。

## 方法路线（可替换）
- 主路线：`prepare_system_from_pdb` → `minimize_energy` → `run_nvt_equilibration` → `run_npt_production` → MDAnalysis 分析。
- 力场-水模型配对（源表）：标准蛋白 amber14-all.xml + amber14/tip3pfb.xml；蛋白+小分子 amber14 + GAFF2 + TIP3P-FB；膜蛋白 CHARMM36m + TIP3P；核酸 AMBER99-bsc1 或 AMBER14 + TIP3P；IDR ff19SB 或 CHARMM36m + TIP3P。
- 平台降级：优先 `Platform.getPlatformByName('CUDA')` + `{'DeviceIndex': '0', 'Precision': 'mixed'}`，异常回落 OpenCL，再回落 CPU。
- 替代引擎（源列出，非本卡实现）：GROMACS、NAMD；系统搭建可用 CHARMM-GUI；辅助工具 AmberTools。
- 配体参数化替代：`openff.toolkit.Molecule.from_smiles` → `generate_conformers(n_conformers=1)` → `openff-2.0.0.offxml` 走 Interchange，或走 ACPYPE 生成 GAFF2。

## 操作序列（Operations）
1. 安装：`conda install -c conda-forge openmm mdanalysis nglview`，或 `uv pip install openmm mdanalysis`；配体参数化再 `uv pip install openff-toolkit`。
2. 修 PDB：`PDBFixer(filename=input_pdb)` → `findMissingResidues` / `findNonstandardResidues` / `replaceNonstandardResidues` / `removeHeterogens(True)` / `findMissingAtoms` / `addMissingAtoms` / `addMissingHydrogens(ph=7.0)` → `PDBFile.writeFile`。
3. 建系：`PDBFile(pdb)` + `ForceField(forcefield_name, water_model)` → `Modeller.addHydrogens(forcefield)` → `addSolvent(forcefield, model='tip3p', padding=10*angstroms, ionicStrength=0.15*molar)` → `createSystem(nonbondedMethod=PME, nonbondedCutoff=1.0*nanometer, constraints=HBonds, rigidWater=True, ewaldErrorTolerance=0.0005)`。
4. 最小化：`LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.004*picoseconds)` 建 `Simulation`；`simulation.minimizeEnergy(tolerance=10*kilojoules_per_mole/nanometer, maxIterations=1000)`；打印初/末势能并写 `minimized.pdb`。
5. NVT：`context.setVelocitiesToTemperature(300*kelvin)`，清 `simulation.reporters`，加 StateDataReporter（report_interval=1000，含 step/potentialEnergy/kineticEnergy/temperature/volume/speed）+ DCDReporter，跑 `n_steps=50000`（约 100 ps，2 fs 步长）。
6. NPT 生产：`system.addForce(MonteCarloBarostat(pressure*bar, temperature*kelvin, 25))` → `context.reinitialize(preserveState=True)`；reporters 换 StateDataReporter（report_interval=5000，含 density）+ DCDReporter + CheckpointReporter(每 50000 步)；跑 `n_steps=500000`（约 1 ns）。
7. 轨迹分析：`mda.Universe(topology_file, trajectory_file)`；`align.AlignTraj(u, u, select='backbone', in_memory=True).run()` → `rms.RMSD(u, select='backbone', ref_frame=0).run()` 取 `R.results.rmsd`（列：frame, time, RMSD）；`rms.RMSF(atoms).run(start=start_frame)` 按残基求平均；接触图用 `contacts.contact_matrix(protein.positions, ligand.positions, radius=4.5)` 逐帧扫。

## 验证契约（Validations）
- 必最小化：原始 PDB 有立体冲突，`minimizeEnergy` 是所有后续步骤前置。
- 平衡阶梯：NVT 50–100 ps → NPT 100–500 ps → 生产；分析时丢弃前 20–50% 视为平衡段。
- 步长：`constraints=HBonds` 下标准 2 fs；启用 HMR（氢质量重分配）后可到 4 fs。
- 长程静电：solvated 体系必须周期性边界 + PME，`ewaldErrorTolerance=0.0005`；对带电体系比 cutoff 更准。
- 检查点：MD 会失败，CheckpointReporter 是重启前提；`context.reinitialize(preserveState=True)` 用于加 barostat 后保留状态。
- RMSD 图：`plot_rmsd` 会画均值参考线（`axhline(mean)`）用来判是否收敛。
- GPU 优势：10–100× 于 CPU，`Precision='mixed'` 是 CUDA 上的常用组合。

## 资源引用（Resources）
- 引擎/库：OpenMM、MDAnalysis、PDBFixer、OpenFF Toolkit（`openff-2.0.0.offxml`）、nglview（可视化）、matplotlib。
- 替代工具：GROMACS、NAMD、CHARMM-GUI、AmberTools、ACPYPE。
- 官方文档：https://openmm.org/documentation.html、https://docs.mdanalysis.org/、https://manual.gromacs.org/、https://www.ks.uiuc.edu/Research/namd/、https://charmm-gui.org/、https://ambermd.org/AmberTools.php。
- 关键论文：Eastman P et al. (2017) PLOS Computational Biology, PMID 28278240（OpenMM）；Michaud-Agrupal N et al. (2011) J Computational Chemistry, PMID 21500218（MDAnalysis）。

## 前后置任务（Task Graph）
无强制前后置。上游常见：结构准备（PDBFixer、加氢、溶剂化）、配体参数化（OpenFF Toolkit / ACPYPE-GAFF2）、必要时来自对接任务的复合物结构。下游常见：RMSD/RMSF/接触分析、结合自由能估算（本卡未提供生产级脚本，需外接）。

## 缺口与降级（Fallback / Gap）
- CUDA 不可用：`try/except` 三级降到 OpenCL 再降到 CPU，速度损失 10–100×；生产跑尽量锁 CUDA。
- 原始 PDB 有缺失残基/非标准残基/多余 heterogen：走 `fix_pdb(input_pdb, output_pdb, ph=7.0)`；pH 依赖加氢用 `addMissingHydrogens(ph)`。
- 配体缺力场参数：OpenFF Toolkit + `openff-2.0.0.offxml` 走 Interchange，或 ACPYPE 生成 GAFF2；膜蛋白换 CHARMM36m。
- 步长/精度权衡：默认 2 fs + HBonds 约束；需更快时启用 HMR 到 4 fs（源列为标准做法）。
- 生产中断：从 `npt_checkpoint.chk` 重启，避免整段重跑。
- 增强采样 / QM-MM / 生产级结合自由能：源未给出实现，属明确缺口，须外接工具而非在本卡内自行扩展。
