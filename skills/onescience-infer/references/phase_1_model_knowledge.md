# 阶段 1：模型知识获取

目标：在编码或运行前，建立有来源、无臆造的模型理解。

## 来源顺序

1. 用户提供的文件、路径、模型 ID 和指令
2. HuggingFace model card 和模型文件
3. 官方 README、推理文档、示例和 package 文档
4. 配置文件，例如 `config.json`、Hydra 配置、YAML 配置、tokenizer 或 processor 配置，以及模型专用元数据
5. Checkpoint 元数据、文件名、revision、safetensors index 文件、shard map 和 license 说明
6. 仅在缺少一手来源或用户明确要求时，使用论文或第三方示例

当来源来自在线内容或可能随版本变化时，依赖之前必须确认当前内容。

## 抽取内容

将 `model_knowledge.md` 保存到 `infer_workdir`，并把它作为后续 codegen 与 execution 阶段读取的权威知识文件。在 `model_knowledge.md` 中记录以下字段：
- 模型身份：名称、来源、revision、license、任务族
- 入口：package、class、pipeline API、CLI 或仓库 runner
- 必需配置：文件名、必需 key、默认值、override
- 必需权重：checkpoint 名称、sharding、precision、device 预期
- 输入契约：文件格式、tensor、变量名、shape、单位、网格、时间轴、mask
- 输出契约：字段、shape、单位、时间轴、坐标、文件格式
- 预处理：归一化、transform、重网格化、插值、padding、tokenization、batching
- 运行假设：CPU/GPU/CUDA 版本、内存、precision、分布式需求
- 验证线索：示例、期望输出、baseline metric、已知 smoke test

来源中不存在的事实使用 `MISSING:`。只有必须设置默认值才能继续时，才使用 `ASSUMPTION:`，并标明后续如何验证。

## 决策门

在已知最小模型契约之前，不要进入模型加载或代码生成：

- 如何实例化模型或 runner
- 配置和权重从哪里来
- 最小输入格式和输出格式
- 执行设备需求

如果模型信息不足，返回阻塞状态，并要求用户提供模型 ID、仓库、checkpoint 路径或文档。
