# Paper2Code 边界契约

本文件给 `onescience-role` 提供论文复现任务的默认层级约束与边界规则。

## 职责边界

### onescience-role（本层）负责：

1. 消费上游 workflow 传递的 `paper_source`、mode、framework、真实 `domain_route`
2. 将 `onescience-paper-repro` 的前处理流水线拆解为角色链
3. 为每个阶段定义角色交接物
4. 决定是否进入执行层（onescience-skill → onescience-paper-repro → onescience-coder）
5. 在规划阶段只输出角色链与交接物，不展开完整执行链

### onescience-role 不负责：

- 实际下载或复制论文材料（Stage 1 执行由 onescience-paper-repro 负责）
- 实际生成代码（Stage 4/5 实现层由 coder 负责）
- 解析论文内容（由 onescience-paper-repro 负责）

## 角色链约束

论文复现任务涉及三类角色：

```
research-lead → paper-analyst → paper-reproducer
```

- **research-lead**：确认研究目标、论文选择、模式选择
- **paper-analyst**：完成论文获取、复现信息抽取与歧义审计
- **paper-reproducer**：把复现规格和完整任务描述交给执行层（代码生成由 coder 消费 paper-repro 产物完成）

实际执行时，论文获取、解析、复现规格和任务描述由 `onescience-paper-repro` 完成，代码生成由 `onescience-coder` 完成。通用最小角色链为：

```
research-lead → paper-reproducer
```

其中 `paper-reproducer` 内聚论文复现职责，但执行层必须先进入 `onescience-paper-repro`，再交接给 `onescience-coder`。

若论文主题已经落入明确科学领域，role 层应在交接中保留领域角色，例如：

```
research-lead → domain-scientist → model-engineer → paper-reproducer
```

`paper2code` 只表示任务方法，不覆盖 `domain_route` 中的真实领域。

## 阶段约束

1. **按序推进**：论文获取与解析 → 复现信息抽取 → 歧义审计 → Coder 任务描述；已有合格 artifact 可满足对应阶段，但阶段顺序不可倒置
2. **歧义审计是防幻觉关键**：在交给 coder 之前，必须记录明确给出、推断得到、未说明但实现必须选择的项
3. **Coder 任务描述依赖复现规格并完整覆盖规格**：必须先生成 `reproduction_spec.md`，再生成自包含的 `coder_task_description.md`；`coder_task_description.md` 必须承载 `reproduction_spec.md` 中所有已确定内容，供 `onescience-coder` 单独消费
4. **代码与 notebook 不在 role 层生成**：由 `onescience-paper-repro` 交接给 `onescience-coder` 后完成

## 工作目录约束

role 层必须把论文工作目录约束传递给执行层，但不直接创建、下载或写入这些文件。

| 场景 | 工作目录规则 |
|------|--------------|
| arXiv URL / PDF / ID | `.paper2code_work/<arxiv_id>/`，例如 `.paper2code_work/2406.01465/` |
| arXiv ID 带版本号 | 目录去掉版本号，例如 `2406.01465v2` 仍使用 `.paper2code_work/2406.01465/` |
| 只有标题或 DOI | 先由 `onescience-paper-repro` 解析 arXiv 来源；无法解析时使用标题 slug 或 DOI slug 临时目录 |
| 用户指定 `output_dir` | 只表示最终代码落点，不改变 `.paper2code_work/<paper_key>/` |

`onescience-paper-repro` 应在该目录保存论文材料、中间分析和核心产物，包括 `paper_text.md`、`reproduction_spec.md`、`coder_task_description.md` 等。不要生成 `paper_source.json` 或 `evidence_index.md` 作为额外交接文件；来源信息和证据位置写入 `reproduction_spec.md`。

## 输入约束

从 workflow 层接收的交接摘要必须包含：

| 字段 | 说明 | 必填 |
|------|------|------|
| `paper_source` | arxiv ID/URL、本地 PDF、粘贴文本或已知论文名 | 是 |
| `arxiv_id` | 当 `paper_source` 可解析为 arxiv 时提取，如 `2106.09685` | 否 |
| `mode` | `minimal` / `full` / `educational` | 是 |
| `framework` | `pytorch` / `jax` / `numpy` | 是 |
| `user_intent` | 用户原始意图描述 | 是 |
| `domain_route` | 真实科学领域，如 `earth` / `biology` / `materials` / `cfd` / `general-science` | 是 |
| `domain_task_family` | 固定为 `paper-reproduction` | 是 |
| `task_method` | 固定为 `paper2code` | 是 |
| `output_dir` | 用户指定的最终代码生成目录；不能当作论文工作目录 | 否 |

## 输出约束

向 onescience-skill 传递时，至少包含：

| 字段 | 说明 |
|------|------|
| `current_role` | `paper-reproducer` |
| `role_chain` | `["research-lead", "paper-reproducer"]` |
| `handoff_artifacts` | paper_source, mode, framework, domain_route, stage_status, pipeline stages |
| `execution_entry` | `onescience-paper-repro` |
| `next_skill` | `onescience-skill` |
| `planning_only` | true/false |

`handoff_artifacts` 中必须包含或要求下游生成：

- `paper_workdir=.paper2code_work/<arxiv_id-or-paper_key>`
- `implementation_code_used=false`
- `output_dir=<用户指定最终代码目录>`，仅当用户指定时提供
- `required_outputs=[reproduction_spec.md, coder_task_description.md]`
- `coder_handoff_fields=[paper_repro_handoff, task_description_path, task_description_content, paper_workdir, coder_reference_mode, coder_static_review_required]`
- `reproduction_spec.md` 是审计和追溯产物，不作为 `onescience-coder` 的编码输入；`onescience-coder` 只消费 `coder_task_description.md`

## 禁止事项

- 不要在 role 层实际下载论文或生成代码
- 不要跳过歧义审计直接进入 `onescience-coder`
- 不要用 `paper2code` 覆盖 Earth/CFD/Biology/Materials 等真实科学领域
- 不要查找、打开、下载、clone、复制或参考官方/第三方已实现代码仓库；role 层交接物不得包含“去 GitHub 查官方代码”这类动作
- 不要创造不存在的 skill
- 在规划阶段不要展开 `onescience-skill -> onescience-paper-repro -> onescience-coder` 完整链路
