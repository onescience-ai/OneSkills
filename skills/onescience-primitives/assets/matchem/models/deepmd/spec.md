# architecture_overview
DeepMD 是基于深度学习的原子间势函数模型，核心思想是将体系总能量分解为逐原子能量贡献的加和：`E_total = Σ_i E_i`。每个原子的能量由其局部化学环境决定，模型通过两个子网络实现这一映射：

- **Descriptor（embedding net）**：将中心原子 i 在其截断半径 `rcut` 内的局部邻域环境编码为一个对称性保持的特征向量 `D_i`。该向量对同种元素的置换不变，对体系的平移、旋转和置换保持等变性。
- **Fitting net**：将特征向量 `D_i` 映射为原子能量 `E_i`，通常是一个全连接前馈网络。

模型通过能量对原子坐标和晶胞参数（virial tensor）的自动微分获得力和应力：

- 力：`F_i = -∂E_total / ∂r_i`
- 应力（virial）：`Ξ_αβ = -∂E_total / ∂ε_αβ`（其中 ε 为应变张量）

与 MACE 的关键差异：DeepMD 不依赖显式的 E(3)-等变消息传递和图卷积，而是通过 descriptor 的对称性约束（对旋转/平移/置换的不变性）保证物理合理性。这使得 DeepMD 的架构更简洁、训练速度通常更快，且与 LAMMPS 的集成更成熟（native `pair_style deepmd`）。

支持的 descriptor 类型：
- `se_e2_a`：双体角度描述符（默认、最常用），通过径向和角度信息的乘积构造嵌入特征。
- `se_e2_r`：双体径向描述符，仅用径向距离信息。
- `se_e3`：三体角度描述符，与 `se_e2_a` 的结构相似但使用三体信息。
- `se_atten`：基于注意力机制的描述符，通过可学习的注意力权重聚合邻域信息。
- `DPA-2`：多任务预训练模型架构，可同时处理多元素多体系。
- `DPA-3`：大规模预训练模型架构。
- `DPA-4`：最新一代架构。
- `hybrid`：混合多种 descriptor 类型的组合描述符。

扩展能力：
- **DPLR**（Deep Potential Long Range）：长程静电相互作用模型，通过引入原子电荷和 Ewald 求和处理长程库仑力。
- **DPRc**（Deep Potential Range Correction）：半经验范围校正模型，对短程势进行经验修正。
- **Spin**：自旋极化势函数，支持磁性体系。
- **Dipole/Polarizability/DOS**：偶极矩、极化率和电子态密度预测。

# parameter_scale
参数规模由 descriptor 类型和 fitting net 结构共同决定，以典型 `se_e2_a` 配置为例：

- `sel`（每个元素的截断半径内邻居数目上限）：典型值 `[80, 80]`（两元素体系）、`[40, 40, 40]`（三元素体系），直接影响 descriptor 输入维度和边数。
- `rcut`（截断半径）：典型值 `4.0` - `7.0` Å，配合 `sel` 控制邻域大小。
- `neuron`（fitting net 隐层神经元数）：典型 `[25, 50, 100]` 到 `[240, 240, 240]`，层数和宽度直接影响参数量。
- `axis_neuron`（descriptor axis neuron）：典型 `4`、`8`、`12`，控制 embedding 矩阵大小。
- `n_neuron`（descriptor 中的 neuron 数）：典型 `[25, 50, 100]`。
- `resnet_dt`（fitting net 残差连接）：`true` 时引入跳跃连接，不显著增加参数但可能改善训练。
- `type_map`（元素类型列表）：例如 `["O", "H"]`，决定 embedding net 对每种元素的独立参数。

工程判断：
- 小体系纯元素体系（如 Cu、Si）：`sel` 30-60，`neuron` `[120, 120, 120]`，`rcut` 4-6 Å 即可。
- 多元素复杂体系（如 MOF、液体电解质）：增大 `sel` 至 80-150，适当增加 fitting net 层数。
- DPA-3/DPA-4 预训练模型：参数量较大，但可直接使用于 fine-tuning 或 zero-shot 推理，无需调整结构参数。

# architecture_structure
主干结构按能量势函数路径组织，以 `se_e2_a` 为例：

输入构型
  原子坐标 + 原子类型 + 晶胞参数（周期体系）
    -> coord: (Nframes, NAtoms, 3)
    -> type: (Nframes, NAtoms) 或 (NAtoms,)
    -> cell: (Nframes, 9) 或 None

局部邻域构建
  coord + type + cell + rcut
    -> neighbor list (Nframes, Natoms, sel, 4)
      格式: [type_i, type_j, dR_x, dR_y, dR_z]
    -> 相对坐标 r_ij: (edge, 3)

Descriptor / Embedding Net
  输入: r_ij 的平滑径向函数 s(r_ij)
    -> 径向网络: embedding matrix G(s(r_ij))
    -> 角度信息乘积: G^T * G（se_e2_a 核心对称操作）
    -> 局部帧 embedding: D_i = concat + MLP
    -> descriptor feature: (Nframes * Natoms, descriptor_dim)

