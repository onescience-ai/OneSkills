---
name: onescience-primitive-distiller
description: OneScience 原语蒸馏执行技能。用于将 scientific-agent-skills、第三方科研工具、数据库、服务、数据集、输出格式或工作流文档蒸馏为 onescience-primitives 资产包，并判断是否需要 resource、expert 或 executor 落地；不直接执行科研分析。
type: executor
---

# OneScience Primitive Distiller

你是 OneScience 的原语蒸馏执行技能（`type=executor`）。你的职责是把外部科研 agent skill 或第三方科研能力材料，标准化为 `onescience-primitives` 可以检索、绑定、规划和交接的 primitive 资产包。

本技能解决的是体系整合，不是目录合并。默认产物是 resource 级 primitive；只有当执行边界、输入输出、环境和验证方式都足够稳定时，才建议提升为 executor；只有当需要复杂取舍、领域决策和 fallback 时，才建议提升为 expert。

## 触发场景

使用本技能处理以下请求：

- 将 `scientific-agent-skills/skills/<name>` 蒸馏到 `skills/onescience-primitives/assets/`。
- 把第三方科研包、CLI、SDK、数据库、服务、数据集、输出格式或工作流经验注册为 OneScience primitive。
- 评估一个外部 agent skill 应落地为 primitive、expert、executor，还是拆成多个对象。
- 为已有 primitive 补齐 `primitive_id`、provider、provenance、requirements、contracts 或依赖关系。

不要用本技能执行真实科研分析、训练、推理、HPC 提交、报告生成或代码重构。这些任务应交给对应的 executor。

## 输入格式

```yaml
primitive_distillation_request:
  source:
    kind: agent_skill | upstream_docs | third_party_tool | database | service | dataset | output_format | workflow
    location: <source path, repo locator, URL, or supplied text>
    name: <source capability name>
  target:
    domain: <bio | cfd | climate | matchem | general>
    category: <tools | databases | datasets | services | output-format | workflow-planning | application | models | components | datapipes | contracts | visualization>
    primitive_name: <lower_snake_case or existing primitive directory name>
  options:
    distillation_status: resource_only | resource_with_execution_assets | propose_expert | propose_executor | split
    copy_knowledge_references: true
    copy_execution_assets: false
    update_consumers: true
```

缺少 `target` 时，先根据来源内容给出保守分类建议；能稳定判断时直接创建 resource 级 primitive 草案，不能稳定判断时返回需要用户确认的候选分类。

## 工作流程

1. **Inventory**
   - 读取来源 `SKILL.md`、frontmatter、`When to use`、workflow、examples、references manifest、scripts manifest 和 assets manifest。
   - 只在确实需要蒸馏执行资产时检查脚本和模板内容；默认不复制脚本。

2. **Classify**
   - 第三方包、CLI、SDK、HPC 软件、实验室工具 -> `tools`。
   - 数据库、知识库、API 数据源 -> `databases`。
   - 数据集、benchmark、标准样本集 -> `datasets`。
   - 云平台、远程计算、实验接口 -> `services`。
   - docx、pdf、pptx、表格、图件等交付形态 -> `output-format`。
   - 可复用路线、决策树、fallback -> `workflow-planning`。
   - 面向任务的工具组合和模板集合 -> `application`。
   - 输入输出 schema、handoff、验证规则 -> `contracts`。

3. **Distill**
   - frontmatter `description` -> `metadata.description`、`tags`、`capabilities`。
   - `When to use` 和 workflow -> `workflow_planning.md`。
   - API、依赖、输入输出、环境要求和限制 -> `spec.md`。
   - 安装、命令、常见失败和操作边界 -> `usage.md`。
   - `references/` -> 选择性写入 primitive 的 `references/`，并在 `metadata.json.knowledge_assets` 中登记来源、用途、媒体类型和 SHA-256。
   - scripts/assets -> 只有在 `copy_execution_assets: true` 且用户确认后，才进入 `execution_assets` 白名单；其余脚本只记录为迁移候选。

