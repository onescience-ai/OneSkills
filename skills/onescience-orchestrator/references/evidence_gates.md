# 证据边界与四层门禁全文（从 SKILL.md 剥离）

> 本文为 orchestrator 的证据纪律权威全文。SKILL.md 正文保留压缩版要点；
> **凡进入阶段三步骤 11（observation 决策）、任何 PASS/COMPLETE 判定或最终报告撰写之前，必须先读取本文**。

## 在线查证三通道分治与先验兜底（onescience-online-knowledge）

（与 SKILL.md 硬路由兜底配套生效）

- **三类知识来源与门禁各不相同，不得互相硬套**：
  1. **文献（channel=literature）**：接地**方法学选择**（泛函类别、核种、参照化合物、机理、实验值）；承重数值带 `[n]` + `domain_match`，全文取不到只引摘要并标 `abstract-only`。
  2. **结构/物质数据（channel=structure）**：晶体坐标/晶格/空间群**只能来自 COD 真实下载并经化学式回验通过**的记录（`source_type=database`、`provenance=COD:<id>`、`self_verified=true`）；**严禁把模型记忆坐标写进 POSCAR/CIF 或冒充某文献/COD 出处**。
  3. **软件参数（channel=software-param）**：ENCUT/k 网格/LCHIMAG/LEPSILON/IVDW 等 INCAR 标签来自 `software-doc`（内置参考表/官方 wiki），**不套『必须引 [n]』门**；存疑项（如 `ICHIBARE`）标 `⚠` 待核对，不得当已核实。
- **线上优先→先验兜底，不因缺知识而 blanket-BLOCKED**：任一承重知识先取在线；**在线确实未命中**（found=false/OFFLINE）时，**不因缺该知识而 blocked 整个任务**——降级为 `source_type=model-prior`、`verified_online=false`、正文标 `⚠ 未经在线核实的模型先验`，继续执行。
- **兜底不等于伪造**：带 `⚠ model-prior` 标注的尽力值是**诚实降级**，可用于「继续跑/脚手架/演示」；但若最终科学结论整体建立在先验承重参数上，必须**保留 ⚠ 标注不得升格为『来自文献/数据库』**，并据【证据边界契约】判 PARTIAL 而非 PASS。冲突的是「无出处且冒充已核实」，不是「如实标注的先验」。
- **结构回验失败即剔除**：structure 通道下载到但化学式回验不符（编号错配）的候选，按错误丢弃、换下一候选；全部不中才走先验兜底。

## 证据边界契约（对所有 executor_step 与最终状态判定强制生效——修「为跑完而伪造」病灶）

- **证据 tagging**：每个进入结论/交付的参数、阈值、数据集、研究对象、指标必须标注来源 ∈ {user_provided, literature[n], local_card, executed_log, proposed_candidate(待确认)}；`fabricated`（无来源自造）**禁止**作为本次结果。
- **禁止合成/演示数据充当结果**：不得生成 synthetic/demo/模拟样本用于训练或评估并把它当本次研究数据/结果；缺真实数据时该科学步骤回报 BLOCKED 或诚实 PARTIAL。
- **禁止替代模型顶替**：不得用简化/玩具模型（如以稳态热传导顶替流动-传热耦合 CFD、以 2D 顶替 3D）的输出充当用户要求的模拟结果；可作为「方法演示/脚手架」交付但必须显式标注 `not-a-result`，且不得据此判 PASS。
- **禁止自设验收阈值判 PASS**：验收阈值/稳定性判据必须 user_provided 或 literature[n]；agent 只能提 proposed_candidate 请用户确认，不得自定阈值后自判 PASS/COMPLETE。
- **验收阈值溯源门禁**：任何进入最终报告的验收/PASS 判定必须引用来源 ∈ {user_provided, literature[n]}；无来源则该判定必须标注 `engineering_threshold(smoke)` 且科研 PASS 必须 BLOCKED。**自证闭环禁止**：不得（生成模拟结果 → 自设验收阈值 → 让模拟结果通过自设阈值 → 宣布科研 PASS/签收）。
- **状态判定门禁（单一事实源）**：宣告任何步骤或整体 PASS/COMPLETE 前，逐条核对所报数值与执行日志/引文一致；出现汇总与日志不一致（如报告 MAE≠运行 MAE）即不得 PASS，须回修或降为 PARTIAL/BLOCKED。
- **propose-vs-block（修过度 BLOCKED）**：对任务委托给 agent 的选择（模型/软件/方法选型），不得以「用户未提供」为由 BLOCKED 索要；应基于文献/本地卡提出 2-3 个有证据候选+推荐项+请用户确认该关键选择；仅对**用户私有/不可推断**输入（自有数据集路径、自有集群配置等）才 BLOCKED。
- **不得 blanket-BLOCKED + 领域准确性**：模型/软件/超参选型是 agent 委托项，agent 必须提 2-3 个有证据候选+推荐+理由，只对影响科学范围或验收标准的部分请求确认，不得以「用户没告诉我超参」全部甩回 BLOCKED；fallback/候选数据集或方法例子必须领域正确（如 QM9 不是 MOF 数据集），候选必须引用正确领域来源。
- **证据洞下的总姿态**：科学结论=BLOCKED 或诚实 PARTIAL（写明「未产生本次结果」）；工程脚手架可交付为 PARTIAL 并标注 not-a-result；严禁以「继续跑完」为由伪造证据或虚报状态。

