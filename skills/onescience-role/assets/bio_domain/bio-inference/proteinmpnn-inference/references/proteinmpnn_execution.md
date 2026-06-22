# ProteinMPNN 执行要点

入口 `protein_mpnn_run.py` 支持 PDB 输入、JSONL 批量输入、fixed chains、fixed positions、tied positions、PSSM、bias、omit AA、score-only 和 probability 输出。

关键风险：

- PDB backbone 原子顺序和缺失会影响几何特征。
- 设计链控制应通过 helper JSON 或 `pdb_path_chains`，不要改模型 forward。
- `model_name` 与权重目录要一致，CA-only 模式必须使用 CA-only 权重。
- 输出 FASTA/score/probability 要和设计约束逐项核对。
