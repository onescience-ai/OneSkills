# launch

DP-GEN 通过命令行接口 `dpgen` 提供三大核心命令：`run`（启动主动学习循环）、`debug`（工作流调试与监控）、`collect`（收集最终数据集）。

## 基本启动命令

```sh
# 启动主动学习循环（核心命令）
dpgen run param.json machine.json

# 从特定迭代轮次启动（跳过已完成轮次）
dpgen run param.json machine.json --restart

# 调试模式（查看当前状态、失败任务）
dpgen debug param.json machine.json

# 收集所有迭代的数据集
dpgen collect param.json machine.json
```

## 典型 DP-GEN 启动流程

### 步骤 1 — 准备工作目录

```sh
# 创建工作目录
mkdir my_dpgen_project
cd my_dpgen_project

# 准备初始训练数据
mkdir -p init_data/
# 将初始 AIMD 数据（DeePMD-kit system 格式）放入 init_data/

# 准备 DFT 计算模板
# 如果使用 VASP：
#   - 创建 INCAR_template（固定 DFT 参数）
#   - 准备各元素的 POTCAR 文件（如 POTCAR_Al, POTCAR_Mg）
# 如果使用 CP2K：
#   - 创建 cp2k_input_template
```

### 步骤 2 — 编写 param.json

```sh
cat > param.json << 'EOF'
{
    "type_map": ["Al", "Mg"],
    "mass_map": [26.98, 24.31],
    "init_data_prefix": "./",
    "init_data_sys": [
        "init_data/"
    ],
    "sys_configs": [
        [8, 16, 8],
        [8, 16, 8],
        [8, 16, 8]
    ],
    "sys_batch_size": "auto",
    "numb_models": 4,
    "default_training_param": {
        "model": {
            "type": "standard",
            "descriptor": {
                "type": "se_e2_a",
                "sel": [46, 92],
                "rcut_smth": 0.5,
                "rcut": 6.0,
                "neuron": [25, 50, 100],
                "axis_neuron": 16,
                "resnet_dt": false
            },
            "fitting_net": {
                "neuron": [240, 240, 240],
                "resnet_dt": true,
                "seed": 1
            }
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
            "numb_steps": 200000,
            "seed": 1,
            "disp_file": "lcurve.out",
            "disp_freq": 1000,
            "save_freq": 10000
        }
    },
    "model_devi_dt": 0.002,
    "model_devi_skip": 0,
    "model_devi_f_trust_lo": 0.10,
    "model_devi_f_trust_hi": 1.00,
    "model_devi_v_trust_lo": 0.10,
    "model_devi_v_trust_hi": 1.00,
    "model_devi_clean_traj": true,
    "model_devi_jobs": [
        {
            "sys_idx": [0, 1, 2],
            "temps": [50, 100, 200, 300, 400, 500],
            "press": [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0],
            "trj_freq": 10,
            "nsteps": 5000,
            "ensemble": "npt",
            "_idx": "00"
        }
    ],
    "fp_style": "vasp",
    "shuffle_poscar": false,
    "fp_task_max": 20,
    "fp_task_min": 5,
    "fp_accurate_threshold": 0.999,
    "fp_accurate_soft_threshold": 0.995
}
EOF
```

### 步骤 3 — 编写 machine.json（调度器配置）

