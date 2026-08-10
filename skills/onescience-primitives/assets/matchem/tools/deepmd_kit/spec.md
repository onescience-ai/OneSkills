# architecture_overview
DeepMD-kit 是基于深度学习的原子间势函数（MLIP）训练与部署工具集。核心思想是通过深度神经网络从第一性原理（DFT）数据中学习势能面（PES），将高精度量子力学计算结果映射为可高效计算的经典力场模型。工具集以命令行接口 `dp` 为核心入口，提供从数据准备、模型训练、模型操作到生产部署的完整工具链。

DeepMD-kit 的软件生态定位：

- 输入：第一性原理计算数据（VASP/CP2K/LAMMPS/QCHEM/Gaussian/ABACUS/SIESTA 等格式的原子构型+能量/力/应力标签），经 dpdata 统一转换为 DeePMD-kit 内部 system 格式。
- 模型：Deep Potential（DP）系列神经网络模型，由 descriptor（环境描述子）和 fitting_net（拟合网络）两部分组成。descriptor 将原子局部环境编码为特征向量，fitting_net 将特征映射为原子能量贡献。
- 输出：冻结的 `.pb` 或 `.pth` 模型文件，可部署到 LAMMPS（pair_style deepmd）、ASE（DeepPotential calculator）、GROMACS（HackMD patch）、i-PI 等 MD 引擎中，实现大规模经典分子动力学模拟。
- 核心原理：Deep Potential 方法的数学基础是将体系总能量分解为每个原子的局部环境贡献之和（E = ΣE_i），通过神经网络拟合 E_i，保证能量对体系尺寸的 extensivity。力由能量对坐标的解析梯度获得（F = -∂E/∂R），应力由 virial 定理导出，天然满足能量守恒。

# ecosystem_and_toolchain
DeepMD-kit 生态由以下工具链组件协同工作：

## 数据准备层
- **dpdata**：多格式数据读取与转换库。支持 VASP（OUTCAR/POSCAR/vasprun.xml）、CP2K、LAMMPS（dump/log）、QCHEM、Gaussian、ABACUS、PWmat、SIESTA、FHI-aims、DeepMD-kit 原生格式（set.000/type.raw/type_map.raw/box.npy/coord.npy/energy.npy/force.npy/virial.npy）之间的转换。提供 LabeledSystem 类封装标记数据，MultiSystems 类管理多体系数据集合。支持 train/validation/test 数据划分。

## 模型定义层
- **descriptor**：环境描述子模块。将原子 i 的局部环境（邻域原子集合）编码为固定长度的特征向量 D_i。DeepMD-kit 支持多种 descriptor 类型，各有不同的精度-效率权衡。
- **fitting_net**：拟合网络模块。接收 descriptor 输出特征，映射为原子能量贡献 E_i。可扩展为偶极（dipole）、极化率（polarizability）、电子态密度（DOS）等多物理量拟合。

## 训练与操作层
- **dp train**：模型训练命令。读取 input.json 配置文件，加载训练/验证数据，启动 TensorFlow 或 PyTorch 后端训练。
- **dp freeze**：模型冻结命令。将训练 checkpoint 转为单一 `.pb` 文件（TensorFlow）或 `.pth` 文件（PyTorch），移除训练专用节点，用于生产部署。
- **dp compress**：模型压缩命令。对 descriptor 中的 embedding net 做多项式插值压缩，大幅加速推理速度（通常 5-20x），同时保持精度。
- **dp test**：模型测试命令。在测试数据集上评估模型的能量/力/应力预测精度，输出 RMSE 和误差分布。

## 部署与接口层
- **LAMMPS pair_style deepmd**：通过 DeePMD-kit 编译的 LAMMPS 插件，在 LAMMPS 中以 pair_style 方式调用 DP 模型进行 MD 模拟。
- **ASE DeepPotential calculator**：通过 ASE 接口调用 DP 模型进行结构弛豫、单点能计算、振动分析等。
- **GROMACS HackMD patch**：将 DP 模型集成到 GROMACS MD 引擎中。
- **i-PI client**：通过 i-PI 通用接口连接 DP 模型进行路径积分分子动力学（PIMD）。