Fitting Net
  输入: descriptor D_i
    -> 全连接网络（可带残差连接）:
       D_i -> Linear(neuron[0]) -> ReLU -> ... -> Linear(neuron[N]) -> ReLU -> Linear(1)
    -> 原子能量 E_i: (Nframes * Natoms,)

能量聚合与求导
  E_total = Σ_i E_i
  F_i = -∂E_total / ∂r_i（autodiff 对 coord）
  virial = -∂E_total / ∂ε（autodiff 对 cell）

# input_schema
DeepMD-kit Python API 输入（`dpdata.LabeledSystem` 或 `DeepmdDataSystem`）：

训练数据：
- `coord`：`(Nframes, Natoms * 3)` 或 `(Nframes, Natoms, 3)`，原子笛卡尔坐标。
- `type`：`(Nframes, Natoms)` 或 `(Natoms,)`，原子类型（整数索引，从 0 开始）。
- `cell`：`(Nframes, 9)` 或 `(Nframes, 3, 3)`，晶胞参数（行优先存储），非周期体系可省略。
- `energy`：`(Nframes,)`，体系总能量标签。
- `force`：`(Nframes, Natoms, 3)`，原子受力标签。
- `virial`：`(Nframes, 9)` 或 `(Nframes, 3, 3)`，维里张量标签（可选）。
- `type_map`：元素名称列表，例如 `["O", "H"]`。
- `atom_names`：原子类型名称列表，需与 `type_map` 一致。

训练输入 JSON 关键字段：
- `model`：`{}`，模型配置，包含 `descriptor`、`fitting_net` 子配置。
- `model.descriptor.type`：descriptor 类型，如 `"se_e2_a"`。
- `model.descriptor.sel`：`[int, ...]`，每种元素的邻居数。
- `model.descriptor.rcut`：截断半径。
- `model.descriptor.rcut_smth`：平滑起始半径。
- `model.fitting_net.neuron`：`[int, ...]`，fitting net 每层神经元数。
- `model.fitting_net.resnet_dt`：是否使用残差连接。
- `model.type_map`：元素名称列表。
- `learning_rate`、`training`、`loss` 等训练超参。

推理输入（`deepmd.DeepPot`）：
- `coord`：`(Natoms, 3)`，单帧原子坐标。
- `cell`：`(3, 3)` 或 `(9,)`，晶胞参数。
- `atype`：`(Natoms,)`，原子类型（整数）。

# output_schema
`DeepPot.eval(coord, cell, atype)` 返回：

- `energy`：`float` 或 `(1,)`，体系总能量（eV）。
- `force`：`(Natoms, 3)`，原子受力（eV/Å）。
- `virial`：`(9,)` 或 `(3, 3)`，维里张量（eV），`[XX, XY, XZ, YX, YY, YZ, ZX, ZY, ZZ]` 顺序。
- `atom_energy`：`(Natoms,)`，逐原子能量（eV），仅当模型支持时返回。
- `atom_pref`：`(Natoms,)` 或 `None`，逐原子 pre-factor（eV/Å²），fparam 相关时返回。
- `atom_virial`：`(Natoms, 9)` 或 `None`，逐原子维里，仅当模型支持时返回。

训练输出（checkpoint）：
- `model.ckpt`：TensorFlow checkpoint 文件（.index + .data-00000-of-00001）。
- `frozen_model.pb`：冻结后的 Protocol Buffers 格式模型（用于 LAMMPS 部署）。

# shape_transformations
数据与张量变化流程：

原始构型数据
  dpdata.LabeledSystem (from VASP/OUTCAR, CP2K, LAMMPS dump, extxyz, etc.)
    -> coord: (Nframes, Natoms * 3)
    -> cell: (Nframes, 9)
    -> type: (Natoms,)
    -> energy: (Nframes,)
    -> force: (Nframes, Natoms, 3)

DeepmdDataSystem 预处理
  type_map + rcut + sel
    -> neighbor list: (Nframes, Natoms, max_sel_sum, 4)
    -> type: 整数索引
    -> 各帧按 sel 截断邻居，不足补零

Descriptor 计算（se_e2_a）
  邻域相对坐标 r_ij: (Nframes, Natoms, sel_i, 3)
    -> s(r_ij): (Nframes, Natoms, sel_i, M1)  # 径向平滑函数
    -> G(s(r_ij)): (Nframes, Natoms, M1, M2)  # embedding matrix
    -> G^T G: (Nframes, Natoms, M2, M2)        # 对称操作
    -> flatten + MLP: (Nframes * Natoms, descriptor_dim)

Fitting Net 映射
  descriptor: (Nframes * Natoms, D_desc)
    -> FC layers: (Nframes * Natoms, 1)
    -> atom energy: (Nframes, Natoms)

能量聚合与梯度
  E_total: (Nframes,)
  F_i = -∂E_total/∂r_i: (Nframes, Natoms, 3)
  virial = -∂E_total/∂ε: (Nframes, 3, 3)

