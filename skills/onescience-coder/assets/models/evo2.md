# Model Card: Evo2

## 基本信息

- 模型名：`Evo2`
- 任务类型：`基因组语言模型 / 长序列 DNA 建模`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/evo2/models/mamba.py`

## 模型定位

Evo2 是面向基因组序列的 foundation model 路线，在 OneScience 中通过 NeMo / Megatron Mamba 集成，核心对象是 tokenized genome sequence，而不是蛋白结构或分子图。

补充说明：

- 主模型封装类是 `MambaModel`
- 底层使用 `Evo2StyleMCoreMambaModel` 处理 logits 与训练 loss
- 配套 tokenizer 和 FASTA 推理数据集位于 `onescience.models.evo2.data`

## 输入定义

- `mamba_forward_step` 期望 batch 字段：
  - `tokens`
  - `position_ids`
  - `labels`
  - `loss_mask`
- `MambaModel.forward` 参数：
  - `input_ids`
  - `position_ids`
  - `attention_mask=None`
  - `labels=None`
  - `loss_mask=None`
- `SimpleFastaDataset` 推理样本字段：
  - `tokens`
  - `position_ids`
  - `seq_idx`
  - `loss_mask`

## 输出定义

- 推理时：
  - 若 `labels is None`，返回 logits，形状语义为 `[batch, seq, vocab]`
- 训练时：
  - 若提供 `labels`，底层模型返回 reweighted language model loss
- `SimpleFastaDataset.write_idx_map` 可输出 `seq_idx_map.json`，用于把 seq id 映射回 dataset index

## 主干结构

- `Evo2Tokenizer`
  - 基于 NeMo tokenizer，把 DNA 文本转为 token ids
- `SimpleFastaDataset`
  - 用 `NvFaidx` 读取 FASTA，构造 `tokens/position_ids/loss_mask`
- `MambaModel`
  - 托管 NeMo GPTModel 接口和推理 wrapper
- `Evo2StyleMCoreMambaModel`
  - embedding -> Mamba decoder -> output layer
  - 训练时使用大小写处理和 reweighted cross entropy
- `HybridMambaConfig8BEvo2Loss`
  - 提供 8B 风格混合 Mamba 配置默认值

## 主要依赖组件

- `Evo2Tokenizer`
- `SimpleFastaDataset`
- `MambaModel`
- `Evo2StyleMCoreMambaModel`
- `HybridMambaConfig8BEvo2Loss`

## 主要 Shape 变化

- FASTA sequence -> tokenizer ids: `List[int]`
- dataset `tokens`: `(seq_len,)`
- batch `tokens`: `(Batch, SeqLen)`
- decoder hidden states 内部遵循 Megatron sequence-first 约定
- 推理 logits 返回到 batch-first：`(Batch, SeqLen, Vocab)`

## 默认关键参数

- `HybridMambaConfig8BEvo2Loss.seq_length=8192`
- `hidden_size=4096`
- `num_layers=52`
- `vocab_size=512`
- `tokenizer_library="byte-level"`
- `to_upper="normalized_weighted"`
- `use_targeted_variance_loss=False`
- `SimpleFastaDataset(prepend_bos=True)` 时首 token 使用 `tokenizer.eod`，并把首位 `loss_mask` 置 0

## 常见修改点

- 改最大上下文时，要同时确认 tokenizer padding、dataset sample length、训练脚本 `--seq-length` 和模型 config
- 做 FASTA 推理时，优先用 `SimpleFastaDataset` 或 example 的 predict/infer 路线
- 做训练时，必须提供 `labels` 和 `loss_mask`，仅有 `tokens` 不足以计算 loss
- 数据预处理若使用 JSON 路线，要对齐 `append_eod`、`enforce_sample_length` 和 mmap dataset 配置

## 风险点

- Evo2 依赖 NeMo、Megatron、BioNeMo 相关包，不能按普通 PyTorch 单文件模型假设
- `GenomeDataset` 的可选 adapter 默认名写作 `evo2`，但 biology adapter registry 当前没有注册 `evo2` adapter；需要自定义 adapter 或使用 Evo2 自带数据路径
- `SimpleFastaDataset` 注释说明其当前更偏 prediction，不直接覆盖 pretraining / fine-tuning 所需的 label offset 协议
- `attention_mask` 在 Mamba 推理中基本置为 `None`，不要照搬 Transformer attention mask 逻辑

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `models/evo2/models/mamba.py`
3. 再看 `models/evo2/data/tokenizer.py` 与 `fasta_dataset.py`
4. 若涉及训练脚本，再看 `examples/biosciences/evo2/README.md`

## 组件契约入口

- `../contracts/evo2mamba.md`
- 当前 Evo2 主体未通过 OneScience `One*` wrapper 拼装，按 NeMo / Megatron 配置、组件契约与 Evo2 data helper 对齐

## 源码锚点

- `./onescience/src/onescience/models/evo2/models/mamba.py`
- `./onescience/src/onescience/models/evo2/data/tokenizer.py`
- `./onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `./onescience/src/onescience/models/evo2/utils/config.py`
- `./onescience/examples/biosciences/evo2/README.md`
