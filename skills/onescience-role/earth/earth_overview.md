# Earth Role Overview

本文件是 `onescience-role` 进入 Earth 领域后的第一入口。

它只负责两件事：

1. 判断当前请求应该落到哪个 Earth 任务桶。
2. 决定应给 `onescience-coder` 或后续运行相关层交什么摘要。

不要在这里展开具体实现，也不要重复上游入口的工作流识别。

## 进入本文件时的默认前提

默认上游已经完成这些基础判断：

- 当前请求属于 `earth`
- 当前请求已经进入 `onescience-role`
- 当前阶段可能是数据、模型、训练、推理或多阶段串联之一

如果这些前提仍不成立，只补最小必要判断，不要重新做完整入口分析。

## Earth 任务入口判断

优先按当前主目标把任务归入以下 7 类之一：

1. `existing-earth-data-adaptation`
适用：复用已有 Earth 数据流、已有数据接口或已有 example 的数据组织方式。

2. `new-data-interface-construction`
适用：新增一套 Earth 数据接口，先完成读取、样本组织或 datapipe 设计。

3. `earth-model-construction`
适用：复用现有 Earth 模型做结构改造，或组合现有资产形成新模型。

4. `earth-training-pipeline`
适用：围绕训练入口、配置、样本组织和训练闭环做规划。

5. `earth-inference-pipeline`
适用：围绕推理入口、结果导出和推理链路做规划。

6. `external-reference-inference`
适用：需要参考外部权重、外部推理链路或外部结果对照。

7. `earth-multi-stage-workflow`
适用：需要把数据、模型、训练、推理等多个阶段串成一个完整流程。

具体说明和参考入口见 `skills/onescience-role/earth/task_map.md`。

## Earth Role 的输出要求

在进入下游前，至少整理出：

- `earth_task_type`
- `stage_goal`
- `current_role`
- `role_chain`
- `handoff_artifacts`
- `coder_reference_targets`
- 是否只是规划阶段

如果后续还会进入服务器端运行或调试，再额外保留：

- 目标入口是训练还是推理
- 是否存在固定运行约束
- 是否已有可参考的 `SLURM` 提交样式

说明：

- 若当前只是规划阶段，`coder_reference_targets` 和未来执行入口只表示后续可进入的方向
- 当前这一跳仍应停留在 `onescience-role`，不要把未来执行入口误当成已调用的 skill
- 规划阶段最多给出一个未来执行入口，通常是 `onescience-coder`；不要展开 `coder -> runtime` 或 `coder -> runtime -> installer` 完整链路

## 下探原则

- 需要代码实现时，交给 `onescience-coder`
- 需要服务器端提交、日志获取或运行排查时，只保留运行约束，不在本层展开
- 当前若只是规划任务路线，可停留在“任务桶识别 + 交接摘要”层级
- 当前若只是规划任务路线，不要把 `onescience-skill`、`onescience-runtime`、`onescience-installer` 写成当前 pipeline 阶段

## 本层应读取的资料

默认先读取：

- `skills/onescience-role/earth/boundary_contract.md`

再按任务桶细分需要读取：

- `skills/onescience-role/earth/task_map.md`

必要时回退：

- `skills/onescience-role/references/role_matrix.md`

## 一个标准例子

如果请求是“新建一个 Earth 数据接口，参考 `TJ-Data`，先不要写代码”，则本层应：

1. 归类为 `new-data-interface-construction`
2. 确定当前主目标是先形成读取与接口约定
3. 把后续参考方向交给 `onescience-coder`
4. 明确标记当前只做规划，不进入代码生成
