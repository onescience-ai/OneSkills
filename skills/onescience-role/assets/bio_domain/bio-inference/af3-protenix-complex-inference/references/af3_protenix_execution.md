# AF3 / Protenix 推理执行要点

## AlphaFold3

入口是 `examples/biosciences/alphafold3/run_alphafold.py`。关键参数包括 `--json_path` 或 `--input_dir`、`--model_dir`、`--output_dir`、`--run_data_pipeline`、`--run_inference`、`--flash_attention_implementation`、`--num_recycles`、`--num_diffusion_samples`。

保守兼容时优先使用 `xla` attention fallback。数据 pipeline 会触发 MSA/template 搜索和较重 CPU/数据库需求。

## Protenix

统一入口是 `examples/biosciences/protenix/runner/inference_unified.py`。常用参数包括 `--input_json_path`、`--load_checkpoint_path`、`--dump_dir`、`--dtype bf16`、`--model.N_cycle`、`--sample_diffusion.N_sample`、`--sample_diffusion.N_step`、`--use_msa`。

## 输出检查

AF3/Protenix 输出必须能追溯结构文件、confidence、ranking/summary 信息和输入实体。配体或核酸任务要检查实体数、原子数和 bond/CCD 相关告警。
