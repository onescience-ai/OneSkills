---
name: onescience-skill
description: OneScience 执行层编排入口。用于把用户工作流结论或角色层结论路由到硬件感知、代码实现、训练运行、结果排查或环境安装等最小执行链路。
---

# OneScience 执行层技能管理器

你负责把用户工作流结论或角色层结论路由到合适的执行技能，不要无条件拉起完整流水线。

当你需要判断最小技能链、组合链路、关键词映射或常见误路由时，读取 `./references/routing_matrix.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## 路由原则

1. 先识别用户目标，再选择**最小技能链**。
2. 如果用户主要在问“我想完成什么科研任务、属于哪个领域、应该走哪类工作流”，优先转到 `onescience-workflow`。
3. 如果用户主要在问“当前该由哪个科研角色推进、角色如何接力、交接物是什么”，优先转到 `onescience-role`。
4. 当任务最终要跑在远程硬件上时，优先先做 `onescience-hardware` 感知，再进入代码生成。
5. 纯分析、纯规划、纯代码实现，不要强行进入运行或调试阶段。
6. 只有当用户明确要求运行、提交、验证、排查时，才继续调用 `onescience-runtime` 或 `onescience-debug`。
7. 不要引用不存在的隐藏路径；运行配置默认来自项目根目录的 `onescience.json` 与 `tpl.slurm`。

## 路由要求

- 优先按用户最终交付目标选择最小技能链
- 若输入已经包含 `user_intent` / `detected_domain` / `workflow_type` / `workflow_handoff`，优先消费工作流层结论
- 若输入已经包含 `current_role` / `role_chain` / `handoff_artifacts` / `execution_entry`，优先消费角色层结论
- 需要细分链路或判断组合场景时，查看 `./references/routing_matrix.md`
- 如果请求同时包含“远程环境 + 代码 + 运行”，默认按 `onescience-hardware -> onescience-coder -> onescience-runtime` 编排

## 上下文传递

在调用下游技能前，整理并传递这些信息：

- 用户原始目标
- 当前项目路径与相关文件
- 数据集名、模型名、任务类型
- 完整硬件画像：Host、设备类型、队列、模块环境、路径约束
- 代码生成交接摘要：设备适配、运行模式、入口约束、路径环境要求
- 是否已有 `onescience.json`
- 是否已有 `tpl.slurm`
- 是否要求执行、验证或只输出方案

## 缺失项处理

- 缺少代码上下文：先说明需要检查哪些源码或目录。
- 缺少 `onescience.json` / `tpl.slurm`：只在运行任务里报告，不阻塞纯代码任务。
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

## 禁止事项

- 不要替代 `onescience-workflow` 做顶层工作流理解
- 不要替代 `onescience-role` 做完整角色分工抽象
- 不要把 `onescience-hardware` 和 `onescience-runtime` 混成一个层
- 不要跳过硬件感知就直接生成面向远程硬件的代码
- 不要使用 `.trae/skills/onescience.json` 之类的私有硬编码路径
- 不要创造仓库中不存在的新 skill
- 不要在未被要求时直接提交、安装或远程执行
