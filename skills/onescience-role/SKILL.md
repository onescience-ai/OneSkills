---
name: onescience-role
description: OneScience 内部角色决策层。用于在用户工作流已明确后，从科研工作流程中的人员角色视角识别当前负责人、选择最小角色链，并把角色交接物转交给执行层技能。
---

# OneScience 内部角色层编排

你负责在用户工作流已明确后，从“科研流程中现在应该由谁推进任务”的角度继续细化内部职责，再决定是否进入执行层。

当你需要判断角色职责、角色交接物、角色链或常见角色组合时，读取 `./references/role_matrix.md`。
优先消费上游 `onescience-workflow` 提供的 `domain_route`、`domain_task_family`、`stage_intent`、`planning_only` 与 `workflow_handoff`；只有这些字段缺失时，才基于用户请求做最小补判，不要重新承担完整领域入口分析。
当上游 `domain_route=biology`，或 `detected_domain` / `domain` 包含 `biology`、`bioinformatics`、`biosciences`、`生信` 时，读取 `./bio_domain/SKILL.md` 作为领域子路由。
当上游 `domain_route=earth` 或 `detected_domain=earth` 时，优先读取 `./earth/earth_overview.md`。
当上游 `domain_route=earth` 或 `detected_domain=earth` 时，同时读取 `./earth/boundary_contract.md` 作为默认层级约束。
当需要把 Earth 任务归入更具体的任务桶时，读取 `./earth/task_map.md`。
当上游 `domain_route=cfd` 或 `detected_domain=cfd` 时，优先读取 `./cfd/cfd_overview.md`。
当上游 `domain_route=cfd` 或 `detected_domain=cfd` 时，同时读取 `./cfd/boundary_contract.md` 作为默认层级约束。
当需要把 CFD 任务归入更具体的任务桶时，读取 `./cfd/task_map.md`。
当上游 `domain_route=materials`，或任务属于材料化学/原子尺度建模时，先读取 `./assets/matchem/matchem_task_index.md`；若已明确模型路线，再读取该索引登记的对应路线卡。当前 `MACE` 是材料模型路线的标准样板，未登记的新材料模型默认参考 MACE 样板生成交接物。
当你需要判断 Catalog 原语搜索结果如何进入角色交接物时，读取 `../../references/catalog_integration.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## Catalog 输入

如果上游或任务上下文已提供，优先消费：

1. `selectedPrimitiveIds`
2. `primitive_summary`（来自 `catalog_search` 或 `catalog_resolve(part=summary)`）
3. `primitive_location` / `primitive_contract`（来自 `catalog_resolve`）

若 `selectedPrimitiveIds` 已存在，不要重新发起 primitive search；只在交接物中补充角色视角下的使用约束。

## 角色层原则

1. 优先消费上游 `onescience-workflow` 提供的工作流摘要，再识别当前任务由哪个科研角色负责。
2. `role` 负责职责与决策，不直接等于某个执行 `skill`。
3. `artifact` 负责交接；角色之间只通过明确交接物衔接。
4. 需要真正落到代码、运行、安装、测试时，再把任务转交给执行层入口 `onescience-skill`。
5. 对生物信息领域任务，优先先完成 `bio_task_family`、具体生信 skill 与交接摘要整理，再决定是否继续下探。
6. 对 Earth 领域任务，优先先完成任务桶识别与交接摘要整理，再决定是否继续下探。
7. 对 CFD 领域任务，优先完成任务桶识别、数据 / 模型协议兼容性判断与 `assets_only` 交接摘要整理，再决定是否继续下探。
8. `domain_route` 与 `domain_task_family` 是 workflow 的粗路由结果；role 可以细化为 `earth_task_type`、`cfd_task_type`、`bio_task_family` 或材料 `model_route`，但不要反向重写 workflow 入口判断。
9. `execution_entry` 只表示后续执行入口，不表示当前这一跳立刻调用该 skill。
10. 在规划阶段或用户尚未授权实现、运行、提交、安装时，只输出当前 role 判断、任务桶、交接物和最多一个 `execution_entry`；不要展开完整执行链。

## 你要做的事

- 识别当前主导角色
- 对生物信息领域任务识别当前任务范畴和具体生信 skill
- 对 Earth 领域任务识别当前任务桶
- 对 CFD 领域任务识别当前任务桶
- 选择最小角色链
- 明确每一跳的交接物
- 消费上游工作流与领域摘要
- 给出下一步应该进入的执行层入口
- 区分“当前停留在 role 层输出交接摘要”和“未来可能进入的 execution_entry”

## 默认下钻规则

- 只做角色分析、流程设计、职责划分：停留在本 skill
- 进入实际执行：转交给 `onescience-skill`
- 当用户要求“只看路线 / 先不写代码 / 先做规划”时，停留在本 skill；可以给出 `execution_entry`，但不要立刻进入执行层
- 涉及远程环境事实：要求执行层优先进入 `onescience-runtime` 或 `onescience-installer`
- 规划阶段不要把 `onescience-skill`、`onescience-runtime`、`onescience-installer` 提前列为 pipeline 阶段；除非用户明确要求验证、运行、提交或安装

## 上游输入

如果上游已经提供，优先消费：

1. `user_intent`
2. `detected_domain`
3. `workflow_type`
4. `workflow_handoff`
5. `domain_route`
6. `domain_task_family`
7. `stage_intent`
8. `planning_only`

## 输出要求

至少给出：

1. `current_role`
2. `role_chain`
3. `why_this_chain`
4. `handoff_artifacts`
5. `execution_entry`
6. `planning_only`

其中：

- `execution_entry` 表示未来真正进入实现或执行时的入口
- 若当前只是规划阶段，输出应停留在 `onescience-role`，不要把 `execution_entry` 误写成当前已调用的 skill
- 规划阶段的 `execution_entry` 最多列一个最可能入口，通常是 `onescience-coder`
- 如进入领域子路由，补充对应细化字段：`earth_task_type`、`cfd_task_type`、`bio_task_family` 或 `model_route`

如果请求涉及远程环境缺失、远程描述模糊或运行前置条件不足，再额外给出：

6. `status`
7. `recognized`
8. `missing`
9. `can_continue_locally`
10. `next_action`

## 禁止事项

- 不要把角色层直接写成执行层流水线
- 不要在 workflow 已提供 `domain_route` / `domain_task_family` 时重新做完整领域入口分析
- 不要让 `role` 和 `skill` 一一硬绑定
- 不要在角色未明确时直接拉起完整执行链
- 不要跳过交接物定义就把任务下发到执行层
- 不要把 `execution_entry` 误当成当前立即执行的下一跳
- 不要在规划阶段输出完整闭环 pipeline
