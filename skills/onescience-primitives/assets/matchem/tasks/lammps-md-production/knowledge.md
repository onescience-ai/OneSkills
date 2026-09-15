# LAMMPS 分子动力学生产运行 (lammps-md-production)

## 任务目标
在 LAMMPS 中使用 DeePMD 机器学习势或 ReaxFF 反应力场执行分子动力学生产模拟：准备 input.lammps 脚本、选择系综（NVE/NVT/NPT）、设置时间步长与热浴/压浴参数、配置电荷平衡（ReaxFF QEq）、运行模拟并输出轨迹与热力学数据。支持在线模式（uvx 按需部署）与离线模式（用户指定可执行文件）。

## 适用范围 / 不适用场景
适用：DeePMD 势驱动的凝聚相 MD（units metal，pair_style deepmd）；ReaxFF 反应力场 MD（units real，pair_style reaxff + fix qeq/reaxff）；NVE/NVT/NPT 系综生产运行与平衡；高温反应动力学模拟（ReaxFF，需小时间步 0.1 fs 或更小）。
不适用：路由层不猜测离线可执行文件名称或 module；不适用于非 LAMMPS 引擎的 MD；DeePMD 模型训练属上游任务。

## 实体槽（Entity Slots）
- potential_type: deepmd / reaxff
- ensemble: NVE / NVT / NPT
- units: metal（DeePMD，时间 ps，距离 Å）/ real（ReaxFF，时间 fs）
- timestep: 0.0005 ps = 0.5 fs（DeePMD 典型）；0.25 fs 或 0.1 fs（ReaxFF，高温需更小）
- temperature: 目标温度（K）
- pressure: 目标压力（NPT 时）
- tau_t: 热浴阻尼参数（metal 单位 ps；real 单位 fs）
- tau_p: 压浴阻尼参数（NPT）
- model_file: graph.pb / graph_compressed.pb（DeePMD）或 ffield.reax.*（ReaxFF）
- data_file: data.system（LAMMPS 数据文件）
- atom_style: atomic（DeePMD）/ charge（ReaxFF，需 QEq）
- nsteps: 总步数
- dump_freq / thermo_freq: 轨迹与热力学输出频率

## 输入输出契约
输入：
- LAMMPS 数据文件（data.system）：原子坐标、类型、模拟盒
- 势函数文件：DeePMD model（graph.pb / graph_compressed.pb）或 ReaxFF ffield（ffield.reax.*）
- 原子类型→元素映射：DeePMD 需 mass 命令设置每类型质量；ReaxFF 通过 pair_coeff 尾部元素符号映射
- 系综/温度/压力/时间步长/步数
- 执行模式：在线（uvx）或离线（用户指定 lmp/lmp_mpi/srun）

输出：
- log.lammps：热力学日志（step temp pe ke etotal press vol lx ly lz xy xz yz）
- traj.lammpstrj：原子轨迹（dump custom，含 id type x y z；ReaxFF 可加 q）
- restart 文件（若配置）
- ReaxFF 可选：fix reaxff/species 输出物种时间序列

## 方法路线（可替换）
DeePMD 路线（units metal）：
- pair_style deepmd graph_compressed.pb + pair_coeff * *
- atom_style atomic，boundary p p p，neighbor 1.0 bin
- NVT：fix nvt temp T T tau_t；NPT：fix npt temp T T tau_t iso P P tau_p；NVE：fix nve
- velocity all create T seed
- timestep 0.0005（0.5 fs）

ReaxFF 路线（units real）：
- pair_style reaxff NULL + pair_coeff * * ffield.reax C H O（元素映射）
- atom_style charge，boundary p p p，neighbor 2.0 bin，neigh_modify every 1 delay 0 check yes
- fix qeq/reaxff every cutlo cuthi tol reaxff（电荷平衡，必须）
- NVT：fix nvt temp T T tau_t
- timestep 0.25 fs（高温降至 0.1 fs 或 0.05 fs）
- 可选：fix reaxff/species 追踪反应产物

