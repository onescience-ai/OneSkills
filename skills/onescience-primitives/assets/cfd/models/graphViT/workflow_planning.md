# description

graphViT 的规划决策重点是判断任务是否为非结构网格上的时序 CFD 预测，并确保 EagleDatapipe、cluster 文件、节点类型编码、状态通道和自回归训练目标之间保持一致。模型以 GraphViT 为主：局部 GNN 处理网格近邻关系，RNNClusterPooling 汇聚到簇级 latent graph，PreLNTransformerBlock 在簇空间建立长距离依赖，GraphViTDecoder 将全局信息回填到节点并预测状态增量。

# when_to_use

- 任务是二维非结构网格流体动力学时序预测。
- 数据包含节点坐标、三角网格、速度、压力、节点类型和有效节点 mask。
- 需要在大规模节点图上捕获远距离空间依赖，但直接全节点注意力成本过高。
- 已经有或可以生成 constrained k-means cluster 文件。
- 输出目标是节点级下一步或多步滚动状态预测。

不适合优先使用的情况：

- 数据是规则网格图像形式且无非结构拓扑，可优先考虑 FNO、U-Net、FourCastNet 类模型。
- 任务没有时间维或不需要自回归滚动。
- 无法提供 cluster 分配或节点类型字段，且短期内不准备改造 datapipe。
- 需要严格守恒或显式求解器约束，而当前训练目标仅以监督损失为主。

# inputs

决策前应收集：

- 数据根目录、split 目录和 cluster 目录。
- `sim.npz` 是否包含 `pointcloud/VX/VY/PS/PG/mask`。
- `triangles.npy` 是否可转换为边。
- `constrained_kmeans_<n_cluster>.npy` 是否存在且与配置一致。
- 状态通道定义：速度维度、压力维度和拼接后的 `state_size`。
- 节点类型是否为 one-hot，且维度是否为 9。
- 训练、验证、测试窗口长度。
- 资源预算：GPU 数量、显存、目标 batch size、训练时长。

# outputs

规划输出应包含：

- `model_choice`：是否选择 `GraphViT`。
- `datapipe_choice`：是否使用 `EagleDatapipe` 以及数据字段是否需要适配。
- `model_parameters`：`state_size`、`w_size`、`n_attention`、`nb_gn`、`n_heads`、`pos_length`。
- `data_parameters`：`window_length_train/val/test`、`n_cluster`、`normalized`、`type_as_onehot`、`with_cells`。
- `training_plan`：batch size、学习率、loss_alpha、patience、checkpoint_dir。
- `evaluation_plan`：N-RMSE 时间步、动画数量、checkpoint 加载路径。
- `risk_notes`：cluster、mask、shape、DDP checkpoint 和长程滚动误差风险。

# procedure

```text
1. 判断任务类型
  -> 是否为 mesh-based temporal CFD forecasting
  -> 是否需要节点级状态滚动预测

2. 检查 Eagle 数据协议
  -> split 文件是否存在
  -> sim.npz 和 triangles.npy 是否完整
  -> cluster 文件是否与 n_cluster 匹配
  -> node_type 是否可 one-hot 到 9 维

3. 配置 datapipe
  -> 设置 data_dir / cluster_dir / splits_dir
  -> 设置 window_length_train/val/test
  -> 设置 n_cluster、normalized、type_as_onehot、with_cells
  -> 验证 batch 输出字段和 shape

4. 配置 GraphViT
  -> state_size = velocity_dim + pressure_dim
  -> w_size 根据资源预算选择，默认 512
  -> n_attention 和 n_heads 保持 attention mask 维度兼容
  -> nb_gn 根据局部传播需求调整

5. 训练
  -> state = concat(velocity, pressure)
  -> model(..., apply_noise=True)
  -> 使用 output_hat 与 target 计算增量损失
  -> 使用反归一化后的 state_hat 计算速度和压力指标
  -> 按验证集 best loss 保存 checkpoint

6. 评估与可视化
  -> 加载 best_model.pth
  -> model(..., apply_noise=False)
  -> 计算逐时间步 N-RMSE
  -> 可选用 cells 生成流场动画
```

# constraints

- 不要把 graphViT 当作无 cluster 的普通 GNN 使用；cluster 是主架构的一部分。
- `n_attention` 与 `n_heads` 默认都为 4；若改动其中之一，需要验证 attention mask shape。
- `w_size + 4 * pos_length` 必须能被 `n_heads` 整除。
- `state_size` 改动必须同步到模型、loss、denormalize 和通道切分逻辑。
- `node_type` 索引语义固定：normal、disable、input、output、wall 会影响噪声注入和边界覆盖。
- 评估动画依赖 `cells`，若 `with_cells=False` 只能做数值评估或需另行构造三角面。
- 训练/评估默认依赖硬编码归一化统计量，跨数据集迁移时必须重新审查尺度。

# next_phase_recommendation

- 若目标是复现实例：先使用默认 Eagle 配置运行训练或加载已有 checkpoint 做评估。
- 若目标是接入新 CFD 数据：先实现 EagleDatapipe 兼容字段或新 datapipe，确保输出字段与 GraphViT.forward 对齐。
- 若节点数很大：优先增加/调整 cluster 数量，而不是直接增大 Transformer 序列长度。
- 若长程预测误差增长快：增加训练窗口、使用 scheduled sampling、调低学习率或强化边界节点约束。
- 若局部细节不足：增加 `nb_gn` 或 Decoder 局部传播深度。
- 若全局依赖不足：增加 `n_attention`、`w_size` 或改进 cluster 构造质量。

# fallback

- 缺少 cluster 文件：先运行 clusterize 脚本或将配置改为已有的 `n_cluster`，不要直接绕过 pooling。
- 出现空 batch：检查 split 文件路径、样本目录和损坏样本，必要时先过滤数据。
- shape 不匹配：逐项打印 `mesh_pos/edges/state/node_type/clusters/clusters_mask` 的 batch shape，优先修复 datapipe。
- attention mask 报错：确认 `n_attention`、`n_heads`、`K` 和 mask reshape 逻辑一致。
- checkpoint 加载失败：区分包含 `model_state_dict` 的 checkpoint 和纯 state_dict，兼容 DDP 前缀。
- 新数据不适配 hard-coded normalization：先关闭归一化或重建统计量，再比较指标。
