# Execution Handoff Contract

执行技能（`type=executor`）只接收当前步骤的明确任务，不重新规划整个用户目标。executor 拥有当前 step，不拥有全局工作流；除非该技能自己的 `SKILL.md` 明确声明了下游委托与恢复规则，否则完成或受阻后都把控制权交回 `onescience-orchestrator`。

## Handoff 格式

```yaml
step_handoff:
  step_id: <步骤ID>
  attempt: <当前尝试次数，从 1 开始>
  execution_skill: <执行技能名称>
  step_goal: <本步骤目标>
  step_wallclock_budget_seconds: <步骤墙钟预算，autonomous_mode 下必填>
  execution_flags:
    autonomous_mode: <true|false>
    training_allowed: <true|false，继承用户约束，false 包含训练 dry-run/参数更新>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物>
  resource_bindings:
    - path: <资源路径>
      type: <资源类型>
      purpose: <用途>
  inputs: <执行所需输入，根据任务类型可为空或包含具体字段>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
  completion_scope: <spec_delivery | code_delivery | scientific_result>
```

## 执行技能返回格式

```yaml
execution_result:
  skill: <执行技能名称>
  attempt: <当前尝试次数>
  status: <success | partial | failed | blocked | step_timeout>
  failure_category: <transient | environment | dependency | data | code | scientific | platform | unknown | null>
  result_identity: <research_result | engineering_demo | smoke_test | not_a_result>   # C 层门禁强制字段
  result_identity_basis: <申报依据；产物自述含 smoke/demo/simplified/toy/not suitable for production 等关键词时 orchestrator 自动锁 not_a_result，executor 不得申报更高身份>
  artifacts:
    <产物清单>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
  events:
    - event_type: <step_started|repair_attempted|retry_started|diagnosis_completed>
      timestamp: <ISO8601>
      description: <事件描述>
```

**授权与约束传递**：用户原始要求、会话已有连续执行授权、输出目录和禁止训练必须传到每个
executor。已有明确授权不重新确认；未决科学值仍保留未决，自主执行不等于允许猜测。

**result_identity 与状态判定约束（C/D 层门禁）**：

- `completion_scope=spec_delivery|code_delivery` 的纯交付步骤按文件和约定检查验收，可返回
  `status=success`，但 `result_identity=not_a_result`，仅表示规格/代码交付完成。不得据此宣称
  科研 PASS。科研结果的下面各项判据不要求源码或文档本身成为 `research_result`。

- `result_identity ∈ {engineering_demo, smoke_test, not_a_result}` 的 step：状态只能标 `DEMO_PASS` / `PARTIAL` / `BLOCKED`，**禁止标 PASS**；其输出禁止进入最终报告「关键发现/科研结论」段，只能进入「方法演示/脚手架」段并前置「以下为演示输出，不构成本次科研结论」；下游依赖其产物的 step 自动继承 `not_a_result` 身份。
- **输入门禁 ≠ 结果身份门禁**：用户确认「使用默认示例/典型参数/推荐值」只解除 input_gate（允许用默认值继续执行），不解除 result_identity_gate——默认值跑出的产物仍是 `engineering_demo`，不得申报 `research_result`。
- 验证类 step（网格独立性/能量守恒/可复现审计/指标对标等）判 FAIL/PARTIAL 时，orchestrator 自动回退其上游已标 PASS 的 step 为 `UNVERIFIED`/`PARTIAL`（D 层级联回退，写 `validation_rollback` event）；executor 不得在验证失败后仍申报上游产物 PASS。
- `status=complete` 前提：所有 step `result_identity=research_result` + 所有验证 step PASS + 无未解除 `blocked_missing`；否则终态只能是 `complete_with_caveats` / `partial` / `blocked`。

## Step Owner 与下游委托规则

- `step_handoff.execution_skill` 是当前步骤的权威 owner；当前步骤被选定为 `executor_step` 后，orchestrator 正式 dispatch 给该 owner。若 owner 判断需要调整，先回到新一轮 planning / selection。
- `execution_result` 是 `executor_step` 的正式完成回执；caller 以该回执更新 observation，而不是用自身工具结果替代 executor-owned 步骤。
- executor 只在自身 `SKILL.md` 明确写出的窄委托 / 恢复合同内调用下游技能。该合同至少说明：可委托技能、触发条件、委托覆盖范围，以及委托完成后的恢复位置。
- 若当前 skill 没有写明上述合同，或当前问题已超出合同范围，则返回 `execution_result` 给 `onescience-orchestrator`，由 orchestrator 决定后续技能与下一步。
- 运行通道歧义、环境歧义、下一业务阶段归属、跨技能后续链路选择等，默认由 `onescience-orchestrator` 决定；只有当前 skill 明确声明可在窄范围内恢复当前任务时，才继续内部委托。

## 常见执行技能的职责（仅用于 handoff 便利摘要，不是权威边界来源）

本节只用于帮助上游快速组织 handoff 字段，不是 orchestrator 判定 executor 职责边界、排他范围或明确不负责事项的权威来源。

