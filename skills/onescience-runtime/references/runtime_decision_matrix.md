# Runtime Decision Matrix

本文件用于把 `onescience-runtime` 的关键决策规则整理成可快速查阅的矩阵，避免规则只分散在 `SKILL.md` 叙述里。

目标不是重复所有执行细节，而是明确：

- 什么时候必须阻断
- 什么时候必须向用户确认
- 什么时候可以继续执行
- 什么时候应该回退到上游 skill 或当前通道自身处理

## 一、统一判断顺序

`onescience-runtime` 处理运行请求时，顺序固定为：

1. `discover`：提取用户语义中的环境线索，先标记为候选事实
2. `discover`：判断 `execution_mode`
3. `discover`：判断当前通道前置条件是否满足
4. `preflight`：通过实际接入通道确认候选环境事实
5. `preflight`：判断输入是否完整
6. `preflight`：判断是否需要用户确认
7. `preflight`：判断当前 backend / 平台是否处于支持边界内
8. `execute`：进入提交、轮询、日志同步闭环
9. `diagnose`：基于执行证据给出基础失败分类

不要跳过前面的判断，直接提交作业。

## 二、语义环境线索确认规则

用户说出的环境信息只能先作为候选，例如 Host、队列、分区、SCnet 区域、GPU/DCU/CPU、module、conda 环境或远端路径。runtime 不应把这些语义线索直接当成 `hardware_profile`、`submission_target` 或已确认 backend。

| 语义线索 | 确认通道 | 未确认时动作 |
| --- | --- | --- |
| Host / partition / SLURM 队列 | SSH / SLURM 只读探针 | `confirmation_required=true` 或阻断 |
| GPU / DCU / CPU 类型 | `hardware_profile` 探测与 backend selector | 只作为 backend candidate |
| module / conda / driver stack | 远端只读命令或已有硬件画像 | 未确认前不得判定 ready |
| SCnet region / queue | SCnet 通道返回结果或 `scnet-chat` 委托结果 | 由 `scnet_mcp` 路由发现或阻断 |
| SCnet task_id | SCnet 通道状态结果或 fallback 结果 | 只查状态，不重新提交 |
| 远端路径 | SSH / SCnet 可写性检查 | 不可写则阻断或回退可写目录 |

确认后才能升级为：

- `hardware_profile`
- `submission_target`
- `backend_id`
- `runtime_profile_ref`
- `execution_readiness=ready_to_execute`

## 三、执行模式矩阵

当前使用：

- `execution_mode=local`
- `execution_mode=local_slurm`
- `execution_mode=remote_slurm`
- `execution_mode=remote_direct`

推荐映射：

- `execution_channel=local_direct` -> `local + local`
- `execution_channel=local_slurm` -> `local_slurm + local`
- `execution_channel=ssh_slurm` -> `remote_slurm + ssh`
- `execution_channel=scnet_mcp` -> `remote_direct + cloud_api`（SCnet 路由标签；命中 SCnet 作业、文件、账户、区域、队列或集群相关需求时，直接调用 `scnet-chat` 技能执行）

| 条件 | 结论 | 下一步 |
| --- | --- | --- |
| 用户明确要求 `SCnet` / MCP 提交 | `execution_mode=remote_direct` | 进入 `scnet_mcp` 路由；命中 SCnet 作业、文件、账户、区域、队列或集群相关需求时，直接调用 `scnet-chat` 技能执行 |
| 请求里直接出现 `region` / `queue` / `task_id` / 下载日志 | `execution_mode=remote_direct` | 进入 `scnet_mcp` 路由；命中对应 SCnet 需求时，直接调用 `scnet-chat` 技能执行 |
| 用户明确要求读取 `onescience.json` / `tpl.slurm` / `sbatch` | `execution_mode=remote_slurm` | 进入 `remote_slurm` 规则 |
| 用户只说“提交远程运行”，未提 SCnet | 默认 `execution_mode=remote_slurm` | 进入 `remote_slurm` 规则 |
| 用户未明确要求执行，只是在改代码或做方案 | 不进入运行闭环 | 回到 `onescience-coder` 或上游 skill |

补充约束：

- 未经用户明确要求，不要把默认 `remote_slurm` 自动切到 `remote_direct`
- 显式 `SCnet` 请求也不要降格成 `remote_slurm`
- 远程执行意图一旦明确，不得再插入本地业务执行作为前置验证；本地只保留 `local_preparation`

### 远程意图与本地准备边界

