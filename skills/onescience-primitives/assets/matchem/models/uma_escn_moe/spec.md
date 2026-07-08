# architecture_overview
`uma_escn_moe` 对应 `eSCNMDMoeBackbone`，注册名为 `escnmd_moe_backbone`。它是 UMA eSCNMD 主干的 MoE/MOLE 扩展版：基础几何编码、邻域图、球谐表示和等变消息传递完全继承 `eSCNMDBackbone`，新增部分负责把指定 block 中的线性层或 SO2 卷积子层替换为专家层，并按体系级条件生成专家混合系数。

component_info：该组件是 UMA HydraModel 中面向多域材料势建模的专家路由 backbone 原语，定位于普通 `escnmd_backbone` 难以同时覆盖多 dataset、多组成、多电荷/自旋或多任务分布时的可扩展主干；关键特征包括 `routing_mlp` 动态路由、`MOLEGlobals` 全局专家系数与体系尺寸缓存、可选组成嵌入、按层选择的 MOLE 替换策略、训练期专家统计日志，以及将 so2 MOLE 专家合并回普通 eSCNMDBackbone 的推理部署路径。

整体设计：

``` text
AtomicData / data_dict
  -> eSCNMDBackbone 基础路径
       charge / spin / dataset embedding
       OTF graph 或预计算图
       Gaussian distance expansion
       Wigner / SO2 / SO3 rotation basis
       eSCNMD_Block 等变消息传递
  -> eSCNMDMoeBackbone 专家扩展
       convert_model_to_MOLE_model(...)
       routing_mlp(csd_mixed_emb + optional composition)
       expert_mixing_coefficients: (NumGraphs, num_experts)
       mole_sizes: (NumGraphs,)
       MOLE / MOLEDGL expert linear layer
  -> node_embedding / displacement / orig_cell / batch
  -> UMA heads 输出 energy / forces / stress
```

# parameter_scale
参数规模由基础 eSCNMDBackbone 参数和 MOLE 专家参数共同决定。基础默认规模与 `uma_escn_md` 一致，额外规模主要来自专家层、路由 MLP 和可选 composition embedding。

基础主干默认规模项：

- `sphere_channels=128`
- `lmax=2`
- `mmax=2`
- `edge_channels=128`
- `num_distance_basis=512`
- `num_layers=2`
- `hidden_channels=128`
- `max_num_elements=100`
- `dataset_list` 非空，决定 dataset embedding 表规模。

MoE/MOLE 默认规模项：

- `num_experts=8`：每个被替换线性层拥有 `num_experts` 组专家权重。
- `moe_dropout=0.0`：作用在路由 MLP 输出归一化前。
- `use_composition_embedding=False`：若开启，增加 `Embedding(max_num_elements, sphere_channels)`。
- `moe_expert_coefficient_norm="softmax"`：默认使用 softmax 后加小偏置的专家系数归一化。
- `layers_moe=None`：默认替换全部 `eSCNMD_Block`；传入层号列表可限制专家化层数。
- `moe_layer_type="pytorch"`：默认使用 Python 版 MOLE 层。
- `moe_single=False`：默认每个目标层独立专家参数；开启时相同形状层可共享替换缓存。
- `moe_type="so2"`：默认替换 SO2 相关线性子层。

路由 MLP 规模：

``` text
routing_mlp_dim = (1 + use_composition_embedding) * sphere_channels
Linear(routing_mlp_dim, num_experts * 2)
SiLU
Linear(num_experts * 2, num_experts * 2)
SiLU
Linear(num_experts * 2, num_experts)
SiLU
```

工程判断：

- `num_experts` 和 `layers_moe` 对参数量、显存和训练稳定性影响最大。
- `moe_type="all"` 会替换更多线性层，参数和风险均高于默认 `so2`。
- 若只需要普通 UMA 表征或单一数据域，优先使用 `uma_escn_md`，避免专家层带来的额外复杂度。

# architecture_structure
主模型结构由基础 eSCNMD 主干和 MOLE 专家扩展两部分组成：

