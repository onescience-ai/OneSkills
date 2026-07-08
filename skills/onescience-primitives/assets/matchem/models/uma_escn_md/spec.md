# architecture_overview
`uma_escn_md` 对应 `eSCNMDBackbone`，是 UMA 原子势模型的共享主干组件，而不是完整的多头输出包装器。组件定位是把 `AtomicData` 风格的原子体系转换为可被 UMA head 消费的等变节点嵌入：它保留原子几何、元素种类、体系 charge/spin/dataset 条件信息和局部邻域方向信息，并通过多层等变消息传递形成节点级球谐表示。

组件基础信息概括：该组件是 UMA HydraModel 中的 backbone 原语，注册名为 `escnmd_backbone`，面向材料、分子、晶体、表面和吸附体系的通用 MLIP 表征学习；关键特征包括 on-the-fly 邻域构图、SO(3)/SO(2) 旋转基、charge/spin/dataset 条件嵌入、eSCNMD 等变 block、可选 graph parallel 分区以及面向能量、力、应力 head 的统一 embedding 输出。

整体路径：

``` text
AtomicData / data_dict
  pos, atomic_numbers, batch, natoms, cell, pbc, charge, spin, dataset
  -> charge / spin / dataset 条件嵌入
  -> 可选应力 displacement 注入
  -> OTF graph 或输入 edge_index/cell_offsets
  -> 距离、方向与 Wigner 旋转
  -> 原子球面嵌入 + 边度嵌入
  -> 多层 eSCNMD_Block 等变消息传递
  -> 等变归一化
  -> node_embedding / displacement / orig_cell / batch
  -> UMA heads 预测 energy / forces / stress
```

# parameter_scale
源码不固定单一参数量，参数规模由构造参数共同决定，可通过 `num_params` 属性统计当前实例参数总数。

主要规模控制项：

- `sphere_channels=128`：每个球谐系数的通道数，是主干宽度的核心控制项。
- `lmax=2`：节点球谐最高阶，决定 `sph_feature_size=(lmax+1)^2`，默认 `9`。
- `mmax=2`：边旋转与降阶映射使用的 m 上限，默认与 `lmax` 对齐。
- `edge_channels=128`：源/目标元素边嵌入通道数。
- `num_distance_basis=512`：Gaussian 距离展开维度。
- `num_layers=2`：`eSCNMD_Block` 层数。
- `hidden_channels=128`：block 内部隐藏通道。
- `max_num_elements=100`：元素嵌入表规模。
- `dataset_list`：dataset embedding 表规模由数据集列表长度决定，不能为空。

默认配置下，主干属于轻量到中等规模的 UMA backbone；实际显存和时间更多受原子数、边数、cutoff、max_neighbors、batch size、是否计算梯度力/应力以及是否启用 activation checkpointing 影响。

# architecture_structure
主干结构按条件嵌入、图构造、几何旋转、等变消息传递和输出组织五段组成：

``` text
条件体系嵌入
  charge: (NumGraphs,)
    -> ChgSpinEmbedding(type="pos_emb", channel=128)
  spin: (NumGraphs,)
    -> ChgSpinEmbedding(type="pos_emb", channel=128)
  dataset: list[str] / encoded dataset
    -> DatasetEmbedding(channel=128, dataset_list=...)
  concat(charge, spin, dataset)
    -> Linear(3 * sphere_channels, sphere_channels)
    -> SiLU
    -> csd_mixed_emb: (NumGraphs, sphere_channels)

局部邻域图
  otf_graph=True
    pos, cell, natoms, batch, pbc
      -> generate_graph(cutoff=5.0, max_neighbors=300)
      -> edge_index: (2, NumEdges)
      -> edge_distance: (NumEdges,)
      -> edge_distance_vec: (NumEdges, 3)
  otf_graph=False
    edge_index, cell_offsets, nedges
      -> edge_distance_vec / edge_distance

旋转与边特征
  edge_distance_vec
    -> init_edge_rot_mat
    -> rotation_to_wigner(Jd_0..Jd_lmax)
    -> CoefficientMapping(lmax=2, mmax=2)
  edge_distance
    -> GaussianSmearing(0.0, cutoff, num_distance_basis, 2.0)
  atomic_numbers[source/target]
    -> source_embedding / target_embedding
  concat(distance_embedding, source_embedding, target_embedding)
    -> x_edge: (NumEdges, 512 + 2 * 128)

节点球面表示
  atomic_numbers
    -> sphere_embedding
    -> x_message: (TotalAtoms, (lmax+1)^2, sphere_channels)
  x_message[:, 0, :]
    + csd_mixed_emb[batch]
    -> 条件化初始节点表示
  x_message + x_edge + edge_index + Wigner
    -> EdgeDegreeEmbedding

等变主干
  repeated num_layers=2
    eSCNMD_Block(
      x_message, x_edge, edge_distance, edge_index,
      wigner_and_M_mapping, wigner_and_M_mapping_inv,
      sys_node_embedding, node_offset
    )
  -> get_normalization_layer(norm_type="rms_norm_sh")
  -> node_embedding
```

辅助关系：

