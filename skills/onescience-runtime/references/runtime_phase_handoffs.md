# Runtime Phase Handoffs

本文件把 `onescience-runtime` 内部 4 个固定阶段的交接面单独展开，目的是让后续实现、资产样例与 QA 都围绕同一套 phase contract 对齐。

结构化 phase 示例可参考：`../assets/phase_examples/`。
共享 profile id 可参考：`../assets/execution_profiles.json`。

当前 phase 级示例最少覆盖：

- `ssh_slurm_runtime_happy_path`
- `ssh_slurm_runtime_host_confirmation`
- `ssh_slurm_runtime_installer_fallback`
- `scnet_mcp_runtime_happy_path`
- `scnet_mcp_runtime_status_fallback`

对外仍然只有一个公开 skill：`onescience-runtime`。

对内固定拆成：

1. `discover`
2. `preflight`
3. `execute`
4. `diagnose`

## 一、总原则

- 每个阶段只回答当前阶段该回答的问题，不越权替下个阶段做决定。
- 阶段之间传递的是结构化交接物，不是自由叙述。
- `discover` 产出语义线索、环境事实或候选目标，不直接提交。
- `preflight` 产出可执行判断，不直接吞并安装。
- `execute` 只负责执行与状态回收，不负责重新解释环境。
- `diagnose` 只负责基础执行诊断，不接管完整测试编排。

## 二、共享 phase context

建议后续实现时，把四阶段都挂到同一份 `runtime_phase_context` 上，至少保持下面字段稳定：

- `execution_mode`
- `access_mode`
- `execution_channel`
- `intent`
- `backend_id`
- `backend_status`
- `execution_readiness`
- `blocking_reason`
- `submission_target`
- `evidence`

其中：

- `execution_mode/access_mode/execution_channel` 解决“走哪条链路”
- `backend_id/backend_status` 解决“命中哪个 backend”
- `execution_readiness/blocking_reason` 解决“当前能不能继续”
- `submission_target` 解决“最终往哪里执行”
- `evidence` 解决“当前判断依据是什么”

## 三、阶段定义

### 1. `discover`

目标：

- 识别当前请求属于 `local`、`remote_slurm` 还是 `remote_direct`
- 从用户语义里提取环境线索，并标记为候选事实
- 收集或消费环境事实
- 归一化 backend 候选与提交目标候选

只消费：

- 用户意图
- 上游 handoff
- 已存在的 `hardware_profile`
- 项目配置中的执行线索
- 通道显式输入，例如 `region/queue/task_id`

至少产出：

- `execution_mode`
- `access_mode`
- `execution_channel`
- `submission_target_candidates`
- `backend_candidates`
- `hardware_profile` 或 `hardware_profile_ref`
- `missing_facts`
- `evidence.discovery`

如果环境信息只来自用户语义，`discover` 只能产出候选值，例如 `submission_target_candidates`、`backend_candidates` 或 `semantic_environment_hints`，不应直接产出最终 `hardware_profile`。

不应产出：

- 最终 `ready_to_execute`
- 真实提交结果
- 深度失败分类

推荐问题边界：

- “这次该走哪种执行模式？”
- “当前有哪些可用 Host / 区域 / backend 候选？”
- “还缺哪些环境事实？”

### 2. `preflight`

目标：

- 在已知链路和目标候选的前提下，判断当前是否允许执行
- 固化最终 backend / profile / target
- 识别应该回退 installer 还是应该追问用户

只消费：

- `discover` 输出
- `runtime_profile`
- 项目级运行配置
- 模板渲染字段
- 轻量探针结果

至少产出：

- `backend_id`
- `runtime_profile_ref`
- `install_profile_ref`
- `submission_target`
- `execution_readiness`
- `blocking_reason`
- `confirmation_required`
- `missing_fields`
- `installer_fallback_required`
- `evidence.preflight`

`preflight` 负责把候选环境线索通过实际接入通道确认成事实：`ssh_slurm` 使用 SSH / SLURM 探针，`scnet_mcp` 使用 SCnet MCP 区域、队列、任务与日志接口。未确认前不得进入 `execute`。

典型分流：