## 高级功能层
- **Model Deviation**：模型偏差计算。对同一构型用多个独立训练的模型（ensemble）进行预测，计算原子受力的标准差。这是主动学习流程（DP-GEN）中筛选候选构型的核心指标。
- **Deep Potential Long Range (DPLR)**：长程静电扩展。将体系分解为短程 DP 部分和长程静电部分（Ewald 求和），适用于离子体系和高分子电解质。
- **Deep Potential Range Correction (DPRc)**：范围修正。通过短程修正网络修正长程相互作用在 cutoff 处的截断效应。
- **Spin Deep Potential**：spin 势函数。在 descriptor 中引入原子磁矩作为额外输入，建模磁性体系的势能面。
- **Multi-task Training**：多任务训练。同一模型同时拟合多个 DFT 设置（不同泛函、不同 basis set）或多种物理量（能量+偶极+DOS）的数据。
- **Finetuning**：预训练模型微调。在 DPA-2/DPA-3 等大规模预训练模型基础上，用小规模目标体系数据 fine-tune，降低数据需求。

# data_preparation_workflow
数据准备是 DeepMD-kit 训练的第一步，核心工具为 dpdata。

## 输入数据格式
DeepMD-kit 支持多种 DFT 软件的输出作为原始数据源：

| DFT 软件 | 输入格式 | dpdata 加载方法 |
|----------|---------|----------------|
| VASP | OUTCAR | `dpdata.LabeledSystem('OUTCAR')` |
| VASP | vasprun.xml | `dpdata.LabeledSystem('vasprun.xml', fmt='vasp/xml')` |
| CP2K | cp2k output | `dpdata.LabeledSystem('cp2k_output', fmt='cp2k/output')` |
| LAMMPS | dump + log | `dpdata.LabeledSystem('lmp.dump', fmt='lammps/dump')` |
| QCHEM | qchem output | `dpdata.LabeledSystem('qchem.out', fmt='qchem')` |
| Gaussian | gaussian log | `dpdata.LabeledSystem('gaussian.log', fmt='gaussian/log')` |
| ABACUS | abacus output | `dpdata.LabeledSystem('abacus_output', fmt='abacus/scf')` |
| PWmat | pwmat output | `dpdata.LabeledSystem('atom.config', fmt='pwmat')` |
| SIESTA | siesta output | `dpdata.LabeledSystem('siesta_output', fmt='siesta/output')` |
| FHI-aims | aims output | `dpdata.LabeledSystem('aims.out', fmt='fhi_aims/output')` |

## 数据转换流程

步骤 1 — 读取原始数据：
```python
import dpdata
ls = dpdata.LabeledSystem('OUTCAR', fmt='vasp/outcar')
```

步骤 2 — 数据检查与筛选：
```python
# 检查体系信息
print(ls.get_nframes(), ls.get_natoms())
print(ls['energies'])  # 能量数组
print(ls['forces'])    # 力数组

# 按条件筛选构型（例如筛选能量范围内的构型）
ls_filtered = ls.sub_system(
    ls['energies'] < threshold_high
)
```

步骤 3 — 写入 DeePMD-kit 原生格式：
```python
# 随机打乱并划分 train/valid
ms = dpdata.MultiSystems(ls)
train, valid = ms.train_test_split(test_size=0.1, seed=42)

# 写入 system 格式
dpdata.LabeledSystem.to_deepmd_npy(train, './train_data/')
dpdata.LabeledSystem.to_deepmd_npy(valid, './valid_data/')
```

## DeePMD-kit 原生 System 格式
DeePMD-kit 使用纯 numpy 二进制格式存储训练数据，以一个 `system` 目录为单位：

