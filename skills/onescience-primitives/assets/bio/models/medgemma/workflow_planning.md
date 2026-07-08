# description

MedGemma 的规划知识用于把医学文本问答、报告总结、医学考试评测、影像相关提示和批量医学样本推理任务转换为模型变体选择、配置加载、输入格式准备、推理执行和安全审查流程。

# when_to_use

- 用户需要医学文本问答、摘要、解释或报告辅助分析。
- 用户需要对 MedQA 等医学问答数据进行批量评测。
- 用户提供医学图像相关任务并明确需要 MedGemma，但应注意当前源码多模态实现限制。
- 当前 workflow 阶段是 `medical_text_inference`、`medical_qa` 或 `medical_report_assistance`。
- 不在蛋白结构生成、分子 docking、蛋白-配体打分任务中使用。

# inputs

- 任务类型：文本问答、报告总结、批量评测、交互问答或多模态医学图像任务。
- 模型资源：`model_path`、`tokenizer_path`、模型变体、是否使用 vLLM。
- 推理参数：max tokens、temperature、top_p、top_k、tensor parallel size。
- 数据输入：messages、text、question、JSON/JSONL 文件或图像信息。
- 安全约束：是否需要免责声明、人工复核和禁止临床决策自动化。

# outputs

- 召回决策：是否使用 MedGemma，以及选择 4B 多模态还是 27B 文本变体。
- 执行计划：配置文件、输入文件、输出目录和覆盖参数。
- 结果产物：OpenAI 兼容响应、单样本预测文件、汇总文件和错误日志。
- 下游交接：医学文本报告、评测表或人工复核队列。

# procedure

1. 判断任务是否属于医学文本或医学多模态理解。
2. 判断输入是否需要图像；若需要，确认当前源码多模态能力是否足够。
3. 选择模型变体：文本优先可选 27B，图像相关任务选择 4B。
4. 检查模型路径、tokenizer 路径、GPU 和 vLLM 可用性。
5. 准备输入 JSON/JSONL，确保每条样本包含 `messages`、`text` 或 `question`。
6. 设置推理参数，医疗场景优先使用较低温度和明确输出约束。
7. 运行文件推理或交互推理。
8. 检查错误目录、汇总结果和空响应。
9. 将输出交给人工医学审阅或评测脚本。

# constraints

- 不能把 MedGemma 输出作为自动临床诊断、处方或急救决策。
- 模型权重必须本地可用，不能只写模型名。
- 当前源码的图像推理未完整实现，规划多模态任务时必须标注风险。
- 输入中包含隐私医学数据时应遵守去标识化和访问控制要求。
- 评测任务应固定 seed、temperature 和版本，便于复现。

# next_phase_recommendation

- 医学问答结果应进入人工复核或基准评测统计。
- 报告总结任务应保留原文、提示词、模型版本和生成参数。
- 如果必须做医学图像推理，下一阶段应补全图像预处理和多模态 runner，再进行小样本验证。
- 对批量输出建立错误样本重试和低置信度人工检查机制。

# fallback

- vLLM 初始化失败：设置 `use_vllm=false` 或使用 Transformers 后端。
- 模型路径错误：检查本地权重目录和 tokenizer 文件。
- 显存不足：降低 max length、使用更小变体、降低并行 batch 或增加 tensor parallel。
- 多模态输出不可用：退回文本描述输入，或先实现图像 runner。
- JSON 输入无效：转换为包含 `messages`、`text` 或 `question` 的 JSONL。
