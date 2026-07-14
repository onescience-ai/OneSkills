---
name: onescience-infer
description: OneScience 科学模型推理执行技能。用于用户希望运行或构建 HuggingFace 模型、官方文档模型、本地 checkpoint 或项目原生 runner 的推理工作流时，覆盖气象/地球系统、生信、材料、流体和通用科研模型等领域，包括模型卡与配置发现、输入数据准备、checkpoint 加载、推理入口生成或复用、执行、结果验证、可视化和 baseline 对比。接收格式与 onescience-orchestrator 调用执行技能时的 step_handoff 保持一致，返回 execution_result。需要时协调交接给 onescience-coder、onescience-runtime 以及数据准备类技能。
type: executor
---

# OneScience Infer

## 职责

将本技能作为科学模型推理任务的执行工作流。把 orchestrator 交给本技能的当前步骤，例如“为 HuggingFace checkpoint 生成推理入口”“使用本地 checkpoint 跑一次材料性质预测”“准备生信模型输入并执行推理”“验证流体仿真 surrogate 输出”，转化为从模型知识获取到结果验证的可追踪闭环。

本技能只消费当前执行步骤，不重新规划完整用户目标。本技能负责推理工作流契约和阶段顺序；当代码实现、数据构建或运行提交由已有执行技能更适合负责时，应将当前步骤交接给对应技能。依赖包、硬件和运行环境需求不单独成阶段，而是在推理执行阶段交给 `onescience-runtime`。

## 工作流

创建或更新工作目录；当 `step_handoff.inputs.runtime.code_save_dir`、上游交接物或用户明确指定了代码保存目录时，`infer_workdir` 必须使用 `<code_save_dir>/.infer_work/`。其中 `code_save_dir` 用于保存最终代码入口、runner 或用户要求的结果输出，`infer_workdir` 用于保存模型知识、计划、manifest、runtime 请求/结果、验证报告等 infer 中间知识产物。若上游已显式提供 `step_handoff.inputs.runtime.infer_workdir`，则应直接使用该目录，并要求其与 `code_save_dir` 语义保持一致；若未提供代码保存目录，但 `step_handoff.inputs.runtime.workdir`、`task_context.relevant_artifacts` 或用户明确指定了工作目录，则沿用该目录；否则兼容性回退到 `.onescience/infer/<run_id>/`。进入具体代码生成或执行阶段时，必须从 `infer_workdir` 中已保存的知识文件读取并交接，不依赖未落盘的会话上下文。

本技能不依赖 `scripts/` 目录下的预置脚本；如需生成或修改推理入口，使用项目原生入口或交接给 `onescience-coder` 产出明确文件。

在消费上游交接或生成产物前，先读取 `references/workflow_contract.md`。随后按顺序执行以下阶段，并在进入某个阶段时读取对应阶段文件：

1. 模型知识获取：读取 `references/phase_1_model_knowledge.md`
2. 数据准备：读取 `references/phase_3_data_preparation.md`
3. 模型加载：读取 `references/phase_4_model_loading.md`
4. 推理代码生成：读取 `references/phase_5_codegen.md`
5. 推理执行：读取 `references/phase_6_execution.md`
6. 结果验证：读取 `references/phase_7_validation.md`

## 交接边界

### 输入契约

本技能接收的调用信息必须与 `onescience-orchestrator` 调用 executor 的格式一致：

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: onescience-infer
  step_goal: <本步骤目标>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物>
  resource_bindings:
    - path: <资源标识或路径>
      type: <资源类型>
      purpose: <用途>
  inputs: <推理所需输入，例如模型、checkpoint、数据、参数、运行方式>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

如果用户直接调用本技能而没有显式 `step_handoff`，先把用户请求规范化为等价的 `step_handoff`，再进入工作流。

### 输出契约

返回结果必须与上游交接格式一致，使用 `execution_result`：

```yaml
execution_result:
  skill: onescience-infer
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

当需要生成或修改模型专用 Python pipeline、runner、adapter、绘图代码和测试时，使用 `onescience-coder`。

当需要安装依赖、修复 CUDA/PyTorch、配置 conda 环境、检查硬件或提交运行时，把 package 和环境需求写入执行阶段的 runtime handoff，由 `onescience-runtime` 在执行过程中统一处理。

当需要本地或远程执行、SLURM 提交、SCnet 路由、日志同步、执行诊断或运行前环境处理时，使用 `onescience-runtime`。

当数据接入、格式转换、重网格化或可复用数据集构建成为实质性子任务时，使用 `onescience-dataset-builder` 等数据工作流技能。

当用户只要求规划或代码生成时，不要静默安装 package、提交远程作业或下载大型数据集。如果用户明确要求运行推理，则在完成必要的预检和授权后继续进入执行阶段。

## 证据规则

优先使用一手模型来源：HuggingFace model card、仓库 README、官方推理文档、配置文件、checkpoint 元数据和用户提供的文件。使用在线 model card、文档、package 元数据、公共数据目录或当前 API 时，必须确认最新信息，并在最终报告中引用来源。

不要编造缺失的 shape、变量、归一化常数、坐标系、网格、序列长度、采样率、特征空间、物理单位、forecast horizon、pressure level 或 checkpoint 名称。无法确认的项在 `model_knowledge.md`、`inference_plan.md` 和运行 manifest 中标记为 `MISSING:` 或 `ASSUMPTION:`。

领域特有元数据只在对应任务中作为附加规则处理：

- 气象/地球系统：保留时间、lead time、变量、level、网格、投影、单位和归一化来源。
- 生信：保留物种/参考版本、序列或特征命名、坐标约定、样本/批次元数据和预处理来源。
- 材料：保留结构/组成、晶胞、势函数或描述符、单位、边界条件和结构约束。
- 流体/CFD：保留网格/mesh、边界条件、时间步、物理量单位、无量纲参数和守恒量检查来源。
- 通用科研模型：保留输入 schema、单位、坐标/索引、预处理和输出解释。

## 必需输出

至少在 `infer_workdir` 中生成或更新以下产物：

- `step_handoff.json`：接收到或规范化后的 orchestrator 执行交接
- `inference_request.json`：从 `step_handoff` 派生出的推理请求和约束
- `model_knowledge.md`：有来源的模型事实和缺口
- `inference_plan.md`：阶段计划、依赖、数据契约、runner 契约和验证标准
- `inference_run_manifest.json`：覆盖所有阶段的结构化状态
- 如果需要代码，则给出生成代码、项目原生入口或命令引用，并在 manifest 中标注其位于 `code_save_dir` 或项目原生路径
- 如果执行过推理，则给出执行日志或 runtime 结果引用
- `validation_report.md`：输出检查、可视化、baseline 对比和剩余风险

最终回复和结构化返回必须报告状态、`code_save_dir`、`infer_workdir`、关键产物、执行状态、验证状态和未解决阻塞项，并以 `execution_result` 作为返回交接物。
