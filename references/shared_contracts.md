# Shared Contracts

本文件定义 `onescience-runtime` 与 `onescience-installer` 之间共享的执行契约。

当前公开执行技能为：

- `onescience-runtime`
- `onescience-installer`

其中：

- 环境识别能力由 `runtime/installer` 的 `discover` 阶段承担
- 运行后基础诊断能力由 `runtime` 的 `diagnose` 阶段承担

共享 profile 注册表位于 `skills/onescience-runtime/assets/execution_profiles.json`。

## 核心原则

1. `hardware_profile` 仍是环境事实的唯一共享来源。
2. `runtime` 与 `installer` 共享同一套 `execution_profile`，不要各自发明并行环境描述。
3. `execution_mode` 是主执行模式字段；`execution_channel` 只是对外展示用的路由标签。
4. `backend_id` 仍是 runtime stable backend registry 的共享标识，但后续选择逻辑应先看 `execution_mode` 再看 backend。
5. `runtime` 负责运行闭环，`installer` 负责环境安装/修复，二者不要互相吞并职责。

## 执行模式

当前统一使用：

- `execution_mode=local`
- `execution_mode=remote_slurm`
- `execution_mode=remote_direct`

配套接入元数据：

- `access_mode=local`
- `access_mode=ssh`
- `access_mode=cloud_api`

推荐映射：

- `execution_channel=ssh_slurm` -> `execution_mode=remote_slurm` + `access_mode=ssh`
- `execution_channel=scnet_mcp` -> `execution_mode=remote_direct` + `access_mode=cloud_api`

## 共享对象：`execution_profile`

建议维护三块共享 profile：

### 1. `hardware_profile`

只描述环境事实，例如：

- `host`
- `scheduler_type`
- `cpu.*`
- `accelerators[]`
- `software.driver_stack`
- `software.capability_readiness`
- `software.modules`
- `software.conda_env`
- `storage.*`

### 2. `runtime_profile`

只描述怎么启动与回收任务，例如：

- `execution_mode`
- `access_mode`
- `scheduler_type`
- `launch_mode`
- `visibility_env`
- `distributed_backend`
- `template_family`
- `render_fields`
- `log_strategy`
- `status_strategy`

这些 profile id 统一登记在 `execution_profiles.json.runtime_profiles[]`。

### 3. `install_profile`

只描述怎么安装/修复用户态环境，例如：

- `installer_backend`
- `module_setup`
- `python_env_strategy`
- `framework_stack`
- `dependency_family`
- `precheck_rules`

这些 profile id 统一登记在 `execution_profiles.json.install_profiles[]`，并继续绑定到 installer backend / workspace profile。

## `backend_id` 与 backend registry

`backend_specs.json` 当前主要登记配置驱动的 `remote_slurm` backend。当前 stable backend 包括：

- `slurm_dcu`
- `slurm_gpu`
- `slurm_gpu_multinode_torchrun`
- `slurm_cpu`

每个 backend 现在至少应继续描述：

- `execution_mode`
- `access_mode`
- `scheduler_type`
- `runtime_profile`
- `install_profile`
- `support_matrix`
- `selector`
- `environment_constraints`

约束：

- runtime config 的 `runtime.backend_id` 必须来自 registry
- runtime config 的 `runtime.execution_profile.*_ref` 必须与 registry 中登记的 profile 对齐
- installer 若消费 `required_backend_id`，也必须来自同一 registry

补充约束：

- `install_profile_ref` 不等于 installer backend 名称
- `install_profile_ref` 必须先在 `execution_profiles.json.install_profiles[]` 中登记
- install profile 再绑定到 `skills/onescience-installer/assets/backend_profiles.json` 里的 installer backend
- `remote_direct` 通道允许只通过 profile registry 声明轻量 channel backend，例如 `scnet_mcp_direct`

## 消费边界

### `onescience-runtime`

负责内部 4 阶段：

1. `discover`
2. `preflight`
3. `execute`
4. `diagnose`

四阶段建议共享同一份最小 phase context，至少稳定携带：

- `execution_mode`
- `access_mode`
- `execution_channel`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`
- `submission_blocked`
- `submission_target`
- `evidence.*`

消费：

- `hardware_profile`
- `runtime_profile`
- 项目级运行配置
- 本地代码/脚本路径

负责产出：

- `submission_state`
- `execution_state`
- `log_state`
- `job_id/task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `status_source`
- `next_action`

补充约束：

- `preflight` 若发现配置声明的入口脚本、诊断脚本或探针脚本在当前项目中不存在，应直接返回 `submission_blocked=missing_entrypoint`
- `diagnose` 若缺少最小前置条件，例如模型源码、可实例化类、日志文件或可写 artifact 目录，应返回结构化阻断，不要伪装成业务执行失败
- artifact 目录不可写属于本地写出受限，应与远端作业失败、代码失败区分开

### `onescience-installer`

负责内部 4 阶段：

1. `discover`
2. `precheck`
3. `install`
4. `verify`

四阶段建议共享同一份最小 phase context，至少稳定携带：

- `execution_mode`
- `access_mode`
- `execution_channel`
- `required_backend_id`
- `installer_backend`
- `workspace_bootstrap_profile`
- `install_domain`
- `precheck_outcome`
- `blocking_reason`
- `installed_env_summary`
- `evidence.*`

消费：

- `hardware_profile`
- `install_profile`
- `workspace bootstrap profile`
- `install domain profile`

负责产出：

- `install_state`
- `precheck_outcome`
- `installed_env_summary`
- `blocking_reason`
- `next_action`

### 代码实现层

- `onescience-coder` 仍只消费 `codegen_handoff`

## 统一状态语义

跨层至少保持：

- `execution_mode`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`

补充约束：

- `remote_slurm` 链路通常仍需要 `backend_id`
- `remote_direct` 链路可以先只带 `execution_mode + access_mode + execution_readiness`
- `execution_readiness=blocked_by_host` 时，应显式补细粒度原因
- `submission_blocked=missing_entrypoint` 时，不应继续进入远程提交
- `blocking_reason=artifact_dir_not_writable` 时，不应归类为业务代码失败

## 当前支持边界

当前 stable runtime backend 集中在 `remote_slurm` 模式。

当前 `remote_direct` 主要通过 `scnet_mcp` 这组运行资产表达：

- 它仍然走 `onescience-runtime`
- 它不要求伪造 `onescience.json`
- 它以 `execution_mode=remote_direct` 表达

## QA 要求

至少应校验：

- backend registry 中的 `execution_mode/access_mode/scheduler_type/profile refs`
- runtime config 中的 `execution_profile`
- runtime request/result 中 `execution_channel` 与 `execution_mode/access_mode` 的一致性
- installer resolution 与 `support_matrix.installer` 一致性

一句话原则：

`runtime` 负责“发现环境、预检、执行、基础诊断”，`installer` 负责“安装与修复环境”，共享同一套 `execution_profile`。
