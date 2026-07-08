# launch

AlphaFold 通过示例脚本启动，常见模式是先准备数据库、参数目录、FASTA 和输出目录，再选择 monomer 或 multimer preset。

```sh
python onescience/examples/biosciences/alphafold/run_alphafold.py --fasta_paths onescience/examples/biosciences/alphafold/fasta/af2-monomer-protein.fasta --output_dir ./outputs/alphafold --data_dir ${AF2_DATA_DIR} --model_preset monomer --db_preset reduced_dbs --max_template_date 2024-01-01
```

# input_schema

- 必需输入: FASTA 文件、AlphaFold 参数目录、数据库根目录、输出目录。
- 常用参数:
  - `--fasta_paths`: 单个或多个 FASTA 路径。
  - `--output_dir`: 预测产物目录。
  - `--data_dir`: 数据库根目录。
  - `--model_preset`: 默认按任务选择，单体常用 `monomer`，复合物用 `multimer`。
  - `--db_preset`: 资源受限时可用 `reduced_dbs`，完整检索用 `full_dbs`。
  - `--max_template_date`: 必须显式给定，避免模板泄漏。
- 输入 FASTA 的链组织必须和 preset 匹配，multimer 应走 multimer pipeline。

# runtime_interfaces

- `run_alphafold.py`: 端到端推理入口。
- `DataPipeline`: 单体 MSA 与 template 特征构造。
- `DataPipelineMultimer`: 多链特征构造、MSA pairing 与 chain merge。
- `RunModel.process_features`: 把 raw feature dict 转成模型输入。
- `RunModel.predict`: 执行模型推理并返回结果字典。
- `AmberRelaxation`: 可选结构松弛接口。

# main_functions

- `predict_structure`
- `process_features`
- `predict`
- `get_confidence_metrics`
- `make_sequence_features`
- `make_msa_features`

# execution_resources

- 需要 JAX/Haiku、HH-suite/HMMER/Kalign 等外部搜索工具和 AlphaFold 数据库。
- GPU 推理推荐使用；长序列、multimer 和完整数据库检索会显著增加 CPU、内存和磁盘开销。
- 数据库检索阶段依赖大量本地文件和可执行程序，轻量环境中不要默认运行。

# operation_limits

- 不支持 DNA/RNA 或小分子复合物的 AF3-style 输入。
- 不适合作为 OneScience `One*` wrapper 组件直接改造。
- MSA 和 template 缺失会降低结果质量或导致 pipeline 失败。
- `max_template_date`、数据库版本和参数版本会影响可复现性。
