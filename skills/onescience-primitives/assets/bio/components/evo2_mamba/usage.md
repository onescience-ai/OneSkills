# launch

该组件原语描述 Evo2 的 DNA tokenizer、FASTA dataset 和 Mamba 前向适配层。它们用于把数据管线 batch 接到完整 `MambaModel`，不负责创建训练器或解析命令行。

```sh
python -c "from onescience.models.evo2.data.tokenizer import Evo2Tokenizer; from onescience.models.evo2.data.fasta_dataset import SimpleFastaDataset; from onescience.models.evo2.models.mamba import MambaModel, mamba_forward_step; import inspect; print(inspect.signature(Evo2Tokenizer)); print(inspect.signature(SimpleFastaDataset)); print(inspect.signature(SimpleFastaDataset.__getitem__)); print(inspect.signature(mamba_forward_step)); print(inspect.signature(MambaModel.forward))"
```

# input_schema

- `Evo2Tokenizer` 将 DNA 字符串映射为 token id；字符表、special token 与 checkpoint 必须匹配。
- `SimpleFastaDataset` 输入 FASTA 路径、tokenizer 和 `prepend_bos`，逐项返回模型预测所需的 token 样本。
- `mamba_forward_step` 的 batch 必须有 `tokens`、`position_ids`、`labels`、`loss_mask`。
- 模型返回训练 loss 或推理 logits，具体取决于是否传监督字段及底层 Mamba 状态。

# runtime_interfaces

- `Evo2Tokenizer`：DNA 文本编码/解码组件。
- `SimpleFastaDataset`：FASTA 到预测样本的数据组件。
- `SimpleFastaDataset.write_idx_map(...)`：保存样本索引和序列 ID 映射。
- `mamba_forward_step(model, batch)`：标准训练 batch 到 `MambaModel.forward` 的适配器。
- `MambaModel.forward(...)`：组件最终连接的完整模型接口。

# main_functions

- `Evo2Tokenizer.encode`
- `Evo2Tokenizer.decode`
- `SimpleFastaDataset.__getitem__`
- `SimpleFastaDataset.write_idx_map`
- `mamba_forward_step`

# execution_resources

- tokenizer/dataset 主要使用 CPU；Mamba 前向依赖 NeMo、Megatron、BioNeMo 和加速器环境。
- 长 FASTA 应限制 sequence length，并显式处理截断、BOS/EOD 与 padding。
- 分布式模型要求 batch 张量位于正确设备和并行 rank。

# operation_limits

- Mamba 路线通常不使用标准 Transformer attention mask，不能据此省略 `loss_mask`。
- FASTA dataset 用于预测样本，不自动生成训练标签、数据混合权重或 mmap 语料。
- DNA 大小写重加权会改变 loss 语义，训练和评估必须采用同一策略。
