# Component Contract: UMA Parameter Policy

## 目标

本卡用于生成 UMA / HydraModel 训练、fine-tuning、验证、推理和部署参数。目标是把 UMA 参数写成“任务驱动的最小配置”，而不是复制完整 Hydra 模板。

核心效果：

- 根据 E、EF、EFS、推理、弛豫、MD、批推理、分子 charge/spin 等任务选择参数。
- 只写需要覆盖的 Hydra 节点，不展开无关 head、task、MoE 或 backbone 参数。
- 对 `elem_refs`、`normalizer_rmsd`、`dataset_name`、checkpoint、`Jd.pt`、PBC 先确认再生成。
- 新任务未覆盖时，回到源码锚点确认配置消费路径。

## 输入/输出契约

输入信息至少包括：

- 任务阶段：`checkpoint_inference`、`finetune_energy`、`finetune_ef`、`finetune_efs`、`relax_or_md`、`batch_inference`、`molecule_charge_spin`、`crystal_or_adsorbate_pbc`、`moe_advanced`。
- checkpoint：是否为转换后的 UMA checkpoint，`checkpoint_location` 是否存在。
- 数据：ASE DB/LMDB/AtomicData 路径、train/val/test 划分、`dataset_name`、目标标签 E/F/S。
- 统计量：与当前数据同源的 `elem_refs`、`normalizer_rmsd`。
- 结构语义：分子/晶体/表面/吸附体系，cell、pbc、tags、fixed、charge、spin。
- 运行方式：Hydra config、单卡/多卡、batch、步数、评估和保存频率。

输出应为：

- 最小 Hydra override 或 YAML 片段。
- 需要先运行的数据统计、checkpoint 转换或环境检查。
- 对不能确认的字段保留 TODO，不复用别的数据集数值。

## 确定性资源

当用户要求“写对 UMA 参数”“生成 Hydra override”“校验 fine-tune 配置”时，优先使用本卡对应的机器资源：

- 参数 Schema：`./uma_parameter_schema.json`
- 配置生成器：`./uma_hydra_override_builder.py`
- 通用校验器：`./material_config_validator.py`

推荐流程：

1. 先把任务整理成 JSON context，至少包含 `task_type`、`data_probe`、`checkpoint_probe`、`training` 或 `run`。
2. 用 `uma_hydra_override_builder.py --context-file <context.json> --format overrides|yaml|json` 生成最小 Hydra override。
3. 若已有配置，先转成 JSON，再用 `material_config_validator.py --model uma --task-type <task>` 校验。
4. 校验失败时修正 `dataset_name/elem_refs/normalizer_rmsd/head/tasks/checkpoint` 的同源性，不要直接复用其它数据集统计量。

## 总原则

- 不把 UMA demo 配置整份复制到新任务。
- `dataset_name`、transforms、head、tasks、normalizer、elem_refs 必须同源。
- `elem_refs` 和 `normalizer_rmsd` 必须来自当前 fine-tune 数据或明确兼容的数据统计。
- 只为当前标签写 head 和 task：E 只写 energy，EF 写 energy+forces，EFS 再加 stress。
- 只在明确需要时覆盖 backbone 参数；默认不要改 `cutoff/lmax/mmax/num_layers/sphere_channels`。
- MoE、dataset-specific wrapper、多 head 只在任务明确需要多域路由时启用。

## 先探测再写

写参数前必须确认：

- checkpoint 是否已转换为 OneScience UMA 可加载格式；fine-tuning 使用 `checkpoint_location`。
- `Jd.pt` 是否能通过 `jd_path` 或 `ONESCIENCE_UMA_JD_PATH` 找到。
- 数据格式和路径是否与 dataloader 匹配，train/val 是否分开。
- `dataset_name` 是否与 checkpoint 支持的 task/head 对齐。
- 当前任务是 E、EF 还是 EFS；是否真的有 stress 标签和正确 shape。
- `elem_refs`、`normalizer_rmsd` 是否由同一份训练数据统计得到。
- 分子任务是否有 charge/spin；OMOL 或 spin gap 推理要读取这些键。
- 晶体/表面/吸附任务是否有 cell、pbc、tags、fixed；batch 内 PBC 是否一致。
- 推理 `task_name` 是否正确，例如 `oc20`、`omat`、`omol`。