| 场景 | 允许的本地动作 | 禁止的本地动作 |
| --- | --- | --- |
| 用户明确要求远程执行 / 远程测试 / 提交到 SCnet | 文件存在性检查、提交清单、命令模板渲染、提交脚本生成、静态语法检查 | 本地执行测试脚本、训练脚本、业务入口脚本、`pytest`、`python script.py`、import 运行依赖 |
| 用户明确要求提交到 SLURM | `onescience.json` / `tpl.slurm` / backend 字段核对、提交脚本渲染 | 用本地 `bash` / `python` 替代 `sbatch` 进行业务验证 |
| 用户未要求执行，只要求生成代码或方案 | 可停留在上游 skill | 自动提交远程作业或本地运行脚本 |

远程意图下的本地准备阶段建议统一命名为 `local_preparation`，并在 evidence 中记录 `local_execution=skipped_by_remote_intent`。本地依赖缺失只能说明本机环境不可运行，不能作为远程环境或 SCnet 队列环境的失败结论。

## 四、`remote_slurm` 决策矩阵

### 1. 前置输入检查

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| 缺少 `onescience.json` | 阻断 | 回到 `onescience-workflow` 完成初始化 |
| 缺少用户代码入口 `runtime.script.code_path` | 阻断 | 回到 `onescience-coder` 或用户输入补齐 |
| 缺少完整环境画像 | 阻断 | 留在 `onescience-runtime` 补齐环境事实 |
| `runtime.backend_id` 与硬件画像 selector 不一致 | 阻断 | 报告配置/环境不一致 |
| `support_matrix.runtime = planned` | 可继续留在 runtime | 完成模板/字段核对并返回 `backend_not_stable`，不做真实提交 |
| `support_matrix.runtime = unsupported_for_now` | 阻断 | 报告 backend 未开放运行 |

建议对“当前硬件组合根本没有命中已登记 backend”的返回，收口成与
`skills/onescience-runtime/assets/examples/ssh_slurm_runtime_result_backend_not_supported.json`
一致的结构化结果。

当前仓库已无 `support_matrix.runtime = planned` 的 backend；如果未来新增 planned runtime backend，仍应收口到统一的 `backend_not_stable` 结构化结果，避免不同维护者各自发明字段。

建议对“缺少 `onescience.json`”的返回，收口成与
`skills/onescience-runtime/assets/examples/ssh_slurm_runtime_result_missing_runtime_config.json`
一致的结构化结果，避免把配置缺失、backend 阻断和 host 确认混成同一类错误。

建议对“缺少完整硬件画像”的返回，收口成与
`skills/onescience-runtime/assets/examples/ssh_slurm_runtime_result_missing_hardware_profile.json`
一致的结构化结果。

建议对“缺少用户代码入口”的返回，收口成与
`skills/onescience-runtime/assets/examples/ssh_slurm_runtime_result_missing_code_path.json`
一致的结构化结果。

建议对“模板字段缺失”的返回，收口成与
`skills/onescience-runtime/assets/examples/ssh_slurm_runtime_result_template_fields_missing.json`
一致的结构化结果，并显式列出缺失字段。

### 2. Host 与提交目标确认

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| Host 已通过 SSH / SLURM 通道确认且唯一 | 继续 | 进入模板渲染/提交 |
| Host 缺失 | `confirmation_required=true` | 向用户展示可选 Host |
| Host 有多个候选但未选定 | `confirmation_required=true` | 向用户确认目标 Host |
| partition 与硬件画像不一致 | 阻断 | 先校准配置，不直接提交 |

### 3. 探针与提交流程

| 场景 | 推荐动作 | 说明 |
| --- | --- | --- |
| 环境信息完整、模板字段齐全 | 可直接 `sbatch` | 这是当前默认闭环 |
| 远端 Python / module 可用性不确定 | 先进入已确认 module / conda 环境，再做轻量探针 | 探针失败先阻断，不提交空作业 |
| module / conda 激活后 torch 仍不可用 | 回退 `onescience-installer` | runtime 只确认 readiness，不执行安装或修复 |
| 需要 `conda create` / `pip install` / 工作区同步 | 回退 `onescience-installer` | environment mutation 不属于 runtime |
| 只做运行入口连通性验证 | 允许最小探针脚本 | 仍需保留统一结果输出 |
| 缺失关键渲染字段 | 阻断 | 报告字段缺失，不静默猜测 |

当前默认提交模式：