4. **Normalize**
   - 生成稳定 `primitive_id`: `<domain>.<category>.<primitive_name>`。
   - 目录固定为 `skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/`。
   - 第三方来源写入 `provider_kind`、`provider_name` 和 `source.distilled_from`，不要创建长期 bridge。
   - `metadata.domain` 优先使用目录 domain；需要兼容旧值时写 `legacy_domain`。

5. **Write Primitive**
   - 最小资产包必须包含 `metadata.json`、`spec.md`、`usage.md`、`workflow_planning.md`。
   - JSON 必须是 UTF-8、可解析、无注释、无绝对本地路径、无密钥。
   - markdown 文件只写可操作事实、边界和契约；不要复制大段上游文档。

6. **Connect Consumers**
   - 当已有 application/workflow primitive 明确消费该能力时，可在消费者 `metadata.json` 增加 `primitive_dependencies`。
   - 在消费者 `spec.md` 或 `workflow_planning.md` 中引用 `primitive_id`，说明角色和边界。
   - 消费者仍应通过 `resource_retrieval_result.matched_resources[*].content` 使用内容，不得直接读取另一个 primitive 的资产文件。

7. **Return Result**
   - 返回本次生成或修改的 primitive 路径、分类理由、未复制资产、执行提升建议和后续补齐项。

## 原语不是只有四件套

四件套是最小可交付核心包，不是上限：`metadata.json`、`spec.md`、`usage.md`、`workflow_planning.md`。

完整 primitive 还可以再带三层扩展：

- `references/`：只读知识补充，应该登记到 `metadata.json.knowledge_assets`
- `scripts/`：只有在白名单、hash、边界和许可证都审过以后，才作为 execution assets 进入
- consumer 依赖：`primitive_dependencies`、`provider`、`provenance`、`contracts`

更完整的 bundle 边界、蒸馏流水线和晋级规则见 `references/primitive_bundle_and_flow.md`。

## 全量覆盖与智能代码迁移

全量整合不是把源仓库的 163 个 `SKILL.md` 目录逐个复制到 `assets/`，而是为每个源技能建立可审计的迁移记录，并根据证据拆分为一个或多个 primitive、executor 或 expert 候选。

使用随附的只读盘点器生成候选清单：

```bash
python skills/onescience-primitive-distiller/scripts/build_skill_migration_manifest.py \
  --source-root <scientific-agent-skills-repo> \
  --target-root <oneskills-dev-repo> \
  --output <migration-manifest.json> \
  --markdown-output <migration-summary.md>
```

使用完整流水线先盘点、再按内置或外部 plan 物化 primitive：

```bash
python skills/onescience-primitive-distiller/scripts/distill_skill_batch.py \
  --source-root <scientific-agent-skills-repo> \
  --target-root <oneskills-dev-repo> \
  --plan-file skills/onescience-primitive-distiller/assets/materialize_plan.example.json \
  --force
```

只需要物化已盘点的候选时，可直接使用 `materialize_skill_primitives.py`；默认使用脚本内置迁移计划，也可以通过 `--plan-file` 指向 JSON plan。plan 模板见 `assets/materialize_plan.example.json`。

盘点器只读取源文件，不导入包、不执行脚本、不复制代码。它输出以下证据：

- `explicit_provenance`：目标原语通过 `source.distilled_from` 明确指向源技能。
- `heuristic_name_match` / `heuristic_alias_match`：仅作为人工复核候选，不能视为完成整合。
- `uncovered`：没有目标原语映射，需要进入后续批次。
- 知识通道：触发范围、工作流、接口、验证与限制、示例、references。
- 代码证据：文件类型、大小、SHA-256、接口信号、安装信号和风险信号。

### 知识整合矩阵

| 源技能内容 | 目标落点 | 要求 |
| --- | --- | --- |
| frontmatter `description` / tags | `metadata.json` | 保留触发词、能力边界和来源 |
| `When to use` / workflow / examples | `workflow_planning.md` | 转换为适用时机、决策步骤、fallback 和 handoff |
| API、依赖、输入输出、环境 | `spec.md` | 写成结构化边界，不复制无关背景 |
| 安装、命令、常见失败 | `usage.md` | 保留可操作示例和版本限制 |
| `references/` | primitive references 或拆分后的 companion primitive | 按主题保留，避免把长文档全部塞入 `SKILL.md` |
| scripts / assets 中的接口说明 | `spec.md` + `execution_assets` | 先记录候选，再经过执行化门禁 |

