---
name: onescience-runtime
description: 【统一运行与基础诊断技能】在代码生成完成后，识别执行模式、做运行前预检、提交任务、轮询状态、同步日志，并基于执行证据给出基础失败分类。不直接处理用户请求，需由上游技能调用。
---

# OneScience Runtime Skill

## 职责

`onescience-runtime` 是统一运行入口。建议把它视为一个公开 skill、四个内部阶段：

1. `discover`
2. `preflight`
3. `execute`
4. `diagnose`

在运行任务里：

1. 识别当前应走哪个 `execution_mode`
2. 将用户语义中的环境线索整理为候选事实，并通过实际接入通道确认
3. 判断是否需要先回退到 `onescience-installer`
4. 在可执行时生成脚本或命令并提交运行
5. 轮询状态、同步日志
6. 基于执行证据给出基础失败分类

需要进一步判断字段归属或层间交接时，读取 `./references/runtime_contract.md`。
需要把语义环境线索通过实际通道确认成环境事实时，读取 `./references/runtime_probe_contract.md`。
需要查看 SSH/SLURM 只读探测信号采集模板时，读取 `./assets/probe_templates/ssh_slurm_probe.sh`。
需要查看 SCnet DAS / torch 轻量环境探针模板时，读取 `./assets/probe_templates/scnet_das_torch_probe.sh`。
需要明确 `discover/preflight/execute/diagnose` 四阶段分别该交接什么时，读取 `./references/runtime_phase_handoffs.md`。
需要确认 `runtime_profile_ref/install_profile_ref` 的规范命名与绑定关系时，读取 `./assets/execution_profiles.json`。
需要查看 phase 级结构化示例时，读取 `./assets/phase_examples/`。
需要快速判断当前请求该阻断、确认还是继续时，读取 `./references/runtime_decision_matrix.md`。
需要走 SCnet MCP 通道时，读取 `./references/scnet_channel.md`。
需要处理 OneScience 生信模型推理交接时，读取 `./assets/bio_inference_templates/bio_inference_handoff.yaml`。
需要确认 per-model request、推理 manifest 与校验工具归属时，读取 `{onescience_path}/onescience/examples/biosciences/_manifests/` 下的 `contract.json`、`inference_run_manifest.yaml`、`model_requests/` 与 `tools/`；per-model request 示例已归属 OneScience 官方仓库，runtime 不再在 `skills/onescience-runtime/assets/` 保留本地副本。
需要处理“远程环境未配置”或“远程信息不完整”的异常场景时，读取 `../../references/remote_fallback.md`。

## 执行模式

runtime 使用以下执行模式：

- `execution_mode=local`
- `execution_mode=local_slurm`
- `execution_mode=remote_slurm`
- `execution_mode=remote_direct`

补充接入元数据：

- `access_mode=local`
- `access_mode=ssh`
- `access_mode=cloud_api`

路由映射：

- `execution_channel=local_slurm` 等价于 `local_slurm + local`
- `execution_channel=ssh_slurm` 等价于 `remote_slurm + ssh`
- `execution_channel=scnet_mcp` 等价于 `remote_direct + cloud_api`

### `local_slurm`（登录节点直接提交模式）

适用场景：

- agent 当前运行环境即为 HPC 登录节点（已 SSH 进入服务器）
- `sbatch`、`squeue`、`sacct`、`module` 命令可直接调用，无需 SSH 跳转
- 代码直接生成到当前文件系统，无需上传

与 `remote_slurm` 的区别：

- 不需要 SSH 跳转，`access_mode=local`
- `discover` 阶段直接执行本地命令探测：`which sbatch`、`conda info --envs`、`module avail`
- `execute` 阶段直接调用 `sbatch`，不通过 SSH
- `execution_channel=local_slurm`
- 不需要 `onescience.json` 中的 SSH Host 字段，但仍需 partition/queue 信息

自动识别规则：若 `which sbatch` 成功且无 SSH 上下文，优先识别为 `local_slurm`。

### `remote_slurm`（当前默认远程模式）

适用场景：

- 用户要求基于 `onescience.json`、`tpl.slurm` 或现有 SLURM 配置提交
- 上游已经提供完整硬件画像与 backend 选择
- 当前正式稳定 backend 都落在这个模式上

### `remote_direct`（SCnet MCP）

适用场景：

- 用户明确提到 `SCnet`
- 请求里直接出现区域、队列、`task_id`、下载日志、MCP 提交
- 目标是直接上传脚本并通过平台 API 运行

### `local`

适用场景：

- 用户明确要求在本地直接运行
- 当前任务不需要远程提交

远程意图优先于任何“本地最小验证”建议。只要用户明确要求远程执行、远程测试、提交到 SLURM 或提交到 SCnet，就不要在本地执行测试脚本、训练脚本、业务入口脚本，或通过 import 运行依赖来判断远程环境；本地只允许做文件存在性、提交清单、命令模板渲染和不触发业务依赖的静态语法检查。

## 输入约定

runtime 现在同时消费：

- `hardware_profile`
- `runtime_profile`
- `install_profile`
- 项目级运行配置
- 本地代码/脚本路径

用户自然语言里的 Host、队列、区域、设备类型、module、conda 环境或远端路径只表示环境线索。runtime 可以把它们整理为候选，但不能在未经确认和探测时直接当作 `hardware_profile`、`submission_target` 或最终 backend。

