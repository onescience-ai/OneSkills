# Component Contract: MACE Parameter Policy

## 目标

本卡用于生成 MACE 训练、fine-tuning、验证、推理和部署参数。目标不是穷举所有 CLI 参数，而是让智能体像熟悉 MACE 的使用者一样：

- 先判断任务阶段和数据契约，再写参数。
- 只写当前任务需要的参数，不为了“完整”复制 demo。
- 对 checkpoint、数据字段、单位、E0s、stress/virial 等高风险项先探测后生成。
- 遇到未覆盖的新任务，回到源码锚点确认参数消费路径。

## 输入/输出契约

输入信息至少包括：

- 任务阶段：`scratch_train`、`foundation_finetune`、`evaluate`、`ase_inference`、`relax_or_md`、`lammps_export`、`stress_or_virial_train`。
- 数据路径和格式：`train_file`、`valid_file`、`test_file`、是否为 `extxyz/.xyz`。
- 标签字段：`energy_key`、`forces_key`，可选 `stress_key`、`virials_key`、`dipole_key`。
- 目标性质：能量、力、应力、virial、MD 稳定性、结构弛豫或 LAMMPS 部署。
- checkpoint 信息：是否有 `foundation_model`，模型元素、`r_max`、`num_interactions`、product/readout 结构是否可加载。
- 运行环境：单卡/多卡、GPU/DCU、dtype、batch、时间预算。

输出应为：

- 最小可运行 YAML 或 CLI 参数列表。
- 必要的运行前检查命令或检查项。
- 对未确认字段保留明确 TODO，不臆造数值。

## 确定性资源

当用户要求“写对参数”“生成训练配置”“校验配置”时，优先使用本卡对应的机器资源：

- 参数 Schema：`./mace_parameter_schema.json`
- 配置生成器：`./mace_config_builder.py`
- 通用校验器：`./material_config_validator.py`

推荐流程：

1. 先把任务整理成 JSON context，至少包含 `task_type`、`data_probe`、`checkpoint_probe`、`training` 或 `run`。
2. 用 `mace_config_builder.py --context-file <context.json> --format yaml|json|overrides` 生成最小配置。
3. 若已有配置，先转成 JSON，再用 `material_config_validator.py --model mace --task-type <task>` 校验。
4. 校验失败时修正数据探测或 checkpoint 探测，不要直接放宽参数策略。

## 总原则

- 不直接复制 demo 参数；demo 只提供流程和字段示例。
- YAML 中布尔值为 `false`、`null`、空列表、空字符串时默认不写。
- 训练参数从“数据 + 目标 + checkpoint”推导；不是从某个旧实验全量继承。
- fine-tuning 优先继承 foundation checkpoint 的结构，不主动覆盖 `r_max`、`num_channels`、`max_L`、`correlation`、`num_interactions`。
- 只在有对应标签和任务需求时写 stress/virial/dipole/hessian/multihead 参数。
- 若参数会影响模型结构或权重迁移，必须先读 `mace_finetuning_utils.md`、`mace_block.md` 或源码。

## 先探测再写

写参数前必须确认：

- extxyz 真实字段名：能量在 `Atoms.info`，力在 `Atoms.arrays`，不要默认使用裸 `energy/forces`。
- 数据划分：优先显式 `train_file` + `valid_file`；没有验证集时再考虑 `valid_fraction`。
- 元素集合：训练/验证/测试元素必须被 `E0s` 或 foundation 支持。
- 单位和符号：能量单位、力单位、stress/virial shape 与符号必须与训练脚本预期一致。
- `E0s` 策略：`average` 便捷但不等于高精度；跨 DFT 设置或小数据优先显式原子参考能。
- foundation checkpoint：读取 `r_max`、`num_interactions`、`len(products)`、`len(interactions)`、`atomic_numbers`，确认目标元素和结构兼容。
- 多卡入口：优先复用 demo `run.sh` 或本项目推荐启动脚本，再生成 `torchrun/srun` 参数。

## 任务类型决策表

| 阶段 | 必写参数 | 条件参数 | 不应默认写 |
| --- | --- | --- | --- |
| scratch_train | `model: MACE`、`name`、`train_file`、验证来源、`E0s`、`energy_key`、`forces_key`、`r_max`、`num_interactions`、`num_channels`、`max_L`、`correlation`、loss weights、batch、epoch/lr | `stress_key/virials_key`、`default_dtype`、`ema/swa`、scheduler、DDP 参数 | `foundation_model`、foundation 迁移参数、无标签的 stress/virial |
| foundation_finetune | `foundation_model`、数据文件、字段名、`E0s`、loss weights、较小 `lr`、batch/epoch | `scaling`、`num_samples_pt`、`ema/swa`、`restart_latest`、`save_cpu`、`foundation_model_readout` | 主动覆盖 foundation 架构参数、无验证依据的 `max_L/correlation` |
| evaluate | 模型路径、`test_file`、字段名、device/dtype、batch | 输出表、误差类型、SWA/EMA 模型选择 | 训练 epoch、optimizer、loss schedule |
| ase_inference | 模型路径、device、dtype、目标输出 | `default_dtype`、committee、charges_key | 训练参数、数据划分参数 |
| relax_or_md | calculator 模型路径、device/dtype、结构文件、优化器/MD 控制参数 | 温控、步长、约束、轨迹输出 | `E0s`、loss、optimizer 训练参数 |
| lammps_export | 输入模型、输出路径、元素顺序、dtype、单位制 | legacy alias、模型格式转换参数 | 训练 batch/lr/epoch |
| stress_or_virial_train | energy/forces 字段、`stress_key` 或 `virials_key`、对应 weight | stress/virial 单位转换、SWA stress/virial weight | 同时写 stress 与 virial 但数据只含一种 |

