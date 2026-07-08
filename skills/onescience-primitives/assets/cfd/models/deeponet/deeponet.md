# Model Card: deeponet

## 基本信息

- 模型名：`deeponet`
- 任务类型：`cfd / model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/cfd_benchmark/DeepONet.py`

## 模型架构概览

DeepONet 的架构定位是 `branch-trunk 算子学习`。它在 CFD_Benchmark 中作为可被 `model_factory.get_model(args, device)` 或直接模块导入使用的模型原语，主要服务于 CFD 场预测、网格/点级回归和多模型 benchmark 对比。组件基础定位可以概括为：使用 Branch Net 编码输入函数特征、Trunk Net 编码评估坐标，再通过点级特征乘积输出物理场。

## 参数规模

参数规模不在源码中写死，主要由以下 `args` 字段和构造默认值决定：`act`, `branch_depth`, `fun_dim`, `geotype`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `trunk_depth`, `unified_pos`。

- 隐藏宽度主要由 `n_hidden` 或 `hidden_dim_processor` 控制。
- 深度主要由 `n_layers`、`processor_size`、`branch_depth/trunk_depth` 或 U-shape 下采样层数控制。
- 输出规模由 `out_dim` 决定，输入规模由 `space_dim/fun_dim` 或显式图节点/边特征维度决定。
- 典型 benchmark 默认可从 `run.py` 继承：`n_hidden=64`、`n_layers=3`、`n_heads=4`、`dropout=0.0`、`modes=12`、`task='steady'`。

## 架构结构

- 主干结构：OneMlp Branch Net + OneMlp Trunk Net + 点级乘法融合 + Linear 输出头。
- 核心业务入口：`structured_forward`, `unstructured_forward`, `forward`。
- 源码类：`Model`；若存在辅助类，则包括 `Model`。
- 时间条件：若源码读取 `time_input`，则可用 `timestep_embedding` 将 `T` 注入隐藏表示。
- 位置条件：若源码读取 `unified_pos`，结构化网格可通过 `unified_pos_embedding(shapelist, ref)` 替换或增强坐标输入。

## 输入模式

- `x`: `(Batch, NumPoints, space_dim)`，坐标、评估点或统一位置编码的输入载体。
- `fx`: `(Batch, NumPoints, fun_dim)` 或 `None`，与位置对齐的输入场特征；若模型依赖双分支或 branch 输入，应优先提供有效 `fx`。
- `T`: `(Batch,)` 或 `(Batch, 1)`，仅在 `time_input=True` 时作为时间条件使用。
- `geo`: 可选几何/图信息；大多数 `cfd_benchmark` operator 模型不直接消费该字段。
- `args` 默认/来源：
- `act`: 默认/来源 `gelu`。
- `branch_depth`: 默认/来源 `5`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `n_hidden`: 默认/来源 `64`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `trunk_depth`: 默认/来源 `6`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

## 输出模式

- 输出通常为 `(Batch, NumPoints, out_dim)`；图/点云模型在内部可能 squeeze 单图 batch，但最终保持节点或点级目标变量输出。
- `out_dim` 必须与目标变量通道数一致，例如速度分量、压力、温度或其它 CFD 监督量。

## 形状变换

```text
输入准备
  x / node_features / edge_features
    -> 与 datapipe 输出 schema 对齐
  fx
    -> 与 x 的点顺序严格对齐

特征编码
  原始输入
    -> 预处理/编码模块
    -> hidden: (..., n_hidden) 或 (..., hidden_dim_processor)

主干计算
  点级输入保持 `(Batch, NumPoints, *)`，不做网格重排。

输出恢复
  hidden
    -> decoder / head / final block
    -> prediction: (..., out_dim)
```

## 常见修改点

- 按数据集输入/目标变量同步修改 `fun_dim`、`space_dim`、`out_dim`。
- 对结构化网格模型，优先修改 `shapelist`、`modes`、`unified_pos`、`ref`，确保 `NumPoints == prod(shapelist)`。
- 对注意力类模型，可调整 `n_layers`、`n_heads`、`mlp_ratio`、`dropout`、`slice_num/psi_dim/attn_type`。
- 对谱算子类模型，可调整 `modes`、Geo 投影分辨率、padding 策略和是否使用统一位置编码。
- 对图模型，可调整构图方式、边特征维度、聚合方式、processor 层数或图池化策略。

## 实现风险