## 四层证据门禁补强

（修 ws07 planning-time 参数越界 + ws09 execution/acceptance-time 身份抬高与验证 FAIL 后仍 complete 两个病灶；与上文证据边界契约配套生效，对老架构与新架构一视同仁）

**A. 知识层门禁（domain_match，修文献跨域迁移当本次参数）**：
- `resource_retrieval_result.online_evidence.citations[]` 每条必须带 `domain_match ∈ {exact, adjacent, cross_domain}` 标签（由 primitives step 11 / live-literature Step 5 产出；orchestrator 消费时复核）。
- `domain_match=cross_domain` 的文献**只能作为方法学参考**（验证思路、网格无关性方法、湍流模型候选等），**不得作为本次任务的参数/阈值/几何/工况来源**；若被引为参数来源，该参数自动降级为 `pending_user_confirmation`，并向 gaps.jsonl 追加 `gate_hit=domain_mismatch` 缺口行。
- 兜底检索完成后池内 `domain_match=exact` 数为 0 时：必须触发第二轮更精准 query（query 强制包含场景锚词，如「immersion cooling」「data center」），仍为 0 则如实标注「在线兜底形式成功、实质未命中目标域」，相关科学结论保持 BLOCKED 或诚实 PARTIAL，不得用 adjacent/cross_domain 文献硬凑本次参数。

**B. 计划层门禁（参数四态标签，修 planning-time 把候选写成本次研究参数）**：
- `planner_proposal`、`Global Plan`、`research_plan.md` 中**每个具体数字/参数/阈值/几何/工况/验收判据**必须带四态标签之一：
  * `confirmed_input`：用户本轮明确提供（须有 task_state.events 的 `user_confirmation` 事件佐证）
  * `literature_candidate`：附来源 `[n]` + 该文献 `domain_match` + 与本任务研究对象的适用性判断（同域/近域/跨域）
  * `pending_user_confirmation`：agent 提出的候选，用户确认后才允许进入执行
  * `blocked_missing`：不可推断且无文献支持，必须 BLOCKED
- **REJECT 门禁**：planning 产物中只要存在**未打四态标签的裸数字**，该 planning 步骤直接判 REJECT，不得标 completed、不得进入执行阶段，并向 gaps.jsonl 追加 `gate_hit=bare_number_reject`。
- `literature_candidate` / `pending_user_confirmation` 参数**不得**在执行阶段被静默升格为 `confirmed_input`；升格必须有用户本轮明确确认记录（`user_confirmation` 事件）。
- 本门禁**不因「最后停在 BLOCKED」而豁免**：ws06 式「planning 里写死 600×1000×2000 mm、y+≈1、500-1000 万网格但无来源」同样 REJECT。

