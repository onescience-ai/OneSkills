# Shared Contracts

本文件用于定义 `onescience-hardware`、`onescience-runtime`、`onescience-installer`、`onescience-debug` 之间共享的跨 skill 契约。

目标不是重复各自 skill 内部的细节，而是明确：

- 哪些字段属于跨 skill 的公共语义
- 哪些资产必须引用同一套 backend 标识
- 哪些层可以消费完整硬件画像，哪些层只能消费精简摘要

## 核心原则

1. `hardware_profile` 是远程环境事实的唯一共享来源。
2. `codegen_handoff` 是 `hardware -> coder` 的唯一精简交接面。
3. `backend_id` 是 `runtime / installer / debug` 在 `ssh_slurm` 通道里共同识别远程执行后端的共享标识。
4. `runtime.target` 与 `hardware_profile` 的 selector 语义必须一致。
5. `installer` 与 `debug` 不得自行创造与 `hardware_profile` 平行的远程环境描述。
6. `execution_channel` 是 `runtime` 对外暴露的统一运行入口语义。

## 共享资产

当前仓库中的共享资产主要包括：

- `skills/onescience-hardware/assets/examples/*.json`
- `skills/onescience-runtime/assets/backend_specs.json`
- `skills/onescience-runtime/assets/examples/*.json`
- `skills/onescience-installer/assets/backend_profiles.json`
- `skills/onescience-installer/assets/workspace_bootstrap_profiles.json`
- `skills/onescience-installer/assets/install_domains.json`
- `skills/onescience-installer/assets/request_examples/*.json`
- `skills/onescience-installer/assets/resolution_examples/*.json`
- `skills/onescience-debug/assets/examples/*.json`

这些资产共同组成：

`hardware output -> backend spec -> runtime config -> installer/debug request`

`scnet_mcp` 通道的补充规则位于：

- `skills/onescience-runtime/references/scnet_channel.md`

## 共享字段

### 1. `backend_id`

由 `onescience-runtime` backend registry 统一登记，当前包括：

- `slurm_dcu`
- `slurm_gpu`
- `slurm_cpu`

约束：

- `hardware` 示例中的 `expected_backend_id` 必须来自 runtime registry
- `runtime` 示例中的 `runtime.backend_id` 必须来自 runtime registry
- `ssh_slurm` runtime 结果/请求如果不直接携带 `runtime`，则至少要能通过 `submission_target.backend_id` 或 `runtime_config -> runtime.backend_id` 解析回 registry
- `installer/debug` 示例中的 `required_backend_id` 必须来自 runtime registry

`scnet_mcp` 通道不依赖 `backend_id` 才能提交，它的主识别字段是 `execution_channel=scnet_mcp`。

### 1.5 `execution_channel`

当前统一值包括：

- `ssh_slurm`
- `scnet_mcp`

约束：

- 所有运行结果都应携带 `execution_channel`
- `ssh_slurm` 才消费 `hardware_profile + backend_id + onescience.json`
- `scnet_mcp` 不应伪造 `onescience.json` 或 SSH 上下文

### 2. `scheduler_type`

这是共享的运行模式语义，不同层都可见：

- `hardware_profile.scheduler_type`
- `codegen_handoff.runtime_mode`
- `runtime.mode`
- `runtime.target.scheduler_type`

约束：

- 这些字段必须在同一条链路上保持一致

### 3. 主加速卡语义

共享字段包括：

- `hardware_profile.accelerators[].kind`
- `hardware_profile.accelerators[].vendor`
- `codegen_handoff.accelerator_kind`
- `codegen_handoff.accelerator_vendor`
- `runtime.target.accelerator_kind`
- `runtime.target.accelerator_vendor`

如果是 CPU-only：

- `hardware_profile.accelerators: []`
- `accelerator_kind: cpu`
- `accelerator_vendor: none`

### 4. 运行能力语义

共享字段包括：

