# description

SimpleFold 规划知识用于用真实 processor、FoldingDiT、flow path、sampler 与 LightningModule 构建训练或结构采样代码。

# when_to_use

- 已有 SimpleFold 处理后的原子/token/ESM 特征，需要调用 `FoldingDiT`。
- 需要复用 `SimpleFold.training_step`、EMA、采样或 pLDDT 分支。
- 需要从 flow-matching 模型生成蛋白结构。
- 不用于把原始 FASTA 直接传入模型类。

# inputs

- architecture、processor、loss、path、sampler 及可选 optimizer/scheduler/pLDDT module。
- 与 `esm_model` 匹配的处理后 batch。
- 推理 sampler 配置和 checkpoint。
- 主干调试时的 `noised_pos`、`t`、`feats` 与可选 `self_cond`。

# outputs

- 主干的 `predict_velocity` 与 token `latent`。
- Lightning 训练 loss 或 `predict_step` 采样结果。
- EMA/checkpoint 状态及可选 confidence 输出。

# procedure

1. 召回 `simplefold_data_pipeline` 确定训练或推理 batch 契约，再从 checkpoint/config 构造 processor、FoldingDiT 组件、flow path、sampler 和 loss。
2. 用这些对象实例化 `SimpleFold` 并加载 checkpoint。
3. 训练时由 datamodule/processor 提供 batch，走 `training_step`。
4. 推理时由同一 feature protocol 提供 batch，走 `predict_step`。
5. 仅做主干验证时调用 `FoldingDiT(noised_pos, t, feats, self_cond)`。
6. 检查 atom count、token count、atom-to-token mapping 与 ESM channels。

# constraints

- 直接使用 `onescience.models.simplefold` 的模型、processor 与 sampler 契约。
- FASTA 必须在模型外转换为完整 feature dict。
- processor、architecture、sampler、path 与 checkpoint 必须同规格。
- `esm_s` 必须匹配所选 `esm_model`。

# next_phase_recommendation

- 将采样坐标交给结构格式化和质量评估。
- 训练任务进入 Lightning trainer、EMA 和 checkpoint 流程。
- 修改 feature schema 时同时更新 processor 与主干测试。

# fallback

- shape 失败时回到 `simplefold_data_pipeline` 检查 atom-to-token mapping 和 atom masks。
- ESM 维度失败时恢复 checkpoint 对应的 `esm_model` 与表征层数。
- 采样失败时单独验证 `FoldingDiT.forward`，再检查 path/sampler 集成。
