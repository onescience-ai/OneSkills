# Runtime Contract

本文件说明 `onescience-runtime` 的职责、输入分层与输出边界。

如果需要看四阶段更细的输入/输出交接，继续读取 `./runtime_phase_handoffs.md`。
如果需要看实际环境探测的输入、输出和安全边界，继续读取 `./runtime_probe_contract.md`。

当前建议把 `onescience-runtime` 视为统一运行与基础诊断入口；它对外是一个 skill，对内拆成 4 个固定阶段：

1. `discover`
2. `preflight`
3. `execute`
4. `diagnose`

共享 profile 注册表位于 `../assets/execution_profiles.json`。

## 执行模式

runtime 现在优先按 `execution_mode` 理解链路：

- `local`
- `local_slurm`
- `remote_slurm`
- `remote_direct`

补充接入元数据：

- `access_mode=local`
- `access_mode=ssh`
- `access_mode=cloud_api`

推荐映射：

- `execution_channel=local_direct` 等价于 `execution_mode=local` + `access_mode=local`
- `execution_channel=local_slurm` 等价于 `execution_mode=local_slurm` + `access_mode=local`
- `execution_channel=ssh_slurm` 等价于 `execution_mode=remote_slurm` + `access_mode=ssh`
- `execution_channel=scnet_mcp` 表示 `execution_mode=remote_direct` + `access_mode=cloud_api` 的 SCnet 路由上下文；命中 SCnet 作业、文件、账户、区域、队列或集群相关需求时，直接调用 `scnet-chat` 技能执行，runtime 只消费结果

## runtime 的职责

runtime 负责回答“代码怎么跑起来，并在失败时给出基础执行诊断”：

- 识别当前执行模式
- 将用户语义中的环境线索整理为候选事实
- 通过实际接入通道发现或确认完整环境事实
- 运行前预检
- 选择 backend 与 runtime profile
- 生成脚本或命令
- 提交 / 执行 / 轮询
- 同步或下载日志
- 基于执行证据做基础失败分类

runtime 不负责：

- 安装或修复用户态环境
- 系统驱动部署
- 长链路领域测试编排

如果预检发现环境未 ready，应回退到 `onescience-installer`，而不是在 runtime 中偷偷补装依赖。

### Readiness 与安装边界

runtime 可以确认目标环境是否 ready，但不能改变目标环境。

允许的 readiness confirmation：

- `module load`
- `conda activate`
- `python -c 'import torch'`
- 轻量 probe task
- 远端路径可写性检查

禁止的 environment mutation：

- `conda create`
- `pip install`
- `git clone` / 同步 OneScience 工作区
- `conda init` / 修改 shell 初始化文件
- 安装或升级系统 / 用户态依赖

如果 runtime 通过实际通道确认 `python_not_ready`、`torch_not_ready`、`distributed_runtime_not_ready` 或 OneScience import 不可用，应输出 blocker 并把 `next_action` 指向 `onescience-installer`。installer 完成安装和 `verify` 后，再把环境交回 runtime。

## 四阶段稳定交接面

建议把内部 4 阶段视为固定流水线，而不是随意跳转的步骤：

1. `discover`
   - 产出执行模式、目标候选、环境事实与缺失事实
2. `preflight`
   - 产出最终 backend/profile/target，以及 `execution_readiness`
3. `execute`
   - 产出提交状态、运行状态、日志同步结果
4. `diagnose`
   - 产出基础失败分类、状态来源与下游交接物

稳定判断：

- `discover` 回答“走哪条链路、有哪些候选、缺什么事实”
- `preflight` 回答“当前能不能执行、为什么不能、该不该回退 installer”
- `execute` 回答“是否已提交、现在跑到哪一步、日志同步到哪里”
- `diagnose` 回答“更像哪类失败、下一步该留在 runtime 还是回退 installer/上游”

## 共享输入：`execution_profile`

runtime 消费三类输入：

### 1. `hardware_profile`

环境事实，通常来自 `discover` 阶段产出：

- `host`
- `scheduler_type`
- `cpu.*`
- `accelerators[]`
- `software.modules`
- `software.conda_env`
- `software.driver_stack`
- `software.capability_readiness`
- `storage.*`

用户语义中的环境描述只能作为候选输入，例如“昆山 SCnet”“某个 DCU 队列”“GPU 集群”“hpctest01”。这些描述在经过用户确认和实际通道探测前，不应升级为 `hardware_profile`。

### 2. `runtime_profile`

运行方式与模板约束：

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

这些 profile id 统一从 `execution_profiles.json.runtime_profiles[]` 读取，不再在 phase 示例、文档和 backend spec 里各自发明别名。

