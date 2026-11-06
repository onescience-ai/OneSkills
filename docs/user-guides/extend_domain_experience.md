# 新增领域技能：开发、提交、安装与验证

## 1. 先确定新增能力的接入点

根据能力性质选择接入方式：

| 新增内容 | 推荐方式 | 对外结果 |
| --- | --- | --- |
| 模型、数据、组件、领域知识、使用说明、工作流经验 | 优先在 `onescience-primitives/assets/` 新增 primitive | 通过资源技能返回 `resource_retrieval_result` |
| 具有独立检索规则、权限、provider 或生命周期的资源库 | 新增 `type=resource` 技能 | `resource_retrieval_result` |
| 对任务中某个功能、阶段或方面进行规划，确定处理方案、步骤和依赖 | 新增或扩展 `type=expert` 技能 | `planner_proposal` |
| 实际执行具体任务或操作，按任务约定返回结果内容、生成文件，或同时提供两者 | 新增或扩展 `type=executor` 技能 | `execution_result`，包含结果内容及文件引用（如有） |

expert 为所分配的任务部分制定方案，由 orchestrator 融合各部分规划并调度执行；expert 不直接执行所规划的操作。

executor 负责执行具体任务，按任务要求和技能契约直接返回内容、保存产物并返回文件引用，或同时提供两者。直接返回的结果应明确字段和数据格式，供调用方或其他技能使用；需要落盘的代码、数据、模型、报告等产物，应保存到约定位置。

确定接入方式时，应复用 coder、runtime、installer 已覆盖的通用能力，避免新增职责重复的技能。

如果只新增 primitive，通常不需要新增 `SKILL.md`。按现有目录约定放置：

```text
skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/
  metadata.json
  spec.md
  usage.md
  workflow_planning.md
```

以上文件分别描述用于召回的身份与来源信息、规格契约、使用方法和规划知识。领域目录沿用仓库实际命名，例如 `bio`、`climate`、`cfd`、`matchem`，不要另建同义目录。primitive 的 `metadata.json` 和技能的 YAML frontmatter 是两套元信息，不能互相替代。

## 2. 编写新技能及完整 frontmatter

新增技能的名称必须以 `onescience-` 为前缀。在 `skills/<skill-name>/` 中编写 `SKILL.md`，其他目录按需添加：

```text
skills/onescience-spectrum-qc/
  SKILL.md
  references/    # 按需读取的契约与领域细则
  scripts/       # 可重复执行的确定性操作
  assets/        # 确有需要的资源或模板
```

### 当前必需的元信息

YAML 顶层必须同时声明 `name`、`description`、`type`、`capabilities`。不要把 `type` 或 `capabilities` 只写在正文或嵌入另一个 `metadata` 字段。

下面是 executor 示例；职责、输入输出和检索词应根据实际技能填写：

```yaml
---
name: onescience-spectrum-qc
description: 按用户给定的规则校验光谱 CSV 的坐标和信号列，返回检查结果，并按任务要求生成质量报告文件；用于光谱数据质量检查，不负责模型训练或环境安装。
type: executor
capabilities:
  owns:
    - 光谱文件契约检查
    - 按用户规则执行光谱质量检查
    - 检查结果整理与返回
    - 按任务要求保存质量报告
  not_owns:
    - 模型训练
    - 环境安装
    - 作业提交
  inputs:
    - step_handoff
    - spectrum_files
    - validation_rules
  outputs:
    - execution_result
    - validation_result
    - quality_report
  downstream: []
  prereq:
    - 输入文件可访问
    - 已提供需要执行的质量规则
  intent_aspects:
    - spectral_quality_control
  operation_types:
    - validate
  artifact_types:
    - report
  domains:
    - materials
  trigger_keywords:
    - 光谱质量检查
    - 光谱CSV校验
---
```

