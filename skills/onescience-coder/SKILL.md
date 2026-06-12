---
name: onescience-coder
description: 面向 OneScience 代码库的实现技能。用于用户已进入实现阶段时分析可行性、选择最小改造路径，并按需完成 DataPipe、模型、组件或配置相关代码实现；代码生成完成后必须执行静态需求一致性 review，逐条核对生成代码是否满足参数、结构、输入输出、组件复用和文件落点等要求，并根据 review 反馈回改代码。若用户只是询问技能路线、规划路径、先不要写代码或尚未授权实现，应先进入 onescience-workflow / onescience-role，而不是直接触发本 skill。
---

# OneScience 代码实现

## 入口边界

如果用户只是要求“只告诉我技能路线”“先不要写代码”“先做规划”“先看怎么走”，或当前请求尚未授权实现代码，本 skill 不应继续做 DataPipe、模型或配置方案设计。

此时应返回上游路由语义：

- 当前应先进入 `onescience-workflow`
- 若已识别领域与任务类型，下一跳应进入 `onescience-role`
- `onescience-coder` 只能作为未来执行入口，不是当前下一跳

不要在这种情况下读取 datapipe / model / contract 卡片，也不要输出实现策略、文件落点或测试计划。

## 工作顺序

1. 如果上游已提供代码生成交接摘要，则先把它作为只读输入；不要在本 skill 内重新处理硬件探测逻辑。
2. 如果交接摘要中包含 `paper_repro_handoff=true`、`task_method=paper2code` 或 `domain_task_family=paper-reproduction`，只把 `task_description_content` 或 `task_description_path` 指向的 `coder_task_description.md` 作为论文复现编码任务输入；不要再读取 `reproduction_spec.md` 来补齐任务细节。若 `coder_task_description.md` 明显缺少实现必需信息，应报告任务描述不完整并要求上游重新生成，而不是自行综合两份文档。
3. 如果交接摘要中包含 `coder_reference_mode=assets_only`，不要读取 `./references/workflow.md`，直接按交接摘要和 `coder_task_description.md` 读取 `./assets/` 下的模型卡、数据卡和组件契约。
4. 如果没有 `assets_only` 约束，再读 `./references/workflow.md`，理解 OneScience 的整体实现路径。
5. 复述任务，明确是数据、模型、组件还是配置问题。
6. 判断是否能直接复用现有实现；不能复用时，给出最小改造路径。
7. 只读取与当前任务直接相关的资料，再开始实现。
8. 代码生成完成后，必须执行一次静态需求一致性 review；若发现代码与需求不一致，先调整代码，再复查并输出 review 结论。

## 按需读取的资料

- 使用当前技能时，首先记录当前技能所在上层目录的绝对路径，并使用 `{onescience_path}` 变量指代，后续使用卡片时，若需要该路径则相应替换
- 做方案设计时，再读 `./references/first_round_guide.md`
- 开始实现前，再读 `./references/second_round_guide.md`
- 需要选模型时，先读 `./assets/models/model_index.md`
- 需要选 DataPipe 时，先读 `./assets/datapipes/datapipe_index.md`
- 需要选组件契约时，先读 `./assets/contracts/component_index.md`
- 上游交接 `tool_family=single-cell`、AnnData、Scanpy 或 scvi-tools 时，按需使用 `./assets/bio_single_cell_tools/` 下的脚本资产；这些是实现层资产，不从 `onescience-role/bio_domain/.../scripts` 读取新入口
- 上游交接 bulk RNA-seq、variant calling、long-read、functional genomics screen、post-transcriptional regulation 或 protein design validation workflow 时，按需使用 `./assets/bio_workflow_templates/`
- 上游交接 OneScience 生信模型训练、微调、模块修改、batch 协议或 datapipe adapter 任务时，按需使用 `./assets/bio_model_templates/` 下的 handoff 模板
- 上游交接 CRISPR guide、primer/probe、plasmid verification、restriction digest 或 RNA dot-bracket 轻量检查任务时，按需使用 `./assets/bio_molecular_templates/` 与 `./assets/bio_molecular_tools/`
- 上游交接 comparative genomics、pathogen surveillance、phasing/imputation/PRS、phylogenetics、population genetics/GWAS、Newick tree QC 或 GWAS summary stats QC 时，按需使用 `./assets/bio_population_templates/` 与 `./assets/bio_population_tools/`
- 上游交接 segmentation、WSI tiling、flow cytometry panel、IMC analysis、image manifest、label mask、cytometry event table 或 marker intensity QC 时，按需使用 `./assets/bio_cell_imaging_templates/` 与 `./assets/bio_cell_imaging_tools/`
- 上游交接 feature matrix metadata、sample sheet、biomarker model card、causal genomics、variant prioritization、pharmacogenomics handoff、biomarker split leakage 或 ctDNA VAF panel QC 时，按需使用 `./assets/bio_table_templates/` 与 `./assets/bio_table_qc_tools/`
- 上游交接 blot quantification、liquid handling protocol 或 ELN/protocol record 时，按需使用 `./assets/bio_protocol_templates/`
- 上游交接 omics database query、regulatory annotation query 或可复现分析报告骨架时，按需使用 `./assets/bio_knowledge_templates/` 与 `./assets/bio_report_templates/`
- 上游交接实验室仪器 ASM 转换、展平、校验或 parser 导出任务时，按需使用 `./assets/bio_lab_quality_tools/`
- 确认索引后，只继续读取命中的具体卡片，避免一次性加载全部资料
- 需要精确生成 MACE/UMA 训练、微调、验证或推理参数时，先读对应 `*_parameter_policy.md`，再使用：
  - 参数 Schema：`./assets/contracts/mace_parameter_schema.json` 或 `./assets/contracts/uma_parameter_schema.json`
  - 生成器：`./assets/contracts/mace_config_builder.py` 或 `./assets/contracts/uma_hydra_override_builder.py`
  - 校验器：`./assets/contracts/material_config_validator.py`
