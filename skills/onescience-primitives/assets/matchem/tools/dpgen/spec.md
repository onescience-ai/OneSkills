# DP-GEN 技术规格说明

---

## #software_overview

DP-GEN（Deep Potential GENerator）是一个主动学习（Active Learning）框架，用于自动化生成 Deep Potential（DP）系列势函数的训练数据。其核心思想是通过"探索-标注-训练"（Exploration-Labeling-Training）的闭环迭代，从少量初始第一性原理分子动力学（AIMD）数据出发，自动探索体系的构型空间，筛选不确定性高的构型进行 DFT 标注，并重新训练势函数，最终构建出覆盖目标相空间的高质量 MLIP（Machine Learning Interatomic Potential）训练数据集。

DP-GEN 的定位是一个 HPC 工作流编排引擎，而非直接的物理模拟器。它并不自行执行 DFT 计算或 MD 模拟，而是通过调用外部软件完成以下分工：
- **训练**：调用 DeePMD-kit（`dp train`）训练 ensemble 模型（默认 4 个独立初始化的模型）
- **探索**：调用 LAMMPS（`pair_style deepmd`）使用 ensemble 模型进行 MD 模拟，在温度/压力/应变等热力学条件下搜索构型空间
- **筛选**：通过 DeePMD-kit 的 `model_devi` 模块计算 Model Deviation（模型偏差），根据用户设定的 trust levels（σ_low / σ_high）筛选候选构型
- **标注**：调用 VASP / CP2K / PWmat / PWscf / SIESTA / Gaussian 等第一性原理软件，对候选构型进行 DFT 单点能计算，获取能量、力和应力（virial）标签
- **迭代**：将新标注数据加入训练集，自动触发下一轮训练，直至 Model Deviation 收敛或达到预设最大迭代轮数

DP-GEN 的设计哲学是实现"端到端"势函数开发：用户只需提供初始数据和配置文件，框架会自动完成数据扩展、模型训练和质量评估的全流程，极大降低了 MLIP 构建的入门门槛和人工干预需求。该框架特别适合那些缺乏大量 DFT 训练数据、但需要高精度 MLIP 的研究场景。

---

## #core_concepts

### 主动学习 / 并发学习（Active Learning / Concurrent Learning）

DP-GEN 采用主动学习策略（在材料模拟领域也称为 Concurrent Learning），其核心循环如下：