| 字段 | 填写要求与用途 |
| --- | --- |
| `name` | 非空、唯一，必须以 `onescience-` 开头，使用小写字母、数字和连字符，建议与目录名一致 |
| `description` | 准确说明做什么、何时使用、返回什么；帮助初筛，避免吸引无关任务 |
| `type` | 新增领域技能通常选 `resource`、`expert` 或 `executor`；`orchestrator` 是已有编排入口 |
| `capabilities.owns` | 明确负责的原子动作，用于职责划分与执行器选择 |
| `capabilities.not_owns` | 明确不负责的动作，防止与其他技能抢占职责 |
| `capabilities.inputs` / `outputs` | 接收与返回的内容，包括技能间传递的数据、规划、状态或文件，须与正文及实际回执一致 |
| `capabilities.downstream` | 本技能可按明确委托合同调用的下游技能；无委托则 `[]` |
| `capabilities.prereq` | 真正需要的前置条件；不要把可自动获取的公共依赖写成必须由用户提供 |
| `capabilities.intent_aspects` | 语义明确的意图方面；expert 召回的重要依据 |
| `capabilities.operation_types` | 覆盖的操作，例如 create、run、validate；与实际能力一致 |
| `capabilities.artifact_types` | 涉及的产物类别，例如 code、dataset、report；不生成此类产物时可为 `[]`，返回内容仍通过 `outputs` 声明 |
| `capabilities.domains` | 领域范围，优先与已有技能的领域语义保持一致 |
| `capabilities.trigger_keywords` | 有区分度的触发词，不要堆砌无关领域词 |

`capabilities` 上述 **11 个子字段都必须存在，值均为字符串列表**，允许明确使用 `[]`。不要使用逗号分隔的字符串、空值或嵌套对象代替列表。声明的能力必须有正文流程和实际实现支撑；不能为了被召回而扩大职责。

### 正文与输入输出契约

正文应写清适用场景、输入获取方式、执行或规划步骤、结果返回方式、失败条件和验证方式；涉及文件时，说明文件格式和保存位置。详细规则放入 `references/`，并注明读取时机；脚本依赖、运行命令和必要环境单独说明。

按类型对齐当前公共契约：

- **resource**：接收 `resource_retrieval_request`，返回 `resource_retrieval_result`，包括检索层级、`knowledge_gap`、匹配资源及其 `content`、限制和来源。调用方消费返回内容，`path` 只是标识，不授权绕过资源技能读取 `assets/`。
- **expert**：接收意图、分配的任务部分、资源摘要和可用执行器元信息，针对该部分返回 `planner_proposal`，说明处理方案、步骤、依赖、所需资源、预期结果、验收条件及 fallback，交由 orchestrator 融合和调度。
- **executor**：接收 `step_handoff`，实际执行交接的具体任务。按约定直接返回结果内容、生成落盘产物，或同时完成两者，并通过 `execution_result` 交回执行状态、结果内容和文件引用。下游技能可消费返回内容，也可按交接契约使用已生成的文件。请求、技能加载和交接只是中间状态，不能输出一段请求后就结束任务。

以下 executor 回执同时返回检查结果和已落盘的报告引用：

```yaml
execution_result:
  skill: onescience-spectrum-qc
  attempt: 1
  status: success
  failure_category: null
  result_identity: not_a_result
  result_identity_basis: 返回数据契约检查结果，不包含科研结论
  artifacts:
    - path: /absolute/task/output/quality_report.json
      description: 已保存的逐文件光谱质量检查报告
  observation:
    summary: 已完成检查，返回检查结果并保存质量报告
    completed:
      - 光谱文件契约检查
      - 质量报告保存
    validation_result:
      valid: true
      issues: []
    missing: []
    risks: []
    next_recommendation: 按用户授权进入后续步骤
  events: []
```