### 3. 项目级运行配置

例如 `onescience.json` 中的：

- `runtime.backend_id`
- `runtime.execution_profile`
- `runtime.cluster.*`
- `runtime.script.*`
- `runtime.logs.*`
- `runtime.submission.*`

## 运行配置分层

### 语义环境线索

这些字段只表示候选事实，不表示已确认环境：

- 用户提到的 Host / 集群 / 平台名称
- 用户提到的 region / queue / partition
- 用户提到的 CPU / GPU / DCU 类型
- 用户提到的 module / conda / path 线索

runtime 必须通过实际确认通道把它们升级为环境事实：

- `ssh_slurm`：通过 SSH / SLURM 配置、只读探针或远端命令确认 Host、partition、module、driver stack 与路径可用性。
- `scnet_mcp`：通过 SCnet 通道确认 region、queue、task_id 与日志可用性；命中 SCnet 作业、文件、账户、区域、队列或集群相关需求时，直接调用 `scnet-chat` 技能执行，runtime 只消费结果。

### 环境事实

这些字段只来自 `hardware_profile`，不要猜测：

- `host`
- `scheduler_type`
- `partition`
- `cpu.*`
- `accelerators[]`
- `software.*`
- `storage.*`

### 项目申请与脚本入口

这些字段主要来自 `onescience.json` 或用户输入：

- `runtime.cluster.nodes`
- `runtime.cluster.gpus_per_node`
- `runtime.cluster.cpus_per_task`
- `runtime.cluster.time_limit`
- `runtime.cluster.memory`
- `runtime.script.code_path`
- `runtime.script.job_name`

### 运行 profile

这些字段由 backend/profile 决定或约束：

- `runtime.execution_profile.execution_mode`
- `runtime.execution_profile.access_mode`
- `runtime.execution_profile.runtime_profile_ref`
- `runtime.execution_profile.install_profile_ref`
- `runtime.script.template`
- 模板变量映射

其中：

- `runtime_profile_ref` 绑定运行链路与执行模板
- `install_profile_ref` 只绑定回退 installer 时的安装 profile
- `install_profile_ref` 不等于 installer backend 名称

## backend 选择

当前 `backend_specs.json` 中的 stable backend 仍集中在 `remote_slurm`：

- `slurm_dcu`
- `slurm_gpu`
- `slurm_gpu_multinode_torchrun`
- `slurm_cpu`

对 runtime 来说，backend 选择顺序应是：

1. 先确认 `execution_mode`
2. 再根据 `hardware_profile` 与 selector 选择 backend
3. 再读取 backend 绑定的 `runtime_profile` / `install_profile`
4. 再进入模板渲染、命令生成与执行

补充说明：

- `remote_slurm` 通过 `backend_specs.json` 选择 backend，再反查 `execution_profiles.json`
- `remote_direct` 当前主要通过 `execution_channel + runtime_profile_ref` 表达，不要求伪造 `onescience.json`

这个顺序意味着：

- backend 选择发生在 `preflight` 决策阶段，而不是 `execute` 阶段临时决定
- `discover` 可以给候选 backend，但不应直接固化最终 backend

## 与 installer 的边界

runtime：

- 发现环境
- 判断是否 ready
- 执行作业
- 回收日志
- 输出基础诊断

installer：

- 安装缺失依赖
- 修复用户态运行环境
- 验证环境 ready

当发现以下问题时，runtime 应回退到 installer，而不是继续执行：

- framework stack 缺失
- conda/env 未准备好
- distributed runtime 不满足
- 用户明确要求先装环境

## 与深度排障的边界

runtime 内部 `diagnose` 阶段只负责：

- 识别执行失败属于提交失败、环境失败、日志未就绪还是业务脚本失败
- 向下游给出 `failure_reason`、`status_source`、`synced_logs`

它不应接管完整测试框架或深度领域排障。

## 统一输出

runtime 对外至少稳定输出：

- `execution_channel`
- `execution_mode`
- `access_mode`
- `submission_state`
- `execution_state`
- `log_state`
- `submission_target`
- `job_id/task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `failure_reason`
- `next_action`

如果进入远程日志消费链，建议同时输出：

- `observations.status_source`
- `observations.log_readiness`

如果需要对内拆解，建议对应到：

- `evidence.discovery`
- `evidence.preflight`
- `evidence.execute`
- `evidence.diagnose`

一句话原则：

`onescience-runtime` 不是“拿到脚本就提交”，而是“先发现环境、做运行前预检，再执行并给出可消费的运行证据与基础诊断”。
