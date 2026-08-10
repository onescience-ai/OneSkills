# launch
推荐通过 OneScience DeepMD demo YAML 启动训练，先 dry-run 检查最终命令与数据路径，再正式运行：

``` sh
cd examples/matchem/deepmd/demo
bash run.sh --config configs/water_se_e2_a.yaml --dry-run
bash run.sh --config configs/water_se_e2_a.yaml
```

直接使用训练入口时，可按 water 配置展开为完整参数：

``` sh
dp train water_se_e2_a.json
```

# input_schema
训练数据准备（通过 `dpdata`）：

- 数据格式：支持 VASP (`OUTCAR`/`vasprun.xml`)、CP2K、LAMMPS dump、Quantum ESPRESSO、Gaussian、extxyz 等。
- `dpdata.LabeledSystem`：从 DFT 输出文件中读取坐标、能量、力和应力。
  ``` python
  import dpdata
  data = dpdata.LabeledSystem("OUTCAR", fmt="vasp/outcar")
  print(data["energies"])  # (Nframes,)
  print(data["forces"])    # (Nframes, Natoms, 3)
  print(data["coords"])    # (Nframes, Natoms, 3)
  ```
- `DeepmdDataSystem`：DeepMD 内部训练数据管理类，负责批处理、邻域搜索和 shuffle。

训练输入 JSON 关键字段：
- `model`：模型配置块。
  - `type_map`：元素名称列表，如 `["O", "H"]`。
  - `descriptor`：descriptor 子配置。
    - `type`：如 `"se_e2_a"`。
    - `sel`：每种元素的邻居数上限，如 `[80, 80]`。
    - `rcut`：截断半径，Å。
    - `rcut_smth`：平滑起始半径，Å。
    - `neuron`：embedding 层神经元数，如 `[25, 50, 100]`。
    - `axis_neuron`：axis neuron 数，如 `4`。
  - `fitting_net`：fitting net 子配置。
    - `neuron`：隐层神经元数，如 `[240, 240, 240]`。
    - `resnet_dt`：是否使用残差连接，`true`。
- `learning_rate`：学习率配置。
  - `type`：`"exp"` 指数衰减。
  - `start_lr`：初始学习率，如 `0.001`。
  - `decay_steps`：衰减步数。
- `training`：训练配置。
  - `training_data`：训练数据配置。
    - `systems`：数据系统路径列表。
    - `batch_size`：如 `"auto"` 或具体值。
  - `validation_data`：验证数据配置。
  - `numb_steps`：总训练步数，如 `1000000`。
  - `seed`：随机种子。
  - `disp_file`：`"lcurve.out"`，学习曲线输出文件。
  - `disp_freq`：输出频率。
  - `save_freq`：checkpoint 保存频率。
- `loss`：损失函数配置。
  - `type`：`"ener"`。
  - `start_pref_e`、`limit_pref_e`：能量损失前置因子起始值与上限。
  - `start_pref_f`、`limit_pref_f`：力损失前置因子起始值与上限。
  - `start_pref_v`、`limit_pref_v`：virial 损失前置因子（可选）。

# model_construction
## Python 中构造模型
DeepMD 模型的构造通过 JSON 配置文件完成，训练时由 `dp train` 命令自动构建：

``` python
# 训练入口（命令行）
# dp train input.json

# 或通过 Python API 加载已训练模型
from deepmd.infer import DeepPot

# 加载 frozen model
dp = DeepPot("frozen_model.pb")
```

## 模型冻结（model freezing）
训练完成后，使用 `dp freeze` 命令将 checkpoint 冻结为 `.pb` 文件：

``` sh
dp freeze -o frozen_model.pb
```

此命令将当前的 `model.ckpt` 冻结为 `frozen_model.pb`，包含完整的计算图和权重，可用于推理部署。

指定 checkpoint 编号的冻结：

``` sh
dp freeze --checkpoint-folder ./train/ -o frozen_model.pb
```

# runtime_interfaces
## DeepPot 推理接口
``` python
from deepmd.infer import DeepPot
import numpy as np

# 加载 frozen model
dp = DeepPot("frozen_model.pb")

# 准备输入
coord = np.array([[0.0, 0.0, 0.0],
                   [0.0, 0.0, 1.0]])  # (Natoms, 3)
cell = np.eye(3) * 10.0                # (3, 3)
atype = np.array([0, 1])               # (Natoms,)

# 推理
energy, force, virial = dp.eval(coord, cell, atype)
print(f"Energy: {energy} eV")
print(f"Forces:\n{force}")
print(f"Virial:\n{virial}")

# 获取逐原子能量（若模型支持）
energy, force, virial, atom_energy, atom_virial = dp.eval(
    coord, cell, atype, atomic=True
)
```