``` text
基础 eSCNMD 主干
  输入
    pos: (TotalAtoms, 3)
    atomic_numbers: (TotalAtoms,)
    batch: (TotalAtoms,)
    natoms: (NumGraphs,)
    cell / pbc
    charge / spin / dataset
  -> csd_embedding
    charge embedding
    spin embedding
    dataset embedding
    mix_csd + SiLU
    csd_mixed_emb: (NumGraphs, sphere_channels)
  -> set_MOLE_coefficients(...)
  -> displacement / cell 处理
  -> _generate_graph(...)
  -> Wigner rotation
  -> atom embedding + edge degree embedding
  -> set_MOLE_sizes(...)
  -> log_MOLE_stats()
  -> eSCNMD_Block x num_layers
  -> equivariant norm
  -> node_embedding

MOLE 转换
  eSCNMDMoeBackbone.__init__
    -> super().__init__(**kwargs)
    -> parent_kwargs = kwargs
    -> num_experts > 0
       -> convert_model_to_MOLE_model(...)

convert_model_to_MOLE_model
  routing_mlp
    input: csd_mixed_emb 或 [composition, csd_mixed_emb]
    output: (NumGraphs, num_experts)
  global_mole_tensors
    expert_mixing_coefficients
    mole_sizes
    ac_start_idx
  replace target layers
    moe_type="so2"    -> SO2_Convolution.fc_m0 与 so2_m_conv.fc
    moe_type="so2m0"  -> 仅 SO2_Convolution.fc_m0
    moe_type="all"    -> 所有 Linear
    moe_type="notso2" -> 非 SO2 路径 Linear

运行时专家路由
  csd_mixed_emb: (NumGraphs, sphere_channels)
  optional composition:
    atomic_numbers_full -> composition_embedding
    index_reduce(mean by batch_full)
  routing_mlp(...)
    -> expert_mixing_coefficients_before_norm
    -> dropout
    -> softmax 或 pnorm
    -> global_mole_tensors.expert_mixing_coefficients
  edge_index + batch_full
    -> mole_sizes: 每个体系的目标边/节点片段规模
  MOLE.forward(x)
    -> 按体系取专家混合权重
    -> 对当前片段执行 F.linear
```

部署合并路径：

``` text
merge_MOLE_model(data)
  num_experts == 0
    -> return self
  data -> csd_embedding -> set_MOLE_coefficients
  mole_type 必须为 "so2"
  model_search_and_replace(recursive_replace_so2_MOLE, replace_MOLE_with_linear)
  drop routing_mlp / composition_embedding / num_experts
  new_model = eSCNMDBackbone(**parent_kwargs)
  new_model.load_state_dict(self.state_dict())
  new_model.eval()
  -> 普通 eSCNMDBackbone
```

# input_schema
`eSCNMDMoeBackbone` 继承 `eSCNMDBackbone` 的 `forward(data_dict)` 输入协议，并增加 MoE 构造参数。

forward 数据字段：

- `pos`: `(TotalAtoms, 3)`，原子坐标。
- `atomic_numbers`: `(TotalAtoms,)`，原子序数；路由和可选组成嵌入会使用。
- `batch`: `(TotalAtoms,)`，每个原子所属体系 id。
- `natoms`: `(NumGraphs,)`，每个体系原子数。
- `cell`: `(NumGraphs, 3, 3)`，晶胞。
- `charge`: `(NumGraphs,)`，体系电荷。
- `spin`: `(NumGraphs,)`，体系自旋。
- `dataset`: dataset 标识；默认启用 dataset embedding 时必须提供并与 `dataset_list` 对齐。
- `pbc`: `(NumGraphs, 3)`，当 `otf_graph=True` 且 `always_use_pbc=False` 时必须提供。

构图字段：

- `otf_graph=True`：内部根据 `cutoff`、`max_neighbors`、`pbc` 调用 `generate_graph`。
- `otf_graph=False`：输入必须额外提供 `edge_index`、`cell_offsets`、`nedges`。

MoE 构造参数默认值：

- `num_experts=8`
- `moe_dropout=0.0`
- `use_global_embedding=False`，源码标注 obsolete。
- `use_composition_embedding=False`
- `moe_expert_coefficient_norm="softmax"`，可选实现还包括 `pnorm`。
- `act=torch.nn.SiLU`
- `layers_moe=None`
- `moe_layer_type="pytorch"`
- `moe_single=False`
- `moe_type="so2"`
- `model_version=1.0`
- `**kwargs`：透传给基础 eSCNMDBackbone，包括 `sphere_channels=128`、`lmax=2`、`mmax=2`、`cutoff=5.0`、`max_neighbors=300`、`num_layers=2`、`hidden_channels=128`、`dataset_list`、`jd_path` 等。

