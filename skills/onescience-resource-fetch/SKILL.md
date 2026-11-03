---
name: onescience-resource-fetch
description: OneSkills 资源层「物化」技能（type=resource），专管数据准备：任务需要的模型权重/checkpoint 或数据集在本地不存在时，直接从 ModelScope 拉到本地统一缓存并返回可用的绝对路径。解析顺序固定四段式——任务级资源规划（请求里没有具体资源名时，先按 references/resource_planning.md 把任务拆成资源需求并派生检索词，不回问用户）→ 调用方显式路径 → 本地探测（~/.onescience 缓存、工作区 data/、注册表记录）→ ModelScope 下载；缺即下、不询问确认。对提示词几乎不做要求：只给裸名（无需组织名/repo_id）即可下载，只给任务描述（连数据名、模型名都没给）也能自己定位仓库；repo_id 定位链为显式 → 资源卡抽取 → 默认约定 OneScience/<name> → 官方 OpenAPI 检索并按元数据打分自动择优（逐字同名 > 名称互为前缀或包含 > 标题描述与请求词重合 > 任务语义重合 > 任务标签命中 > 下载量 > 可信机构命名空间 > 体积在 --max-repo-bytes 上限内且更小），检索长句命中为空时脚本自动拆词重试；多个候选按分数顺序降级重试，选择理由与落选候选写进 selection 字段透明上报；只有显式 --strict-name 才退回"多同名不猜、报 repo_ambiguous"。下载走 SDK→CLI→Git LFS 三级降级，完成后做完整性校验（可见文件数/必需文件通配/大小下界/content_digest）并把 {name, kind, repo_id, local_path, digest} 注册进 ~/.onescience/resource_registry.json 供复用。接收统一 resource_retrieval_request（intent=provision，或用户点名"下载模型/数据集""缺少数据集/权重""准备训练数据""接入数据"，或只给出一个训练/微调/评测/复现类 AI4S 任务而没点任何资源名），返回 resource_retrieval_result 并附 provisioned_resources[]。边界：只物化 ModelScope 的 dataset / model 两类仓库，不做格式标准化转换（交 data-standardizer）、不检索知识卡（交 primitives）、不编码（交 coder）、不训练推理（交 trainer/infer）、不装软件（交 installer）、不写技能树、不代管凭据（认证失败只如实报 authentication_failed）；禁止用占位数据/模拟数据顶替未获取到的资源。
type: resource
capabilities:
  owns:
    - 资源缺失判定
    - 本地候选路径探测
    - ModelScope 仓库下载
    - 下载完整性校验
    - 本地资源缓存注册
  not_owns:
    - 数据格式标准化转换
    - 知识卡检索与在线查证
    - 代码生成与修改
    - 训练与推理执行
    - 环境与软件安装
    - 凭据管理
  inputs:
    - resource_retrieval_request
  outputs:
    - resource_retrieval_result
  downstream: []
  prereq: []
  intent_aspects:
    - resource_provision
    - data_preparation
  operation_types:
    - retrieve
    - create
  artifact_types:
    - dataset
    - model
  domains:
    - earth
    - biology
    - materials
    - cfd
    - general
  trigger_keywords:
    - 下载模型
    - 下载数据集
    - modelscope
    - 缺少数据集
    - 缺少模型权重
    - 准备训练数据
    - 接入数据
    - 资源物化
    - 找数据集
    - 选模型权重
    - 准备数据
    - 任务级资源规划
    - 自动选仓下载
---

# OneScience Resource Fetch

你是 OneSkills 资源层的物化技能（`type=resource`）。资源层的知识召回由 `onescience-primitives` 负责，**把资源真正取到本地**由你负责：输入一个逻辑资源名（数据集名 / 模型名），输出一个可直接使用的本地绝对路径 + 完整性结论，或如实报告取不到及其原因。

渐进披露：正文只保留触发、硬门禁与契约字段；下载细节、契约扩展、校验细则下沉 `references/`，在标注「必须先读取」的位置必须先读再做。

## 何时使用

- 任务所需的**数据集**或**模型权重/checkpoint** 在本地、工作区、缓存里都不存在，且该资源发布在 ModelScope。
- 上游（orchestrator / executor）在 `blocked_reason=data_missing`、`model_checkpoint_missing`、`resource_acquisition` 类缺口上要求补数据准备。
- 用户直说"把 X 数据集下到本地""取一下 MACE/ERA5 的权重""准备训练数据"。
- 用户**只给了裸资源名**（没有组织名、没有 `repo_id`，甚至语种或大小写与仓库名不完全一致）：站内检索 + 打分自动择优后直接物化，不回问"完整仓库名是什么"。
- 用户**只给了任务描述**（连数据集/模型名都没提，如"训练一个猫狗图像分类器""复现这篇论文的 DFT 结果"）：先做资源规划再检索定位，把选中的仓库与理由一并交回。

