# launch
推荐通过 UMA demo 的 Hydra 配置启动微调或推理，让 `HydraModel` 负责装配 `escnmd_backbone` 与输出 head。示例命令使用完整关键覆盖参数，实际数据路径和数据集统计量需替换为目标任务的值：

``` sh
python examples/matchem/uma/demo/main.py runner.train_eval_unit.model.checkpoint_location="${ONESCIENCE_MODELS_DIR}/UMA/checkpoint/uma-s-1p1_converted.pt" runner.train_eval_unit.model.overrides.backbone.model=escnmd_backbone runner.train_eval_unit.model.overrides.backbone.otf_graph=true runner.train_eval_unit.model.overrides.backbone.max_neighbors=300 runner.train_eval_unit.model.overrides.backbone.cutoff=5.0 runner.train_eval_unit.model.overrides.backbone.regress_stress=false runner.train_eval_unit.model.overrides.backbone.always_use_pbc=false runner.train_eval_unit.model.overrides.backbone.jd_path="${ONESCIENCE_MODELS_DIR}/UMA/Jd.pt" data.dataset_name=omat data.train_dataset="${ONESCIENCE_DATASETS_DIR}/matchem/uma/train.aselmdb" data.val_dataset="${ONESCIENCE_DATASETS_DIR}/matchem/uma/val.aselmdb" data.elem_refs="[0.0]" data.normalizer_rmsd=1.0 data.heads.energy.model=MLP_Energy_Head optim.lr=0.0004 optim.weight_decay=0.001 trainer.batch_size=2 trainer.epochs=1 trainer.evaluate_every_n_steps=100 trainer.checkpoint_every_n_steps=1000
```

若项目 demo 提供 `run.sh`，优先使用 dry-run 检查最终命令与环境变量：

``` sh
cd examples/matchem/uma/demo
bash run.sh --config configs/finetune_uma.yaml --dry-run
bash run.sh --config configs/finetune_uma.yaml
```

Python API 直接调用主干的最小示例：

``` python
from onescience.models.UMA.uma_escn_md import eSCNMDBackbone

backbone = eSCNMDBackbone(
    otf_graph=True,
    dataset_list=["omat"],
    use_dataset_embedding=True,
    always_use_pbc=False,
    max_neighbors=300,
    cutoff=5.0,
    jd_path="${ONESCIENCE_MODELS_DIR}/UMA/Jd.pt",
)
emb = backbone(data_dict)
```

# input_schema
运行输入分为模型构造参数、`forward` 数据字段和训练/微调配置字段。

`forward` 数据准备：

- `pos`: `(TotalAtoms, 3)`，原子坐标，float32/float64。
- `atomic_numbers`: `(TotalAtoms,)`，原子序数。
- `batch`: `(TotalAtoms,)`，原子所属体系 id。
- `natoms`: `(NumGraphs,)`，每个结构原子数。
- `cell`: `(NumGraphs, 3, 3)`，晶胞；非周期分子也建议给足够大真空盒。
- `charge`: `(NumGraphs,)`，默认数据侧通常取 `0`，但 OMOL 或带电分子必须显式给出。
- `spin`: `(NumGraphs,)`，默认数据侧通常取 `0`，自由基或自旋任务必须显式给出。
- `dataset`: 与 `dataset_list` 对齐的数据集标识，例如 `omat`、`oc20`、`omol`。
- `pbc`: `(NumGraphs, 3)`，`always_use_pbc=False` 时必填；晶体/表面通常为 true，分子通常为 false。

默认构造参数与常用覆盖：

- `otf_graph=False`，微调和推理常覆盖为 `true` 以内部构图。
- `max_neighbors=300`。
- `cutoff=5.0`。
- `regress_stress=False`；EFS 任务覆盖为 `true`。
- `always_use_pbc=True`；分子或混合任务常覆盖为 `false` 并由数据提供 `pbc`。
- `sphere_channels=128`、`lmax=2`、`mmax=2`、`edge_channels=128`、`num_distance_basis=512`、`num_layers=2`、`hidden_channels=128`。
- `distance_function="gaussian"`，当前只支持该值。
- `use_dataset_embedding=True`，因此 `dataset_list` 必须配置。
- `activation_checkpointing=False`，显存紧张时可设为 `true`。
- `use_cuda_graph_wigner=False`，推理性能优化时再评估开启。
- `jd_path=None`，推荐显式传入 `Jd.pt` 路径。

训练/微调配置字段：

