# launch

MedGemma 是 OneScience `Module` 形式的医学生成模型，使用配置选择 vLLM 或 Transformers 后端。推理代码直接构造 `MedGemma` 并传入 OpenAI Chat Completion 风格的消息。

```sh
python -c "from onescience.models.medgemma.medgemma import MedGemma; import inspect; print(inspect.signature(MedGemma)); print(inspect.signature(MedGemma.forward)); print(inspect.signature(MedGemma.inference)); print(inspect.signature(MedGemma.predict_text)); print(inspect.signature(MedGemma.predict_multimodal))"
```

# input_schema

- `configs.model`：至少包含 `variant`、`is_multimodal`、`model_path`、`tokenizer_path`。
- `configs.inference`：包含 `use_vllm`、`gpu_memory_utilization`、`max_model_len`、`tensor_parallel_size`、`default_max_tokens`、`temperature`、`top_p`。
- `forward` 输入 `messages: list[dict]`，每项至少有 `role` 和 `content`；采样参数为 `max_tokens`、`temperature`、`top_p`、`n`。
- `inference` 接受含 `messages` 或 `instances` 的字典，并从可选 `parameters` 读取采样参数。
- 输出为模型运行器格式化的 Chat Completion 风格字典。

# runtime_interfaces

- `MedGemma(configs)`：完整模型封装并初始化运行后端。
- `MedGemma.forward(messages, max_tokens=None, temperature=0.7, top_p=0.9, n=1)`：生成入口。
- `MedGemma.inference(data)`：OneScience 统一字典接口。
- `MedGemma.predict_text(...)`、`predict_multimodal(...)`：简化任务接口。
- `VLLMModelRunner`、`TransformersModelRunner`：实际模型加载与生成后端。
- `MedGemmaPredictor.predict(...)`：消息转换与响应格式化。

# main_functions

- `MedGemma.forward`
- `MedGemma.inference`
- `MedGemma.predict_text`
- `MedGemma.predict_multimodal`
- `MedGemmaPredictor.predict`

# execution_resources

- 需要本地可读取的模型与 tokenizer；模型变体和 tokenizer 必须匹配。
- vLLM 后端适合 GPU 批量推理，Transformers 是兼容回退；大模型可能需要 tensor parallel。
- 调用方负责控制上下文长度、输出 token 数、显存利用率和结果持久化。

# operation_limits

- 模型生成内容不能替代医生诊断、治疗建议或临床复核。
- 当前源码的多模态路径并未完整实现，图像任务不能假定与文本路径具有相同可用性。
- `instances` 必须能被转换为消息；缺少 `messages` 和 `instances` 会抛出 `ValueError`。
- vLLM 初始化失败时会回退到 Transformers，吞吐量和显存行为会变化。