## 何时不要用

- 缺的是**知识**（论文、参数惯例、晶格结构）→ `onescience-primitives` / `onescience-online-knowledge`。
- 缺的是**软件包或运行环境**（pip/conda 库、VASP/LAMMPS）→ `onescience-installer`。
- 已有本地路径且只需**格式转换 / AI-Ready 标准化 / 切分** → `onescience-data-standardizer`。
- 需要**发布**资源到 ModelScope（上传）→ `onescience-modelscope-publish`。
- 用户显式禁止联网或要求只做只读校测 → 用 `probe` / `--probe-only`，不得下载。

## 强制协议

1. 你接收统一 `resource_retrieval_request`、返回统一 `resource_retrieval_result`（`intent=provision` 时的扩展字段见 `references/provision_contract.md`，**构造请求或返回结果前必须先读该文件**）。
2. 物化只能通过本技能 `scripts/fetch_resource.py provision` 完成，候选检索只能用同脚本的 `search` 子命令（只读）；不得手写 `wget`/`curl`/`git clone` 绕过三级降级与幂等缓存，也不得直接把 `modelscope download` 命令丢回给用户当结果。
3. 自动择优必须透明：结果里的 `selection`（`chosen`/`score`/`reasons`/`alternatives`/`excluded`）与 `fetch_attempts` 原样带回，不得只报一个本地路径而不说选了哪个仓库、为什么选它、还试过哪些。
4. 写入边界：只允许写 `~/.onescience/**` 与调用方显式指定的目录。**技能树 `skills/**` 与仓库知识区一律只读**；资源内容交给调用方后由调用方自行读取，本技能不加工数据内容。
5. 缺即下：段1 显式路径与段2 本地探测未命中即进入下载，不弹确认、不要求用户批准；但**绝不允许**在下载失败后用占位数据、随机张量、示例文件或缺失文件"凑齐"目录继续下游。
6. 路径规范：下文 `scripts/`、`references/` 均指**实际加载的本技能目录**下的路径，不假定技能装在当前工作目录；调用示例中的绝对路径由执行时拼出。
7. 结果只声明事实：`status`、`method`、`files/bytes`、`verification.checks` 必须来自脚本真实输出；`repo_not_found` / `authentication_failed` 等缺口要原样透传 `blocked_reason` 与 `next_recommendation`。

## 输入契约

```yaml
resource_retrieval_request:
  user_request: <需要准备的资源描述，含资源名与类型>
  task_state_summary: <当前任务状态摘要，可选>
  intent: provision                 # 缺省即 provision（本技能只做这一件事）
  content_request: <"下载并返回本地路径" | "只探测" | "校验已有资源"，可选>
  provision_spec:
    - name: <逻辑资源名，如 era5-tutorial / mace-mp-0>
      kind: dataset | model
      domain: <earth | materials | ...，可选>
      repo_id: <显式 ModelScope repo_id，可选，最高优先级>
      repo_hints: [<资源卡/论文里出现的 modelscope.cn 链接或 repo_id 文本>，可选]
      revision: <版本/分支，可选>
      source_dir: <段1 显式本地目录，可选>
      required_files: [<下载后必须存在的文件通配式>]
      min_bytes: <大小下界，可选>
      allow_download: <true|false，默认 true；false 等价于只探测>
      allow_name_search: <true|false，默认 true；false 等价于禁用按名检索>
      allow_git_lfs_fallback: <true|false，默认 false>
      search_query: [<任务级检索词，可选；与 name 一起决定候选命中面>]
      task_hint: [<任务描述片段，可选；参与候选打分>]
      max_repo_bytes: <自动择优的体积上限，默认 8 GiB，可用 --max-repo-bytes 或环境变量覆盖>
      candidate_attempts: <按打分顺序最多尝试几个候选，默认 3>
      strict_name: <true|false，默认 false；true 时多个同名仓库不代作选择>
      allow_gated: <true|false，默认 false；true 时把需凭据的仓库纳入择优>
```

`provision_spec` 缺失时，从 `user_request` 抽取资源名与类型（数据集/模型判定见 `references/repo_id_inference.md`）。抽取不到名称**不等于要先回问用户**：按 `references/resource_planning.md` 做任务级资源规划——拆出需要哪些资源、各自 `kind` 与体积上限、派生安全逻辑名与 1–3 个检索词，再用 `search` / `--search-query` 定位候选；只有规划加两轮检索都拿不到任何候选时，才如实报 `resource_plan_empty` 并说明缺什么。不得凭空捏一个仓库名去下载，也不得用占位数据顶替。

