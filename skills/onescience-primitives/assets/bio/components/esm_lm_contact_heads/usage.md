# launch

Python API 方式调用，通常接在 ESM trunk 输出之后：

```sh
python -c "from onescience.modules.esm.heads import RobertaLMHead, ContactPredictionHead; print(RobertaLMHead.__name__, ContactPredictionHead.__name__)"
```

# input_schema

LM head 需要 hidden states；contact head 需要 attention maps 和原始 tokens，并正确标记 BOS/EOS/padding。

# runtime_interfaces

- `RobertaLMHead.forward`: 输出 token logits。
- `ContactPredictionHead.forward`: 从 attention map 估计接触概率。

# main_functions

- `forward`

# execution_resources

LM head 开销与词表大小相关；contact head 开销与残基长度平方相关。

# operation_limits

contact head 不能脱离 attention maps 使用；特殊 token 裁剪配置错误会使接触图坐标偏移。该模块不输出 docking score。
