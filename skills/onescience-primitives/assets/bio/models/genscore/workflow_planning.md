# description

GenScore 规划知识用于构建蛋白图与配体图的混合密度前向、训练损失或高层 scoring 代码，并保持 encoder、图特征和 checkpoint 一致。

# when_to_use

- 已有配体与蛋白/口袋图，需要计算节点对混合密度输出。
- 需要训练或评估 GenScore 双塔图模型。
- 需要用源码 `scoring` 对结构输入生成最终 score 或贡献结果。
- 不用于生成 docking pose 或新分子。

# inputs

- `GraphTransformer` 或 `GatedGCN` 的真实构造参数。
- 配体/靶点 PyG graph batches，包含 `x`、`pos`、`batch`，配体还含 `edge_index`。
- `GenScore` 的 `in_channels`、`hidden_dim`、`n_gaussians`、dropout 和 `dist_threhold`。
- 可选 checkpoint 与高层 scoring 所需结构数据。

# outputs

- 模型前向七元组，或经评估函数得到的 score/贡献结果。
- 训练 loss 与 checkpoint 加载结果。
- encoder 类型和特征维度记录。

# procedure

1. 召回 `biology_genscore_dataset` datapipe 构造配体图、蛋白/口袋图与 batch，再检查两侧 node/edge feature 维度和配对。
2. 用源码 `_build_encoder` 等价参数构造两个同输出通道的 encoder。
3. 构造 `GenScore`，保持源码参数名 `dist_threhold`。
4. 加载匹配的 `model_state_dict`。
5. 训练时将七元组交给源码损失；推理时交给 `run_an_eval_epoch` 或使用高层 `scoring`。
6. 检查 score 数量与输入配体 ID 一致。

# constraints

- 构造参数、路径和样本均由调用方显式传入源码接口。
- `GenScore.forward` 不直接返回最终标量 score。
- ligand/target encoder 输出必须含 `x`、`pos`、`batch`。
- encoder 类型、feature dims 和 checkpoint 必须一致。

# next_phase_recommendation

- 将 score 与配体 ID 交给候选排序。
- 原子/残基贡献输出可进入可解释性报告。
- 训练后同时验证混合密度 loss 和最终 scoring 指标。

# fallback

- checkpoint 加载失败时重建准确 encoder 与 feature dims。
- 图 batch 失配时回到 `biology_genscore_dataset`，不在 forward 内广播不同样本。
- 最终 score 缺失时检查评估后处理，而不是修改七元组返回值。
