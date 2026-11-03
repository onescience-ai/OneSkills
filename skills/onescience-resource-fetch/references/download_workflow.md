# 取源与物化工作流（ModelScope / HuggingFace / 官网直链 / 共享目录）

本文件是段 2.5（共享目录 find）与段 3（网络物化）的权威流程。**从哪里取由调用方按 `source_selection.md` 评估决定**：ModelScope 是默认但非唯一最优，HuggingFace（`--source hf`）、官网直链（`--source url`）与共享目录 find（`--find-shared`）走同一套缓存/锁/原子落位/完整性校验/体积上限纪律。实现落在 `scripts/modelscope_hub.py` + `scripts/fetch_resource.py`，与 `onescience-data-standardizer` 内置的下载器**互不依赖**（各自独立演进），但缓存目录、可见文件口径、失败分类保持一致，便于同一份数据被两条链路复用。

## 1. 触发与门控

- 段 1（显式 `source_dir`）与段 2（本地探测）都未命中 → 直接进入下载，**不询问用户**（缺即下是本技能的默认策略）。
- 唯二不下载的情形：调用方显式 `allow_download=false` / `--probe-only`（只读校测、离线受限），或用户要求先确认。此时返回 `resolution_method=probe_only_miss` + `reason=resource_missing`，不得谎报已就绪。
- 下载前只做一件额外前置：目标卷剩余空间 < 2 GiB 时直接 `insufficient_disk_space`，不去写半截缓存。

## 2. repo_id 推断链

优先级从高到低，命中即停（细则见 `repo_id_inference.md`）：

1. `--repo-id` / `provision_spec.repo_id` 显式给出 → `repo_id_source=explicit`
2. `--repo-hint`（资源卡 `spec.md`/`usage.md` 正文、论文链接、`metadata.json` 的 `provider`/`source`/`provenance`）中抽到 `modelscope.cn/<datasets|models>/<org>/<name>` 或 `repo_id: <org>/<name>` → `card_extract`
3. 默认约定 `OneScience/<name>` → `default_convention`；拼出来的仓库名先做一次只读存在性确认，不存在则走站内检索 + 元数据打分：逐字同名命中记 `name_search`，靠任务语义/热度/命名空间/体积择优命中记 `name_search_ranked`，按分数取前 `--candidate-attempts`（默认 3）个候选依次尝试，前一个下载失败或校验不过就换下一个（记进 `fetch_attempts`）；候选全被排除（需凭据 / 超 `--max-repo-bytes`）→ `no_selectable_repo`，一个候选都没有或检索接口不可达 → 仍按默认约定发起下载，让后端给权威原因。`--strict-name` 才退回"多个逐字同名 → `repo_ambiguous`"。细则见 `repo_id_inference.md` 第 4 节；`--no-name-search` 可整层关掉，`--probe-only` 与显式/资源卡抽取的 `repo_id` 都不会触发这层查询。

`repo_id_source` 必须随结果返回：它决定了"这个仓库名是猜的还是取证的"。

## 3. 缓存与幂等

| kind | 缓存落点 |
| --- | --- |
| dataset | `~/.onescience/datasets/<name>/raw/` |
| model | `~/.onescience/models/<name>/` |

缓存根默认 `~/.onescience`，可用 `ONESCIENCE_RESOURCE_HOME` 整体改写（系统盘小时尤其有用）；附加只读探测目录用 `ONESCIENCE_DATASETS_DIR` / `ONESCIENCE_MODELS_DIR`，与 `onescience-data-standardizer` 用的是同一批变量，所以一边取到的数据另一边不会重复下载。

- 命中判定 = 目录下**至少一个可见文件**（相对路径每一段都不以 `.` 开头）。SDK 记账残留（`.lock/`、`._____temp/`、`.mdl`/`.msc`）不算命中。
- 探到统一缓存目录时 `resolution_method=cache_hit`，其余本地命中（工作区、共享库、注册表里的外部路径）记 `local_probe`；两者都不会发网络请求。
- 空目录先删除再下载；下载写入**按资源名隔离的工作目录** `~/.onescience/datasets/<name>/.raw.tmp.<pid>`（dataset）或 `~/.onescience/models/.state/<name>/.<name>.tmp.<pid>`（model），成功归一后才 `move` 到正式位置。
- 锁也按资源名隔离在同一工作目录下的 `.fetch.lock`（`O_CREAT|O_EXCL`），轮询最多 30 分钟；锁文件超过 1 小时视为陈旧可抢占。两个不同资源的下载不会互相排队。
- 失败后的清理只会动**本资源**的路径：删自己的临时目录 → 若该资源的缓存目录只剩记账残留则删目录骨架；删作用域目录时用 `rmdir` 语义（非空即停），不会连带删掉兄弟资源。
- 复用：`resource_registry.json` 里已有同 `name`+`kind` 且 `local_path` 可用时，段 2 直接命中，不再发起网络请求。

## 4. 三级后端降级

```text
SDK  snapshot_download(repo_id, repo_type=dataset|model, cache_dir=<tmp>, revision=?)
 │    失败：可重试类（network / checksum）退避重试 1s→4s→16s，最多 3 次
 │    repo_not_found / auth / disk 立即短路，不再空耗重试预算
 ▼
CLI  modelscope download --dataset|--model <repo_id> --repo-type <t> --local_dir <tmp> [--revision R]
 │    注意 v1.37+ 无 --repo-id 参数；rc≠0 时按 stderr 尾部分类
 ▼
Git LFS（默认关闭，需 --allow-git-lfs-fallback）
     git lfs install && git clone https://www.modelscope.cn/<type>s/<repo_id>.git <tmp>
```

