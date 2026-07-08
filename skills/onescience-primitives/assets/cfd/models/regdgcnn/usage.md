# launch

推荐 Python API 直接实例化目标模块，CLI 则可复用 CFD_Benchmark runner。

Python API 示例：

```python
from types import SimpleNamespace
from onescience.models.cfd_benchmark import RegDGCNN
import torch

args = SimpleNamespace(
    model="RegDGCNN",
    task="steady",
    geotype="structured_2D",
    shapelist=[64, 64],
    space_dim=2,
    fun_dim=3,
    out_dim=1,
    time_input=False,
    unified_pos=0,
    ref=8,
    n_hidden=64,
    n_layers=3,
    n_heads=4,
    act="gelu",
    mlp_ratio=1,
    dropout=0.0,
    modes=12,
    slice_num=32,
    psi_dim=8,
    attn_type="nystrom",
    mwt_k=3,
    branch_depth=5,
    trunk_depth=6,
    emb_dims=128,
)
device = torch.device("cuda:0")
model = RegDGCNN.Model(args, device).to(device)
x = torch.randn(2, 64 * 64, 2, device=device)
fx = torch.randn(2, 64 * 64, 3, device=device)
pred = model(x, fx)
```

CLI 示例：

```sh
python run.py --model RegDGCNN --task steady --geotype structured_2D --space_dim 2 --fun_dim 3 --out_dim 1 --n_hidden 64 --n_layers 3 --n_heads 4 --act gelu --mlp_ratio 1 --dropout 0.0 --unified_pos 0 --ref 8 --modes 12 --slice_num 32 --psi_dim 8 --attn_type nystrom --mwt_k 3 --branch_depth 5 --trunk_depth 6 --emb_dims 128 --data_path ./data/cfd --loader airfoil --batch_size 8 --epochs 500 --lr 0.001 --gpu 0
```

# input_schema

- `x`: `(Batch, NumPoints, space_dim)`，点坐标或几何特征。
- `fx`: `(Batch, NumPoints, fun_dim)`，点级输入物理特征；与 `x` 在点维度严格对齐。
- `geo`: 保留接口；`RegDGCNN` 当前不使用外部图结构，`PointNet` 也不依赖邻接。
- `args` 默认/来源：
- `dropout`: 默认/来源 `0.0`。
- `emb_dims`: 默认/来源 `128`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `n_hidden`: 默认/来源 `64`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `space_dim`: 默认/来源 `2`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

默认参数说明：
- `dropout`: 默认/来源 `0.0`。
- `emb_dims`: 默认/来源 `128`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `n_hidden`: 默认/来源 `64`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `space_dim`: 默认/来源 `2`。
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

- 支持范围：点云中局部几何邻域很重要，但没有固定图边或希望动态邻域建模的任务。
- 限制条件：期望使用外部 `geo` 图结构的任务；当前源码忽略 `geo`，由特征动态构图。
- 常见失败模式包括 `args` 字段缺失、输入点数与 `shapelist` 不一致、非结构数据缺少图/边特征、`time_input` 与 `T` 传入不一致、显存不足。
- 进行多模型对比时，应优先保持同一 datapipe schema，不要为单个模型静默改变目标变量或归一化策略。
