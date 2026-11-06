# 阶段 4：训练代码生成

目标：生成与训练契约、数据契约和 checkpoint 语义一致、可复现的训练 pipeline。

## Codegen 输入

写代码前，先从 `trainer_workdir` 中已保存的知识文件读取并汇总：

- `source_capture.md`
- `training_knowledge.md`
- `data_preparation_plan.md`
- `data_manifest.json`
- `training_plan.md`
- 运行目标和硬件约束
- 必需输出和验证标准

本阶段由 trainer 负责生成完整训练脚本内容与代码级契约，包括训练策略、数据配置、split 假设、loss、optimizer、scheduler、评测频率、checkpoint 策略、日志与验证要求。这里的“生成”指 trainer 先行定义脚本应包含的全部内容，而不是把这些内容再交给 `onescience-coder` 重新决定。仅当需要将这些已定义内容写入仓库、修改仓库现有文件、补齐最终文件路径或对接项目原生目录结构时，才使用 `onescience-coder`。交接包含当前步骤需要的路径、散列、契约、参数默认值和阻塞项；大文本保持为 trainer 任务产物，由 coder 在技能执行上下文按需读取并校验，不重复内嵌全文。

## Pipeline 要求

论文复现时，生成前将训练计划和代码配置逐字段对照上游规格，检查实验/阶段/更新对象和来源。
不得把未决值改成默认值，不得重新决定 split、网络拓扑、loss 或 best/last checkpoint 语义。
科学必需值缺失时保留显式必填配置和清晰错误，先实现已确定部分，返回 `partial` 与缺项，不能
将占位配置描述为可运行。若用户禁止训练，生成代码后只执行其允许的非训练检查。

生成的训练代码应支持：

- 对 config、checkpoint、train/val/test 数据、输出目录、device、dtype、batch size、seed 和领域参数提供显式 CLI 参数或配置项
- 明确区分从头训练、初始化权重、继续训练和微调的入口参数
- 在 `code_save_dir` 或项目原生目录下使用确定性的最终输出路径，并在 `trainer_workdir` 中记录对应引用
- 结构化日志和机器可读的结果摘要
- 对缺失文件、格式错误输入、device 不匹配、checkpoint 语义冲突和无效输出给出清晰失败信息
- 除非用户明确要求，执行期间不要隐藏式下载

对于已有项目原生训练入口的模型，应优先复用原生 trainer、config、dataset 或 runner，不要重新实现内部逻辑。

## Trainer -> Coder 落盘交接

对于来自 paper-repro 的任务，继续传递唯一规格的 `reproduction_spec_path`、
`reproduction_spec_sha256` 和作用范围明确的未决项；coder 在技能执行上下文读取并校验同一规格。
下述 trainer 派生任务书仅用于额外的训练落盘工作，不是 paper-repro 的交付前提，不能替代/改写上游规格，也不能因为缺少它而阻止论文代码
生成。所有既有执行授权、禁止训练和输出目录约束随 handoff 传递。

`onescience-coder` 在本阶段只负责把 trainer 已经定义完成的训练脚本内容物化为仓库文件，或对现有项目文件做对应修改；不负责重新决定训练脚本应包含的训练策略、数据语义、checkpoint 语义、日志策略和验证要求。


当需要将 trainer 已定义的训练内容落盘到仓库并交接给 `onescience-coder` 时，至少提供以下信息：

```text
trainer_handoff=true
task_method=training_codegen
trainer_workdir=<code_save_dir>/.trainer_work/<run_id>
code_save_dir=<用户代码保存目录>
source_capture_path=<trainer_workdir>/source_capture.md
source_capture_sha256=<文件 SHA-256>
training_knowledge_path=<trainer_workdir>/training_knowledge.md
training_knowledge_sha256=<文件 SHA-256>
data_preparation_plan_path=<trainer_workdir>/data_preparation_plan.md
data_preparation_plan_sha256=<文件存在且下游需要时提供>
data_manifest_path=<trainer_workdir>/data_manifest.json
data_manifest_sha256=<文件存在且下游需要时提供>
training_plan_path=<trainer_workdir>/training_plan.md
training_plan_sha256=<文件 SHA-256>
task_description_path=<trainer_workdir>/coder_task_description.md
task_description_sha256=<文件 SHA-256>
required_outputs=<当前步骤要求输出>
validation_criteria=<当前步骤完成标准>
coder_static_review_required=true
next_action=onescience-coder
```

具体代码生成前，必须先从 `trainer_workdir` 中保存的知识文件读取，再由 trainer 明确训练核心逻辑与文件级契约后组织交接内容。训练策略、数据配置、loss、optimizer、scheduler、eval/checkpoint cadence、日志与验证要求必须先由 trainer 明确给出；`onescience-coder` 不负责补全这些核心训练决策，只负责按 trainer 契约写入仓库并做静态对齐。trainer 交接给 coder 时传递执行所需任务产物的 `*_path` 与 `*_sha256`，由 coder 在技能执行上下文按需读取；resource skill 的 assets 仍只能通过资源结果消费。

## 任务描述要求

`coder_task_description.md` 必须是自包含落盘任务书，不得写“详见 training_plan.md”或“请再读取其它文件”。它承接 trainer 已明确的训练内容，不承担补全核心训练逻辑的职责。至少应覆盖：

- 训练任务概述
- 数据来源、split、schema、变量和 shape
- 模型入口、训练入口和需要复用/修改的位置
- checkpoint 语义与初始化策略
- loss、optimizer、scheduler、batch、precision、distributed 约束
- 预期代码文件结构
- checkpoint、日志、评估、结果保存和静态 review 要求
- 所有 `MISSING:`、`INFERRED:` 和 `ASSUMPTION:` 项

## 最小测试

生成代码时，至少生成一个静态测试或 smoke test：

- CLI help/import 测试
- 配置解析和 manifest shape 检查
- checkpoint 参数语义检查
- 用户允许训练且科学必需配置齐备时才执行 tiny batch 训练或训练 dry-run；禁止训练时不执行
- 输出 schema 验证

在测试或预检实际运行前，不要声称生成的训练 pipeline 可执行。

codegen 阶段允许生成静态检查脚本、CLI/help/import 测试、配置校验辅助物、启动脚本、runtime request / manifest 等静态产物；但禁止预创建最终运行证据文件，例如 `trainer.log`、`train.log`、`metrics.json`、`metrics.jsonl`、`predictions.json`、`targets.json`、checkpoint 指标摘要等。

若生成 dry-run、tiny-batch 或 internal validation 辅助文件，必须明确标识其用途，不得复用正式训练 / 推理 / 评测运行证据文件名，也不得把这些辅助产物伪装成真实执行结果。