- `args` 字段缺失会在构造阶段直接触发属性错误；生成配置时应至少覆盖源码读取的字段。
- `shapelist` 与真实点数不一致会导致 reshape、padding 或窗口注意力阶段失败。
- `time_input=True` 但调用 `forward` 未传入 `T`，会造成时间条件缺失或维度不一致。
- 非结构任务不要强行套结构网格模型；需要先确认 Geo 投影、插值或构图策略。
- 图模型的 `geo/graph/edge_features` 必须由 datapipe 提前准备，模型不负责从坐标自动构图。

## 启动方式

推荐 Python API 直接实例化目标模块，CLI 则可复用 CFD_Benchmark runner。

Python API 示例：

```python
from types import SimpleNamespace
from onescience.models.cfd_benchmark import DeepONet
import torch

args = SimpleNamespace(
    model="DeepONet",
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
model = DeepONet.Model(args, device).to(device)
x = torch.randn(2, 64 * 64, 2, device=device)
fx = torch.randn(2, 64 * 64, 3, device=device)
pred = model(x, fx)
```

CLI 示例：

```sh
python run.py --model DeepONet --task steady --geotype structured_2D --space_dim 2 --fun_dim 3 --out_dim 1 --n_hidden 64 --n_layers 3 --n_heads 4 --act gelu --mlp_ratio 1 --dropout 0.0 --unified_pos 0 --ref 8 --modes 12 --slice_num 32 --psi_dim 8 --attn_type nystrom --mwt_k 3 --branch_depth 5 --trunk_depth 6 --emb_dims 128 --data_path ./data/cfd --loader airfoil --batch_size 8 --epochs 500 --lr 0.001 --gpu 0
```

## 输入模式

- `x`: `(Batch, NumPoints, space_dim)`，坐标、评估点或统一位置编码的输入载体。
- `fx`: `(Batch, NumPoints, fun_dim)` 或 `None`，与位置对齐的输入场特征；若模型依赖双分支或 branch 输入，应优先提供有效 `fx`。
- `T`: `(Batch,)` 或 `(Batch, 1)`，仅在 `time_input=True` 时作为时间条件使用。
- `geo`: 可选几何/图信息；大多数 `cfd_benchmark` operator 模型不直接消费该字段。
- `args` 默认/来源：
- `act`: 默认/来源 `gelu`。
- `branch_depth`: 默认/来源 `5`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `n_hidden`: 默认/来源 `64`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `trunk_depth`: 默认/来源 `6`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

默认参数说明：
- `act`: 默认/来源 `gelu`。
- `branch_depth`: 默认/来源 `5`。
- `fun_dim`: 默认/来源 `INPUT_CHANNELS`。
- `geotype`: 默认/来源 `structured_2D`。
- `n_hidden`: 默认/来源 `64`。
- `out_dim`: 默认/来源 `TARGET_CHANNELS`。
- `ref`: 默认/来源 `8`。
- `shapelist`: 默认/来源 `[H, W]`。
- `space_dim`: 默认/来源 `2`。
- `time_input`: 默认/来源 `False`。
- `trunk_depth`: 默认/来源 `6`。
- `unified_pos`: 默认/来源 `0`。
- `task`: 通用 runner 默认 `steady`，当前模型不一定直接读取。
- `T_in`: 通用 runner 默认 `10`，当前模型不一定直接读取。
- `T_out`: 通用 runner 默认 `10`，当前模型不一定直接读取。

## 运行时接口

- `Model(args, device)`: 构造模型原语，`args` 必须支持属性访问。
- `forward(...)`: 主要运行时业务接口，执行场预测或节点回归。
- `model_factory.get_model(args, device)`: 辅助工厂入口，仅在复用原 CFD_Benchmark runner 或多模型统一调度时使用。

## 主要函数

- `structured_forward`
- `unstructured_forward`
- `forward`

## 执行资源

- 推荐 GPU 运行；谱算子、Transformer 和大图消息传递模型对显存较敏感。
- CPU 可用于小 batch 冒烟测试，但训练通常较慢。
- 需要安装 OneScience 运行环境及源码中对应依赖；图模型还需要 `torch_geometric` 或 `dgl`。
- 可用 `CUDA_VISIBLE_DEVICES` 或 runner 的 `--gpu` 指定设备。

## 运行限制

- 支持范围：输入函数特征和评估坐标可清晰分离的稳态或条件算子学习任务。
- 限制条件：缺少有效 fx、强依赖局部拓扑或需要规则网格谱卷积的任务。
- 常见失败模式包括 `args` 字段缺失、输入点数与 `shapelist` 不一致、非结构数据缺少图/边特征、`time_input` 与 `T` 传入不一致、显存不足。
- 进行多模型对比时，应优先保持同一 datapipe schema，不要为单个模型静默改变目标变量或归一化策略。

