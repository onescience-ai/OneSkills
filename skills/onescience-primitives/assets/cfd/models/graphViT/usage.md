# launch

graphViT 通常通过 EagleMeshTransformer 示例脚本运行，配置文件为 `conf/graphvit_eagle.yaml`。

单卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
python train_graphvit.py
```

多卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
torchrun --standalone --nnodes=1 --nproc_per_node=4 train_graphvit.py
```

评估与动画生成示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
python eval_graphvit.py
```

Python API 最小调用示例：

```python
from onescience.models.graphvit import GraphViT

model = GraphViT(
    state_size=4,
    w_size=512,
    n_attention=4,
    nb_gn=4,
    n_heads=4,
)

velocity_hat, output_hat, target = model(
    mesh_pos,
    edges,
    state,
    node_type,
    clusters,
    clusters_mask,
    apply_noise=False,
)
```

# input_schema

原始数据准备遵循 EagleDatapipe 约定：

```text
Eagle_dataset/
  Cre/
  Spl/
  Tri/
    <case_path>/
      sim.npz
      triangles.npy
      constrained_kmeans_40.npy

splits/
  train.txt
  valid.txt
  test.txt
```

示例配置默认参数：

- `datapipe.source.data_dir="${ONESCIENCE_DATASETS_DIR}/Eagle/Eagle_dataset"`
- `datapipe.source.cluster_dir="${ONESCIENCE_DATASETS_DIR}/Eagle/Eagle_dataset"`
- `datapipe.source.splits_dir="./splits/"`
- `datapipe.data.window_length_train=6`
- `datapipe.data.window_length_val=25`
- `datapipe.data.window_length_test=25`
- `datapipe.data.n_cluster=40`
- `datapipe.data.normalized=True`
- `datapipe.data.type_as_onehot=True`
- `datapipe.data.with_cells=True`
- `datapipe.dataloader.batch_size=2`
- `datapipe.dataloader.num_workers=4`
- `model.name="GraphViT"`
- `model.w_size=512`
- `model.state_size=4`
- `training.max_epoch=1000`
- `training.lr=1e-4`
- `training.loss_alpha=0.1`
- `training.patience=100`
- `training.checkpoint_dir="./checkpoints/eagle_graphvit/"`
- `training.gpuid=0`
- `training.max_anim_on_infer=5`

运行时 batch 字段映射：

```text
mesh_pos <- x["mesh_pos"]
edges <- x["edges"].long()
velocity <- x["velocity"]
pressure <- x["pressure"]
state <- concat(velocity, pressure, dim=-1)
node_type <- x["node_type"]
mask <- x["mask"]
clusters <- x["cluster"].long()
clusters_mask <- x["cluster_mask"].long()
cells <- x["cells"]，仅评估可视化使用
```

# runtime_interfaces

- `GraphViT.forward(mesh_pos, edges, state, node_type, clusters, clusters_mask, apply_noise=False)`：自回归滚动预测主接口，返回完整预测状态、预测增量和目标增量。
- `positional_encoder(...)`：生成节点与簇的傅里叶位置编码。
- `encoder(...)`：把节点状态、节点类型和边几何编码为节点/边隐特征。
- `graph_pooling(...)`：按 cluster 聚合节点特征得到簇级表示。
- `attention`：簇级 Pre-LN Transformer block 列表，用于全局依赖建模。
- `graph_retrieve(...)`：把簇级表示融合回节点并输出状态增量。

# main_functions

- `forward`

# execution_resources

- 设备：支持 CPU/GPU，训练建议使用 GPU；示例脚本通过 `DistributedManager` 选择设备。
- 数据资源：Eagle 数据量较大，需准备 `sim.npz`、`triangles.npy`、split 文件和预计算 cluster 文件。
- 内存/显存：主要受 `Batch`、`Time`、`NumNodes`、`NumEdges`、`NumClusters`、`MaxClusterSize`、`w_size` 和 Transformer block 数影响。
- 分布式：训练脚本支持 DDP，可用 `mpirun`、`torchrun` 或 Slurm 脚本启动。
- checkpoint：默认保存到 `./checkpoints/eagle_graphvit/best_model.pth`。
- 评估输出：默认从 checkpoint 加载最佳模型，并在 `animation_results/` 保存对比动画。

# operation_limits

- `node_type` 必须是 9 维 one-hot，否则源码中节点类型常量索引不可用。
- `state_size` 必须等于 `velocity` 与 `pressure` 拼接后的最后一维；Eagle 示例为 4。
- 需要预计算 cluster 文件；`n_cluster` 必须与文件名和 datapipe 支持范围一致。
- 输入窗口至少包含 2 个时间步，因为模型从 `t=1` 开始预测。
- 长时间滚动存在误差累积，训练窗口 `6` 与评估窗口 `25` 的差异需要通过验证指标监控。
- 若坐标维度不是 3，需要检查 Fourier position embedding、edge geometry 和 GraphViTEncoder 的边输入维度。
- 常见失败模式包括：cluster 索引越界、空 batch、mask 维度不匹配、attention mask 维度不匹配、checkpoint 缺失或 DDP/non-DDP state_dict key 不兼容。
