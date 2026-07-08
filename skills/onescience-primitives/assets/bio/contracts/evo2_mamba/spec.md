# component_info

`evo2_mamba` 是 Evo2 基因组语言模型组件契约，覆盖 `MambaModel`、`Evo2StyleMCoreMambaModel`、`Evo2Tokenizer` 和 `SimpleFastaDataset`。原始 contract 中模块族为 `transformer`，目标统一入口为 `OneTransformer`，注册名为 `style="Evo2Mamba"`，注册状态为 `contract_only`。

# purpose

用于长基因组序列 tokenization、FASTA prediction dataset 构造，以及基于 Mamba 的语言模型 forward 与 reweighted loss。它处理 genome tokens，不处理蛋白结构坐标、MSA 或 PDB。

# input_schema

```text
MambaModel.forward:
  input_ids
  position_ids
  attention_mask=None
  labels=None
  loss_mask=None

mamba_forward_step batch:
  tokens
  position_ids
  labels
  loss_mask

SimpleFastaDataset.__getitem__:
  tokens
  position_ids
  seq_idx
  loss_mask
```

# output_schema

```text
推理:
  logits: (B, SeqLen, Vocab)

训练:
  language model loss

FASTA dataset:
  seq_idx_map.json from write_idx_map
```

# parameters

- `HybridMambaConfig8BEvo2Loss`: `num_layers=52`、`seq_length=8192`、`hidden_size=4096`、`vocab_size=512`、`mamba_state_dim=128`、`mamba_head_dim=64`、`ffn_hidden_size=21504`、`to_upper="normalized_weighted"`、`use_targeted_variance_loss=False`。
- `SimpleFastaDataset`: `fasta_path`、`tokenizer`、`prepend_bos=True`。

# key_dependencies

- `mamba.py`
- `tokenizer.py`
- `fasta_dataset.py`
- `config.py`
- `README.md`

# usage_and_risks

Evo2Tokenizer 将 DNA 文本转 token ids，SimpleFastaDataset 读取 FASTA 并可插入 BOS/EOD token，Mamba 模型执行 embedding、decoder 和 output layer；若提供 labels，则计算 reweighted cross entropy。`contract_only` 来自原始 contract，表示 `style="Evo2Mamba"` 不代表当前源码已在 `OneTransformer` registry 中可直接实例化。pretraining/fine-tuning 不能只用 SimpleFastaDataset prediction 输出。

# code_references

- `{onescience_path}/onescience/src/onescience/models/evo2/models/mamba.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/tokenizer.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/utils/config.py`
- `{onescience_path}/onescience/examples/biosciences/evo2/README.md`
