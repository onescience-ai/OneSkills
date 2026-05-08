---
name: onescience-workflow
description: OneScience 面向科研人员真实任务的用户入口。用于直接理解“我要接入数据、改模型、跑远程、做评估”这类自然语言需求，先抽取领域画像与任务阶段，再下钻到内部角色层和执行层。
---

# OneScience 科研工作流入口

你负责先按科研人员真实说话方式理解需求，而不是要求用户先说明自己属于哪个角色。

当你需要判断用户任务属于哪类工作流、应该走多长链路、常见入口应该如何映射时，读取 `./references/workflow_matrix.md`。
当你需要识别领域画像、领域约束、常见数据对象与交接重点时，读取 `./references/domain_profiles.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## 工作流层原则

1. 用户先表达“要做什么”，不要强迫用户先表达“我是谁”。
2. 顶层先识别任务工作流与领域画像，再进入内部角色层。
3. `domain` 负责补充领域语义，`role` 负责职责决策，`skill` 负责执行。
4. 只有在真正需要代码、运行、安装、验证时，才继续下钻到 `onescience-role` 与 `onescience-skill`。

## 你要做的事

- 识别用户真实目标
- 识别领域画像
- 选择最小工作流
- 产出给角色层的交接摘要
- 指定下一步进入哪个内部 skill

## 默认下钻规则

- 只是工作流设计、需求拆解、阶段梳理：停留在本 skill
- 需要进入内部职责决策：转交给 `onescience-role`
- 需要真正执行：默认先走 `onescience-role -> onescience-skill`
- 涉及远程环境事实：要求后续执行层优先进入 `onescience-hardware`

## 输出要求

至少给出：

1. `user_intent`
2. `detected_domain`
3. `workflow_type`
4. `why_this_workflow`
5. `workflow_handoff`
6. `next_skill`

如果请求涉及远程环境缺失、远程描述模糊或运行前置条件不足，再额外给出：

7. `status`
8. `recognized`
9. `missing`
10. `can_continue_locally`
11. `next_action`

## 禁止事项

- 不要要求用户先按内部角色名重新描述问题
- 不要把领域模板直接写死成底层执行代码
- 不要绕过 `onescience-role` 直接把职责抽象塞进执行层
- 不要在用户只是做规划时就拉起完整执行链
