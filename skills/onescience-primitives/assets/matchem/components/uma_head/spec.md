# component_info
`uma_head` 是 UMA head 族组件，定位为 eSCNMD backbone 后的任务读出层集合。它通过 Hydra class path、registry 或模型 heads 配置调用，将节点球谐表示转换为能量、力、应力等 property，并可按 dataset 生成专用输出。

# purpose
- 用途：从 UMA backbone 嵌入预测 energy、forces、stress，并按 dataset 包装多任务输出。
- 解决问题：把共享 backbone 的节点特征映射到具体监督任务，支持直接力或能量导数力两种路线。
- 适用场景：UMA 多任务训练、fine-tuning、推理、数据集专用 head、MoE head。
- 不适用场景：图构建、径向边特征、backbone 消息传递、loss 聚合。

# input_schema
- `emb["node_embedding"]`: `(NumAtoms, SphFeatureSize, SphereChannels)`。
- `emb["displacement"]`: 需要 stress 导数时使用。
- `emb["orig_cell"]`: stress 分支恢复原 cell 时使用。
- `emb["batch"]`: MoE wrapper 计算每图原子数时使用。
- `data["batch"]`: `(NumAtoms,)`。
- `data["batch_full"]`: dataset wrapper 中原子级 mask 使用。
- `data["natoms"]`: `(NumGraphs,)`。
- `data["pos"]`: 需要基于能量导数求力时必须可求导。
- `data["pos_original"]`: stress 分支梯度输入。
- `data["cell"]`: stress 体积归一化需要。
- `data["dataset"]`: 多数据集 wrapper 需要。

# output_schema
- `energy`: `(NumGraphs,)` 或 `(NumGraphs, 1)`。
- `forces`: `(NumAtoms, 3)`。
- `stress`: `(NumGraphs, 9)` 或配置约定的 rank-2 张量表示。
- wrapper 输出：`{dataset_name}_{property}` 格式的 key，值可为 `{property: tensor}` 或裸 tensor，取决于 `wrap_property`。
- `MLP_EFS_Head`: 可同时输出 energy、forces、stress。
- `Linear_Force_Head`: 直接从 l=1 球谐分量输出 forces。

# parameters
- `backbone`: 提供 `sphere_channels`、`hidden_channels`、`regress_forces`、`regress_stress`、`direct_forces` 等配置。
- `prefix`: 输出 key 前缀。
- `wrap_property`: 是否将 tensor 包装成 `{property: tensor}`。
- `reduce`: energy/stress 聚合方式，常见 `"sum"` 或 `"mean"`。
- `dataset_names`: 支持的数据集名称集合。
- `head_cls`: registry 中的 head 类名。
- `head_kwargs`: head 构造参数。
- `hidden_dim` / `num_layers`: 配置层面常见 head MLP 参数。

# key_dependencies
- `uma_escn_md_block.py`
- `uma_embedding.py`
- `uma_loss.py`
- `uma_mole_block.py`
- `uma_mole_utils.py`
- `uma_irreps.py`
- `uma_so3_layers.py`
- `base.py`
- `mlip_unit.py`

# usage_and_risks
- 典型使用：在 UMA Hydra `data.heads` 或 `HydraModel` 中配置 head，训练 unit 再按 task property 读取输出。
- 直接力与能量导数力不能混用，需要与 backbone 的 `direct_forces`、`regress_forces` 对齐。
- stress 分支依赖 `pos_original`、`displacement` 和 `cell`，shape 与 loss 预期必须一致。
- dataset wrapper 要求 batch 内 `dataset` 名称被 `dataset_names` 完整覆盖。
- `wrap_property` 会改变输出 dict 结构，必须同步 loss 和 metric 读取逻辑。
- 模型并行归约路径需要单独测试 direct force 和 energy aggregation。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/head/uma_head.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/base.py`
- `{onescience_path}/onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`