## 执行流程

1. **规划与定名定型**：为每个资源确定 `name` 与 `kind`（dataset/model），名称决定缓存落点与默认 repo_id 约定。请求里没有具体资源名时先做**任务级资源规划**（读 `references/resource_planning.md`）：从任务反推需要哪些 dataset/model、领域与体积上限、必需文件，派生安全逻辑名与检索词，把任务原文填进 `--task-hint`。
2. **段1 显式路径**：给了 `source_dir` 就用它；目录内无可见文件 → `blocked_reason=explicit_path_empty`，不得静默改走下载后当作用户给的路径。
3. **段2 本地探测**：按顺序探测 `ONESCIENCE_DATASETS_DIR`/`ONESCIENCE_MODELS_DIR`（若设置）→ 统一缓存 `~/.onescience/datasets/<name>/raw`（dataset）或 `~/.onescience/models/<name>`（model）→ 共享只读库 `/public/share/onestore/onedatasets/<name>` → 工作区 `data/<name>`、`.onescience/data/<name>` → `resource_registry.json` 记录路径；命中判据是**至少一个非隐藏文件**（口径与标准器一致）。探到统一缓存目录时记 `resolution_method=cache_hit`，其余本地命中记 `local_probe`。
4. **段3 ModelScope 物化**：`repo_id` 推断链（显式 → 资源卡抽取 → 默认约定 `OneScience/<name>` → 官方 OpenAPI 检索 + 元数据打分自动择优）、三级降级（SDK→CLI→Git LFS）、临时目录原子落位、锁与重试、磁盘空间前置、失败分类，全部按 `references/download_workflow.md` 与 `references/repo_id_inference.md` 第 4 节执行，不自行简化。打分顺序：逐字同名 > 名称互为前缀或包含 > 标题描述与请求词重合 > 任务描述重合 > 任务标签命中 > 下载量 > 可信机构命名空间 > 体积在上限内且更小；`gated/private/login_required` 与超出 `--max-repo-bytes` 的候选不进自动择优（记入 `selection.excluded`）。最多试 `--candidate-attempts`（默认 3）个候选，前一个取不到或完整性校验不过就换下一个，全过程记进 `fetch_attempts`。只有 `--strict-name` 才退回"多个逐字同名 → `repo_ambiguous` 交调用方选定"。
5. **完整性校验**：可见文件数 ≥ `min_files`、大小 ≥ `min_bytes`、每个 `required_files` 通配式都命中，并计算 `content_digest`；任一不过 → `blocked_reason=verification_failed`，把已落盘路径与失败项交回调用方，**不得改判通过**。
6. **注册与返回**：写 `~/.onescience/resource_registry.json`（幂等 upsert，不删除历史），组装 `resource_retrieval_result`，`provisioned_resources[]` 每项给出 `local_path`、`repo_id`、`resolution_method`（`explicit_path|local_probe|cache_hit|modelscope_fetch|probe_only_miss`）、`files`、`bytes`、`content_digest`、`verification`、`limitations`。

## 脚本入口

```bash
# 物化一个数据集（缺即下，结果 JSON 同时落盘）
python3 scripts/fetch_resource.py provision \
  --name <dataset_name> --kind dataset --domain <domain> \
  [--repo-id <org/name>] [--repo-hint "<资源卡原文片段>"] [--revision <tag>] \
  [--source-dir <段1显式目录>] [--required-file "*.nc" --required-file "README.md"] \
  [--no-name-search] [--min-bytes <N>] [--extra-probe-path <dir>] [--output <result.json>]

# 只给任务或关键词：先看候选与打分（只读，不下载、不写缓存）
python3 scripts/fetch_resource.py search \
  --query "<任务关键词或裸资源名>" [--query "<同义词>"] --kind dataset|model \
  [--task-hint "<任务描述原文>"] [--top 8] [--max-repo-bytes <N>] [--output <cands.json>]

# 任务级物化：逻辑名自拟，检索词与任务描述交给打分
python3 scripts/fetch_resource.py provision --name <自拟安全名> --kind dataset \
  --search-query "<关键词>" --task-hint "<任务描述>" \
  [--max-repo-bytes <N>] [--candidate-attempts 3] [--allow-gated] [--strict-name]

# 只探测、绝不下载（只读校测 / 离线受限）
python3 scripts/fetch_resource.py provision --name <name> --kind model --probe-only
python3 scripts/fetch_resource.py probe --name <name> --kind dataset
python3 scripts/fetch_resource.py list
```

