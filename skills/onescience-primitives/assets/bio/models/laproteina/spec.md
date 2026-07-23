# architecture_overview

LaProteina 的公开模型类是 `onescience.models.laproteina.proteina.Proteina`，继承 LightningModule。构造器根据 `cfg_exp` 建立 `ProductSpaceFlowMatcher`、`LocalLatentsTransformer` 或 `LocalLatentsTransformerMotifUidx`，并可加载冻结的 `AutoEncoder`；训练和预测均围绕包含多种蛋白表示的 batch 字典进行。

# parameter_scale

- `Proteina(cfg_exp, store_dir=None, autoencoder_ckpt_path=None)`。
- 局部 latent 维度优先来自 autoencoder；无 autoencoder 时取 `cfg_exp.product_flowmatcher.local_latents.dim`，缺省回退为 `8`。
- 优化器是 `torch.optim.Adam`，学习率来自 `cfg_exp.opt.lr`。
- 网络深度、宽度、flow modalities、采样步数和 guidance 参数均来自传入配置，模型类没有统一固定规模。

# architecture_structure

```text
clean protein modalities
  -> optional frozen AutoEncoder
  -> ProductSpaceFlowMatcher.corrupt_batch
  -> local latent Transformer
  -> clean-sample prediction
  -> flow-matching loss (training)
  or full_simulation (inference)
  -> atom37 coordinates + residue types
```

`call_nn` 支持 recycling；`predict_for_sampling` 支持 `full` 与 `ucond`；`predict_step` 使用已绑定的 inference config 驱动 flow matcher 完整采样。

# input_schema

- 构造输入 `cfg_exp` 必须包含 autoencoder、`product_flowmatcher`、`nn` 和 optimizer 所需字段。
- `training_step(batch, batch_idx)` 接收数据模态字典，内部添加 clean sample、时间/噪声状态、mask、自条件与 folding/inverse-folding 条件。
- 推理前调用 `configure_inference(inf_cfg, nn_ag)`。
- `predict_step` 的 batch 至少要提供采样所需的 `nsamples`、`nres` 及配置选定的条件字段。

# output_schema

- `training_step` 返回 batch 平均训练 loss。
- `predict_for_sampling` 返回所请求模式下的网络输出字典。
- `predict_step` 返回 list；每个元素是 `(coordinates, aatype)`，其中坐标 shape 为 `[n, 37, 3]`，残基类型 shape 为 `[n]`。
- `sample_formatting` 还支持原始 samples、atom37、PDB string 和 `coors37_n_aatype` 等内存表示。

# shape_transformations

1. clean modalities 由 autoencoder 或直接输入映射到 product space。
2. flow matcher 生成 `x_0`、`x_1`、`x_t`、`t` 与 `mask`。
3. Transformer 在 mask 和可选条件下预测 clean sample。
4. 推理通过多步 simulation 生成 batch samples。
5. formatter 将生成模态恢复为 `(B, N, 37, 3)` 坐标和 `(B, N)` residue types。

# key_dependencies

当前没有与 LaProteina 内部 flow matcher、Transformer 或 autoencoder 一一对应的独立 bio component primitive；构建代码时直接引用本模型源码模块。

# common_modification_points

- 通过 `cfg_exp.nn.name` 在两个源码支持的 Transformer 类之间选择，不使用未定义名称。
- 调整 product-space modalities 时同步修改 flow matcher、batch 字段和 sample formatter。
- 使用 classifier-free guidance 时确保 batch 含 `cath_code` 或 `x_motif`。
- 替换 autoencoder checkpoint 时核验 latent dimension，并保持其参数冻结策略。

# implementation_risks

- 未提供任何 autoencoder checkpoint 配置字段时构造器会抛出 `ValueError`；显式设为 `None` 才表示不用 autoencoder。
- `predict_step` 前未调用 `configure_inference` 会因 `inf_cfg` 缺失而失败。
- batch modalities 与 `product_flowmatcher` 配置不一致会在加噪、loss 或格式化阶段失败。
- Lightning checkpoint 中还保存 `nflops` 与 `nsamples_processed`，自定义加载逻辑应保留兼容。

# code_references

- `{onescience_path}/onescience/src/onescience/models/laproteina/proteina.py`
- `{onescience_path}/onescience/src/onescience/models/laproteina/flow_matching/product_space_flow_matcher.py`
- `{onescience_path}/onescience/src/onescience/models/laproteina/nn/local_latents_transformer.py`
- `{onescience_path}/onescience/src/onescience/models/laproteina/nn/local_latents_transformer_unindexed.py`
- `{onescience_path}/onescience/src/onescience/models/laproteina/partial_autoencoder/autoencoder.py`
