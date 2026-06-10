# Routing Matrix

本文件给 `onescience-skill` 提供稳定的执行层路由决策表。

## 顶层判断

如果用户主要在问：

- 科研任务该怎么推进
- 属于哪个工作流
- 不同领域人员会怎么理解这个任务

先转给 `onescience-workflow`。

如果用户主要在问：

- 当前该由哪个科研角色推进
- 角色怎么接力
- 角色之间如何交接

先转给 `onescience-role`。

如果输入已经包含 `onescience-role` 的 `execution_entry` 与 `handoff_artifacts`，执行层应优先消费这两个字段来选择最小执行链。不要在 `onescience-skill` 中重新判断 `domain_route`、`domain_task_family`、角色链或领域任务桶。

## 执行层原则

当前公开执行技能为：

1. `onescience-runtime`
2. `onescience-installer`

## 最小技能链优先级

先问自己：用户最终要交付什么？

1. 只是实现或修改代码
   -> `onescience-coder`
2. 只是运行、提交、生成脚本、查状态、下载日志
   -> `onescience-runtime`
3. 只是安装或修复执行环境
   -> `onescience-installer`
4. 只是验证、测试、排查
   -> 优先 `onescience-runtime` 的 `diagnose` 路径

如果一个请求同时命中多个阶段，优先选择覆盖目标所需的最短链路，而不是默认拉起全流程。

## 组合链路

### 1. 面向远程环境实现

适用信号：

- “按某个 DCU / GPU / SLURM 环境适配代码”
- “先识别 Host / 队列，再生成训练或推理代码”

技能链：

`onescience-coder`

补充说明：

- 如果代码实现必须知道远程事实，可由上游附带环境线索；不要默认显式拉起额外环境识别 skill

### 2. 实现并运行

适用信号：

- “写完代码后直接跑起来”
- “补齐训练入口并提交到 slurm”
- “实现后验证运行”
- “生成验证脚本并实际执行”
- “先写代码，再本地跑一下前向 / 最小验证”

技能链：

`onescience-coder -> onescience-runtime`

传递规则：

- 给 `onescience-runtime`：项目运行配置、本地脚本路径、环境事实线索
- 若未显式指定远程环境，且目标是本地最小验证，默认按 `execution_mode=local`、`access_mode=local` 继续
- 不要把“已生成验证脚本”误判为“已完成运行验证”
- 由 runtime 内部做 `discover/preflight`

### 3. 实现并通过 SCnet 运行

适用信号：

- “生成代码后提交到 SCnet 跑一下”
- “用本地 SCnet MCP 提交任务”

技能链：

`onescience-coder -> onescience-runtime`

传递规则：

- 给 `onescience-runtime`：`execution_mode=remote_direct`、`access_mode=cloud_api`
- 如需显式标注通道，可同时传 `execution_channel=scnet_mcp`

### 4. 已有代码，只做运行

适用信号：

- “当前工程已有脚本，直接提交”
- “读取 onescience.json 并运行”

技能链：

`onescience-runtime`

### 5. 环境安装或修复

适用信号：

- “在 DCU 环境安装 OneScience”
- “初始化远程依赖”
- “环境缺包，帮我修一下”

技能链：

`onescience-installer`

### 6. 运行后排查

适用信号：

- “作业报错，帮我看日志”
- “loss 异常，帮我排查”

默认技能链：

- 若已有运行产物：`onescience-runtime`
- 若仍需重新执行并诊断：`onescience-runtime`
## 关键词到技能

- “角色、岗位、职责、交接、谁来做、科研流程分工” -> `onescience-role`
- “科研任务、工作流、领域、阶段、我想做什么、怎么推进” -> `onescience-workflow`
- “实现、改造、接入、生成代码” -> `onescience-coder`
- “SCnet、区域、队列、task_id、下载日志、MCP 提交” -> `onescience-runtime`
- “提交、运行、slurm、作业、集群” -> `onescience-runtime`
- “测试、验证、排查、debug、loss 异常” -> `onescience-runtime`
- “安装、环境、依赖、初始化、修环境” -> `onescience-installer`

## 缺失项处理

- 缺少远程环境事实：优先进入 `onescience-runtime` 的 `discover/preflight`
- 缺少 SCnet 区域或队列：先走 `onescience-runtime` 的 `scnet_mcp` 发现
- 缺少 `onescience.json` / `tpl.slurm`：仅阻塞 `remote_slurm` 运行链路
- 缺少源码上下文：先说明要读哪些目录或文件
- 只有代码生成需求：不要强行补 `runtime` 或 `installer`

## Backend 状态处理

当环境事实已经通过 runtime / installer 的实际接入通道确认，并能归一化为某个 `backend_id` 时，执行层除选择技能链外，还应显式暴露：

- `backend_id`
- `backend_status`
- `execution_readiness`

处理原则：

- 命中已支持 backend 时，可继续进入对应执行技能
- 命中 `planned_backend` 且目标是 runtime 时，可继续进入 runtime，但必须显式披露当前仍是 planned backend
- 命中 `unsupported_for_now` 时，应明确阻断对应阶段
- backend 已支持但环境未 ready 时，优先回退到 installer 或让 runtime 报出阻断原因

## 常见误路由

### 错误 1：纯代码任务也拉起运行链

后果：

- 无意义增加上下文
- 让 `coder` 和 `runtime` 职责混杂

### 错误 2：运行前就把安装链强行混进运行链

后果：

- 安装与提交职责混淆
- 环境修复与作业执行边界不清

### 错误 3：显式 SCnet 请求硬改成 `remote_slurm`

后果：

- 强行要求 `onescience.json`、`tpl.slurm` 或 SSH 信息
- 忽略平台 API 的区域隔离、队列访问和错误面