- 最终 scope / exclusivity / non-responsibility 判断，以对应 executor 的 `capabilities` 元信息为权威来源；仅在 `capabilities` 无法判定边界归属时，按需深读对应 SKILL.md。
- 若本节简写摘要与 executor 自身 `SKILL.md` 冲突，以 executor 自身 `SKILL.md` 为准。
- 技能名称和 `description` 用于初筛；`capabilities` 元信息用于最终任务拆分。仅在 `capabilities` 边界重叠时按需深读 SKILL.md。

### onescience-coder
- 接收：step spec、资源路径、目标目录、运行时参数（数据源路径、输出路径等）
- 执行：生成或修改代码
- 返回：代码产物、静态检查结果、未验证风险
- **重要**：生成的代码必须从函数参数、命令行参数或配置文件读取路径，不得硬编码或从环境变量推断默认值

示例 handoff：
```yaml
step_handoff:
  step_id: "implement_data_processing"
  execution_skill: onescience-coder
  step_goal: "实现 ERA5 数据处理脚本"
  inputs:
    parameters:
      source_dir: "/public/onestore/ERA5"
      output_dir: "./processed_data"
      variables: ["temperature", "pressure"]
      time_range: ["2020-01-01", "2020-12-31"]
  required_outputs:
    - "数据处理脚本，从参数读取 source_dir 和 output_dir"
    - "生成的代码应支持命令行参数或配置文件传入路径"
```

生成代码示例：
```python
# 正确：从参数获取
def process_data(source_dir: str, output_dir: str, variables: List[str]):
    ...

# 错误：硬编码或环境变量推断
source_dir = os.environ.get("ONESCIENCE_DATASETS_DIR", "/public/onestore")
source_dir = os.path.join(source_dir, "ERA5")
```

### onescience-paper-repro
- 接收：当前任务目标、用户明确要求、论文来源、输出约束，以及用户/上游显式提供的
  acceptance contract 或 evaluation artifacts（如有）
- 执行：意图审计、全文获取、逐字段充分性判断、必要的官方仓库只读补证、结构化提取、
  同一规格内的实现契约、核验和落盘交接门禁
- 返回：唯一 `reproduction_spec.md` 的路径、完整内容、SHA-256、conflicts、按实验/阶段及
  构建/运行影响分类的 unresolved、recommended consumer；不得再要求旧版独立任务书/JSON 契约
- 完成后必须回 orchestrator observation/planning；不得在同一回执中附带 coder 生成的源码、
  trainer 训练结果或 infer 评测结果，也不得把 `next_action` 固定为 coder

无原生 skill bridge 时，内联执行仍须使用独立的 `step_handoff` 和
`execution_result.skill=onescience-paper-repro`，并完整执行 paper-repro 的 stages/references/
gates。只生成一份概念 spec、随后由 orchestrator 直接写代码，不构成合法的 paper-repro 回执。

有 Skill 工具时必须实际调用 paper-repro，不把加载 primitives、直接 webfetch PDF 或复述
prompt 记作执行了该技能。来源获取失败或全文未核验不得以“prompt 已完整”跳过。
可交接时，给 coder 传 `paper_repro_handoff=true`、`reproduction_spec_path`、
`reproduction_spec_content`、`reproduction_spec_sha256`、conflicts、key_unresolved，并将
完整内容映射到 `reference_resources[*].content`。规格落盘后计算散列，修改后重新读回计算；
不能传摘要，不能在下游生成另一份规格。`partial` 时继续独立可实现模块，保留受阻部分。
代码请求只有在所需源码/配置实际存在、非空且约定验收完成后才满足；未决必填值导致构建或运行
受阻时明确返回 `partial`，不得将静态通过等同于可运行。

### onescience-runtime
- 接收：可运行入口、配置、执行目标
- 执行：preflight、execute、status、logs、diagnose
- 返回：运行证据、失败分类

### onescience-installer
- 接收：环境缺口、目标后端、安装 profile
- 执行：安装、修复或验证环境
- 返回：安装结果、环境状态

## Observation 处理

- success：写入 artifacts 和 events，交给 orchestrator 基于最新 Task State 判断是否需要继续规划下一步
- partial：记录已完成部分、缺失项和残余风险；orchestrator 先回到 observation/planning，再重新选择一个新的 next_step。若当前修复动作仍属于某个 executor-owned 范围，继续通过对应 executor dispatch。
- failed：记录失败证据和 `failure_category`。orchestrator 根据 failure_category 选择策略：
  - `transient` → 指数退避重试（最多 2 次）
  - `code` → 委托 onescience-coder 修复后重试（最多 2 次）
  - `environment` → 委托 onescience-installer 修复环境后重试
  - `scientific` / `dependency` → 直接进入 blocked，需要人工研判
  - `platform` → 阻塞后重试 1 次，仍失败则 block
  - `unknown` → 进入 diagnose 后根据诊断结果再判定
- blocked：记录阻断原因和所需用户输入；只有阻断被解除后才允许继续
- step_timeout：步骤超过 wallclock 预算，写入 event，进入 blocked。恢复后 budget 翻倍，attempt 递增后重新执行。

- 执行技能返回的结果只表示当前步骤的观察输入，不等同于直接跳转到下一条 executor 链路；后续由 orchestrator 基于最新 Task State 重新选择。