**C. 执行层门禁（result_identity，修 smoke/demo 输出被抬成科研结果）**：
- 每个 executor_step 的 `execution_result` 必须声明 `result_identity ∈ {research_result, engineering_demo, smoke_test, not_a_result}`。
- **关键词自动锁**：executor 产出的脚本/日志/报告自述中出现 `smoke`、`demo`、`simplified`、`toy`、`not suitable for production`、`demonstration only`、`engineering_validation(smoke` 等任一关键词时，orchestrator **自动锁定**该 step 的 `result_identity=not_a_result`，executor 不得自行申报更高身份；锁定动作向 gaps.jsonl 追加 `gate_hit=result_identity_lock`。
- `result_identity ∈ {engineering_demo, smoke_test, not_a_result}` 的 step：
  * 状态只能标 `DEMO_PASS` / `PARTIAL` / `BLOCKED`，**禁止标 PASS**；
  * 其输出**禁止**进入最终报告的「关键发现 / 科研结论」段，只能进入「方法演示 / 脚手架」段，且前置标注「以下为演示输出，不构成本次科研结论」；
  * 下游依赖该 step 产物的 step 自动继承 `not_a_result` 身份，不得被抬高。
- **输入门禁 ≠ 结果身份门禁**：用户确认「使用默认示例/典型参数/推荐值」只解除 `input_gate`（允许用默认值继续执行），**不解除** `result_identity_gate`（默认值跑出来的产物仍是 `engineering_demo`，不是 `research_result`）。orchestrator 必须在 `user_confirmation` 事件里显式记录本次解除的是哪道门，不得把前者当后者的授权。

**D. 验收层门禁（验证 FAIL 级联回退 + complete_with_caveats，修验证失败后仍判 PASS/complete）**：
- **级联回退**：验证类 step（网格独立性/能量守恒/可复现审计/指标对标等）判 FAIL 时，orchestrator 必须**自动回退**其上游所有已标 PASS 的 step：PASS → `UNVERIFIED`（产物被失败验证覆盖）或 `PARTIAL`；回退动作写入 `validation_rollback` event 并向 gaps.jsonl 追加 `gate_hit=validation_rollback`，不得静默。
- **complete 门禁**：`task_state.status=complete` 的前提是**同时满足**：① 所有 step 的 `result_identity=research_result`；② 所有验证类 step PASS；③ 无未解除的 `blocked_missing` 参数；④ **可视化交付契约满足**（`REPORT_single.html` 已落盘且非空、零外链、含内嵌图，见 SKILL.md「可视化交付契约」节）。任一不满足时 status 只能是 `complete_with_caveats`（工程链跑通但存在 not_a_result/DEMO_PASS 或验证 PARTIAL 或可视化缺失）、`partial`（验证 FAIL 且无可交付回退产物）或 `blocked`；降级动作向 gaps.jsonl 追加 `gate_hit=complete_downgrade`。
- **结论前置标注**：`complete_with_caveats` / `partial` 状态下，最终输出**第一行必须**前置：「⚠ 本次未产生科研结论，以下为方法演示/工程脚手架输出，验证状态：<FAIL/PARTIAL 明细>」；禁止把演示数值（如「最大温升 1.03 K」「换热系数 35249 W/(m²·K)」「无热点」）写进「关键发现」段。
- **禁止无条件完成自述**：存在验证 FAIL 或任一 `not_a_result` step 时，禁止输出「任务已完成，所有步骤均有可追溯证据链」这类无条件完成自述；必须改为「工程链已跑通，但科研验证未通过（明细），本次不产生科研结论」。

## 门禁可观测性（A/B 归因用）

A/B/C/D 任一门禁被触发（REJECT / 自动锁 / 级联回退 / status 降级 / domain 降级）时，orchestrator 必须向工作区状态目录的 `.onescience/gaps.jsonl` 追加一行（与 task_state.json 同一状态区；**严禁写进 `skills/**` 知识树内路径**，那会污染只读知识库），含 `gate_hit ∈ {domain_mismatch, bare_number_reject, result_identity_lock, validation_rollback, complete_downgrade}` 与 `gate_layer ∈ {A_knowledge, B_planning, C_execution, D_acceptance}` 字段，便于下一轮 A/B 直接统计「哪层门禁真的生效、哪层还在被绕过」，不再靠人读 session 日志归因。
