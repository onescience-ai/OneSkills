# CFD_Benchmark Args Contract

本文档用于生成或改写 `onescience.models.cfd_benchmark` 模型训练配置时统一检查 `args` 字段，避免只读单个模型文件或单个案例脚本时遗漏参数。

## 适用范围

源码锚点：
- `./onescience/src/onescience/models/cfd_benchmark/*.py`
- `./onescience/examples/cfd/CFD_Benchmark/run.py`

覆盖模型：
- `DeepONet`
- `Factformer`
- `FNO`
- `F_FNO`
- `Galerkin_Transformer`
- `GFNO`
- `GNOT`
- `GraphSAGE`
- `Graph_UNet`
- `LSM`
- `MeshGraphNet`
- `MWT`
- `ONO`
- `PointNet`
- `RegDGCNN`
- `Swin_Transformer`
- `Transformer`
- `Transolver`
- `U_FNO`
- `U_Net`
- `U_NO`

## 使用原则

- 生成任何 `cfd_benchmark` 多模型 benchmark、训练脚本或 YAML 配置前，先读取本文件，再读取目标模型卡。
- 默认直接导入目标模型模块，例如 `from onescience.models.cfd_benchmark import FNO, U_Net, LSM, Transolver`，再调用 `FNO.Model(args, device)`。
- 默认不要通过 `onescience.models.cfd_benchmark.model_factory.get_model` 获取模型，除非用户明确要求复刻 `examples/cfd/CFD_Benchmark` 原 runner。
- 模型超参数应写入 YAML，再读成支持属性访问的 `args` 对象，例如 `argparse.Namespace`、`types.SimpleNamespace` 或支持 `args.xxx` 的配置对象。
- 本文档是配置生成契约，不要求在训练脚本中加入强制运行时校验；如果字段来源已经确定，直接生成完整 YAML 即可。
- `shapelist`、`space_dim`、`fun_dim`、`out_dim` 必须来自 datapipe、数据探测或 adapter 规格，不要根据模型名猜测。
- 如果某个模型不适配当前数据协议，应在第一轮方案中标记为 `adapter-required` 或 `not-recommended`，不要静默替换成手写 toy model。

## 通用 Args

这些字段是 `CFD_Benchmark/run.py` 和大多数 `cfd_benchmark` 模型共享的基础配置。生成 YAML 时建议显式写出，避免依赖隐式默认值。

| 字段 | 推荐默认值或来源 | 说明 |
| --- | --- | --- |
| `model` | 目标模型名 | 例如 `Transolver`、`FNO`、`U_Net`、`LSM` |
| `task` | `steady` | 可选 `steady`、`dynamic_autoregressive`、`dynamic_conditional`；新稳态 CFD 代理任务默认 `steady` |
| `geotype` | 来自数据协议 | 可选 `unstructured`、`structured_1D`、`structured_2D`、`structured_3D` |
| `shapelist` | 来自数据探测 | 结构网格必填，例如 `[H, W]` 或 `[D, H, W]`；非结构点云可为 `null` |
| `space_dim` | 来自坐标维度 | 2D 坐标通常为 `2`，3D 坐标通常为 `3` |
| `fun_dim` | 来自输入特征通道数 | 模型输入函数值或节点特征维度 |
| `out_dim` | 来自目标变量通道数 | 目标场通道数 |
| `time_input` | `false` | dynamic conditional 任务才通常开启 |
| `T_in` | `10` | 动态序列输入长度；稳态任务可保留默认但不会成为核心字段 |
| `T_out` | `10` | 动态序列输出长度；稳态任务可保留默认但不会成为核心字段 |
| `n_hidden` | `64` | 通用 hidden dim |
| `n_layers` | `3` | Transformer / DeepONet / MWT 等层数 |
| `n_heads` | `4` | 注意力头数，LSM 也会读取 |
| `act` | `gelu` | 激活函数名 |
| `mlp_ratio` | `1` | attention 类模型 feed-forward 比例 |
| `dropout` | `0.0` | dropout |
| `unified_pos` | `0` | 是否使用统一位置嵌入 |
| `ref` | `8` | 统一位置嵌入的参考点数 |
| `modes` | `12` | FNO / U_FNO / U_NO / U_Net / LSM / MWT 等谱或基函数规模 |
| `slice_num` | `32` | Transolver physical state slicing 数量 |
| `psi_dim` | `8` | ONO 专用 |
| `attn_type` | `nystrom` | ONO 专用，可选 `nystrom`、`linear`、`selfAttention` |
| `mwt_k` | `3` | MWT wavelet basis 参数 |
| `branch_depth` | `5` | DeepONet branch network 层数 |
| `trunk_depth` | `6` | DeepONet trunk network 层数 |
| `emb_dims` | `128` | RegDGCNN embedding feature dim |

## 模型到 Args 映射

下表列出当前 `./onescience/src/onescience/models/cfd_benchmark` 下各模型构造时实际访问的 `args.xxx` 字段。生成某个模型的 YAML 时，至少包含对应字段，并结合“通用 Args”补齐数据字段。

