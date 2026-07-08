# launch

Python API 示例：

```sh
python -c "from types import SimpleNamespace; from onescience.datapipes.biology.dataloader import get_genome_dataloader; extra=SimpleNamespace(sequence_type='DNA',use_pipeline=False,use_adapter=False,model_name='none',use_msa=False); data=SimpleNamespace(extra=extra); source=SimpleNamespace(path='/path/to/genome.fa'); cfg=SimpleNamespace(source=source,data=data,num_workers=0); loader=get_genome_dataloader(cfg); print(next(iter(loader)))"
```

# input_schema

```text
必备:
  source.path: FASTA 文件或包含 FASTA 的目录

可选:
  data.extra.sequence_type: DNA 或 RNA
  data.extra.use_pipeline: 是否输出统一 pipeline 特征
  data.extra.use_adapter: 是否调用 adapter
  data.extra.model_name: adapter 名称
  num_workers: DataLoader worker 数
```

# runtime_interfaces

- `get_genome_dataloader(configs)`: 构建 genome DataLoader。
- `GenomeDataset(configs)`: 读取 FASTA 并形成 genome 样本。
- `NucleotideEncoder(sequence_type)`: 提供 DNA/RNA 编码与解码。

# main_functions

- `get_genome_dataloader`
- `encode`
- `decode`
- `__getitem__`

# execution_resources

- FASTA 读取和核苷酸编码主要在 CPU 上完成。
- 大基因组 FASTA 会带来较高内存和 I/O 压力。
- Evo2 路径需要额外准备模型 tokenizer 和长序列数据预处理环境。

# operation_limits

- 只适合基础 FASTA 读取和轻量编码。
- 不直接完成 Evo2 预训练或微调数据格式。
- 不处理 BED/GFF 注释、变异文件、基因区域切窗或样本标签。
- 若目录中 FASTA 层级较深，需要先展平或扩展扫描逻辑。
