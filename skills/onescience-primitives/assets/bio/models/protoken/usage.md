# launch

PDB 编码与重建示例:

```sh
python onescience/src/onescience/flax_models/protoken/scripts/infer.py --pdb_path ./input.pdb --save_dir_path ./outputs/protoken --load_ckpt_path ./ckpts/protoken_params.pkl --padding_len 768
```

token indexes 解码为结构示例:

```sh
python onescience/src/onescience/flax_models/protoken/scripts/decode_structure.py --input_path ./outputs/protoken/vq_code_indexes.pkl --output_dir ./outputs/protoken_decode --load_ckpt_path ./ckpts/protoken_params.pkl --padding_len 768
```

# input_schema

- `infer.py` 输入:
  - `--pdb_path`: 单个 PDB。
  - `--save_dir_path`: 输出目录。
  - `--load_ckpt_path`: ProToken checkpoint。
  - `--padding_len`: 常见默认 `768`。
- `decode_structure.py` 输入:
  - `--input_path`: token index pickle。
  - `--output_dir`: 输出目录。
  - ProToken checkpoint。
  - padding length / output path。
- 与 PT-DiT 联动输入:
  - `protoken_emb.pkl`。
  - `aatype_emb.pkl`。
  - ProToken decoder checkpoint。

# runtime_interfaces

- `scripts/infer.py`: PDB 到 token 与重建结构。
- `scripts/decode_structure.py`: token indexes 到 PDB。
- `VQTokenizer`: 离散 codebook quantization。
- `InferenceVQWithLossCell`: encoder/tokenizer/decoder 推理封装。
- `Protein_Decoder`: 结构输出。

# main_functions

- `inference`
- `decode`
- `squared_euclidean_distance_fn`
- `entropy_loss_fn`
- `compute_plddt`
- `from_pdb_string`
- `to_pdb`

# execution_resources

- 需要 JAX/Flax、ProToken checkpoint、PDB 输入和可写输出目录。
- 长蛋白或较大 `padding_len` 会增加显存。
- 与 PT-DiT 联动时还需要 embedding pickle 和 PT-DiT checkpoint。

# operation_limits

- 不接收纯 FASTA 直接做 AF2/AF3 结构预测。
- token 解码结构是重建结果，不等同于实验验证结构。
- 输入 PDB 缺残基或缺原子时会影响特征和重建质量。
- checkpoint 与 codebook 不一致时输出不可解释。
