# description

该原语用于规划基因组 FASTA 读取和核苷酸编码任务。决策重点是判断任务是否只需要轻量 DNA/RNA 序列样本，还是需要进入 Evo2 这类长序列语言模型的数据协议；前者可直接复用 `GenomeDataset`，后者应转向 Evo2 tokenizer 和预处理链路。

# when_to_use

- 输入是 DNA/RNA FASTA。
- 目标是快速读取序列、检查样本或做简单编码。
- 需要为自定义 genome adapter 搭建最小 dataset skeleton。
- Evo2 推理前需要确认 FASTA 内容，但最终 token batch 仍由 Evo2 数据层生成。

# inputs

- FASTA 文件或目录路径。
- 序列类型：DNA 或 RNA。
- 是否需要 adapter。
- 是否需要输出 token ids、原始序列或模型 batch。
- 下游模型是否为 Evo2 或其他基因组语言模型。

# outputs

```text
datapipe_choice:
  name: biology_genome_dataset
  action: reuse_basic_fasta | use_evo2_tokenizer | extend_adapter | reject

data_contract:
  sequence_type: DNA | RNA
  record_unit: fasta_record
  output_protocol: raw_sample | encoded_sequence | evo2_tokens

risk_flags:
  - pipeline_has_protein_semantics
  - evo2_adapter_missing
  - long_sequence_not_chunked
  - recursive_scan_missing
```

# procedure

1. 确认输入是否为 FASTA，且序列字母表符合 DNA/RNA。
2. 判断下游是否需要 Evo2 token batch；若需要，优先选择 Evo2 tokenizer。
3. 若只需轻量读取，使用 `GenomeDataset`。
4. 检查目录是否需要递归扫描。
5. 读取小样本确认 sequence、description、长度和编码结果。
6. 根据下游模型补充切窗、label、mask 或 adapter。

# constraints

- 不要把通用 `aatype` 输出直接当成 Evo2 batch。
- 不要假设该原语会自动完成长序列切分和 packing。
- 不要在 adapter 未注册时启用 `use_adapter=True`。
- 不要用该原语直接处理 VCF、BED、GFF 或多组学表格。

# next_phase_recommendation

- Evo2 推理：进入 Evo2 tokenizer 和 `SimpleFastaDataset`。
- Evo2 训练：进入 FASTA/JSON 预处理到 mmap dataset 的流程。
- 自定义基因组模型：新增 adapter，明确 token、mask、label 和切窗规则。
- 数据质控：补充序列长度分布、非法字符和重复 record 检查。

# fallback

- FASTA 解析失败：先标准化 header 和序列换行。
- 字母表不匹配：确认 DNA/RNA 类型并清理非法字符。
- 长序列内存过高：先做离线切窗或流式读取。
- Evo2 batch 不匹配：放弃通用 pipeline，使用 Evo2 专用数据入口。
