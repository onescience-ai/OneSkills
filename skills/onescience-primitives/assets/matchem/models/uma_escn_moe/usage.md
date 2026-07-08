# launch
推荐通过 UMA Hydra 配置启动，使 `HydraModel` 装配 `escnmd_moe_backbone` 与任务 head。下面示例给出完整关键覆盖参数，数据路径、元素参考能量和归一化常数需替换为目标数据集真实值：

``` sh
python examples/matchem/uma/demo/main.py runner.train_eval_unit.model.checkpoint_location="${ONESCIENCE_MODELS_DIR}/UMA/checkpoint/uma-s-1p1_converted.pt" runner.train_eval_unit.model.overrides.backbone.model=escnmd_moe_backbone runner.train_eval_unit.model.overrides.backbone.otf_graph=true runner.train_eval_unit.model.overrides.backbone.max_neighbors=300 runner.train_eval_unit.model.overrides.backbone.cutoff=5.0 runner.train_eval_unit.model.overrides.backbone.regress_stress=false runner.train_eval_unit.model.overrides.backbone.always_use_pbc=false runner.train_eval_unit.model.overrides.backbone.jd_path="${ONESCIENCE_MODELS_DIR}/UMA/Jd.pt" runner.train_eval_unit.model.overrides.backbone.num_experts=8 runner.train_eval_unit.model.overrides.backbone.moe_dropout=0.0 runner.train_eval_unit.model.overrides.backbone.use_composition_embedding=false runner.train_eval_unit.model.overrides.backbone.moe_expert_coefficient_norm=softmax runner.train_eval_unit.model.overrides.backbone.moe_layer_type=pytorch runner.train_eval_unit.model.overrides.backbone.moe_single=false runner.train_eval_unit.model.overrides.backbone.moe_type=so2 runner.train_eval_unit.model.overrides.backbone.model_version=1.0 data.dataset_name=omat data.train_dataset="${ONESCIENCE_DATASETS_DIR}/matchem/uma/train.aselmdb" data.val_dataset="${ONESCIENCE_DATASETS_DIR}/matchem/uma/val.aselmdb" data.elem_refs="[0.0]" data.normalizer_rmsd=1.0 data.heads.energy.model=MLP_Energy_Head optim.lr=0.0004 optim.weight_decay=0.001 trainer.batch_size=2 trainer.epochs=1 trainer.evaluate_every_n_steps=100 trainer.checkpoint_every_n_steps=1000
```

若 demo 提供封装脚本，先 dry-run 再正式运行：

``` sh
cd examples/matchem/uma/demo
bash run.sh --config configs/finetune_uma_moe.yaml --dry-run
bash run.sh --config configs/finetune_uma_moe.yaml
```

Python API 最小构造示例：

``` python
from onescience.models.UMA.uma_escn_moe import eSCNMDMoeBackbone

model = eSCNMDMoeBackbone(
    num_experts=8,
    moe_dropout=0.0,
    use_composition_embedding=False,
    moe_expert_coefficient_norm="softmax",
    layers_moe=None,
    moe_layer_type="pytorch",
    moe_single=False,
    moe_type="so2",
    model_version=1.0,
    otf_graph=True,
    dataset_list=["omat"],
    always_use_pbc=False,
    max_neighbors=300,
    cutoff=5.0,
    jd_path="${ONESCIENCE_MODELS_DIR}/UMA/Jd.pt",
)
out = model(data_dict)
```

固定路由后合并为普通 backbone 的示例：

``` python
merged_model = model.merge_MOLE_model(data_dict)
merged_model.eval()
```

# input_schema
数据输入与 `uma_escn_md` 一致，并额外要求 MoE 路由上下文稳定。

forward 数据字段：

- `pos`: `(TotalAtoms, 3)`，原子坐标。
- `atomic_numbers`: `(TotalAtoms,)`，原子序数；同时用于组成嵌入。
- `batch`: `(TotalAtoms,)`，原子到体系的映射。
- `natoms`: `(NumGraphs,)`，每个体系原子数。
- `cell`: `(NumGraphs, 3, 3)`，晶胞。
- `pbc`: `(NumGraphs, 3)`，`always_use_pbc=False` 时必填。
- `charge`: `(NumGraphs,)`，默认可为 `0`，但带电分子必须显式给出。
- `spin`: `(NumGraphs,)`，默认可为 `0`，但自旋相关任务必须显式给出。
- `dataset`: dataset 标识，必须与 `dataset_list` 和路由训练上下文一致。

构图字段：

- `otf_graph=True`：模型内部构图，常用默认 `cutoff=5.0`、`max_neighbors=300`。
- `otf_graph=False`：输入必须包含 `edge_index`、`cell_offsets`、`nedges`。

MoE 默认参数：

