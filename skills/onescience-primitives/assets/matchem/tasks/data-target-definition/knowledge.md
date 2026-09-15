# 数据与目标定义 (data-target-definition)

> Task 骨架卡。type=task，domain=matchem，位于 `assets/matchem/tasks/data-target-definition/`。
> 本卡不绑定单一场景，而是被多个场景的同一工序复用；场景差异全部落在「实体槽」上。

## 泛化来源（Generalization Provenance）

本卡由 `scenario_catalogs/materials/` 下 **21 个场景**的 workflow 第一步归并而成。

| 源字段 | 源取值（21 个场景完全一致） | 落到本卡的位置 |
|---|---|---|
| `workflow[0].step_name` | 数据与目标定义 | `name` = data-target-definition |
| `workflow[0].step_input[].var` | `{DATASET}` | `slot:dataset:*` |
| `workflow[0].step_input[].var` | `{TARGET}` | `slot:target_property:*` |
| `workflow[0].quality_gate[0]` | 训练/验证/测试划分可追溯 | `edge:validation:traceable-split` + `slot:split_scheme:*` |
| `workflow[0].quality_gate[1]` | 无未说明的数据泄漏 | `edge:validation:no-undocumented-leakage` |
| `workflow[0].outputs` | 清洗数据表 / 目标定义 / 数据审计报告 | 见「输入输出契约」 |
| `workflow[0].depend_step_id` | `[]`（无前置） | 无 `edge:prev` |
| `workflow[1].step_id` | s02 根源模型训练与适用域评估 | `edge:next:material-property-prediction` |
| `missing_information_policy` | 禁止用默认值补齐 | 见「缺口与降级」的 BLOCKED 规则 |

泛化率：**21 场景 : 1 卡**。若按 1:1 直出，同一套门禁要在 21 处重复维护。

## 任务目标

把上游场景需求书里的 `{DATASET}` 与 `{TARGET}` 落定为**可审计的数据契约**，产出三件东西：

1. 清洗数据表（去重、缺失标注、单位归一后）
2. 目标定义（性质名、单位、优化方向、可靠阈值、不适用条件）
3. 数据审计报告（样本量、重复率、缺失率、划分方案与互斥性证明、许可信息）

本任务**不产出科学结论**，只产出下游可用的输入契约。关键标签缺失时必须标记 `BLOCKED`。

## 适用范围 / 不适用场景

适用：
- 需要从数据库或用户提供的表格建立监督学习样本集的 materials 场景
- 目标性质为标量（模量、吸附能、形成能、带隙、热稳定性等）
- 场景需求书已给出 `required_results` 与 `acceptance_requirements`

不适用：
- 无标签的纯生成/逆向设计任务（应走 candidate-generation 骨架）
- 目标为时序轨迹或场量（气象/流体域，走各自域的时空对齐骨架）
- 数据来源不可追溯或许可不明（直接 BLOCKED，不进入后续工序）

## 实体槽（Entity Slots）

| 槽 | 取值域 | 场景差异如何体现 |
|---|---|---|
| `dataset` | matpl / dp / dpa3 / oc20 / mofdb / csv-user-provided | 决定接入路径：库内数据集走 `edge:resource:datasets/*`，用户表格走本地 CSV 审计 |
| `target_property` | elastic_modulus / bulk_modulus / adsorption_energy / formation_energy / band_gap / thermal_stability | 决定单位、优化方向、可靠阈值（取 `atom:*` 事实） |
| `split_scheme` | random / scaffold / time-based | 决定泄漏检查方式：scaffold 按骨架分组，time-based 按时间切点，random 需查同结构重复 |

槽取值写进 metadata.json 的 `slot:<key>:<value>` tag；检索时上层请求的槽值与卡的槽值取交集，交集为空即降级。

## 输入输出契约

输入：
- `{DATASET}`：CSV/JSON/数据库导出，须含样本标识、目标值列、单位、许可信息
- `{TARGET}`：目标性质的自然语言描述，须可操作化为「名称 + 单位 + 方向 + 阈值」

输出（机器可读，供 s02 消费）：
- `cleaned_table`：路径 + 行数 + 列清单 + 每列单位
- `target_definition`：`{property, unit, direction, reliable_threshold, not_applicable_when}`
- `audit_report`：`{n_total, n_unique, duplicate_rate, missing_rate_per_column, split:{scheme,train,valid,test,disjoint:bool}, license}`
- `decision`：`PASS` / `PARTIAL` / `BLOCKED`（四态沿用场景需求书的 `acceptance_decision`）

## 方法路线（可替换）

