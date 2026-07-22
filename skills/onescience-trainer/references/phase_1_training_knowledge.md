# 阶段 1：训练知识整理

目标：在编码或运行前，建立有来源、无臆造的训练理解。

## 阶段资源评估

进入本阶段前，必须基于阶段 0 的资源使用记录和 `workflow_contract.md` 的初始召回结果，评估已召回资源是否足以建立训练知识。

- 从已召回资源中筛选能支撑模型身份、训练入口、配置语义、checkpoint 语义、数据契约、loss/optimizer/scheduler 和验证线索的资源。
- 若资源只覆盖输入获取但不足以解释训练契约，应按“训练知识整理”目标再次调用 `type=resource` 技能补充训练规格知识、使用知识和规划决策知识。
- 补充召回时应带上阶段 0 已确认事实与缺口，避免泛化搜索。
- 不得沿资源 `path` 直接读取资源文件来补洞；只能使用资源技能返回的 `content`、用户明确提供内容或上游已展开内容。
- 在 `training_knowledge.md` 中记录资源名称、用途、限制、冲突、补召回结果和仍为 `MISSING:` 的知识。

## 来源顺序

1. 阶段 0 输出的 `source_capture.md` 和 `training_request.json`
2. 初始与阶段补召回的 `type=resource` 资源内容
3. 用户提供的文件、路径、模型目录、训练脚本和指令
4. 项目 README、训练文档、示例、配置文件和 package 文档
5. checkpoint 元数据、文件名、配置快照、日志目录、历史训练说明
6. 仅在缺少一手来源或用户明确要求时，使用论文或第三方示例

当来源来自在线内容或可能随版本变化时，依赖之前必须确认当前内容。

## 抽取内容

将 `training_knowledge.md` 保存到 `trainer_workdir`，并把它作为后续 codegen 与 execution 阶段读取的权威知识文件。在 `training_knowledge.md` 中记录以下字段：

- 任务身份：名称、来源、任务族、训练目标、输出目标
- 模型身份：代码路径、模块/类、训练入口、配置入口、license
- 权重语义：从头训练、初始化权重、继续训练、微调、是否恢复 optimizer/scheduler state
- 必需配置：文件名、必需 key、默认值、override、日志和 checkpoint 路径约束
- 数据契约：样本来源、字段、shape、单位、split、标签、mask、归一化、增强、collate
- 训练契约：loss、optimizer、scheduler、batch 语义、precision、梯度裁剪、累计步数、分布式需求
- 运行假设：CPU/GPU/CUDA 版本、内存、加速后端、依赖包、远程执行需求
- 验证线索：预期日志、checkpoint 命名、关键指标、早停或 best model 规则

来源中不存在的事实使用 `MISSING:`。只有必须设置默认值才能继续时，才使用 `ASSUMPTION:`，并标明后续如何验证。

## 继续训练与微调判定

必须显式区分以下语义：

- `train_from_scratch`：无外部权重或只使用随机初始化
- `init_from_checkpoint`：只加载模型权重，不恢复训练状态
- `resume_training`：恢复模型、optimizer、scheduler、global step 和相关状态
- `finetune`：加载预训练权重，并可能冻结部分模块、替换 head 或调整学习率策略

如果用户说明与现有脚本语义冲突，以用户说明优先，并把冲突写入 `training_knowledge.md`。

## 决策门

在已知最小训练契约之前，不要进入训练策略规划或代码生成：

- 如何实例化模型或训练 runner
- checkpoint 是初始化、resume 还是微调输入
- 最小训练数据格式和目标标签
- 至少一个可执行的训练目标和验证线索

如果训练知识不足，返回阻塞状态，并要求用户提供模型目录、训练脚本、配置、checkpoint 路径或训练说明。