### `remote_slurm`

- `onescience.json` 位于项目根目录
- `runtime.execution_profile.execution_mode` 应为 `remote_slurm`
- `runtime.execution_profile.access_mode` 应为 `ssh`
- `runtime.backend_id` 来自 stable backend registry
- `runtime.execution_profile.runtime_profile_ref/install_profile_ref` 来自 `execution_profiles.json`
- `tpl.slurm` 优先位于项目根目录；缺失时回退到 skill 内置模板
- 完整硬件画像提供 Host、平台、队列、模块和环境约束

### `remote_direct`

- 当前环境已安装并可调用对应平台接入
- 用户请求或上游上下文中应能提供本地脚本路径、运行命令或已有 `task_id`
- 这个模式不依赖 `onescience.json` 或 SSH 上下文

如果当前环境缺少运行所需依赖，但问题属于“环境未安装/未修复”，应回退到 `onescience-installer`，不要在 runtime 中临时补装。注意不要把 `install_profile_ref` 误当成 installer backend 名称；真正的安装骨架仍由 install profile 再绑定到 `dcu_remote_install/gpu_remote_install` 等 installer backend。

## 执行流程

1. 先确定 `execution_mode`
2. 进入 `discover`
   - 收集语义环境线索，形成候选 Host / region / queue / backend
   - 通过对应实际通道确认环境事实：`ssh_slurm` 走 SSH / SLURM 探针，`scnet_mcp` 走 SCnet MCP 区域、队列和任务接口
3. 进入 `preflight`
   - 检查 Host/路径/配置是否完整
   - 检查环境是否已 ready
   - 检查配置声明的本地入口脚本、训练脚本、诊断脚本或探针脚本是否真实存在于当前项目
   - 若配置里声明了入口文件但当前项目不存在，直接阻断并返回 `submission_blocked=missing_entrypoint`，不要继续远程提交
   - 若环境缺失，回退到 `onescience-installer`
4. 进入 `execute`
   - `remote_slurm`：读取 `onescience.json`、模板和 backend specs，生成并提交作业
   - `remote_direct`：上传、提交、查状态、下载日志
   - `local`：本地直接执行
5. 进入 `diagnose`
   - 分类提交失败、环境失败、日志未就绪或业务脚本失败
   - 先检查 diagnose 所需最小前置条件是否满足，例如代码文件、模型类、探针脚本、日志文件或可写 artifact 目录
   - 若最小前置条件缺失，直接返回结构化阻断，不要假设项目里存在模型源码、可导入依赖或可写输出目录
   - 返回可消费的日志与状态证据

## 远程提交授权规则

- 同一个用户请求或同一条工作流里，远程提交业务确认最多发生一次
- 如果用户已经明确要求“提交远程运行”“跑一下”“验证运行”“提交到 slurm”“提交到 SCnet”等执行动作，不要再额外询问是否提交
- 如果用户只要求生成代码或方案，不要自动提交远程作业
- 若目标 Host、运行入口脚本、资源规模或执行模式发生变化，应重新确认
- 远程执行请求中的本地准备阶段应命名为 `local_preparation`；若未执行本地脚本，应显式记录 `local_execution=skipped_by_remote_intent`

## 日志同步规则

- 日志同步属于 `onescience-runtime` 的职责
- 本地日志目录默认是 `.onescience/logs/<job_id>/`
- `remote_slurm` 默认同步 `*.out` 与 `*.err`
- `remote_direct` 默认下载平台关联的标准输出与错误日志
- 同步失败时，应报告 `sync_status=failed`
- 作业等待超时，应返回 `execution_state=running_or_unknown`

## 约束

- 不要自动修改用户的 `onescience.json`
- 不要在 Host 未确认时默认选择远程主机
- 不要把用户语义中的环境线索直接当成已确认环境事实
- 不要绕过 SSH / SLURM / SCnet MCP 等实际接入通道伪造环境探测结果
- 不要在发现入口脚本、探针脚本或模型源码缺失后继续提交远程任务
- 不要把代码生成交接摘要误用为完整硬件画像
- 不要在代码尚不存在时提交空作业
- 不要把安装行为混进 runtime
- 不要把深度测试编排混进 runtime
- 不要把排队阶段的占位日志内容当成真实日志交给下游
- 不要把 artifact 目录不可写误判成业务代码失败；应明确标记为本地写出受限

## 输出要求

至少给出：

1. `execution_channel`
2. `execution_mode`
3. `access_mode`
4. 使用的配置文件路径，或 `region/queue`
5. 远程主机或远端上传路径
6. 提交脚本路径，或运行命令 / 探针命令
7. 作业 ID / 任务 ID，或提交失败原因
8. 远端日志路径与日志查看方式
9. 本地日志同步目录
10. `sync_status`
11. 已同步日志列表；若为空，说明原因
12. 若阻断，给出 `submission_blocked` 或等价阻断原因

如果进入远程运行，建议额外给出：

12. `observations.status_source`
13. `observations.log_readiness`

一句话原则：

`onescience-runtime` 负责“发现环境、预检、执行、基础诊断”的运行闭环；环境安装请回退到 `onescience-installer`。
