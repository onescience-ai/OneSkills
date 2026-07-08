# launch

AlphaFold3 通过 JSON 输入和示例脚本启动，可以分别控制 data pipeline 和 inference。

```sh
python onescience/examples/biosciences/alphafold3/run_alphafold.py --json_path onescience/examples/biosciences/alphafold3/inputs/7r6r_data.json --model_dir ${AF3_MODEL_DIR} --output_dir ./outputs/alphafold3 --run_data_pipeline=true --run_inference=true --flash_attention_implementation=xla --num_recycles=10 --num_diffusion_samples=5
```

# input_schema

- 必需输入: AF3 JSON、模型参数目录、输出目录。
- 常用参数:
  - `--json_path`: 单个 JSON 输入。
  - `--input_dir`: 批量 JSON 输入目录。
  - `--run_data_pipeline`: 默认按输入是否已有特征决定；已有 MSA/template 时可关闭。
  - `--run_inference`: 只做数据搜索时可关闭。
  - `--flash_attention_implementation`: 兼容优先可用 `xla`。
  - `--num_recycles`: 常见默认 `10`。
  - `--num_diffusion_samples`: 常见默认 `5`。
- JSON 可描述蛋白、RNA、DNA、配体、离子、用户 CCD、模板、MSA 和 bonds。

# runtime_interfaces

- `run_alphafold.py`: 端到端推理入口。
- `make_model_config`: 构建模型配置。
- `ModelRunner`: 加载参数并执行推理。
- `process_fold_input`: 执行 data pipeline 和 featurisation。
- `predict_structure`: 针对 fold input 生成结构样本。
- `write_outputs`: 写出结构、置信度和可选 embedding/distogram。

# main_functions

- `make_model_config`
- `predict_structure`
- `write_fold_input_json`
- `write_outputs`
- `process_fold_input`
- `post_process_inference_result`
- `write_output`

# execution_resources

- 需要 JAX/Haiku、模型参数、数据库、MSA 搜索工具、CCD/RDKit 相关资源。
- GPU 推理推荐使用；不同 flash attention 实现对 GPU、CUDA/cuDNN/Triton 兼容性要求不同。
- data pipeline 可能大量占用 CPU、磁盘 I/O 和数据库读取。

# operation_limits

- 不应把 Protenix 的 PyTorch feature dict 直接喂给 AlphaFold3 JAX 模型。
- pair embeddings 体积随 `N_token^2` 增长，保存时要评估磁盘与内存。
- 配体和自定义 CCD 输入需要化学组件定义一致。
- 模型权重和结果使用条款需由用户确认。
