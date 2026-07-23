# description

LaProteina 规划知识用于基于 `Proteina` 的配置化 product-space flow matching 接口构建蛋白生成训练或采样代码。

# when_to_use

- 需要训练 LaProteina 的 flow matcher 与局部 latent Transformer。
- 需要按长度、CATH 或 motif 条件生成蛋白样本。
- 已有匹配的模型与可选 autoencoder checkpoint，需要复用 `predict_step`。
- 不用于从蛋白序列直接做确定性结构预测。

# inputs

- 完整 `cfg_exp`，包含 `product_flowmatcher`、`nn`、optimizer 和 autoencoder 设置。
- 训练 batch 的 clean modalities 与条件字段。
- 推理 `inf_cfg`、可选 autoguidance network `nn_ag`。
- 采样 batch 的 `nsamples`、`nres` 与条件字段。

# outputs

- 训练 loss 或生成样本 list。
- 每个生成样本的 atom37 坐标 `[n,37,3]` 与 residue type `[n]`。
- 与配置、checkpoint、条件模式和采样参数绑定的执行代码。

# procedure

1. 从 checkpoint 与任务确定 `cfg_exp.nn.name` 和 product-space modalities。
2. 配置 autoencoder checkpoint；不用 autoencoder 时显式配置为 `None`。
3. 构造 `Proteina(cfg_exp, ...)` 并加载匹配 checkpoint。
4. 训练时向 Lightning trainer 提供 batch，调用 `training_step` 路径。
5. 推理时先调用 `configure_inference(inf_cfg, nn_ag)`。
6. 构造含 `nsamples`、`nres` 和条件的 batch，调用 `predict_step`。
7. 验证每个 tuple 的坐标和 residue type 长度一致。

# constraints

- 直接导入 `onescience.models.laproteina`，配置与路径由调用方提供。
- `cfg_exp.nn.name` 只能使用源码支持的两个名称。
- CFG 的 unconditional 分支要求 batch 含 `cath_code` 或 `x_motif`。
- 推理前必须设置 `inf_cfg`。

# next_phase_recommendation

- 对生成坐标执行结构有效性与设计性评估。
- 需要文件结果时从返回的 atom37/residue types 独立序列化。
- 训练任务进入 Lightning runtime、日志和 checkpoint 规划。

# fallback

- latent 维度不匹配时核对 autoencoder 与 flow matcher 配置。
- 条件采样失败时检查条件字段，不删除模型内断言。
- 输出格式化失败时保留原始 flow samples 并检查 modalities/mask。
