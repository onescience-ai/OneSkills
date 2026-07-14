# 阶段 5：推理代码生成

目标：生成与模型契约和数据契约一致、可复现的推理 pipeline。

## Codegen 输入

写代码前，先从 `infer_workdir` 中已保存的知识文件读取并汇总：

- `model_knowledge.md`
- 存在数据时的 `data_preparation_plan.md` 和 `data_manifest.json`
- `model_loading_plan.md`
- `inference_plan.md`
- 运行目标和硬件约束
- 必需输出和验证标准

非平凡代码生成或仓库编辑应使用 `onescience-coder`。交接内容必须自包含，包含路径、契约、参数默认值和阻塞项；在 infer -> coder 交接时，路径只用于追踪，供 coder 直接消费的知识必须同时以内容形式提供，不能只传文件路径。

## Pipeline 要求

生成的推理代码应支持：

- 对 config、checkpoint、input、output directory、device、dtype、batch size、seed 和领域参数提供显式 CLI 参数
- 在 `code_save_dir` 或项目原生目录下使用确定性的最终输出路径，并在 `infer_workdir` 中记录对应引用
- 结构化日志和机器可读的结果摘要
- 对缺失文件、格式错误输入、device 不匹配和无效输出给出清晰失败信息
- 除非用户明确要求，执行期间不要隐藏式下载

对于 HuggingFace 模型，若文档给出官方 API 模式，应使用该模式。对于仓库模型，复用官方 runner 或 datapipe 模块，不要重新实现内部逻辑。

## Infer -> Coder 交接

当将当前阶段交接给 `onescience-coder` 时，至少提供以下信息：

```text
infer_handoff=true
task_method=inference_codegen
infer_workdir=<code_save_dir>/.infer_work/<run_id>
code_save_dir=<用户代码保存目录>
model_knowledge_path=<infer_workdir>/model_knowledge.md
model_knowledge_content=<model_knowledge.md 全文或执行所需完整内容>
data_preparation_plan_path=<infer_workdir>/data_preparation_plan.md
data_preparation_plan_content=<可选，但只要下游需要就必须提供>
data_manifest_path=<infer_workdir>/data_manifest.json
data_manifest_content=<可选，但只要下游需要就必须提供>
model_loading_plan_path=<infer_workdir>/model_loading_plan.md
model_loading_plan_content=<可选，但只要下游需要就必须提供>
inference_plan_path=<infer_workdir>/inference_plan.md
inference_plan_content=<inference_plan.md 全文或执行所需完整内容>
required_outputs=<当前步骤要求输出>
validation_criteria=<当前步骤完成标准>
next_action=onescience-coder
```

具体代码生成前，必须先从 `infer_workdir` 中保存的知识文件读取，再组织交接内容。由于 `onescience-coder` 只允许直接消费 `reference_resources[*].content` 或资源技能返回内容，infer 交接给 coder 时必须同时传递 `*_path` 与 `*_content`；路径用于追踪与 provenance，内容用于直接消费。

## 输入输出适配器

将 adapter 与模型逻辑分离：

- 输入 adapter：把准备好的数据转换为模型 batch
- 输出 adapter：写出 tensor、NetCDF/Zarr/CSV/JSON/image 或模型原生产物
- 验证 adapter：读取输出，不需要重新运行推理

对于所有领域，尽可能在输出中保留可解释元数据，例如坐标、单位、样本 ID、结构 ID、参考版本、mesh/field 映射、时间轴或模型原生 metadata。

## 最小测试

生成代码时，至少生成一个静态测试或 smoke test：

- CLI help/import 测试
- Manifest shape 和文件存在性检查
- 可行时执行 tiny sample inference
- 输出 schema 验证

在测试或预检实际运行前，不要声称生成的 pipeline 可执行。