## 任务类型决策表

| 阶段 | 必写参数 | 条件参数 | 不应默认写 |
| --- | --- | --- | --- |
| checkpoint_inference | `checkpoint_location`、`task_name`、结构输入、device | `r_data_keys`、`molecule_cell_size`、`jd_path` | 训练 dataset、loss、optimizer |
| finetune_energy | checkpoint、dataset、`dataset_name`、`elem_refs`、energy head/task、energy loss/metric、batch/lr/steps | normalizer、eval/save 频率 | forces/stress task、`regress_stress` |
| finetune_ef | checkpoint、dataset、`MLP_EFS_Head`、energy+forces tasks、`regress_stress: false`、normalizer | direct forces 相关参数、scheduler | stress task、MoE |
| finetune_efs | checkpoint、dataset、`MLP_EFS_Head`、energy+forces+stress tasks、`regress_stress: true` | stress transform/reshape、stress normalizer | 无 stress 标签时启用 EFS |
| relax_or_md | calculator checkpoint、task_name、device、结构/PBC、MD 或 relax 控制参数 | charge/spin、constraints、trajectory | fine-tune loss/optimizer |
| batch_inference | checkpoint、task_name、batch 数据源、collate/loader 参数 | heterogeneous batch 处理、r_data_keys | 训练 head/task 修改 |
| molecule_charge_spin | `task_name: omol`、charge、spin、真空 cell 或非 PBC 策略 | spin multiplicity、molecule cell size | 强制晶体 PBC |
| crystal_or_adsorbate_pbc | cell、pbc、tags/fixed、task_name | `always_use_pbc`、`max_neighbors` | 缺 cell 时按晶体处理 |
| moe_advanced | MoE checkpoint、dataset routing、专家/head 配置 | load balance 或 routing loss | 普通单数据集任务启用 MoE |

## E / EF / EFS 绑定规则

- Energy-only：只写 energy head/task/loss。不要写 forces/stress 任务来“占位”。
- EF：使用能同时输出 energy/forces 的 head，例如 `MLP_EFS_Head`；`regress_stress` 保持 `false`。
- EFS：确认数据有 stress 标签、单位和 shape，再使用 `MLP_EFS_Head` 并设置 `regress_stress: true`。
- 训练任务列表必须和 head 输出 key 对齐；`pass_through_head_outputs` 或 property wrapper 改变输出结构时，同步调整 loss key。
- stress normalizer 与 force normalizer 不可随意共用，除非 demo 或源码明确这样处理。

## 必填参数策略

fine-tuning 必须写：

- `checkpoint_location`：转换后的 UMA checkpoint 路径。
- `dataset_name`：与 transforms、tasks、head、normalizer 同源。
- `train_dataset`、`val_dataset` 或等价数据配置。
- `elem_refs`：当前数据统计得到的元素参考能。
- `normalizer_rmsd`：当前数据统计得到的归一化常数。
- 当前任务的 head 与 tasks_list。
- batch、学习率、训练步数/epoch、评估和 checkpoint 频率。

推理必须写：

- checkpoint、`task_name`、device 和结构输入。
- 分子任务写 `charge/spin` 读取策略；晶体/表面任务写 PBC/cell 策略。

## 条件参数策略

