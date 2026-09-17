# Task-Centric 知识卡契约（9 字段 + tags 边）

> 本文件替代原 `knowledge/schemas/*.yaml`。TC 知识一律以 **`metadata.json` + `knowledge.md`** 文档组落地，
> 路径遵循既有三层约定 `<domain>/<category>/<primitive>/`，**不新增 metadata 字段、不改字段名**，
> 保证 catalog_search 逻辑不变。

## 1. metadata.json 的 9 个字段（不可增减、不可改名）

| 字段 | 用途 | TC 约定 |
|---|---|---|
| `name` | primitive-id | kebab-case，全局唯一，等于所在目录名；**必须能看出卡片讲什么**（哈希 id、纯编号、裸 `card`/`task` 一律不合格，见 §2c） |
| `type` | 卡片种类 | `task` / `workflow` / `scenario` / `model` / `tool` / `dataset` / `datapipes` / `components` / `application` / `visualization` / `databases` / `workflow-planning` / `contracts` / `output-format` |
| `domain` | 领域 | 用**目录名**：`bio` / `cfd` / `climate` / `general` / `matchem`（语义领域写进 description 与 tags） |
| `version` | 版本 | semver，演进时递增 |
| `visibility` | 可见性 | `public` |
| `created_at` | 创建日 | `YYYY-MM-DD` |
| `updated_at` | 更新日 | `YYYY-MM-DD` |
| `description` | 描述 | 一段中文 prose，须含：任务目标、关键实体、连接关系的人读说明 |
| `tags` | 标签 | **承载知识图全部边**（见下），另含语义领域词与检索关键词 |

## 2. tags 承载的知识图边（命名空间约定）

所有连接关系写进 `tags`，前缀区分语义。catalog_search 可命中文本，文件系统可 grep，**无需新字段**。

| tag 前缀 | 含义 | 示例 | 解析规则 |
|---|---|---|---|
| `edge:task:<name>` | 指向 Task 卡（workflow/scenario 用） | `edge:task:material-property-prediction` | 同 domain 的 `tasks/<name>/` |
| `edge:workflow:<name>` | 指向 Workflow 卡（scenario 用） | `edge:workflow:material-screening-workflow` | 同 domain 的 `workflow/<name>/`（type=workflow） |
| `edge:resource:<category>/<name>` | 指向资源卡（Task 用） | `edge:resource:models/mace` | 同 domain 的 `<category>/<name>/`，**必须解析到真实卡** |
| `edge:method:<vocab>` | 方法路线（词表，非卡片） | `edge:method:machine-learning-potential` | 方法说明写在 knowledge.md「方法路线」节 |
| `edge:operation:<vocab>` | 操作动词（词表） | `edge:operation:run-inference` | 操作说明写在 knowledge.md「操作序列」节 |
| `edge:validation:<vocab>` | 验证契约（词表） | `edge:validation:prediction-accuracy` | 验证说明写在 knowledge.md「验证契约」节 |
| `edge:next:<task>` / `edge:prev:<task>` | Task Graph 前后置 | `edge:next:candidate-ranking` | 同 domain `tasks/<name>/` |
| `edge:step:<step_id>:<task>` | Workflow 卡里源场景步骤与 Task 的映射 | `edge:step:s01:data-target-definition` | 第 3 段必须解析到同 domain `tasks/<name>/` |
| `edge:fallback_method:<vocab>` | 前提不满足时的改道方法 | `edge:fallback_method:density-functional-theory` | 改道条件写在 knowledge.md「缺口与降级」节 |
| `edge:scenario:<name>` | 指向 Scenario 卡（legacy `workflow-planning` 卡跨系接线用） | `edge:scenario:matchem-2d-perovskite-lab-ml-synthesis-scenario` | 同 domain 的 `scenario/<name>/`；命中 legacy 卡后必须沿此边反查 Scenario 卡并完整展开 |
| `edge:alias:<name>` | 同一场景两张 Scenario 卡（语义卡 ↔ 图谱卡）互指 | `edge:alias:matchem-mof-mechanical-stability-machine-learning-prediction-scenario` | 同 domain 的 `scenario/<name>/`；两条谱系都要展开，互为别名而非替代 |
| `slot:<slot_name>:<value>` | 实体槽取值 | `slot:adsorbate:CO2` | 槽定义写在 knowledge.md「实体槽」节 |
| `atom:<atom_id>` | 指向 `references/tc/atoms.jsonl` 的原子事实 | `atom:atom_mpp_mace_mae_energy` | 数值级召回时 grep atoms.jsonl；**id 必须真实存在** |
| `runnable` | 裸标签：该卡所在任务/资源可执行落地 | `runnable` | 仅作检索关键词，不校验 |
| `runnable:script` | **本卡自带**可执行脚本（E2E 可跑） | `runnable:script` | 卡目录下必须有 `script/*.py` |
| `src:scenario_id:<id>` | 场景卡溯源到 `scenario_catalogs/` 的原始 JSON | `src:scenario_id:MOF结构力学稳定性机器学习预测` | 不参与边解析，只用于回查源需求书 |
| `src:catalog:<path>` / `src:paper:<id>` / `src:workflow_steps:<n>` | 源目录、关联论文、源步骤数 | `src:catalog:scenario_catalogs/materials` | 不参与边解析 |
| `src:scenario_family:<name>` / `src:scenarios_count:<n>` | 骨架族名与归并了多少个场景 | `src:scenarios_count:21` | 不参与边解析，是泛化率的账本 |
| `src:step:<step_id>` | Task 卡反查它在源场景里是第几步 | `src:step:s01` | 应与所属 Workflow 的 `edge:step` 一致 |

