# 训练工作流契约

在生成产物或接收上游交接前，先使用本契约。本契约必须与 `onescience-orchestrator/references/execution_handoff_contract.md` 保持一致：输入消费 `step_handoff`，输出返回 `execution_result`。

## 上游输入：step_handoff

本技能的标准输入是 orchestrator 调用 executor 的交接物：

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
    - path: <资源路径>
      type: <资源类型>
      purpose: <用途>
      content: <上游已展开的资源内容，可选；若未提供，不得沿 path 直接读取>
  inputs:
    instruction_source:
      source_type: <text | url | local_file | handoff | mixed | unknown>
      text: <可选>
      url: <可选>
      local_path: <可选>
      notes: <可选>
    model:
      code_path: <模型代码路径、仓库或模块入口，可选>
      training_entrypoint: <训练入口或脚本路径，可选>
      source_type: <repository | local | package | paper | unknown>
      config_hint: <可选>
      task_type: <forecast | classification | regression | generation | simulation | unknown>
    checkpoint:
      init_checkpoint: <初始化权重，可选>
      resume_checkpoint: <继续训练权重，可选>
      finetune_checkpoint: <微调权重，可选>
      revision_or_hash: <可选>
    data:
      train_source: <训练数据文件、目录、数据集 ID 或待生成说明>
      val_source: <可选>
      test_source: <可选>
      input_format: <可选>
      split_hint: <可选>
      domain_metadata: <领域特有元数据，可选>
    parameters:
      optimizer: <可选>
      scheduler: <可选>
      batch_size: <可选>
      epochs_or_steps: <可选>
      precision: <可选>
      distributed_mode: <single | ddp | deepspeed | fsdp | megatron | unknown>
      extra: <模型或领域参数，可选>
    runtime:
      execution_intent: <plan_only | generate_code | run_local | run_remote | validate_only | unknown>
      execution_mode: <local | local_slurm | remote_slurm | remote_direct | unknown>
      code_save_dir: <用户指定的代码保存目录，可选>
      trainer_workdir: <trainer 工作目录，可选；推荐显式提供>
      workdir: <trainer 工作目录兼容字段；当提供 code_save_dir 时优先使用 <code_save_dir>/.trainer_work/<run_id>>
      package_requirements: <需要安装或确认的包，可选>
      environment_requirements: <Python/加速后端/内存/模块/镜像等运行需求，可选>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

如果上游未显式提供某些字段，不要猜测高风险事实；把缺失项写入 `missing`、`blockers` 或 `MISSING:` 标记。

## 资源召回契约

本技能先召回资源再执行阶段任务：

1. 接收或规范化 `step_handoff` 后，立即根据训练目标、领域、模型名、数据名、checkpoint、训练入口、用户约束和 `resource_bindings` 中的资源标识，调用匹配的 `type=resource` 技能。
2. 初始召回目标是获取训练规格知识、模型/数据使用知识、训练规划决策知识和可复用实现线索。
3. 阶段 0 到阶段 3 每个阶段开始前，必须对已召回资源做阶段级评估：判断资源是否足以支撑当前阶段目标、哪些资源使用、哪些暂不使用、哪些缺失。
4. 若当前阶段资源不足，必须按当前阶段目标再次调用 `type=resource` 技能补充资源，不得用直接读取资源 `path` 的方式替代召回。
5. 资源 `path` 只用于标识、追踪和最终报告；训练依据只能来自用户明确提供的内容、上游已展开的 `resource_bindings[*].content`、`reference_resources[*].content` 或 `resource_retrieval_result.matched_resources[*].content`。
6. 在 `source_capture.md`、`training_knowledge.md`、`data_preparation_plan.md`、`training_plan.md` 和 `trainer_run_manifest.json` 中记录资源名称、用途、限制、缺口和补召回结果。

资源召回请求格式：

