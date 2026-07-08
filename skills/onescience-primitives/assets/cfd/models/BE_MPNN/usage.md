# launch

该模型通常通过 Python API 在 BENO 训练/推理脚本中启动，由配置文件 `conf/beno.yaml` 提供数据、模型和训练参数。

单卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
python train.py
```

多卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
torchrun --standalone --nnodes=1 --nproc_per_node=4 train.py
```

推理与结果绘图示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
python inference.py
```

Python API 最小调用示例：

```python
import torch.nn as nn
from onescience.models.beno.BE_MPNN import HeteroGNS

model = HeteroGNS(
    nnode_in_features=10,
    nnode_out_features=1,
    nedge_in_features=7,
    latent_dim=128,
    nmessage_passing_steps=10,
    nmlp_layers=2,
    mlp_hidden_dim=128,
    activation=nn.ReLU,
    boundary_dim=128,
    trans_layer=3,
)

out = model(batch)
```

# input_schema

数据准备以 BENO datapipe 为主，原始文件默认组织如下：

```text
data_dir/
  RHS_<file_prefix>_all.npy
  SOL_<file_prefix>_all.npy
  BC_<file_prefix>_all.npy
```

示例配置默认参数：

- `datapipe.source.data_dir="${ONESCIENCE_DATASETS_DIR}/BENO/data/Dirichlet/"`
- `datapipe.source.cache_dir="./cache_data/"`
- `datapipe.source.file_prefix="N32_4c"`
- `datapipe.data.ntrain=900`
- `datapipe.data.ntest=100`
- `datapipe.data.resolution=32`
- `datapipe.data.ns=10`
- `datapipe.data.domain_bounds=[[0, 1], [0, 1]]`
- `datapipe.dataloader.batch_size=1`
- `datapipe.dataloader.num_workers=0`
- `datapipe.dataloader.pin_memory=True`

模型默认参数：

- `nnode_in_features=10`（示例配置）
- `nnode_out_features=1`（示例配置）
- `nedge_in_features=7`（示例配置）
- `latent_dim=128`（源码默认）
- `nmessage_passing_steps=10`（源码默认）
- `nmlp_layers=2`（源码默认与示例配置一致）
- `mlp_hidden_dim=128`（源码默认）
- `activation=nn.ELU`（源码默认；示例配置 `act="relu"` 会映射为 `nn.ReLU`）
- `boundary_dim=128`（源码默认与示例配置一致）
- `trans_layer=3`（源码默认与示例配置一致）

模型运行时输入字段：

```text
batch["G1"].x
batch["G1"].edge_index
batch["G1"].edge_features
batch["G1"].boundary
batch["G2"].x
batch["G2"].edge_index
batch["G2"].edge_features
batch["G2"].boundary
batch["G1+2"].y
```

其中 `batch["G1+2"].y` 不进入模型 forward，但用于训练损失和评估。

# runtime_interfaces

- `HeteroGNS.forward(data)`：接收 BENO 异构图 batch，返回节点级解场预测。
- `Encoder.forward(x, edge_features, x_inbd, edge_inbd_features)`：将 G1/G2 节点和边特征投影到 latent 空间。
- `Processor.forward(...)`：执行 G1/G2 两个分支的多步消息传递。
- `InteractionNetwork.forward(x, edge_index, edge_features, boundary)`：执行单步边界条件感知的图消息传递。
- `Decoder.forward(x, x_inbd)`：分别解码两个分支并求和得到最终节点输出。

# main_functions

- `forward`
- `message`
- `update`

# execution_resources

- 设备：支持 CPU 与 GPU；训练建议使用 GPU。
- 显存/内存：主要由图节点数、边数、batch size、消息传递步数和边界 Transformer 层数决定。
- 数据：BENO datapipe 初始化会加载并预处理 `RHS/SOL/BC` 数组，首次构图会生成 `.pt` 缓存，`cache_dir` 需要可写。
- 分布式：示例训练脚本支持 `DistributedManager` 和 DDP，可通过 `torchrun` 或 `mpirun` 启动。
- 环境变量：示例配置依赖 `ONESCIENCE_DATASETS_DIR` 定位数据集根目录。
- 训练默认设置：`epochs=1000`、`optimizer=Adam`、`lr=1.0e-5`、`weight_decay=5.0e-4`、`scheduler=CosineAnnealingWarmRestarts`、`T_0=16`、`T_mult=2`、`save_period=1`。

# operation_limits

- 输入必须遵循 BENO datapipe 的异构图协议；普通张量不能直接传入 `HeteroGNS.forward`。
- 边界张量最后一维必须为 3，并能被边界 Transformer 解释为边界坐标和边界值序列。
- `G1` 与 `G2` 的节点数量和节点顺序应一致，因为 Decoder 直接相加两个分支的节点输出。
- 示例推理脚本按 `resolution * resolution` 重建完整网格，并默认 test batch size 适合逐样本重建；扩大 batch 时需检查索引回填逻辑。
- 当前实现更适配二维椭圆型 PDE 与 BENO 数据格式；迁移到三维、多物理量输出或时序 PDE 时，需要同步改造 datapipe、边界编码和输出头。
- 常见失败模式包括：`boundary` shape 不匹配、`edge_features` 维度与 `nedge_in_features` 不一致、缓存数据与当前配置不一致、checkpoint 参数名与 DDP 包装状态不一致、训练目标归一化与推理反归一化尺度不一致。
