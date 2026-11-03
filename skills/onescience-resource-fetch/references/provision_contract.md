# Provision 契约扩展

`onescience-resource-fetch` 是第二个 `type=resource` 技能，与 `onescience-primitives` 共用同一信封：入 `resource_retrieval_request`，出 `resource_retrieval_result`。本文件定义 `intent=provision` 时的扩展字段与下游消费规则；`intent` 为 `resource|task|workflow|scenario` 的知识召回仍归 primitives，本技能不参与。

## 1. 分工与选择规则

| 需求 | 归属 | 判据 |
| --- | --- | --- |
| 要知识（模型卡、参数惯例、晶格结构、工作流规划） | `onescience-primitives` | 本地资产能答"是什么/怎么用/什么参数" |
| 要把模型权重或数据集取到本地 | `onescience-resource-fetch` | 关心的是**落盘路径可用性**，不是知识 |
| 两者都要 | 先 fetch 后按 card 消费 | 缺资源又缺知识时各自触发，不互相替代 |

orchestrator 依旧按 `description` 覆盖范围决定是否调用本技能（阶段一步骤 2 的资源技能选择逻辑不变），不因存在两个 resource 技能而要求点名。

## 2. 请求扩展字段

```yaml
resource_retrieval_request:
  intent: provision
  provision_spec:                 # 列表，支持一次准备多个资源
    - name: <逻辑资源名，必填，安全目录名>
      kind: dataset | model       # 必填，判定规则见 repo_id_inference.md
      domain: <可选>
      repo_id: <可选，显式仓库，最高优先级>
      repo_hints: [<含 modelscope.cn 链接或 repo_id 的原文>]
      revision: <可选>
      source_dir: <可选，段1 显式本地目录>
      required_files: [<文件通配式>]
      min_bytes: <可选>
      allow_download: <默认 true；false 等价 --probe-only>
      allow_name_search: <默认 true；false 等价 --no-name-search>
      allow_git_lfs_fallback: <默认 false>
      search_query: [<任务级检索词，可选>]
      task_hint: [<任务描述原文片段，可选，参与候选打分>]
      max_repo_bytes: <自动择优体积上限，默认 8 GiB>
      candidate_attempts: <最多试几个候选，默认 3>
      strict_name: <默认 false；true 时多同名不代作选择>
      allow_gated: <默认 false；true 时把需凭据的仓库纳入择优>
      source: <modelscope | hf | url，段3 取源供应商，默认 modelscope；判据见 source_selection.md>
      hf_repo: <HuggingFace org/name，source=hf 时必需>
      source_url: <官网 http(s) 直链，source=url 时必需>
      hf_endpoint: <HF 镜像 endpoint，默认读 HF_ENDPOINT，如 https://hf-mirror.com>
      shared_roots: [<共享目录根，配合 find_shared 做按名 find>]
      find_shared: <默认 false；true 时下载前对有界共享根按名查找现成副本>
```

`name` 无法从 `user_request` 抽取时**不回问用户**：按 `resource_planning.md` 做任务级资源规划，自行派生安全逻辑名与检索词（填 `search_query`/`task_hint`）；`kind` 判不准时按"消费方怎么用它"决定（喂给训练/推理的是 model，喂给 datapipe/dataset-builder 的是 dataset），仍不确定就先 `search` 验证候选存在再定。没有 `repo_id` 只有裸 `name` 时，默认约定 `OneScience/<name>` 不存在会自动走官方 OpenAPI 检索 + 元数据打分择优，多个候选按分数降级重试（细则见 `repo_id_inference.md` 第 4 节）；`allow_name_search=false` 关掉整层，`strict_name=true` 退回"多同名不代作选择"。规划加两轮检索都拿不到候选，才报 `resource_plan_empty` / `no_selectable_repo`，不得凭空捏仓库名，也不得用占位数据顶替。

一个资源的 `source_dir` / `repo_id` 只属于它自己：多个资源请发多条 `provision_spec` 项（或多次调用），不要共用一个路径/仓库——脚本侧对"多个 `--name` + `--local-dir`/`--repo-id`"直接拒绝（退出码 2）。

## 3. 结果扩展字段

