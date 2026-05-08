# SCnet Runtime Channel

本文件定义 `onescience-runtime` 在 `execution_channel=scnet_mcp` 时的提交流程、路径约束与错误对照。

## 通道前置条件

`scnet_mcp` 是依赖本地 SCnet MCP 服务的外部执行通道，不是仓库内部自带能力。

进入该通道前至少确认：

- 当前机器仍安装了 SCnet MCP
- 当前会话还能正常调用 SCnet MCP 接口
- 需要真实回归时，维护记录里要显式写明本次使用的本地环境可访问该服务

如果服务已卸载、未安装或连接不可用：

- 将状态标记为 `blocked`
- 允许继续完成静态契约、文档、路由与安装器校验
- 不要把这类失败归因为 runtime 逻辑回归，除非已证明确实能连通 MCP

## 何时选择 `scnet_mcp`

满足以下任一条件时，runtime 应优先选择 `scnet_mcp`：

- 用户明确提到 `SCnet`
- 请求里直接出现区域、队列、`task_id`、下载日志、MCP 提交
- 目标是把本地最小脚本或现有脚本直接上传到 SCnet 做真实执行验证

## 最小闭环

1. `scnet_list_regions`
2. `scnet_get_resources(region=...)`，或直接使用 `scnet_list_regions` 返回的队列
3. `scnet_upload_file(local_path=..., region=...)`
4. `scnet_submit_task(region=..., queue=..., command=...)`
5. `scnet_get_task_status(task_id=..., region=...)`
6. `scnet_download_log(task_id=..., region=..., log_type=stdout/stderr)`

如果任务本身是“先生成代码再提交”，先让上游 `onescience-coder` 在本地生成脚本，并尽量先本地跑一遍最小验证。

如果 `scnet_get_task_status` 已不能稳定返回旧任务或已完成任务状态：

7. 回退到 `scnet_list_regions_tasks(region=...)`
8. 通过 `task_id` 匹配当前任务，再解释 `statQ / statR / statC`

## 目录与权限规则

### 1. 不要默认在 `/` 下创建目录

实测里，直接在根目录创建文件夹可能返回：

- `创建文件夹失败: Insufficient authority, prohibit operation`

默认策略：

- 优先直接上传到用户家目录或家目录下已存在的可写目录
- 若确实需要目录，先用 `list_files` 或 `file_exists` 判断家目录下的目标目录是否可写
- 需要临时目录时，优先在家目录下选择已存在或可写的位置；`./tmp` 只作为明确验证可写后的兜底选择
- 如果 `create_folder` 返回 `Insufficient authority, prohibit operation`，不要继续重试根目录建目录

### 2. 区域文件系统相互隔离

上传、日志下载、远端文件列表都依赖区域。

执行要求：

- 上传脚本用哪个 `region`，提交任务、查状态、下载日志就继续用哪个 `region`
- 不要把一个区域里的远端路径拿去另一个区域直接提交

## 队列选择规则

### 1. 先看该区域真实可用队列

不要依赖本地环境里的历史默认值。即使用户没给 `queue`，也先从：

- `scnet_list_regions`
- `scnet_get_resources(region=...)`

读取当前区域可访问队列，再显式提交。

### 2. 切区后不要复用旧队列

常见错误：

- 切到新区域后仍沿用旧区域默认队列
- 返回 `未找到可访问的队列`

修复动作：

- 显式传 `queue`
- 该 `queue` 必须来自当前 `region` 的返回结果

### 3. `account/partition` 组合错误通常不是脚本问题

常见错误：

- `Batch job submission failed: Invalid account or account/partition combination specified`

修复动作：

- 更换当前区域下另一个有权限的队列
- 或改到另一个用户确实有权限的区域
- 不要在脚本内容上浪费时间

## 运行环境探测

某些队列里不保证 `python3` 在 `PATH`。

如果解释器不确定，先提交轻量探针：

```bash
which python3 || which python || ls -1 /usr/bin/python* /usr/local/bin/python* 2>/dev/null || echo NO_PYTHON_FOUND
```

如果需要进一步判断 module，可再补一条只读探针：

```bash
module avail 2>/dev/null || echo NO_MODULE_CMD
```

## 状态与日志判定

### 1. `completed` 只代表调度完成

任务状态 `completed` 后，仍然必须检查：

- 标准输出 `.out`
- 错误日志 `.err`

典型场景：

- 调度成功
- 业务脚本失败
- `.err` 里出现 `python3: command not found`

### 2. `scnet_get_task_status` 失败时要回退

实测里，已完成任务后续再查时，可能出现：

- `error_code: 404`
- `message: 获取任务状态失败: 'NoneType' object has no attribute 'get'`

处理方式：

1. 不要直接把它判成任务不存在
2. 继续调用 `scnet_list_regions_tasks(region=...)`
3. 用 `task_id` 在该区域任务列表中匹配状态
4. 把最终状态来源记录为 `status_source=scnet_list_regions_tasks`

### 3. 排队阶段日志可能尚未生成

实测里，任务仍在 `queued` / `starting` 阶段时，下载日志可能得到一个“下载成功但文件内容是占位 JSON”的本地文件，例如：

- `{"code":"911020","data":null,"msg":"File does not exist"}`

处理方式：

1. 不要把这个内容当成真实 `.out/.err`
2. 记录 `log_readiness=not_ready`
3. 保持 `sync_status=not_started` 或 `partial`
4. 继续轮询任务状态，等日志真正生成后再下载

### 4. 本地日志才是下游 debug 的稳定输入

下载日志后，把本地日志路径交给 `onescience-debug`，不要让 debug 直接依赖远端临时状态。

## MCP 侧异常

### `Transport closed`

含义：

- MCP 连接中断
- 不能据此直接判断远端任务提交失败或成功

处理方式：

1. 先重试一个轻量接口，例如 `scnet_list_regions` 或 `scnet_interaction_manual`
2. 如果连接恢复，再继续提交或查状态
3. 如果连接未恢复，停止新增推断，只报告“当前无法继续向平台发起调用”

### `Service unavailable / not installed`

含义：

- 本机未安装 SCnet MCP
- 或该服务已被卸载，当前会话根本无法发起 MCP 调用

处理方式：

1. 停止真实提交流程
2. 在结果中明确写出“环境阻断，不是作业结果”
3. 把剩余工作收束到文档、资产、静态 QA 和待恢复回归计划
