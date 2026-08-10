# launch
DeePMD-kit 通过命令行接口 `dp` 提供训练、操作和部署功能。最基本的启动方式：

```sh
# 训练模型
dp train input.json

# 使用 PyTorch 后端
dp --pt train input.json

# 使用 TensorFlow 后端
dp --tf train input.json
```

## 典型训练启动流程

### 步骤 1 — 数据准备（使用 dpdata）
```python
import dpdata

# 读取 VASP 计算结果
ls = dpdata.LabeledSystem('OUTCAR', fmt='vasp/outcar')

# 划分训练集和验证集
ms = dpdata.MultiSystems(ls)
train, valid = ms.train_test_split(test_size=0.1, seed=42)

# 写入 DeePMD-kit 原生格式
dpdata.LabeledSystem.to_deepmd_npy(train, './train_data/')
dpdata.LabeledSystem.to_deepmd_npy(valid, './valid_data/')
```

### 步骤 2 — 编写 input.json 配置
```sh
# 创建 input.json
cat > input.json << 'EOF'
{
  "model": {
    "type": "standard",
    "descriptor": {
      "type": "se_e2_a",
      "sel": [46, 92],
      "rcut_smth": 0.5,
      "rcut": 6.0,
      "neuron": [25, 50, 100],
      "axis_neuron": 16,
      "seed": 1
    },
    "fitting_net": {
      "type": "ener",
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
    "training_data": {
      "systems": ["./train_data/"],
      "batch_size": "auto",
      "auto_prob": "prob_sys_size"
    },
    "validation_data": {
      "systems": ["./valid_data/"],
      "batch_size": 1
    },
    "numb_steps": 1000000,
    "seed": 10,
    "disp_file": "lcurve.out",
    "disp_freq": 1000,
    "save_freq": 10000
  }
}
EOF
```

### 步骤 3 — 训练
```sh
# 单卡训练
dp train input.json

# 四卡并行训练（需安装 Horovod）
horovodrun -np 4 dp train input.json

# PyTorch 后端多 GPU 训练
dp --pt train input.json
```

### 步骤 4 — 模型操作
```sh
# 冻结模型
dp freeze -o frozen_model.pb

# 指定 checkpoint 步数冻结
dp freeze -c 500000 -o frozen_model.pb

# 压缩模型（先准备包含 compress 参数的 input.json）
dp compress input.json -i frozen_model.pb -o compressed_model.pb

# 精度测试
dp test -m frozen_model.pb -s ./test_data/ -d detail_output -n 100
```

### 步骤 5 — LAMMPS 部署
```bash
# LAMMPS 输入文件
pair_style deepmd frozen_model.pb
pair_coeff * *
```

### Finetuning（DPA-3 预训练模型微调）
```sh
dp train finetune_input.json
```
`finetune_input.json` 示例：
```json
{
  "model": {
    "type": "standard",
    "descriptor": { "type": "dpa3" },
    "fitting_net": { "type": "dpa3" }
  },
  "learning_rate": {
    "start_lr": 1e-5,
    ...
  },
  "training": {
    "init_model": "./dpa3_pretrained.pb",
    "numb_steps": 100000,
    ...
  }
}
```

# input_schema
## 训练数据字段
DeePMD-kit 原生 system 格式需要的字段（在 `set.*/` 目录中以 `.npy` 文件存储）：

| 文件 | 数据类型 | Shape | 必需 | 说明 |
|------|---------|-------|------|------|
| `type.raw` | int32 | `[natoms]` | 是 | 原子类型编号（从 0 开始） |
| `type_map.raw` | str 文本 | `[nelements]` | 推荐 | 元素符号列表，每行一个 |
| `set.*/box.npy` | float64 | `[nframes, 9]` | 是 | 晶胞矩阵（9 分量，行优先） |
| `set.*/coord.npy` | float64 | `[nframes, natoms*3]` | 是 | 分数坐标 |
| `set.*/energy.npy` | float64 | `[nframes]` | 是 | 体系总能量 |
| `set.*/force.npy` | float64 | `[nframes, natoms*3]` | 是 | 每个原子的受力 |
| `set.*/virial.npy` | float64 | `[nframes, 9]` | 否 | virial 张量（应力训练需要） |
| `set.*/atomic_energy.npy` | float64 | `[nframes, natoms]` | 否 | 逐原子能量（高级用法） |

## input.json 配置结构

完整配置结构按功能块分为四大部分：

### model（模型定义）
```json
{
  "model": {
    "type": "standard",             // 模型类型：standard / multi / dplr / spin
    "descriptor": {                 // 环境描述子
      "type": "se_e2_a",           // descriptor 类型
      "sel": [46, 92],             // 每种元素最大邻居数
      "rcut": 6.0,                 // cutoff 半径（Å）
      "rcut_smth": 0.5,            // cutoff 平滑区间（Å）
      "neuron": [25, 50, 100],     // embedding net 层节点数
      "axis_neuron": 16,           // 轴向神经元数
      "type_one_side": false,      // 是否区分 (i,j) 和 (j,i)
      "seed": 1                    // 随机种子
    },
    "fitting_net": {               // 拟合网络
      "type": "ener",              // 拟合类型：ener / dipole / polar / dos
      "neuron": [240, 240, 240],   // 网络每层节点数
      "resnet_dt": true,           // 是否使用 ResNet
      "seed": 1,
      "atom_ener": []              // （可选）原子参考能
    },
    "compress": {                  // （可选）压缩配置
      "type": "se_e2_a",
      "min_nbor_dist": 0.7,
      "model_file": "frozen_model.pb",
      "table_config": [0.0, 4.0, 0.01]
    }
  }
}
```

