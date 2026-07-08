# launch
该组件原语以 Python API 方式被模型层调用，最小示例用于展示直接构造 block 的参数形态：

``` python
from e3nn import o3
from onescience.modules.block.mace_block import LinearNodeEmbeddingBlock, LinearReadoutBlock

node_embedding = LinearNodeEmbeddingBlock(
    irreps_in=o3.Irreps("4x0e"),
    irreps_out=o3.Irreps("64x0e"),
)
readout = LinearReadoutBlock(
    irreps_in=o3.Irreps("64x0e"),
    heads=["Default"],
)
```

在完整训练中通常通过 MACE 配置间接启动：

``` sh
python examples/matchem/mace/train.py --model=MACE --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --r_max=6.0 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --valid_fraction=0.05 --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --energy_key=TolEnergy --forces_key=force --E0s=isolated --batch_size=2 --valid_batch_size=4 --max_num_epochs=10 --energy_weight=10 --forces_weight=1000 --device=cuda
```

# input_schema
输入准备流程：

原子结构数据
  extxyz / AtomicData
    -> 元素表编码
    -> `node_attrs: (NumAtoms, NumElements)`
    -> 邻居搜索和周期偏移
    -> `edge_index: (2, NumEdges)`
    -> `edge_attrs: (NumEdges, SphericalHarmonicsDim)`
    -> `edge_feats: (NumEdges, NumRadial)`

节点分支
  `node_attrs`
    -> `LinearNodeEmbeddingBlock`
    -> `node_feats`

交互分支
  `node_feats + edge_attrs + edge_feats + edge_index`
    -> `InteractionBlock`
    -> `EquivariantProductBasisBlock`
    -> readout

多头分支
  `head` / `node_heads`
    -> head mask
    -> 多头 readout 或 scale/shift

# runtime_interfaces
- `LinearNodeEmbeddingBlock.forward(node_attrs)`：元素 one-hot 到节点标量特征。
- `RadialEmbeddingBlock.forward(edge_lengths, node_attrs, edge_index, atomic_numbers)`：距离基、cutoff 与可选 ZBL 相关特征。
- `InteractionBlock.forward(...)`：执行一层等变边消息聚合。
- `EquivariantProductBasisBlock.forward(node_feats, sc, node_attrs)`：执行高阶 product basis 更新。
- `LinearReadoutBlock.forward(x, heads=None)`：逐原子能量线性读出。
- `NonLinearReadoutBlock.forward(x, heads=None)`：带非线性的逐原子能量读出。
- `ScaleShiftBlock.forward(x, head)`：按 head 应用 scale 与 shift。

# main_functions
- `forward`

# execution_resources
- CPU 可用于构造和小 batch 形状验证。
- 训练和含高阶 irreps 的推理建议使用 GPU/DCU。
- 显存主要受 `NumAtoms`、`NumEdges`、`num_channels`、`max_L`、`correlation` 和 interaction 层数影响。
- 需要与 MACE 数据管线、等变张量运算、scatter 聚合和材料 batch 字段配套使用。

# operation_limits
- 不负责从坐标构建近邻图，也不负责计算 loss。
- 输入 irreps 与构造参数不匹配会在 tensor product 或 linear wrapper 阶段失败。
- `correlation` 和 `hidden_irreps` 改动通常会破坏旧 checkpoint 兼容性。
- 多头任务要求 `heads`、`head`、`node_heads` 与训练数据完全一致。
- 逐原子能量解释需要结合上层模型的能量聚合逻辑，不应只看单个 readout block 输出。