## 规划决策

### 描述

DeepONet 的规划决策知识用于指导 agent 判断何时选择该模型、如何生成配置、如何准备数据接口，以及失败时如何切换到辅助模型或适配器。它的组件定位是：使用 Branch Net 编码输入函数特征、Trunk Net 编码评估坐标，再通过点级特征乘积输出物理场。 在多模型 CFD_Benchmark 任务中，应以该主模型的输入协议和源码读取的 args 字段为核心，其它模型仅作为性能、结构或适配策略参考。

### 适用场景

- 当任务满足：输入函数特征和评估坐标可清晰分离的稳态或条件算子学习任务。。
- 当用户要求复用 `onescience.models.cfd_benchmark.DeepONet` 或进行 CFD_Benchmark 多模型对比。
- 当 datapipe 能提供源码要求的关键字段：`act`, `branch_depth`, `fun_dim`, `geotype`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `trunk_depth`, `unified_pos`。
- 不建议使用场景：缺少有效 fx、强依赖局部拓扑或需要规则网格谱卷积的任务。。

### 输入

- 任务类型：`steady`、`dynamic_autoregressive` 或 `dynamic_conditional`。
- 数据几何：`structured_1D/2D/3D`、`unstructured`，以及可选 `shapelist`。
- 输入输出通道：`space_dim`、`fun_dim`、`out_dim`。
- 运行资源：GPU 显存、batch size、点数/网格尺寸。
- 模型超参：源码读取字段 `act`, `branch_depth`, `fun_dim`, `geotype`, `n_hidden`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `trunk_depth`, `unified_pos`。

### 输出

- 生成一份可实例化的 `args` 或 YAML 配置。
- 明确 datapipe 输出 schema：输入张量、目标张量、可选时间 `T`、可选图结构。
- 给出模型选择理由、风险标记和备选模型。
- 给出最小冒烟测试：构造假输入并检查输出 shape 是否匹配 `out_dim`。

### 执行流程

1. 读取数据协议，确认 `space_dim/fun_dim/out_dim/geotype/shapelist`。
2. 按源码读取字段补齐 args；缺失字段不要依赖隐式默认。
3. 根据几何类型选择路径：结构化网格先验证 `NumPoints == prod(shapelist)`，非结构网格先验证投影或构图策略。
4. 实例化 `Model(args, device)`，用一个 batch 做 forward shape 测试。
5. 若通过冒烟测试，再接入训练脚本、损失函数、归一化和评估指标。
6. 记录失败原因并决定是修 datapipe、改 args，还是切换辅助模型。

### 约束

- 不得把代码路径写入 `main_functions`；源码路径仅由 `spec.md` 的 `code_references` 表达。
- `fun_dim/out_dim` 必须来自数据协议，不应根据模型名猜测。
- `shapelist` 必须来自真实结构网格或 adapter 探测结果。
- `unified_pos`、`time_input`、图结构、Geo 投影等开关必须与 datapipe 输出一致。
- 多模型对比中不要静默替换任务目标、训练集划分或归一化方式。

### 下一阶段建议

- 若冒烟测试通过，下一阶段生成训练 YAML 和最小训练命令。
- 若精度不足，优先检查数据归一化、目标变量、边界条件特征和模型容量，再考虑更换主干。
- 若结构网格模型在非结构数据上失败，优先生成 adapter 或切换到 `Transolver`、`GraphSAGE`、`MeshGraphNet`、`PointNet/RegDGCNN` 等更匹配路线。
- 若图模型失败，优先检查 `edge_index/graph/edge_features`，而不是修改输出头。

### 回退策略

- `AttributeError: args.xxx`: 回到源码字段清单补齐配置。
- `shape mismatch/reshape failed`: 检查 `NumPoints`、`shapelist`、`space_dim/fun_dim` 和 `unified_pos`。
- `CUDA out of memory`: 降低 batch size、点数、`n_hidden/n_layers`，或使用 checkpoint/分块推理。
- 非结构数据不兼容：生成插值/投影/构图 adapter；若风险高，切换到更适配的辅助模型。
- 训练不收敛：先检查归一化和目标量，再调整学习率、损失函数和模型容量。

## 组件契约入口

- ../contracts/onemlp.md
- ../contracts/timestep_embedding.md
- ../contracts/unified_pos_embedding.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/cfd_benchmark/DeepONet.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/exp/exp_steady.py`
