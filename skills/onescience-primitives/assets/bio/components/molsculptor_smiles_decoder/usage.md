# launch

Python API 方式调用，通常由 MolSculptor decoder 或 inferencer 调用：

```sh
python -c "from onescience.flax_models.MolSculptor.net.decoder import Decoder; print(Decoder.__name__)"
```

# input_schema

准备 SMILES token ids、mask、rope index 和来自 graph encoder 或 diffusion 模块的条件向量。token 词表需包含 BOS、EOS、UNK。

# runtime_interfaces

- `Decoder.__call__`: 根据条件和已有 token 输出下一步或全序列 logits。
- `AttentionBlock.__call__`: 条件注意力更新。
- `TransitionBlock.__call__`: 前馈更新。

# main_functions

- `__call__`

# execution_resources

开销随序列长度、层数、hidden size 增长；生成阶段还需要 beam search、top-k 或 top-p 等外部采样逻辑。

# operation_limits

输出只是 token logits，不保证 SMILES 合法；需要后续标准化、去重、性质过滤或 docking reward 评估。
