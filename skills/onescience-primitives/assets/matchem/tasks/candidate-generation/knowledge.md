# 候选材料生成 (candidate-generation)

## 任务目标

在给定 `material_family` 与性能意图下，产出**结构合法、去重、来源可追溯**的候选材料集合（默认 ≥ 100 个带随机种子的唯一候选），作为 `structure-validation` 与 `material-property-prediction` 的输入。生成物只能表述为候选线索，不得表述为已验证材料。

## 适用范围 / 不适用场景

**适用**：有明确材料族与可测目标；约束、单位、优先级可审计；候选会经独立合法性与新颖性核验。

**不适用**：约束只写成模糊的「高性能」「低毒」而无可测指标；无化学合法性与重复审计；目标化学空间含模型不支持的元素/反应且不允许外推验证。

## 实体槽（Entity Slots）

| 槽名 | 类型 | 允许取值 | 必填 |
|---|---|---|---|
| `material_family` | enum | MOF, zeolite, perovskite, alloy | 否 |
| `target_property` | enum | adsorption_energy, band_gap | 否 |

## 输入输出契约

| 项 | 内容 |
|---|---|
| 输入 | 材料族、参考结构/配体库、约束与目标性质、随机种子 |
| 输出 | 候选结构集合（CIF/SMILES/SDF）+ 生成方法 + 种子 + 无效/重复候选及原因 |

## 方法路线（可替换）

1. **structure-substitution（保守）**：在已知骨架上做位点取代、官能团装饰、超胞/缺陷枚举。适用：有可靠参考结构、需保持可合成性先验。
2. **de-novo-generation（探索）**：性质/活性引导的三维生成或图生成。适用：需跳出已知骨架、有可审计的约束与验证回路。前提：生成模型覆盖目标元素与化学空间。

生成模型不支持目标化学空间时，**改道** structure-substitution 并显式标注覆盖边界。

## 操作序列（Operations）

| 顺序 | 操作 | 说明 |
|---|---|---|
| 1 | `enumerate-candidates` | 按方法路线生成候选，记录种子与条件 |
| 2 | `sanitize-structures` | 元素/键级/立体化学合法性检查，用 `tools/rdkit`、`tools/pymatgen` |
| 3 | `deduplicate` | 按骨架/组成/指纹去重，保留重复原因 |

## 验证契约（Validations）

- `chemical-validity`：价态、配位、键长合法，无原子重叠。
- `novelty-check`：与参考库按骨架与指纹比对，区分记忆与真正新颖；划分须按化学系列/时间独立，避免参考泄漏。

## 资源引用（Resources）

| 资源 | 路径 | 角色 |
|---|---|---|
| pymatgen | `matchem/tools/pymatgen` | 晶体结构枚举与合法性检查 |
| RDKit | `matchem/tools/rdkit` | 分子合法性、指纹与去重 |

## 前后置任务（Task Graph）

**candidate-generation**（next）→ `structure-validation` → `material-property-prediction` → `candidate-ranking`。

## 缺口与降级（Fallback / Gap）

- 改道触发：生成模型不覆盖目标元素/反应 → 改道 structure-substitution；无参考骨架库 → 降级为组成空间枚举并标注可信度下降。
- 分层降级：`full` / `partial` / `task_only` / `none`；`retrieval_level != full` 时向 `.onescience/gaps.jsonl` 追加缺口记录。
- 已知缺口：MOF 专用拓扑生成资源卡未建；可合成性预测资源缺失。