`merge_MOLE_model(data)` 输入：

- 需要包含 `atomic_numbers`、`batch`、`charge`、`spin`、`dataset`。
- 该方法用输入样本计算一次专家混合系数，将当前 MOLE 专家合并为普通线性层；只支持 `mole_type="so2"`。

# output_schema
主干 forward 输出与基础 eSCNMDBackbone 一致：

- `node_embedding`: `(TotalAtoms_orPartitionAtoms, (lmax+1)^2, sphere_channels)`，默认约为 `(TotalAtoms, 9, 128)`。
- `displacement`: `None` 或 `(NumGraphs, 3, 3)`。
- `orig_cell`: `None` 或 `(NumGraphs, 3, 3)`。
- `batch`: `(TotalAtoms_orPartitionAtoms,)`。

MoE 内部运行态输出或缓存：

- `global_mole_tensors.expert_mixing_coefficients`: `(NumGraphs, num_experts)`，每个体系的专家混合权重。
- `global_mole_tensors.mole_sizes`: `(NumGraphs,)`，MOLE 层按体系切分输入片段所需的规模信息。
- `routing_mlp` 输出归一化前张量：`(NumGraphs, num_experts)`。

完整 UMA 模型的物理输出由 head 产生：

- energy-only：`MLP_Energy_Head` 或 `Linear_Energy_Head`。
- EF/EFS：`MLP_EFS_Head`。
- dataset-specific 多任务：`DatasetSpecificMoEWrapper` 或 `DatasetSpecificSingleHeadWrapper` 可辅助选择 head。

`merge_MOLE_model(data)` 输出：

- 当 `num_experts==0`：返回当前模型。
- 当 `num_experts>0` 且 `mole_type="so2"`：返回已合并专家权重的普通 `eSCNMDBackbone`，处于 eval 模式。

# shape_transformations
特征与路由张量变化流程：

``` text
输入原子体系
  atomic_numbers: (TotalAtoms,)
  batch: (TotalAtoms,)
  charge / spin: (NumGraphs,)
  dataset: (NumGraphs) 或 dataset 名称序列
  pos / cell / pbc / natoms

基础条件嵌入
  charge -> (NumGraphs, sphere_channels)
  spin -> (NumGraphs, sphere_channels)
  dataset -> (NumGraphs, sphere_channels)
  concat -> (NumGraphs, 3 * sphere_channels)
  mix_csd + SiLU -> csd_mixed_emb: (NumGraphs, sphere_channels)

可选组成嵌入
  use_composition_embedding=True
    atomic_numbers_full
      -> composition_embedding: (TotalAtoms, sphere_channels)
      -> index_reduce(mean, batch_full)
      -> composition: (NumGraphs, sphere_channels)
    [composition, csd_mixed_emb]
      -> concat-like flatten: (NumGraphs, 2 * sphere_channels)
  use_composition_embedding=False
    csd_mixed_emb
      -> routing input: (NumGraphs, sphere_channels)

专家路由
  routing input
    -> routing_mlp
    -> expert_mixing_coefficients_before_norm: (NumGraphs, num_experts)
    -> moe_dropout
    -> softmax 或 pnorm
    -> expert_mixing_coefficients: (NumGraphs, num_experts)

MOLE 输入尺寸
  edge_index: (2, NumEdges)
  batch_full[edge_index[1]]
    -> scatter add
    -> mole_sizes: (NumGraphs,)

MOLE 专家线性层
  expert weights: (num_experts, out_features, in_features)
  expert_mixing_coefficients: (NumGraphs, num_experts)
    -> mixed weights: (NumGraphs, out_features, in_features)
  x: (Segment, in_features) 或 chunked segment
    -> 按 mole_sizes 切片
    -> F.linear(segment, mixed_weight[system])
    -> output: (Segment, out_features)

基础 eSCNMD 输出
  eSCNMD_Block x num_layers
    -> node_embedding: (TotalAtoms_orPartitionAtoms, 9, 128) 默认
```

