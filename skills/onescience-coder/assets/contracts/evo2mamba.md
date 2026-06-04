# Contract: Evo2Mamba

## 基本信息

- 组件名：`MambaModel / Evo2StyleMCoreMambaModel / Evo2Tokenizer / SimpleFastaDataset`
- 所属模块族：`transformer`
- 统一入口：`OneTransformer`
- 注册名：`style="Evo2Mamba"`
- 注册状态：`contract_only`

## 组件职责

Evo2 Mamba 组件负责长基因组序列的 tokenization、FASTA prediction dataset 构造，以及基于 NeMo / Megatron Mamba 的语言模型 forward 与 reweighted loss。

补充说明：

- 这是基因组语言模型，不处理蛋白结构坐标、MSA 或 PDB
- 契约层把 Mamba 主模型收束到 `OneTransformer`；`Evo2Tokenizer` 与 `SimpleFastaDataset` 属于数据 / tokenizer 辅助，不作为 `One*` 模型组件注册
- 依赖 NeMo、Megatron、BioNeMo 生态，不能按普通 PyTorch 小模型方式实例化
- `SimpleFastaDataset` 当前定位是 prediction，不覆盖完整 pretraining / fine-tuning 数据协议

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `MambaModel.forward` 输入：
  - `input_ids`
  - `position_ids`
  - `attention_mask=None`
  - `labels=None`
  - `loss_mask=None`
- `mamba_forward_step` batch 字段：
  - `tokens`
  - `position_ids`
  - `labels`
  - `loss_mask`
- `SimpleFastaDataset.__getitem__` 输出：
  - `tokens`
  - `position_ids`
  - `seq_idx`
  - `loss_mask`

内部统一做法：

- `Evo2Tokenizer` 将 DNA 文本转 token ids
- `SimpleFastaDataset` 通过 `NvFaidx` 读取 FASTA，并可在序列前插入 BOS/EOD token
- `Evo2StyleMCoreMambaModel` 执行 embedding、Mamba decoder、output layer
- 若提供 `labels`，先做 uppercase/lowercase 处理，再计算 reweighted cross entropy
- 若不提供 `labels`，返回 batch-first logits

## 构造参数

- `HybridMambaConfig8BEvo2Loss`
  - `num_layers=52`
  - `seq_length=8192`
  - `hidden_size=4096`
  - `vocab_size=512`
  - `mamba_state_dim=128`
  - `mamba_head_dim=64`
  - `ffn_hidden_size=21504`
  - `to_upper="normalized_weighted"`
  - `use_targeted_variance_loss=False`
- `SimpleFastaDataset`
  - `fasta_path`
  - `tokenizer`
  - `prepend_bos=True`

## 输出约定

- 推理：
  - `logits`: `(B, SeqLen, Vocab)`
- 训练：
  - language model loss
- FASTA dataset：
  - `seq_idx_map.json` 可由 `write_idx_map` 写出

如果有明确边界条件，也写在这里：

- `prepend_bos=True` 时首位 `loss_mask=0`
- `attention_mask` 在 Mamba 路线中通常不按 Transformer mask 使用
- pretraining / fine-tuning 需要 label offset 协议，不能只用 `SimpleFastaDataset` prediction 输出

## 典型调用位置

- `examples/biosciences/evo2/train_one_node.py`
- `examples/biosciences/evo2/train_slurm.py`
- Evo2 checkpoint 转换、推理与 FASTA prediction 工具链

## 典型参数

- prediction dataset：
  - `SimpleFastaDataset(fasta_path, tokenizer, prepend_bos=True)`
- config 默认：
  - `seq_length=8192`
  - `vocab_size=512`
  - `tokenizer_library="byte-level"`
- 契约层目标调用：
  - `OneTransformer(style="Evo2Mamba", ...)`

## 风险点

- `style="Evo2Mamba"` 是 skill 契约归一名，不表示当前源码已经在 `OneTransformer` registry 中可直接实例化
- `GenomeDataset` 的通用 adapter 路线不等价于 Evo2 训练 batch，需要优先使用 Evo2 自带 tokenizer / data helper
- 长序列上下文和模型配置、训练脚本参数、checkpoint 必须一致
- lowercase reweighting 和 `to_upper` 会影响 loss 语义，不能在数据预处理里随意统一大小写而不检查配置
- NeMo/Megatron pipeline 并行和 inference context 会影响 logits 返回形态

## 源码锚点

- `./onescience/src/onescience/models/evo2/models/mamba.py`
- `./onescience/src/onescience/models/evo2/data/tokenizer.py`
- `./onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `./onescience/src/onescience/models/evo2/utils/config.py`
- `./onescience/examples/biosciences/evo2/README.md`
