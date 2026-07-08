# launch

推荐 Python API 直接实例化目标模块，CLI 则可复用 CFD_Benchmark runner。

Python API 示例：

```python
from types import SimpleNamespace
from onescience.models.cfd_benchmark import MeshGraphNet
import torch

args = SimpleNamespace(fun_dim=6, out_dim=3)
device = torch.device("cuda:0")
model = MeshGraphNet.Model(args, device).to(device)

node_features = torch.randn(4096, 6, device=device)
edge_features = torch.randn(12000, 4, device=device)
graph = ...  # DGLGraph 或 CuGraphCSC，由 datapipe 构造
pred = model(node_features, edge_features, graph)
```

CLI 示例：

```sh
python run.py --model MeshGraphNet --task steady --geotype structured_2D --space_dim 2 --fun_dim 3 --out_dim 1 --n_hidden 64 --n_layers 3 --n_heads 4 --act gelu --mlp_ratio 1 --dropout 0.0 --unified_pos 0 --ref 8 --modes 12 --slice_num 32 --psi_dim 8 --attn_type nystrom --mwt_k 3 --branch_depth 5 --trunk_depth 6 --emb_dims 128 --data_path ./data/cfd --loader airfoil --batch_size 8 --epochs 500 --lr 0.001 --gpu 0
```

# input_schema

- `node_features`: `(NumNodes, fun_dim)`，节点物理/边界/几何输入特征，`fun_dim` 来自数据协议。
- `edge_features`: `(NumEdges, 4)`，源码默认边特征维度固定为 4；若 datapipe 生成的边特征维度变化，需要同步修改模型构造。
- `graph`: `DGLGraph`、`list[DGLGraph]` 或 `CuGraphCSC`，必须由 datapipe 预先构造。
- `args`: 至少包含 `fun_dim`、`out_dim`；构造函数内部还提供 `processor_size=15`、`hidden_dim_processor=128`、`aggregation="sum"` 等默认参数。

默认参数说明：
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

# runtime_interfaces

- `Model(args, device)`: 构造模型原语，`args` 必须支持属性访问。
- `forward(...)`: 主要运行时业务接口，执行场预测或节点回归。
- `model_factory.get_model(args, device)`: 辅助工厂入口，仅在复用原 CFD_Benchmark runner 或多模型统一调度时使用。

# main_functions

- `forward`

# execution_resources

- 推荐 GPU 运行；谱算子、Transformer 和大图消息传递模型对显存较敏感。
- CPU 可用于小 batch 冒烟测试，但训练通常较慢。
- 需要安装 OneScience 运行环境及源码中对应依赖；图模型还需要 `torch_geometric` 或 `dgl`。
- 可用 `CUDA_VISIBLE_DEVICES` 或 runner 的 `--gpu` 指定设备。

# operation_limits

- 支持范围：已有 DGLGraph/CuGraphCSC、显式边特征和非结构网格拓扑的节点级预测。
- 限制条件：只有 `(x, fx)` operator view 而没有 graph/edge_features 的数据；模型本身不负责构图。
- 常见失败模式包括 `args` 字段缺失、输入点数与 `shapelist` 不一致、非结构数据缺少图/边特征、`time_input` 与 `T` 传入不一致、显存不足。
- 进行多模型对比时，应优先保持同一 datapipe schema，不要为单个模型静默改变目标变量或归一化策略。
