# Orchestration Examples

本文件用于说明：当远程环境已经被归一化到某个 `backend_id` 后，`onescience-workflow`、`onescience-role`、`onescience-skill` 三层应如何在交接物中显式携带 backend 状态。

目标不是重复具体路由规则，而是给出一套跨编排层共享的最小输出形态。

## 共享字段

当上游已经识别出远程 backend 时，建议三层至少共享这些字段：

- `backend_id`
- `backend_status`
- `execution_readiness`
- `remote_involved`

其中：

- `backend_id`: `slurm_dcu` / `slurm_gpu` / `slurm_cpu`
- `backend_status`: `stable_backend` / `planned_backend` / `unsupported_for_now`
- `execution_readiness`: `ready_to_execute` / `blocked_by_host` / `blocked_by_backend`

## 三层交接建议

### 1. `workflow_handoff`

至少包含：

- `user_intent`
- `detected_domain`
- `workflow_type`
- `remote_involved`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `next_skill`

### 2. `role_decision`

至少包含：

- `current_role`
- `role_chain`
- `execution_entry`
- `handoff_artifacts.backend_id`
- `handoff_artifacts.backend_status`
- `handoff_artifacts.execution_readiness`

### 3. `skill_resolution`

至少包含：

- `task_type`
- `next_skill`
- `next_action`
- `backend_id`
- `backend_status`
- `execution_readiness`

## 当前状态语义

- `stable_backend`：可进入标准执行链
- `planned_backend`：可继续编排，但必须明确当前只是规划后端
- `unsupported_for_now`：可继续做识别与说明，但对应执行阶段应显式阻断

这些状态应根据目标执行链路从 `backend_specs.json` 的 `support_matrix` 推导，而不是只看 backend 的 runtime `status`。

`execution_readiness` 则用于表达“这个具体环境现在能不能往下执行”：

- `ready_to_execute`：当前 host 已满足继续执行
- `blocked_by_host`：backend 支持，但当前 host 的 readiness 未通过
- `blocked_by_backend`：backend 本身尚不支持，对应执行阶段应显式阻断

## 示例资产

仓库中的结构化示例位于：

- `skills/onescience-debug/assets/examples/gpu_model_remote_debug_torch_blocked.json`
- `skills/onescience-runtime/assets/examples/slurm_dcu_runtime.json`
- `skills/onescience-runtime/assets/examples/slurm_gpu_runtime.json`
- `skills/onescience-installer/assets/resolution_examples/cpu_install_request_blocked.json`