- 三个后端都不可用（既无 SDK 也无 CLI）→ `reason=backend_unavailable`，建议在目标环境 `pip install modelscope`；是否安装由 installer 决定，本技能不代装。
- 降级不能抹真因：SDK 已给出具体分类（如 `repo_not_found`/`network_error`）而 CLI 回退仅仅因为未安装而失败时，上报的 `blocked_reason` 仍取前者，后者进 `details.fallback_errors`；只有所有尝试都说"后端不可用"时才报 `backend_unavailable`。
- SDK 落点可能多一层仓库名目录，归一化时把唯一子目录上提到正式路径，避免下游拿到两层嵌套目录。

## 4.5 其他来源后端（HuggingFace / 官网直链 / 共享目录）

```text
共享目录 find   --find-shared [--shared-root <根>]：本地探测未命中、下载前，对有界共享根按名查找
                （深度≤4、命中目录不下钻、扫描封顶），命中现成副本 provider=shared、零网络
HuggingFace     hub.fetch_hf -> huggingface_hub.snapshot_download(repo_id=org/name, local_dir=<tmp>)
                repo_id 必须 org/name（HF 无单命名空间默认约定，不给不猜）；镜像用 --hf-endpoint/HF_ENDPOINT
官网直链        hub.fetch_url -> urllib 下载单个 http(s) 文件/归档到 <tmp>，归档自动解包，受体积上限
                非 http(s) 一律 invalid_source_link；落盘后同样过完整性校验并注册
```

- 三种新后端与 ModelScope 三级降级共享 `_fetch_lock`/临时目录/`_normalize`/非空校验/失败清理，换来源不降标准；`fetch.method` 分别记 `hf`/`url`，`resolution_method` 记 `huggingface_fetch`/`url_fetch`/`shared_find`，`provider` 记 `huggingface`/`url`/`shared`。
- HuggingFace/官网直链同样**不代管凭据**：gated HF 仓或需登录的官网失败只报 `authentication_failed`/`network_error`；来源权威性由调用方负责，禁止用来路不明的镜像/网盘顶替。

## 5. 失败分类与上报

分类函数 `modelscope_hub.classify_error`，判定顺序**不可调换**：认证 → 网络 → 磁盘 → 校验和 → 仓库不存在 → 兜底。网络信号必须先于 repo 措辞——DNS/断网的 traceback 里常混有 "repo ... not exist"，先匹配仓库规则会把可重试的网络故障误判成 `repo_not_found`（标准器链路已实测过该缺陷）。

| reason | 含义 | 可重试 | 上报要求 |
| --- | --- | --- | --- |
| `backend_unavailable` | SDK 与 CLI 都没有 | 否（先装） | 给出 `pip install modelscope`；需要装环境交 installer |
| `network_error` | 连接/超时/DNS/代理 | 是 | 3 次退避后仍失败才上报，附最后一次错误尾部 |
| `repo_not_found` | 404 / 不存在 | 否 | 返回 `suggested_repo_id`，请调用方核对名称或改提供显式路径 |
| `repo_ambiguous` | `--strict-name` 下站内多个逐字同名仓库 | 否 | 列 `details.candidates` 请调用方选定 `--repo-id`；默认（非 strict）不报此因，而是按打分自动择优并换候选重试 |
| `no_selectable_repo` | 有候选但都需凭据或超体积上限 | 否 | 列 `details.candidates` 与排除原因；出路是配凭据 + `--allow-gated`、放宽 `--max-repo-bytes`、或显式 `--repo-id` |
| `resource_plan_empty` | 只给任务且规划 + 两轮检索都无候选 | 否 | 说明还缺哪类信息（领域/模态/任务类型），不得改下占位数据 |
| `authentication_failed` | 401/403/token | 否 | 提示配置 `MODELSCOPE_API_TOKEN` 或 `~/.modelscope/credentials`；**本技能不读写凭据** |
| `insufficient_disk_space` | 空间不足 | 否 | 报出剩余字节与阈值 |
| `checksum_mismatch` | 内容损坏 | 是 | 建议清缓存重取 |
| `empty_payload` | 报成功但无可见文件 | 否 | 明确"仓库为空或仅元数据"，不得当成成功 |
| `verification_failed` | 落盘但必需文件/大小不过 | 否 | 保留已落盘路径 + 逐项 checks，交调用方决定换仓库；自动择优下若还有候选未试，脚本会先换下一个候选再上报 |

任何失败都写进 `missing_resources[]`（含 `message`、`details`、`next_recommendation`），`status` 取 `failed`（全部失败）或 `partial`（部分成功）。**禁止**把失败包装成 `success`，禁止用空目录或占位文件让下游继续。

未命中时的 `details.probed[]` 逐个给出候选目录的 `exists/usable/files/bytes`，调用方据此区分"路径不存在"与"存在但是空骨架"，前者是名称/仓库问题，后者是上次下载中断。

## 6. 凭据边界

- 公开仓库无需凭据；私有/受限仓库由 ModelScope SDK/CLI 自行读取 `MODELSCOPE_API_TOKEN` 或 `~/.modelscope/credentials`。
- 本技能不收集、不写入、不回显任何 token；不在结果 JSON 里出现凭据路径之外的敏感内容，也不把凭据写进 `resource_registry.json`。

## 7. 观测字段

`provisioned_resources[].fetch` 必含：`repo_id`、`repo_id_source`、`repo_type`、`local_path`、`method`（`sdk|cli|git_lfs|hf|url|cache_hit`）、`files`、`bytes`、`duration_seconds`、`retries`；顶层 `provider` 标明最终来源（`modelscope|huggingface|url|shared|cache|local|explicit`）。段 1/段 2/段 2.5 命中时 `fetch.method` 记解析方式（`explicit_path`/`local_probe`/`shared_find`）并附 `note: resolved locally, no provider call`，避免让调用方误以为发生过网络请求。
