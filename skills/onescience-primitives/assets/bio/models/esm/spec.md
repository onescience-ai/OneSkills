# component_info

ESM 是蛋白质语言模型与结构建模组件集合，覆盖单序列语言建模、MSA 建模、ESMFold 结构预测、GVP inverse folding 和变异效应打分等场景；以氨基酸/多序列比对 token 为输入，通过预训练 Transformer 表征驱动 logits、contact、结构 trunk 或序列采样模块。

# architecture_overview

ESM 在 OneScience 中不是单一网络，而是一组蛋白序列基础模型：

- ESM2：单序列蛋白语言模型，输出 token logits、隐藏层表征和可选 contact map。
- MSATransformer：多序列比对输入模型，适合 MSA 表征与接触预测。
- ESMFold：以 ESM2 表征为条件，接 folding trunk 与 OpenFold 风格结构输出头。
- GVPTransformerModel：以骨架坐标为条件进行 inverse folding 序列采样。

# parameter_scale

- ESM2 预训练族覆盖 8M、35M、150M、650M、3B、15B 等规模。
- 源码默认 `ESM2(num_layers=33, embed_dim=1280, attention_heads=20)` 对应 650M 级配置语义。
- ESMFold 默认加载 `esmfold_v1`，内部使用 ESM2 语言模型表征、folding trunk、distogram、pTM、pLDDT 等输出头。

# architecture_structure

序列表征路线
  FASTA / amino acid sequence
    -> Alphabet batch converter
    -> token ids: (Batch, SeqLen)
    -> ESM2 embedding + rotary Transformer layers
    -> lm_head logits / hidden representations / attentions
    -> contact_head optional contacts

结构预测路线
  amino acid sequence
    -> batch_encode_sequences
    -> ESM2 per-layer representations
    -> weighted layer combine + projection
    -> FoldingTrunk(sequence state, pair state)
    -> distogram / lddt / ptm heads
    -> atom37 positions + PDB

# input_schema

- ESM2 主输入：`tokens`，二维整数张量 `(Batch, SeqLen)`，由 `Alphabet` 按 FASTA 序列转换。
- ESMFold API 输入：`sequences`，字符串或字符串列表；多链可用 `:` 分隔。
- ESMFold forward 输入：`aa`, `mask`, `residx`, `masking_pattern`, `num_recycles`。
- 表征提取 CLI 输入：模型位置、FASTA 文件、输出目录、`repr_layers` 与 `include`。
- inverse folding 输入：骨架坐标、可选 partial sequence、temperature、confidence。

# output_schema

- ESM2：`logits`、`representations`，可选 `attentions` 与 `contacts`。
- ESMFold：`positions`、`atom37_atom_exists`、`plddt`、`mean_plddt`、`ptm`、`predicted_aligned_error`、`distogram_logits`、`lm_logits`。
- `output_to_pdb` / `infer_pdb`：PDB 字符串或 PDB 文件。
- 表征提取脚本：每条序列一个 `.pt` 文件，包含 mean/per-token/BOS/contact 等所选结果。

# shape_transformations

- FASTA sequence -> tokens: `(Batch, SeqLen)`
- token embedding: `(Batch, SeqLen, EmbedDim)`
- Transformer internal: `(SeqLen, Batch, EmbedDim)`
- logits: `(Batch, SeqLen, Vocab)`
- representations[layer]: `(Batch, SeqLen, EmbedDim)`
- ESMFold sequence -> aa: `(Batch, N_res)`
- ESM layer stack: `(Batch, N_res, N_layer + 1, ESM_dim)`
- sequence state: `(Batch, N_res, C_s)`
- pair state: `(Batch, N_res, N_res, C_z)`
- atom37 positions: `(Batch, N_res, 37, 3)`

# key_dependencies

- `ESM2`
- `MSATransformer`
- `ESMFold`
- `FoldingTrunk`
- `GVPTransformerModel`
- `Alphabet`
- `FastaBatchedDataset`
- `pretrained.load_model_and_alphabet`

# common_modification_points

- 更换任务时优先切换模型入口：表征提取用 ESM2，结构预测用 ESMFold，骨架到序列用 GVP inverse folding。
- 长序列 ESMFold 推理优先调小 `--max-tokens-per-batch` 或设置 `--chunk-size`，不要直接改 trunk 结构。
- 需要特定层表征时修改 `repr_layers` 和 `include`，保持 FASTA batch converter 协议不变。
- 变异打分应复用 variant-prediction 入口，保证 mutation column、offset 和 scoring strategy 与数据表一致。

# implementation_risks

- ESM 权重路径和 `torch.hub` 缓存目录必须可用，否则预训练加载失败。
- CPU 上 ESMFold 需要把 ESM 转为 fp32；大模型 CPU 推理会非常慢。
- ESMFold 的链间连接通过 residue index offset 和 poly-G linker 表达，多链结果不能按普通连续单链解释。
- MSA Transformer 输入协议与单序列 ESM2 不同，表征提取脚本显式拒绝 MSA Transformer。
- 长序列结构预测易触发显存不足，需要调整 batch token 数、chunk size 或 CPU offload。

# code_references

- `{onescience_path}/onescience/src/onescience/models/esm/esm2.py`
- `{onescience_path}/onescience/src/onescience/models/esm/msa_transformer.py`
- `{onescience_path}/onescience/src/onescience/models/esm/esmfold/v1/esmfold.py`
- `{onescience_path}/onescience/src/onescience/models/esm/inverse_folding/gvp_transformer.py`
- `{onescience_path}/onescience/src/onescience/models/esm/pretrained.py`
- `{onescience_path}/onescience/examples/biosciences/esm/README.md`
- `{onescience_path}/onescience/examples/biosciences/esm/scripts/extract.py`
- `{onescience_path}/onescience/examples/biosciences/esm/scripts/fold.py`
