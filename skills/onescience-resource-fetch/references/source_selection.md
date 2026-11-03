# 取源选择：共享目录 / ModelScope / HuggingFace / 官网直链

本篇是"从哪里把资源取到本地"的**权威决策流程**。旧版本技能只认 ModelScope；现在 ModelScope 只是**可选来源之一、且不是无条件第一优先级**——由调用方（宿主大模型）按下面的维度评估，决定先查共享目录、还是走 ModelScope / HuggingFace / 官网直链。脚本对四种来源施加**同一套**缓存、锁、原子落位、完整性校验与体积上限纪律，换来源不降标准。

## 0. 顺序铁律（先近后远，能不下就不下）

1. **段1 显式路径**（`--local-dir` / `source_dir`）→ 命中即用。
2. **段2 本地/统一缓存探测**（`~/.onescience`、`ONESCIENCE_DATASETS_DIR`/`ONESCIENCE_MODELS_DIR`、工作区 `data/`、注册表记录）→ 命中即用，零网络。
3. **段2.5 共享目录 find**（`--find-shared` / `--shared-root` / `ONESCIENCE_SHARED_ROOTS`）→ 在声明的共享根里做一次**有界按名查找**（深度≤4、命中目录不再下钻、扫描预算封顶），命中现成副本即免下载。站点预置数据、内网大体积数据、离线环境优先用这条。
4. **段3 网络物化**：前三步都没货才走下载，来源由第 2 节决定。

前三步命中都是**只读、零网络**，`provider` 分别记 `explicit` / `local`（含 `cache`）/ `shared`；只有段3 才可能发网络请求。

## 1. 四种来源速查

| 来源 | 触发方式 | 何时用 | 来源标识要求 | `resolution_method` | `fetch.method` |
| --- | --- | --- | --- | --- | --- |
| 共享目录 | `--find-shared [--shared-root <根>]` | 站点/内网已预置、大体积、离线优先 | 目录基名==`name`（大小写与 `-`/`_` 不敏感） | `shared_find` | 无（本地） |
| ModelScope（默认） | 缺省，或 `--source modelscope` | CN 可达稳、校验链路成熟、本项目 `OneScience/*` 发布仓；裸名可自动站内检索择优 | 显式 `--repo-id` → 资源卡抽取 → 默认 `OneScience/<name>` → 站内检索打分 | `modelscope_fetch` | `sdk`/`cli`/`git_lfs` |
| HuggingFace | `--source hf --hf-repo <org/name>`（或 `--repo-hint` 给出 `huggingface.co/...` 链接） | 资源权威/最新首发在 HF 官方组织，或已知 ModelScope 镜像缺/旧/不全 | **必须 `org/name`**，HF 无单命名空间默认约定，不给不猜 | `huggingface_fetch` | `hf` |
| 官网直链 | `--source url --source-url <https://…>` | ModelScope/HF/共享都没有，但论文附件/项目官网给出权威直链 | 只允许 http(s)，文件或归档包（`.zip/.tar/.tar.gz/.tgz/.tar.bz2` 自动解包） | `url_fetch` | `url` |

`provider` 字段（`explicit|local|shared|cache|modelscope|huggingface|url`）随结果与注册表返回，标明"这份数据最终是谁给的"。

## 2. 评估维度（决定段3 走哪条）

对每个待取资源，逐条权衡下列维度，再定来源。维度之间无固定权重，按任务实情判断：

1. **权威性与首发**：这个资源的"老家"在哪？很多模型/数据集首发在 HuggingFace 官方组织（如 `facebook/*`、`deepseek-ai/*`、`microsoft/*`，以及大量 `datasets/`）或论文附件/项目官网；ModelScope 上常常是**镜像**。首发源更权威时优先首发源。
2. **时效/最新**：要最新版而 ModelScope 镜像可能滞后 → 走 HF/官网。做基准、复现近期工作尤其要注意。
3. **完整性**：镜像有时只放部分文件或缺配置/权重。若下游要求特定文件而镜像没有 → 换更全的来源，别拿残缺目录凑数。
4. **可达与速度**：国内/内网环境下 ModelScope 与共享目录快且稳；HF、海外官网可能慢或需镜像/代理（`--hf-endpoint`/`HF_ENDPOINT` 指向 `https://hf-mirror.com` 等）。可达性差时优先本地/共享/ModelScope。
5. **许可与门槛**：gated 私有、需 token 或需申请的来源要自备凭据，本技能**不代管凭据**（认证失败只如实报 `authentication_failed`）。无凭据就选公开可得的那条。
6. **体积**：段3 自动来源都受 `--max-repo-bytes` 上限约束（默认 8 GiB，`ONESCIENCE_RESOURCE_MAX_REPO_BYTES` 可改）；直链/仓库超限记 `over_max_bytes`。冒烟/自测用小上限。