- `HydraModel` 负责实例化该 backbone，并挂载 `MLP_Energy_Head`、`MLP_EFS_Head`、`MLP_Stress_Head`、`Linear_Energy_Head` 或 `Linear_Force_Head`。
- `eSCNMDMoeBackbone` 是相关辅助模型，可在多域或多任务场景下引入 MoE/MOLE 专家路由；本原语只记录基础 eSCNMD backbone。

# input_schema
`eSCNMDBackbone.forward(data_dict)` 接收 `AtomicData` 兼容字典，核心字段如下：

- `pos`: `(TotalAtoms, 3)`，原子坐标，float。
- `atomic_numbers`: `(TotalAtoms,)`，原子序数，forward 内会转为 long。
- `batch`: `(TotalAtoms,)`，每个原子所属体系编号。
- `natoms`: `(NumGraphs,)`，每个体系的原子数。
- `cell`: `(NumGraphs, 3, 3)`，晶胞矩阵；应力或 PBC 构图需要。
- `charge`: `(NumGraphs,)`，体系电荷。
- `spin`: `(NumGraphs,)`，体系自旋。
- `dataset`: dataset 标识，启用 `use_dataset_embedding=True` 时必须存在并与 `dataset_list` 对齐。
- `pbc`: `(NumGraphs, 3)`，当 `otf_graph=True` 且 `always_use_pbc=False` 时必须提供，且一个 batch 内要求全 true 或全 false。

当 `otf_graph=True`：

- 模型内部通过 `generate_graph` 构造 `edge_index`、`edge_distance`、`edge_distance_vec`。
- 关键默认参数：`cutoff=5.0`、`max_neighbors=300`、`radius_pbc_version=1`、`always_use_pbc=True`。

当 `otf_graph=False`：

- 输入必须额外包含 `edge_index`、`cell_offsets`、`nedges`。
- `cell_offsets` 与 `cell.repeat_interleave(nedges)` 用于恢复周期平移后的边向量。

构造参数默认值：

- `max_num_elements=100`
- `sphere_channels=128`
- `lmax=2`
- `mmax=2`
- `grid_resolution=None`
- `num_sphere_samples=128`，源码标注未使用。
- `otf_graph=False`
- `max_neighbors=300`
- `use_pbc=True`，已废弃。
- `use_pbc_single=True`，已废弃。
- `cutoff=5.0`
- `edge_channels=128`
- `distance_function="gaussian"`
- `num_distance_basis=512`
- `direct_forces=True`
- `regress_forces=True`
- `regress_stress=False`
- `num_layers=2`
- `hidden_channels=128`
- `norm_type="rms_norm_sh"`
- `act_type="gate"`
- `ff_type="grid"`
- `activation_checkpointing=False`
- `chg_spin_emb_type="pos_emb"`
- `cs_emb_grad=False`
- `dataset_emb_grad=False`
- `dataset_list=None`，但实际断言不能为空。
- `use_dataset_embedding=True`
- `use_cuda_graph_wigner=False`
- `radius_pbc_version=1`
- `always_use_pbc=True`
- `jd_path=None`

# output_schema
`forward` 返回 backbone embedding 字典：

- `node_embedding`: `(TotalAtoms_orPartitionAtoms, (lmax+1)^2, sphere_channels)`，默认形状约为 `(TotalAtoms, 9, 128)`；graph parallel 初始化时为当前分区节点表示。
- `displacement`: `None` 或 `(NumGraphs, 3, 3)`，当 `regress_stress=True` 且 `direct_forces=False` 时创建并参与自动微分。
- `orig_cell`: `None` 或 `(NumGraphs, 3, 3)`，应力路径中保存原始晶胞。
- `batch`: `(TotalAtoms_orPartitionAtoms,)`，节点到体系的映射。

该主干本身不直接输出 `energy`、`forces` 或 `stress`。这些物理量由 UMA head 消费 `node_embedding` 后产生：

- `MLP_Energy_Head` / `Linear_Energy_Head`: system-level energy。
- `MLP_EFS_Head`: energy、forces，并在配置允许时输出 stress。
- `MLP_Stress_Head`: stress 相关输出。
- `Linear_Force_Head`: 直接力输出。

# shape_transformations
张量与特征变化流程：