模型导出
  TensorFlow SavedModel
    -> freeze_graph
    -> frozen_model.pb: 单一文件，含计算图和权重

# key_dependencies
- `deepmd-kit`：核心训练和推理框架。
- `dpdata`：数据采集和格式转换（支持 VASP、CP2K、LAMMPS、Quantum ESPRESSO、Gaussian 等）。
- `TensorFlow` 或 `PyTorch`：后端深度学习框架（当前主流为 TensorFlow 2.x 和 PyTorch 版）。
- `LAMMPS` + `USER-DEEPMD` 插件：MD 模拟部署。
- `ASE` + `deepmd` calculator：ASE 接口下的推理和结构弛豫。
- `DP-GEN`：主动学习工作流，与 DeepMD 深度集成的训练数据生成工具。
- `GROMACS` + DeepMD plugin：GROMACS MD 引擎接口。
- `i-PI`：路径积分分子动力学接口。
- `horovod`（可选）：分布式训练框架。

# common_modification_points
- 数据格式转换：使用 `dpdata` 将不同 DFT 软件的输出转为 DeepMD 训练格式，注意能量/力/应力的单位和符号一致性。
- 元素类型映射：`type_map` 必须与训练数据的原子种类严格一致，不同材料体系需要不同的 `type_map`。
- Descriptor 选择：
  - 水系、简单材料 → `se_e2_a`（默认）。
  - 需要更精确的径向信息 → `se_e2_r`。
  - 需要三体角度信息 → `se_e3`。
  - 大规模预训练 / 多元素 → `DPA-2`、`DPA-3`、`DPA-4`。
- `sel` 参数的确定：需分析训练集中每种原子的邻居数分布，取略大于最大邻居数的值；`sel` 过小导致信息丢失，过大增加计算开销。
- `rcut` 与 `rcut_smth`：`rcut_smth` 一般比 `rcut` 小 0.5-1.0 Å，确保平滑过渡。
- 长程静电：对于离子体系或极性体系，应考虑使用 DPLR 模型处理长程库仑相互作用。
- 自旋体系：磁性材料（如 Fe、Co、Ni）应使用 spin 版本的 descriptor 和 fitting net。
- Fine-tuning：DPA-3/DPA-4 预训练模型支持 fine-tuning，需设置较小的学习率和冻结部分层。
- LAMMPS 部署：需将训练好的模型冻结为 `frozen_model.pb`，LAMMPS 输入文件中使用 `pair_style deepmd frozen_model.pb`。
- 分布式训练：使用 `horovodrun` 或 DeepMD-kit 内置的 `dp train --mpi` 进行多卡训练。

# implementation_risks
- `sel` 设置过小：训练数据中某些原子邻居数超过 `sel` 时，超出的邻居信息被截断，导致模型学不到完整的局部环境，表现为力和应力的系统偏差。
- `rcut` 与物理边界冲突：周期体系的 `rcut` 不能超过晶胞最小边长的一半，否则邻域搜索会跨越周期边界错误地重复计入原子。
- 能量/力/应力单位错配：VASP 输出单位为 eV、eV/Å、kBar，DeepMD 内部使用 eV、eV/Å、eV，需通过 `dpdata` 的单位转换确保一致性。
- 冻结模型版本兼容性：TensorFlow checkpoint 的版本需与 LAMMPS 的 `USER-DEEPMD` 插件版本匹配，跨版本可能导致加载失败。
- `rcut_smth` 设置不当：`rcut_smth` 离 `rcut` 太远会导致太多邻居权重被平滑衰减，太近则导数不连续。
- `type_map` 顺序错误：`type_map` 中的元素顺序必须与 `dpdata.System` 中的 `atom_names` 严格一致，否则训练时的原子类型编码完全错位。
- 数据增强不足：DeepMD 不包含显式的旋转不变性内置机制（依赖 descriptor 数学对称性），数据增强（平移/旋转训练构型）可提高泛化性。
- 力收敛问题：DeepMD 通过自动微分获得力，若 fitting net 过深或激活函数梯度消失，可能导致力预测不准。
- DPLR 模型的环境依赖性：DPLR 需要设置 Ewald 求和参数（`ewald_beta`、`ewald_skin`），这些参数对不同的体系敏感。
- DPA-3/DPA-4 fine-tuning 失败：预训练模型的元素覆盖与 fine-tuning 数据不匹配时，可能需要重新训练 embedding 层。

# code_references
- `{onescience_path}/onescience/src/onescience/models/deepmd/`：模型实现入口。
- `{onescience_path}/onescience/examples/matchem/deepmd/`：训练示例和配置文件。
- DeepMD-kit 源码：`https://github.com/deepmodeling/deepmd-kit`。
- DeepMD-kit 文档：`https://docs.deepmodeling.com/projects/deepmd/en/latest/`。
- DP-GEN 工作流：`https://github.com/deepmodeling/dpgen`。
- LAMMPS USER-DEEPMD：LAMMPS 内置 pair_style deepmd 接口。