## 3. 默认倾向：ModelScope 起步，按需切换

用户诉求与本项目环境共同决定：**同等/无明确信号时默认 ModelScope**（CN 可达、校验链路成熟、是本项目发布仓库、且裸名也能自动检索择优），但"默认"不等于"唯一"或"一定最优"。出现下列**明确信号**之一就切到更合适的来源，不要死守 ModelScope：

- 已知该资源权威/最新首发在 HuggingFace（给了 `huggingface.co` 链接、或就是 HF 官方组织的知名模型/数据集）→ `--source hf`。
- 明确知道 ModelScope 镜像缺失、滞后或不完整，而 HF 有全量最新 → `--source hf`。
- ModelScope 与 HF 都没有，但论文附件/项目官网给出权威直链 → `--source url`。
- 站点共享盘/内网很可能已有（离线、大体积、团队已下过）→ 先 `--find-shared`，命中即免下载。
- 拿不准：先 `search`（只读）或直接 ModelScope 起步；取回后若发现不对（空目录、缺必需文件、版本明显旧），**换来源再来**，全过程记进 `fetch_attempts` 并如实转述。

## 4. 选源必须透明可问责

- 结果里的 `provider`、`repo_id`、`repo_id_source`、`fetch.method` 必须来自脚本真实输出；走过 ModelScope 站内检索还有 `selection`（`chosen`/`score`/`reasons`/`alternatives`/`excluded`）。
- 换来源、降级重试的每一步进 `fetch_attempts`（含各来源与结局）。
- 向用户转述时必须说清"**从哪取的、为什么从这取**"（例如"ModelScope 镜像仅含权重缺配置，改从 HuggingFace 官方 `org/name` 取全量""共享盘 `/public/share/...` 已有副本，直接复用未下载"），不能只丢一个本地路径。

## 5. 放宽来源但不失控（安全边界）

选源放开的是"从哪里取"，不放开工纪律：

- **仍只能通过 `scripts/fetch_resource.py provision`**，不得手写 `wget`/`curl`/`git clone` 绕过缓存/锁/校验/体积上限（强制协议不变）。
- **官网直链只允许 http(s)**，有体积上限，落盘后同样过完整性校验并注册；来源权威性由调用方负责，本技能不因为"是官网"就跳过校验。
- **只允许权威来源**：官方 `org` 的 ModelScope/HuggingFace 仓库、论文附件/项目官网直链、站点声明的共享根。**禁止**从公开搜索引擎、来路不明的网盘/第三方镜像随便抓一个名字相近的仓库顶替——那会把来源不明的数据写进训练链路。
- 任一来源失败都如实分类上报（`repo_not_found`/`network_error`/`authentication_failed`/`empty_payload`/`over_max_bytes`/`invalid_source_link`/`verification_failed` 等），**绝不允许**用占位数据、随机张量或示例文件"凑齐"目录让下游继续。

## 6. 决策示例

- **知名 HF 模型**：任务要用 `facebook/dinov2-base`，其权威首发与最新版在 HuggingFace → `provision --name dinov2_base --kind model --source hf --hf-repo facebook/dinov2-base`（内网慢可加 `--hf-endpoint https://hf-mirror.com`）。
- **ModelScope 缺文件**：先按默认取了 ModelScope 镜像，完整性校验报缺 `config.yml` → 换 `--source hf` 取全量仓库。
- **内网已有**：大体积气象数据团队已放共享盘 `/public/share/onestore/onedatasets` → `provision --name era5_tutorial --kind dataset --find-shared`，命中即免下载（`provider=shared`）。
- **小众数据集只有官网直链**：作者 GitHub release 挂了 `data.tar.gz` → `provision --name exotic_mat --kind dataset --source url --source-url https://github.com/<org>/<repo>/releases/download/v1/data.tar.gz`，脚本下载并自动解包后校验。

四者的共同点：先评估"权威/最新/完整/可达/门槛/体积"，再选来源；来源可换，纪律不变。