- 生成参数前必须先把数据探测、checkpoint 探测和任务类型整理成 JSON context；缺失高风险字段时让生成器失败，不要猜值。

## 设计与实现原则

- 优先复用已有组件、接口和目录结构
- 优先最小改动，不重写无关模块
- 明确哪些文件直接改、哪些只加适配层
- 如果上游已给出代码生成交接摘要，仅根据其中的设备适配、路径约束和入口要求实现代码
- 不要在本 skill 内部直接处理 Host、队列、module、conda 等硬件探测细节
- 如果任务本身就是“实现/修复代码”，可以在简短设计后直接进入编码，不必强制停在方案阶段
- 如果需求边界不清、改动范围大或风险高，再先输出方案并等待确认

## 链路续传原则

- 如果上游已明确传递 `required_chain=[onescience-coder, onescience-runtime]` 或 `final_execution_skill=onescience-runtime`，则当前任务在代码完成后仍未结束；必须继续把任务交接给 `onescience-runtime`
- 如果上游同时传递 `chain_continuation_required=true`，不要把“代码已完成”误判为“整条任务链已完成”
- 如果用户请求明确包含“跑一下”“提交”“验证运行”“SCnet”“SLURM”“下载日志”或其它执行信号，即使本轮主要工作是编码，也必须在输出中显式保留运行交接

## 验证原则

- 用户明确要求验证、测试、排查时，交给 `onescience-runtime` 的 `diagnose` 阶段；需要运行或日志证据时由 runtime 统一提交、同步和分类
- 不要把远程测试当成所有编码任务的前置门槛
- 没有执行证据时，不要声称“已验证通过”

## 代码生成后 Review 原则

代码生成后的 review 是静态需求一致性审查，不是运行校验、测试执行、日志排查或 debug。

若上游交接包含 `coder_static_review_required=true`，静态 review 是代码生成完成前的硬性门槛；不能只说“建议 review”，也不能省略 review 结果直接结束。

执行方式：

1. 从用户原始需求、已确认的详细执行信息、上游交接摘要和读取过的契约卡片中提取需求清单。
2. 逐条检查生成或修改的代码是否满足需求清单，至少覆盖：
   - 参数与配置：要求的参数数量、名称、默认值、必填/可选关系是否完整，例如要求 9 个参数时不能只实现 8 个。
   - 模型与结构：要求的主干、组件族和关键结构是否一致，例如要求 Swin Transformer 时不能实现成普通 CNN、MLP、vanilla Transformer 或其它结构。
   - 输入输出协议：变量数、时间步、shape、batch 组织、返回字段和单位是否与需求一致。
   - 数据与训练逻辑：样本构造、split、normalization、loss、rollout、metric、checkpoint 或配置入口是否覆盖需求。
   - OneScience 复用：是否使用了已确认的 datapipe、模型卡、组件契约和最小适配路径。
   - 文件落点与命名：新增文件、类名、函数名、注册名和 import 路径是否符合约定。
3. 若发现偏差，必须先修改代码，使其重新对齐需求；不要只把偏差写进最终说明。
4. 回改后再次做静态 review，直到没有已知需求偏差，或明确列出无法在当前信息下解决的阻塞项。
5. 除非用户明确要求运行，否则不要为了 review 主动运行训练、推理、测试、下载数据或提交远程任务；这类执行验证仍交给 `onescience-runtime`。
6. 最终输出必须包含 `静态需求一致性 review 结果` 小节，列出已核对项、已修正偏差和仍需确认项；缺少该小节时，不算完成代码生成。

## 输出要求

至少给出：

1. 问题理解
2. 可行性与复用点
3. 最小实现路径
4. 需要修改或新增的文件

如果进入编码阶段，再补充：

- 关键实现说明
- 尚未验证的风险点
- 静态需求一致性 review 结果：列出已核对的关键需求、发现并已修正的问题、仍未覆盖或需用户确认的项

如果上游已要求续传到 `onescience-runtime`，还必须补充：

- `next_action=onescience-runtime`
- `chain_continuation_required=true`
- `runtime_handoff`：至少包含本地脚本路径或入口文件、期望 `execution_mode`、`access_mode`、可选 `execution_channel`
- 若用户已授权执行、提交或验证运行，补充 `submission_authorized=true` 与 `authorization_scope`

## 禁止事项

- 不要在上游已指定 `onescience-coder -> onescience-runtime` 时，把代码完成误判为任务完成
- 不要在需要续传到 `runtime` 时省略 `next_action`、`chain_continuation_required` 或 `runtime_handoff`

## 文件落点

- 默认在当前项目目录下工作
- 只有当用户明确指定 `case` 目录时，才把生成文件固定写入 `case`