- 调度后端为 `slurm`
- 正式作业提交优先 `sbatch`
- `bash/python` 仅用于远端轻量探针、提交脚本内部命令或用户未明确远程执行时的非调度最小验证；远程意图明确时，不应在本地用 `bash/python` 替代正式提交

## 五、`remote_direct`（`scnet_mcp`）决策矩阵

### 1. 前置条件检查

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| 本地 SCnet 接入可调用 | 继续 | 进入 `scnet_mcp` 路由，并优先委托 `scnet-chat` 处理已覆盖的平台操作 |
| 本地 SCnet 接入未安装、已卸载或连接失败 | 阻断 | 标记外部依赖阻断，不伪造真实回归 |
| 用户未明确要求 SCnet，但上下文“可能”适合 SCnet | 需确认 | 向用户确认是否改走 SCnet |

建议对“需确认是否改走 SCnet”的返回，收口成与
`skills/onescience-runtime/assets/examples/scnet_mcp_runtime_confirmation_required.json`
一致的结构化结果。

### 2. 区域与队列

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| 区域已确认，队列也来自该区域 | 继续 | 直接调用 `scnet-chat` 技能执行平台动作，runtime 记录结果 |
| 区域已确认，但队列未明确 | 继续 | 由 `scnet-chat` 发现该区域可访问队列，再显式选择 |
| 切换了区域 | 继续 | 必须重新获取该区域队列 |
| 队列来自旧区域或无访问权限 | 阻断 | 重新选择当前区域可访问队列 |

### 3. 目录与日志

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| 远端目标目录明确且可写 | 继续 | 上传并提交 |
| 根目录创建受限 | 回退 | 优先上传到用户家目录或已存在可写目录 |
| 日志下载结果是占位 JSON | 不视为失败 | 记录 `log_readiness=not_ready`，继续轮询 |
| `get_task_status` 对已知任务失效 | 回退 | 改走 `list_regions_tasks` 匹配 `task_id` |

### 4. 软件环境 readiness

| 检查项 | 结果 | 动作 |
| --- | --- | --- |
| 目标队列内 DAS / torch probe ready | 继续 | 可进入正式 execute |
| module 加载后 `python3` 指向 DAS Python | 阻断或重探 | 先保存 conda Python，再加载 module，不把 DAS Python 的 torch 缺失当成 conda 环境失败 |
| 裸 `python3` 失败但 DAS probe ready | 继续 | 以目标软件环境 probe 为准 |
| `libgalaxyhip.so.5` / HIP 动态库缺失 | 阻断 | 优先判定 DTK/HIP runtime 未进入 `LD_LIBRARY_PATH`，检查 SGHPC/DAS module |
| DAS / torch probe 不 ready | 阻断 | 返回 `torch_not_ready` 或 `python_not_ready`，下一步交给 installer |
| 需要创建 conda 环境或安装依赖 | 回退 | 交给 `onescience-installer` |

## 六、统一输出状态机

建议后续所有 runtime 结果都按下面语义收口，即使字段名暂未全部实现，也应保持判断一致。

### 1. `submission_state`

- `not_started`
- `confirmation_required`
- `submitted`
- `failed`

### 2. `execution_state`

- `blocked`
- `queued`
- `running`
- `completed`
- `running_or_unknown`
- `failed`

### 3. `log_state`

- `not_started`
- `not_ready`
- `partial`
- `synced`
- `failed`
- `skipped_timeout`

### 4. `next_action`

- `onescience-runtime`
- `onescience-installer`
- `onescience-coder`
- `onescience-workflow`
- `user_confirmation`

### 5. `blocking_reason`

建议统一落在有限集合内，例如：

- `missing_runtime_config`
- `missing_hardware_profile`
- `missing_code_path`
- `host_not_confirmed`
- `backend_not_supported`
- `backend_not_stable`
- `template_fields_missing`
- `scnet_service_unavailable`
- `queue_not_accessible`
- `remote_path_not_writable`
- `scnet_channel_not_confirmed`

## 七、诊断阶段的稳定输出面

无论当前通道是什么，`diagnose` 阶段至少稳定保留：

- `execution_channel`
- `submission_target`
- `job_id` 或 `task_id`
- `job_status`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- 必要时的 `observations`

## 八、一句话原则

`onescience-runtime` 不是“拿到脚本就提交”，而是“先做通道判断和输入校验，再进入可解释、可回退、可同步日志的运行闭环”。

如果需要更细的 phase 输入/输出交接，读取 `runtime_phase_handoffs.md`。
