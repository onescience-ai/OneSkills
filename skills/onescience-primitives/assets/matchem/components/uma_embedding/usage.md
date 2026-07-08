# launch
Python API 示例：

``` python
from onescience.modules.embedding.uma_embedding import DatasetEmbedding

dataset_embedding = DatasetEmbedding(
    dataset_list=["omat", "mptrj"],
    embedding_size=128,
)
condition = dataset_embedding(["omat", "mptrj"])
```

完整 UMA 训练中通常通过配置启用：

``` sh
python examples/matchem/uma/train.py --config-name=uma_finetune --model.backbone.use_dataset_embedding=true --model.backbone.dataset_list='[omat,mptrj]' --model.backbone.embedding_size=128 --model.backbone.cutoff=6.0 --model.backbone.sphere_channels=128 --trainer.max_epochs=10 --optim.batch_size=2
```

# input_schema
输入准备流程：

图几何
  atomic_numbers: (NumAtoms,)
  edge_index: (2, NumEdges)
  edge_distance: (NumEdges,)
  edge_distance_vec: (NumEdges, 3)
  batch: (NumAtoms,)
    -> EdgeDegreeEmbedding
    -> node init embedding

系统条件
  charge: (NumGraphs,)
  spin: (NumGraphs,)
    -> ChgSpinEmbedding
    -> condition vector

数据集条件
  dataset: list[str] 或 id
    -> DatasetEmbedding
    -> dataset condition

# runtime_interfaces
- `EdgeDegreeEmbedding.forward_chunk(...)`：分 chunk 计算边度嵌入。
- `EdgeDegreeEmbedding.forward(...)`：聚合边度信息为节点初始特征。
- `ChgSpinEmbedding.forward(x)`：编码 charge/spin 条件。
- `DatasetEmbedding.forward(dataset_list)`：编码 dataset 条件。

# main_functions
- `forward`
- `forward_chunk`

# execution_resources
- edge degree embedding 的成本随边数增长。
- dataset/charge/spin embedding 成本较低。
- 分 chunk 路径可降低大图边嵌入峰值显存。
- 需要与 UMA 径向层、SO3 mapping 和 backbone 通道配置一致。

# operation_limits
- `dataset_list` 漏项会导致 dataset 无法映射。
- charge/spin 语义必须与训练和推理一致。
- 改 `sphere_channels`、edge channels 或 cutoff 会影响 checkpoint 兼容。
- 非周期或缺失图字段需先在 graph compute/datapipe 层处理。