**硬约束**
- `edge:resource:*` 与 `edge:task:*`、`edge:workflow:*`、`edge:next/prev:*`、`edge:scenario:*`、`edge:alias:*` 必须解析到真实卡目录，否则视为悬空边（validator 报错）。
- `references/tc/scenario_task_index.json` 是由卡片 metadata 机械生成的**确定性检索索引**（scenario→workflow→tasks→resources 全链），检索协议要求先查索引再走关键词路径；卡片边发生变更后必须重新生成，禁止手改索引内容。
- `edge:method/operation/validation/fallback_method:*` 是词表边，允许无对应卡（本轮 Method/Operation/Validation 不单独建卡，知识内嵌在 Task 卡的 knowledge.md 中）。
- `atom:*` 必须能在 `references/tc/atoms.jsonl` 中查到，悬空 atom 引用按错误处理。
- **`runnable:script` 只允许出现在自带 `script/` 目录的卡上**（通常是 `tools/` 资源卡）。Task 卡表达「可执行」用裸 `runnable` + `edge:resource:<category>/<tool>`，由资源卡承载脚本；这样脚本只有一份，不会出现两处路径漂移。
- **`src:*` 是溯源标签，不是边**：不参与卡目录解析，也不得用它替代 `edge:*`。它的唯一作用是把卡片回连到 `scenario_catalogs/` 的原始场景 JSON、步骤与关联论文，以及记录一张骨架卡归并了多少个场景（`src:scenarios_count`）。

## 2b. 场景 → Task 的泛化规则（从 scenario_catalogs 转卡时遵守）

场景 JSON 的 `workflow[]` 不是一步一张卡，而是先归并再建卡：

| 源字段 | 归并判据 | 落到卡的位置 |
|---|---|---|
| `workflow[i].step_name` | 字面完全相同且位于同一步序 | 合并为同一张 Task 骨架卡的 `name`（中文步骤名须先译成英文 kebab 短名，见 §2c） |
| `workflow[i].step_input[].var` | 变量集合相同 | Task 卡的 `slot:<key>:<value>`（变量名 → 槽名，取值域 → 槽值） |
| `workflow[i].quality_gate[]` | 门禁原文相同 | Task 卡的 `edge:validation:<vocab>` + knowledge.md「验证契约」节 |
| `workflow[i].outputs[]` | — | Task 卡 knowledge.md「输入输出契约」节 |
| `workflow[i].depend_step_id` | — | `edge:prev:*` / `edge:next:*` 与 Workflow 卡的 `edge:step:*` |
| `scenario_id` / `related_papers` | 每个场景唯一 | **Scenario 卡**（一场景一卡），不进 Task 卡 |
| 共享同一套骨架的场景群 | 步骤名/变量/门禁全同 | **Workflow 骨架卡**（一族一卡），用 `src:scenarios_count` 记归并数 |

硬规则：
- **禁止 1:1 直出**。若 N 个场景的某一步在 step_name + var 集合 + quality_gate 上完全一致，必须归并为 1 张 Task 卡，N 写进所属 Workflow 卡的 `src:scenarios_count`。
- 场景差异只能落在槽取值上；如果差异大到必须改门禁或改操作序列，那它是另一个骨架族，开新卡而不是往现卡里塞条件分支。
- Task 骨架卡不得写死具体场景名；具体场景名只出现在 Scenario 卡的 `src:scenario_id`。

## 2c. 卡夹命名硬门禁（全领域、全知识类型，无例外）

目录名是知识库的检索入口：catalog_search 与人工定位先看到的就是这一串字。它不是内部 id，
不得用任何只对生成器有意义的写法。

| 禁止形态 | 反例 | 为什么不行 | 正例 |
|---|---|---|---|
| 哈希 id | `it-01684b6f`、`tk-bio-9a8b7c6d`、`gap-a1b2c3d4` | 零信息 | `matchem-mof-mechanical-stability-ml-prediction` |
| 裸占位词 | `card`、`task`、`workflow`、`component` | 全库同名，互相覆盖 | `cfd-batch-inference-physics-3d-turbulence-transformer-inst` |
| 编号骨架 | `cfd-s001-workflow`、`b03-task` | 看不出讲什么 | `cnn-airfoil-steady-flow-surrogate` |
| 中文/空格名 | `翼型阻力预测`、`my card` | 路径不可移植 | `3d-turbulence-transformer-multiscale-prediction` |

