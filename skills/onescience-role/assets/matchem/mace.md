# MACE Role Decomposition

## 角色定位

MACE 路线适合把通用智能体转成“材料原子势函数/微调/模拟”专业角色。角色层要先确定科学问题，再决定数据、模型、运行、评估的最小交接链。

本文件也是后续材料领域模型 skill 的标准样板。新增模型时不要复制 MACE 的专有字段本身，而是复用它的结构：`何时选择 -> 科学目标 -> 数据策略 -> 模型策略 -> 训练与运行 -> 验证 -> 交接模板 -> 风险点`。

## 何时选择 MACE

优先选择 MACE，当用户目标包含：

- 基于 MACE-MP / MACE-MPA / MACE-OMAT / 自有 `.model` 的微调
- 使用 extxyz/xyz 训练能量、力、应力的机器学习势
- 用训练好的势函数做 ASE 结构弛豫、MD、GSFE、弹性、扩散、界面或缺陷性质
- 从 DeepMD 数据转换到 MACE extxyz，再做 fine-tuning
- 需要 LAMMPS 部署或 MACECalculator 推理

## 拆解顺序

### 1. 科学目标

先把目标归到一个可验证的材料问题：

- 势函数精修：提高目标体系的 E/F/S 精度
- 下游模拟：结构弛豫、有限温 MD、扩散、RDF、热稳定性
- 缺陷/界面：GSFE、空位/间隙/位错、吸附、异质界面
- 力学/热力学：弹性常数、体模量、声子、压力、密度

### 2. 数据策略

按可得性选择最小数据路径：

- 已有公开或 DFT 数据：检查是否可转为 extxyz
- DeepMD npy/raw：用 dpdata/ASE 转成 extxyz，并保留 type_map、energy、forces、virial/stress
- 晶体/缺陷小体系：从弛豫结构做随机原子扰动；若要应力，再做小应变扰动
- 液体/无定形/复杂界面：从 AIMD/MC/增强采样轨迹抽帧
- 数据很多或 OOD 风险高：用多 seed MACE ensemble、力不确定性或结构多样性筛选

### 3. 模型策略

默认优先 fine-tune 合适 foundation model，而不是从零训练。

- 数据小且目标接近 foundation 分布：fine-tune
- 目标体系 DFT 设置与 foundation 很接近：可考虑 `E0s=foundation`
- DFT 设置不同或元素参考能重要：优先提供自算 isolated atom E0s
- 数据极少或怕遗忘：考虑多头或部分冻结，但先确认 OneScience 示例是否已有入口
- 需要更高精度：优先调 loss weight、验证集和数据覆盖，再盲目放大模型

### 4. 训练与运行

交给 coder 时指向：

- 模型卡：`onescience-coder/assets/models/mace.md`
- 数据卡：`onescience-coder/assets/datapipes/materials_mace.md`
- 组件契约：`onescience-coder/assets/contracts/mace_material_stack.md`

优先复用 OneScience 示例：

- `./onescience/examples/matchem/mace/demo/run.sh`
- `./onescience/examples/matchem/mace/demo/configs/*.yaml`
- `./onescience/examples/matchem/mace/train.py`
- `./onescience/examples/matchem/mace/scripts/eval_configs.py`
- `./onescience/examples/matchem/mace/scripts/run_md.py`

### 5. 验证

验证顺序不要只停留在训练集：

1. 训练/验证 loss 是否平滑收敛
2. E/F/S RMSE 或 MAE 是否达标
3. 未见结构或 OOD 测试集是否稳定
4. 下游物性是否合理：MD 不炸、弛豫收敛、GSFE/弹性/扩散趋势合理
5. 若用于生产 MD，比较 foundation、fine-tuned、必要时 DFT/AIMD 片段

## 默认交接模板

```yaml
model_route: mace
task_stage: finetune
system_class: crystal_or_interface_or_molecule
structure_format: extxyz
target_properties: [energy, forces, stress]
data_keys:
  energy_key: REF_energy
  forces_key: REF_forces
  stress_key: REF_stress
reference_model_or_checkpoint: <MACE foundation or local .model>
data_strategy: public_dataset_or_deepmd_conversion_or_md_sampling
validation_plan: rmse_plus_downstream_property
runtime_intent: dry-run_or_slurm_or_local
```

## 可复用样板接口

后续新增材料模型时，按同一接口替换模型专有内容：

- `model_route`: 新模型短名
- `route_triggers`: 用户会如何提到该模型、checkpoint、数据格式或示例
- `data_strategy`: 该模型首选格式、转换工具、关键字段和 split 方式
- `model_strategy`: 是否优先 foundation fine-tuning、是否支持多头/冻结/adapter
- `execution_entry`: demo、train.py、Hydra、inference 或 calculator 入口
- `validation_plan`: RMSE/MAE 加至少一个材料下游验证
- `risk_points`: cutoff、参考能、归一化、单位、PBC、checkpoint 兼容等模型专有风险

MACE 当前是最重要、最完整的路线；后续模型卡优先保持与本文件同构，便于 role 层稳定路由。

## 角色层风险

- 不要建议修改 foundation model 的 `r_max` 作为第一手段；论文和教程都强调 cutoff 应与 foundation 设置保持一致。
- 不要在 E0s 不清楚时承诺能量偏置可靠；材料势函数对原子参考能非常敏感。
- 不要把 `energy`/`forces` key 写死；ASE 新版本下建议使用显式参考字段，如 `REF_energy`、`REF_forces`。
- 不要把单个材料体系的验证指标外推到复杂界面或长时间 MD。