```
┌─────────────────────────────────────────────────────────────┐
│  iter.000          iter.001          iter.002    ...         │
│                                                             │
│  初始数据 ──▶ 训练 ──▶ 探索 ──▶ 筛选 ──▶ 标注 ──▶ 数据扩充  │
│              ▲                                       │      │
│              └────────────────── 迭代 ◀──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

每一轮迭代包含以下步骤：

1. **初始数据准备**：用户通过少量 AIMD（推荐 100–500 个构型作为起点）或已有 DFT 计算结果作为初始训练集，放置在 `iter.000/` 目录下
2. **训练（00.train）**：使用当前全部已标注数据训练一组 ensemble 模型（4 个），每个模型使用不同的随机初始化种子
3. **探索（01.model_devi）**：使用 ensemble 模型在 LAMMPS 中驱动 MD 模拟，在目标热力学条件下探索构型空间。每 N 步输出候选构型，计算 model deviation
4. **筛选**：根据 model deviation 筛选候选构型：
   - 若 $\\sigma_{\\max}$ 在 $[\\sigma_{\\text{low}}, \\sigma_{\\text{high}}]$ 范围内 → 模型的预测不确定性适中，标记为"需标注"构型
   - 若 $\\sigma_{\\max} < \\sigma_{\\text{low}}$ → 模型预测已很准确，丢弃
   - 若 $\\sigma_{\\max} > \\sigma_{\\text{high}}$ → 构型可能不合理（物理上不稳定），丢弃
5. **标注（02.fp）**：对筛选出的构型启动 DFT 计算（VASP/CP2K 等），获取能量、力和应力标签
6. **数据扩充**：将新标注的构型与已有训练集合并，进入下一轮迭代

DP-GEN 自动维护每轮迭代的目录结构：`iter.000/`, `iter.001/`, `iter.002/` ...

### Model Deviation（模型偏差）

Model Deviation 是 DP-GEN 筛选候选构型的核心指标，基于 ensemble of models 方法计算：

- **计算方法**：使用 N 个（默认 4 个）独立训练的 DP 模型，对同一构型分别预测原子受力 $\\mathbf{F}_i^{(1)}, \\mathbf{F}_i^{(2)}, ..., \\mathbf{F}_i^{(N)}$，计算每个原子的受力标准差：
  $$
  \\sigma_i = \\text{std}(\\mathbf{F}_i^{(1)}, \\mathbf{F}_i^{(2)}, \\mathbf{F}_i^{(3)}, \\mathbf{F}_i^{(4)})
  $$
- **最大力偏差**：$\\sigma_{\\max} = \\max_i(\\sigma_i)$，这是最常用的筛选判据
- **原子力偏差**：$\\sigma_i$，每个原子的偏差，可用于定位哪些化学环境的不确定性最高

Model Deviation 既支持力偏差（`model_devi_f_trust_lo/hi`），也支持 virial/应力偏差（`model_devi_v_trust_lo/hi`）。

### Trust Levels（可信度阈值）

Trust Levels 分为下界（lo）和上界（hi），分别控制筛选的灵敏度：

- **σ_low（下界）**：低于此值的构型被认为模型已充分学习，无需额外标注。设置过高会导致标注不足、模型精度不够；设置过低会导致大量构型被选中、DFT 计算资源浪费
- **σ_high（上界）**：高于此值的构型被认为是不合理的离群构型（如两个原子距离过近导致力异常大），丢弃以避免污染数据库。设置过低会丢失有价值的构型；设置过高会引入不合理构型

典型 trust level 取值（需根据体系化学键强度调整）：

| 体系类型 | f_trust_lo (eV/Å) | f_trust_hi (eV/Å) | 说明 |
|---------|-------------------|-------------------|------|
| 简单金属（Al、Cu） | 0.05–0.10 | 0.50–1.00 | 金属键较弱 |
| 共价晶体（Si、C） | 0.10–0.30 | 1.00–3.00 | 共价键强、方向性强 |
| 离子晶体（NaCl） | 0.05–0.15 | 0.50–1.50 | 中等强度 |
| 水/分子液体 | 0.10–0.20 | 1.00–2.00 | 分子间+分子内 |
| 高压体系 | 0.20–0.50 | 2.00–5.00 | 压力导致更大的力 |

### Ensemble of Models

DP-GEN 使用 ensemble strategy 评估模型的认知不确定性（epistemic uncertainty）：

- 默认使用 4 个独立训练的模型
- 每个模型使用相同的 hyperparameters（descriptor、fitting_net 配置），但不同的随机种子（seed）初始化权重
- 在某些策略下也支持使用不同超参数的模型组成异构 ensemble
- Ensemble 模型的数量是一个 trade-off：更多模型提高 deviation 的统计可靠性，但增加训练计算成本（正比于模型数）
- 4 个模型是经验上训练成本与 deviation 可靠性之间的最佳平衡点

### 探索策略（Exploration Strategies）

DP-GEN 支持多种探索策略来覆盖构型空间：

1. **温度升温探索**：从低温到高温逐步升温，系统性地覆盖势能面不同能量区域
2. **压力扫描**：在不同压力（或应力）条件下进行 MD，获取不同密度/体积下的构型
3. **多相共存**：对复杂体系（如含缺陷、界面）分别设置不同的初始构型进行独立探索
4. **扰动增强探索**：通过随机扰动原子位置或速度，扩大探索范围

### 并发任务提交

DP-GEN 的设计目标之一是高效利用 HPC 资源。同一迭代轮次中的多个 DFT 计算任务可以并发提交到队列系统：

- 每个被筛选出的构型对应一个独立的 DFT 计算任务
- DP-GEN 通过 `machine.json` 和 Slurm/PBS/LSF 接口自动生成并提交这些任务
- 支持设置最大并发任务数 (`numb_task`) 以避免过度占用队列资源
- 任务完成后自动检测结果、标记失败任务并支持重试

### DP-GEN 与 DeePMD-kit 的关系

DP-GEN 是 DeePMD-kit 的上游数据生成框架：
- DeePMD-kit 提供模型训练、推理、压缩等核心 ML 能力
- DP-GEN 使用 DeePMD-kit 作为 ML 引擎，在此基础上增加了主动学习循环控制、HPC 任务编排、DFT 软件接口等功能
- 典型的端到端工作流：**DP-GEN（数据生成）→ DeePMD-kit（最终模型训练）→ LAMMPS（MD 部署）**

---

## #common_workflows

### 工作流 1：标准 DP-GEN 主动学习（从头构建 MLIP 数据集）

**目标**：为特定材料体系从头构建高质量的 DP 训练数据集。

**步骤**：

**步骤 1 — 初始数据准备**

从短时 AIMD（如 2–10 ps、100–500 帧）或已有 DFT 计算中获取初始构型，转换为 DeePMD-kit 原生 system 格式：
```python
import dpdata
ls = dpdata.LabeledSystem('OUTCAR', fmt='vasp/outcar')
ls.to_deepmd_npy('./init_data/')
```
初始数据放置在 `iter.000/02.fp/` 目录下（以 data.000, data.001 等命名）。

**步骤 2 — 配置文件编写**

编写三个核心配置文件：

`param.json`（整体配置）：
```json
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
```

`machine.json`（集群与DFT任务参数）：
```json
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
```

`generate_input.py` 或 VASP 模板（`INCAR_template`、`POTCAR`）文件，提供 DFT 计算的固定参数。

**步骤 3 — 启动迭代**
```bash
dpgen run param.json machine.json
```

**步骤 4 — 监控与调试**
```bash
# 查看当前迭代状态
dpgen debug param.json machine.json