```
system/
├── type.raw        # 原子类型（整数，shape: [natoms]）
├── type_map.raw    # 元素名映射（文本，每行一个元素符号）
├── set.000/        # 第 0 组构型数据
│   ├── box.npy     # 晶胞矢量，shape: [nframes, 9]
│   ├── coord.npy   # 原子坐标（分数坐标），shape: [nframes, natoms*3]
│   ├── energy.npy  # 体系总能量，shape: [nframes]
│   ├── force.npy   # 原子受力，shape: [nframes, natoms*3]
│   └── virial.npy  # （可选）virial 张量，shape: [nframes, 9]
├── set.001/
│   └── ...
└── ...
```

- `type.raw`：整数编码的原子类型（从 0 开始）。
- `type_map.raw`：元素符号列表，如 `H\nO\n` 表示 type 0 = H, type 1 = O。
- `set.*/`：每组至多包含若干帧构型，多个 set 目录利于分布式数据加载。
- `box.npy` 为 9 分量行优先的晶胞矩阵 `[xx, xy, xz, yx, yy, yz, zx, zy, zz]`。
- 对于非周期体系，`box.npy` 可为全零（表示无 PBC）。

## 训练数据配置：training_data 块
在 `input.json` 中通过 `training_data` 和 `validation_data` 参数指定数据路径：

```json
"training": {
    "training_data": {
        "systems": [
            "./train_data/system_001/",
            "./train_data/system_002/"
        ],
        "batch_size": "auto",
        "auto_prob": "prob_sys_size"
    },
    "validation_data": {
        "systems": ["./valid_data/system_001/"],
        "batch_size": 1
    }
}
```

`auto_prob` 参数控制从不同 system 采样 batch 的概率：`"prob_sys_size"` 按体系大小加权，`"prob_uniform"` 均匀采样。

# model_architecture
DeepMD-kit 模型由 descriptor（环境描述子）和 fitting_net（拟合网络）两部分串联组成。

## Descriptor 类型

### 1. se_e2_a（Smooth Edition, Embedding to Atom）
最经典、最广泛使用的 descriptor。对中心原子 i 的每个邻域原子 j：
- 计算距离 R_ij 和方向向量 R_ij。
- 通过 embedding network G(s_ij) 将标量距离 s_ij = 1/R_ij 嵌入为特征向量。
- 将 embedding 输出与方向相关的球面分量耦合，构造环境矩阵 D_i。
- 对标量距离和角度的平滑截止函数保证邻居列表变化的连续性。
- 优点：准确、通用。缺点：高角动量时计算量大。

### 2. se_e2_r（Smooth Edition, Embedding to Radial）
se_e2_a 的简化变体。仅使用径向（距离）信息构造 descriptor，不编码角度信息。
- 结构更简单，参数更少，速度更快。
- 对角度依赖弱的体系（简单金属、惰性气体）足够。
- 不适于共价键、氢键等有强方向性的体系。

### 3. se_e3（3-body Embedding）
扩展 se_e2_a 以显式编码三体（角度）信息。
- 以距离和角度作为 embedding network 输入。
- 比 se_e2_a 对角度信息更敏感。
- 对水分子、有机分子等方向键体系更准确。

### 4. se_atten（Smooth Edition with Attention）
在 se_e2_a 基础上引入自注意力（self-attention）机制。
- 允许 descriptor 根据全局化学环境动态调整局部环境表示权重。
- 对复杂多元素体系表现更好。
- 计算量较 se_e2_a 稍大。

### 5. DPA-2 / DPA-3 / DPA-4（Deep Potential Attention 系列）
新一代预训练模型架构系列，基于 attention 和 message-passing 框架：
- **DPA-2**：结合 se_atten 与多任务训练策略，在 OC20/OC22 等多元素 benchmark 上取得 SOTA 性能。
- **DPA-3**：统一 DeepMD-kit 框架下的预训练模型，兼容 DP/DPA 系列。通过 `"model_type": "standard"` 和 `"descriptor": "dpa3"` 配置。支持大规模预训练后在目标体系上 finetune。
- **DPA-4**：DPA-3 的后续版本，进一步扩展模型容量与预训练数据覆盖面。
- 配置参数示例（DPA-3）：
```json
{
  "model": {
    "type": "standard",
    "descriptor": {
      "type": "dpa3"
    },
    "fitting_net": {
      "type": "dpa3"
    }
  }
}
```