`observation.validation_result` 承载可直接使用的检查结果，`artifacts` 登记已落盘的报告。只要求返回内容时，`artifacts` 可为 `[]`；要求生成文件时，必须确认文件已保存并返回准确路径，供调用方或后续技能使用。完成范围以 `step_handoff` 为准，结果身份按实际证据填写；失败或部分完成时，说明具体原因和缺失项。数值验收条件应来自用户要求或明确的领域依据。

详细契约以这些文件为准：

- [资源契约](../../skills/onescience-orchestrator/references/resource_contract.md)
- [专家规划契约](../../skills/onescience-orchestrator/references/planner_contract.md)
- [执行交接契约](../../skills/onescience-orchestrator/references/execution_handoff_contract.md)
- [文件交接契约](../../skills/onescience-orchestrator/references/file_handoff_contract.md)

## 3. 本地校验元信息与实现

编写完成后，使用 orchestrator 的 Python 脚本直接读取并校验 frontmatter，**不依赖宿主智能体的技能元信息接口**。确认所用 Python 环境已安装 PyYAML，再在仓库根目录运行：

```bash
mkdir -p artifacts/new-skill
python skills/onescience-orchestrator/scripts/discover_skill_metadata.py \
  --skills-root skills \
  > artifacts/new-skill/metadata-source.json
```

检查命令退出码为 `0`，JSON 中 `inventory_complete=true`、`errors=[]`，且 `skills` 中包含新增技能及完整能力声明。脚本也检查同一根目录下其他技能；`--type executor` 仅过滤输出，不缩小完整性检查范围。字段缺失、重复名称或损坏 YAML 必须定位解决，不能因为输出文件存在就认为校验成功。

元信息校验通过后，还需按技能职责验证实际操作、返回内容、接口和失败路径，涉及文件时检查文件，并记录结果。通用技能校验器可能不接受本仓库扩展的顶层 `type/capabilities`，不要为通过这类校验而删除当前编排依赖的字段。

## 4. 将新增技能与已有技能提交到独立开发分支

目标项目：<http://218.90.133.98:8929/sugonhpc/onescience/oneskills-dev>。

在目标仓库中从 `master` 创建独立开发分支，保留已有技能，提交新增技能及对已有技能的配套修改，使该分支中的 `skills/` 构成完整、版本一致的技能体系。后续安装、测试与优化均基于该开发分支，通过后再合并到 `master`。

提交前，检查新增技能、已有技能及配套的 `references/`、`scripts/`、`assets/` 等文件是否完整。若修改了技能目录之外的配置或文档，应明确添加相应路径，避免提交无关文件、测试数据、模型权重或凭据。

记录开发分支名和提交 SHA，供后续下载、安装与测试时核对版本。

## 5. 下载开发分支中的技能，安装到执行任务的智能体目录

在实际执行任务的机器上，从 GitLab 下载该开发分支中的完整技能，并安装到目标智能体实际使用的技能目录。按执行环境确认安装位置：

| 执行环境 | 安装位置或检查方法 |
| --- | --- |
| 本仓库当前 Codex 测试环境 | 项目 `.codex/skills/`；其他部署按实际原生配置或插件安装位置确定 |
| onescience-bench 的 Codex Worker | 检查适配器使用的 Codex 配置根目录；当前适配器会从配置根目录的 `skills/` 复制挂载关系到隔离运行时，常见源目录为 `~/.codex/skills/` |
| OpenCode | 常见为 `~/.config/opencode/skills/`；设置了 `OPENCODE_CONFIG_DIR` 时检查其 `skills/`，或检查插件/`skills.paths` 的实际来源 |
| 其他智能体或插件安装 | 按其安装说明确认实际发现目录和依赖挂载，不凭目录名猜测 |

## 6. 根据目标选择测试方式

### 6.1 只测试新增技能的功能

安装后，若只验证新增技能的功能，**在测试提示词中明确指定使用该技能**，直接进入该技能，无需通过 orchestrator 自动召回。

示例提示词：