- `num_experts=8`
- `moe_dropout=0.0`
- `use_global_embedding=False`，已过时，不建议作为新配置重点。
- `use_composition_embedding=False`
- `moe_expert_coefficient_norm="softmax"`
- `act=torch.nn.SiLU`
- `layers_moe=None`
- `moe_layer_type="pytorch"`
- `moe_single=False`
- `moe_type="so2"`
- `model_version=1.0`

基础 backbone 默认参数：

- `sphere_channels=128`
- `lmax=2`
- `mmax=2`
- `edge_channels=128`
- `num_distance_basis=512`
- `num_layers=2`
- `hidden_channels=128`
- `regress_stress=False`
- `activation_checkpointing=False`
- `use_dataset_embedding=True`
- `use_cuda_graph_wigner=False`
- `always_use_pbc=True`
- `jd_path=None`，推荐显式传入。

训练配置字段：

- `runner.train_eval_unit.model.checkpoint_location`：转换后的 UMA checkpoint。
- `data.dataset_name`：如 `oc20`、`omat`、`omol` 或自定义 dataset。
- `data.elem_refs`：每元素参考能量。
- `data.normalizer_rmsd`：归一化常数。
- `data.train_dataset` / `data.val_dataset`：ASE DB、LMDB 或 datapipe 支持的数据路径。
- `data.heads`：可使用 `MLP_Energy_Head`、`MLP_EFS_Head` 或 dataset-specific wrapper。
- `data.tasks_list`：energy、forces、stress 的 loss、normalizer、metric 配置。
- `optim.lr=0.0004`、`optim.weight_decay=0.001`。
- `trainer.batch_size=2`、`trainer.epochs=1` 或 `trainer.max_steps=<int>`。
- `trainer.evaluate_every_n_steps=100`、`trainer.checkpoint_every_n_steps=1000`。

# runtime_interfaces
- 构造接口：`eSCNMDMoeBackbone(...)`，创建带 MOLE 专家路由的 UMA eSCNMD 主干。
- 主干推理接口：`forward(data_dict)`，继承自基础主干，内部会调用 MOLE hook 并返回 backbone embedding。
- 路由系数接口：`set_MOLE_coefficients(atomic_numbers_full, batch_full, csd_mixed_emb)`，生成并缓存专家混合系数。
- 路由尺寸接口：`set_MOLE_sizes(nsystems, batch_full, edge_index)`，按体系计算 MOLE 层输入片段规模。
- 专家统计接口：`log_MOLE_stats()`，训练期每 500 次记录专家系数方差与均值。
- 合并接口：`merge_MOLE_model(data)`，将 so2 MOLE 专家合并为普通 eSCNMDBackbone。
- 上层装配接口：`HydraModel(backbone=..., heads=...)`，把该主干接入 energy/forces/stress head。
- head 辅助接口：`DatasetSpecificMoEWrapper`、`DatasetSpecificSingleHeadWrapper`，用于 dataset-specific 输出头。

# main_functions
- `forward`
- `set_MOLE_coefficients`
- `set_MOLE_sizes`
- `log_MOLE_stats`
- `merge_MOLE_model`
- `csd_embedding`
- `_generate_graph`
- `_get_rotmat_and_wigner`
- `_get_displacement_and_cell`

# execution_resources
- 真实训练和批量推理建议使用 GPU/DCU；CPU 仅适合配置检查和小体系 smoke test。
- 相比 `uma_escn_md`，显存和参数量额外受 `num_experts`、`layers_moe`、`moe_type` 和是否开启 composition embedding 影响。
- `moe_type="all"` 或较大的 `num_experts` 会显著增加专家权重与优化器状态。
- `moe_layer_type="pytorch"` 是默认稳定路径；`dgl` 路径需要额外 C++ 扩展支持。
- `regress_stress=True`、activation checkpointing、graph parallel 和 MOLE 分块会叠加复杂度，建议先做小 batch forward。
- 运行需要 UMA checkpoint、`Jd.pt`、dataset embedding 配置、材料数据读取栈和与任务同源的 normalizer/loss/head。

# operation_limits
- 该原语是 backbone，不直接输出 energy/forces/stress，必须配合 UMA head。
- `num_experts=0` 时退化为普通 eSCNMDBackbone，不再具有专家路由能力。
- `mole_type` 仅支持 `so2`、`so2m0`、`all`、`notso2`。
- `merge_MOLE_model` 只支持 `mole_type="so2"`。
- 合并模型依赖传入样本的路由系数；它适合固定上下文部署，不等价于保留动态 MoE 的通用模型。
- `dataset_list` 和输入 `dataset` 必须与训练配置一致，否则路由和 dataset embedding 都可能失效。
- `elem_refs`、`normalizer_rmsd`、head 和 task 配置必须来自同一数据上下文。
- PBC、无边图、`Jd.pt`、`otf_graph=False` 预计算图字段等基础 UMA 限制仍然适用。
- 专家模型更容易过拟合小数据集，需用验证集监控专家塌缩、跨 dataset 误差和下游 MD 稳定性。
