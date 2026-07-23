# launch

LaProteina 是基于 product-space flow matching 的蛋白结构生成模型。完整模型入口为 Lightning `Proteina`；训练器调用 `training_step`，推理器加载 checkpoint 后调用 `configure_inference` 和 `predict_step`。

```sh
python -c "from onescience.models.laproteina.proteina import Proteina; import inspect; print(inspect.signature(Proteina)); print(inspect.signature(Proteina.load_from_checkpoint)); print(inspect.signature(Proteina.training_step)); print(inspect.signature(Proteina.configure_inference)); print(inspect.signature(Proteina.predict_step))"
```

# input_schema

- 构造输入 `cfg_exp` 至少描述 `product_flowmatcher`、`nn`、优化器及 autoencoder checkpoint；`store_dir` 控制临时验证产物位置。
- 训练 batch 是包含坐标、局部 latent、残基/原子 mask 和条件信息的字典，具体字段由 LaProteina datapipe 与 flow matcher 配置决定。
- 推理 batch 描述目标长度、样本数；motif scaffolding 还需 motif 坐标、原子选择、contig/残基映射和相应 mask。
- `predict_step` 返回采样结果列表；`sample_formatting` 可将 product-space 样本转换为 atom37/PDB 友好的坐标、mask 和残基类型。
- 主要采样参数为步数、self-conditioning、guidance weight、autoguidance ratio、目标长度和每批样本数。

# runtime_interfaces

- `Proteina(cfg_exp, store_dir=None, autoencoder_ckpt_path=None)`：完整 Lightning 模型。
- `Proteina.load_from_checkpoint(...)`：恢复主模型权重和训练状态。
- `Proteina.training_step(batch, batch_idx)`、`validation_step(...)`：训练/验证入口。
- `Proteina.configure_inference(inf_cfg, nn_ag)`：绑定采样配置和可选 autoguidance 模型。
- `Proteina.predict_step(batch, batch_idx)`、`predict_for_sampling(...)`：结构采样入口。
- `Proteina.sample_formatting(...)`：输出结构格式化。

# main_functions

- `Proteina.training_step`
- `Proteina.validation_step`
- `Proteina.configure_inference`
- `Proteina.predict_for_sampling`
- `Proteina.predict_step`
- `Proteina.sample_formatting`
- `Proteina.configure_optimizers`

# execution_resources

- 依赖 PyTorch、Lightning、OmegaConf 及与主模型匹配的 autoencoder checkpoint。
- 源码训练和采样面向 CUDA；结构长度、采样步数、batch size 与并行样本数共同决定显存。
- motif 任务还需经过一致编号和单位处理的 motif 结构数据。

# operation_limits

- LaProteina 生成结构候选，不是给定 FASTA 的确定性结构预测器。
- autoguidance 权重大于零时必须提供结构兼容的 guidance checkpoint。
- motif 原子选择、链编号或残基映射错误会直接破坏条件约束。
- 输出仍需进行几何质量、可设计性和独立折叠验证。