```text
请使用 onescience-spectrum-qc 技能执行以下任务。

任务：检查 /absolute/test/input/ 下的光谱 CSV。
输入契约：第一列是波数，第二列是信号值，具体单位见输入说明。
检查规则：采用随输入提供的 validation_rules.json，报告缺失列、非有限值和坐标顺序问题。
结果：通过 execution_result 返回逐文件检查结果，供后续技能使用；同时将质量报告保存为 /absolute/test/output/quality_report.json，并返回文件引用。
验收：返回结果和报告文件均与预先准备的异常样本清单一致；合法样本应通过；失败项说明文件及原因。

本次只测试该技能的目标功能，不测试 orchestrator 的自动召回与整套计划融合。
允许使用本技能声明的必要依赖，测试输入、返回结果和执行日志由测试调用方记录到 /absolute/test/output/。
```

单技能测试仍可使用该技能所需的资源检索、环境验证或明确声明的下游委托。根据技能类型确定验收重点：

| 技能类型 | 功能测试重点 |
| --- | --- |
| resource | 能否返回正确资源及请求深度的内容，来源、限制和知识缺口判断是否准确 |
| expert | proposal 是否完成分配的任务部分的规划，方案、步骤、依赖及交接信息是否可用 |
| executor | 是否实际完成具体任务；按任务契约检查返回内容、落盘文件或两者，以及接口、数据格式、错误行为和约定指标 |

准备有明确预期的正常与异常样本，按任务约定验收：直接返回内容时，验证字段、数据语义和调用方能否正确消费；要求落盘时，验证文件是否存在、内容和格式是否正确；同时要求返回内容与文件时，两者都要检查，并核对一致性。结果供后续技能使用时，进一步验证内容或文件交接是否可用。科研指标使用对应真实数据与评价协议，工程接口验证与科研效果验证分别记录。

### 6.2 测试整个技能体系中的协作

需要进一步验证自动召回、规划融合和执行交接时，另开测试任务，从 `onescience-orchestrator` 入口提出真实用户目标，**不点名要求调用新增技能**，检查其是否按元信息和任务需求被正确选中。

检查完整链路：资源结果是否进入意图识别；专家是否为分配的任务部分返回可融合的 proposal；新增 executor 是否按职责被调度；handoff 是否传递完整输入和用户约束；返回内容是否被调用方或后续技能正确使用；执行结果是否更新 Task State 并驱动后续步骤；最终结果与约定指标是否满足要求。

只出现在技能清单中，不等于已被调用；只被调用，也不等于改善了任务效果。分别记录“是否召回/调度”“是否正确执行”“最终任务是否达标”。保留提示词、智能体及模型版本、技能提交 SHA、元信息发现结果、Task State、handoff、正式回执、运行日志和产物。

比较新增前后的效果时，尽量固定任务、模型、数据、运行环境、资源预算和验收协议。单技能功能测试通过与协作测试通过应分别报告，不能互相替代。

## 7. 使用 onescience-bench 评测已有用例

如果新增能力可以覆盖 onescience-bench 的已有评测任务，按评测仓库 `README.md` 进行定量评测。文件名、参数和支持的智能体以当前检出版本为准。

### 选择匹配的任务与 Profile

| 任务类型 | Profile | 默认数据集 |
| --- | --- | --- |
| 推理 | `eval_profiles/onescience_infer.json` | `benchmarks/datasets/infer` |
| 训练实现 | `eval_profiles/onescience_train.json` | `benchmarks/datasets/train` |
| 论文复现 | `eval_profiles/onescience_paper_repro.json` | `benchmarks/datasets/paper_repro` |
| 二次开发 | `eval_profiles/onescience_sec_develop.json` | `benchmarks/datasets/sec_develop` |
| 科学场景 | `eval_profiles/onescience_scenario.json` | `benchmarks/datasets/scenario` |

