---
name: onescience-runtime
description: 【运行执行技能】在代码生成完成后，选择合适的执行通道（SSH/SLURM 或 SCnet MCP）提交任务、轮询状态并同步日志。不直接处理用户请求，需由上游技能调用。
---

# OneScience Runtime Skill

## 职责

在运行任务里：

1. 识别当前应走哪个 `execution_channel`
2. 在 `ssh_slurm` 通道里读取 `onescience-hardware`、`onescience.json` 与模板，生成并提交远程作业
3. 在 `scnet_mcp` 通道里通过本地 SCnet MCP 上传文件、提交任务、轮询状态并下载日志
4. 统一向下游返回作业状态、日志路径和下一步动作，供 `onescience-debug` 分析

需要进一步判断字段归属或层间交接时，读取 `./references/runtime_contract.md`。
需要走 SCnet MCP 通道时，读取 `./references/scnet_channel.md`。
需要处理“远程环境未配置”或“远程信息不完整”的异常场景时，读取 `../../references/remote_fallback.md`。

## 执行通道

`onescience-runtime` 是统一运行入口，但内部区分两个执行通道：

- `execution_channel=ssh_slurm`
- `execution_channel=scnet_mcp`

### `ssh_slurm`（默认通道）

适用场景：

- 用户要求读取 `onescience.json`
- 用户要求基于 `tpl.slurm` 或现有 SLURM 配置提交
- 上游已经提供完整硬件画像与 backend 选择
- **这是默认提交方式，除非用户明确要求使用 SCnet MCP**

### `scnet_mcp`（需用户确认）

适用场景：

- 用户明确提到 `SCnet` 并要求使用 MCP 提交
- 请求里直接出现区域、队列、`task_id`、下载日志、MCP 提交
- **重要：如果用户未明确要求使用 SCnet MCP，不得自动切换到该通道**
- **如果当前环境可能支持 SCnet MCP 但用户未明确说明，必须先向用户确认是否使用**

## 输入约定

### `ssh_slurm` 通道

- `onescience.json` 位于当前项目根目录，属于用户项目级运行配置
- `runtime.backend_id` 当前稳定值为 `slurm_dcu` 或 `slurm_gpu`
- `runtime.target` 描述调度器类型、平台类型和主加速卡类型
- `runtime.environment` 描述 CPU / accelerator 默认环境与运行能力
- `tpl.slurm` 优先位于当前项目根目录；如果缺失，必须回退读取本 skill 自带的 `./assets/tpl.slurm`
- `runtime.script.code_path` 是用户代码脚本路径
- `runtime.script.path` 是生成后的作业脚本路径
- `runtime.logs` 描述日志等待与同步策略
- `runtime.submission` 描述远程提交授权策略
- 完整硬件画像提供 Host、平台、队列、模块和环境约束
- `skills/onescience-runtime/assets/backend_specs.json` 是 backend selector、support matrix、template 与 render field 的统一登记表

如果缺少项目级 `onescience.json`，应停止 `ssh_slurm` 通道提交并回到 `onescience-workflow` 完成初始化。不要在 runtime 中生成伪配置，也不要提交远程作业。

### `scnet_mcp` 通道

- 当前环境已安装并可调用 SCnet MCP
- 用户请求或上游上下文中应能提供本地脚本路径、运行命令，或可由当前工作流生成这些信息
- 可选输入包括：区域偏好、队列偏好、现有 `task_id`、是否需要下载日志
- 这个通道不依赖 `onescience.json`、`tpl.slurm` 或 SSH 上下文

如果当前机器未安装、已卸载或暂时无法调用 SCnet MCP：

- 把该请求判定为外部依赖阻断
- 可以继续完成文档、资产、路由和静态 QA 校验
- 不要伪造“已完成真实 SCnet 回归”的结论

## 执行流程

1. 先确定 `execution_channel`
2. 如果是 `ssh_slurm`：
   - 校验 `runtime.script.code_path` 是否存在，并查找 `onescience.json` 与 `tpl.slurm`
   - **检查完整硬件画像中是否已明确 Host 信息**：
     - 如果硬件画像中未提供 Host 或 Host 信息模糊（例如有多个可用 Host 但未选择），**必须暂停执行并向用户确认**
     - 向用户展示可用的 Host 列表（来自 `~/.ssh/config` 或上游硬件感知结果）
     - 等待用户明确选择后，再继续后续步骤
   - 读取完整硬件画像中的 Host、平台、队列、模块和环境信息
   - 从 `onescience.json` 提取 backend、目标平台、环境、集群、模块、conda、脚本和环境变量配置，并对照 `backend_specs.json`
   - 先确认完整硬件画像与 `runtime.backend_id` 是否匹配，再确认 `support_matrix.runtime` 是否允许继续执行，最后基于模板生成运行脚本
   - 创建远程连接，并把提交脚本与用户代码脚本传到远端环境
   - 在远端执行运行命令或 `sbatch` 提交命令
