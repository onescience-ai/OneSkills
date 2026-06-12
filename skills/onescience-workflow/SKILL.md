---
name: onescience-workflow
description: OneScience / OneSkills 面向科研人员真实任务的用户入口。用于直接理解“我要接入数据、改模型、跑远程、做评估、复现论文”这类自然语言需求；论文复现 paper2code 必须解析论文/arxiv/PDF 来源并重新生成代码，禁止搜索、打开、下载、clone 或参考官方/第三方已实现代码仓库；当用户说“使用/启动/打开/进入 onescience”或“使用/启动/打开/进入 oneskills”时，也先进入本 skill 抽取领域画像与任务阶段，再按需下钻到内部角色层和执行层。
---

# OneScience 科研工作流入口

你负责先按科研人员真实说话方式理解需求，而不是要求用户先说明自己属于哪个角色。

当用户只表达“使用 onescience / oneskills”“启动 onescience / oneskills”“打开 onescience / oneskills”“进入 onescience / oneskills”或“onescience / oneskills 模式”时，识别为统一入口请求，停留在本 skill，引导用户补充具体科研目标，不要直接拉起完整执行链。

如果用户明确点名某个具体 skill，例如 `onescience-coder`、`onescience-runtime`、`onescience-installer` 等，则优先使用对应 skill；对应 skill 可按自身规则判断是否需要转回本入口。

当你需要判断用户任务属于哪类工作流、应该走多长链路、常见入口应该如何映射时，读取 `./references/workflow_matrix.md`。
当你需要识别领域画像、领域约束、常见数据对象与交接重点时，读取 `./references/domain_profiles.md`。
处理论文复现 paper2code 时，第一动作只能是解析论文来源（arxiv ID/URL、论文标题、PDF、本地文件或粘贴文本），不得搜索 GitHub/GitLab/Bitbucket、official code、repository、source code、model zoo 或任何已实现代码来源。若需要联网查题名，只能以论文/arxiv/PDF/出版页为目标，不得加入 `code`、`github`、`repo`、`implementation` 等实现仓库关键词。
论文复现信号优先级高于模型、训练、推理、保存目录等通用代码信号。看到“复现论文 / 实现论文 / implement this paper / 根据论文生成代码 / paper to code”时，必须锁定为 `workflow_type=paper2code_task`、`task_method=paper2code`；不要把 `user_intent` 改写成“获取官方代码”“下载官方仓库”“克隆论文代码”或把任务降级为 `model-task`。
当识别到 `detected_domain=biology`，或当前请求明显属于生物信息 / 生命科学数据与模型任务时，在交接摘要中设置 `domain_route=biology`，并要求后续优先进入 `onescience-role` 的 `bio_domain` 路径。
当识别到 `detected_domain=earth` 且后续需要进入内部职责决策时，在交接摘要中设置 `domain_route=earth`，并要求后续优先进入 `onescience-role` 的 `earth` 路径。
当识别到 `detected_domain=cfd` 且后续需要进入内部职责决策时，在交接摘要中设置 `domain_route=cfd`，并要求后续优先进入 `onescience-role` 的 `cfd` 路径。
当识别到材料化学 / 原子尺度建模任务时，在交接摘要中设置 `domain_route=materials`，并要求后续优先进入 `onescience-role` 的 `matchem` 路线。
当识别到论文复现任务时——用户粘贴 arxiv 链接/论文 ID、上传或粘贴论文内容、提供论文标题、说"复现这篇论文""实现这篇论文""implement this paper""根据论文生成代码"等——在交接摘要中设置 `workflow_type=paper2code_task`、`task_method=paper2code`、`domain_task_family=paper-reproduction`，并尽量保留真实科学领域到 `domain_route`（如 `earth`、`biology`、`materials`、`cfd`，无法判断时用 `general-science`）。同时整理 `paper_source`（arxiv ID、URL、本地 PDF、粘贴文本或已知论文名）；如果用户只给标题，应优先解析论文/arxiv 来源。保留用户原始意图为“基于论文重新生成复现代码”，不得改写为“获取官方代码”。**不要搜索、打开、下载、clone、复制或参考官方/第三方已实现代码仓库；不要使用 GitHub/GitLab/Bitbucket/code repository 查询来推进 paper2code。** 若用户指定保存目录，该目录表示生成复现代码的落点，不是已实现代码仓库的 clone 目标。
当你需要判断何时通过 Catalog 搜索 AI 原语或 skill、何时直接 resolve 已绑定原语时，读取 `../../references/catalog_integration.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../../references/remote_status_examples.md`。

## 首次使用项目初始化

本 skill 是 OneScience 体系的用户入口，负责对用户无感地完成项目级运行配置初始化。

每次处理用户请求时，先检查当前用户项目根目录是否存在 `onescience.json`：

