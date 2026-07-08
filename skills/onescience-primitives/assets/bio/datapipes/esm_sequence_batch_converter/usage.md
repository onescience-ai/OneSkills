# launch

Python API 示例：

```sh
python -c "from onescience.datapipes.esm.alphabet import Alphabet; alphabet=Alphabet.from_architecture('ESM-1b'); converter=alphabet.get_batch_converter(); labels,seqs,tokens=converter([('seq1','MKTAYIAKQRQISFVKSHFSRQDILD')]); print(labels, tokens.shape)"
```

# input_schema

```text
单序列 batch:
  [('seq_id', 'AMINOACIDSEQUENCE'), ...]

MSA batch:
  [('msa_id', [('row1', 'ALIGNEDSEQ'), ('row2', 'ALIGNEDSEQ')]), ...]

可选:
  truncation_seq_length: int
```

# runtime_interfaces

- `Alphabet.from_architecture(name)`: 构造指定 ESM 架构的 alphabet。
- `Alphabet.get_batch_converter()`: 获取单序列 BatchConverter。
- `BatchConverter(...)`: 将序列 batch 转为 token batch。
- `MSABatchConverter(...)`: 将 MSA batch 转为 token batch。
- `FastaBatchedDataset.from_file(path)`: 从 FASTA 构造批数据集。

# main_functions

- `from_architecture`
- `get_batch_converter`
- `__call__`
- `from_file`
- `get_batch_indices`

# execution_resources

- 主要消耗 CPU 和内存。
- batch token 数与序列长度、MSA 深度直接相关。
- 长序列或深 MSA 建议设置截断或 token budget。

# operation_limits

- 不适合直接处理核酸序列。
- 不生成结构 feature dict。
- 不负责训练/验证 split。
- MSA 行长度不一致会导致转换失败。
