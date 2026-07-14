# 推理工作流契约

在生成产物或接收上游交接前，先使用本契约。本契约必须与 `onescience-orchestrator/references/execution_handoff_contract.md` 保持一致：输入消费 `step_handoff`，输出返回 `execution_result`。

## 上游输入：step_handoff

本技能的标准输入是 orchestrator 调用 executor 的交接物：

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
  inputs:
    model:
      id_or_path: <模型 ID、仓库或本地路径>
      source_type: <huggingface | repository | local | paper | unknown>
      revision: <可选>
      checkpoint_hint: <可选>
      config_hint: <可选>
    data:
      input_source: <输入文件、目录、数据集 ID 或待生成说明>
      input_format: <可选>
      sample_selector: <可选>
      domain_metadata: <领域特有元数据，可选>
    parameters:
      inference_type: <single_sample | batch | rollout | benchmark | interactive | unknown>
      device: <cpu | cuda | dcu | tpu | unknown>
      dtype: <可选>
      batch_size: <可选>
      seed: <可选>
      extra: <模型或领域参数，可选>
    runtime:
      execution_intent: <plan_only | generate_code | run_local | run_remote | validate_only | unknown>
      execution_mode: <local | local_slurm | remote_slurm | remote_direct | unknown>
      code_save_dir: <用户指定的代码保存目录，可选>
      infer_workdir: <infer 工作目录，可选；推荐显式提供>
      workdir: <infer 工作目录兼容字段；当提供 code_save_dir 时优先使用 <code_save_dir>/.infer_work/<run_id>>
      package_requirements: <需要安装或确认的包，可选>
      environment_requirements: <Python/加速后端/内存/模块/镜像等运行需求，可选>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

如果上游未显式提供某些字段，不要猜测高风险事实；把缺失项写入 `missing`、`blockers` 或 `MISSING:` 标记。

## 规范化请求

将 `step_handoff` 规范化为 `inference_request.json`。该文件是工作目录内部状态，不替代上游交接物。

```json
{
  "schema_version": "onescience-infer-request-v2",
  "source_handoff_path": "step_handoff.json",
  "step": {
    "step_id": "",
    "step_goal": "",
    "user_goal": "",
    "completion_criteria": []
  },
  "model": {
    "id_or_path": "",
    "source_type": "huggingface | repository | local | paper | unknown",
    "revision": "",
    "checkpoint_hint": "",
    "config_hint": ""
  },
  "task": {
    "domain": "earth | biology | materials | cfd | general-science | unknown",
    "objective": "",
    "inference_type": "single_sample | batch | rollout | benchmark | interactive | unknown",
    "requested_outputs": []
  },
  "data": {
    "input_source": "",
    "input_format": "",
    "sample_selector": "",
    "domain_metadata": {},
    "preprocessing_constraints": []
  },
  "runtime": {
    "execution_intent": "plan_only | generate_code | run_local | run_remote | validate_only | unknown",
    "execution_mode": "local | local_slurm | remote_slurm | remote_direct | unknown",
    "hardware": "cpu | cuda | dcu | tpu | unknown",
    "code_save_dir": "",
    "infer_workdir": "",
    "workdir": "",
    "package_requirements": [],
    "environment_requirements": {}
  },
  "constraints": {
    "network_allowed": "unknown",
    "large_download_allowed": "unknown",
    "remote_submission_allowed": "unknown",
    "trust_remote_code_allowed": "unknown"
  },
  "resource_bindings": []
}
```

`runtime.code_save_dir` 用于保存最终代码入口、runner 和用户要求的结果输出；`runtime.infer_workdir` / `runtime.workdir` 用于保存 infer 中间知识产物。若提供 `code_save_dir`，则应将 `infer_workdir` 规范化为 `<code_save_dir>/.infer_work/<run_id>`，并将 `workdir` 视为该 infer 工作目录的兼容字段，而不是最终代码输出目录。

`domain_metadata` 承载领域特有信息，不把任何领域字段作为通用必填项：

