# 任务级资源规划（只给任务、不给资源名时）

本篇是**段 0**的权威流程：当请求里只有一个训练/微调/评测/复现类任务、连数据集名或模型名都没给时，如何在不回问用户的前提下，把任务拆成可检索的资源需求、定位到 ModelScope 上的真实仓库并物化。实现落在 `scripts/fetch_resource.py`（`search` 子命令 + `provision` 的 `--search-query/--task-hint`）与 `scripts/modelscope_hub.py`（`query_variants`/`search_candidates_expanded`/`rank_candidates`）。

核心立场：**对提示词几乎不做要求**。用户只说"训练一个猫狗图像分类器"，本技能负责把它变成"下载哪个仓库、为什么是它"，而不是反问"你要哪个数据集"。回问用户只发生在第 6 节列出的、确实无候选可用的情形。

## 0. 何时走这一篇

- 请求里**没有任何具体资源名 / repo_id / 页面链接**，只有一个任务描述（"训练一个 X 分类器""复现这篇论文的 DFT 结果""给 Y 做微调"）。→ 必须走本篇。
- 请求里有裸资源名但没有组织名（"下载 pets_small"）。→ 不必做完整规划，直接 `provision --name <裸名>`，让第 4 节的站内检索 + 打分自动择优；本篇第 3、4 节仍是它的判据来源。
- 请求里有显式 `repo_id` / `source_dir` / 资源卡链接。→ **不走本篇**，按 `download_workflow.md` 直接物化。

规划产出的是一批 `provision_spec`（每个资源一条），随后每条都走 `download_workflow.md` 的段 1→段 3。

## 1. 从任务反推资源需求

把任务描述拆成"要跑通它，本地必须存在哪些资源"。逐条回答：

1. **要几类资源**：一个训练任务通常至少 1 个 `dataset`；要"复现/评测/推理"往往还要 1 个 `model`（权重）。既要数据又要权重就拆成两条 `provision_spec`，不要合成一条。
2. **各自 `kind`**：判据是**下游怎么消费**（喂训练/推理的是 `model`，喂 datapipe/standardizer 的是 `dataset`），细则见 `repo_id_inference.md` 第 1 节。判不准就先按消费方默认选一个 `kind`，用 `search --kind` 验证该类型下确有候选再定，不回问。
3. **领域与模态**：从任务抽出领域词（图像/文本/分子/材料/气象…）与模态（分类/检测/分割/生成/回归…）。这些词是第 3 节检索词与第 4 节打分的主要输入。
4. **体积上限 `max_repo_bytes`**：按"够跑通任务即可"估一个上界，避免一句话任务拉下几百 GB。冒烟/自测/示例级任务给到 MB 量级（如 `5000000`）；正式训练可放宽。缺省上限 8 GiB（`ONESCIENCE_RESOURCE_MAX_REPO_BYTES` 可改）。显式 `--repo-id` 不受此限。
5. **必需文件 `required_files` / `min_bytes`**：能预判就填（如图像数据集常有 `*.jpg`/`*.png`、分子数据常有 `*.xyz`/`*.extxyz`），交给段 3 后的完整性校验；预判不了就留空，只用"至少一个可见文件"兜底。

## 2. 派生稳定的英文安全逻辑名

`name` 同时是缓存目录名与注册表键，必须是单段安全名 `^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$`（`repo_id_inference.md` 第 2 节）。任务里往往没有现成英文名，按下面规则**自行派生**，不要为了一个名字回问用户：

- 用任务的**领域 + 模态/用途**拼一个小写下划线名：猫狗图像分类 → `catdog_clf`；藏红花基因数据 → `saffron_genome`；CO₂ 吸附 MOF 数据 → `co2_mof_adsorption`。
- 只用 `[a-z0-9_]`，不带组织名、不带路径分隔符、不带中文。名字不必等于最终仓库名——它只决定缓存落点，真正的 `repo_id` 由第 4 节检索择优决定。
- 中文/任务原文不要丢：放进 `--search-query` 与 `--task-hint`，它们才是检索与打分的输入。
- 派生名写入注册表时在 `limitations` 注明"逻辑名由任务描述派生"，保证可追溯。

