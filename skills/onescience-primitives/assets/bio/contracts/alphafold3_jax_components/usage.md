# launch

```sh
python {onescience_path}/onescience/examples/biosciences/alphafold3/run_alphafold.py --json_path input.json --output_dir outputs/alphafold3 --run_data_pipeline false --flash_attention_implementation xla --num_diffusion_samples 5 --num_recycles 10
```

# input_schema

输入可以是 AF3 folding JSON 或 input directory。已有特征推理时可设置 `--run_data_pipeline false`；需要 MMseqs 搜索时可配置 `--use_mmseqs true`。模型 batch 需要 token features、MSA、template、reference structure、atom cross attention 与 bond layout。

# runtime_interfaces

- `process_fold_input`: 读取并处理 folding input。
- `ModelRunner.run_inference`: 执行模型推理。
- `predict_structure`: 编排数据处理、模型推理和结果写出。
- `Model.get_inference_result`: 将 dense atom layout 映射回输出结构。

# main_functions

- `process_fold_input`
- `run_inference`
- `predict_structure`
- `__call__`
- `sample`
- `get_inference_result`

# execution_resources

需要 JAX/Haiku、AF3 参数、可用的注意力实现、可选数据库和 MSA/template 工具。CPU 数据管线和 diffusion 多样本推理都会增加运行资源需求。

# operation_limits

`contract_only` 表示不可假设 `OnePairformer(style="AlphaFold3JAXPairformer")` 当前可运行。AF3 JAX 与 Protenix feature dict 不兼容；confidence head 是对 diffusion samples 的评估，不能只取第一个 sample 当最终 ranking。