- 如果不存在，自动从 `./assets/onescience.default.json` 生成一份到项目根目录 `onescience.json`。
- `./assets/onescience.default.json` 必须保持与项目级 `onescience.json` 相同的基础字段结构，至少包含 `runtime.backend_id`、`runtime.remote`、`runtime.target`、`runtime.environment`、`runtime.cluster`、`runtime.modules`、`runtime.conda`、`runtime.resources`、`runtime.script`。
- 不要要求用户先输入“初始化当前项目”之类的提示词。
- 不要在生成前打断用户确认；这是 OneScience 项目配置的默认初始化行为。
- 如果项目根目录已经存在 `onescience.json`，不要覆盖，不要重写用户配置。
- 生成后可以在最终输出中简短说明“已初始化项目级 onescience.json”，但不要把这变成用户必须参与的交互流程。
- 自动生成 `onescience.json` 只表示配置文件存在；其中队列、分区、conda 环境、脚本路径等字段仍应在真正进入 `onescience-runtime` 前结合硬件画像和用户项目上下文校正。

`tpl.slurm` 不需要由 workflow 初始化；项目缺失模板时，`onescience-runtime` 会使用自身 `assets/tpl.slurm` 作为只读模板兜底。

## Catalog 协作

1. 若任务上下文已包含 `selectedPrimitiveIds`，视为 UI 已绑定原语，跳过 `catalog_search(kind=primitive)`，直接要求下游 `catalog_resolve`。
2. 若用户要接入数据集、模型、应用或能力资产，且尚未绑定原语，优先触发 `catalog_search(kind=primitive)`，选中后再 `catalog_resolve(part=location|contract)` 并写入任务上下文。
3. `<available_skills>` 仍优先于 `catalog_search(kind=skill)`；仅当名单无法满足意图或语义模糊时再搜索 skill。
4. Catalog 只负责发现与摘要；正文加载仍通过 `skill` tool，原语细节通过 `catalog_resolve`。

## 工作流层原则

1. 用户先表达“要做什么”，不要强迫用户先表达“我是谁”。
2. 顶层先识别任务工作流与领域画像，再进入内部角色层。
3. `domain` 负责补充领域语义，`role` 负责职责决策，`skill` 负责执行。
4. 只有在真正需要代码、运行、安装、验证时，才继续下钻到 `onescience-role` 与 `onescience-skill`。
5. `next_skill` 只表示当前这一跳应进入哪个内部 skill，不表示整条链路未来可能用到的所有 skill。
6. 当用户明确说“先不要写代码”“只告诉我技能路线”“先做规划”“先看怎么走”时，当前路由必须停在规划层；不要把未来可能进入的 `onescience-coder`、`onescience-runtime` 或其它执行 skill 误写成当前 `next_skill`。
7. 在规划阶段或用户尚未授权实现、运行、提交、安装时，只输出当前所在层、当前下一跳和最多一个未来执行入口；不要展开 `onescience-skill -> onescience-coder -> onescience-runtime -> onescience-installer` 这类完整 pipeline。

## 你要做的事

- 识别用户真实目标
- 在项目首次使用时自动初始化 `onescience.json`
- 识别领域画像
- 选择最小工作流
- 产出给角色层的交接摘要
- 指定下一步进入哪个内部 skill
- 区分“当前下一跳”和“后续可能进入的执行入口”

## 默认下钻规则

- 只是工作流设计、需求拆解、阶段梳理：停留在本 skill
- 需要进入内部职责决策：转交给 `onescience-role`
- 需要真正执行：默认先走 `onescience-role -> onescience-skill`
- 当用户要求“只看路线 / 先不写代码 / 先做规划”时，即使未来会进入 `onescience-coder`，当前 `next_skill` 也应先保持为 `onescience-role`
- 涉及远程环境事实：要求后续执行层优先进入 `onescience-runtime` 或 `onescience-installer`
- 规划阶段不要把 `onescience-skill`、`onescience-runtime`、`onescience-installer` 提前列为 pipeline 阶段；除非用户明确要求验证、运行、提交或安装

## 输出要求

至少给出：

1. `user_intent`
2. `detected_domain`
3. `workflow_type`
4. `domain_route`
5. `domain_task_family`
6. `task_method`（如适用，例如 `paper2code`）
7. `paper_source`（论文复现任务适用）
8. `stage_intent`
9. `planning_only`
10. `why_this_workflow`
11. `workflow_handoff`
12. `next_skill`

其中：

- `next_skill` 只表示当前立即进入的下一跳
- 若当前只是规划阶段，可以在 `workflow_handoff` 中说明未来可能进入的执行入口，但不要把它们写成当前 `next_skill`
- 规划阶段的推荐输出是 `current_layer`、`next_skill`、`future_execution_entry`；`future_execution_entry` 最多列一个最可能入口
- `domain_route` 只表达真实科学领域路线，`domain_task_family` 只表达粗任务族，`task_method` 表达横向方法；具体角色链、任务桶、coder assets 和模型兼容性由 `onescience-role` 继续细化
- **论文复现任务特别说明**：当识别到 `task_method=paper2code` 时，`next_skill` 应为 `onescience-role`（需要角色层进一步细化角色链和交接物），而不是直接跳到 `onescience-skill` 或 `onescience-paper-repro`；执行入口应在 `workflow_handoff` 中标注为 `future_execution_entry=onescience-paper-repro`

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
- 不要把“未来可能进入的执行 skill”误当成“当前立即进入的 next_skill”
- 不要在规划阶段输出完整闭环 pipeline