先阅读候选用例的任务说明，确认其目标、输入、产物和指标确实能检验新增能力。没有合适用例时，先执行自定义任务测试；不要把不匹配用例的分数当作该技能效果。

在评测仓库中选择匹配的 Profile，按 README 准备依赖和智能体。配置实际执行智能体 `agent_id`、模型 `base_model` 和 `use_oneskill=true`；初次验证将 `run_config.max_concurrency` 设为 `1`，保留原有评测阶段。若存在 `run_config.agent_id/base_model`，当前调度器将其用于执行过程评审，应与任务执行模型区分，并在前后对比时保持评审配置一致。

运行前，确认评测 Worker 能读取本次安装的技能版本。当前 OpenCode 适配器从其配置目录的 `skills/` 获取技能用于隔离运行；Codex 适配器也有独立的运行时配置挂载。交互会话能发现技能，并不代表评测进程使用了同一安装来源。

### 先执行单个匹配用例

以下命令在评测仓库根目录运行，Profile 与用例按实际任务替换：

```bash
python scripts/parallel_eval.py \
  --profile eval_profiles/onescience_infer.json \
  --dataset_path benchmarks/datasets/infer/alphagenome_inference.json
```

这里以 AlphaGenome 演示单用例参数写法，实际应选择与新增能力匹配的用例。确认单用例流程可用后，再按 README 运行相关数据集目录或 Profile 默认数据集。

**区分 benchmark 的协作入口与单技能入口。** 当前调度器在 `use_oneskill=true` 时会前置 orchestrator 入口，在 `false` 时明确禁止技能。不能通过设置 `false` 来测试新增技能，也不能仅靠修改用例提示词就认定绕开了编排。默认路径适合测技能体系协作；若只测单技能，优先使用第 6.1 节的显式调用任务。确需复用 benchmark 的单技能定量评测时，应先确认该版本提供对应入口，或单独实现并记录受控的 Worker 入口适配，同时保持原用例的产物契约和评价标准。

### 查看产物、执行过程与评测指标

按 README 的结果布局检查：

```text
eval-records/<agent_id>-<agent_version>/<base_model>/<task_type>/
  submissions/<case_id>/           # 实际任务产物
  eval_results/
    summary.json
    <case_id>/
      agent_result.json
      execute_task_result.json
      rule_eval.json
      score.json                  # 仅在启用评分阶段时生成
      logs/                       # stdout、stderr、轨迹及冒烟日志
```

结合用例配置读取各项指标、失败项和原始日志，尤其是 `logs/agent_stdout.log` 中的任务执行过程，并检查新增技能的实际调用证据。保持评测器与验收条件不变，不向任务 Worker 提供评测器实现、参考答案或其他运行的历史产物。前后对比报告至少写明技能提交版本、用例、执行与评审模型、运行环境、功能/指标结果，以及失败原因；高分不能替代新增技能确实被调用和产物符合要求的证据。

## 8. 在开发分支测试优化，通过后合并到 master

根据功能测试、协作测试或评测结果，定位元信息发现、技能路由、任务执行、环境依赖和结果验证中的具体问题，在同一开发分支上修改。提交并推送优化后的新增技能及已有技能的配套修改，重新下载、安装，在新会话中复测，直至达到本次测试要求。若直接修改了安装副本，应将改动同步回源仓库。

测试记录应包含开发分支、最终测试的提交 SHA、智能体实际安装路径、测试任务与验收依据、返回结果或文件位置、执行日志及指标，以及未解决的限制，并明确单技能功能测试和协作测试各自的范围与结果。

完成测试和优化后，在 GitLab 创建或更新 Merge Request，以该开发分支为源分支、`master` 为目标分支，附上最终提交的测试证据，审核通过后再合并。若合并前又修改了技能或解决了代码冲突，应对受影响部分复测，确保合并的内容与验证结果对应。

合并后，将目标智能体中的技能同步为 `master` 上的合并版本，记录部署提交 SHA。