```yaml
resource_retrieval_result:
  task_intent: resource_provision
  provisioned_resources:
    - name / kind / domain
      local_path: <绝对路径，调用方可直接读>
      resolution_method: explicit_path | local_probe | shared_find | cache_hit | modelscope_fetch | huggingface_fetch | url_fetch | probe_only_miss
      provider: explicit | local | shared | cache | modelscope | huggingface | url
      repo_id: <实际来源；本地命中可为 null>
      repo_id_source: explicit | card_extract | default_convention | name_search | name_search_ranked | registry_or_unknown
      fetch: {method: sdk|cli|git_lfs|hf|url|cache_hit, files, bytes, retries, duration_seconds, repo_id}
      selection: {chosen, score, reasons[], name_exact, file_size, downloads, license,
                  searched[], max_repo_bytes, alternatives[], excluded[]}
      fetch_attempts: [{repo_id, repo_id_source, outcome, files, bytes}]
      files / bytes: <int，仅统计可见文件>
      content_digest: <sha256(relative path + size)>
      verification: {passed: true, files, bytes, checks: [...], failures: []}
      registry_key: <dataset:<name> | model:<name>，未注册则 null>
      why_matched / limitations
  missing_resources:
    - {name, kind, reason, message, details, suggested_repo_id, next_recommendation}
  blocked_reason: <missing_resources[0].reason>
  next_recommendation: <missing_resources[0].next_recommendation>
```

`matched_resources` 与 `provisioned_resources` 内容一致，保留前者是为了兼容只认旧字段的调用方；两者不得给出不一致的结论。

`selection` 与 `fetch_attempts` 只在走过站内检索择优时出现（`repo_id_source` 为 `name_search` / `name_search_ranked`）：前者说明"为什么是这个仓库"，后者说明"按什么顺序试过哪些候选、各自结局"。转述给用户时必须带上选中的 `repo_id` 与主要 `reasons`，不能只报一个本地路径——这是自动择优唯一的问责凭证。

## 4. 下游消费规则

- 只有 `provisioned_resources[].local_path` 是**落盘事实**，调用方可直接读取；`content_digest` 与 `verification.checks` 是它被验收过的证据。
- `resolution_method` 的区分对调用方有用：`cache_hit` = 命中统一缓存（同一份数据以前取过），`local_probe` = 工作区/共享库/注册表里的其他路径，`shared_find` = 有界共享目录按名 find 命中的现成副本（零下载），`modelscope_fetch`/`huggingface_fetch`/`url_fetch` = 本次真的走了网络（`provider` 进一步区分 modelscope/huggingface/url）。需要"强制重新拉取"时只能清缓存或传 `revision`，不能靠重复调用同一名字期待刷新。
- 零网络承诺只针对不落盘的前三种 `resolution_method`：`explicit_path` / `local_probe` / `cache_hit` 不产生任何请求。走到下载那一步时，若 `repo_id` 是按默认约定拼的，会先花 1–2 次只读轻量请求做存在性确认与必要时检索（它们不传输数据文件）；`repo_id_source=name_search`（逐字同名命中）与 `name_search_ranked`（按任务语义与元数据择优命中）就是这一层换过仓库的标记，配套 `warnings` 与 `selection.reasons` 会写明原委；检索长句无命中时脚本会自动拆词重试，多花的仍是不传输数据的只读查询。
- 写进 `Task State.resource_bindings` 时：`resource_type` 取 `dataset`/`model`，`path` 取 `local_path`，`purpose` 写明服务于哪个步骤，并保留 `repo_id` 与 `content_digest` 以便复现追溯。
- `missing_resources` 非空即视为该资源缺口未闭合：orchestrator 按 `reason` 分类——`backend_unavailable`/`network_error` 走 installer 或重试，`repo_not_found`/`authentication_failed` 才是需要用户介入的硬约束；`repo_ambiguous` 只在调用方显式要求 `strict_name=true` 时出现（`details.candidates` 是同名候选列表，此时本技能不代作选择）；`no_selectable_repo` 表示有候选但都需凭据或超体积上限（配好凭据加 `--allow-gated`、或放宽 `--max-repo-bytes`、或显式指定 `--repo-id`）；`resource_plan_empty` 表示任务里推不出可检索的资源需求（说明还缺领域/模态/任务类型哪一项）；`details.probed[]` 里的 `exists=true/usable=false` 条目意味着上次下载中断过，而不是路径写错；**任何情况下都不得用占位数据、示例文件或随机张量顶替**（对应 evidence_gates 的 `fabricated` 禁令）。
- 下游若还需要格式标准化，把 `local_path` 作为 `source_dir` 交给 `onescience-data-standardizer`，由它维护自己的 AI-Ready 产物与 `data_management.json` 注册；本技能的 `resource_registry.json` 只描述原始资源位置。

## 5. autonomous_mode 与文件交接

`autonomous_mode=true` 时不额外询问下载确认（本就是缺即下）。文件交接模式下：

- 输入从 `.onescience/handoff/step_{id}.yaml` 的 `task_context.provision_spec`（或 `task_context.resources_needed`）读取；
- 结果原子写入 `.onescience/handoff/step_{id}_result.yaml`，其中 `execution_result.artifacts.provisioned_resources` 携带本节第 3 段的完整结构；
- 单个资源下载可能耗时数十分钟，调用方需按 orchestrator 的 `references/autonomous_mode_details.md` 中 wallclock 预算规则设置 `step_wallclock_budget_seconds`，超时记 `step_timeout` 而不是重试到无限。
