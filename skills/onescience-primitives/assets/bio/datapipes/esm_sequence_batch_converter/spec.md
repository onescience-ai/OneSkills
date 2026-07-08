# pipeline_responsibility

将蛋白序列、FASTA 记录或 MSA 对齐转换为 ESM 模型常用的 token tensor batch。该原语负责词表管理、特殊 token 插入、padding、批组装和 MSA batch 转换，不负责 MSA 搜索、蛋白结构特征生成或模型推理。

# pipeline_architecture

```text
输入
  单序列 batch
    -> [(label, sequence), ...]
  MSA batch
    -> [(label, [(msa_label, aligned_sequence), ...]), ...]
  FASTA
    -> FastaBatchedDataset

Alphabet
  -> token_to_idx / idx_to_token
  -> prepend_bos / append_eos
  -> padding_idx / cls_idx / eos_idx / mask_idx

BatchConverter
  -> 清理序列空格
  -> 截断到 truncation_seq_length
  -> 计算 max_len
  -> 填充 padding
  -> 输出 labels, strs, tokens

MSABatchConverter
  -> 校验每个 MSA 内序列等长
  -> 对每条 aligned sequence 编码
  -> 输出 MSA token batch

结构数据
  ESMStructuralSplitDataset
    -> 按 split 组织结构样本
```

# data_loading

- `read_fasta` 读取 FASTA 文本记录。
- `FastaBatchedDataset` 将 FASTA 序列组织为可按 token 数量分批的数据集。
- `read_alignment_lines` 可读取对齐文本行。
- `ESMStructuralSplitDataset` 用于结构相关 split 数据读取。

# sampling_strategy

- FASTA 数据按 record 顺序索引。
- `FastaBatchedDataset` 可按 token 预算生成 batch indices。
- BatchConverter 本身不划分 train/val/test，只处理调用方传入的 batch。
- MSA batch 要求同一个 MSA 内所有序列长度一致。

# data_transform

- 序列字符映射为 ESM vocabulary token id。
- 根据 alphabet 配置添加 BOS/EOS。
- 按 batch 最大长度 padding。
- 可按 `truncation_seq_length` 截断长序列。
- MSA 转换保留 MSA 维度，形成 batch x msa_depth x sequence_length 的 token 表示。

# input_schema

```text
单序列:
  batch:
    - label: str
      sequence: str

MSA:
  batch:
    - label: str
      alignment:
        - msa_label: str
          aligned_sequence: str

FASTA:
  fasta_path: path
  records:
    >description
    SEQUENCE
```

# output_schema

```text
BatchConverter output:
  labels: list[str]
  strs: list[str]
  tokens: tensor-like[int]
    shape: (Batch, SequenceLengthWithSpecialTokens)

MSABatchConverter output:
  labels: list[str]
  strs: nested list[str]
  tokens: tensor-like[int]
    shape: (Batch, MSASequences, SequenceLengthWithSpecialTokens)
```

# constraints

- 只处理 ESM alphabet 支持的蛋白序列字符。
- MSA 输入要求同一 alignment 内序列长度一致。
- 不生成 MSA，不做比对，也不处理结构模板。
- truncation 会丢弃超长序列尾部信息。
- 下游若需要结构坐标或 OpenFold feature dict，不能只使用该原语。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/esm/alphabet.py`
- `{onescience_path}/onescience/src/onescience/datapipes/esm/batch_converter.py`
- `{onescience_path}/onescience/src/onescience/datapipes/esm/constants.py`
- `{onescience_path}/onescience/src/onescience/datapipes/esm/fasta.py`
- `{onescience_path}/onescience/src/onescience/datapipes/esm/structural_dataset.py`