```sh
cat > machine.json << 'EOF'
{
    "train": {
        "command": "dp",
        "machine": {
            "batch_type": "Slurm",
            "local_root": "./",
            "context_type": "local",
            "tasks_per_node": 4
        },
        "resources": {
            "number_node": 1,
            "cpu_per_node": 4,
            "gpu_per_node": 4,
            "queue_name": "gpu",
            "group_size": 1,
            "source_list": ["/opt/intel/oneapi/setvars.sh"]
        }
    },
    "model_devi": {
        "command": "lmp_mpi",
        "machine": {
            "batch_type": "Slurm",
            "local_root": "./",
            "context_type": "local"
        },
        "resources": {
            "number_node": 2,
            "cpu_per_node": 32,
            "queue_name": "cpu",
            "group_size": 4,
            "source_list": ["/opt/intel/oneapi/setvars.sh"]
        }
    },
    "fp": {
        "command": "mpirun -np 32 vasp_std",
        "machine": {
            "batch_type": "Slurm",
            "local_root": "./",
            "context_type": "local"
        },
        "resources": {
            "number_node": 1,
            "cpu_per_node": 32,
            "queue_name": "cpu",
            "group_size": 1,
            "source_list": ["/opt/intel/oneapi/setvars.sh"]
        }
    }
}
EOF
```

### 步骤 4 — 准备 DFT 计算模板（VASP 示例）

```sh
cat > INCAR_template << 'EOF'
SYSTEM = DP-GEN
ENCUT = 520
ISMEAR = 0
SIGMA = 0.05
ISIF = 2
NSW = 0
IBRION = -1
EDIFF = 1E-6
EDIFFG = -0.01
LREAL = Auto
PREC = Accurate
ADDGRID = .TRUE.
NCORE = 4
EOF
```

### 步骤 5 — 启动 DP-GEN

```sh
# 首次启动
dpgen run param.json machine.json

# 监控进度（另开终端）
dpgen debug param.json machine.json

# 如果中断后需要续传
dpgen run param.json machine.json --restart
```

### 步骤 6 — 收集结果

```sh
# 收集所有轮次的标注数据
dpgen collect param.json machine.json
# 输出目录：collect_dir/ 包含合并后的 system 格式数据

# 使用收集数据进行最终模型训练
dp train final_input.json
```

## DP-GEN 命令行参考

| 命令 | 功能 | 典型用法 |
|------|------|---------|
| `dpgen run` | 启动/续传主动学习循环 | `dpgen run param.json machine.json` |
| `dpgen run --restart` | 从断点续传 | `dpgen run param.json machine.json --restart` |
| `dpgen debug` | 查看当前状态 | `dpgen debug param.json machine.json` |
| `dpgen debug --task failed` | 列出失败任务 | `dpgen debug param.json machine.json --task failed` |
| `dpgen collect` | 收集合并数据集 | `dpgen collect param.json machine.json` |
| `dpgen simplify` | 简化数据（版本迁移） | `dpgen simplify param.json machine.json` |
| `dpgen autotest` | 自动化测试流程 | `dpgen autotest param.json machine.json` |

## 关键命令行参数详解

### dpgen run

```sh
dpgen run PARAM MACHINE [OPTIONS]

Options:
  --restart           从最近的中断点续传迭代
  --debug             启用详细调试输出
  --dry-run           仅模拟运行（不实际提交任务）
```

### dpgen debug

```sh
dpgen debug PARAM MACHINE [OPTIONS]

Options:
  --task TASK_TYPE    查看特定任务类型状态
                      TASK_TYPE: train | model_devi | fp | failed
  --iter ITER         查看特定迭代轮次（如 --iter 3）
  --json              以 JSON 格式输出
```

### dpgen collect

```sh
dpgen collect PARAM MACHINE [OPTIONS]

Options:
  --iter START:END    仅收集指定轮次范围的数据
  --output-dir DIR    指定输出目录（默认 collect_dir/）
  --with-init         包含初始数据
```

## 典型 DP-GEN 运行目录结构

