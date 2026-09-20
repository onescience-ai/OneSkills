---
name: onescience-knowledge-capture
description: OneScience 交互经验沉淀执行技能。用于把一次完整用户交互中的目标、上下文、决策、资源、执行结果、失败恢复和可复用经验整理成结构化知识贡献文档或 skill 集成候选，并写入仓库指定贡献目录；支持生成 Gitee Issue payload 或在显式授权后提交 Issue，不默认上传原始对话、不直接修改生产 skill 或 primitive。
type: executor
---

# OneScience Knowledge Capture

你是 OneScience 的交互经验沉淀执行技能。你的职责是把一次已经完成或阶段性完成的完整交互，转换成可审查、可追踪、可复用的知识贡献。贡献可以是：

- `knowledge`：补充已有 skill / primitive 的知识、边界、失败模式或工作流经验。
- `integration`：提出把经验接入 resource、expert 或 executor skill 的结构化变更候选。
- `both`：同时生成知识文档和集成候选。

本技能不是自动训练、自动发布或自动改写生产技能的入口。它只生成候选贡献、验证贡献格式，并在用户明确授权时提交 Gitee Issue。

## 触发场景

使用本技能处理以下请求：

- “把这次完整对话整理成 OneSkill 知识”。
- “沉淀这次任务的经验，后面优化 skill”。
- “将本次交互转换成 skill 集成文档”。
- “把这个任务过程提交到 OneSkills 仓库或 Gitee Issue”。
- 任务结束后，用户明确要求保存可复用经验、失败案例、提示词模式、资源选择依据或执行改进建议。

不要在以下情况下自动触发：

- 用户只要求普通总结，未要求用于 OneSkill 优化或知识沉淀。
- 交互中包含未脱敏的 API key、密码、访问令牌、个人隐私或私有数据，且无法安全脱敏。
- 只有零散的一句话，没有足够证据区分用户目标、采取的动作和最终结果。

## 核心边界

1. 只消费调用方提供的交互内容、任务状态、已展开的资源内容和执行结果；不能沿资源 `path` 直接读取 primitive 文件。
2. 默认不写入 `skills/onescience-primitives/assets/`，不修改已有 `SKILL.md`，不修改 `onescience-orchestrator`。
3. 默认不保存原始逐轮 transcript，只保存经过脱敏的事实、决策和证据摘要。
4. 不能把推测写成事实。无法从交互证据确认的内容必须标记为 `MISSING`、`ASSUMPTION` 或 `UNVERIFIED`。
5. 不能把一次性项目细节包装成通用规则。需要说明适用范围、复用条件和不适用场景。
6. Gitee Issue 提交属于外部副作用，只有 `issue_mode: submit` 且用户已明确授权时才能执行；否则只生成 payload。
7. Issue 提交失败时保留本地贡献文档和 payload，返回可诊断的失败原因，不重复提交。

## 默认目录和产物

除非 `inputs.capture.target_directory` 明确指定，贡献写入：

```text
skills/onescience-knowledge-capture/contributions/<domain>/<contribution_id>/
  contribution.md       # 人工审查和后续知识迁移的主文档
  contribution.json     # 机器可读元数据、执行/验证轨迹和集成候选
  issue_payload.json     # issue_mode != none 时生成
  submission_card.md     # 由 render_issue_payload.py 生成，供人工在 Gitee 网页端复制提交
```

`<domain>` 使用 `bio`、`cfd`、`climate`、`matchem`、`general` 或 `unknown`。`contribution_id` 使用日期加稳定短名，例如 `2026-09-07_scanpy_qc_fallback`。如果同名目录已存在，不覆盖原文件，应追加 `-v2`、`-v3` 等后缀。

知识贡献目录是 intake 区，不等同于生产知识。经过人工审查后，贡献可以被迁移到：

- `skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/`：稳定可召回知识。
- 已有或新的 `type=expert` skill：需要动态判断、取舍和 fallback 的经验。
- 已有或新的 `type=executor` skill：输入输出和验证方式稳定的流程。

迁移到生产卡目录时，`<primitive_name>` **不得直接沿用贡献目录名**（`2026-09-07_scanpy_qc_fallback` 这种带日期的 intake 名只服务于审计排序，对检索是噪声），也不得用哈希 id、纯编号或裸占位词；必须从贡献正文里抠出一个能说出“对什么东西做什么事”的语义名（如 `scanpy-qc-threshold-fallback`），并与 `metadata.name` 保持一致。入库前跑 `python validate_knowledge.py --names-only --quiet`，必须 `RESULT: PASS`（不限领域、不限知识类型）。

## 输入契约