| 方法 | 适用 | 代价 | tag |
|---|---|---|---|
| 自动契约审计（默认） | 结构化表格、列语义清晰 | 低，stdlib 可离线跑 | `edge:method:dataset-contract-audit` |
| 目标操作化 | 需要把自然语言目标转成带方向与阈值的定义 | 低，需引用 atom 事实 | `edge:method:target-operationalization` |
| 人工整编（改道） | 列语义不明、单位缺失、多来源需手工对齐 | 高，需人介入 | `edge:fallback_method:manual-curation` |

改道条件：`duplicate_rate > 5%` 或任一关键列 `missing_rate > 20%` 或单位列缺失 → 自动审计不足以定契约，改人工整编，并把 decision 降为 `PARTIAL`。

## 操作序列（Operations）

| # | 操作 | tag | 落点 |
|---|---|---|---|
| 1 | 载入数据集并识别列语义 | `edge:operation:load-dataset` | `tools/dataset-contract-auditor` → `script/audit_dataset.py --demo` |
| 2 | 重复检查（全行 + 样本标识） | `edge:operation:check-duplicates` | 同上，输出 `duplicate_rate` |
| 3 | 缺失检查（逐列缺失率） | `edge:operation:check-missingness` | 同上，输出 `missing_rate_per_column` |
| 4 | 划分互斥性验证 | `edge:operation:verify-split-disjointness` | 同上，输出 `split.disjoint` |
| 5 | 冻结目标定义 | `edge:operation:freeze-target-definition` | 同上 `--target/--unit/--direction/--threshold` |

可执行落点：`tools/dataset-contract-auditor` 带 `runnable:script`，其 `script/audit_dataset.py` 仅依赖 Python 标准库，支持 `--demo` 内置样例，可离线跑通并输出 JSON 审计报告。

## 验证契约（Validations）

| 验证 | tag | 判据 | 不通过时 |
|---|---|---|---|
| 无未说明的数据泄漏 | `edge:validation:no-undocumented-leakage` | 同一结构/骨架不得跨 train 与 test；时间切点之后的样本不得进 train | decision=REJECT |
| 划分可追溯 | `edge:validation:traceable-split` | `split_scheme` 明确且三份互斥，折数 ≥5（见 `atom:atom_rv_cross_validation_folds`） | decision=PARTIAL |
| 目标单位一致 | `edge:validation:target-unit-consistency` | 目标列单位唯一，方向明确，阈值有出处 | decision=BLOCKED |

阈值出处取自 `references/tc/atoms.jsonl`：
- `atom_rv_cross_validation_folds`：5 折交叉验证是标准做法，fold < 3 结果不可靠
- `atom_mpp_prediction_r2_threshold`：R² > 0.9 可靠，0.7–0.9 需交叉验证，< 0.7 不可用于决策
- `atom_mpp_formation_energy_stability`：形成能 < 0 稳定，0 ~ +0.05 eV/atom 亚稳，> +0.05 不稳定

## 资源引用（Resources）

| 资源 | 路径 | type | 用途 |
|---|---|---|---|
| dataset-contract-auditor | `assets/matchem/tools/dataset-contract-auditor/` | tool | 可执行落点，产出审计报告 JSON |
| pymatgen | `assets/matchem/tools/pymatgen/` | tool | 结构解析、化学计量与空间群核对 |
| matpl | `assets/matchem/datasets/matpl/` | dataset | `slot:dataset:matpl` 时的数据来源 |

## 前后置任务（Task Graph）

- 前置：无（`workflow[0].depend_step_id = []`）
- 后继：`edge:next:material-property-prediction`（对应源场景 s02 根源模型训练与适用域评估）
- 所属骨架族：`src:scenario_family:materials-generic-4step`（s01 → s02 → s03 → s04）

## 缺口与降级（Fallback / Gap）

| 缺口 | 表现 | 处置 |
|---|---|---|
| 目标列缺失或全为空 | 无法操作化 `{TARGET}` | decision=BLOCKED，记录 `missing_resources:[target_labels]`，禁止用默认值补齐 |
| 许可信息缺失 | 无法确认可用性 | decision=PARTIAL，追加 gaps.jsonl，`suggested_fill` 写「补数据许可声明」 |
| 单位列缺失 | 无法做单位一致性验证 | 改道 `edge:fallback_method:manual-curation`，decision=PARTIAL |
| `slot:dataset` 取值在域内无资源卡 | 如 mofdb 无对应 datasets 卡 | 只降级本任务的接入路径，不影响 Task Graph 其余部分；追加 gaps.jsonl |
| 划分互斥性验证失败 | 存在泄漏 | decision=REJECT，必须重划分后才能进 s02 |

降级后 `retrieval_level` 由 full 降为 partial，按 SKILL.md 协议向 `references/tc/gaps.jsonl` 追加一行缺口记录。