- `runner.train_eval_unit.model.checkpoint_location`：转换后的 UMA checkpoint，微调必填。
- `data.dataset_name`：数据集名称，需与 transforms、head、normalizer 同源。
- `data.elem_refs`：元素参考能量列表，不能跨数据集随意复用。
- `data.normalizer_rmsd`：归一化常数，需来自同一训练数据统计。
- `data.train_dataset` / `data.val_dataset`：ASE DB、LMDB 或项目 datapipe 支持的数据路径。
- `data.heads`：head 配置；energy-only 常用 `MLP_Energy_Head`，EF/EFS 常用 `MLP_EFS_Head`。
- `data.tasks_list`：energy、forces、stress 的 loss、normalizer、metric 定义。
- `optim.lr=0.0004`、`optim.weight_decay=0.001`。
- `trainer.batch_size=2`、`trainer.epochs=1` 或 `trainer.max_steps=<int>`。
- `trainer.evaluate_every_n_steps=100`、`trainer.checkpoint_every_n_steps=1000`。

# runtime_interfaces
- 构造接口：`eSCNMDBackbone(...)`，创建 UMA eSCNMD 等变主干。
- 主干推理接口：`forward(data_dict)`，返回节点嵌入、应力 displacement 信息和 batch 映射。
- 条件嵌入接口：`csd_embedding(charge, spin, dataset)`，生成体系级 charge/spin/dataset 混合表示。
- 构图接口：`_generate_graph(data_dict)`，根据 `otf_graph` 选择内部构图或使用预计算边。
- 旋转接口：`_get_rotmat_and_wigner(edge_distance_vecs, use_cuda_graph)`，生成边旋转矩阵和 Wigner 映射。
- 应力梯度接口：`_get_displacement_and_cell(data_dict)`，在应力回归路径中注入对称晶胞扰动。
- 上层装配接口：`HydraModel(backbone=..., heads=..., finetune_config=...)`，将该主干和 UMA heads 组合为完整 E/F/S 模型。
- 输出 head 接口：`MLP_Energy_Head`、`MLP_EFS_Head`、`MLP_Stress_Head`、`Linear_Energy_Head`、`Linear_Force_Head` 消费 backbone embedding 并产出物理量。

# main_functions
- `forward`
- `csd_embedding`
- `_generate_graph`
- `_get_rotmat_and_wigner`
- `_get_displacement_and_cell`
- `num_params`
- `no_weight_decay`

# execution_resources
- CPU 可用于配置检查、小体系 smoke test 和模型结构实例化；真实训练、批量推理、力/应力计算建议使用 GPU/DCU。
- 显存主要随 `TotalAtoms`、`NumEdges`、`max_neighbors`、`sphere_channels`、`num_layers`、batch size 和是否计算梯度力/应力增长。
- `regress_stress=True` 或非直接力路径会引入额外自动微分图，资源消耗明显高于 energy-only。
- `activation_checkpointing=True` 可降低显存，但会增加计算时间；默认 chunk size 为 `1024 * 128` 条边。
- `use_cuda_graph_wigner=True` 只在 CUDA 设备、非训练模式且运行环境支持时才用于 Wigner 计算优化。
- 运行环境需要 UMA 材料栈、AtomicData/ASE DB 数据读取、旋转基文件 `Jd.pt`、checkpoint 和与数据集匹配的 transforms/head/loss 配置。

# operation_limits
- 该原语只是 backbone，不直接给出 `energy`、`forces`、`stress`；必须配合 UMA head 或 HydraModel 使用。
- `dataset_list` 不能为空，且输入 `dataset` 必须能被 dataset embedding 识别。
- `distance_function` 只支持 `gaussian`。
- `otf_graph=False` 时输入必须已有 `edge_index`、`cell_offsets`、`nedges`。
- `otf_graph=True` 时若 cutoff 内无边会失败；单原子或稀疏大真空结构需要特殊处理或过滤。
- 一个 batch 内 PBC 当前要求全 true 或全 false；混合分子和晶体应拆 batch 或在 datapipe 层适配。
- 非周期分子若 `always_use_pbc=True`，必须提供足够大真空盒，否则可能产生非物理周期近邻。
- `uma-s-1p1.pt` 与 `uma-s-1p1_converted.pt` 不等价；OneScience 微调配置通常使用转换后 checkpoint。
- `elem_refs`、`normalizer_rmsd`、`dataset_name`、`heads`、`tasks_list` 必须来自同一任务上下文。
- `pass_through_head_outputs` 在上层 HydraModel 中会改变最终输出 dict 结构，下游训练和推理脚本需按同一约定解析。
