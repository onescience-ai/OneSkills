# Orchestration Examples

本文件说明：`onescience-workflow`、`onescience-role`、`onescience-skill` 三层应如何在交接物中显式携带执行模式与执行状态。

当前公开执行技能为：

- `onescience-runtime`
- `onescience-installer`

其中：

- `execution_mode=remote_slurm` 通常继续归一化到某个 `backend_id`
- `execution_mode=remote_direct` 可以先不伪造 `backend_id`
- `execution_channel` 继续作为路由标签显式携带

## 共享字段

建议三层至少共享：

- `execution_mode`
- `access_mode`
- `execution_channel`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`
- `remote_involved`

其中：

- `execution_mode`: `local | remote_slurm | remote_direct`
- `access_mode`: `local | ssh | cloud_api`
- `execution_channel`: `ssh_slurm | scnet_mcp`
- `backend_id`: `slurm_dcu | slurm_gpu | slurm_gpu_multinode_torchrun | slurm_cpu`
- `backend_status`: `stable_backend | planned_backend | unsupported_for_now`
- `execution_readiness`: `ready_to_execute | blocked_by_host | blocked_by_backend`

补充约束：

- `execution_mode=remote_slurm` 时，应继续补齐 `backend_id + backend_status`
- `execution_mode=remote_direct` 时，可以只携带 `execution_mode + access_mode + execution_readiness`
- 如果同时给出 `execution_channel`，它必须与 `execution_mode/access_mode` 保持一致

## 三层交接建议

### 1. `workflow_handoff`

至少包含：

- `user_intent`
- `detected_domain`
- `workflow_type`
- `remote_involved`
- `execution_mode`
- `access_mode`
- `execution_channel`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`
- `next_skill`

### 2. `role_decision`

至少包含：

- `current_role`
- `role_chain`
- `execution_entry`
- `handoff_artifacts.execution_mode`
- `handoff_artifacts.access_mode`
- `handoff_artifacts.execution_channel`
- `handoff_artifacts.backend_id`
- `handoff_artifacts.backend_status`
- `handoff_artifacts.execution_readiness`
- `handoff_artifacts.blocking_reason`

### 3. `skill_resolution`

至少包含：

- `task_type`
- `next_skill`
- `next_action`
- `execution_mode`
- `access_mode`
- `execution_channel`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`

## 当前状态语义

- `stable_backend`：可进入标准执行链
- `planned_backend`：可继续编排并进入 runtime，但必须明确当前只是规划后端
- `unsupported_for_now`：可继续做识别与说明，但对应执行阶段应显式阻断

`execution_readiness` 用于表达“这个具体环境现在能不能往下执行”：

- `ready_to_execute`
- `blocked_by_host`
- `blocked_by_backend`

如果当前链路已经阻断，建议继续补更细粒度 `blocking_reason`，例如：

- `backend_not_supported`
- `host_not_confirmed`
- `torch_not_ready`
- `scnet_channel_not_confirmed`

## 当前推荐的执行入口

- 运行、提交、查状态、下载日志 -> `onescience-runtime`
- 安装、环境修复 -> `onescience-installer`
- 显式 SCnet 请求 -> 仍进入 `onescience-runtime`
- 若只是推断 SCnet 可能更合适但用户未确认，也仍进入 `onescience-runtime`

## 示例资产

仓库中的结构化示例位于：

- `skills/onescience-runtime/assets/examples/*.json`
- `skills/onescience-installer/assets/resolution_examples/*.json`

当前编排回归应优先覆盖：

- `runtime` 单入口
- `installer` 环境修复入口
- `remote_slurm`
- `remote_direct`
