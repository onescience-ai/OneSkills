# VASP DFT 工作流 (vasp-dft-workflow)

## 任务目标
通过 VASP 任务路由层，将用户的 DFT 计算意图分类为 static（单点 SCF）、relax（几何/晶胞弛豫）、dos（态密度）、band（能带）四种任务类型，生成对应的 INCAR/KPOINTS/POSCAR 输入文件与 POTCAR 映射指令，输出可直接提交的任务目录。路由层不执行计算，执行交由 dpdisp-submit 完成。

## 适用范围 / 不适用场景
适用：周期性体系（晶体、表面、分子晶体）的 DFT 输入准备；需要按意图分发到 static/relax/dos/band 子流程的场景；dos/band 依赖前序 SCF 产物（电荷密度/波函数）的延续计算。
不适用：孤立分子气相计算；路由层不拥有完整 INCAR 模板，不执行/提交计算，不绕过子技能专属护栏。

## 实体槽（Entity Slots）
- calc_type: static / relax / dos / band
- ENCUT: 平面波截断能（eV），必须显式提供
- kpoint_policy: KSPACING（默认）或 explicit KPOINTS mesh
- ISMEAR / SIGMA: 展宽方法与参数，必须显式
- ISIF: 弛豫类型（仅 relax），分 ion-only / cell+ion / low-dimensional slab
- IBRION / NSW / EDIFFG: 弛豫控制参数
- NEDOS / LORBIT: DOS 分辨率与投影设置
- ISPIN / MAGMOM: 自旋极化（按需）
- IVDW: 范德华修正（按需）
- EDIFF / NELM / PREC / LREAL: 通用 SCF 控制

## 输入输出契约
输入：
- 用户提供的结构文件（static/relax）或前序 SCF 产物路径（dos/band）
- 必须参数：ENCUT、ISMEAR/SIGMA、k 点策略、POTCAR 元素映射
- relax 额外必须：IBRION、NSW、EDIFFG、ISIF 及弛豫意图分类
- dos 额外必须：源 SCF 上下文路径、DOS 意图（total/projected）、能量窗口/分辨率
- band 额外必须：源 SCF 上下文路径、晶体/路径约定或显式 k-path

输出：
- 任务目录含 POSCAR、INCAR、可选 KPOINTS、POTCAR 映射/组装指令
- 设置摘要与假设说明
- 未决科学选择供用户确认
- 若需执行，附 dpdisp-submit 交接说明

## 方法路线（可替换）
默认路线：KSPACING 控制 k 点（不生成 KPOINTS 文件），仅用户明确要求时生成显式 mesh。
- static：单点 SCF，NSW=0 语义
- relax：ISIF 驱动弛豫意图映射（ion-only / cell+ion / slab）
- dos：基于前序 SCF 电荷密度/波函数延续，NEDOS/LORBIT 控制分辨率与投影
- band：line-mode 高对称路径 KPOINTS，ISMEAR 策略适配 band 阶段
- 路由规则：意图模糊时仅问一个聚焦澄清问题再分发

## 操作序列（Operations）
1. 路由分类：根据用户意图选择 static/relax/dos/band 子技能
2. 前置检查：dos/band 必须验证 SCF 前序产物可用性，缺失则停止并询问
3. 收集必须参数：结构、ENCUT、ISMEAR/SIGMA、k 策略、POTCAR 映射
4. 生成 INCAR：按任务类型填充参数（弛豫需显式 ISIF 选择理由）
5. 生成 KPOINTS：仅 dos 显式 mesh 或 band line-mode 时生成
6. 输出 POTCAR 映射指令：按元素顺序，不编造赝势
7. 汇总假设与未决选择，附 dpdisp-submit 交接说明

## 验证契约（Validations）
- 赝势合法性：不得编造 POTCAR，必须用户提供或指向官方资源
- 前置产物完整性：dos/band 启动前验证 SCF 上下文路径存在
- 参数显式暴露：所有假设必须明示，未决科学选择上报用户确认
- ISIF 选择合理性（relax）：必须附选择理由
- k-path 约定一致性（band）：晶体/路径约定明确
- 输出格式：handoff-ready 任务目录，可直接交接提交

## 资源引用（Resources）
- 可执行：VASP（需用户持有合法授权与赝势资源）
- 提交工具：dpdisp-submit（Shell/Slurm/PBS/LSF/Bohrium 作业提交）
- 路由子技能：dft-vasp/static、dft-vasp/relax、dft-vasp/dos、dft-vasp/band
- 共享策略：不编造赝势、显式暴露假设、报告未决选择、返回 handoff-ready 目录

## 前后置任务（Task Graph）
无强制前后置。内部依赖：dos/band 需要前序 static SCF 产物（电荷密度/波函数）。执行阶段统一交接 dpdisp-submit。

## 缺口与降级（Fallback / Gap）
- 意图模糊：仅问一个聚焦澄清问题，不猜测分发
- 前置 SCF 产物缺失（dos/band）：停止并要求用户提供，不自行编造
- k 点策略不确定：默认 KSPACING，用户要求时切换为显式 mesh
- 赝势不可用：不可编造，需用户确认 VASP 授权与 POTCAR 资源
- ISIF 意图不明确（relax）：分类为 ion-only / cell+ion / slab 三选一，模糊则询问
- 执行请求：路由层不执行，一律交接 dpdisp-submit
