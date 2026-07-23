# launch

该原语描述 AlphaFold3 JAX 完整模型内部的 Evoformer/Pairformer、原子交叉注意力、扩散和置信度组件。它们必须在 Haiku 变换中使用，并共享 `feat_batch.Batch`、global config 与完整模型参数树。

```sh
python -c "from onescience.flax_models.alphafold3.model.network.evoformer import Evoformer; from onescience.flax_models.alphafold3.model.network.modules import PairFormerIteration, EvoformerIteration; from onescience.flax_models.alphafold3.model.network.diffusion_head import DiffusionHead; from onescience.flax_models.alphafold3.model.network.confidence_head import ConfidenceHead; import inspect; print(inspect.signature(Evoformer)); print(inspect.signature(Evoformer.__call__)); print(inspect.signature(PairFormerIteration)); print(inspect.signature(EvoformerIteration)); print(inspect.signature(DiffusionHead)); print(inspect.signature(ConfidenceHead))"
```

# input_schema

- `Evoformer` 输入为 AF3 `feat_batch.Batch`，包含 token/atom、MSA、模板、reference structure、bond layout、mask 和链/实体索引。
- 输出核心为 `single` 与 `pair` embedding，供扩散头和置信度头共享。
- `DiffusionHead` 还读取噪声坐标、噪声水平、原子布局和条件 embedding；主要配置为样本数、步数、noise/step scale、Transformer 与 atom-cross-attention 参数。
- `ConfidenceHead` 读取扩散样本及 trunk embedding，输出 pLDDT/PAE/PDE/resolved 等置信度张量。

# runtime_interfaces

- `network.evoformer.Evoformer`：MSA、模板、原子条件和 Pairformer 主干。
- `network.modules.PairFormerIteration`、`EvoformerIteration`：内部迭代 block。
- `network.atom_cross_attention`：atom/token 间的编码器与解码器。
- `network.diffusion_head.DiffusionHead`：坐标去噪和采样。
- `network.confidence_head.ConfidenceHead`：样本置信度评估。
- `model.Model`：推荐的完整组件编排入口。

# main_functions

- `Evoformer.__call__`
- `PairFormerIteration.__call__`
- `DiffusionHead.__call__`
- `DiffusionHead.sample`
- `ConfidenceHead.__call__`
- `Model.get_inference_result`

# execution_resources

- 依赖 JAX、Haiku、AF3 参数树及由 AF3 数据管线生成的 batch/layout。
- token/atom 数、MSA 深度、Pairformer 层数、扩散步数和样本数决定显存与耗时。
- 注意力实现和分片策略必须与设备能力匹配。

# operation_limits

- AF3 JAX feature/layout 与 Protenix 或 AlphaFold2 batch 不可直接互换。
- 内部组件不解析 folding JSON、CCD 或结构文件，也不负责最终结果写出。
- 不能只对任意一个扩散样本解释置信度；排序需使用完整样本对应的 confidence 输出。
