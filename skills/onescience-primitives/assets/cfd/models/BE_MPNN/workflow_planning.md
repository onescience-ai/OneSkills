# description

BE_MPNN 的规划决策重点是判断当前任务是否属于 BENO 风格的边界条件感知 PDE 代理求解，并在数据协议、模型结构和训练/推理脚本之间保持一致。该模型适合作为 BENO datapipe 的下游主模型：用 `G1` 建模域内 forcing 与几何特征，用 `G2` 建模边界条件分支，通过边界 Transformer 将边界点序列变成全局调制信息，再由图消息传递预测节点解场。

# when_to_use

- 任务是二维椭圆型 PDE、Poisson/Dirichlet/Neumann 类问题或类似边界条件驱动的解场预测。
- 数据可以被组织为 `RHS/SOL/BC` 三类数组，并由 BENO datapipe 构造为 `G1/G2/G1+2` 异构图。
- 需要显式利用复杂边界形状、边界点序列和非均匀边界值。
- 输出目标是采样节点处的标量或少量通道解场。
- 希望使用消息传递网络处理不规则采样节点和邻接边特征。

不宜优先使用的情况：

- 输入是规则网格且无复杂边界条件，可优先考虑 FNO、U-FNO、UNO 等规则网格神经算子。
- 任务是蛋白质、分子、气象或通用图分类，BE_MPNN 的输入协议和边界嵌入假设并不匹配。
- 数据无法提供边界点序列或 `G1/G2` 双分支图结构。

# inputs

决策前应确认：

- PDE 类型：是否为 BENO 适配的 elliptic PDE 或边界驱动问题。
- 原始数据：是否有 `RHS_<prefix>_all.npy`、`SOL_<prefix>_all.npy`、`BC_<prefix>_all.npy`。
- 数据字段：RHS 坐标列、forcing 列、cell_state 列和 SOL 目标列是否与 datapipe 约定一致。
- 边界条件：边界点数、边界坐标和值是否可形成 `(BoundaryNodes, 3)`。
- 图规模：`resolution`、`ns`、节点数、边数和 batch size。
- 输出要求：预测标量解场还是多通道解场。
- 运行模式：训练、推理、评估、可视化或模型结构改造。

# outputs

规划输出应包含：

- `model_choice`：是否选择 `HeteroGNS/BE_MPNN` 作为主模型。
- `datapipe_choice`：是否使用 `BENODatapipe` 以及需要修改的数据字段。
- `model_parameters`：`nnode_in_features`、`nedge_in_features`、`nnode_out_features`、`latent_dim`、`nmessage_passing_steps`、`boundary_dim`、`trans_layer`。
- `training_entry`：训练脚本、配置文件、checkpoint 输出目录。
- `inference_entry`：推理脚本、checkpoint 加载策略、结果重建方式。
- `risk_notes`：shape、归一化、边界维度、缓存一致性和分布式运行风险。

# procedure

```text
1. 识别任务
  -> 是否是边界条件驱动的 PDE surrogate
  -> 是否需要不规则域或复杂边界建模

2. 检查数据协议
  -> RHS/SOL/BC 文件是否齐备
  -> file_prefix、resolution、ntrain、ntest 是否与文件内容匹配
  -> 边界字段是否能形成 (BoundaryNodes, 3)

3. 构造或复用 BENODatapipe
  -> 生成 HeteroData
  -> 检查 G1/G2 节点特征维度
  -> 检查 edge_features 维度
  -> 检查 G1+2.y 与模型输出节点顺序一致

4. 配置 BE_MPNN
  -> nnode_in_features = G1.x.shape[-1]
  -> nedge_in_features = G1.edge_features.shape[-1]
  -> nnode_out_features = 目标通道数
  -> 根据显存预算调整 latent_dim 和 nmessage_passing_steps
  -> 根据边界复杂度调整 boundary_dim 和 trans_layer

5. 训练与评估
  -> 使用 model(batch) 得到节点输出
  -> 与 batch["G1+2"].y 计算训练损失
  -> 使用 u_normalizer.decode 恢复物理尺度后计算 L2/MAE
  -> 按 save_period 保存 checkpoint

6. 推理与重建
  -> 加载最新或指定 checkpoint
  -> 对 test_loader 前向预测
  -> 用 sample_idx 回填到 resolution x resolution 网格
  -> 解码并输出图像或数组结果
```

# constraints

- 文件落地与配置应保持 BENO 示例目录约定，避免把模型路径写死到业务字段中。
- 模型 `forward` 不负责数据校验；调用前必须保证 `G1/G2` 字段完整。
- `boundary` 最后一维固定匹配边界 Transformer 的 `enc_in=3`。
- `trans_layer` 仅控制边界 Transformer 深度；不要把它当作消息传递步数。
- 修改 datapipe 字段后，必须同步修改模型输入维度与训练脚本中配置。
- 多通道输出需要同步修改 `nnode_out_features`、目标 `y` shape、loss reshape 和推理回填逻辑。
- 若使用缓存，配置变化后应确保旧 `.pt` 缓存不会被误用。

# next_phase_recommendation

- 若当前任务只是运行 BENO 示例：优先使用现有 `train.py`、`inference.py` 和 `conf/beno.yaml`，只修改数据路径、样本数和输出目录。
- 若当前任务是新 PDE 数据接入：先改造或复用 `BENODatapipe`，确保输出图协议与 BE_MPNN 对齐，再训练模型。
- 若边界条件更复杂：优先扩展边界特征和 `boundary_fn`，并保持 `(BoundaryNodes, C)` 到全局边界向量的清晰映射；若 C 不再等于 3，同步修改 Transformer `enc_in`。
- 若误差集中在复杂几何附近：尝试增加 `boundary_dim`、`nmessage_passing_steps`、边界采样密度或在 Decoder 引入门控融合。
- 若训练不稳定：降低学习率、检查 normalizer、增加残差正则或减少消息传递深度。

# fallback

- 当 `HeteroData` 字段不完整时：先回退到 datapipe 诊断，打印 `G1/G2/G1+2` 的字段与 shape。
- 当边界 shape 不匹配时：先在数据层将边界坐标和值整理为 `(BoundaryNodes, 3)`；若业务确实需要更多边界通道，再改造 `InteractionNetwork.boundary_fn`。
- 当缓存与配置不一致时：清理或更换 `cache_dir`，重新预处理。
- 当 checkpoint 加载失败时：区分 DDP 与非 DDP state_dict，必要时剥离或补充 `module.` 前缀。
- 当 BE_MPNN 表达能力不足时：先调大 latent/message passing/boundary encoder，再考虑替换分支融合或引入其他神经算子。
- 当任务不满足 BENO 图协议时：不要强行调用 BE_MPNN，改选规则网格神经算子或先实现适配 datapipe。
