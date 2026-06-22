---
name: onescience-role
description: OneScience 内部角色决策层。用于在用户工作流已明确后，从科研工作流程中的人员角色视角识别当前负责人、选择最小角色链，并把角色交接物转交给执行层技能；paper2code 角色交接必须禁止 GitHub/code/repository 检索和官方/第三方实现代码参考。
---

# OneScience 内部角色层编排

你负责在用户工作流已明确后，从“科研流程中现在应该由谁推进任务”的角度继续细化内部职责，再决定是否进入执行层。

当你需要判断角色职责、角色交接物、角色链或常见角色组合时，读取 `./references/role_matrix.md`。
优先消费上游 `onescience-workflow` 提供的 `domain_route`、`domain_task_family`、`task_method`、`paper_source`、`stage_intent`、`planning_only` 与 `workflow_handoff`；只有这些字段缺失时，才基于用户请求做最小补判，不要重新承担完整领域入口分析。
当上游 `domain_route=biology`，或 `detected_domain` / `domain` 包含 `biology`、`bioinformatics`、`biosciences`、`生信` 时，读取 `./assets/bio_domain/SKILL.md` 作为领域子路由。
当上游 `domain_route=earth` 或 `detected_domain=earth` 时，优先读取 `./assets/earth/earth_overview.md`。
当上游 `domain_route=earth` 或 `detected_domain=earth` 时，同时读取 `./assets/earth/boundary_contract.md` 作为默认层级约束。
当需要把 Earth 任务归入更具体的任务桶时，读取 `./assets/earth/task_map.md`。
当上游 `domain_route=cfd` 或 `detected_domain=cfd` 时，优先读取 `./assets/cfd/cfd_overview.md`。
当上游 `domain_route=cfd` 或 `detected_domain=cfd` 时，同时读取 `./assets/cfd/boundary_contract.md` 作为默认层级约束。
当需要把 CFD 任务归入更具体的任务桶时，读取 `./assets/cfd/task_map.md`。
当上游 `domain_route=materials`，或任务属于材料化学/原子尺度建模时，先读取 `./assets/matchem/matchem_task_index.md`；若已明确模型路线，再读取该索引登记的对应路线卡。当前 `MACE` 是材料模型路线的标准样板，未登记的新材料模型默认参考 MACE 样板生成交接物。
当上游 `task_method=paper2code`、`domain_task_family=paper-reproduction`，或用户任务明确属于论文复现时，先读取 `./assets/paper2code/paper2code_overview.md` 了解论文复现前处理流水线，再读取 `./assets/paper2code/boundary_contract.md` 作为默认层级约束；当需要把论文复现任务归入更具体的任务桶时，读取 `./assets/paper2code/task_map.md`。论文复现是横向任务方法，不覆盖 `domain_route` 中的真实科学领域；但 role 层不得把它改写为“获取官方代码”的普通模型实现任务，不得选择纯 `model-engineer` 链作为主链。
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
11. 对 paper2code，必须保持 `task_method=paper2code`、`domain_task_family=paper-reproduction` 和 `paper_source`，并把 `implementation_code_used=false` 作为下游约束传递；不要输出“论文官方代码仓库地址”“去 GitHub 查官方实现”“clone 到输出目录”等交接物。

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

- 只做角色分析、流程设计、职责划分：停留在本skill
- 进入实际执行：输出 `next_skill=onescience-skill`，由 `onescience-skill` 路由层根据 `execution_entry` 和 `handoff_artifacts` 决策具体执行链路
- 只做规划或尚未授权实现/运行/安装时，输出 `next_skill=onescience-role` 或保持当前层，不要把 `onescience-skill` 写成当前立即下一跳
- 消费方（Codex编排层/opencode路由层）应读取`next_skill`决定下一跳，不要直接跳到`execution_entry`的值
- 当用户要求“只看路线/先不写代码/先做规划”时，停留在本skill；可以给出`execution_entry`，但不要立刻进入执行层
- 涉及远程环境事实：要求执行层优先进入`onescience-runtime`或`onescience-installer`
- 规划阶段不要把`onescience-skill`、`onescience-runtime`、`onescience-installer`提前列为pipeline阶段；除非用户明确要求验证、运行、提交或安装

## 上游输入

如果上游已经提供，优先消费：

1. `user_intent`
2. `detected_domain`
3. `workflow_type`
4. `workflow_handoff`
5. `domain_route`
6. `domain_task_family`
7. `task_method`
8. `paper_source`
9. `stage_intent`
10. `planning_only`

## 输出要求

至少给出：

1. `current_role`
2. `role_chain`
3. `why_this_chain`
4. `handoff_artifacts`
5. `execution_entry`
6. `next_skill`
7. `planning_only`

其中：

- `execution_entry`表示未来真正进入实现或执行时的入口（消费方：`onescience-skill`路由层）
- `next_skill`表示当前立即进入的下一跳；规划阶段应停留在 `onescience-role`，执行阶段才为 `onescience-skill`。消费方（Codex编排层或 opencode 路由层）应读取此字段决定下一跳，而非直接跳到 `execution_entry`
- `execution_entry`和`next_skill`是两个独立字段：`next_skill`是立即下一跳，`execution_entry`是最终执行入口
- 若当前只是规划阶段，输出应停留在`onescience-role`，不要把`execution_entry`误写成当前已调用的skill
- 规划阶段的`execution_entry`最多列一个最可能入口；paper2code 固定为 `onescience-paper-repro`，普通代码任务通常是 `onescience-coder`
- **论文复现任务特别说明**：当上游传递 `task_method=paper2code` 或识别到论文复现任务时，必须设置 `execution_entry=onescience-paper-repro`；在规划阶段，`next_skill` 应保持为 `onescience-role`（停留在角色层），只有用户明确授权实现时才输出 `next_skill=onescience-skill`（进入执行层）；`handoff_artifacts` 中必须包含 `paper_source`、`paper_workdir` 规则、`implementation_code_used=false` 等约束
- 如进入领域子路由，补充对应细化字段：`earth_task_type`、`cfd_task_type`、`bio_task_family`或`model_route`

如果请求涉及远程环境缺失、远程描述模糊或运行前置条件不足，再额外给出：

8. `status`
9. `recognized`
10. `missing`
11. `can_continue_locally`
12. `next_action`

## 禁止事项

- 不要把角色层直接写成执行层流水线
- 不要在 workflow 已提供 `domain_route` / `domain_task_family` 时重新做完整领域入口分析
- 不要让 `role` 和 `skill` 一一硬绑定
- 不要在角色未明确时直接拉起完整执行链
- 不要跳过交接物定义就把任务下发到执行层
- 不要把 `execution_entry` 误当成当前立即执行的下一跳；当前立即下一跳始终由 `next_skill` 指定，规划阶段停留在 `onescience-role`，执行阶段才进入 `onescience-skill`
- 不要在规划阶段输出完整闭环pipeline
