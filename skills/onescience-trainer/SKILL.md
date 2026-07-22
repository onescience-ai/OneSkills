---
name: onescience-trainer
description: OneScience 科学模型训练执行技能。用于用户希望基于文本说明、网页说明、本地项目路径、已有 checkpoint 或项目原生训练入口来规划、生成并执行模型训练工作流，覆盖气象/地球系统、生信、材料、流体和通用科研模型等领域，包括训练信息获取、数据与切分规划、训练策略整理、完整训练脚本内容生成、训练执行组织以及结果验证。接收格式与 onescience-orchestrator 调用执行技能时的 step_handoff 保持一致，返回 execution_result。需要时协调交接给 onescience-coder、onescience-runtime 以及数据工作流技能。
type: executor
---

# OneScience Trainer

## 职责

将本技能作为科学模型训练任务的执行工作流。把 orchestrator 交给本技能的当前步骤，例如“根据网页说明生成训练脚本”“基于已有 checkpoint 继续训练”“按文本给定的数据与优化器约束生成微调入口”“整理训练计划并提交训练”，转化为从训练信息获取到结果验证的可追踪闭环。

本技能只消费当前执行步骤，不重新规划完整用户目标。本技能负责训练工作流契约和阶段顺序，负责明确训练策略、数据配置、split 假设、loss、optimizer、scheduler、评测频率、checkpoint 策略、日志与验证要求等完整训练脚本内容；这些内容由 trainer 直接定义并保留在 trainer_workdir 中。训练执行阶段的外层控制、入口确定、预检要求和结果归因也由 trainer 负责。只有当这些已定义内容需要写入仓库、修改现有项目文件或对接项目原生目录结构时，才把当前步骤中的文件落盘子动作交接给 `onescience-coder`。依赖包、硬件和运行环境需求不单独成阶段，而是在训练执行阶段通过 `onescience-runtime` 统一处理。

## 工作流

创建或更新工作目录；当 `step_handoff.inputs.runtime.code_save_dir`、上游交接物或用户明确指定了代码保存目录时，`trainer_workdir` 必须使用 `<code_save_dir>/.trainer_work/<run_id>/`。其中 `code_save_dir` 用于保存最终训练脚本、配置、日志引用和用户要求的结果输出，`trainer_workdir` 用于保存训练知识、计划、manifest、runtime 请求/结果、验证报告等 trainer 中间知识产物。若上游已显式提供 `step_handoff.inputs.runtime.trainer_workdir`，则应直接使用该目录，并要求其与 `code_save_dir` 语义保持一致；若未提供代码保存目录，但 `step_handoff.inputs.runtime.workdir`、`task_context.relevant_artifacts` 或用户明确指定了工作目录，则沿用该目录；否则兼容性回退到 `.onescience/trainer/<run_id>/`。进入具体代码生成或执行阶段时，必须从 `trainer_workdir` 中已保存的知识文件读取并交接，不依赖未落盘的会话上下文。

本技能不依赖 `scripts/` 目录下的预置脚本；训练入口、配置、数据适配器、损失函数、评估逻辑和测试要求等完整训练脚本内容都由 trainer 先行定义，不再把这些内容重新交给 `onescience-coder` 决定。若需要将这些已定义内容写入仓库、修改现有项目文件或对接项目原生目录结构，再交接给 `onescience-coder` 落盘为明确文件。

在消费上游交接或生成产物前，先读取 `references/workflow_contract.md`。随后必须先根据 `step_handoff.step_goal`、`task_context.user_goal`、`inputs`、`resource_bindings` 和用户直接请求，从 `type=resource` 技能中召回与训练目标相关的资源，获取训练规格知识、模型/数据使用知识和训练规划决策知识；无论上游是否提供了 `resource_bindings`，都不能跳过初始资源召回。资源 `path` 仅用于标识和追踪，允许作为训练依据的只有用户明确提供内容、上游已展开的资源内容和资源技能返回的 `matched_resources[*].content`。

阶段 0 到阶段 3 在执行具体任务前，必须先基于当前阶段目标评估已召回资源是否足够；若资源缺失、粒度不足或与当前阶段目标不匹配，应再次调用 `type=resource` 技能，按当前阶段目标补充召回资源，再结合资源内容完成该阶段产物。阶段 4 之后消费阶段 0 到阶段 3 已落盘的知识产物与资源使用记录，由 trainer 生成完整训练脚本内容；仅在需要仓库改写或最终文件落点时，按需交接给 `onescience-coder`。

随后按顺序执行以下阶段，并在进入某个阶段时读取对应阶段文件：