# 检查失败任务
dpgen debug param.json machine.json --task failed

# 手动重试失败任务
dpgen run param.json machine.json --restart
```

**步骤 5 — 收集最终数据集**
```bash
dpgen collect param.json machine.json
```
收集所有迭代轮次中成功标注的构型，合并为统一数据集。

**步骤 6 — 最终训练**
使用收集到的完整数据集，在 DeePMD-kit 中进行最终模型训练（通常使用更大的训练步数和更精细的超参数调优）。

### 工作流 2：基于已有数据集的扩展（数据增强）

**目标**：为已有 DP 模型补充训练数据，提高特定热力学条件下的精度。

**步骤**：
1. 准备已有标注数据集
2. 修改 `param.json` 中的 `init_data_sys` 指向已有数据集
3. 调整 `model_devi_jobs` 中的探索条件（temps/press），聚焦于当前模型预测较差的区域
4. 执行 `dpgen run`，DP-GEN 将自动在已有数据基础上进行扩展

### 工作流 3：多相体系主动学习

**目标**：为含多相（固相+液相、不同晶体相）的体系构建统一势函数。

**步骤**：
1. 在 `param.json` 的 `model_devi_jobs` 中配置多个 sys_idx，每个对应不同的初始结构
2. `sys_configs` 参数中分别指定各体系的初始原子坐标和晶胞
3. DP-GEN 将为每个 sys_idx 分别启动独立的 MD 探索轨迹
4. 确保 trust levels 足够宽松以覆盖各相的力范围差异

---

## #key_parameters

### param.json 核心参数

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| `type_map` | 元素类型映射 | `["Al", "Mg"]` | 按原子序数排列的元素列表 |
| `mass_map` | 原子质量 | `[26.98, 24.31]` | 对应 type_map 中各元素的质量（amu） |
| `numb_models` | Ensemble 模型数 | 4 | 训练模型数量，建议 3-6 |
| `init_data_sys` | 初始数据路径 | `["init_data/"]` | DeePMD-kit system 格式的初始训练数据 |
| `sys_configs` | 探索体系原子坐标 | `[[8,16,8], ...]` | 每个 sys 的原子坐标文件路径（POSCAR 格式） |
| `sys_batch_size` | 训练 batch size | `"auto"` | 训练时使用的 batch size |
| `default_training_param` | 训练超参数模板 | （见示例） | 传递给 DeePMD-kit 的 input.json 内容模板 |

### machine.json（model_devi 探索参数）

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| `model_devi_dt` | MD 轨迹输出间隔 (ps) | 0.002 | 每 ps 输出一个构型候选用于偏差判断 |
| `model_devi_skip` | 跳过前 N 帧 | 0 | 跳过 MD 开头的不稳定帧 |
| `model_devi_f_trust_lo` | 力偏差下界 (eV/Å) | 0.05–0.30 | 低于此值的构型被丢弃（模型已准确） |
| `model_devi_f_trust_hi` | 力偏差上界 (eV/Å) | 0.50–3.00 | 高于此值的构型被丢弃（不合理构型） |
| `model_devi_v_trust_lo` | virial 偏差下界 (eV) | 0.10 | 应力的偏差筛选下界 |
| `model_devi_v_trust_hi` | virial 偏差上界 (eV) | 1.00 | 应力的偏差筛选上界 |
| `model_devi_clean_traj` | 是否清理轨迹文件 | `true` | 完成后自动删除 LAMMPS dump 轨迹以节省磁盘 |
| `model_devi_jobs` | 探索任务列表 | （详见下文） | 可配置多个探索任务 |

### model_devi_jobs 子参数

每个探索任务对象包含：

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| `sys_idx` | 体系索引列表 | `[0, 1, 2]` | 对应 sys_configs 中的体系编号 |
| `temps` | 温度列表 (K) | `[50, 100, 200, 300, 400, 500]` | 每个温度启动一个独立 MD 轨迹 |
| `press` | 压力列表 (bar) | `[1.0, 10.0, 100.0, 1000.0]` | 每个压力启动一个独立 MD 轨迹 |
| `trj_freq` | 候选输出频率 | 10 | 每 N 步输出一次构型进行模型偏差计算 |
| `nsteps` | MD 运行步数 | 5000 | 每个 MD 轨迹的总步数 |
| `ensemble` | 统计系综 | `"npt"` / `"nvt"` | MD 使用的统计系综类型 |
| `dt` | 时间步长 (ps) | 0.001 | 默认可不设置，在 machine.json 顶层定义了 model_devi_dt |
| `_idx` | 任务组标识 | `"00"` | 用于构建目录名的标识字符串 |

### fp（DFT 标注）参数

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| `fp_style` | DFT 软件类型 | `"vasp"`, `"cp2k"`, `"pwmat"`, `"pwscf"`, `"siesta"`, `"gaussian"` | 标注所用的第一性原理软件 |
| `fp_task_max` | 最大并发 DFT 任务数 | 20 | 同一轮迭代中同时提交的 DFT 任务数上限 |
| `fp_task_min` | 最小 DFT 任务数 | 5 | 当候选构型低于此数时取消本轮迭代 |
| `fp_accurate_threshold` | 精确收敛阈值 | 0.999 | VASP SCF 收敛精度（EDIFF），0.999 对应默认精度 |
| `fp_accurate_soft_threshold` | 软精度阈值 | 0.995 | 若 SCF 收敛困难，允许退而求其次的精度 |
| `shuffle_poscar` | 随机扰动 POSCAR | `false` | 标注前是否随机扰动原子位置（防对称性陷阱） |

### train（训练）参数

| 参数 | 含义 | 典型取值 | 说明 |
|------|------|----------|------|
| `numb_steps` | 训练总步数 | 200,000 – 1,000,000 | 主动学习中每轮训练步数，通常较最终训练少 |
| `start_lr` | 起始学习率 | 0.001 | 主动学习中每轮从头训练，不使用 fine-tuning |
| `stop_lr` | 终止学习率 | 3.51e-8 | 指数衰减终点 |
| `decay_steps` | 衰减步数 | 5000 | 学习率衰减的指数衰减步长 |
| `start_pref_f` | 力损失起始权重 | 1000 | 初期强调力精度的拟合 |
| `limit_pref_f` | 力损失最终权重 | 1.0 | 后期平衡能量与力的精度 |

---

## #input_file_structure

### 配置文件体系

DP-GEN 使用多个 JSON 配置文件和各阶段模板文件，完整结构如下：

```
dpgen_workspace/
├── param.json                    # 主配置文件（整体流程控制）
├── machine.json                  # 资源与调度配置文件
├── INCAR_template                # VASP 计算模板（当 fp_style=vasp 时）
├── POTCAR_Al                     # Al 元素的 POTCAR（VASP）
├── POTCAR_Mg                     # Mg 元素的 POTCAR（VASP）
├── input.lammps.template         # LAMMPS 输入模板（可选自定义）
├── iter.000/                     # 第 0 轮（初始数据）
│   ├── 00.train/                 # 训练目录
│   │   ├── 000/                  # 第 0 个模型的训练
│   │   │   ├── input.json        # 自动生成的 DeePMD-kit 训练配置
│   │   │   ├── model.ckpt-*.pt   # 训练 checkpoint
│   │   │   └── lcurve.out        # 训练曲线
│   │   ├── 001/
│   │   ├── 002/
│   │   └── 003/
│   ├── 01.model_devi/            # 探索目录
│   │   ├── task.000.000000/      # sys_idx=0, temp/press组合1
│   │   │   ├── conf.lmp          # LAMMPS 初始构型
│   │   │   ├── input.lammps      # 自动生成的 LAMMPS 输入
│   │   │   └── model_devi.out    # 模型偏差输出
│   │   ├── task.000.000001/
│   │   └── ...
│   ├── 02.fp/                    # DFT 标注目录
│   │   ├── data.000/             # 初始数据（用户提供）
│   │   ├── task.000.000000/      # 标注任务
│   │   │   ├── POSCAR            # 待标注构型
│   │   │   ├── INCAR
│   │   │   ├── POTCAR
│   │   │   ├── OUTCAR
│   │   │   └── vasprun.xml
│   │   └── ...
│   └── 03.validate/              # （可选）验证目录
├── iter.001/                     # 第 1 轮（主动学习第一轮）
│   ├── 00.train/
│   ├── 01.model_devi/
│   ├── 02.fp/
│   └── ...
├── iter.002/
│   └── ...
└── iter.N/                       # 最终轮次
```

### param.json 完整结构

```json
{
    "type_map": [...],              // 元素类型映射（必需）
    "mass_map": [...],              // 原子质量（必需）
    "init_data_prefix": "./",       // 初始数据路径前缀
    "init_data_sys": [...],         // 初始数据体系列表（必需）
    "sys_configs": [...],           // 探索体系原子坐标配置
    "sys_batch_size": "auto",       // 训练 batch size
    "numb_models": 4,               // Ensemble 模型数
    "train_style": "dp",           // 训练后端（dp 或 deepmd-nvnmd）
    "default_training_param": {...}, // 训练超参数模板
    "model_devi_dt": 0.002,        // 候选输出间隔 (ps)
    "model_devi_skip": 0,          // 跳过帧数
    "model_devi_f_trust_lo": ...,  // 力偏差下界
    "model_devi_f_trust_hi": ...,  // 力偏差上界
    "model_devi_v_trust_lo": ...,  // virial 偏差下界
    "model_devi_v_trust_hi": ...,  // virial 偏差上界
    "model_devi_clean_traj": true, // 是否清理轨迹
    "model_devi_jobs": [...],      // 探索任务定义
    "fp_style": "vasp",           // DFT 软件类型
    "shuffle_poscar": false,       // 是否随机扰动
    "fp_task_max": 20,            // 最大并发 DFT 任务
    "fp_task_min": 5,             // 最小 DFT 任务数
    "fp_accurate_threshold": ...,  // 精度阈值
    "fp_accurate_soft_threshold": ...,
    "use_ele_temp": 0              // 电子温度 (0 表示不使用)
}
```

### machine.json 完整结构

```json
{
    "train": {
        "command": "dp",           // 训练命令
        "machine": {
            "batch_type": "Slurm", // 调度器类型（Slurm/PBS/LSF/Shell）
            "local_root": "./",
            "context_type": "local" // 执行上下文（local/ssh/lsf）
        },
        "resources": {
            "number_node": 1,      // 节点数
            "cpu_per_node": 4,     // 每节点 CPU 核数
            "gpu_per_node": 4,     // 每节点 GPU 数
            "queue_name": "gpu",   // 队列名
            "group_size": 1,       // 每组任务数
            "source_list": [...]   // 环境初始化脚本
        }
    },
    "model_devi": {
        "command": "lmp_mpi",      // LAMMPS 可执行文件
        "machine": { ... },
        "resources": { ... }
    },
    "fp": {
        "command": "mpirun -np 32 vasp_std", // DFT 可执行文件
        "machine": { ... },
        "resources": { ... }
    }
}
```

### 支持的 DFT 软件及模板文件

| fp_style | 所需模板文件 | 说明 |
|----------|------------|------|
| `vasp` | INCAR_template, POTCAR_* | VASP 单点能计算 |
| `cp2k` | cp2k_input_template | CP2K DFT 计算 |
| `pwmat` | etot.input_template, atom.config_template | PWmat DFT 计算 |
| `pwscf` | pwscf_input_template | Quantum ESPRESSO |
| `siesta` | siesta_input_template | SIESTA DFT |
| `gaussian` | gaussian_input_template | Gaussian 量子化学 |

---

## #hpc_considerations

### 并行策略与资源分配

DP-GEN 是典型的三层并行工作流，每层有不同的资源需求：

**训练层（00.train）：**
- 需求：GPU 节点，每模型至少 1 张 GPU
- ensemble 模型可并行训练（4 个模型同时训练 → 4 个 GPU）
- DP-GEN 会自动为每个模型生成独立的 input.json，分配不同的 seed
- 建议：使用 GPU 节点（NVIDIA V100/A100/DCU），每模型 200,000 – 500,000 步训练
- 训练数据路径需要在所有训练节点上可访问（共享文件系统）

**探索层（01.model_devi）：**
- 需求：CPU 节点（含 GPU 加速 LAMMPS 可选），MPI 并行
- 每个探索任务（sys_idx × temp × press 的组合）可独立运行
- 建议配置 `group_size` 参数将多个温度/压力组合打包到同一个作业（减少作业提交数）
- LAMMPS deepmd pair style 的推理可使用 GPU 加速，也可纯 CPU

**标注层（02.fp）：**
- 需求：CPU 多核节点，纯 MPI 并行
- 每个候选构型是一个独立的 DFT 单点能计算
- 通过 `fp_task_max` 控制最大并发任务数，避免过度占用队列
- 建议：每个 VASP 任务使用 16-64 核，根据体系规模调整

### 队列管理策略

```json
// 示例：三级队列配置
{
    "train": {
        "resources": {
            "queue_name": "gpu_v100",     // GPU 训练队列
            "number_node": 1,
            "gpu_per_node": 4
        }
    },
    "model_devi": {
        "resources": {
            "queue_name": "cpu_large",    // CPU LAMMPS 队列
            "number_node": 4,
            "cpu_per_node": 32,
            "group_size": 8               // 每个作业打包 8 个探索任务
        }
    },
    "fp": {
        "resources": {
            "queue_name": "cpu_small",    // CPU DFT 队列
            "number_node": 1,
            "cpu_per_node": 32,
            "group_size": 1               // 每个 DFT 任务单独一个作业
        }
    }
}
```

### 磁盘存储管理

- 每轮迭代产生大量 LAMMPS dump 轨迹文件（设置 `model_devi_clean_traj: true` 自动清理）
- DFT 输出文件（OUTCAR、WAVECAR、CHGCAR）占用大量空间，建议定期清理或压缩归档
- 建议使用 `dpgen collect` 定期将已标注构型导出并归档，清理原始迭代目录
- 典型磁盘消耗：100 轮迭代、每轮 50 个标注构型 → 约 50–200 GB（取决于体系大小）

### 容错与断点续传

- **任务失败处理**：DP-GEN 自动检测失败任务并记录到日志，支持 `dpgen run --restart` 重新提交失败任务
- **迭代中断续传**：如果整个 `dpgen run` 进程被中断，重新运行相同命令会自动检测已完成步骤并跳过
- **DFT 收敛失败**：若某个构型的 DFT 计算不收敛，DP-GEN 会自动（可选）降低精度重试（`fp_accurate_soft_threshold`），或标记为失败跳过
- **训练发散**：如训练 loss 不下降，DP-GEN 会警告但不自动停止，需人工判断是否需要调整超参数

### 典型资源估算

| 体系规模 | 元素数 | 每轮 VASP 任务数 | 每轮机时估算 | 推荐迭代轮数 |
|---------|--------|----------------|-------------|-------------|
| 小分子/简单晶体 (<50 atoms) | 1-2 | 10-30 | ~100-500 CPU·h | 10-30 |
| 中等晶体 (50-150 atoms) | 2-3 | 20-60 | ~500-2000 CPU·h | 20-50 |
| 复杂体系 (>150 atoms) | 3+ | 30-100 | ~2000-10000 CPU·h | 30-80+ |

### 跨调度器支持

DP-GEN 支持主流 HPC 调度系统：
- **Slurm**：`"batch_type": "Slurm"`，通过 `sbatch` 提交、`squeue` 查询
- **PBS/Torque**：`"batch_type": "PBS"`，通过 `qsub` 提交、`qstat` 查询
- **LSF**：`"batch_type": "LSF"`，通过 `bsub` 提交、`bjobs` 查询
- **Shell**：`"batch_type": "Shell"`，在本地直接运行（适用于工作站或交互式节点）

---

## #source_references

- [DP-GEN 官方文档](https://docs.deepmodeling.com/projects/dpgen/en/latest/)
- [DP-GEN GitHub 仓库](https://github.com/deepmodeling/dpgen)
- [DP-GEN 快速入门教程](https://docs.deepmodeling.com/projects/dpgen/en/latest/quick-start/index.html)
- [DP-GEN param.json 参数详解](https://docs.deepmodeling.com/projects/dpgen/en/latest/param.html)
- [DP-GEN machine.json 参数详解](https://docs.deepmodeling.com/projects/dpgen/en/latest/machine.html)
- [DeePMD-kit 官方文档](https://docs.deepmodeling.com/projects/deepmd/en/latest/)
