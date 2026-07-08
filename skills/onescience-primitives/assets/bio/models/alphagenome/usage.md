# launch

AlphaGenome 提供推理、变异评分、轨迹评估和微调四类示例入口。

```sh
python onescience/examples/biosciences/alphagenome/run_inference.py --fasta_path ${DATA_ROOT_DIR}/reference/HOMO_SAPIENS/GRCh38.p13.genome.fa --model_dir ${MODEL_ROOT_DIR}/alphagenome-all-folds --chromosome chr19 --start 10587331 --end 11635907 --output_dir ./outputs/alphagenome --organism HOMO_SAPIENS --model_version FOLD_0
```

```sh
python onescience/examples/biosciences/alphagenome/run_variant_scoring.py --fasta_path ${DATA_ROOT_DIR}/reference/HOMO_SAPIENS/GRCh38.p13.genome.fa --model_dir ${MODEL_ROOT_DIR}/alphagenome-all-folds --vcf_path ./variants.vcf --output_dir ./outputs/alphagenome_variant --organism HOMO_SAPIENS --model_version all_folds
```

# input_schema

- 推理默认参数:
  - `--chromosome`: 默认 `chr1`。
  - `--start`: 默认 `1000000`。
  - `--end`: 默认 `2048576`。
  - `--output_dir`: 默认 `./outputs`。
  - `--organism`: 默认 `HOMO_SAPIENS`。
  - `--model_version`: 推理示例默认 `FOLD_0`。
- 变异评分默认参数:
  - `--vcf_path`: 未提供时使用内置演示变异。
  - `--model_version`: 示例默认 `all_folds`。
- 轨迹评估默认参数:
  - `--model_version`: 默认 `FOLD_0`。
  - `--allow_download`: 默认 `False`。
  - `--bundles`: 未指定时评估所有支持数据束。
- 微调默认参数:
  - `--num_steps=1000`。
  - `--batch_size=2`。
  - `--learning_rate=1e-5`。
  - `--log_every=50`。
  - `--save_every=200`。

# runtime_interfaces

- `run_inference.py`: genomic interval 推理。
- `run_variant_scoring.py`: SNV/VCF 变异效应评分。
- `run_track_prediction_eval.py`: 官方验证集轨迹预测评估。
- `run_finetuning.py`: 自定义 regions + BigWig 微调。
- `AlphaGenomeModel.predict_interval`: SDK 区间预测。
- `AlphaGenomeModel.predict_variant`: reference/alternate 输出。
- `AlphaGenomeModel.score_variant`: 返回变异评分表。
- `get_numpy_dataset_iterator`: 数据集迭代器。

# main_functions

- `predict_interval`
- `predict_variant`
- `score_variant`
- `get_recommended_scorers`
- `get_dataset_iterator`
- `get_forward_fn`
- `get_train_step`
- `create_from_kaggle`
- `create_from_huggingface`

# execution_resources

- 需要 JAX/Haiku、Orbax checkpoint、参考 FASTA 与索引、模型权重。
- 从 Kaggle 或 HuggingFace 加载权重需要网络和对应凭据；离线环境应提供 `model_dir`。
- 1 Mbp 窗口和 all-folds 推理对显存、内存和 checkpoint 读取带宽要求较高。
- 微调需要 BigWig 读取依赖和区域表。

# operation_limits

- 不支持蛋白结构预测、分子 docking 或小分子生成。
- 参考等位基因与 FASTA 不一致时，变异评分应停止并修正输入。
- 坐标必须遵循脚本约定的 0-based interval。
- 小鼠和人类模型、参考基因组、metadata 不应混用。