## 必填参数策略

scratch train 必须显式写结构参数，因为没有 checkpoint 可继承：

- `num_interactions`：先按任务尺度选常规值，再结合 receptive field 检查。
- `r_max`：由材料体系邻域尺度、密度和 demo 经验决定；写入后会同时影响 radial 与构图。
- `num_channels/max_L/correlation`：按精度预算和显存预算选择；低成本基线可从小模型开始。
- `E0s`：优先显式字典或可靠 isolated/average 策略；不能覆盖所有元素时先修数据或参考能。

foundation fine-tuning 必须把 checkpoint 当作结构来源：

- 写 `foundation_model` 后，训练脚本会从 checkpoint 读取 `r_max`。
- 当前 OneScience `configure_model` 会从 foundation checkpoint 提取 `hidden_irreps/num_interactions/correlation/r_max` 等结构配置；因此省略结构参数是有意的配置裁剪。
- 若换成不提取 checkpoint 配置的自定义脚本，必须先读取 checkpoint 后再显式写匹配结构参数。
- 不要为了“和 demo 一样”再写一组不确定的结构参数。
- 若必须改结构，先确认 `load_foundations_elements` 能迁移对应 `interactions/products/readouts`，否则容易出现 product index、contraction weight 或 readout shape 错误。

## 条件参数策略

- `ema`：小数据 fine-tuning 或长训练可写；`ema_decay` 只有需要覆盖默认值时写。
- `swa`：需要 stage-two 平滑或 demo 已验证时写；`start_swa/swa_lr/swa_*_weight` 只在明确调度时写。
- `scaling=rms_forces_scaling`：fine-tuning 或力主导任务常用；scratch baseline 不必默认写。
- `num_samples_pt`：有预训练样本筛选或 fine-tuning 选择逻辑时写。
- `restart_latest/save_cpu`：只在断点续训、集群存储或 CPU 保存模型需求明确时写。
- `distributed`：只在实际由 `torchrun/srun` 多进程启动时写。
- `stress_weight/virials_weight`：只有标签存在且目标需要应力/virial 时写。

## 配置裁剪规则

1. 先生成任务最小骨架。
2. 从数据探测结果补 `energy_key/forces_key/stress_key/virials_key`。
3. 从 checkpoint 探测结果决定是否保留结构参数。
4. 删除未使用的训练阶段参数，例如 eval 配置中的 optimizer、inference 配置中的 loss。
5. 删除默认 false 的布尔项和空值项。
6. 保留会影响复现实验的 `seed/name/work_dir`。
7. 对无法确认的高风险参数写成待确认项，不填假值。

## 最小配置骨架

scratch train：

```yaml
name: <run_name>
model: MACE
train_file: <train.xyz>
valid_file: <valid.xyz>
E0s: <average|isolated|explicit_dict>
energy_key: <energy_field>
forces_key: <forces_field>
r_max: <cutoff>
num_interactions: <n>
num_channels: <channels>
max_L: <lmax>
correlation: <order>
batch_size: <n>
max_num_epochs: <n>
lr: <lr>
energy_weight: <w>
forces_weight: <w>
```

foundation fine-tuning：

```yaml
name: <run_name>
foundation_model: <checkpoint.model>
model: MACE
train_file: <train.xyz>
valid_file: <valid.xyz>
E0s: <average|foundation|explicit_dict>
energy_key: <energy_field>
forces_key: <forces_field>
batch_size: <n>
max_num_epochs: <n>
lr: <small_lr>
energy_weight: <w>
forces_weight: <w>
```

只有在数据和任务确认后，再补 `stress_key`、`stress_weight`、`virials_key`、`virials_weight`、`ema`、`swa`、`scaling` 等条件参数。

## 风险检查

- fine-tuning 报 `products[i] index out of range`、contraction weight shape 错误时，优先检查目标模型结构是否被参数覆盖，而不是先改训练数据。
- `E0s=foundation` 必须有 `foundation_model`；跨任务 head 时要确认 foundation E0 来源。
- 元素不在 checkpoint `atomic_numbers` 中时，不能直接 fine-tune；先换 checkpoint、扩元素策略或重新训练。
- stress 与 virial 不能只凭字段名判断符号；必须确认数据生成约定。
- 多卡训练的报错会在所有 rank 重复，优先看最早的 rank traceback 和模型配置。

## 下钻关系

- 数据字段、单位、extxyz：`../datapipes/materials_mace.md`
- foundation 迁移：`./mace_finetuning_utils.md`
- 结构参数影响：`./mace_block.md`、`./mace_radial.md`、`./mace_symmetric_contraction.md`
- loss 权重与 DDP 归约：`./mace_loss.md`
- 推理、ASE、LAMMPS：`./mace_calculator.md`

## 源码锚点

- `./mace_parameter_schema.json`
- `./mace_config_builder.py`
- `./material_config_validator.py`
- `./onescience/examples/matchem/mace/train.py`
- `./onescience/examples/matchem/mace/demo/_parse_config.py`
- `./onescience/examples/matchem/mace/demo/configs/*.yaml`
- `./onescience/src/onescience/utils/mace/tools/arg_parser.py`
- `./onescience/src/onescience/utils/mace/tools/arg_parser_tools.py`
- `./onescience/src/onescience/utils/mace/tools/model_script_utils.py`
- `./onescience/src/onescience/utils/mace/tools/finetuning_utils.py`
- `./onescience/src/onescience/utils/mace/tools/train.py`