```
my_dpgen_project/
├── param.json                         # 主配置文件
├── machine.json                       # 资源调度配置
├── INCAR_template                     # VASP 输入模板（VASP 模式）
├── POTCAR_Al                          # Al 赝势
├── POTCAR_Mg                          # Mg 赝势
├── init_data/                         # 初始训练数据
│   ├── type.raw
│   ├── type_map.raw
│   └── set.000/
│       ├── box.npy
│       ├── coord.npy
│       ├── energy.npy
│       └── force.npy
├── iter.000/                          # 第 0 轮迭代（初始）
│   ├── 00.train/                      # 训练步骤
│   │   ├── 000/                       # 模型 0
│   │   │   ├── input.json             # 训练配置
│   │   │   ├── model.ckpt-200000.pt   # checkpoint
│   │   │   ├── frozen_model.pb        # 冻结模型
│   │   │   └── lcurve.out             # 训练曲线
│   │   ├── 001/                       # 模型 1
│   │   ├── 002/                       # 模型 2
│   │   └── 003/                       # 模型 3
│   ├── 01.model_devi/                 # 探索步骤
│   │   ├── job_000/                   # 探索任务组
│   │   │   ├── task.000.000000/       # sys=0, T=50K, P=1bar
│   │   │   │   ├── conf.lmp           # LAMMPS 初始构型
│   │   │   │   ├── input.lammps       # LAMMPS 输入
│   │   │   │   └── model_devi.out     # 模型偏差输出
│   │   │   └── task.000.000001/       # sys=0, T=50K, P=10bar
│   │   └── ...
│   └── 02.fp/                         # DFT 标注步骤
│       ├── data.000/                  # 初始数据（用户提供）
│       ├── candidate_task_list.txt    # 候选构型任务列表
│       ├── task.000.000000/           # 标注任务 0
│       │   ├── POSCAR                 # 待标注构型
│       │   ├── INCAR                  # VASP 输入
│       │   ├── POTCAR                 # VASP 赝势
│       │   ├── OUTCAR                 # VASP 输出
│       │   └── vasprun.xml            # VASP XML 输出
│       └── ...
├── iter.001/                          # 第 1 轮迭代
│   ├── 00.train/
│   │   └── ...
│   ├── 01.model_devi/
│   │   └── ...
│   └── 02.fp/
│       └── ...
├── iter.002/                          # 第 2 轮迭代
│   └── ...
└── collect_dir/                       # （运行 dpgen collect 后生成）
    ├── all_sys/
    │   ├── type.raw
    │   ├── type_map.raw
    │   └── set.000/
    │       ├── box.npy
    │       ├── coord.npy
    │       ├── energy.npy
    │       └── force.npy
    └── ...
```

# input_schema

## param.json 配置字段完整说明

