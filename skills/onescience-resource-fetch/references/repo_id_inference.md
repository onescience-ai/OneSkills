# 资源名、类型与 repo_id 判定

## 1. kind 判定（dataset / model）

只有两类，判据是**下游怎么消费它**，不是它叫什么：

| kind | 典型信号 | 落点 |
| --- | --- | --- |
| `model` | 权重、checkpoint、`.pt/.pth/.ckpt/.safetensors/.onnx`、"加载模型推理/微调"、ModelScope `models/` 页面、`from_pretrained` 的目标 | `~/.onescience/models/<name>/` |
| `dataset` | 训练/评测数据、`.nc/.h5/.zarr/.csv/.extxyz/.xyz`、train/val/test 切分、ModelScope `datasets/` 页面、要交给 datapipe/standardizer | `~/.onescience/datasets/<name>/raw/` |

线索冲突时按优先级：用户原话 > 资源卡里给出的链接前缀（`datasets/` 还是 `models/`）> 消费方契约（trainer/infer 要 model，data-standardizer/dataset-builder 要 dataset）。仍判不准时**不回问用户**：按消费方默认选定一个 `kind`，先用 `search --kind` 确认该类型下确有候选再物化；任务确实两边都要（既要权重又要评测数据）时发两条 `provision_spec`，不要为了省事把同一份数据下两遍。

## 2. name 规范

`name` 同时用作缓存目录名与注册表键，必须是单段安全名：`^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$`（脚本侧 `validate_name` 强校验，含 `/`、`\`、`..` 直接 `invalid_resource_name`）。

- 论文/资源卡里出现的大小写与分隔符保持原样作为逻辑名，不做隐式小写化——`ERA5-tutorial` 与 `era5-tutorial` 会被当成两个不同资源。
- 同一份数据的不同子集用独立 name（如 `mace-mp-0` 与 `mace-mp-0-small`），不要把子目录塞进 name。
- 用户给的是中文描述（"藏红花基因数据"）或只给了任务时，按 `resource_planning.md` 第 2 节自行派生一个稳定的英文安全名（如 `saffron_genome`），把中文原文放进 `--search-query` / `--task-hint` 参与检索与打分；派生名写入注册表时在 `limitations` 注明"逻辑名由任务描述派生"，不要为了一个名字去回问用户。

## 3. repo_id 抽取来源

按 `download_workflow.md` 的优先级执行，可抽取的文本来源：

1. 用户或上游 executor 直接给的 `repo_id` / 页面链接；
2. primitives 资源卡正文——`spec.md`、`usage.md`、`knowledge.md` 里的 `modelscope.cn/datasets/<org>/<name>`、`modelscope.cn/models/<org>/<name>` 或 `repo_id: <org>/<name>`；把这些原文通过 `--repo-hint` 传入，**不要自己改写**抽取结果；
3. `metadata.json` 的 `provider` / `source` / `provenance` 字段值；
4. 都没有时回落默认约定 `OneScience/<name>`，并按第 4 节做存在性确认与必要时检索。

正则实现见 `fetch_resource.infer_repo_id`（`REPO_URL_RE` / `REPO_ID_RE`）。抽到多个候选时取与 `name` 最贴近的一个，并在 `limitations` 里说明"repo_id 由资源卡抽取，存在多个候选"。

## 4. 回落顺序：默认约定 → 站内检索

只有 `repo_id` 是由默认约定拼出来时（`repo_id_source=default_convention`）才会走这一节；调用方显式给的、或从资源卡抽到的 `repo_id` 不做任何额外查询。

1. 先对 `OneScience/<name>` 做一次存在性确认（官方 OpenAPI 只读 `GET /{datasets|models}/<repo_id>`，一个请求，不下载）；
2. 确认不存在 → 站内检索（`GET /{datasets|models}?search=<query>&page_size=20`）。检索词是 `name` 加上 `--search-query` 给的额外词；**该端点按子串匹配，长句几乎必然 0 命中**，所以脚本在整句无命中时自动按空白与标点拆词重试（最多 6 次查询，实际发出的每次记在 `search_trace`/`queries_tried`）；
3. 候选打分排序（`modelscope_hub.rank_candidates`，权重从高到低）：逐字同名 1000 > 名称互为前缀或包含 400 > 标题/描述与请求词共同词 80×n（≤240）> 与任务描述共同词 40×n（≤240）> 任务标签命中 60×n（≤180）> 下载量 `100×log10(1+downloads)`（≤400）> 可信机构命名空间 150 > `likes`（≤50）> 体积在上限内按 `150×(1-size/max)` 越小越优先；同分按下载量、体积、`repo_id` 字典序破平。每个候选都带 `score` 与中文 `reasons`；
4. 排除项：`gated`/`private`/`login_required` 的仓库默认不进自动择优（`--allow-gated` 可放开），体积超过 `--max-repo-bytes`（缺省读 `ONESCIENCE_RESOURCE_MAX_REPO_BYTES`，再缺省 8 GiB）的候选记 `excluded=over_max_bytes`；体积未知的候选保留但注明未参与体积排序；
5. 择优与降级重试：按分数取前 `--candidate-attempts`（默认 3）个候选依次尝试，逐字同名记 `repo_id_source=name_search`，靠语义/热度选中的记 `name_search_ranked`；某个候选下载失败（`repo_not_found`/`network_error`/`authentication_failed`/`empty_payload`/`checksum_mismatch`/`fetch_failed`）或落盘后完整性校验不过，就换下一个候选，全过程记进 `fetch_attempts`；
6. 全部候选用尽 → 上报最后一个候选的权威原因（不要把"检索没搜到"当成失败原因，也不要把可重试的网络故障写成 `repo_not_found`）；有候选但全被排除 → `no_selectable_repo` + `details.candidates`；一个候选都没有 → 保留默认约定发起真实下载，让后端给出 404/鉴权等权威原因；
7. 保守模式：`--strict-name` 只采纳**逐字同名且唯一**的命中，多个同名时报 `repo_ambiguous` + `details.candidates` 交调用方选定，不代作选择；
8. 存在性确认返回 401/403 视为仓库存在（受控仓库），直接交给带凭据的 SDK/CLI 路径。

关掉这一层：`--no-name-search`。换站点：`MODELSCOPE_OPENAPI_BASE`（默认 `https://www.modelscope.cn/openapi/v1`）。`--probe-only` 与只读 `probe` 根本走不到这里，不产生任何网络请求；`search` 子命令只读、不写缓存，可反复用来预览候选。