`DeepPot.eval()` 参数说明：
- `coord`：`(Natoms, 3)`，原子坐标（Å）。
- `cell`：`(3, 3)` 或 `(9,)`，晶胞参数（Å）。
- `atype`：`(Natoms,)`，原子类型（整数，0 起始）。
- `atomic`：`bool`，是否返回逐原子能量和维里。
- 返回值：`(energy, force, virial)` 或 `(energy, force, virial, atom_energy, atom_virial)`。

## LAMMPS 接口
在 LAMMPS 输入脚本中使用 DeepMD 势函数：

``` lammps
# LAMMPS 输入文件示例
units           metal
atom_style      atomic
boundary        p p p

# 使用 DeepMD pair style
pair_style      deepmd frozen_model.pb
pair_coeff      * *

# 或指定元素对
pair_coeff      * * O H
```

LAMMPS 编译时需包含 `USER-DEEPMD` 包：

``` sh
# 编译 LAMMPS with DeepMD
cmake -D PKG_USER-DEEPMD=ON -D DEEPMD_ROOT=/path/to/deepmd-kit .
make -j 4
```

运行时需确保 `libdeepmd.so` 在 `LD_LIBRARY_PATH` 中。

## ASE 计算器接口
``` python
from ase import Atoms
from ase.optimize import BFGS
from deepmd.calculator import DP

# 定义体系
atoms = Atoms("H2O",
              positions=[[0.0, 0.0, 0.0],
                         [0.9, 0.0, 0.0],
                         [-0.3, 0.8, 0.0]],
              cell=[10, 10, 10],
              pbc=True)

# 设置 DeepMD calculator
atoms.calc = DP(model="frozen_model.pb")

# 能量和力
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
print(f"Energy: {energy} eV")
print(f"Forces:\n{forces}")

# 结构弛豫
opt = BFGS(atoms)
opt.run(fmax=0.01)
```

# main_functions
- `DeepPot.eval(coord, cell, atype, atomic=False)`：推理接口，返回能量、力、应力和可选的逐原子量。
- `dp train input.json`：训练入口。
- `dp freeze -o frozen_model.pb`：模型冻结。
- `dp test -m frozen_model.pb -s system_dir`：模型测试。
- `dp compress -i input.json -o compressed_model.pb`：模型压缩（量化，减少推理开销）。

# execution_resources
- CPU 可用于数据预处理、`dpdata` 格式转换和小规模 smoke test。
- 训练建议使用 GPU/DCU；DeepMD 训练的计算瓶颈在邻域搜索和自动微分。
- 显存消耗与 `sel`、`Natoms`、`batch_size`、fitting net 的 `neuron` 直接相关。
- 力计算需要额外的显存用于反向传播。
- 分布式训练支持 `horovod` 或 `dp train --mpi`，数据并行效率依赖于通信带宽。
- DPA-3/DPA-4 等大型预训练模型需要较大显存（通常 16-32 GB GPU）。
- 推理（LAMMPS/ASE）的资源消耗远低于训练，可在单 CPU 或 GPU 上运行大规模 MD。

# operation_limits
- `rcut` 必须小于晶胞最小边长的一半（周期体系），否则邻域搜索会错误地跨越多重周期边界。
- `sel` 必须大于训练数据中所有构型的实际邻居数，否则信息被截断，但过大的 `sel` 会增加内存和计算开销。
- `type_map` 的元素顺序和数量必须与训练数据完全一致，且 `sel` 和 `fitting_net.neuron` 需与 `type_map` 的长度匹配。
- 冻结模型（`.pb`）与 LAMMPS 的 `USER-DEEPMD` 版本需兼容：建议使用同一版本的 DeepMD-kit 编译 LAMMPS 插件。
- Energy/force/virial 的单位必须在数据处理、训练和推理各阶段保持一致（深势内部使用 eV、eV/Å、eV）。
- 非周期体系不提供应力/维里预测，需将 `cell` 设为足够大的真空盒子或使用开放边界条件。
- DPLR 模型需要虚拟原子（Wannier center）的位置和 Ewald 参数，适用于离子/极性体系但不适用于所有场景。
- 模型压缩（`dp compress`）会引入精度损失，需验证压缩后模型与原模型的能量/力一致性。
