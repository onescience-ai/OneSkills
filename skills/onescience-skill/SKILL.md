---
name: onescience-skill
description: OneScience 执行层编排入口。用于把工作流层或角色层结论路由到最小执行链路；公开执行技能为 `onescience-runtime` 与 `onescience-installer`。
---

# OneScience 执行层技能管理器

你负责把工作流层或角色层结论路由到合适的执行技能，不要无条件拉起完整流水线。

当你需要判断最小技能链、组合链路、关键词映射或常见误路由时，读取 `./references/routing_matrix.md`。
当你需要判断跨执行链路的共享 backend 与执行模式语义时，读取 `../../references/shared_contracts.md`。
当你需要消费 OneScience 仓库内 examples/biosciences 资产时，读取 `./assets/onescience_dependency.json`，并以 `{onescience_path}/onescience/examples/biosciences/_manifests/contract.json` 为能力契约来源。
当你需要判断 Catalog 原语 resolve 结果如何进入执行链时，读取 `../../references/catalog_integration.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## Catalog 协作

1. 若 `selectedPrimitiveIds` 或 `primitive_contract` 已在上游给出，执行层直接消费，不重复 `catalog_search(kind=primitive)`。
2. 若仍缺可执行原语且任务涉及数据/模型/应用资产，先补 `catalog_search(kind=primitive)` → `catalog_resolve`，再进入 `onescience-coder` / `onescience-runtime`。
3. skill 选择仍优先 `<available_skills>`；名单不足时再 `catalog_search(kind=skill)`，确定后用 `skill` tool 加载。

## 路由原则

1. 先识别用户目标，再选择最小技能链。
2. 工作流理解问题优先转到 `onescience-workflow`。
3. 角色分工问题优先转到 `onescience-role`。
4. 当前公开执行技能为：
   - `onescience-runtime`
   - `onescience-installer`
5. 显式运行、提交、验证、查状态、下载日志，优先进入 `onescience-runtime`。
6. 环境安装、环境修复、依赖补齐，优先进入 `onescience-installer`。
7. 纯分析、纯规划、纯代码实现，不要强行进入运行或安装阶段。
8. `onescience-runtime` 内部承担 `discover/preflight/execute/diagnose`，`onescience-installer` 内部承担 `discover/precheck/install/verify`，不要再向外拆出额外执行 skill。

## 路由要求

- 优先按用户最终交付目标选择最小技能链。
- 若输入已经包含 `user_intent` / `detected_domain` / `workflow_handoff`，优先消费工作流层结论。
- 若输入已经包含 `current_role` / `role_chain` / `handoff_artifacts` / `execution_entry`，优先消费角色层结论。
- 若同时包含 workflow 与 role 结论，执行层以 role 的 `execution_entry` 和 `handoff_artifacts` 为直接路由依据；不要反向重做领域识别或角色链判断。
- 需要细分链路或判断组合场景时，查看 `./references/routing_matrix.md`。
- 如果请求同时包含“远程环境 + 代码 + 运行”，优先按 `onescience-coder -> onescience-runtime` 编排；由 runtime 内部做 `discover/preflight`。
- 如果请求明确包含“SCnet + 代码 + 提交”，默认按 `onescience-coder -> onescience-runtime` 编排，并传递 `execution_mode=remote_direct`、`access_mode=cloud_api`，必要时再补 `execution_channel=scnet_mcp`。
- 如果运行前发现环境未 ready，应回退到 `onescience-installer`，不要提前把安装链路和运行链路混在一起。
- 如果已有 backend 识别结论，则在进入 `runtime` / `installer` 前显式说明当前 backend 是 `stable_backend`、`planned_backend` 还是 `unsupported_for_now`。

## 上下文传递

在调用下游技能前，整理并传递这些信息：

- 用户原始目标
- 当前项目路径与相关文件
- 本地待上传脚本路径、SCnet 区域偏好、队列偏好、现有 `task_id`
- 期望 `execution_mode` / `access_mode`，以及可选的 `execution_channel`
- 数据集名、模型名、任务类型
- 完整环境事实：Host、设备类型、队列、模块环境、路径约束
- backend 状态：`backend_id`、是否 stable、是否 planned、是否当前不支持
- 代码生成交接摘要：设备适配、运行模式、入口约束、路径环境要求
- 是否已有 `onescience.json`
- 是否已有 `tpl.slurm`
- 是否要求执行、验证、安装修复或只输出方案
- 如果用户已经明确要求远程运行、提交或验证运行，传递 `submission_authorized=true` 与 `authorization_scope=current_workflow`

## 缺失项处理

- 缺少代码上下文：先说明需要检查哪些源码或目录。
- 缺少 `onescience.json`：仅阻塞 `remote_slurm` 运行链路；不要阻塞纯代码链路。
- 缺少 `tpl.slurm`：运行链路中由 `onescience-runtime` 使用内置模板兜底。
- 缺少 SCnet 区域或队列：优先交给 `onescience-runtime` 的 `scnet_mcp` 资产自行发现。
- 远程主机或设备约束不明确：优先进入 `onescience-runtime` 的 `discover/preflight`，必要时再显式回退环境识别阶段。
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
8. `next_action`：下一步进入 `coder` / `runtime` / `installer`

如果请求已可识别远程 backend，再额外给出：

9. `backend_id`
10. `backend_status`
11. `execution_readiness`

## 禁止事项

- 不要替代 `onescience-workflow` 做顶层工作流理解。
- 不要替代 `onescience-role` 做完整角色分工抽象。
- 不要把安装与运行提交混成同一个输出结论。
- 不要把显式 SCnet 提交请求硬改造成 `remote_slurm`。
- 不要在 backend 仍是 planned 或 unsupported 时假装它已经稳定可执行。
- 不要创造仓库中不存在的新 skill。
- 不要在未被要求时直接提交、安装或远程执行。