1. 输入获取：读取 `references/phase_0_input_acquisition.md`
2. 训练知识整理：读取 `references/phase_1_training_knowledge.md`
3. 数据与切分规划：读取 `references/phase_2_data_and_split.md`
4. 训练策略规划：读取 `references/phase_3_training_strategy.md`
5. 训练代码生成：读取 `references/phase_4_codegen.md`
6. 训练执行：读取 `references/phase_5_execution.md`
7. 结果验证：读取 `references/phase_6_validation.md`

## 交接边界

### 输入契约

本技能接收的调用信息必须与 `onescience-orchestrator` 调用 executor 的格式一致：

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: onescience-trainer
  step_goal: <本步骤目标>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物>
  resource_bindings:
    - path: <资源标识或路径>
      type: <资源类型>
      purpose: <用途>
  inputs: <训练所需输入，例如说明文本、URL、模型、checkpoint、数据、参数、运行方式>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

如果用户直接调用本技能而没有显式 `step_handoff`，先把用户请求规范化为等价的 `step_handoff`，再进入工作流。

### 输出契约

返回结果必须与上游交接格式一致，使用 `execution_result`：

```yaml
execution_result:
  skill: onescience-trainer
  status: <success | partial | failed | blocked>
  artifacts:
    <产物清单>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
```

### 下游技能

当需要将 trainer 已定义的训练脚本内容写入仓库、修改项目现有文件、补齐最终文件路径或对接项目原生目录结构时，使用 `onescience-coder`。`onescience-coder` 负责代码落盘与静态对齐，不负责补全 trainer 尚未明确的训练核心决策。

当需要安装依赖、修复 CUDA/PyTorch、配置 conda 环境、检查硬件或提交运行时，把 package 和环境需求写入执行阶段的 runtime handoff，由 `onescience-runtime` 在执行过程中统一处理运行通道与环境动作。训练执行阶段的外层控制与结果解释仍由 trainer 持有。

当需要本地或远程执行、SLURM 提交、SCnet 路由、日志同步、执行诊断或运行前环境处理时，通过 `onescience-runtime` 选择和调用合适的运行通道。

当数据接入、格式转换、重网格化、切分构建或可复用数据集构建成为实质性子任务时，使用 `onescience-dataset-builder` 等数据工作流技能。

当用户只要求规划或代码生成时，不要静默安装 package、提交远程作业或下载大型数据集。如果用户明确要求运行训练，则在完成必要的预检和授权后继续进入执行阶段。

## 证据规则

优先使用一手训练来源：用户提供的文本、URL 页面、项目 README、训练文档、配置文件、checkpoint 元数据、训练脚本说明和用户提供的文件。使用在线页面、package 元数据、公共数据目录或当前 API 时，必须确认最新信息，并在最终报告中引用来源。

不要编造缺失的模型路径、训练入口、checkpoint 路径、optimizer、scheduler、batch 语义、数据 schema、split、归一化、变量、单位、采样率、分布式策略、日志路径或指标名称。无法确认的项在 `source_capture.md`、`training_knowledge.md`、`training_plan.md` 和运行 manifest 中标记为 `MISSING:` 或 `ASSUMPTION:`。

领域特有元数据只在对应任务中作为附加规则处理：

- 气象/地球系统：保留时间范围、历史窗口、lead time、变量、level、网格、投影、单位和归一化来源。
- 生信：保留物种/参考版本、序列或特征命名、坐标约定、样本/批次元数据和预处理来源。
- 材料：保留结构/组成、晶胞、势函数或描述符、单位、边界条件和结构约束。
- 流体/CFD：保留网格/mesh、边界条件、时间步、物理量单位、无量纲参数和守恒量检查来源。
- 通用科研模型：保留输入 schema、单位、坐标/索引、预处理和输出解释。

## 必需输出

至少在 `trainer_workdir` 中生成或更新以下产物：

- `step_handoff.json`：接收到或规范化后的 orchestrator 执行交接
- `training_request.json`：从 `step_handoff` 派生出的训练请求和约束
- `source_capture.md`：文本或 URL 中已确认的训练事实、来源与缺口
- `training_knowledge.md`：有来源的训练事实和缺口
- `data_preparation_plan.md`：数据与切分规划
- `data_manifest.json`：训练数据清单、schema 和来源记录
- `training_plan.md`：训练策略、依赖、脚本契约和验证标准
- `trainer_run_manifest.json`：覆盖所有阶段的结构化状态
- `coder_task_description.md`：当需要代码落盘时，交给 `onescience-coder` 的自包含落盘任务描述
- 如果需要代码，则给出生成代码、项目原生入口或命令引用，并在 manifest 中标注其位于 `code_save_dir` 或项目原生路径
- 如果执行过训练，则给出执行日志或 runtime 结果引用
- `validation_report.md`：脚本、日志、checkpoint、指标和剩余风险

最终回复和结构化返回必须报告状态、`code_save_dir`、`trainer_workdir`、关键产物、执行状态、验证状态和未解决阻塞项，并以 `execution_result` 作为返回交接物。