## 5. 为什么这不等于“随便抓一个仓库”

下面第 6 节的禁止项仍然成立：不得从公开搜索引擎 / 第三方镜像抓来源不明的权重。自动择优的边界是：

- **只走 ModelScope 官方 OpenAPI**，候选全部来自站内检索结果，不拼接、不猜测 `org/name`；
- **打分可审计**：`selection` 里带回 `chosen`/`score`/`reasons`/`alternatives`/`excluded`/`searched`，调用方能看出为什么是它、还考虑过谁；
- **有体积上限**：自动选中的仓库不会超过 `--max-repo-bytes`（缺省 8 GiB），避免一句话任务拉下几百 GB；
- **有校验与降级**：落盘后要过完整性校验，不过就换下一个候选，而不是把坏数据交下去；
- **可信命名空间优先**：`modelscope`/`iic`/`damo`/`alibaba-nlp`/`ai-modelscope`/`qwen`/`deepseek`/`thudm`/`opencsg`/`infinity` 在同等条件下排在个人镜像之前；
- 要"绝不代作选择"的调用方用 `--strict-name` 拿回旧的 `repo_ambiguous` 语义。

风险量级相当于人工在站点搜索框里输入名字、按下载量与命名空间挑第一个结果，区别是这里把挑选依据写进了结果里。

## 6. 默认约定与“未发布”的区别

默认 `OneScience/<name>` 不存在、检索也没有任何可选候选时，最终返回 `repo_not_found` + `suggested_repo_id`，语义是**该资源没按约定发布、站内也找不到可用替身**，不是“网络坏了”：

- 不可重试，SDK 立即短路，CLI / Git LFS 各试一次；
- 下一步只有四种合法出路：换更短/更准的检索词再试一轮（`search`）、调用方给出真实 `repo_id`、提供本地 `source_dir`、或改由 `onescience-primitive-distiller` / `onescience-modelscope-publish` 把资源发布进约定仓库；
- 不得因为“仓库不存在”就退化去公开搜索引擎或镜像站抓一个名字相近的仓库——那会把来源不明的权重写进训练链路。

## 7. revision 与版本可追溯

`revision` 来自用户指定、资源卡声明或注册表记录。留空即取 ModelScope 默认分支，此时 `limitations` 必须注明"未固定版本，后续复现可能取到不同内容"；对需要严格复现的任务（论文复现、基准评测），优先固定 `revision` 再物化。
