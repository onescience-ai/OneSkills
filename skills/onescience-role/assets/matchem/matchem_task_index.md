# MatChem Task Index

## 使用目标

本索引用于材料化学/原子尺度建模任务的角色层拆解。它不替代执行层写代码，而是帮助角色层把用户的自然语言目标拆成可交给 `onescience-coder` 或 `onescience-runtime` 的交接物；验证、测试、排查统一进入 `onescience-runtime` 的 `diagnose` 阶段。

## 模型路线注册表

本节是材料模型路线的可扩展注册表。当前已支持 `MACE` 和 `UMA`，后续新增模型时只在这里追加一行，不要把下游逻辑写死成二选一。

| 路线 | 典型信号 | 首选下钻 | 当前成熟度 |
| --- | --- | --- |
| `MACE` | MACE-MP、MACE-MPA、MACE-OMAT、extxyz、E0s、fine-tuning、force field、ASE MD、LAMMPS、结构弛豫、缺陷/界面/固态电解质 | [mace.md](./mace.md) | `canonical_pattern` |
| `UMA` | UMA、uma-s、OC20、OMAT、OMOL、Hydra、ase_db、elem_refs、normalizer_rmsd、charge/spin、FAIRChemCalculator | [uma.md](./uma.md) | `registered` |
| `<future-model>` | 新材料模型名称、专用 checkpoint、专用数据格式或示例目录 | `<future-model>.md` | `planned` |

## 新模型接入接口

新增材料模型时，保持这组接口不变：

- role 路线卡：`onescience-role/assets/matchem/<model_route>.md`
- coder 模型卡：`onescience-coder/assets/models/<model_route>.md`
- coder 数据卡：`onescience-coder/assets/datapipes/materials_<model_route>.md`
- coder 组件契约：`onescience-coder/assets/contracts/<model_route>_material_stack.md`
- 索引登记：
  - 本文件的模型路线注册表
  - `onescience-coder/assets/models/model_index.md`
  - `onescience-coder/assets/datapipes/datapipe_index.md`
  - `onescience-coder/assets/contracts/component_index.md`

`MACE` 是当前最完整的标准样板。后续材料模型默认按 MACE 的套路写：先拆科学目标，再拆数据策略、模型策略、训练/运行入口、验证闭环和风险点。

如果用户提到尚未登记的新材料模型：

1. 先标记 `model_route=unregistered_material_model`
2. 用任务语义寻找最接近的已登记路线
3. 若它是 MLIP / 原子势函数 / 微调 / MD 类任务，默认优先参考 MACE 样板
4. 输出需要补齐的模型卡、数据卡、组件契约和源码锚点，不要假装已有专用 skill

## 通用角色链

### 只做方案或拆任务

`research-lead -> domain-scientist`

交接物：

- 科学目标：训练势函数、微调、推理、MD、弛豫、性质计算、结果排查
- 材料体系：分子、晶体、表面、吸附、界面、缺陷、液体、固态电解质
- 目标物性：能量、力、应力、弹性、GSFE、扩散、RDF、声子、吸附能、反应/迁移势垒

### 新数据接入或格式转换

`research-lead -> domain-scientist -> data-engineer`

交接物：

- 原始格式：extxyz、xyz、cif、ASE DB/LMDB、DeepMD npy/raw、轨迹文件
- 标签字段：energy/forces/stress/virial 的实际 key、单位、DFT 设置
- 数据划分：train/valid/test 或 `valid_fraction`
- 是否需要主动学习、扰动采样、MD/MC 采样或模型专用数据格式转换

### 训练/微调/推理实现

`research-lead -> domain-scientist -> data-engineer -> model-engineer`

交接物：

- 模型路线：使用已登记路线，或标记为 `unregistered_material_model`
- 训练目标：E、EF、EFS、能量-only、力主导、应力约束
- 运行入口：模型专用 demo、训练脚本、Hydra 配置或推理脚本
- 关键配置：cutoff/r_max、batch size、loss weights、参考能/归一化、checkpoint
- 硬件意图：本地验证、单卡、多卡、SLURM/DCU/GPU

### 运行、提交或排查

- 运行提交：`research-lead -> model-engineer -> platform-engineer`
- 指标/日志排查：`research-lead -> evaluation-engineer`

## 交给执行层的最小字段

向 `onescience-skill -> onescience-coder` 交接时，至少整理：

- `model_route`: 已登记路线名；未登记时使用 `unregistered_material_model`
- `task_stage`: `data_prepare` / `train` / `finetune` / `inference` / `md` / `relax` / `evaluate`
- `system_class`: molecule / crystal / slab / adsorbate / interface / defect / liquid / electrolyte
- `structure_format`: extxyz / ase_db / lmdb / deepmd / cif / trajectory
- `target_properties`: energy / forces / stress / virial / downstream property
- `data_keys`: energy_key / forces_key / stress_key / charge / spin / dataset_name / model-specific keys
- `reference_model_or_checkpoint`
- `validation_plan`: RMSE + downstream物性，不只看训练 loss
- `runtime_intent`: local / dry-run / slurm / distributed

## 角色层风险判断

- 不要把“训练 loss 下降”当作材料任务完成；必须明确下游物性或未见构型验证。
- 不要只说“用某个材料模型训练一下”；必须写清数据格式、标签 key、参考能量/归一化和 checkpoint 来源。
- 若用户目标是长时间 MD、缺陷能、界面、吸附或 OOD 体系，默认要求额外的验证集或不确定性/主动学习策略。
- 若用户提到远程、多卡、DCU、SLURM，只在交接物中标注运行意图，具体环境事实交给硬件/运行层。