四条约束：

1. **中文源字段先译再当名**。`step_name`、场景中文名、论文中文标题不得直接拿作目录名（旧生成器把中文剔成 ASCII 后整串塌空，兜底成裸名 `card`，多卡互覆）。中文名写在 `knowledge.md` 一级标题与 `description` 里。
2. **防撞名靠补词，不靠编号**。名字已占用就再加一个主题词（方法/对象/交付物），不得退化成 `-s001` 或 `-<哈希>`。
3. **编号与年份本身不是病**。`global-canopy-height-map-2020`（年份）、`co2-cu111-slab`（Miller 指数）、`oc20`（数据集正式简称）都是合法名；只有当整名除编号、领域码和结构词外**再没别的字**时才拦。
4. **入库前自检**：`python validate_knowledge.py --names-only --quiet` 必须 `RESULT: PASS`（CI 同一道门禁，哈希/裸名/编号骨架直接阻断 PR）。

## 3. knowledge.md 章节骨架（Task 卡）

```
# <中文名> (<name>)
## 任务目标
## 适用范围 / 不适用场景
## 实体槽（Entity Slots）
## 输入输出契约
## 方法路线（可替换）
## 操作序列（Operations）
## 验证契约（Validations）
## 资源引用（Resources）
## 前后置任务（Task Graph）
## 缺口与降级（Fallback / Gap）
```

Workflow / Scenario 卡用精简骨架：`## 目标`、`## 任务编排（Task Graph）`、`## 适用场景`、`## 缺口与降级`。

## 4. 目录结构（scenario / workflow / tasks 与资源 category 全部平级，无嵌套）

```
assets/<domain>/
  scenario/             ← Scenario 卡（type=scenario），一场景一卡，edge:workflow 向下连
  workflow/             ← Workflow 骨架卡（type=workflow），一族一卡，edge:task / edge:step 向下连
  tasks/                ← Task 卡（type=task）
  models/ tools/ datasets/ datapipes/ components/
  application/ visualization/ databases/ output-format/
  workflow-planning/    ← 既有实例卡（legacy，type=workflow-planning），不再存 TC 卡
```

`scenario` / `workflow` / `tasks` 与其余资源 category **全部同级**；不存在 `tasks/resources/` 这种嵌套。TC 三层各占一个目录，**目录名即层名、与卡 `type` 一一对应**（validator 强校）；legacy 实例卡留在 `workflow-planning/`，与 TC 层物理隔离。

## 5. 辅助索引（skill 内，不进 assets 域树）

| 文件 | 用途 |
|---|---|
| `references/tc/atoms.jsonl` | 原子事实（数值级召回），每行一个 JSON，靠 `atom:<id>` tag 回链卡片 |
| `references/tc/knowledge_evolution_log.jsonl` | 知识演进日志（预留双向反馈闭环） |

> 缺口记录**不在本目录**：它是运行期写入，落工作区状态目录 `.onescience/gaps.jsonl`（`retrieval_level != full` 或门禁命中时追加）。技能树是只读知识区，不得放任何运行期可写文件，否则单次会话就会改变知识库指纹（seta3 实测撞上：`references/tc/gaps.jsonl` 跑测中被追加 923→2479 字节，导致三臂单变量前提失效）。

## 6. 存量（legacy）卡与 TC 卡的共存

- 存量 711 张卡的 9 个契约字段 **100% 齐备**，但部分批次带有额外字段（`scenario_id`/`source_papers` 410 张、`provider_kind`/`capabilities`/`contracts` 等 66 张），这些字段 catalog_search 不参与匹配，属历史遗留，TC 卡**不得模仿**。
- 存量卡 `domain` 主流用目录名（`matchem` 123 / `materials` 21、`bio` 121 / `biology` 91、`climate` 109 / `weather` 38）。TC 卡统一用**目录名**，与主流一致，避免 catalog 按 domain 过滤时分裂召回。
- 存量 `type` 存在词表外取值（`component` / `module` / `datapipe` 等）。TC 卡只用 `task` / `workflow` / `scenario` / `model` / `tool` / `dataset` 等已收录值。
- `type=workflow-planning` 的实例卡是 legacy 编排证据，**不是** TC 的 Scenario/Workflow 层；TC 的 scenario/workflow 卡已分居 `scenario/` 与 `workflow/` 独立 category，与 legacy 物理隔离，TC 检索时**按 category 目录锁层**（再用 type 复核），legacy 只作补充且须标 `legacy_instance: true`。
- 校验：仓库根 `validate_knowledge.py` 默认只严格校验 TC 卡；`--all` 会把存量卡的偏离降级为 WARN，用于体检而非阻断。