### 顶层参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `type_map` | list[str] | 是 | - | 元素类型名称列表，按原子序数排序 |
| `mass_map` | list[float] | 是 | - | 对应 type_map 中各元素的原子质量（amu） |
| `init_data_prefix` | str | 否 | `"./"` | 初始数据路径前缀 |
| `init_data_sys` | list[str] | 是 | - | 初始训练数据体系路径列表（DeePMD-kit system 格式） |
| `sys_configs` | list[list] | 是 | - | 各探索体系的初始原子坐标文件 |
| `sys_batch_size` | str/int | 否 | `"auto"` | 训练 batch size |
| `numb_models` | int | 否 | `4` | Ensemble 模型数量 |
| `train_style` | str | 否 | `"dp"` | 训练后端（`"dp"` 或 `"deepmd-nvnmd"`） |
| `default_training_param` | dict | 是 | - | DeePMD-kit 训练参数模板 |
| `training_iter0_model_path` | str | 否 | - | 第 0 轮迭代使用的预训练模型路径（跳过第一轮训练） |
| `training_init_model` | bool | 否 | `false` | 是否从上一轮模型 warm-start（true）还是从头训练（false） |
| `model_devi_dt` | float | 否 | `0.002` | MD 轨迹候选输出间隔（ps） |
| `model_devi_skip` | int | 否 | `0` | 跳过 MD 开头不稳定帧数 |
| `model_devi_f_trust_lo` | float | 是 | - | 力偏差筛选下界（eV/Å） |
| `model_devi_f_trust_hi` | float | 是 | - | 力偏差筛选上界（eV/Å） |
| `model_devi_v_trust_lo` | float | 否 | `10.0` | virial 偏差筛选下界（eV） |
| `model_devi_v_trust_hi` | float | 否 | `100.0` | virial 偏差筛选上界（eV） |
| `model_devi_clean_traj` | bool/int | 否 | `true` | 完成探索后是否删除 LAMMPS 轨迹文件 |
| `model_devi_jobs` | list[dict] | 是 | - | 探索任务定义列表 |
| `fp_style` | str | 是 | - | DFT 软件类型：`"vasp"`/`"cp2k"`/`"pwmat"`/`"pwscf"`/`"siesta"`/`"gaussian"` |
| `fp_task_max` | int | 否 | - | 每轮最大并发 DFT 任务数 |
| `fp_task_min` | int | 否 | `0` | 每轮最小 DFT 任务数（低于此数终止迭代） |
| `fp_accurate_threshold` | float | 否 | `0.999` | 精确 SCF 收敛精度阈值（VASP 专有） |
| `fp_accurate_soft_threshold` | float | 否 | `0.995` | 软精度收敛阈值（VASP 专有） |
| `shuffle_poscar` | bool | 否 | `false` | DFT 标注前随机扰动原子位置 |
| `use_ele_temp` | int | 否 | `0` | 电子温度设置（VASP 专有，对应 ISMEAR, 0 表示不设置） |
| `fp_incar_template` | str | 否 | `"INCAR_template"` | VASP INCAR 模板文件路径（VASP 专有） |
| `fp_cp2k_input_template` | str | 否 | `"cp2k_input_template"` | CP2K 输入模板文件路径（CP2K 专有） |
| `fp_pp_files` | list[str] | 否 | - | 赝势文件列表（VASP 专有） |
| `fp_pp_path` | str | 否 | `"./"` | 赝势文件路径前缀（VASP 专有） |

### model_devi_jobs 探索任务定义

每个探索任务是一个 JSON 对象：

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `sys_idx` | list[int] | 是 | - | 对应 sys_configs 中体系编号的列表 |
| `temps` | list[float] | 是 | - | 探索温度列表（K） |
| `press` | list[float] | 否 | - | 探索压力列表（bar），不设置则不控压（NVT） |
| `trj_freq` | int | 是 | - | 每 N 步输出一次候选构型 |
| `nsteps` | int | 是 | - | MD 运行总步数 |
| `ensemble` | str | 是 | - | 统计系综：`"nvt"` 或 `"npt"` |
| `dt` | float | 否 | 继承 `model_devi_dt` | 时间步长（ps），若不指定则使用顶层 `model_devi_dt` |
| `_idx` | str | 是 | - | 任务组标识字符串，用于目录命名 |
| `model_devi_f_trust_lo` | float | 否 | 继承顶层 | 该任务组专用的力偏差下界覆盖值 |
| `model_devi_f_trust_hi` | float | 否 | 继承顶层 | 该任务组专用的力偏差上界覆盖值 |

### default_training_param 训练模板

使用与 DeePMD-kit `input.json` 相同的结构，但 DP-GEN 会自动补充和调整部分参数（如 seed、training_data 路径等）。

| 字段 | 说明 |
|------|------|
| `model` | descriptor 和 fitting_net 定义（与 DeePMD-kit 完全一致） |
| `learning_rate` | 学习率调度策略 |
| `loss` | 损失函数权重配置 |
| `training` | 训练控制参数（numb_steps、disp_freq、save_freq 等） |

**注意**：DP-GEN 会自动为每个 ensemble 模型分配不同的 `seed`（基于 `default_training_param.training.seed` 递增），并自动设置 `training_data` 和 `validation_data` 路径。

### machine.json 配置字段

machine.json 定义了三个阶段的执行环境：`train`、`model_devi`、`fp`。每个阶段包含：

