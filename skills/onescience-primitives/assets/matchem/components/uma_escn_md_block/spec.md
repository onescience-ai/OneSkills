# component_info
`uma_escn_md_block` 是 UMA block 族组件，定位为 eSCNMD backbone 的单层等变消息传递单元。它以节点球谐特征和边几何为输入，执行边消息、残差更新、归一化和 atomwise 前馈，是 UMA 主干表达能力和显存行为的核心控制点。

# purpose
- 用途：更新 UMA 节点球谐表示，完成边消息传递和原子前馈变换。
- 解决问题：在材料原子图上进行旋转相关的局部相互作用建模。
- 适用场景：UMA eSCNMD backbone、MoE backbone、fine-tuning、推理 forward。
- 不适用场景：输出 head、loss、图构建、dataset embedding。

# input_schema
- 节点球谐特征：`(NumAtoms, SphFeatureSize, SphereChannels)`。
- 边特征：`(NumEdges, EdgeChannels)` 或 edge channels list 对应特征。
- `edge_index`: `(2, NumEdges)`。
- `edge_distance`: `(NumEdges,)`。
- SO3 rotation / Wigner / mapping 对象：用于球谐特征旋转和索引。
- 可选 activation checkpoint chunk 信息。
- 约束：`lmax`、`mmax`、sphere layout 和 SO3 mapping 必须与 embedding/head/checkpoint 一致。

# output_schema
- 输出节点球谐特征，shape 与输入节点特征一致。
- `Edgewise`: 生成边消息并聚合到目标节点。
- `SpectralAtomwise` / `GridAtomwise`: 对节点表示执行 atomwise 前馈。
- `eSCNMD_Block`: 完成 norm、edgewise、residual、norm、atomwise、residual 的完整更新。

# parameters
- `sphere_channels`: 球谐通道数。
- `hidden_channels`: 隐藏通道数。
- `lmax`: 最大角动量。
- `mmax`: 最大 m 阶。
- `edge_channels_list`: 边特征通道配置。
- `cutoff`: 边距离截断。
- `norm_type`: 归一化类型。
- `act_type`: 激活类型。
- `ff_type`: `spectral` 或 `grid`。
- `activation_checkpoint_chunk_size`: checkpoint chunk 大小。

# key_dependencies
- `uma_embedding.py`
- `uma_radial.py`
- `uma_moe.py`
- `uma_mole_block.py`
- `uma_activation.py`
- `uma_layer_norm.py`
- `uma_so2_layers.py`
- `uma_so3_layers.py`
- `uma_escn_md.py`
- `uma_escn_moe.py`

# usage_and_risks
- 典型使用：由 `eSCNMDBackbone.blocks` 或 `eSCNMDMoeBackbone` 按层堆叠调用。
- 切换 `ff_type` 会改变 SO3 grid 依赖、显存、速度和数值行为。
- 改 `lmax/mmax/sphere_channels` 通常不能直接加载旧 checkpoint。
- activation checkpoint 需要正确维护 chunk 和 MoE 起始索引。
- Wigner mapping、edge index、rotation 信息不一致可能产生隐性数值错误。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/block/uma_escn_md_block.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_md.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_moe.py`