## 3. 构造检索词（关键：端点是子串匹配）

ModelScope 官方检索端点 `GET /{datasets|models}?search=<q>` 是**子串匹配**，不是分词搜索引擎：**一长句中文几乎必然 0 命中**。所以：

- **检索词要短**：单个 2–6 字中文词（"宠物""猫狗""分子""气象"）或单个英文词（`pets`、`cifar`、`imagenet`），不要塞整句。
- **给多个同义/上位词**：`--search-query` / `search --query` 可重复传，脚本会把 `name` 与所有 `--search-query` 合并成多组查询分别打，命中面更宽。
- **`--task-hint` 照抄任务原文**：它不参与"命中"，只参与第 4 节的语义打分（标题/描述与任务词的重合度），所以可以写整句。
- **整句 0 命中会自动拆词重试**：脚本在整句无命中时按空白与标点（`query_variants`）自动拆词，最多 6 次查询，**首个有结果的变体即停**；实际发出的每次查询记在结果的 `queries_tried` / `search_trace` 里，透明可查。你只管给合理的短词，拆词兜底交给脚本。

先用只读的 `search` 预览候选与打分，确认方向对了再 `provision` 物化：

```bash
python3 scripts/fetch_resource.py search \
  --query "<短词1>" --query "<短词2>" --kind dataset|model \
  [--task-hint "<任务原文整句>"] [--top 8] [--max-repo-bytes <N>] [--output cands.json]
```

`search` 只读、不写缓存、不下载，可反复调词。

## 4. 读打分并选定

`search` 与 `provision` 自动模式都用同一套打分（`modelscope_hub.rank_candidates`），权重从高到低（细则与破平规则见 `repo_id_inference.md` 第 4 节第 3 步）：

> 逐字同名 1000 ＞ 名称互为前缀/包含 400 ＞ 标题描述与请求词共同词 80×n（≤240）＞ 与任务描述共同词 40×n（≤240）＞ 任务标签命中 60×n（≤180）＞ 下载量 100×log10(1+downloads)（≤400）＞ 可信机构命名空间 150 ＞ likes（≤50）＞ 体积在上限内越小越优先 150×(1−size/max)。

每个候选都带 `score` 与中文 `reasons`。选定原则：

1. **默认交给脚本自动选**：`provision` 自动模式取分数最高的候选，不需要人工挑。要"绝不代作选择"才加 `--strict-name`（此时多个逐字同名 → `repo_ambiguous` + `details.candidates`）。
2. **看懂 `reasons` 再转述**：转述给用户时必须带上选中的 `repo_id` 与主要 `reasons`（"逐字同名""下载量最高""命中任务标签 image-classification"），这是自动择优唯一的问责凭证，不能只报一个本地路径。
3. **`excluded` 是硬排除**：`gated`/`private`/`login_required` 的仓库默认不进择优（要放开加 `--allow-gated` 并配好凭据）；体积超 `--max-repo-bytes` 记 `excluded=over_max_bytes`。候选都被排除 → `no_selectable_repo`（见第 6 节），不要退而抓一个来源不明的镜像。
4. **可信命名空间优先不是绝对**：`modelscope`/`iic`/`damo`/`qwen` 等在同等条件下排在个人镜像前，但逐字同名与下载量权重更高——真出现"官方小号 vs 个人高热度同名"时以打分结果为准，`reasons` 会说明。
5. **别用近似名硬凑**：打分低（只有名称包含、没有语义/热度支撑）且任务并不急时，宁可换更准的检索词再搜一轮，也不要选一个明显跑偏的仓库。

## 5. 物化与换候选

选定方向后直接让 `provision` 自动择优物化（它内部就是"按分数取前 `--candidate-attempts` 个候选依次尝试"）：

```bash
python3 scripts/fetch_resource.py provision --name <派生安全名> --kind dataset|model \
  --search-query "<短词>" [--search-query "<同义词>"] --task-hint "<任务原文>" \
  [--max-repo-bytes <N>] [--candidate-attempts 3] [--allow-gated] [--strict-name] \
  [--output prov.json]
```

