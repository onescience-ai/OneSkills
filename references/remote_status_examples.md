# Remote Status Examples

本文件提供远程环境异常场景下的最终推荐输出示例。

## 示例 1：纯代码任务，但没有远程环境

适用场景：

- 用户只要求实现、改造或生成代码
- 当前没有远程配置

```yaml
task_type: 代码实现
reason: 当前目标是生成代码，不依赖远程运行
status: ok
recognized:
  - 当前请求属于代码实现阶段
  - 尚未进入远程运行链路
missing:
  - 远程环境未配置
can_continue_locally: true
next_action: onescience-coder
```

## 示例 2：远程描述模糊

适用场景：

- 用户只说“昆山 DCU”“某个 GPU 集群”
- 还不能唯一确定 Host 或队列

```yaml
task_type: 远程环境感知
reason: 用户提供了远程环境线索，但不足以唯一定位执行环境
status: need_clarification
recognized:
  - 用户提到目标环境为 DCU 集群
missing:
  - 具体 Host
  - 队列或分区
can_continue_locally: true
next_action: onescience-runtime
```

## 示例 3：运行任务被阻断

适用场景：

- 用户要求直接提交作业或远程运行
- 当前远程环境事实或运行配置不完整

```yaml
task_type: 远程运行
reason: 当前阶段必须依赖 discover 阶段产出的环境事实与运行配置
status: blocked
recognized:
  - 当前请求属于远程运行阶段
missing:
  - Host
  - 完整环境画像
  - onescience.json
  - tpl.slurm
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 4：远程环境部分可识别，但仍缺关键字段

适用场景：

- 已识别一个候选 Host 或平台类型
- 但还不能安全进入运行 / 安装阶段

```yaml
task_type: 远程环境补全
reason: 当前远程执行链路所需环境事实不完整
status: partial_context
recognized:
  - 已识别目标平台为 DCU
  - 已识别一个候选 Host
missing:
  - 队列或分区
  - module / conda 约束
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 5：backend 已识别，但 installer 尚未开放

适用场景：

- 已识别目标 backend
- 当前 installer 链路尚未开放

```yaml
task_type: 远程安装
reason: 当前 backend 已识别，但 installer 仍未开放
status: blocked
recognized:
  - 已识别 backend 为 slurm_cpu
  - runtime 已可继续推进
missing:
  - 稳定开放的 installer backend
can_continue_locally: false
next_action: onescience-installer
```

当前这类“链路未开放”的剩余示例主要适用于 `slurm_cpu` 的 installer；CPU-only runtime 与多机 GPU runtime 已转为 stable。

## 示例 6：SCnet MCP 服务不可用

适用场景：

- 用户明确要求走 SCnet
- 当前机器上的 SCnet MCP 已卸载、未安装或无法连通

```yaml
task_type: 远程运行
reason: 用户要求走 SCnet，但本地 MCP 服务当前不可用
status: blocked
recognized:
  - 当前请求显式命中 scnet_mcp 通道
missing:
  - 可调用的 SCnet MCP 服务
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 7：缺少完整环境画像

适用场景：

- 用户要求走 `ssh_slurm`
- 当前没有来自 discover 阶段的规范化环境画像

```yaml
task_type: 远程运行
reason: 当前请求进入 ssh_slurm 通道，但缺少完整环境画像
status: blocked
recognized:
  - 已识别这是远程运行任务
missing:
  - 完整环境画像
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 8：模板渲染字段缺失

适用场景：

- backend 与环境画像都已识别
- 但 `onescience.json` 缺少模板渲染必需字段

```yaml
task_type: 远程运行
reason: 当前运行配置缺少模板渲染所需字段
status: blocked
recognized:
  - 已识别 backend 与目标提交通道
missing:
  - cluster.memory
  - script.job_name
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 9：SCnet 队列不可访问

适用场景：

- 用户明确要求走 SCnet
- 当前区域下指定队列不可访问或不属于该区域

```yaml
task_type: 远程运行
reason: 当前 SCnet 区域与队列组合不可访问
status: blocked
recognized:
  - 当前请求显式命中 scnet_mcp 通道
missing:
  - 当前区域下可访问的队列
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 10：SCnet 远端路径不可写

适用场景：

- 用户明确要求走 SCnet
- 当前选定的远端上传路径没有写权限

```yaml
task_type: 远程运行
reason: 当前 SCnet 远端目标路径不可写
status: blocked
recognized:
  - 当前请求显式命中 scnet_mcp 通道
missing:
  - 可写的远端上传路径
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 11：是否切到 SCnet 仍需用户确认

适用场景：

- 当前上下文显示 SCnet 可能更合适
- 但用户并未明确要求走 SCnet MCP

```yaml
task_type: 远程运行
reason: 当前可推断 SCnet 可能更合适，但还缺用户通道确认
status: need_clarification
recognized:
  - 已推断候选执行通道为 scnet_mcp
missing:
  - 用户对执行通道的明确确认
can_continue_locally: false
next_action: user_confirmation
```

## 示例 12：本地代码入口不存在

适用场景：

- `onescience.json` 已存在
- 但 `runtime.script.code_path` 指向的本地入口脚本不存在

```yaml
task_type: 远程运行
reason: 当前运行配置指向了缺失的本地代码入口
status: blocked
recognized:
  - 已识别目标执行通道与运行配置
missing:
  - 可用的本地代码入口
can_continue_locally: false
next_action: onescience-coder
```

## 示例 13：当前硬件组合没有已登记 backend

适用场景：

- 已有硬件画像
- 但当前 CPU/accelerator/node_scope 组合没有命中任何已登记 runtime backend

```yaml
task_type: 远程运行
reason: 当前硬件组合没有对应的已登记 runtime backend
status: blocked
recognized:
  - 已识别目标为 ssh_slurm 运行任务
missing:
  - 可用的已登记 runtime backend
can_continue_locally: false
next_action: onescience-workflow
```

## 示例 14：已有 SCnet task_id，继续查状态并下载日志

适用场景：

- 用户已经给出 `SCnet task_id`
- 当前目标是查状态、定位任务并回收日志

```yaml
task_type: 远程运行
reason: 当前请求已经携带 SCnet task_id，应直接进入 runtime 单入口做状态查询与日志回收
status: ok
recognized:
  - 当前请求显式命中 scnet_mcp 通道
  - 已提供可用于匹配任务的 task_id
missing: []
can_continue_locally: false
next_action: onescience-runtime
```

## 示例 15：SCnet 任务状态查询失败后回退任务列表

适用场景：

- 已有 `SCnet task_id`
- 直接查状态失败，但可以继续回退到区域任务列表匹配最终状态

```yaml
task_type: 远程运行
reason: 当前任务状态直接查询失败，应回退到区域任务列表继续确认任务状态
status: ok
recognized:
  - 当前请求显式命中 scnet_mcp 通道
  - 已提供可用于匹配任务的 task_id
missing: []
can_continue_locally: false
next_action: onescience-runtime
```

## 使用建议

- 优先复用字段结构，不要随意增删核心字段
- `recognized` 只写已经确认的信息
- `missing` 只写当前阶段真正缺的内容
- `next_action` 指向最小下一步，而不是完整链路