| 模型 | 必要 args 字段 |
| --- | --- |
| `DeepONet` | `act`, `branch_depth`, `fun_dim`, `geotype`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `trunk_depth`, `unified_pos` |
| `Factformer` | `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `FNO` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `F_FNO` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `Galerkin_Transformer` | `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `GFNO` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `GNOT` | `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `GraphSAGE` | `act`, `fun_dim`, `n_hidden`, `n_layers`, `out_dim`, `space_dim` |
| `Graph_UNet` | `act`, `fun_dim`, `n_hidden`, `out_dim` |
| `LSM` | `act`, `fun_dim`, `geotype`, `modes`, `n_heads`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `task`, `time_input`, `unified_pos` |
| `MeshGraphNet` | `fun_dim`, `out_dim` |
| `MWT` | `act`, `fun_dim`, `geotype`, `modes`, `mwt_k`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `ONO` | `act`, `attn_type`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `psi_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `PointNet` | `act`, `fun_dim`, `n_hidden`, `out_dim`, `space_dim` |
| `RegDGCNN` | `dropout`, `emb_dims`, `fun_dim`, `n_hidden`, `out_dim`, `space_dim` |
| `Swin_Transformer` | `act`, `fun_dim`, `geotype`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `Transformer` | `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `Transolver` | `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `slice_num`, `space_dim`, `time_input`, `unified_pos` |
| `U_FNO` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos` |
| `U_Net` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `task`, `time_input`, `unified_pos` |
| `U_NO` | `act`, `fun_dim`, `geotype`, `modes`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `task`, `time_input`, `unified_pos` |

## YAML 生成建议

### 结构网格稳态场

适用于规则网格、结构网格或可以整理为 `(x, fx)` operator view 的稳态 CFD 数据。

```yaml
model: FNO
task: steady
geotype: structured_2D
shapelist: [H, W]
space_dim: 2
fun_dim: INPUT_CHANNELS
out_dim: TARGET_CHANNELS
time_input: false
unified_pos: 0
ref: 8
n_hidden: 64
n_layers: 3
n_heads: 4
act: gelu
mlp_ratio: 1
dropout: 0.0
modes: 12
slice_num: 32
psi_dim: 8
attn_type: nystrom
mwt_k: 3
branch_depth: 5
trunk_depth: 6
emb_dims: 128
```

说明：
- `H`、`W`、`INPUT_CHANNELS`、`TARGET_CHANNELS` 必须由 datapipe 探测或 adapter 规格替换为真实值。
- 如果同一套 YAML 模板用于多个模型，可以保留其它模型不读取的字段；这比按模型删字段更不容易漏配。

### 非结构点云或表面采样

适用于翼型表面点云、VTK surface mesh point data、非结构节点场等数据。

```yaml
model: Transolver
task: steady
geotype: unstructured
shapelist: null
space_dim: 2
fun_dim: INPUT_CHANNELS
out_dim: TARGET_CHANNELS
time_input: false
unified_pos: 0
ref: 8
n_hidden: 64
n_layers: 3
n_heads: 4
act: gelu
mlp_ratio: 1
dropout: 0.0
modes: 12
slice_num: 32
psi_dim: 8
attn_type: nystrom
mwt_k: 3
branch_depth: 5
trunk_depth: 6
emb_dims: 128
```

说明：
- 如果后续还要接 FNO / U_Net / LSM，必须先判断是否能构造稳定的 `(x, fx)` view 或结构化插值 view。
- 如果不能构造合理 view，不要把点云数据强行 reshape 成规则网格。

## 常见漏配风险

- 只给了 `n_hidden`、`n_layers`，但漏掉 `fun_dim`、`out_dim`、`space_dim`、`geotype`。
- 结构网格模型漏掉 `shapelist`，导致 forward 内部无法知道空间维度。
- 使用 `Transolver (CFD_Benchmark)` 时漏掉 `slice_num`。
- 使用 `ONO` 时漏掉 `psi_dim` 或 `attn_type`。
- 使用 `MWT` 时漏掉 `mwt_k`。
- 使用 `DeepONet` 时漏掉 `branch_depth` 或 `trunk_depth`。
- 使用 `RegDGCNN` 时漏掉 `emb_dims`。
- `LSM`、`U_Net`、`U_NO` 会读取 `task`，生成稳态任务配置时也应写出 `task: steady`。
- 将 `LSM` 错误导入为 `onescience.models.pdenneval.lsm` 或假设存在 `LSM2d`；当前 benchmark 路线应使用 `onescience.models.cfd_benchmark.LSM`。

## 与数据接口的对齐要求

生成训练代码前，datapipe 或 adapter 应明确给出：
- `input_channels -> fun_dim`
- `target_channels -> out_dim`
- `coordinate_dim -> space_dim`
- `geometry_type -> geotype`
- `structured_shape -> shapelist`
- `time_dependent -> task / time_input / T_in / T_out`

如果 README 没有写清字段名、shape 或 target 变量，先生成只读探测脚本获取真实 schema，再生成模型 YAML 和训练代码。
