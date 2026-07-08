# description

Transformer 的规划决策知识用于指导 agent 判断何时选择该模型、如何生成配置、如何准备数据接口，以及失败时如何切换到辅助模型或适配器。它的组件定位是：将坐标与场特征编码为 token 后使用多层自注意力 block 做全局交互，末层直接输出目标场。 在多模型 CFD_Benchmark 任务中，应以该主模型的输入协议和源码读取的 args 字段为核心，其它模型仅作为性能、结构或适配策略参考。

# when_to_use

- 当任务满足：需要普通全局自注意力基线、点数适中且希望接口与其他 CFD_Benchmark 模型一致的任务。。
- 当用户要求复用 `onescience.models.cfd_benchmark.Transformer` 或进行 CFD_Benchmark 多模型对比。
- 当 datapipe 能提供源码要求的关键字段：`act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos`。
- 不建议使用场景：NumPoints 很大且没有稀疏化/降采样策略的任务。。

# inputs

- 任务类型：`steady`、`dynamic_autoregressive` 或 `dynamic_conditional`。
- 数据几何：`structured_1D/2D/3D`、`unstructured`，以及可选 `shapelist`。
- 输入输出通道：`space_dim`、`fun_dim`、`out_dim`。
- 运行资源：GPU 显存、batch size、点数/网格尺寸。
- 模型超参：源码读取字段 `act`, `dropout`, `fun_dim`, `geotype`, `mlp_ratio`, `n_heads`, `n_hidden`, `n_layers`, `out_dim`, `ref`, `shapelist`, `space_dim`, `time_input`, `unified_pos`。

# outputs

- 生成一份可实例化的 `args` 或 YAML 配置。
- 明确 datapipe 输出 schema：输入张量、目标张量、可选时间 `T`、可选图结构。
- 给出模型选择理由、风险标记和备选模型。
- 给出最小冒烟测试：构造假输入并检查输出 shape 是否匹配 `out_dim`。

# procedure

1. 读取数据协议，确认 `space_dim/fun_dim/out_dim/geotype/shapelist`。
2. 按源码读取字段补齐 args；缺失字段不要依赖隐式默认。
3. 根据几何类型选择路径：结构化网格先验证 `NumPoints == prod(shapelist)`，非结构网格先验证投影或构图策略。
4. 实例化 `Model(args, device)`，用一个 batch 做 forward shape 测试。
5. 若通过冒烟测试，再接入训练脚本、损失函数、归一化和评估指标。
6. 记录失败原因并决定是修 datapipe、改 args，还是切换辅助模型。

# constraints

- 不得把代码路径写入 `main_functions`；源码路径仅由 `spec.md` 的 `code_references` 表达。
- `fun_dim/out_dim` 必须来自数据协议，不应根据模型名猜测。
- `shapelist` 必须来自真实结构网格或 adapter 探测结果。
- `unified_pos`、`time_input`、图结构、Geo 投影等开关必须与 datapipe 输出一致。
- 多模型对比中不要静默替换任务目标、训练集划分或归一化方式。

# next_phase_recommendation

- 若冒烟测试通过，下一阶段生成训练 YAML 和最小训练命令。
- 若精度不足，优先检查数据归一化、目标变量、边界条件特征和模型容量，再考虑更换主干。
- 若结构网格模型在非结构数据上失败，优先生成 adapter 或切换到 `Transolver`、`GraphSAGE`、`MeshGraphNet`、`PointNet/RegDGCNN` 等更匹配路线。
- 若图模型失败，优先检查 `edge_index/graph/edge_features`，而不是修改输出头。

# fallback

- `AttributeError: args.xxx`: 回到源码字段清单补齐配置。
- `shape mismatch/reshape failed`: 检查 `NumPoints`、`shapelist`、`space_dim/fun_dim` 和 `unified_pos`。
- `CUDA out of memory`: 降低 batch size、点数、`n_hidden/n_layers`，或使用 checkpoint/分块推理。
- 非结构数据不兼容：生成插值/投影/构图 adapter；若风险高，切换到更适配的辅助模型。
- 训练不收敛：先检查归一化和目标量，再调整学习率、损失函数和模型容量。