``` text
输入原子体系
  pos: (TotalAtoms, 3)
  atomic_numbers: (TotalAtoms,)
  batch: (TotalAtoms,)
  natoms: (NumGraphs,)
  charge / spin: (NumGraphs,)
  dataset: (NumGraphs) 或 dataset 名称序列

条件嵌入
  charge -> (NumGraphs, sphere_channels)
  spin -> (NumGraphs, sphere_channels)
  dataset -> (NumGraphs, sphere_channels)
  concat -> (NumGraphs, 3 * sphere_channels)
  mix_csd + SiLU -> csd_mixed_emb: (NumGraphs, sphere_channels)

图构造
  OTF graph
    pos + cell + pbc
      -> edge_index: (2, NumEdges)
      -> edge_distance_vec: (NumEdges, 3)
      -> edge_distance: (NumEdges,)
  Precomputed graph
    edge_index + cell_offsets + nedges
      -> edge_distance_vec / edge_distance

旋转映射
  edge_distance_vec
    -> edge_rot_mat: (NumEdges, 3, 3)
    -> wigner: edge-wise SO(3) rotation basis
    -> wigner_and_M_mapping / inv

节点初始化
  atomic_numbers
    -> sphere_embedding: (TotalAtoms, sphere_channels)
    -> x_message: (TotalAtoms, (lmax + 1)^2, sphere_channels)
  csd_mixed_emb[batch]
    -> x_message[:, 0, :] 加性条件化

边特征
  edge_distance
    -> GaussianSmearing: (NumEdges, num_distance_basis)
  source/target atomic_numbers
    -> (NumEdges, edge_channels) + (NumEdges, edge_channels)
  concat
    -> x_edge: (NumEdges, num_distance_basis + 2 * edge_channels)

等变编码
  x_message + x_edge + edge_index + Wigner
    -> EdgeDegreeEmbedding
    -> eSCNMD_Block x num_layers
    -> equivariant norm
    -> node_embedding: (TotalAtoms, 9, 128) 默认
```

# key_dependencies
- `generate_graph`：根据 cutoff、max_neighbors、PBC 生成 UMA 邻域图。
- `resolve_jd_path`：定位 `Jd.pt` 旋转基文件。
- `init_edge_rot_mat` / `rotation_to_wigner` / `RotMatWignerCudaGraph`：边方向旋转与 Wigner 基计算。
- `CoefficientMapping` / `SO3_Grid`：球谐系数映射与 SO(3) 网格。
- `ChgSpinEmbedding` / `DatasetEmbedding` / `EdgeDegreeEmbedding`：体系条件嵌入与边度初始化。
- `GaussianSmearing`：距离径向基展开。
- `eSCNMD_Block`：核心等变消息传递层。
- `get_normalization_layer`：最终等变归一化。
- `MOLEInterface`：为 MoLE/MoE 扩展提供系数、尺寸和统计 hook。
- UMA heads：`MLP_Energy_Head`、`MLP_EFS_Head`、`MLP_Stress_Head`、`Linear_Energy_Head`、`Linear_Force_Head`。

# common_modification_points
- 任务输出切换：energy-only 使用 `MLP_Energy_Head`，EF/EFS 使用 `MLP_EFS_Head`，仅应力或辅助应力路径可参考 `MLP_Stress_Head`。
- EFS 微调：将 `regress_stress=True`，并确保数据、head、loss、normalizer 与 stress 标签同源；若依赖梯度应力，需要关注 `direct_forces=False` 路径。
- 分子任务：显式准备 `charge`、`spin`，必要时设置足够大的真空盒，并确认 `always_use_pbc` 不会把非周期分子错误视作周期体系。
- 晶体、表面、吸附体系：优先保持 `otf_graph=True`、`cutoff=5.0`、`max_neighbors=300` 作为 UMA checkpoint 兼容 baseline，再按边数和显存调节。
- 新数据集微调：扩展或校准 `dataset_list`、`DatasetEmbedding`、`elem_refs`、`normalizer_rmsd`、head 名称和 task 配置。
- 显存优化：开启 `activation_checkpointing=True`，或降低 batch size、max_neighbors、num_layers、sphere_channels；优先不要随意改变与 checkpoint 强绑定的结构参数。
- 旋转计算优化：推理阶段可评估 `use_cuda_graph_wigner=True`，但仅在 CUDA 设备、非训练模式且环境支持时生效。
- MoE 扩展：多域路由时参考 `eSCNMDMoeBackbone` 和 `DatasetSpecificMoEWrapper`，不要在基础 backbone 中临时拼接专家逻辑。

# implementation_risks
- `dataset_list` 虽默认是 `None`，但构造时断言不能为空；配置缺失会直接失败。
- `Jd.pt` 是运行依赖，`jd_path=None` 时依赖 `resolve_jd_path` 和环境约定；路径或设备不匹配会在初始化加载阶段失败。
- `distance_function` 只支持 `"gaussian"`，其他值会抛出 `ValueError`。
- `otf_graph=False` 时必须提供 `edge_index`、`cell_offsets`、`nedges`，否则 forward 会断言失败。
- `otf_graph=True` 且 `always_use_pbc=False` 时输入必须有 `pbc`；同一 batch 内 `pbc` 必须全 true 或全 false，混合周期条件不被当前实现接受。
- 若构图后 `edge_index` 为空，模型会抛出 `ValueError`；常见原因是单原子体系或原子间距超过 cutoff。
- `always_use_pbc=True` 会强制内部使用周期图；非周期分子必须提供足够大真空盒，避免错误近邻。
- `regress_stress=True` 且 `direct_forces=False` 会修改 `pos` 和 `cell` 并启用梯度，显存和梯度图开销明显增加。
- graph parallel 分区要求每个分区有原子；过小体系或不合理并行度可能触发分区断言。
- `pass_through_head_outputs` 属于上层 `HydraModel`，会改变最终输出 dict 结构，训练与推理代码需同步。

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
