---
name: onescience-skill
description: OneScience 执行层编排入口。用于把用户工作流结论或角色层结论路由到硬件感知、代码实现、统一运行入口、结果排查或环境安装等最小执行链路。
---

# OneScience 执行层技能管理器

你负责把用户工作流结论或角色层结论路由到合适的执行技能，不要无条件拉起完整流水线。

当你需要判断最小技能链、组合链路、关键词映射或常见误路由时，读取 `./references/routing_matrix.md`。
当你需要判断跨 `hardware/runtime/installer/debug` 的共享 backend 语义时，读取 `../../references/shared_contracts.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## 路由原则

1. 先识别用户目标，再选择**最小技能链**。
2. 如果用户主要在问“我想完成什么科研任务、属于哪个领域、应该走哪类工作流”，优先转到 `onescience-workflow`。
3. 如果用户主要在问“当前该由哪个科研角色推进、角色如何接力、交接物是什么”，优先转到 `onescience-role`。
4. 当任务最终要跑在远程硬件上时，优先先做 `onescience-hardware` 感知，再进入代码生成。
5. 如果用户明确要求通过本地 SCnet MCP 提交、查状态或下载日志，仍然进入 `onescience-runtime`，但要显式选择 `execution_channel=scnet_mcp`，不要强行要求 `onescience.json`、`tpl.slurm` 或 SSH 上下文。
6. 纯分析、纯规划、纯代码实现，不要强行进入运行或调试阶段。
7. 只有当用户明确要求运行、提交、验证、排查时，才继续调用 `onescience-runtime` 或 `onescience-debug`。
8. 不要引用不存在的隐藏路径；运行配置默认来自项目根目录的 `onescience.json` 与 `tpl.slurm`。

## 路由要求

- 优先按用户最终交付目标选择最小技能链
- 若输入已经包含 `user_intent` / `detected_domain` / `workflow_type` / `workflow_handoff`，优先消费工作流层结论
- 若输入已经包含 `current_role` / `role_chain` / `handoff_artifacts` / `execution_entry`，优先消费角色层结论
- 需要细分链路或判断组合场景时，查看 `./references/routing_matrix.md`
- 如果请求同时包含“远程环境 + 代码 + 运行”，默认按 `onescience-hardware -> onescience-coder -> onescience-runtime` 编排
- 如果请求明确包含“SCnet + 代码 + 提交”，默认按 `onescience-coder -> onescience-runtime` 编排，并传递 `execution_channel=scnet_mcp`
- 如果 `onescience-hardware` 已能识别 `backend_id`，则在进入 `runtime` / `installer` / `debug` 前，显式说明当前 backend 是 `stable_backend`、`planned_backend` 还是 `unsupported_for_now`

## 上下文传递

在调用下游技能前，整理并传递这些信息：

- 用户原始目标
- 当前项目路径与相关文件
- 本地待上传脚本路径、SCnet 区域偏好、队列偏好、现有 `task_id`、期望 `execution_channel`
- 数据集名、模型名、任务类型
- 完整硬件画像：Host、设备类型、队列、模块环境、路径约束
- backend 状态：`backend_id`、是否 stable、是否 planned、是否当前不支持
- 代码生成交接摘要：设备适配、运行模式、入口约束、路径环境要求
- 是否已有 `onescience.json`
- 是否已有 `tpl.slurm`
- 是否要求执行、验证或只输出方案
- 如果用户原始目标已经明确要求远程运行、提交或验证运行，传递 `submission_authorized=true` 与 `authorization_scope=current_workflow`，下游不要在同一工作流里连续询问是否提交远程

## 缺失项处理

- 缺少代码上下文：先说明需要检查哪些源码或目录。
- 缺少 `onescience.json`：通常应已由 `onescience-workflow` 在首次使用时自动初始化；如果直接从本 skill 进入且项目仍缺失配置，运行链路应先回到 `onescience-workflow` 完成项目初始化，不要要求用户手写初始化提示词。
- 缺少 `tpl.slurm`：只在运行任务里记录模板来源；项目级模板缺失时由 `onescience-runtime` 使用内置 `assets/tpl.slurm` 兜底，不阻塞纯代码任务。
- 缺少 SCnet 区域或队列：优先交给 `onescience-runtime` 的 `scnet_mcp` 通道自行发现，不要先阻断
- 远程主机或设备约束不明确：先交给 `onescience-hardware` 感知，再继续下游技能。
- 当下游只是 `onescience-coder`：优先传递代码生成交接摘要，而不是整份完整硬件画像。
- 如果用户未配置远程环境但当前目标只是代码实现，继续本地代码链路，不要误阻塞。

## 输出要求

至少给出：

1. 识别出的任务类型
2. 选择该技能链的原因
3. 下一步由哪个技能继续处理

如果请求涉及远程环境缺失、远程描述模糊或运行前置条件不足，再额外给出：

4. `status`：`ok` / `partial_context` / `need_clarification` / `blocked`
5. `recognized`：已识别出的 Host / 平台 / 队列 / 路径等线索
6. `missing`：当前阶段真正缺失的字段
7. `can_continue_locally`：是否还能停留在本地或代码阶段继续
8. `next_action`：下一步进入 `coder` / `hardware` / `runtime` / `installer` / `debug`

如果请求已可识别远程 backend，再额外给出：

9. `backend_id`
10. `backend_status`：`stable_backend` / `planned_backend` / `unsupported_for_now`
11. `execution_readiness`：`ready_to_execute` / `blocked_by_host` / `blocked_by_backend`

## 禁止事项

- 不要替代 `onescience-workflow` 做顶层工作流理解
- 不要替代 `onescience-role` 做完整角色分工抽象
- 不要把 `onescience-hardware` 和 `onescience-runtime` 混成一个层
- 不要把显式 SCnet MCP 提交请求硬改造成 `ssh_slurm` 通道
- 不要跳过硬件感知就直接生成面向远程硬件的代码
- 不要在 backend 仍是 planned 或 unsupported 时假装它已经稳定可执行
- 不要使用 `.trae/skills/onescience.json` 之类的私有硬编码路径
- 不要创造仓库中不存在的新 skill
- 不要在未被要求时直接提交、安装或远程执行
- 不要在用户已经明确要求运行/提交/验证运行后，反复询问“是否提交远程”；同一工作流只允许第一次必要确认
