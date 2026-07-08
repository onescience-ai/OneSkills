# component_info

MedGemma 是医学大语言模型封装组件，提供 OneScience `Module` 统一接口、OpenAI Chat Completion 风格响应、文件批量推理和交互式推理；源码本身不实现底层 Gemma 网络结构，而是负责加载外部 MedGemma 权重并管理 vLLM/Transformers 推理后端。

# architecture_overview

MedGemma 的源码架构由三层组成：

- `MedGemma`: OneScience 模型入口，读取配置并选择推理后端
- `VLLMModelRunner` / `TransformersModelRunner`: 底层生成引擎
- `MedGemmaPredictor`: 将消息转换为 prompt，并把生成结果整理为 OpenAI 兼容响应

模型变体由配置控制：

- `4b`: 多模态模型，面向文本和医学图像
- `27b`: 纯文本模型，面向医学文本理解与问答

当前源码中的 `predict_with_images` 仍是占位实现，会记录警告并暂时回退到文本推理。

# parameter_scale

- 支持变体：
  - `model.variant=4b`
  - `model.variant=27b`
- 默认推理参数：
  - `default_max_tokens=500`
  - `temperature=0.7`
  - `top_p=0.9`
  - `tensor_parallel_size=1`
  - `gpu_memory_utilization=0.9`
  - `batch_size=1`
  - `num_workers=0`
  - `use_vllm=true`
- 图像输入默认尺寸：
  - `image_input_width=224`
  - `image_input_height=224`

# architecture_structure

配置加载
  inference_config.yaml
    -> load_config / parse_configs
    -> configs.model
    -> configs.inference
    -> configs.output

模型初始化
  MedGemma(configs)
    -> _init_model_runner
      -> VLLMModelRunner if use_vllm
      -> TransformersModelRunner fallback
    -> MedGemmaPredictor

推理路径
  messages
    -> _messages_to_prompt
    -> model_runner.generate
    -> _format_openai_response
    -> choices / usage

文件推理
  JSON/JSONL samples
    -> text/question/messages
    -> predict
    -> per-sample result
    -> summary output

# input_schema

- 配置输入：
  - `model.variant`: `4b` 或 `27b`
  - `model.model_path`: 本地模型权重路径
  - `model.tokenizer_path`: 可选 tokenizer 路径，默认同模型路径
  - `model.is_multimodal`: 是否按多模态模型处理
  - `inference.use_vllm`: 是否优先使用 vLLM
  - `output.dump_dir`: 输出目录
- API 输入：
  - `messages`: `[{ "role": "user", "content": "..." }]`
  - `instances`: 可包含 `role/content`、`text` 或 `question`
  - `parameters`: 可包含 `max_tokens`、`temperature`、`top_p`、`n`
- 文件输入：
  - JSON 或 JSONL
  - 每条样本可包含 `messages`、`text`、`question`、`id`
- 多模态输入：
  - `text`
  - `images`
  - 当前源码中图像路径未完整接入底层多模态推理

# output_schema

- OpenAI 兼容响应：
  - `id`
  - `object=chat.completion`
  - `created`
  - `model`
  - `choices`
  - `usage`
- `choices` 内部字段：
  - `index`
  - `message.role=assistant`
  - `message.content`
  - `finish_reason`
- 文件推理输出：
  - 单样本预测 JSON
  - 汇总结果
  - 错误样本记录

# shape_transformations

文本消息
  messages: List[Dict]
    -> prompt string
    -> tokenizer/model_runner
    -> generated text
    -> OpenAI response

vLLM runner
  prompts: List[str]
    -> SamplingParams
    -> outputs per prompt
    -> text/token_ids/logprob/finish_reason

Transformers runner
  prompt
    -> tokenizer tensors
    -> model.generate
    -> decoded text
    -> normalized outputs list

文件批处理
  JSON/JSONL samples
    -> per-sample messages
    -> per-sample response
    -> saved predictions

# key_dependencies

- `MedGemma`
- `MedGemmaPredictor`
- `VLLMModelRunner`
- `TransformersModelRunner`
- `MedicalInferenceRunner`
- `parse_configs`
- `load_config`
- external MedGemma model weights
- tokenizer assets

# common_modification_points

- 推理吞吐优先调整 `use_vllm`、`tensor_parallel_size`、`gpu_memory_utilization` 和 `max_model_len`。
- 需要纯文本稳定性时可设置 `use_vllm=false` 使用 Transformers 后端。
- 需要控制回答长度和随机性时调整 `default_max_tokens`、`temperature`、`top_p`、`top_k`。
- 需要批量文件推理时使用 JSONL 输入并设置输出目录。
- 需要真正多模态医学图像推理时，应补全 `predict_with_images` 的图像预处理和底层 runner 多模态 prompt 格式。

# implementation_risks

- `model_path` 必须指向本地可加载的 MedGemma 权重，否则初始化失败。
- vLLM 不可用或不兼容时会回退 Transformers，但显存和性能特征会变化。
- 当前多模态接口未完整实现，传入图像时会警告并按文本路径处理。
- 医学输出不能直接作为临床诊断结论，必须有人类专业人员复核。
- Transformers runner 使用 `device_map=device`，不同 transformers 版本可能对该参数接受形式不同。
- 输入 JSON/JSONL 缺少 `messages`、`text` 或 `question` 时会被跳过或记录错误。

# code_references

- `{onescience_path}/onescience/src/onescience/models/medgemma`
