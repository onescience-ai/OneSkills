# Model Card: UMA

## 基本信息

- 模型名：`UMA` / `HydraModel` / `eSCNMDBackbone`
- 任务类型：`materials / universal MLIP / 多任务能量-力-应力预测、微调与推理`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/UMA/base.py`

## 模型定位

UMA 在 OneScience 中以 `HydraModel` 组织：共享 backbone 负责原子结构表征，多个 head 负责不同任务或属性输出。它适合处理基于 UMA checkpoint 的通用原子势推理、微调，以及 OC20/OMAT/OMOL 这类多任务材料数据。

优先用于：

- 基于 `uma-s-1p1` 或转换后 checkpoint 的 fine-tuning
- 分子、晶体、表面、吸附、催化体系的 E/F/S 预测
- 异构 batch 推理、结构弛豫、分子 MD、spin gap 或 adsorbate-on-slab 任务
- 需要 charge/spin/dataset embedding 的多任务势函数场景

## 输入定义

### 数据对象

UMA 使用 `custom_stack.core.atomic_data.AtomicData`，核心字段包括：

- `pos`: `(NumAtoms, 3)`，float32
- `atomic_numbers`: `(NumAtoms,)`
- `cell`: `(NumGraphs, 3, 3)`
- `pbc`: `(NumGraphs, 3)`
- `natoms`: `(NumGraphs,)`
- `batch`: `(NumAtoms,)`
- `charge`: `(NumGraphs,)`
- `spin`: `(NumGraphs,)`
- `fixed`: `(NumAtoms,)`
- `tags`: `(NumAtoms,)`
- `dataset`: str 或 list[str]
- `energy`: `(NumGraphs,)`，训练时可选
- `forces`: `(NumAtoms, 3)`，训练时可选
- `stress`: `(NumGraphs, 3, 3)` 或 reshape 后 `(NumGraphs, 9)`，训练时可选

如果 `otf_graph=True`，模型内部根据 cutoff/max_neighbors 构图；否则输入必须已有 `edge_index`、`cell_offsets`、`nedges`。

### 训练配置入口

OneScience UMA demo 通过 Hydra 配置传入：

- `data.dataset_name`: 如 `oc20`、`omat`、`omol`
- `data.elem_refs`: 每元素参考能量列表
- `data.normalizer_rmsd`: 归一化常数
- `train_dataset` / `val_dataset`: `ase_db` 数据目录
- `data.heads`: 如 `MLP_EFS_Head` 或 `MLP_Energy_Head`
- `data.tasks_list`: energy / forces / stress 的 loss、normalizer、metric 定义
- `runner.train_eval_unit.model.checkpoint_location`: 转换后的 UMA checkpoint

## 输出定义

`HydraModel.forward(data)` 返回各 head 的输出 dict。

常见输出：

- `energy`: `(NumGraphs,)`
- `forces`: `(NumAtoms, 3)`
- `stress`: `(NumGraphs, 9)` 或 `(NumGraphs, 3, 3)`，取决于 head 和 transform

当 `pass_through_head_outputs=True` 时，head 输出直接展开到顶层；否则按 head 名包一层。

Backbone 内部输出给 head 的 embedding 包括：

- `node_embedding`
- `displacement`
- `orig_cell`
- `batch`

## 主干结构

- `HydraModel`
  - 负责加载/冻结 backbone、挂载 heads、调度输出
- `eSCNMDBackbone`
  - charge/spin/dataset embedding
  - on-the-fly radius graph
  - Gaussian distance expansion
  - SO3/SO2 rotation and spherical node embedding
  - 多层 `eSCNMD_Block`
  - equivariant norm
- Heads
  - `MLP_Energy_Head`
  - `MLP_EFS_Head`
  - `MLP_Stress_Head`
  - `Linear_Energy_Head`
  - `Linear_Force_Head`

`eSCNMDMoeBackbone` 在 `eSCNMDBackbone` 上加入 MoE/MOLE 专家路由，适合多域或多任务场景。

## 主要依赖组件

- `uma_material_stack`
- `custom_stack.core.atomic_data.AtomicData`
- `custom_stack.storage.ase_datasets.AseDBDataset`
- `materials.uma.dataloader_builder.get_dataloader`
- `uma_transforms`

## 主要 Shape 变化

- ASE/ASE DB 样本 -> `AtomicData`
- collate 后：
  - `pos`: 全 batch 拼接 `(TotalAtoms, 3)`
  - `natoms`: `(BatchSize,)`
  - `batch`: 每个原子对应的结构 id
- OTF graph 后：
  - `edge_index`: `(2, NumEdges)`
  - `edge_distance`: `(NumEdges,)`
  - `edge_distance_vec`: `(NumEdges, 3)`
- backbone 后：
  - `node_embedding`: `(TotalAtoms, SphericalCoefficients, SphereChannels)`
- head 后：
  - system-level energy / stress
  - atom-level forces

## 默认关键参数

常见 demo 参数：

- `checkpoint_location="${ONESCIENCE_MODELS_DIR}/UMA/checkpoint/uma-s-1p1_converted.pt"`
- `max_neighbors=300`
- `batch_size=2`
- `lr=4.0e-4`
- `weight_decay=1.0e-3`
- `epochs=1` 或 `steps=<int>`
- `evaluate_every_n_steps=100`
- `checkpoint_every_n_steps=1000`
- `otf_graph=True`
- `regress_stress=False` 或按 EFS 任务打开
- `always_use_pbc=False`，按数据语义调整

Backbone 真实默认值包括：

- `sphere_channels=128`
- `lmax=2`
- `mmax=2`
- `cutoff=5.0`
- `edge_channels=128`
- `num_distance_basis=512`
- `num_layers=2`
- `hidden_channels=128`

## 常见修改点

- 从官方/旧 checkpoint 开始：先运行 `scripts/convert_model.py`，再填 `checkpoint_location`
- 新 fine-tune 数据：先运行 `scripts/create_uma_finetune_dataset.py` 或准备 ASE DB/LMDB，再填 `elem_refs`、`normalizer_rmsd`
- 能量-only 任务：用 `MLP_Energy_Head` 与 energy task
- EF/EFS 任务：用 `MLP_EFS_Head`，同步设置 `regress_stress`
- 分子任务：确认 `charge`、`spin`、真空盒和 `pbc`
- 异构任务：确认 dataset embedding 与 head 输出是否按 dataset/task 对齐

## 风险点

- `Jd.pt` 是 rotation basis 运行依赖；可通过 `jd_path` 或 `ONESCIENCE_UMA_JD_PATH` 指定。
- `uma-s-1p1.pt` 与 `uma-s-1p1_converted.pt` 不等价；fine-tuning 配置通常需要转换后的 checkpoint。
- `dataset_name` 必须与 transforms、heads、normalizer、foundation task 保持一致。
- `elem_refs` 和 `normalizer_rmsd` 不能随便复用别的数据集统计值。
- `always_use_pbc=True` 会强制周期图构建；非周期分子必须有足够大真空盒。
- `pbc` 当前要求一个 batch 内全 true 或全 false；混合周期条件需要先拆 batch 或适配。
- `pass_through_head_outputs` 会改变输出 dict 结构，训练和推理代码要同步。

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `../datapipes/materials_uma.md`
3. 再看 `../contracts/uma_material_stack.md`
4. 需要推理示例时看 `examples/matchem/uma/inference/*.py`
5. 需要训练配置时看 demo YAML 和 Hydra template

## 组件契约入口

- `../contracts/uma_material_stack.md`

## 数据入口

- `../datapipes/materials_uma.md`

## 源码锚点

- `./onescience/src/onescience/models/UMA/base.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/models/UMA/uma_escn_moe.py`
- `./onescience/src/onescience/modules/head/uma_head.py`
- `./onescience/src/onescience/modules/block/uma_escn_md_block.py`
- `./onescience/src/onescience/modules/embedding/uma_embedding.py`
- `./onescience/src/onescience/modules/loss/uma_loss.py`
- `./onescience/src/onescience/modules/func_utils/uma_graph/compute.py`
- `./onescience/examples/matchem/uma/demo/run.sh`
- `./onescience/examples/matchem/uma/demo/configs/*.yaml`
- `./onescience/examples/matchem/uma/inference/*.py`
