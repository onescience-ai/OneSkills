# 材料候选筛选场景 (material-candidate-screening)

## 需求描述

一类真实科研需求的抽象：「在某气体捕集/分离目标下，从给定材料族中筛选出若干可签收的候选材料，并说明取舍理由与结论边界。」

场景卡**只做需求绑定与验收口径**，不重复方法与操作细节——能力由工作流编排的 Task 卡提供。典型自然语言请求：

- 「帮我筛一批对 CO₂ 有高吸附能、对 N₂ 有选择性的 MOF 候选」
- 「胺基液体/膜材料里哪些体系值得优先做 SO₂ 捕集实验」
- 「给我一份可签收的短名单，并说明哪些结论只能算探索性线索」

## 需求 → 实体槽绑定

| 需求要素 | 槽 | 取值示例 | 说明 |
|---|---|---|---|
| 材料体系 | `material_family` | MOF, zeolite, amine-liquid, membrane | 决定方法适用性与资源选择 |
| 目标气体 | `adsorbate` | CO2, SO2, H2S | **CO 不在 MLIP 覆盖内**，需改道 DFT |
| 目标性质 | `target_property` | adsorption_energy, selectivity | selectivity 需多性质组合，属已知缺口 |

槽取值同时以 `slot:*` tag 落在 metadata.json，检索期做**精确匹配**：请求槽取值与卡片槽取值无交集时不得硬套该 Task，应改道或记缺口。

## 绑定工作流

默认编排：`matchem/workflow/material-screening-workflow`（边 `edge:workflow:material-screening-workflow`）。

阶段链：候选生成 → 结构核验 → 性质预测 → 精度核算 → 候选排序 → 结果验证。场景可按需裁剪（如只做「已有候选的性质预测 + 排序」时，从阶段 3 起）。

## 交付物与验收

| 交付物 | 验收口径 |
|---|---|
| 候选短名单（Top-N） | 每项带性质值 + 单位 + 不确定度 + 方法路线 |
| 取舍理由 | 淘汰项写明未通过的门槛与原因 |
| 三态结论 | 可签收 / 待复核 / 无法回答，逐项标注 |
| 缺口清单 | 本次检索 `retrieval_level != full` 的记录 |
| 可复现证据 | 阶段 4 的指标 JSON 报告（本机可跑，`code=OK`、`passed` 明确） |

**不得**出现：把预测分数表述为实验性能；无阈值却给「精度合格」结论；跳过门槛继续下游。

## 缺口与降级

- 槽不匹配（如请求 `adsorbate=CO`）→ 改道 DFT 路线；DFT 求解器资源卡缺失 → `partial` + 缺口记录。
- `target_property=selectivity` → 需多性质组合，当前无专用操作序列 → `partial` 并说明。
- 任一阶段 `retrieval_level != full` → 向 `.onescience/gaps.jsonl` 追加记录，供 harvester 填补。