- `jd_path`：新环境、非默认安装或报找不到 `Jd.pt` 时写。
- `r_data_keys=["spin","charge"]`：OMOL、spin gap 或分子 charge/spin 任务写；普通晶体任务不写。
- `molecule_cell_size`：分子非 PBC 推理需要构造真空盒时写。
- `always_use_pbc`：只有确认所有输入都按周期体系处理时写；分子任务默认不强开。
- `max_neighbors`：只有图过密、显存或截断邻居策略明确时覆盖。
- backbone 结构参数：只有从源码、checkpoint 或实验计划确认需要改时写。
- MoE：只有多域路由、专家 checkpoint 或 dataset routing 明确时写。

## 配置裁剪规则

1. 先选择任务族：E、EF、EFS、inference、relax/MD、MoE。
2. 从对应 demo 或 template 抽取最小节点，不复制无关 dataset/head/task。
3. 删除未使用的 loss、metric、head、normalizer、optimizer 子树。
4. 删除默认值覆盖项，尤其是 backbone 结构默认值。
5. 保留会影响可复现的 seed、job name、输出目录和 checkpoint 频率。
6. 对 `???`、空值、跨数据集统计量必须在生成前填实或标为 TODO。

## 最小配置骨架

EF fine-tuning 片段：

```yaml
data:
  dataset_name: <dataset>
  elem_refs: <from_current_data>
  normalizer_rmsd: <from_current_data>
  heads: <MLP_EFS_Head config>
  tasks_list: <energy_and_forces_tasks>
runner:
  train_eval_unit:
    model:
      checkpoint_location: <uma_converted.pt>
      overrides:
        backbone:
          regress_stress: false
optim:
  lr: <lr>
  weight_decay: <wd>
```

EFS 只在 stress 标签确认后增加：

```yaml
runner:
  train_eval_unit:
    model:
      overrides:
        backbone:
          regress_stress: true
data:
  tasks_list: <energy_forces_stress_tasks>
```

推理片段：

```yaml
checkpoint_location: <uma_converted.pt>
task_name: <oc20|omat|omol>
device: <cuda|cpu>
```

OMOL 或 spin/charge 任务再补 `r_data_keys`、`charge`、`spin` 或对应 ASE Atoms metadata。

## 风险检查

- `elem_refs` 元素索引错位会造成系统性能量整体偏移。
- `normalizer_rmsd` 复用其他数据集会让 loss 和 metric 失真。
- checkpoint 未转换或 import alias 不兼容时，不要先改 Hydra 任务参数。
- batch 内混合 PBC 可能导致 graph 构建失败或物理语义错误。
- `regress_stress=true` 但 head/loss/stress transform 未同步时，训练会输出 key/shape 错误。
- `task_name` 与 checkpoint task 不匹配时，推理可能走错 head 或 normalizer。
- `always_use_pbc=true` 对分子任务会引入错误邻居，除非显式构造大真空盒。

## 下钻关系

- 数据准备与统计：`../datapipes/materials_uma.md`
- Hydra/checkpoint/head 装配：`./uma_hydra_model.md`、`./uma_head.md`
- train/eval unit：`./uma_mlip_unit.md`
- loss 与任务列表：`./uma_loss.md`
- elem_refs/normalizer：`./uma_normalization.md`
- PBC 图构建：`./uma_graph_compute.md`
- `Jd.pt`：`./uma_path_utils.md`
- ASE/relax/MD/批推理：`./uma_calculator.md`
- MoE：`./uma_moe.md`

## 源码锚点

- `./uma_parameter_schema.json`
- `./uma_hydra_override_builder.py`
- `./material_config_validator.py`
- `./onescience/examples/matchem/uma/configs/data/*.yaml`
- `./onescience/examples/matchem/uma/scripts/create_uma_finetune_dataset.py`
- `./onescience/examples/matchem/uma/inference/*.py`
- `./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`
- `./onescience/src/onescience/utils/uma/units/mlip_unit/utils.py`
- `./onescience/src/onescience/models/UMA/base.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/modules/head/uma_head.py`
- `./onescience/src/onescience/datapipes/materials/uma_transforms.py`
- `./onescience/src/onescience/modules/func_utils/uma_path_utils.py`