3. 如果是 `scnet_mcp`：
   - 读取可用区域与队列，必要时发现当前可访问队列
   - 校验远端文件落点是否可写；不要默认向 `/` 创建目录，也不要假设 `create_folder` 一定有权限
   - 如果目录创建受限，优先直接上传到用户家目录或家目录下已存在可写目录；不要把 `./tmp` 当成默认首选
   - 上传本地脚本或输入文件
   - 显式指定 `region` 与 `queue` 提交任务
   - 必要时先跑轻量探针命令确认 `python3` / `python` / `module`
   - 轮询状态时优先走 `scnet_get_task_status`；如果已知 `task_id` 存在但接口返回 404 / `NoneType` 类异常，回退到 `scnet_list_regions_tasks(region=...)`
   - 日志下载如果只拿到 `{\"code\":\"911020\",\"data\":null,\"msg\":\"File does not exist\"}` 这类占位结果，视为日志尚未就绪，继续轮询，不要把占位内容当成真实 stdout / stderr
4. 两个通道都统一负责：
   - 处理提交授权
   - 轮询作业状态直到完成、失败或超时
   - 把日志同步或下载到本地目录
   - 返回任务 ID、提交目标、本地日志路径和同步状态

## 远程提交授权规则

- 同一个用户请求或同一条 OneScience 工作流里，远程提交业务确认最多发生一次
- 如果用户已经明确要求“提交远程运行”“跑一下”“验证运行”“提交到 slurm”“提交到 SCnet”等执行动作，不要再额外询问是否提交
- 如果用户只要求生成代码或方案，不要自动提交远程作业
- 一旦进入运行闭环，后续 `scp`、`ssh`、`sbatch`、SCnet 提交、状态轮询、日志同步和同配置重试，都复用本次工作流的提交授权
- 如果后续动作会改变目标 Host、队列/分区、运行入口脚本、资源规模，或从测试运行升级成长时间正式训练，应重新确认
- 业务授权状态只在当前用户请求或当前工作流内有效，不写入 `onescience.json`

## 日志同步规则

- 日志同步属于 `onescience-runtime` 的职责
- `onescience-debug` 只消费 runtime 已同步的本地日志；只有 runtime 明确报告未同步且仍有远端上下文时，debug 才按需读取远端日志
- 本地日志目录默认是 `.onescience/logs/<job_id>/`
- `ssh_slurm` 通道的远端日志目录默认是 `logs`
- `ssh_slurm` 默认同步 `*.out` 与 `*.err`
- `scnet_mcp` 通道默认下载平台任务关联的标准输出与错误日志
- 同步失败时，应报告 `sync_status=failed`、失败原因和远端日志路径
- 作业提交成功但等待超时，应返回 `job_status=running_or_unknown` 与 `sync_status=skipped_timeout`

## `ssh_slurm` 通道的 backend 与模板规则

- backend 选择、source template 与链路支持边界以 `backend_specs.json` 为准
- `tpl.slurm` 是项目根目录的兼容模板入口
- 模板查找优先级是项目根目录 `tpl.slurm`，其次是本 skill 的 `./assets/tpl.slurm`
- 使用 skill 资产模板时，不要要求用户先手动复制模板；可以直接生成脚本，但输出必须说明模板来源
- 允许做变量替换，不允许改模板结构
- runtime 支持不等于 installer/debug 也支持；跨链路判断必须看 `support_matrix`
- 缺失变量时，优先报告配置问题，不要静默猜测

## 约束

- 不要引用 `.trae/skills/onescience.json` 之类的私有路径
- 不要自动修改用户的 `onescience.json`
- 不要在 `ssh_slurm` 通道里跳过 `onescience-hardware` 已确认的硬件约束
- **不要在 Host 信息未确认时自动选择或假设默认 Host**
- **如果硬件画像中未明确 Host 或有多个 Host 可选，必须先向用户确认，不要自行选择**
- 不要把代码生成交接摘要误用为完整硬件画像
- 不要在代码尚不存在时直接提交空作业
- 不要把 `support_matrix.runtime=stable` 误解成 installer/debug 也稳定
- 不要在 `scnet_mcp` 通道里依赖失效默认队列；区域切换后必须重新取该区域可访问队列
- 不要在未确认权限时向 SCnet 远端根目录创建目录
- 不要把排队阶段返回的占位日志内容当成真实运行日志交给 `onescience-debug`
- 当运行任务依赖远程事实但信息缺失时，返回阻断，不要假设默认 Host、队列或区域

## 输出要求

至少给出：

1. `execution_channel`
2. 使用的配置文件路径，或使用的 `region` / `queue`
3. 选择的远程主机，或远端上传路径
4. 生成的提交脚本路径，或运行命令 / 探针命令
5. 作业 ID 或提交失败原因
6. 远端日志路径与日志查看方式
7. 本地日志同步目录
8. `sync_status`
9. 已同步的日志文件列表；若为空，说明原因

如果是 `scnet_mcp`，建议额外给出：

10. `observations.status_source`：当前状态来自 `scnet_get_task_status` 还是 `scnet_list_regions_tasks`
11. `observations.log_readiness`：日志是否已经可下载，避免把占位结果误判成真实输出

**如果需要向用户确认 Host 信息**，额外给出：

10. `confirmation_required=true`
11. `available_hosts`：可用 Host 列表
12. `missing_info`：缺失的具体信息说明
13. `suggested_action`：建议用户如何配置或选择