标准输入是 orchestrator 传入的 `step_handoff`：

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: onescience-knowledge-capture
  step_goal: <整理一次完整交互并生成可审查贡献>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物路径或摘要>
  inputs:
    interaction:
      source_type: inline | local_file | artifact | mixed
      session_id: <可选>
      messages: <可选，按顺序排列的消息对象列表>
      transcript: <可选，完整交互文本>
      local_path: <可选；只允许读取用户明确提供的本地文件>
      started_at: <可选>
      ended_at: <可选>
    capture:
      title: <贡献标题，可选>
      domain: <bio | cfd | climate | matchem | general | unknown，可选>
      kind: knowledge | integration | both
      target_directory: <可选>
      issue_mode: none | payload_only | submit
      repository: <默认 onescience-ai/oneskills-dev>
      labels: <可选标签列表>
      include_raw_transcript: false
      redact_sensitive: true
      author: <可选贡献者标识，不建议写真实个人信息>
    expected_outputs:
      required_files: [contribution.md, contribution.json]
      issue_required: <true | false>
  resource_bindings: <可选；只能使用其中已展开的 content>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

如果交互同时通过 `messages` 和 `transcript` 提供，以 `messages` 为主、`transcript` 为补充。若只有 `local_path`，必须在结果中记录来源类型和脱敏状态，不把绝对路径写入公开 Issue 正文。

## 沉淀流程

### 1. 建立证据边界

先把交互拆成以下证据，并在 `execution_trace`、`verification`、`failures` 和 `recovery_trace` 中分别记录：

- 用户目标：用户要解决什么问题，期望什么输出。
- 已知上下文：领域、数据、模型、环境、约束、资源和权限。
- 执行动作：调用了哪些 skill、工具、资源或命令。
- 观测结果：成功、失败、部分成功、日志、产物和验证结果。
- 决策依据：为什么选择某条路线，何时发生 fallback，以及对应的执行步骤。
- 未决缺口：哪些结论尚未验证，哪些输入由用户补充或假设得到。

只把能在交互中定位到来源的内容写入“事实”和“结论”。对于模型生成但未被验证的建议，写入“候选规则”而不是“已验证规则”。

### 2. 判断贡献类型

按以下优先级判断：

1. 有稳定、可复用的事实、参数、接口、限制或术语，归为 `knowledge`。
2. 有清晰的目标 skill、目标文件、输入输出变化和验证计划，归为 `integration`。
3. 同时满足以上两项，归为 `both`。
4. 只有项目专属路径、临时错误或无法复现的偶然现象时，仍可生成贡献，但 `promotion.recommendation` 必须为 `retain_as_case`，不能建议直接升级为 primitive。

### 3. 选择集成层级

```text
固定事实、工具说明、数据格式、限制       -> primitive resource
动态路线、资源取舍、失败回退、结果解释     -> expert skill
固定入口、稳定步骤、可验证产物             -> executor skill
跨技能调度规则                             -> 只提出 orchestrator 变更建议，不直接修改
```

若无法明确判断，使用 `promotion.recommendation: human_review`，并列出需要人工确认的问题。

### 4. 生成结构化文档

`contribution.md` 必须包含以下章节，顺序保持一致：

1. `Contribution Metadata`
2. `Task Summary`
3. `Interaction Timeline`
4. `Decisions And Evidence`
5. `Resources And Skills`
6. `Artifacts And Verification`
7. `Failures And Recovery`
8. `Reusable Knowledge`
9. `Integration Proposal`
10. `Promotion Decision`
11. `Privacy And Limitations`

每个结论尽量绑定到执行轨迹的 `step_id`、验证目标或产物引用。证据只写摘要，不复制大段日志或上游文档。
能力缺口写入 `capability_attribution`；事实、启发式、约束、fallback、反模式、新知识和未决问题写入 `knowledge_discovery`。

### 5. 生成 Issue payload 与提交卡片

当 `issue_mode` 为 `payload_only` 或 `submit` 时，先生成 `issue_payload.json`：

- `title`：`[Knowledge Contribution][<domain>] <短标题>`。
- `body`：贡献摘要、目标路径、复用价值、证据状态、集成建议、验证状态和隐私说明。
- `labels`：至少包含 `knowledge-contribution`；再追加 `domain:<domain>`、`kind:<kind>` 和调用方提供的标签。
- `milestone`、assignee 等字段只有调用方明确提供时才写入。
- Issue body 必须引用仓库内相对贡献路径，不写本机绝对路径、密钥、用户目录或未经授权的远程 URL。

生成 `issue_payload.json` 后，**必须由本技能自动渲染提交卡片**：把 payload 转成人类可直接复制的「标题 / 标签 / 正文」三块，落盘到同一贡献目录的 `submission_card.md`，不再要求贡献作者手动敲命令（这一步与生成 payload 合并为一个技能动作）。渲染调用如下——脚本只读本地文件、不联网、不需要 token、且幂等，payload 不变则重跑结果一致，因此卡片可随时从 `issue_payload.json` 重新生成而无需重跑整个技能：

```bash
python skills/onescience-knowledge-capture/scripts/render_issue_payload.py \
  --payload <contribution-directory>/issue_payload.json \
  --repo <目标仓库 owner/name>
```