### 6. hybrid descriptor
将多个 descriptor 的输出拼接（concatenate），组合不同 descriptor 的优势。
- 示例：`"type": "hybrid"` + `"list": [{"type": "se_e2_a", ...}, {"type": "se_e2_r", ...}]`
- 适用于同时包含共价和离子相互作用的多元素体系。

## Fitting Net 类型

### 1. energy fitting_net（ener）
标准能量拟合网络。接收 descriptor 输出，通过若干全连接层生成原子能量贡献 E_i，体系总能量 E = ΣE_i。
- 配置字段：`"type": "ener"`。
- 超参数：`"neuron": [240, 240, 240]`（每层节点数），`"resnet_dt": true`（是否启用 ResNet 跳跃连接）。

### 2. dipole fitting_net（dipole）
偶极矩拟合网络。在能量模型基础上增加偶极预测头。
- 需要在 `input.json` 中指定 `"fitting_net"` 的 `"type": "dipole"`。
- 训练数据需包含偶极标签。

### 3. polarizability fitting_net（polar）
极化率拟合网络。预测分子或材料的极化率张量。
- 需要训练数据包含极化率标签。

### 4. DOS fitting_net（dos）
电子态密度拟合网络。预测能量依赖的电子态密度 g(E)。
- 需要训练数据包含 DOS 标签。
- 配合 `"numb_dos"` 参数指定 DOS 能量网格点数。

## 关键模型配置参数（input.json 示例）

```json
{
  "model": {
    "type": "standard",
    "descriptor": {
      "type": "se_e2_a",
      "sel": [46, 92],
      "rcut_smth": 0.5,
      "rcut": 6.0,
      "neuron": [25, 50, 100],
      "type_one_side": false,
      "axis_neuron": 16,
      "seed": 1
    },
    "fitting_net": {
      "type": "ener",
      "neuron": [240, 240, 240],
      "resnet_dt": true,
      "seed": 1
    }
  }
}
```

关键参数说明：
- `rcut`（Å）：local environment cutoff radius，决定每个原子考虑多远的邻域原子。典型值：4-7 Å。
- `rcut_smth`（Å）：cutoff 平滑过渡区间宽度。
- `sel`：每种原子类型的最大邻居数（max neighbors）。格式为 `[n1, n2, ...]` 对应每种元素。
- `neuron`（descriptor 中）：embedding network 每层的节点数。
- `neuron`（fitting_net 中）：拟合网络每层节点数。
- `type_one_side`：是否将原子对 (i,j) 和 (j,i) 视为不同。通常设为 `false`。
- `seed`：随机种子，用于网络权重初始化。

# training_workflow
DeepMD-kit 的训练通过 `dp train` 命令执行，核心配置文件为 `input.json`。

## input.json 完整结构

```json
{
  "_comment": "DeePMD-kit training input.json",
  "model": {
    "type": "standard",
    "descriptor": { ... },
    "fitting_net": { ... }
  },
  "learning_rate": {
    "type": "exp",
    "decay_steps": 5000,
    "start_lr": 0.001,
    "stop_lr": 3.51e-8
  },
  "loss": {
    "type": "ener",
    "start_pref_e": 0.02,
    "limit_pref_e": 1.0,
    "start_pref_f": 1000,
    "limit_pref_f": 1.0,
    "start_pref_v": 0.0,
    "limit_pref_v": 0.0
  },
  "training": {
    "training_data": { ... },
    "validation_data": { ... },
    "numb_steps": 1000000,
    "seed": 10,
    "disp_file": "lcurve.out",
    "disp_freq": 1000,
    "save_freq": 10000
  }
}
```

## dp train 命令与关键参数