- 缺 Host / 多 Host 未确认 -> `confirmation_required`
- 缺配置字段 / 缺代码入口 -> `blocked_by_host` 或回上游补齐
- 环境未 ready -> `execution_readiness=blocked_by_host`，并设置具体 `blocking_reason` 与 `installer_fallback_required=true`
- backend 未开放 -> `blocked_by_backend`
- 条件齐全 -> `ready_to_execute`

`execution_readiness` 只表达粗粒度 readiness；`blocking_reason` 可以更细，例如 `torch_not_ready`、`scnet_service_unavailable` 或 `sbatch_submission_failed`。

推荐问题边界：

- “当前能不能执行？”
- “如果不能，是缺配置、缺确认，还是环境未 ready？”
- “若要执行，最终命中哪个 backend/profile/target？”

### 3. `execute`

目标：

- 根据 `preflight` 固化的执行计划提交任务、轮询状态、同步日志

只消费：

- `preflight` 输出
- 已授权的提交动作
- 最终脚本路径或运行命令

至少产出：

- `submission_state`
- `execution_state`
- `job_id` 或 `task_id`
- `remote_context`
- `local_log_dir`
- `synced_logs`
- `log_state`
- `sync_status`
- `evidence.execute`

不应做的事：

- 重新选择 backend
- 静默改 Host / region / queue
- 发现环境缺依赖后直接补装

推荐问题边界：

- “是否已经提交？”
- “任务现在处于什么状态？”
- “日志同步到了哪里？”

### 4. `diagnose`

目标：

- 基于执行证据给出基础失败分类
- 决定留在 runtime 继续诊断、回退 installer，还是回到上游补上下文

只消费：

- `execute` 输出
- 已同步日志
- 状态查询证据

至少产出：

- `failure_reason`
- `status_source`
- `log_readiness`
- `evidence.diagnose`
- `next_action`
建议只覆盖的失败分类：

- `submission_failed`
- `environment_not_ready`
- `logs_not_ready`
- `business_script_failed`
- `status_fallback_used`

等待超时或日志未就绪不应直接归类为业务脚本失败；只有日志和状态证据足够明确时，才归类为 `business_script_failed`。

不应做的事：

- 重新安装环境
- 直接改代码
- 接管完整测试矩阵

推荐问题边界：

- “这次失败更像是提交失败、环境失败，还是业务脚本失败？”
- “当前是否已有足够日志证据可交给下游？”

## 四、阶段间允许的跳转

只建议允许：

- `discover -> preflight`
- `preflight -> execute`
- `preflight -> installer`
- `preflight -> user_confirmation`
- `execute -> diagnose`
- `diagnose -> runtime`
- `diagnose -> installer`
不建议允许：

- `discover -> execute`
- `discover -> diagnose`
- `execute -> installer`

最后一种情况如果出现，说明 `preflight` 没把环境未 ready 提前识别出来。

## 五、最小交接样式

### `discover -> preflight`

```yaml
execution_mode: remote_slurm
access_mode: ssh
execution_channel: ssh_slurm
submission_target_candidates:
  - host: login-kunshan
    partition: hpctest01
backend_candidates:
  - slurm_dcu
hardware_profile_ref: slurm_dcu_output
missing_facts: []
evidence:
  discovery:
    source: ssh_config_and_hardware_profile
```

### `preflight -> execute`

```yaml
backend_id: slurm_dcu
runtime_profile_ref: remote_slurm_dcu
install_profile_ref: dcu_remote_install_profile
submission_target:
  host: login-kunshan
  partition: hpctest01
execution_readiness: ready_to_execute
confirmation_required: false
missing_fields: []
installer_fallback_required: false
evidence:
  preflight:
    template_fields_checked: true
```

### `execute -> diagnose`

```yaml
submission_state: submitted
execution_state: completed
job_id: "202605010001"
local_log_dir: .onescience/logs/job-202605010001
synced_logs:
  - 202605010001.out
  - 202605010001.err
log_state: synced
sync_status: synced
evidence:
  execute:
    status_probe: sacct
```

## 六、与执行主链的关系

- 环境发现已经内聚到 `discover`
- 基础执行诊断已经内聚到 `diagnose`

也就是说，运行链路不再依赖额外拆分 skill 来解释环境或消费日志证据。

## 七、一句话原则

`runtime` 的四阶段不是四个公开 skill，而是一条内部有状态流水线：先发现，再预检，再执行，最后诊断。