- **逐候选降级重试**：某个候选下载失败（`repo_not_found`/`network_error`/`authentication_failed`/`empty_payload`/`checksum_mismatch`/`fetch_failed`）或落盘后完整性校验不过，脚本自动换下一个候选，全过程记进 `fetch_attempts`（每条含 `repo_id`/`repo_id_source`/`outcome`/`files`/`bytes`）。
- **`repo_id_source` 标记来源**：逐字同名命中记 `name_search`，靠语义/热度/命名空间/体积择优命中记 `name_search_ranked`；两者都会在 `warnings` 里写明"默认仓库不存在，按检索择优改用 X"。
- **结果读 `--output`**：优先解析 `--output` 落盘的 JSON，拿到 `local_path`、`selection`、`fetch_attempts`、`status`。`status=success` 且校验通过才算数。

## 6. 何时才允许说"拿不到"

只有以下情形才如实上报失败，且**必须说清缺什么**，不得凭空捏仓库名、不得用占位/空数据顶替让下游继续：

| 情形 | reason | 上报要点 |
| --- | --- | --- |
| 规划 + 两轮检索（含自动拆词）都拿不到任何候选 | `resource_plan_empty` | 说明任务里还缺哪一项信息（领域 / 模态 / 任务类型），请调用方补一个更具体的检索词或资源名 |
| 有候选但全部需凭据或超体积上限 | `no_selectable_repo` | 列 `details.candidates` 与排除原因；出路是配凭据 + `--allow-gated`、放宽 `--max-repo-bytes`、或显式 `--repo-id` |
| 候选逐个试完仍取不到 / 校验不过 | 最后一个候选的权威 reason | 带 `fetch_attempts` 全过程；不要把"检索没搜到"当失败原因，也不要把可重试网络故障写成 `repo_not_found` |

"两轮检索"指：先用规划派生的短词搜一轮，无果则换更短/更上位或英文同义词再搜一轮（脚本内部的自动拆词已算兜底）。两轮都空才允许报 `resource_plan_empty`。

## 7. 完整示例：只给"训练一个猫狗图像分类器"

用户只说任务，没给任何数据名。规划与执行：

1. **反推需求**：跑通分类训练至少需要 1 个图像分类 `dataset`；本例只做数据准备，暂不拉预训练权重。领域=图像/宠物，模态=分类。冒烟体积上限给 `5000000`（约 5 MB）。
2. **派生名**：`catdog_clf`。
3. **只读预览候选**（整句 0 命中，脚本自动拆词到"宠物"命中）：

   ```bash
   python3 scripts/fetch_resource.py search \
     --query "宠物 猫狗 图像分类数据集" --kind dataset \
     --task-hint "训练一个猫狗图像分类器" --top 8
   ```

   结果 `queries_tried` 显示整句 0 命中、`"宠物"` 命中 4 条，top1 = `modelscope/pets_small`（`score≈984`，`reasons` 含逐字/名称重合与下载量）。
4. **任务级物化**（自动择优，直接落盘）：

   ```bash
   python3 scripts/fetch_resource.py provision --name catdog_clf --kind dataset \
     --search-query "猫狗 图像分类" --task-hint "训练一个猫狗图像分类器" \
     --max-repo-bytes 5000000
   ```

   `status=success`，自动选中 `modelscope/pets_small`（`repo_id_source=name_search_ranked`，`score≈784`），落盘 2 files / 1141 bytes，完整性校验 `passed=true`；`selection.reasons` 与 `fetch_attempts` 一并带回。
5. **转述给用户**：报"已为猫狗分类任务从 ModelScope 选定并下载 `modelscope/pets_small`（依据：名称与任务语义重合 + 下载量），本地路径 `<...>/datasets/catdog_clf/raw`，2 个文件、校验通过"，而不是只丢一个路径。

整个过程没有回问用户一次，也没有要求用户给出组织名或 repo_id——这正是本篇要保证的能力。
