# materials 通用四步筛选骨架 (materials-generic-4step-screening)

> 工作流骨架卡（type=workflow）。位置：`assets/matchem/workflow/materials-generic-4step-screening/`
> 这是**一张卡服务 21 个场景**的泛化载体；场景卡只持有 `edge:workflow:materials-generic-4step-screening` 一条边。

## 目标

把 materials 域「机器学习筛选类」场景的公共工序固化为一条可复用的四步链，并把每步绑定到 Task 骨架卡、门禁与资源。

## 泛化证据

`scenario_catalogs/materials/` 下 21 个场景的 workflow 满足：

- 步数恒为 4，`step_id` 恒为 s01–s04
- `step_name` 逐字相同：数据与目标定义 / 根源模型训练与适用域评估 / 约束候选生成与排序 / 独立验证与结论
- `step_input[].var` 集合相同：`{DATASET}` `{TARGET}` `{MODEL_CONFIG}` `{VALIDATION_DATA}`
- `quality_gate` 逐字相同（每步 2 条）
- `depend_step_id` 恒为线性链：s01←[] , s02←[s01] , s03←[s02] , s04←[s03]

差异只出现在 `scenario_id`、`related_papers` 与变量 `default`/`hint` 上 → 全部落到槽与场景卡，不进本卡。

## 任务编排（Task Graph）

| 源步骤 | step_name | Task 卡 | 状态 | 变量 → 槽 | 门禁（源 quality_gate 原文） |
|---|---|---|---|---|---|
| s01 | 数据与目标定义 | `tasks/data-target-definition` | **新建** | `{DATASET}`→`slot:dataset`，`{TARGET}`→`slot:target_property` | 训练/验证/测试划分可追溯；无未说明的数据泄漏 |
| s02 | 根源模型训练与适用域评估 | `tasks/material-property-prediction` | 复用 | `{MODEL_CONFIG}`→`slot:model_config` | 外部测试与训练数据隔离；不能以训练误差替代泛化性能 |
| s03 | 约束候选生成与排序 | `tasks/candidate-ranking` | 复用 | `{TARGET}`→`slot:target_property` | 所有候选满足硬约束；适用域外候选单独标识 |
| s04 | 独立验证与结论 | `tasks/result-validation` | 复用 | `{VALIDATION_DATA}`→`slot:validation_data` | 预测与验证分开报告；失败候选保留记录 |

辅任务：`tasks/candidate-generation` 可接在 s03 之前（源骨架把「生成」与「排序」合并在 s03，本域已有独立的生成骨架卡，需要显式枚举候选空间时接入）。

步骤映射写进 tags：`edge:step:s01:data-target-definition` 等 4 条，用于从 Task 卡反查它在源场景里是第几步。

## 阻断规则

任一步门禁失败 → 后续步骤不执行，整条链按四态签收：

| 情形 | decision | 后续 |
|---|---|---|
| s01 判 BLOCKED（目标列缺失/样本不足） | BLOCKED | 停，禁止用默认值补齐 |
| s01 判 REJECT（骨架泄漏） | REJECT | 回 s01 重划分 |
| s02 泛化指标不达标 | PARTIAL | 可继续，但 s04 必须标注「待验证预测」 |
| s03 存在硬约束违背候选 | REJECT | 剔除后重排 |
| s04 无独立验证数据 | PARTIAL | 结论只能是「待验证预测」，不得宣称验证成功 |

## 资源落点（本骨架实际会用到的）

| 步骤 | 资源 | 可执行 |
|---|---|---|
| s01 | `tools/dataset-contract-auditor` | ✅ `script/audit_dataset.py`（stdlib，`--demo` / `--demo-leaky` 离线可跑） |
| s01 | `tools/pymatgen`、`datasets/matpl` | 规划级 |
| s02 | `models/mace`、`tools/pymatgen` | 规划级（无本地训练落点） |
| s03 | `models/mace`、`tools/pymatgen` | 规划级 |
| s04 | `tools/prediction-metric-calculator` | ✅ `script/calc_metrics.py`（stdlib，`--demo` 离线可跑） |

两个 ✅ 是本骨架当前**真能跑通**的落点：s01 用审计器产出数据契约，s04 用指标计算器核算精度并给通过判定。s02/s03 只有规划级落点，属已知缺口。

## 适用场景

materials 域中「有标签数据 + 训练模型 + 约束排序 + 独立验证」形态的场景，实测覆盖 21 个（占 materials 101 个场景的 20.8%）。

## 不适用

- 催化反应网络类场景（走「活性位与反应网络定义 → 吸附与反应响应获取 → 活性选择性稳定性联评 → 候选筛选与验证设计」骨架族，19 个场景）
- 电池退化类场景（走「材料与工况建模 → 结构或电化学响应获取 → 退化机制与性能指标分析 → 方案排序与独立复核」骨架族，15 个场景）
- 分离膜类场景（走「结构与分离目标定义 → 传质或吸附性能获取 → 选择性稳定性与能耗分析 → 材料或工艺窗口输出」骨架族，12 个场景）
- 生成/逆向设计类场景（无标签，不适用 s02 的监督训练前提）

## 缺口与降级

| 缺口 | 处置 |
|---|---|
| s02 无本地可执行落点（训练需要 GPU 与数据集） | 标注「无可执行落点，仅规划」，retrieval_level 最多到 partial |
| s03 硬约束判定缺约束求解资源卡 | 追加 gaps.jsonl，`suggested_fill` 写「补约束筛选/优化器资源卡」 |
| s04 缺高保真独立验证资源（DFT 求解器） | 只能用留出集统计验证，结论降级为「待验证预测」 |
| 另 3 个 materials 骨架族尚未建卡（催化 19 / 电池 15 / 分离膜 12 场景） | 这 46 个场景当前只能命中 legacy 实例卡，须标 `legacy_instance: true` |