`--name` 可重复以一次准备多个资源，但 `--kind`、`--domain` 与校验参数对全部名字生效；`--local-dir` / `--repo-id` 只描述单个资源，与多个 `--name` 同时出现时脚本直接报参数错误（退出码 2）而不是把同一个路径/仓库复用给第二个资源。`--name` 是单段安全目录名（`[A-Za-z0-9][A-Za-z0-9._-]*`），资源卡里写成 `iic/nlp_bert_...` 这类带命名空间的标识时，把目录名放进 `--name`、把完整 `org/name` 放进 `--repo-id`，不要整串塞进 `--name`（会按 `invalid_resource_name` 拒绝，避免越界写目录）。缓存根可用 `ONESCIENCE_RESOURCE_HOME` 改位（默认 `~/.onescience`），本地附加探测目录用 `ONESCIENCE_DATASETS_DIR` / `ONESCIENCE_MODELS_DIR`（与 `onescience-data-standardizer` 同一变量），按名检索的接口基址用 `MODELSCOPE_OPENAPI_BASE` 改位（默认 `https://www.modelscope.cn/openapi/v1`）。退出码 0=全部可用，1=有资源取不到（原因见 JSON），2=参数错误。

`search` 的输出是**检索建议不是资源结论**：选定候选后用 `provision --repo-id <repo_id>` 物化，或直接把同一批关键词交给 `provision --name/--search-query` 让脚本自动择优；长句检索命中为空时脚本会自动按空白与标点拆词重试（`queries_tried` 记录了实际发出的每次查询）。自动择优的体积上限默认 8 GiB，可用 `--max-repo-bytes` 或 `ONESCIENCE_RESOURCE_MAX_REPO_BYTES` 覆盖，显式 `--repo-id` 不受此限。

解析结果优先读 `--output` 指定的文件：脚本自身只把信封 JSON 写到 stdout，但 ModelScope 后端日志默认也走 stdout（脚本已把这些日志改道 stderr），传 `--output` 可彻底不依赖通道干净。

## 输出契约（要点）

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <本次准备了什么>
  detected_domain: <领域>
  task_intent: resource_provision
  provisioned_resources:
    - name: <逻辑资源名>
      kind: dataset | model
      local_path: <可直接使用的绝对路径>
      resolution_method: explicit_path | local_probe | cache_hit | modelscope_fetch
      repo_id: <实际来源 repo_id；本地命中为 null 或注册表记录值，不臆造>
      repo_id_source: explicit | card_extract | default_convention | name_search | name_search_ranked | registry_or_unknown
      fetch: {method: sdk|cli|git_lfs|cache_hit, files, bytes, retries, duration_seconds}
      selection: {chosen, score, reasons[], name_exact, file_size, downloads, license,
                  searched[], max_repo_bytes, alternatives[], excluded[]}   # 走过检索择优时给出
      fetch_attempts: [{repo_id, repo_id_source, outcome, files, bytes}]     # 试过的候选与结局
      files: <int>
      bytes: <int>
      content_digest: <sha256>
      verification: {passed: true, checks: [...], failures: []}
      why_matched: <by what stage resolved>
      limitations: <来源与校验边界，1-2 句>
  missing_resources:
    - {name, kind, reason, suggested_repo_id, next_recommendation, details}
  blocked_reason: <missing_resources[0].reason，仅存在缺失时>
  next_recommendation: <该缺口该怎么补，仅存在缺失时>
```

## 按需读取

- 构造 `resource_retrieval_request` / 组装返回结果前：`references/provision_contract.md`（与 primitives 共用契约的 provision 扩展、下游消费规则）。
- 请求里只有任务描述、没有具体资源名时（**必须先读**）：`references/resource_planning.md`（任务 → 资源需求分解、检索词构造、候选打分解读、换候选与放弃条件）。
- 进入段3 下载前：`references/download_workflow.md`（repo_id 推断链、缓存与幂等、锁、三级降级、失败分类与凭据边界）。
- 判定 `kind`、名称与候选仓库时：`references/repo_id_inference.md`。
- 校验规则与下游注册（谁消费 `local_path`、与 `data_management.json` 的关系）：`references/verification_rules.md`。

## 职责边界

负责：资源缺失判定、任务级资源规划与仓库选型（在 ModelScope 官方检索里按任务语义与元数据择优）、本地候选探测、ModelScope dataset/model 仓库物化、下载后完整性校验、缓存注册、失败原因如实分类上报。

不负责：数据格式转换与切分（data-standardizer / dataset-builder）、知识检索与在线查证（primitives / online-knowledge）、代码生成（coder）、训练与推理（trainer / infer）、环境安装（installer）、运行提交（runtime）、上传发布（modelscope-publish）、远程算力与站点配置（runsite / scnet-chat）、凭据的存储与代管。