执行模式：
- 在线 DeePMD：`uvx --from lammps --with deepmd-kit[gpu,torch,lmp] lmp -in input.lammps`
- 在线 ReaxFF：`uvx --from 'lammps[mpi]' lmp -in input.lammps`
- 离线：用户指定 `lmp -in input.lammps` / `mpirun -np 8 lmp_mpi -in input.lammps` / `srun lmp -in input.lammps`

## 操作序列（Operations）
1. 确认执行模式：在线（uvx 可用）或离线（询问用户可执行文件）
2. 收集最小输入：势函数路径、数据文件、元素/质量映射、系综、温度、时间步长、步数
3. 编写 input.lammps：units → boundary → atom_style → read_data → mass/pair_coeff → pair_style → thermo/dump → velocity → fix → timestep → run
4. ReaxFF 额外：设置 atom_style charge、fix qeq/reaxff、neigh_modify
5. 短时间 NVE 稳定性检查（推荐）：验证 etotal 漂移合理、不发散
6. 运行生产模拟
7. 汇总输出：执行命令、输入脚本路径、数据/模型路径、log 路径、轨迹路径、是否成功、警告/错误

## 验证契约（Validations）
- 质量设置完整：DeePMD 需 mass 命令为每类型设质量，否则 velocity create/thermostat 报错 "Not all per-type masses are set"
- QEq 配置（ReaxFF）：必须包含 fix qeq/reaxff，参数从 ffield 文件提取（尾部 reaxff 关键字）
- 电荷字段（ReaxFF）：atom_style charge 或 full，初始电荷从 data 文件或 set 命令初始化，不可用 fix property/atom q 替代
- NVE 稳定性：短时间 NVE 验证 etotal 漂移合理，发散则减小 timestep
- 时间步长安全：DeePMD 典型 0.5 fs；ReaxFF 0.25 fs，含 H 高温需 0.1 fs 或 0.05 fs
- 元素映射一致：pair_coeff 尾部元素顺序必须与 data 文件 atom type 对应
- 在线模式 libmpi 错误：若见 "error while loading shared libraries: libmpi.so"，改用 lammps[mpi] 或安装 MPI 运行时

## 资源引用（Resources）
- 引擎：LAMMPS（https://docs.lammps.org/）
- DeePMD 插件：deepmd-kit（pair_style deepmd）
- ReaxFF 力场：LAMMPS REAXFF package（pair_style reaxff、fix qeq/reaxff、fix reaxff/species）
- 力场文件来源：LAMMPS potentials/ffield.reax.*（https://github.com/lammps/lammps/tree/develop/potentials）
- 在线部署：uvx --from lammps --with deepmd-kit[gpu,torch,lmp]（DeePMD）；uvx --from 'lammps[mpi]'（ReaxFF）
- 势函数上游：DeePMD model 来自 deepmd-potential-training 任务产出的冻结模型（model.pth / graph.pb）

## 前后置任务（Task Graph）
无强制前后置。DeePMD 路线的势函数模型（graph.pb / graph_compressed.pb）通常来自上游 DeePMD 训练任务（dp train → dp freeze 产出）。ReaxFF 路线的 ffield 文件来自已发表参数化或 LAMMPS 官方势函数库。

## 缺口与降级（Fallback / Gap）
- 离线可执行文件未知：不猜测，询问用户使用 lmp / lmp_mpi / mpirun / srun 或 HPC module
- 质量未定义：在 input.lammps 中用 mass 命令显式设置每类型原子质量
- ReaxFF ffield 不可用：指向 LAMMPS 官方 potentials 目录，不编造力场文件
- 模拟发散：减小 timestep（0.25→0.1→0.05 fs），检查初始几何，确认 QEq 收敛
- QEq 迭代不收敛：改善初始电荷、放宽 timestep、或调整 maxiter
- libmpi.so 缺失：改用 `uvx --from 'lammps[mpi]'`（捆绑 MPI 运行时）或系统安装 MPICH/OpenMPI
- 首次在线运行慢：警告用户首次 uvx 部署可能耗时（包体较大）
- NPT 输出不全：thermo_style 中保留 vol lx ly lz 以监控盒变化
