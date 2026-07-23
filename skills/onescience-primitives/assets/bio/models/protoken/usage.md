# launch

ProToken 通过 `src/onescience/flax_models/protoken` 中的 Flax 模型 API 使用。训练和推理代码分别组合编码器、瓶颈、VQ 解码器与蛋白结构解码器：

```sh
python -c "from onescience.flax_models.protoken.model.encoder import VQ_Encoder; from onescience.flax_models.protoken.model.bottleneck import BottleneckModel; from onescience.flax_models.protoken.model.decoder import VQ_Decoder, Protein_Decoder; from onescience.flax_models.protoken.inference.inference import InferenceVQWithLossCell; import inspect; print(inspect.signature(VQ_Encoder)); print(inspect.signature(BottleneckModel)); print(inspect.signature(VQ_Decoder)); print(inspect.signature(Protein_Decoder)); print(inspect.signature(InferenceVQWithLossCell))"
```

# input_schema

- PDB 编码输入应先转换为 residue/atom feature dict、mask、aatype、residue index 与几何字段；模型类不直接读取文件路径。
- checkpoint 参数树、padding length、VQ codebook 和模型配置必须对应同一训练规格。
- 解码输入是离散 token index 或对应 codebook embedding，以及结构恢复所需的序列和 mask 字段。
- 与 PT-DiT 联动输入:
  - `protoken_emb.pkl`。
  - `aatype_emb.pkl`。
  - ProToken decoder checkpoint。

# runtime_interfaces

- `VQ_Encoder.__call__`：把结构特征编码为连续 latent。
- `BottleneckModel.__call__`：执行瓶颈映射与量化相关处理。
- `VQ_Decoder.__call__`：把量化 latent 解码为结构表示。
- `Protein_Decoder.__call__`：输出蛋白结构相关预测。
- `InferenceVQWithLossCell.__call__`：组合 encoder、tokenizer、decoder 与推理损失。

# main_functions

- `VQ_Encoder.__call__`
- `BottleneckModel.__call__`
- `VQ_Decoder.__call__`
- `Protein_Decoder.__call__`
- `InferenceVQWithLossCell.__call__`

# execution_resources

- 需要 JAX/Flax、ProToken checkpoint、PDB 输入和可写输出目录。
- 长蛋白或较大 `padding_len` 会增加显存。
- 与 PT-DiT 联动时还需要 embedding pickle 和 PT-DiT checkpoint。

# operation_limits

- 不接收纯 FASTA 直接做 AF2/AF3 结构预测。
- token 解码结构是重建结果，不等同于实验验证结构。
- 输入 PDB 缺残基或缺原子时会影响特征和重建质量。
- checkpoint 与 codebook 不一致时输出不可解释。