- `hardware_profile.capabilities.launch_mode`
- `codegen_handoff.launch_mode`
- runtime backend constraint 中的 `launch_mode`

共享字段还包括：

- `hardware_profile.accelerators[].distributed_backend`
- `codegen_handoff.distributed_backend`
- runtime backend constraint 中的 `distributed_backend`

### 5. 设备可见性语义

共享字段包括：

- `hardware_profile.accelerators[].visibility_env`
- `codegen_handoff.device_visibility_env`
- runtime backend constraint 中的 `visibility_env`

如果是 CPU-only，统一使用：

- `device_visibility_env: NONE`

## 消费边界

### `onescience-coder`

只消费：

- `codegen_handoff`

不要让它直接读取完整硬件画像中的 Host、partition、module、conda 等细节。

### `onescience-runtime`

消费：

- `execution_channel`
- `hardware_profile`（仅 `ssh_slurm`）
- `runtime backend registry`（仅 `ssh_slurm`）
- 项目级 `onescience.json`（仅 `ssh_slurm`）

它负责把共享字段渲染成具体模板变量，或在 `scnet_mcp` 通道中把本地脚本路径、区域、队列和日志下载规则映射到平台调用。

### `onescience-installer`

消费：

- `hardware_profile`
- `installer backend profile`
- `workspace bootstrap profile`
- `install domain profile`
- 安装请求

它不应跳过 `hardware_profile` 单独推断平台类型。
它可以读取 `software.driver_stack` 及其 `capability_readiness` 判断驱动栈与基础执行能力是否 ready，但不负责系统级驱动安装。
它还应区分：

- backend support status：来自 `support_matrix.installer`
- installer backend profile：来自 `skills/onescience-installer/assets/backend_profiles.json`
- workspace bootstrap profile：来自 `skills/onescience-installer/assets/workspace_bootstrap_profiles.json`
- install domain profile：来自 `skills/onescience-installer/assets/install_domains.json`
- host readiness outcome：来自当前 `hardware_profile` 的 precheck 结果

额外注意：

- `installer backend profile` 可以先以 `planned` 形态存在
- `workspace bootstrap profile` 也可以先以 `planned` 形态存在
- 只有 `support_matrix.installer` 明确切到 `supported`，才表示该安装链路真的可执行
- install request 当前只应表达领域安装意图，不应重新携带 repo 或 env 细节

### `onescience-debug`

消费：

- `hardware_profile`
- debug 请求
- backend support matrix

它不应只凭关键词推断远程环境；涉及远程执行时必须与共享 backend 语义对齐。
它还应区分：

- backend support status：来自 `support_matrix.debug`
- host readiness outcome：来自当前 `hardware_profile` 的 precheck 结果

## 当前支持边界

当前仓库中的 `backend_specs.json` 不只登记 selector，也登记链路支持矩阵。

当前矩阵应按链路理解，而不是对同一个 backend 给出单一全局结论：

- `slurm_dcu`: runtime=`stable` / installer=`supported` / debug=`supported`
- `slurm_gpu`: runtime=`stable` / installer=`unsupported_for_now` / debug=`supported`
- `slurm_cpu`: runtime=`planned` / installer=`unsupported_for_now` / debug=`planned_backend`

因此：

- runtime 的 `stable/planned` 只表达 runtime 自身成熟度
- `installer/debug` 的支持判断必须来自 `support_matrix`，不能再硬编码成“只有 slurm_dcu 支持”
- 上游编排层输出的 `backend_status` 必须结合目标执行链路解释

## QA 要求

至少应存在以下校验：

- hardware 资产自检
- runtime 资产自检
- installer 资产自检
- debug 资产自检
- shared contract 跨层一致性校验

`shared contract` 校验负责发现：

- backend registry 与下游示例之间的漂移
- 不同 skill 资产对同一 backend 的 support matrix 判断不一致
- 不同层对 CPU-only / GPU / DCU 语义定义不一致
- `execution_channel` 结果字段在不同运行通道之间的漂移