### learning_rate（学习率调度）
```json
{
  "learning_rate": {
    "type": "exp",                // 衰减类型：exp / linear
    "start_lr": 0.001,           // 起始学习率
    "stop_lr": 3.51e-8,          // 终止学习率
    "decay_steps": 5000          // 衰减步数
  }
}
```

### loss（损失函数）
```json
{
  "loss": {
    "type": "ener",               // 损失类型
    "start_pref_e": 0.02,        // 能量损失起始权重
    "limit_pref_e": 1.0,         // 能量损失最终权重
    "start_pref_f": 1000,        // 力损失起始权重
    "limit_pref_f": 1.0,         // 力损失最终权重
    "start_pref_v": 0.0,         // virial 损失起始权重（0 表示不训练）
    "limit_pref_v": 0.0,         // virial 损失最终权重
    "start_pref_ae": 0.0,        // 原子能损失起始权重
    "limit_pref_ae": 0.0,        // 原子能损失最终权重
    "start_pref_pf": 0.0,        // 力精调损失起始权重
    "limit_pref_pf": 0.0         // 力精调损失最终权重
  }
}
```
- 权重随训练步数从 `start_pref_*` 线性过渡到 `limit_pref_*`。
- 典型能量/力训练：`start_pref_e: 0.02 → 1.0`，`start_pref_f: 1000 → 1.0`。
- 含应力训练：`start_pref_v: 0.0 → 0.02`。

### training（训练控制）
```json
{
  "training": {
    "training_data": {
      "systems": ["./train_data/"],   // 训练数据路径列表
      "batch_size": "auto",           // batch size："auto" 自动选择
      "auto_prob": "prob_sys_size"   // 多 system 采样策略
    },
    "validation_data": {
      "systems": ["./valid_data/"],   // 验证数据路径
      "batch_size": 1,
      "numb_btch": 1                 // 验证 batch 数
    },
    "numb_steps": 1000000,            // 总训练步数
    "seed": 10,                       // 全局随机种子
    "disp_file": "lcurve.out",        // 训练曲线输出文件
    "disp_freq": 1000,                // 日志输出频率
    "save_freq": 10000,               // checkpoint 保存频率
    "save_ckpt": "model.ckpt",        // checkpoint 文件名前缀
    "init_model": null,               // 预训练模型初始化（fine-tuning）
    "init_frz_model": null,           // 预训练冻结模型初始化
    "profiling": false,              // 启用性能分析
    "profiling_file": "timeline.json" // 性能分析输出
  }
}
```

# runtime_interfaces
DeePMD-kit 的核心运行时接口均在命令行工具 `dp` 中：

- `dp train input.json`：训练模型。从 input.json 读取配置，启动训练循环，输出 lcurve.out 和 model.ckpt.* 文件。
- `dp freeze -o output.pb [-c checkpoint_step]`：冻结模型。将训练 checkpoint 转为单一 .pb/.pth 部署文件。
- `dp compress input.json -i frozen.pb -o compressed.pb`：模型压缩。对 embedding net 做多项式插值加速推理。
- `dp test -m model.pb -s test_data/ [-d output_dir] [-n max_frames]`：精度测试。在测试集上评估 RMSE。
- `dp transfer -O old.ckpt -o new.ckpt`：模型版本迁移。
- `dp --pt` / `dp --tf`：切换 PyTorch / TensorFlow 后端。

Python API 推理接口：
```python
from deepmd.infer import DeepPot
dp = DeepPot('frozen_model.pb')
e, f, v = dp.eval(coords, cell, atype)
# e: energy, shape: (nframes,)
# f: forces, shape: (nframes, natoms*3)
# v: virial, shape: (nframes, 9)
```

# main_functions
- `dp train`：模型训练
- `dp freeze`：模型冻结
- `dp compress`：模型压缩
- `dp test`：模型精度测试

# execution_resources
- **CPU**：可用于 dpdata 数据预处理、dp test 小规模测试、模型冻结/压缩。
- **GPU/DCU**：训练和含力的推理必须使用 GPU，推荐 NVIDIA GPU（CUDA 11.x+）或 DCU（ROCm）。
- **内存**：训练时内存消耗取决于体系原子数（natoms）、rcut、sel 和 batch_size。batch_size 按 `nloc × max(sel)` 缩放。
- **显存**：descriptor 的 `sel` 和 `rcut` 是显存的主要决定因素。se_e2_a 标准配置（sel=46~92，rcut=6.0）在 10^2 原子级别体系上单卡 GPU（24GB）通常可训练 batch_size=4~8。
- **多卡**：推荐通过 Horovod 进行数据并行，线性加速比接近卡数。
- **压缩模型推理**：在 CPU 上可进行小规模 MD（ASE），生产级 MD 推荐 GPU+LAMMPS。

# operation_limits
- 不可直接进行第一性原理计算（需 VASP/CP2K 等制备训练数据）。
- se_e2_r、se_e2_a 需要大量 DFT 标记数据才能保证精度。小数据场景优先考虑 fine-tuning DPA-3。
- model deviation 需要至少 4 个独立训练的模型，增加了训练代价。
- 模型跨后端迁移（TF→PyTorch）需要重新 freeze，checkpoint 文件不互通。
- LAMMPS 部署时，type_map 顺序必须与训练数据完全一致。
- DPLR 长程模型需要训练数据包含电荷信息或通过额外流程分配电荷。