```yaml
resource_retrieval_request:
  user_request: <用户训练需求或当前阶段目标，应包含资源名称、模型/数据/checkpoint/训练入口关键概念>
  task_state_summary: <当前 trainer 阶段、已知事实、缺口和已有资源摘要>
  content_request: "训练规格知识、模型/数据使用知识、训练规划决策知识和可复用实现线索"
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

返回资源结构：

```yaml
resource_retrieval_result:
  status: success | partial | failed
  matched_resources:
    - type: <具体资源类型>
      path: <资源标识或路径，仅追踪>
      name: <资源名称>
      why_matched: <匹配理由>
      limitations: <使用限制>
      content: <完整结构化内容或文本>
```

## 规范化请求

将 `step_handoff` 规范化为 `training_request.json`。该文件是工作目录内部状态，不替代上游交接物。

```json
{
  "schema_version": "onescience-trainer-request-v1",
  "source_handoff_path": "step_handoff.json",
  "step": {
    "step_id": "",
    "step_goal": "",
    "user_goal": "",
    "completion_criteria": []
  },
  "instruction_source": {
    "source_type": "text | url | local_file | handoff | mixed | unknown",
    "text": "",
    "url": "",
    "local_path": "",
    "notes": ""
  },
  "model": {
    "code_path": "",
    "training_entrypoint": "",
    "source_type": "repository | local | package | paper | unknown",
    "config_hint": "",
    "task_type": "forecast | classification | regression | generation | simulation | unknown"
  },
  "checkpoint": {
    "init_checkpoint": "",
    "resume_checkpoint": "",
    "finetune_checkpoint": "",
    "revision_or_hash": ""
  },
  "task": {
    "domain": "earth | biology | materials | cfd | general-science | unknown",
    "objective": "",
    "requested_outputs": []
  },
  "data": {
    "train_source": "",
    "val_source": "",
    "test_source": "",
    "input_format": "",
    "split_hint": "",
    "domain_metadata": {},
    "preprocessing_constraints": []
  },
  "training": {
    "optimizer": "",
    "scheduler": "",
    "batch_size": "",
    "epochs_or_steps": "",
    "precision": "",
    "distributed_mode": "single | ddp | deepspeed | fsdp | megatron | unknown",
    "resume_semantics": "unknown"
  },
  "runtime": {
    "execution_intent": "plan_only | generate_code | run_local | run_remote | validate_only | unknown",
    "execution_mode": "local | local_slurm | remote_slurm | remote_direct | unknown",
    "hardware": "cpu | cuda | dcu | tpu | unknown",
    "code_save_dir": "",
    "trainer_workdir": "",
    "workdir": "",
    "package_requirements": [],
    "environment_requirements": {}
  },
  "constraints": {
    "network_allowed": "unknown",
    "large_download_allowed": "unknown",
    "remote_submission_allowed": "unknown"
  },
  "resource_bindings": []
}
```

`runtime.code_save_dir` 用于保存最终训练脚本、配置和用户要求的结果输出；训练脚本内容本身由 trainer 定义。`runtime.trainer_workdir` / `runtime.workdir` 用于保存 trainer 中间知识产物。若提供 `code_save_dir`，则应将 `trainer_workdir` 规范化为 `<code_save_dir>/.trainer_work/<run_id>`，并将 `workdir` 视为该 trainer 工作目录的兼容字段，而不是最终代码输出目录。仅当需要将 trainer 已定义内容写入 `code_save_dir` 或项目原生路径时，才交给 `onescience-coder` 落盘。

`domain_metadata` 承载领域特有信息，不把任何领域字段作为通用必填项：

- 气象/地球系统：`time_range`、`history_window`、`forecast_horizon`、`variables`、`levels`、`grid`、`projection`、`units`
- 生信：`species`、`reference_build`、`sequence_region`、`feature_schema`、`sample_metadata`、`batch_metadata`
- 材料：`structure_source`、`composition`、`cell`、`periodic_boundary`、`descriptor`、`units`
- 流体/CFD：`mesh`、`boundary_conditions`、`initial_conditions`、`time_step`、`physical_variables`、`nondimensional_numbers`
- 通用科研模型：`input_schema`、`coordinate_system`、`units`、`indexing`、`preprocessing`

## 运行 Manifest

将 `trainer_run_manifest.json` 维护为结构化状态：

```json
{
  "schema_version": "onescience-trainer-run-v1",
  "run_id": "",
  "code_save_dir": "",
  "trainer_workdir": "",
  "workdir": "",
  "handoff_path": "",
  "request_path": "",
  "phase_status": {
    "0_input_acquisition": "pending",
    "1_training_knowledge": "pending",
    "2_data_and_split": "pending",
    "3_training_strategy": "pending",
    "4_codegen": "pending",
    "5_execution": "pending",
    "6_validation": "pending"
  },
  "artifacts": {},
  "handoffs": {},
  "blockers": [],
  "assumptions": [],
  "sources": []
}
```

允许的阶段状态：`pending`、`running`、`success`、`partial`、`blocked`、`failed`、`skipped`。

`code_save_dir` 用于标识最终代码或输出保存位置；训练脚本内容与可执行训练行为的定义由 trainer 持有。`trainer_workdir` 用于标识 `<code_save_dir>/.trainer_work/<run_id>` 下的中间知识产物目录；`workdir` 保留为兼容字段，并指向同一 trainer 工作目录。

## 产物命名

使用稳定的产物名称：

- `step_handoff.json`
- `training_request.json`
- `source_capture.md`
- `training_knowledge.md`
- `data_preparation_plan.md`
- `data_manifest.json`
- `training_plan.md`
- `coder_task_description.md`
- `runtime_request.json`
- `runtime_result.json`
- `validation_report.md`
- `execution_result.json`

如果项目已经有原生目录结构，则在 manifest 中引用原生路径，不要重复复制代码。本技能不要求、也不读取技能内 `scripts/` 目录。`training_plan.md` 必须作为 trainer 拥有的权威训练契约，覆盖可执行训练行为所需的核心决策；`coder_task_description.md` 仅在需要 repo 落盘时才是必需的可选产物。除最终代码入口、配置、日志或用户要求的结果输出外，`step_handoff.json`、`training_request.json`、`source_capture.md`、`training_knowledge.md`、`data_preparation_plan.md`、`data_manifest.json`、`training_plan.md`、`coder_task_description.md`、`runtime_request.json`、`runtime_result.json`、`validation_report.md` 和 `execution_result.json` 等 trainer 中间知识产物都应落在 `trainer_workdir` 中。

## 返回结果：execution_result

结束当前步骤时，生成与 orchestrator 执行结果契约一致的 `execution_result`：

```yaml
execution_result:
  skill: onescience-trainer
  status: <success | partial | failed | blocked>
  artifacts:
    code_save_dir: <最终代码或输出目录>
    trainer_workdir: <trainer 中间知识产物目录>
    workdir: <兼容字段，指向 trainer_workdir>
    handoff: <step_handoff.json>
    request: <training_request.json>
    source_capture: <source_capture.md>
    manifest: <trainer_run_manifest.json>
    training_knowledge: <training_knowledge.md>
    data_preparation_plan: <data_preparation_plan.md，可选>
    data_manifest: <data_manifest.json，可选>
    training_plan: <training_plan.md>
    coder_task_description: <coder_task_description.md，可选；仅当需要 repo 落盘时提供>
    runtime_request: <runtime_request.json，可选>
    runtime_result: <runtime_result.json，可选>
    validation_report: <validation_report.md，可选>
    generated_entrypoint: <生成或引用的训练入口，可选；可为项目原生入口，或由 trainer 定义并经 coder 落盘后的入口>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
```

## 完成标准

只有达到以下状态之一时，当前执行步骤才算结束：

- `success`：本步骤要求的训练规划、完整训练脚本内容生成、执行或验证已完成，且满足声明的完成标准。
- `partial`：已经产生有用产物，但仍存在至少一个非致命缺口。
- `blocked`：缺少用户输入、凭据、文件、授权或可用基础设施，无法继续执行。
- `failed`：某个阶段已尝试执行并失败，有证据支持，且没有自动修复路径。

始终把 `partial`、`blocked` 或 `failed` 的证据记录到 `blockers`，并在 `execution_result.observation` 中说明。训练执行阶段的外层控制权与结果解释权由 trainer 持有；`onescience-runtime` 负责运行通道、环境处理与作业反馈。
