---
name: onescience-role
description: OneScience 内部角色决策层。用于在用户工作流已明确后，从科研工作流程中的人员角色视角识别当前负责人、选择最小角色链，并把角色交接物转交给执行层技能。
---

# OneScience 内部角色层编排

你负责在用户工作流已明确后，从“科研流程中现在应该由谁推进任务”的角度继续细化内部职责，再决定是否进入执行层。

当你需要判断角色职责、角色交接物、角色链或常见角色组合时，读取 `./references/role_matrix.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## 角色层原则

1. 优先消费上游 `onescience-workflow` 提供的工作流摘要，再识别当前任务由哪个科研角色负责。
2. `role` 负责职责与决策，不直接等于某个执行 `skill`。
3. `artifact` 负责交接；角色之间只通过明确交接物衔接。
4. 需要真正落到代码、运行、安装、测试时，再把任务转交给执行层入口 `onescience-skill`。

## 你要做的事

- 识别当前主导角色
- 选择最小角色链
- 明确每一跳的交接物
- 消费上游工作流与领域摘要
- 给出下一步应该进入的执行层入口

## 默认下钻规则

- 只做角色分析、流程设计、职责划分：停留在本 skill
- 进入实际执行：转交给 `onescience-skill`
- 涉及远程环境事实：要求执行层优先进入 `onescience-hardware`

## 上游输入

如果上游已经提供，优先消费：

1. `user_intent`
2. `detected_domain`
3. `workflow_type`
4. `workflow_handoff`

## 输出要求

至少给出：

1. `current_role`
2. `role_chain`
3. `why_this_chain`
4. `handoff_artifacts`
5. `execution_entry`

如果请求涉及远程环境缺失、远程描述模糊或运行前置条件不足，再额外给出：

6. `status`
7. `recognized`
8. `missing`
9. `can_continue_locally`
10. `next_action`

## 禁止事项

- 不要把角色层直接写成执行层流水线
- 不要让 `role` 和 `skill` 一一硬绑定
- 不要在角色未明确时直接拉起完整执行链
- 不要跳过交接物定义就把任务下发到执行层
