# launch

推荐 Python API 直接实例化目标模块，CLI 则可复用 CFD_Benchmark runner。

Python API 示例：

```python
from types import SimpleNamespace
from onescience.models.cfd_benchmark import MWT
import torch

args = SimpleNamespace(
    model="MWT",
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
model = MWT.Model(args, device).to(device)
x = torch.randn(2, 64 * 64, 2, device=device)
fx = torch.randn(2, 64 * 64, 3, device=device)
pred = model(x, fx)
```

CLI 示例：

```sh
python run.py --model MWT --task steady --geotype structured_2D --space_dim 2 --fun_dim 3 --out_dim 1 --n_hidden 64 --n_layers 3 --n_heads 4 --act gelu --mlp_ratio 1 --dropout 0.0 --unified_pos 0 --ref 8 --modes 12 --slice_num 32 --psi_dim 8 --attn_type nystrom --mwt_k 3 --branch_depth 5 --trunk_depth 6 --emb_dims 128 --data_path ./data/cfd --loader airfoil --batch_size 8 --epochs 500 --lr 0.001 --gpu 0
```

# input_schema

- `x`: `(Batch, NumPoints, space_dim)`，坐标、评估点或统一位置编码的输入载体。
- `fx`: `(Batch, NumPoints, fun_dim)` 或 `None`，与位置对齐的输入场特征；若模型依赖双分支或 branch 输入，应优先提供有效 `fx`。
- `T`: `(Batch,)` 或 `(Batch, 1)`，仅在 `time_input=True` 时作为时间条件使用。
- `geo`: 可选几何/图信息；大多数 `cfd_benchmark` operator 模型不直接消费该字段。
- `args` 默认/来源：
- `act`: 默认/来源 `gelu`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `modes`: 默认/来源 `12`。
- `mwt_k`: 默认/来源 `3`。
- `n_hidden`: 默认/来源 `64`。
- `n_layers`: 默认/来源 `3`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

默认参数说明：
- `act`: 默认/来源 `gelu`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `modes`: 默认/来源 `12`。
- `mwt_k`: 默认/来源 `3`。
- `n_hidden`: 默认/来源 `64`。
- `n_layers`: 默认/来源 `3`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

# runtime_interfaces

- `Model(args, device)`: 构造模型原语，`args` 必须支持属性访问。
- `forward(...)`: 主要运行时业务接口，执行场预测或节点回归。
- `model_factory.get_model(args, device)`: 辅助工厂入口，仅在复用原 CFD_Benchmark runner 或多模型统一调度时使用。

# main_functions

- `structured_geo`
- `unstructured_geo`
- `forward`

# execution_resources

- 推荐 GPU 运行；谱算子、Transformer 和大图消息传递模型对显存较敏感。
- CPU 可用于小 batch 冒烟测试，但训练通常较慢。
- 需要安装 OneScience 运行环境及源码中对应依赖；图模型还需要 `torch_geometric` 或 `dgl`。
- 可用 `CUDA_VISIBLE_DEVICES` 或 runner 的 `--gpu` 指定设备。

# operation_limits

- 支持范围：规则网格上需要多尺度频域表达、且可接受 2 的幂 padding 的算子学习任务。
- 限制条件：`shapelist` 与真实网格不一致或 padding 后边界处理敏感的任务。
- 常见失败模式包括 `args` 字段缺失、输入点数与 `shapelist` 不一致、非结构数据缺少图/边特征、`time_input` 与 `T` 传入不一致、显存不足。
- 进行多模型对比时，应优先保持同一 datapipe schema，不要为单个模型静默改变目标变量或归一化策略。
