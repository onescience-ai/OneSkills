# Model Card: MACE

## 基本信息

- 模型名：`MACE` / `ScaleShiftMACE`
- 任务类型：`materials / MLIP / 能量-力-应力势函数训练、微调与原子模拟`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/mace/mace.py`

## 模型定位

MACE 是面向原子体系的 E(3)-等变高阶消息传递势函数模型，适合从原子构型预测总能量，并通过解析梯度得到力、应力、virial、Hessian 等下游量。

本卡是当前材料模型卡的标准样板。后续新增材料领域模型时，优先沿用本卡的章节结构，但替换为新模型自己的输入协议、训练入口、数据卡、组件契约和风险点。

优先用于：

- 基于 MACE-MP / MACE-MPA / MACE-OMAT / 本地 `.model` 的 fine-tuning
- 对目标材料体系训练 MLIP，并用在 ASE/LAMMPS/MD/结构弛豫中
- 处理晶体、缺陷、固态电解质、表面、吸附、液体、界面等原子尺度材料任务

与通用图网络相比，MACE 的关键是：局部邻域图 + 球谐/径向基 + 高阶等变 product basis + 能量读出；力和应力来自能量对坐标/应变的导数。

## 输入定义

### 训练入口输入

OneScience 示例默认通过 `examples/matchem/mace/train.py` 和 demo YAML 传入：

- `train_file` / `valid_file` / `test_file`: `.xyz` 或 `.extxyz`
- `energy_key`: extxyz `Atoms.info` 中的能量字段
- `forces_key`: extxyz `Atoms.arrays` 中的力字段
- `stress_key` / `virials_key`: 可选，应力或 virial 字段
- `E0s`: `average`、`isolated`、`foundation` 或显式原子参考能字典
- `foundation_model`: 可选，传入时进入 fine-tuning 路线

### 模型 forward 输入

`MACE.forward(data)` 接收 PyG 风格 `dict / Batch`，核心字段包括：

- `positions`: `(NumAtoms, 3)`
- `node_attrs`: `(NumAtoms, NumElements)`，按 `AtomicNumberTable` one-hot
- `edge_index`: `(2, NumEdges)`
- `batch`: `(NumAtoms,)`
- `cell`: `(NumGraphs, 3, 3)` 或单构型 cell
- `shifts` / `unit_shifts`: 周期邻居偏移
- `head`: 多头任务时的 head id

通常不要手写这些字段；优先让 `AtomicData.from_config` 和 MACE 训练脚本生成。

## 输出定义

`MACE.forward` 返回 dict：

- `energy`: `(NumGraphs, NumHeads)` 或 `(NumGraphs,)`
- `forces`: `(NumAtoms, 3)`，当 `compute_force=True`
- `stress`: `(NumGraphs, 3, 3)`，当 `compute_stress=True`
- `virials`: `(NumGraphs, 3, 3)`，当 `compute_virials=True`
- `atomic_virials` / `atomic_stresses`: 可选逐原子张量
- `hessian`: 可选二阶导
- `node_feats`: 拼接后的节点等变特征

`ScaleShiftMACE` 额外返回 `interaction_energy`，并对 interaction energy 做 scale/shift 后再与 E0 相加。

## 主干结构

- `LinearNodeEmbeddingBlock`
  - 将原子种类 one-hot 映射为 scalar node features
- `RadialEmbeddingBlock` + spherical harmonics
  - 根据 `r_max` 内邻居距离和方向构造边特征
- 多层 `InteractionBlock`
  - 消息传递并保持 E(3) 等变结构
- `EquivariantProductBasisBlock`
  - 构造高阶 many-body product basis
- `LinearReadoutBlock` / `NonLinearReadoutBlock`
  - 输出逐原子能量贡献
- `get_outputs`
  - 对能量求导得到 forces/stress/virials

## 主要依赖组件

- `mace_material_stack`
- `AtomicData` from `onescience.datapipes.materials.pyg_stack`
- `AtomicNumberTable`
- `MACECalculator` / `LAMMPS_MACE`

## 主要 Shape 变化

- extxyz 构型 -> `Configuration`
- `Configuration` -> `AtomicData`
  - 原子种类转 `node_attrs`
  - 邻居表转 `edge_index`
- embedding 后：
  - node scalar features: `(NumAtoms, Channels)`
  - edge radial features: `(NumEdges, RadialDim)`
- interaction/product 后：
  - node irreps features 保持等变结构
- readout 后：
  - node energy -> graph energy by `scatter_sum`
- forces/stress:
  - 从 graph energy 对 positions/cell displacement 自动微分

## 默认关键参数

OneScience demo 中常见参数：

- `model=MACE`
- `num_interactions=2`
- `num_channels=128`
- `max_L=0` 或 `2`
- `correlation=3`
- `r_max=4.0` 到 `6.0`
- `default_dtype=float64`
- `batch_size=2` 到 `20`
- `energy_weight=1.0` 到 `20.0`
- `forces_weight=1.0` 到 `20.0`
- `stress_weight=0.0` 到 `20.0`
- `lr=1e-4` 到 `1e-3`
- `ema=true`
- `swa=true`

fine-tuning 时常见补充：

- `foundation_model=<path or known model>`
- `scaling=rms_forces_scaling`
- `num_samples_pt`
- `ema_decay=0.98` 到 `0.99999`
- `swa_lr=1e-5` 到 `1e-4`

## 常见修改点

- 新数据字段名不同：同步修改 `energy_key`、`forces_key`、`stress_key`
- DeepMD 数据接入：先转 extxyz，再进入 MACE 训练脚本
- 目标更偏力学/缺陷：提高 forces/stress 权重，并加专门验证集
- 小数据 fine-tuning：优先使用 foundation checkpoint、EMA/SWA、较小 lr
- 下游 MD：优先选验证集误差和 MD 稳定性都好的 `stageone` 或 `stagetwo` model
- LAMMPS 部署：使用 `create_lammps_model.py` 或相关 calculator 脚本生成部署模型

## 风险点

- `r_max` 对 foundation model 很敏感；fine-tuning 默认不要随意改 foundation 使用的 cutoff。
- `E0s=average` 是方便入口，不是高精度默认；若 DFT 设置不同，优先提供自算 isolated atom energies。
- ASE 新版本中 `energy` / `forces` 字段可能与 calculator 交互混淆；新数据建议显式使用 `REF_energy` / `REF_forces`。
- `stress` 与 `virial` 的符号、单位和 shape 要单独核对，不要从字段名直接假设。
- MACE demo 中存在 legacy `mace.*` module alias，用于旧 checkpoint 加载；移动或改名时要保留兼容。
- 多卡/DCU 训练优先通过 demo `run.sh --dry-run` 检查最终命令，不要直接手写 torchrun/srun。

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `../datapipes/materials_mace.md`
3. 再看 `../contracts/mace_material_stack.md`
4. 需要具体运行方式时看 demo YAML 和 `run.sh`
5. 契约仍不足时再回到源码

## 组件契约入口

- `../contracts/mace_material_stack.md`

## 数据入口

- `../datapipes/materials_mace.md`

## 源码锚点

- `./onescience/src/onescience/models/mace/mace.py`
- `./onescience/src/onescience/modules/block/mace_block.py`
- `./onescience/src/onescience/modules/layer/mace_radial.py`
- `./onescience/src/onescience/modules/func_utils/mace_func_utils.py`
- `./onescience/src/onescience/modules/loss/mace_loss.py`
- `./onescience/examples/matchem/mace/train.py`
- `./onescience/examples/matchem/mace/demo/run.sh`
- `./onescience/examples/matchem/mace/demo/configs/*.yaml`
- `./onescience/examples/matchem/mace/scripts/eval_configs.py`
- `./onescience/examples/matchem/mace/scripts/run_md.py`
