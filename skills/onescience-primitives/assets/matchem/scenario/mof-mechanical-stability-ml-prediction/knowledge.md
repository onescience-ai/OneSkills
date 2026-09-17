# MOF 结构力学稳定性机器学习预测 (mof-mechanical-stability-ml-prediction)

> 场景卡（type=scenario），Task-Centric 链的最上层入口。
> 位置：`assets/matchem/scenario/mof-mechanical-stability-ml-prediction/`

## 目标

上层需求：用机器学习预测 MOF 的结构力学稳定性（体模量 / 弹性模量），挑出力学上可靠、值得进入下一步高保真验证的候选骨架，并对每项交付给出 PASS/PARTIAL/REJECT/BLOCKED 判定。

## 来源与转换（Scenario JSON → 本卡）

| 源 JSON 字段 | 源取值 | 转换到本卡 |
|---|---|---|
| `scenario_id` | MOF结构力学稳定性机器学习预测 | `tag src:scenario_id:*`（溯源用，不改 name） |
| `domain` | matchem | `domain` 字段 |
| `type` | paper_scenario | 本卡 `type` = `scenario`（TC 编排层，不沿用源值） |
| `problem_and_applicability.client_request.request` | 围绕该场景完成可执行任务，仅采用关联论文可追溯事实，缺输入标 BLOCKED | description + 「约束继承」 |
| `workflow`（4 步） | s01 数据与目标定义 / s02 根源模型训练与适用域评估 / s03 约束候选生成与排序 / s04 独立验证与结论 | **不在本卡展开**，交给 `edge:workflow:materials-generic-4step-screening` |
| `related_papers[0].paper_id` | doi_10_1016_j_matt_2019_03_002 | `tag src:paper:*` + 下方引用 |
| `acceptance_requirements.acceptance_decision` | PASS / PARTIAL / REJECT / BLOCKED | `slot:acceptance_decision:*` |
| `missing_information_policy` | 不得以默认值替代 | 下传给各 Task 卡的「缺口与降级」 |

关联论文（仅背景与核验依据，不替代本次任务的数据与结论）：
*Structure-Mechanical Stability Relations of Metal-Organic Frameworks via Machine Learning*, doi:10.1016/j.matt.2019.03.002

## 槽绑定（本场景对骨架的实例化）

| 槽 | 本场景取值 | 传给哪个 Task |
|---|---|---|
| `material_family` | MOF | 全部 |
| `target_property` | bulk_modulus（主）、elastic_modulus（备选） | s01 数据与目标定义、s02 根源模型训练 |
| `dataset` | matpl 或 csv-user-provided | s01 |
| `split_scheme` | scaffold（按骨架族划分，防同族泄漏） | s01 |
| `acceptance_decision` | 四态，逐项交付标注 | s04 |

## 编排

本场景只持有一条编排边：`edge:workflow:materials-generic-4step-screening`。
四步骨架的 Task 展开、门禁与资源绑定都写在 Workflow 卡里，本卡不重复，避免同一编排知识出现两处。

## 适用场景

- 有一批 MOF 结构（数据库导出或用户提供 CSV），需要预测力学稳定性指标并排序
- 目标为标量性质，且能明确单位与优化方向
- 允许按骨架族做 train/valid/test 划分

## 不适用

- 目标是气体吸附等温线、扩散系数等非力学性质（应换 Scenario 或换 `target_property` 槽）
- 无标签数据、纯生成式逆向设计（走 candidate-generation 系骨架）
- 需要实验合成验证作为签收条件（本场景只交付计算结论与待验证清单）

## 缺口与降级

| 缺口 | 影响 | 处置 |
|---|---|---|
| 域内无弹性张量计算资源卡（如 VASP / Quantum ESPRESSO） | s04 的「高保真独立验证」无法本地执行，只能用留出集统计验证 | retrieval_level 降为 partial，追加 .onescience/gaps.jsonl，`suggested_fill` 写「补 DFT 求解器资源卡」 |
| `dataset=csv-user-provided` 但用户未给列语义 | s01 无法操作化目标 | s01 判 BLOCKED，整条链停在第一步，不得用默认值补齐 |
| 关联论文全文不可得 | 只能做背景引用，不能提取数值事实 | 标注证据等级为 doc-only，相关 atom 引用降级为 medium 置信 |
