# AF2 / OpenFold 推理执行要点

## AlphaFold

使用 `examples/biosciences/alphafold/run_alphafold.py`。关键参数是 FASTA、`model_preset`、`db_preset`、`max_template_date`、model/data/output 目录。JAX 参数、MSA/template 数据库和外部搜索工具是主要运行风险。

## OpenFold

使用 `examples/biosciences/openfold/run_pretrained_openfold.py`。它是 PyTorch/OpenFold 协议，batch 字段最后一维常带 recycling 维。不要把 AF2 JAX feature pickle 当作无需检查的 OpenFold batch。

## 输出检查

- 至少有 ranked PDB 或 predicted PDB。
- 有 ranking/confidence 文件或可追溯日志。
- PDB 链数和 FASTA 链数一致。
- 残基数与输入序列合理对应，缺失残基要解释。