| 字段 | 说明 |
|------|------|
| `command` | 执行命令（如 `"dp"`、`"lmp_mpi"`、`"mpirun -np 32 vasp_std"`） |
| `machine` | 调度器配置 |
| `machine.batch_type` | 调度器类型：`"Slurm"`/`"PBS"`/`"LSF"`/`"Shell"` |
| `machine.local_root` | 本地工作目录根路径 |
| `machine.context_type` | 执行上下文：`"local"`/`"ssh"`/`"lsf"` |
| `resources` | 资源需求 |
| `resources.number_node` | 分配节点数 |
| `resources.cpu_per_node` | 每节点 CPU 核数 |
| `resources.gpu_per_node` | 每节点 GPU 卡数 |
| `resources.queue_name` | 队列名称 |
| `resources.group_size` | 每作业打包的任务数 |
| `resources.source_list` | 环境初始化脚本列表 |

# runtime_interfaces

DP-GEN 的核心运行时接口：

- `dpgen run param.json machine.json`：启动/续传主动学习迭代循环。在每个迭代轮次自动执行：训练 → 探索 → 筛选 → DFT 标注 → 数据扩充
- `dpgen debug param.json machine.json`：查看当前迭代状态、各步骤的进度和失败任务
- `dpgen collect param.json machine.json`：收集所有轮次中成功标注的构型数据，合并为统一的 DeePMD-kit system 格式数据集
- `dpgen simplify param.json machine.json`：数据简化与版本迁移工具

DP-GEN 的 Python API（编程接口）：

```python
from dpgen.generator.run import run_iter
from dpgen.generator.lib.param import Param

# 通过 API 运行单轮迭代
param = Param.load("param.json", "machine.json")
run_iter(param, machine)
```

# main_functions

- `dpgen run`：主动学习迭代循环（核心命令）
- `dpgen debug`：工作流调试与状态监控
- `dpgen collect`：收集合并标注数据集

# execution_resources

- **训练阶段**：需要 GPU 节点。4 个 ensemble 模型可并行训练，每个模型需要约 4–24 GB 显存（取决于 descriptor 类型和体系规模）。推荐 NVIDIA V100/A100 或 DCU。
- **探索阶段**：需要 CPU 节点（可选 GPU 加速 LAMMPS）。多个探索任务（sys_idx × temp × press 组合）可并行执行。推荐 MPI 并行 LAMMPS，每节点 16-64 核。
- **标注阶段**：需要 CPU 节点。每个 DFT 任务独立计算，推荐每任务 16-64 核（VASP），通过 `fp_task_max` 控制最大并发数。
- **磁盘存储**：每轮迭代产生 LAMMPS dump 轨迹、DeePMD-kit checkpoint、DFT 输出文件。100 轮典型迭代总磁盘消耗约 50–200 GB。建议启用 `model_devi_clean_traj: true` 并定期使用 `dpgen collect` 归档。

# operation_limits

- DP-GEN 不是 DFT 软件，需要底层有 VASP/CP2K/PWmat/PWscf/SIESTA/Gaussian 等第一性原理软件支持
- DP-GEN 不是 MD 引擎，需要底层的 LAMMPS（编译了 DeePMD-kit 的 pair_style deepmd）来执行 MD 探索
- 主动学习的迭代终止条件为：Model Deviation 收敛（所有候选构型的最大偏差均低于 `model_devi_f_trust_lo`）或达到最大迭代轮数
- 每一轮迭代的训练是独立的（从头训练），不同于 fine-tuning 模式
- DP-GEN 第 0 轮（iter.000）的训练数据必须是用户提供的初始 DFT 标注数据，不能为空
- 使用 DP-GEN 前，必须确保 DeePMD-kit 和 LAMMPS（deepmd pair style）已正确安装和配置
- Trust levels（σ_low / σ_high）的设定需要根据目标体系的化学键强度进行校准，不当设置会导致过度标注或欠标注
- 探索任务的温度/压力范围应覆盖目标应用的全部热力学条件，否则生成的势函数在未覆盖区域的精度无法保证