```sh
# 基本训练
dp train input.json

# 多 GPU 训练（Horovod）
horovodrun -np 4 dp train input.json

# TensorFlow 后端
dp --tf train input.json

# PyTorch 后端
dp --pt train input.json
```

训练关键参数：
- `numb_steps`：总训练步数。建议至少 10^5-10^6 步。
- `disp_freq`：日志输出频率（步）。
- `save_freq`：checkpoint 保存频率（步）。
- `disp_file`：训练曲线输出文件。

## 学习率策略
- `"type": "exp"`：指数衰减。`start_lr` → `stop_lr`，按 `decay_steps` 控制衰减速度。
- 也可使用 `"type": "linear"` 线性衰减或其他自定义调度器。

## Loss 权重配置
- `start_pref_e` / `limit_pref_e`：能量损失权重（起始 → 最终）。
- `start_pref_f` / `limit_pref_f`：力损失权重。
- `start_pref_v` / `limit_pref_v`：virial/应力损失权重。
- weight 从起始值线性过渡到最终值（随训练步数）。

## 多 GPU 并行训练
DeepMD-kit 支持通过 Horovod 进行数据并行多卡训练：
```sh
horovodrun -np 4 dp train input.json
```
每张 GPU 处理一个 batch，通过 allreduce 同步梯度。训练数据应在各进程间自动分片。

## Finetuning（微调）
在预训练模型基础上用小数据集 fine-tune：
```json
{
  "model": {
    "type": "standard",
    "descriptor": { "type": "dpa3" },
    "fitting_net": { "type": "dpa3" }
  },
  "training": {
    "init_model": "./pretrained_model.pb",
    "init_frz_model": "./pretrained_frozen.pb",
    ...
  }
}
```
- `init_model`：指定预训练模型 checkpoint 路径。
- `init_frz_model`：指定冻结的预训练模型路径。
- fine-tuning 时通常使用较低的学习率（如 `start_lr: 1e-5`）和较少的训练步数。

## Multi-task Training
在 `input.json` 中设置 `"model": {"type": "multi"}`，在 `"model_dict"` 中定义多个子任务（不同 DFT 泛函、不同体系），共享 descriptor 但每个任务有独立 fitting_net。

## 原子参考能设置
通过 `atom_ener` 参数在 fitting_net 中注入原子参考能（隔离原子能量），加速训练收敛：
```json
"fitting_net": {
    "type": "ener",
    "atom_ener": [0.0, 0.0],
    ...
}
```
对每种元素指定参考能，单位为 energy_unit。

# model_operations
DeepMD-kit 提供完整的模型生命周期管理命令。

## dp freeze — 模型冻结
将训练 checkpoint 转为部署用单一文件：
```sh
dp freeze -o frozen_model.pb
```
或带 checkpoint 参数：
```sh
dp freeze -c 100000 -o frozen_model.pb
```
- `-o`：输出文件路径。
- `-c`：指定 checkpoint 步数（默认使用最新 checkpoint）。
- 输出为 TensorFlow `.pb` 或 PyTorch `.pth` 文件，不包含训练节点。

## dp compress — 模型压缩
对 embedding net 做多项式插值压缩，加速推理：
```sh
dp compress -i frozen_model.pb -o compressed_model.pb
```
关键参数：
- `-i`：输入冻结模型。
- `-o`：输出压缩模型。
- 在 `input.json` 中添加压缩参数：
```json
"model": {
    "compress": {
        "type": "se_e2_a",
        "min_nbor_dist": 0.7,
        "model_file": "frozen_model.pb",
        "table_config": [0.0, 4.0, 0.01]
    }
}
```
- `min_nbor_dist`：最小邻域距离，用于训练压缩插值表的下限。
- `table_config`：[lower, upper, stride]，插值表范围和步长。
- 压缩比：通常 embedding 计算加速 5-20 倍，取决于 `neuron` 配置和 `sel`。