- 气象/地球系统：`time_range`、`init_time`、`lead_time`、`variables`、`levels`、`grid`、`projection`、`units`
- 生信：`species`、`reference_build`、`sequence_region`、`feature_schema`、`sample_metadata`、`batch_metadata`
- 材料：`structure_source`、`composition`、`cell`、`periodic_boundary`、`descriptor`、`units`
- 流体/CFD：`mesh`、`boundary_conditions`、`initial_conditions`、`time_step`、`physical_variables`、`nondimensional_numbers`
- 通用科研模型：`input_schema`、`coordinate_system`、`units`、`indexing`、`preprocessing`

## 运行 Manifest

将 `inference_run_manifest.json` 维护为结构化状态：

```json
{
  "schema_version": "onescience-infer-run-v2",
  "run_id": "",
  "code_save_dir": "",
  "infer_workdir": "",
  "workdir": "",
  "handoff_path": "",
  "request_path": "",
  "phase_status": {
    "1_model_knowledge": "pending",
    "3_data_preparation": "pending",
    "4_model_loading": "pending",
    "5_codegen": "pending",
    "6_execution": "pending",
    "7_validation": "pending"
  },
  "artifacts": {},
  "handoffs": {},
  "blockers": [],
  "assumptions": [],
  "sources": []
}
```

允许的阶段状态：`pending`、`running`、`success`、`partial`、`blocked`、`failed`、`skipped`。

`code_save_dir` 用于标识最终代码或输出保存位置；`infer_workdir` 用于标识 `<code_save_dir>/.infer_work/<run_id>` 下的中间知识产物目录；`workdir` 保留为兼容字段，并指向同一 infer 工作目录。

## 产物命名

使用稳定的产物名称：

- `step_handoff.json`
- `inference_request.json`
- `model_knowledge.md`
- `data_preparation_plan.md`
- `data_manifest.json`
- `model_loading_plan.md`
- `inference_plan.md`
- `inference_entrypoint.py` 或项目原生入口引用
- `runtime_request.json`
- `runtime_result.json`
- `validation_report.md`
- `execution_result.json`

如果项目已经有原生目录结构，则在 manifest 中引用原生路径，不要重复复制代码。本技能不要求、也不读取技能内 `scripts/` 目录。除最终代码入口、runner 或用户要求的结果输出外，`step_handoff.json`、`inference_request.json`、`model_knowledge.md`、`data_preparation_plan.md`、`data_manifest.json`、`model_loading_plan.md`、`inference_plan.md`、`runtime_request.json`、`runtime_result.json`、`validation_report.md` 和 `execution_result.json` 等 infer 中间知识产物都应落在 `infer_workdir` 中。

## 返回结果：execution_result

结束当前步骤时，生成与 orchestrator 执行结果契约一致的 `execution_result`：

```yaml
execution_result:
  skill: onescience-infer
  status: <success | partial | failed | blocked>
  artifacts:
    code_save_dir: <最终代码或输出目录>
    infer_workdir: <infer 中间知识产物目录>
    workdir: <兼容字段，指向 infer_workdir>
    handoff: <step_handoff.json>
    request: <inference_request.json>
    manifest: <inference_run_manifest.json>
    model_knowledge: <model_knowledge.md>
    data_preparation_plan: <data_preparation_plan.md，可选>
    data_manifest: <data_manifest.json，可选>
    model_loading_plan: <model_loading_plan.md，可选>
    inference_plan: <inference_plan.md>
    runtime_request: <runtime_request.json，可选>
    runtime_result: <runtime_result.json，可选>
    validation_report: <validation_report.md，可选>
    generated_entrypoint: <生成或引用的推理入口，可选>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
```

## 完成标准

只有达到以下状态之一时，当前执行步骤才算结束：

- `success`：本步骤要求的推理、代码生成或验证已完成，且满足声明的完成标准。
- `partial`：已经产生有用产物，但仍存在至少一个非致命缺口。
- `blocked`：缺少用户输入、凭据、文件、授权或可用基础设施，无法继续执行。
- `failed`：某个阶段已尝试执行并失败，有证据支持，且没有自动修复路径。

始终把 `partial`、`blocked` 或 `failed` 的证据记录到 `blockers`，并在 `execution_result.observation` 中说明。