# key_dependencies
- `eSCNMDBackbone`：基础 UMA 等变原子结构编码主干。
- `convert_model_to_MOLE_model`：将基础模型指定层转换为 MOLE 专家层。
- `MOLEInterface`：提供 `set_MOLE_coefficients`、`set_MOLE_sizes`、`log_MOLE_stats`、`merge_MOLE_model` hook。
- `MOLE` / `MOLEDGL` / `MOLEGlobals`：专家线性层、可选 DGL 实现和全局路由缓存。
- `model_search_and_replace` 与 `recursive_replace_*`：按 `moe_type` 和 `layers_moe` 搜索并替换目标模块。
- `replace_linear_with_MOLE` / `replace_MOLE_with_linear`：普通线性层与 MOLE 层互转。
- `DatasetSpecificMoEWrapper` / `DatasetSpecificSingleHeadWrapper`：dataset-specific head 包装器。
- `DatasetEmbedding`、`ChgSpinEmbedding`、`eSCNMD_Block`、SO2/SO3 旋转组件：继承自基础 UMA 主干的核心依赖。

# common_modification_points
- 专家数量：调整 `num_experts`；多域差异大时增加专家，数据较少或训练不稳时减少专家。
- 专家化层范围：用 `layers_moe` 仅专家化部分 block，降低参数量和过拟合风险。
- 专家替换类型：默认 `moe_type="so2"`；若只想替换 m=0 路径用 `so2m0`，全线性专家化用 `all`，排除 SO2 路径用 `notso2`。
- 路由输入：开启 `use_composition_embedding=True` 可让路由感知元素组成，适合跨化学空间差异大的任务。
- 路由归一化：`moe_expert_coefficient_norm="softmax"` 稳定常用；`pnorm` 可用于更平滑的非负归一化实验。
- 专家共享：`moe_single=True` 允许相同形状层共享替换缓存，可降低参数量，但会减少层间专家自由度。
- 推理部署：如果训练后要固定某个数据上下文的专家混合，可用 `merge_MOLE_model(data)` 将 so2 MOLE 合并为普通 eSCNMDBackbone。
- 多数据集 head：可配合 `DatasetSpecificMoEWrapper` 或 `DatasetSpecificSingleHeadWrapper`，让 backbone 专家路由与 head 选择同时按 dataset 适配。

# implementation_risks
- `num_experts=0` 会退化为普通 eSCNMD 行为，所有 MOLE hook 直接返回。
- `mole_layer_type="dgl"` 依赖可用的 fairchem C++ 扩展；当前替换函数只明确接受 `"pytorch"`，其他值会抛出错误或断言失败。
- `moe_type` 只能是 `so2`、`so2m0`、`all`、`notso2`；非法值会抛出 `ValueError`。
- `merge_MOLE_model` 只支持 `mole_type="so2"`，其他类型会抛出 `ValueError`。
- `merge_MOLE_model(data)` 依赖输入样本计算专家混合系数；合并后的普通模型只代表该路由上下文，不适合无条件泛化到所有 dataset。
- `use_composition_embedding=True` 时，`model_version=1.0` 会影响 `index_reduce` 的 `include_self` 行为，版本语义需保持一致。
- MOLE 层依赖 `global_mole_tensors.expert_mixing_coefficients` 和 `mole_sizes` 已在 forward 中正确设置；绕过 backbone hook 直接调用替换层会失败。
- activation checkpointing 会分块输入，MOLE 通过 `ac_start_idx` 对齐片段；相关 hook 不一致可能导致片段长度断言失败。
- 专家路由增加参数和训练不稳定风险，尤其在数据量小、dataset 标签噪声大或 elem_refs/normalizer 不同源时。
- 继承的基础风险仍存在：`dataset_list` 不能为空、`Jd.pt` 必须可解析、PBC 不能在同一 batch 混合、无边图会失败。

# code_references
- `{onescience_path}/onescience/src/onescience/models/UMA/base.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_md.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_moe.py`
- `{onescience_path}/onescience/src/onescience/modules/head/uma_head.py`
- `{onescience_path}/onescience/src/onescience/modules/block/uma_escn_md_block.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/uma_embedding.py`
- `{onescience_path}/onescience/src/onescience/modules/loss/uma_loss.py`
- `{onescience_path}/onescience/src/onescience/modules/func_utils/uma_graph/compute.py`
- `{onescience_path}/onescience/examples/matchem/uma/demo/run.sh`
- `{onescience_path}/onescience/examples/matchem/uma/demo/configs/*.yaml`
- `{onescience_path}/onescience/examples/matchem/uma/inference/*.py`