## dp test — 模型精度测试
在测试集上评估模型：
```sh
dp test -m frozen_model.pb -s ./test_data/ -d detail_output -n 100
```
关键参数：
- `-m`：模型文件路径。
- `-s`：测试数据 system 路径。
- `-d`：输出目录（保存每个构型的详细误差）。
- `-n`：最大测试帧数（用于大规模数据抽样）。
- 输出包含能量 RMSE、力 RMSE、virial RMSE 及误差分布统计。

## dp transfer — 旧版模型升级
将旧版本 DeePMD-kit（v0.x/v1.x）训练的模型转换为当前版本兼容格式：
```sh
dp transfer -O old_model.ckpt -o new_model.ckpt
```

# deployment
训练好的 DP 模型可部署到多种 MD 引擎中。

## LAMMPS 部署（pair_style deepmd）
最主流的部署方式。需编译带有 DeePMD-kit patch 的 LAMMPS：
```bash
# LAMMPS input 示例
units           metal
atom_style      atomic
read_data       data.lmp

pair_style      deepmd frozen_model.pb
pair_coeff      * *
# 或指定元素映射
pair_coeff      * * frozen_model.pb H O
```
- 单个 `.pb` 或 `.pth` 文件即为完整的势函数。
- 支持 NVT/NPT/NVE 系综。
- 支持多元素体系（通过 type_map 自动匹配）。

## ASE 部署（DeepPotential calculator）
通过 ASE 接口进行结构弛豫、单点能计算：
```python
from deepmd.calculator import DP
from ase.optimize import BFGS
from ase.io import read

atoms = read('POSCAR')
calc = DP(model='frozen_model.pb')
atoms.calc = calc

opt = BFGS(atoms)
opt.run(fmax=0.01)
```
- 支持 ASE 的结构弛豫器（BFGS、FIRE 等）。
- 支持 ASE 的振动分析接口。

## GROMACS 部署
通过 HackMD patch 将 DP 模型嵌入 GROMACS：
- 需要在编译 GROMACS 时启用 HackMD 支持。
- `.mdp` 文件中设置 `hackmd = deepmd`。
- 在拓扑文件的 `[ pairtypes ]` 或 `[ nonbond_params ]` 节中引用模型路径。

## i-PI 部署
通过 i-PI 的 Socket 或 UNIX 域套接字接口：
```python
# deepmd + i-PI client
from deepmd.infer.deep_pot import DeepPot
dp = DeepPot('frozen_model.pb')
# 通过 i-PI 客户端协议通信
```
- 支持 PIMD（路径积分分子动力学）。
- 支持 NEB、REMD 等增强采样方法。

# model_deviation
Model Deviation（模型偏差）是 DeepMD-kit 中主动学习工作流的核心组件，也是 DP-GEN 的关键计算模块。

## 原理
使用一组（通常 4 个）独立训练的模型组成 ensemble，对同一构型分别预测原子受力。计算各模型预测之间的标准差作为 model deviation：

```
σ_i = std(F_i^(1), F_i^(2), F_i^(3), F_i^(4))  # 第 i 个原子的力偏差
σ_max = max(σ_i)  # 最大原子力偏差（常用指标）
```

## 使用方法
```python
from deepmd.infer.deep_pot import DeepPot
from deepmd.infer.model_devi import calc_model_devi

models = [
    DeepPot('model_00.pb'),
    DeepPot('model_01.pb'),
    DeepPot('model_02.pb'),
    DeepPot('model_03.pb'),
]

# 计算 model deviation
md = calc_model_devi(
    coord, cell, atype, models
)
# 返回每个原子的力偏差和最大偏差
```

## 在 DP-GEN 主动学习中的角色
1. **探索阶段**：用当前 ensemble 模型进行 MD 或结构搜索，生成候选构型。
2. **筛选阶段**：计算候选构型的 model deviation。
   - 若 σ_max 在 [σ_low, σ_high] 范围内 → 标记为"候选"构型，提交 DFT 计算。
   - 若 σ_max < σ_low → 模型已准确，丢弃。
   - 若 σ_max > σ_high → 构型不合理，丢弃。