`issue_mode: payload_only` 完成后，贡献目录应同时含 `issue_payload.json` 与 `submission_card.md`。

### 6. 提交 Issue

**平台现状（重要）**：gitee.com 的建 Issue API 只服务付费企业版空间；对个人仓库和组织 group 仓库（如 `onescience-ai/oneskills-dev`）调用 `POST /repos/{owner}/{repo}/issues` 一律返回 `404 project or enterprise`，脚本无法自动提交。因此**默认使用 `issue_mode: payload_only`**，由人工在 Gitee 网页端创建 Issue。

#### 6.1 默认路径：payload_only + 人工网页提交

提交卡片已在第 5 步由技能自动生成为 `submission_card.md`，贡献作者或领域同事**无需再运行任何命令行**，直接打开该卡片、按 SOP 在 Gitee 网页端复制创建 Issue 即可。完整网页操作步骤与自检清单见 `references/manual_issue_submission.md`。提交成功后，由提交人把 Issue 编号回填到 `contribution.json.submission`（`status` 改为 `submitted`）。

> 兜底：若卡片缺失或 payload 被手工改过，可用同一脚本单独重生成 `python skills/onescience-knowledge-capture/scripts/render_issue_payload.py --payload <...>/issue_payload.json --repo <owner/name> --stdout`。

#### 6.2 可选路径：submit（仅限企业版空间）

仅当目标仓库位于 **Gitee 企业版空间** 时，`issue_mode: submit` 才可能成功，且必须同时满足：

- `capture.issue_mode == submit`。
- 用户已明确授权创建 Issue。
- `GITEE_TOKEN` 或 `GITEE_ACCESS_TOKEN` 已通过环境变量提供，不能从对话正文读取或写入文件。
- `issue_payload.json` 已通过本技能校验，且产物递归敏感信息扫描无命中。
- 本地贡献文件已成功写入并保留。

```bash
python skills/onescience-knowledge-capture/scripts/submit_gitee_issue.py \
  --payload <contribution-directory>/issue_payload.json \
  --repo <企业空间内的仓库 owner/name> \
  --submit
```

默认命令只校验并打印请求摘要；只有显式带 `--submit` 才发起网络请求。若返回 `404 project or enterprise`，说明目标不是企业版空间，**立即回退到 6.1 的人工路径**，保留本地贡献与 payload，返回 `partial` 并在结果中说明原因，不重复尝试自动提交。提交成功后，把返回的 Issue 编号和页面引用写入 `contribution.json.submission`，不把 access token 写入任何产物。

## 输出契约

必须返回：

```yaml
execution_result:
  skill: onescience-knowledge-capture
  status: success | partial | failed | blocked
  artifacts:
    contribution_directory: <相对或绝对目录>
    files_created:
      - contribution.md
      - contribution.json
      - issue_payload.json
      - submission_card.md   # issue_mode != none 时由第 5 步自动渲染
    issue_submission:
      mode: none | payload_only | submit
      status: skipped | generated | submitted | failed
      issue_number: <可选>
      issue_url: <可选>
  observation:
    summary: <沉淀结果摘要>
    facts_captured: <事实数量或列表>
    reusable_rules: <候选规则数量或列表>
    integration_target: <primitive | expert | executor | orchestrator_review | retain_as_case>
    redactions: <脱敏摘要>
    missing: <缺失信息>
    risks: <风险>
    next_recommendation: <后续人工审查或迁移建议>
```

没有成功写入 `contribution.md` 和 `contribution.json` 时，不得返回 `success`。Issue 提交失败但本地文档和 payload 已生成时返回 `partial`。

## 验证要求

完成前必须执行：

1. `contribution.json` 可被标准 JSON 解析。
2. `contribution.md` 包含全部 11 个必需章节。
3. `contribution_id`、`domain`、`kind` 和 `promotion.recommendation` 非空，`execution_trace` 与 `verification` 为非空列表。
4. 对产物递归扫描敏感信息模式：API key、Bearer token、密码、私钥、常见云凭证和疑似 JWT；命中时阻止 Issue 提交并返回 `blocked` 或 `partial`。
5. Issue payload 的标题、正文和标签与贡献元数据一致。
6. 若执行真实提交，记录 HTTP 状态、Issue 编号和返回 URL；不记录认证头。

## 禁止事项

- 不得默认把交互原文上传到 Gitee。
- 不得将用户私有数据、访问凭据、真实个人身份信息或内部服务器信息写入公开文档。
- 不得为了补全文档而臆造命令结果、版本号、性能数字或成功结论。
- 不得直接把贡献文件伪装成已审核的生产 skill。
- 不得在没有显式授权时创建 Issue、推送代码或修改其他技能目录。
- 不得因为 Issue 创建成功就把知识视为已合并；Issue 只表示进入人工审查队列。
