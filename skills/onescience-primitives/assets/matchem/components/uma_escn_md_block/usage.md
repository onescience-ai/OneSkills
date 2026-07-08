# launch
Python API 示例：

``` python
from onescience.modules.block.uma_escn_md_block import eSCNMD_Block

block = eSCNMD_Block(
    sphere_channels=128,
    hidden_channels=256,
    lmax=6,
    mmax=2,
    edge_channels_list=[128, 128],
    cutoff=6.0,
    norm_type="layer_norm",
    act_type="silu",
    ff_type="spectral",
    activation_checkpoint_chunk_size=None,
)
node_embedding = block(x=node_embedding, edge_index=edge_index, edge_distance=edge_distance, edge_features=edge_features)
```

完整 UMA 训练通常由 Hydra 配置构造 backbone：

``` sh
python examples/matchem/uma/train.py --config-name=uma_finetune --model.backbone.num_layers=4 --model.backbone.sphere_channels=128 --model.backbone.hidden_channels=256 --model.backbone.lmax=6 --model.backbone.mmax=2 --model.backbone.cutoff=6.0 --model.backbone.ff_type=spectral --trainer.max_epochs=10 --optim.batch_size=2
```

# input_schema
block 数据流：

节点表示
  x: (NumAtoms, SphFeatureSize, SphereChannels)
    -> norm
    -> edgewise residual update
    -> norm
    -> atomwise residual update

边分支
  edge_index: (2, NumEdges)
  edge_distance: (NumEdges,)
  edge_features: (NumEdges, EdgeChannels)
  SO3 rotation / Wigner mapping
    -> Edgewise
    -> aggregated node message

前馈分支
  ff_type = spectral
    -> SpectralAtomwise
  ff_type = grid
    -> GridAtomwise

# runtime_interfaces
- `set_mole_ac_start_index(module, index)`：为 MoE/activation checkpoint 设置起始索引。
- `Edgewise.forward(...)`：边消息计算与聚合。
- `Edgewise.forward_chunk(...)`：分 chunk 的边消息计算。
- `SpectralAtomwise.forward(x)`：频谱域 atomwise 前馈。
- `GridAtomwise.forward(x)`：网格域 atomwise 前馈。
- `eSCNMD_Block.forward(...)`：完整 block 更新。

# main_functions
- `set_mole_ac_start_index`
- `forward`
- `forward_chunk`

# execution_resources
- 显存主要受 `NumAtoms`、`NumEdges`、`sphere_channels`、`lmax`、`mmax`、`hidden_channels` 和层数影响。
- `grid` 前馈可能改变显存与速度特征。
- activation checkpoint 可降低显存但增加计算时间。
- MoE backbone 还需考虑专家路由和 chunk 索引维护。

# operation_limits
- 输入球谐 layout 必须与 `lmax/mmax` 一致。
- edge rotation、Wigner 和 mapping 对象不一致会产生错误结果。
- 改 backbone 结构参数后旧 checkpoint 通常不可直接加载。
- activation checkpoint chunk 配置不当会导致性能下降或索引错误。