### 代码迁移分层

1. `resource_only`：仅迁移知识；代码依赖不稳定、风险过高、没有清晰输入输出或属于示例代码时使用。
2. `resource_with_execution_assets`：代码具有可复用价值，但仍需要显式白名单、许可证、依赖和运行边界审查。
3. `propose_executor`：代码具备稳定 CLI/API、明确输入输出、可诊断失败模式和可重复验证证据；这里只生成候选，不自动升级。
4. `split_primitives`：一个源技能同时包含工具、数据库、工作流、输出格式或多个任务链时，拆成多个 primitive，并通过依赖关系连接。
5. `propose_expert`：核心价值是领域判断、取舍、fallback 和结果解释，而不是固定脚本执行。

执行资产只有同时满足以下条件才允许物化：来源和许可证明确、文件路径在 primitive 目录内、依赖可声明、无未审查密钥或私有 URL、无隐式破坏性操作、SHA-256 已登记、输入输出契约已写入 `spec.md`，并通过隔离环境的最小运行检查。未满足条件的代码仍可作为知识证据，但不得进入 `execution_assets`。

## Primitive 资产包规范

```text
skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/
  metadata.json
  spec.md
  usage.md
  workflow_planning.md
  references/              # optional knowledge companions declared in metadata
  scripts/                 # optional, only when execution_assets is whitelisted
```

`metadata.json` 推荐字段：

```json
{
  "name": "scanpy",
  "primitive_id": "bio.tools.scanpy",
  "type": "tool",
  "domain": "bio",
  "category": "tools",
  "version": "1.0.0",
  "visibility": "public",
  "provider_kind": "third_party_open_source",
  "provider_name": "scverse",
  "source": {
    "distilled_from": "scientific-agent-skills/skills/scanpy",
    "distillation_status": "resource_only",
    "copied_execution_assets": false
  },
  "knowledge_assets": [],
  "description": "...",
  "tags": [],
  "capabilities": [],
  "requirements": [],
  "contracts": {
    "resource_output": "resource_retrieval_result",
    "execution_asset_policy": "none"
  }
}
```

## 提升规则

- **resource_only**：默认选择。适合第三方工具说明、数据库说明、数据集说明、输出格式、工作流经验和操作约束。
- **resource_with_execution_assets**：仅当脚本/模板是必要交付物、来源可信、路径可控、hash 已登记且用户明确要求复制时使用。
- **propose_expert**：当能力核心是取舍、规划、路线比较、fallback、领域判断，而不是固定命令或固定资源时使用。
- **propose_executor**：当输入输出契约稳定、运行环境明确、失败模式可诊断、测试或验收证据可重复时使用。
- **split**：当一个来源 skill 同时包含工具、数据库、工作流和脚本模板时，拆成多个 primitives；不要塞进一个过宽的对象。

## 硬约束

- 不得把 `scientific-agent-skills/skills/` 整目录复制到 `onescience-primitives/assets/`。
- 不得把 bridge 当目标架构；bridge 只允许作为迁移期兼容层。
- 不得为了接入某个第三方工具修改 orchestrator 的领域硬编码。
- 不得默认继承来源 skill 的脚本执行能力；脚本必须经过白名单、hash 和边界审查。
- 不得把第三方来源写成 OneScience 自有能力；必须保留 provider 和 provenance。
- 不得在 primitive 中写入 API key、私有 URL、绝对本地路径或未授权数据。

## 输出格式

```yaml
primitive_distillation_result:
  status: success | partial | blocked
  generated_assets:
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/metadata.json
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/spec.md
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/usage.md
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/workflow_planning.md
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/references/  # optional
    - skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/scripts/      # optional, only after review
  classification:
    primitive_id: <domain.category.name>
    target_type: resource_only | resource_with_execution_assets | propose_expert | propose_executor | split
    reason: <one or two sentences>
  provenance:
    distilled_from: <source locator>
    copied_execution_assets: true | false
  consumer_updates:
    - <updated existing primitive or none>
  followups:
    - <missing evidence, execution promotion candidate, or validation need>
```
