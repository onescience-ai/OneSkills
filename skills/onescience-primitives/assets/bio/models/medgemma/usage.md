# launch

文件批量推理示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/medgemma/runner/medical_inference_runner.py --config examples/biosciences/medgemma/configs/inference_config.yaml --input "$RUN_DIR/medgemma_input.jsonl" --model_path "$ONESCIENCE_DATASETS_DIR/medgemma/modelscope/google/medgemma-1.5-4b-it" --dump_dir "$RUN_DIR/medgemma_predictions"
```

交互式推理示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/medgemma/runner/medical_inference_runner.py --config examples/biosciences/medgemma/configs/inference_config.yaml --interactive --model_path "$ONESCIENCE_DATASETS_DIR/medgemma/modelscope/google/medgemma-1.5-4b-it" --dump_dir "$RUN_DIR/medgemma_predictions"
```

Python API 示例：

```python
from onescience.models.medgemma.medgemma import MedGemma

model = MedGemma(configs)
result = model.inference({
    "messages": [{"role": "user", "content": "请总结这段医学文本的关键信息。"}],
    "parameters": {"max_tokens": 500, "temperature": 0.7, "top_p": 0.9, "n": 1},
})
```

# input_schema

- CLI 参数：
  - `--config`: 配置文件路径，必需
  - `--input`: JSON/JSONL 输入文件路径
  - `--interactive`: 交互模式开关
  - `--model_path`: 覆盖配置中的模型路径
  - `--dump_dir`: 覆盖配置中的输出目录
- 配置默认参数：
  - `seed=42`
  - `eval_only=true`
  - `model.variant=4b`
  - `model.tokenizer_path=null`
  - `model.prompt_format=chat`
  - `model.is_multimodal=true`
  - `inference.gpu_memory_utilization=0.9`
  - `inference.max_model_len=null`
  - `inference.tensor_parallel_size=1`
  - `inference.default_max_tokens=500`
  - `inference.temperature=0.7`
  - `inference.top_p=0.9`
  - `inference.batch_size=1`
  - `inference.use_vllm=true`
  - `output.output_format=json`
- JSON/JSONL 样本字段：
  - `messages`: Chat messages
  - `text`: 单轮文本输入
  - `question`: 问题文本
  - `id`: 可选样本 ID

# runtime_interfaces

- `MedGemma.forward`: 以 messages 和采样参数执行生成。
- `MedGemma.inference`: OneScience 兼容推理入口，支持 `messages` 或 `instances`。
- `MedGemma.predict_text`: 简化文本推理入口。
- `MedGemma.predict_multimodal`: 多模态入口，目前图像推理未完整实现。
- `MedGemmaPredictor.predict`: prompt 转换、runner 调用和响应格式化入口。
- `VLLMModelRunner.generate`: vLLM 生成入口。
- `TransformersModelRunner.generate`: Transformers 回退生成入口。
- `MedicalInferenceRunner.run_from_file`: JSON/JSONL 批量推理入口。

# main_functions

- `forward`
- `inference`
- `predict_text`
- `predict_multimodal`
- `predict`
- `generate`
- `run_from_file`

# execution_resources

- 4B 模型通常需要 GPU；27B 文本模型需要更高显存或张量并行。
- vLLM 后端需要安装 vLLM 并有兼容模型格式。
- Transformers 后端需要模型和 tokenizer 可由本地路径加载。
- 输出目录必须可写，文件推理会保存单样本结果、汇总和错误记录。
- 医学图像任务还需要图像文件、图像预处理和多模态 prompt 支持；当前源码仅提供部分接口。

# operation_limits

- 生成内容不能替代医生诊断或治疗建议。
- 当前多模态图像推理在源码中未完整接入，实际会退化为文本推理。
- JSON/JSONL 输入缺少有效字段时不会产生预测。
- `use_vllm=true` 但 vLLM 不可用时会回退到 Transformers，性能可能明显下降。
- 模型路径、tokenizer 路径和配置变体必须一致。