3. **标注阶段**：对候选构型进行 DFT 计算，获得能量/力标签。
4. **重训练阶段**：将新标注数据加入训练集，重新训练 ensemble 模型。
5. 迭代上述步骤直到 model deviation 收敛。

Model deviation 是 DeePMD-kit 连接第一性原理计算（VASP/CP2K 等）与大规模 MD 模拟的关键桥梁。

# key_dependencies
- **TensorFlow 2.x**（v2.5+）或 **PyTorch**：深度学习后端。
- **dpdata**：数据格式转换库。
- **Horovod**：多 GPU 分布式训练（可选）。
- **LAMMPS**：主要 MD 引擎（部署用）。
- **ASE**：Python 原子模拟环境接口。
- **GROMACS + HackMD**：GROMACS 部署（可选）。
- **i-PI**：路径积分分子动力学客户端（可选）。

# common_modification_points
- 数据域适配：不同 DFT 软件的 OUTCAR 输出格式有微小差异，需用 dpdata 的 `fmt` 参数精确指定格式。
- 数据质量过滤：在 `dpdata.LabeledSystem.sub_system()` 中按能量范围、力最大值、原子距离等条件筛选构型。
- descriptor 选型：对于含氢键/共价键体系优先使用 se_e2_a/se_e3/se_atten；简单金属或惰性气体可用 se_e2_r。
- `sel` 调整：根据目标体系最大配位数设置 `sel` 参数，太小会丢失邻居信息，太大浪费显存。
- `rcut` 调整：rcut 需覆盖关键化学键长范围。对于含范德华相互作用的体系可能需要更大的 rcut（7-9 Å）。
- 压缩 trade-off：追求极致速度时可增大 `table_config` stride（精度换速度）；追求精度保持时可减小 stride。
- 多元素体系部署：确保 LAMMPS 输入中原子类型与 DP 模型的 type_map 中顺序一致。
- fine-tuning 策略：冻结 descriptor 前几层，仅 fine-tune fitting_net（transfer learning）通常更稳定。

# implementation_risks
- `sel` 不足导致 MD 模拟中模型崩溃（NaN 力）：当 MD 探索到训练数据未覆盖的密堆积构型时，邻居数可能超出 sel 上限。
- `rcut` 选择不当：太小的 rcut 可能遗漏重要化学相互作用；太大的 rcut 大幅增加计算量和显存使用。
- 冻结模型与压缩模型精度差异：dp compress 引入多项式插值近似，需在压缩后用 dp test 验证精度无明显退化。
- 能量/力/应力标签单位不一致：VASP 默认 eV/Å，LAMMPS 常用 metal units（eV/Å），但部分计算软件使用 Hartree/Bohr 或 kcal/mol/Å，需确保单位一致。
- 原子参考能（atom_ener）设置错误导致训练无法收敛或精度差。
- TensorFlow 与 PyTorch 后端兼容性：旧版 TensorFlow 训练的 `.pb` 模型无法直接在 PyTorch 环境中加载。
- LAMMPS type_map 顺序与训练数据不一致导致错误的原子类型映射（静默错误）。
- 周期/非周期体系混用：box 为零的 data system 不应部署到含 PBC 的 MD 模拟中。

# code_references
- 官方文档：`https://docs.deepmodeling.com/projects/deepmd/en/latest/`
- 训练入口：`dp train`（对应的源码模块 `deepmd/entrypoints/train.py`）
- 模型冻结：`dp freeze`（`deepmd/entrypoints/freeze.py`）
- 模型压缩：`dp compress`（`deepmd/entrypoints/compress.py`）
- 精度测试：`dp test`（`deepmd/entrypoints/test.py`）
- LAMMPS pair style：`source/lmp/pair_deepmd.cpp`（DeePMD-kit 源码中）
- DP-GEN 集成：`dpgen` 包中的 `dpgen/generator` 模块
