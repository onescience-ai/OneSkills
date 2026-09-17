# 材料候选筛选工作流 (material-screening-workflow)

## 目标

把「从材料族与性能意图出发，产出可签收的候选短名单」这一目标编排为**可复用 Task 的有序图**，并在每个环节设门槛。工作流只管顺序、门槛与降级，方法与操作细节留在各 Task 卡内，避免重复与漂移。

## 任务编排（Task Graph）

| 阶段 | Task | 门槛（不通过即停止该分支） | 边 |
|---|---|---|---|
| 1 | `candidate-generation` | `chemical-validity` + `novelty-check` 通过，候选数 ≥ 100 | `edge:task:candidate-generation` |
| 2 | `structure-validation` | `geometric-plausibility` + `convergence-check` 通过 | `edge:task:structure-validation` |
| 3 | `material-property-prediction` | `prediction-accuracy` + `physical-plausibility` 通过，带不确定度 | `edge:task:material-property-prediction` |
| 4 | `prediction-accuracy-evaluation` | 脚本核算 MAE/R² 达阈值（本机可跑） | `edge:task:prediction-accuracy-evaluation` |
| 5 | `candidate-ranking` | `ranking-stability` + `uncertainty-propagation` 通过 | `edge:task:candidate-ranking` |
| 6 | `result-validation` | 三态结论：可签收 / 待复核 / 无法回答 | `edge:task:result-validation` |

顺序约束：`1 → 2 → 3 → 4 → 5 → 6`；阶段 4 可与 5 并行（4 复核 3 的精度，5 消费 3 的性质值），但 6 必须在 4、5 之后。

**Task 复用**：六个 Task 均可被其他工作流单独引用（如 `result-validation` 可用于任何预测类工作流的终端复核），复用只需 `edge:task:<name>` 一条边，不需复制 Task 内容。

## 适用场景

- 有明确材料族与可测目标性质，允许计算/预测层面结论。
- 需要可审计的淘汰理由与门槛证据，而非只给一个短名单。
- 允许在资源不足时显式降级并记录缺口。

## 缺口与降级

- **阶段级降级**：某阶段资源仅部分命中 → `retrieval_level=partial`，继续但在交付中标注精度/覆盖降级；仅命中 Task 卡 → `task_only`，只输出方法与契约说明，不产出数值结论；无命中 → `none`，停止该分支。
- **缺口记录**：任一阶段 `retrieval_level != full`，向 `.onescience/gaps.jsonl` 追加记录（domain、task、缺失资源、请求槽取值、时间戳），供 harvester 后续填补。
- **改道**：阶段 3 的 MLIP↔DFT 互备改道按 Task 卡内条件触发；DFT 求解器资源卡当前缺失，触发时记 `partial` 并说明。
- **已知缺口**：DFT 求解器资源卡、MOF 拓扑生成资源、成本/可合成性代理、实验数据回流通道均未建。
