# CFD Role Overview

本文件是 `onescience-role` 进入 CFD 领域后的第一入口。

它只负责三件事：

1. 判断当前请求应该落到哪个 CFD 任务桶。
2. 把 CFD 数据、模型、训练、推理之间的兼容性问题整理成可交接摘要。
3. 决定应给 `onescience-coder` 下发哪些 `assets` 资料。

不要在这里展开具体实现，也不要重复上游入口的工作流识别。CFD 任务进入 coder 时默认采用 `assets_only` 模式，不再依赖 `onescience-coder/references/` 下的通用流程文档。

## 进入本文件时的默认前提

默认上游已经完成这些基础判断：

- 当前请求属于 `cfd`
- 当前请求已经进入 `onescience-role`
- 当前阶段可能是数据接口、模型适配、训练对比、图网络 rollout、推理评估或多阶段串联之一

如果这些前提仍不成立，只补最小必要判断，不要重新做完整入口分析。

## CFD 任务入口判断

优先按当前主目标把任务归入以下 7 类之一：

1. `cfd-existing-datapipe-adaptation`
适用：复用已有 CFD datapipe、已有数据接口或已有 example 的数据组织方式。

2. `cfd-new-dataset-interface`
适用：新增一套 CFD 数据接口，先完成读取、字段探测、样本组织或 datapipe 设计。

3. `cfd-model-adaptation`
适用：把某套 CFD 数据接到 Transolver、FNO、U_Net、LSM、MeshGraphNet 等现有模型或案例。

4. `cfd-model-benchmark-comparison`
适用：用户希望在多个 PDE / CFD / operator 模型上训练并对比效果。

5. `cfd-graph-rollout-stability`
适用：MeshGraphNet / GNS / Vortex shedding 等图网络任务中的噪声扰动训练、多步 rollout 或长时间稳定性评估。

6. `cfd-inference-evaluation`
适用：围绕推理入口、指标、可视化、rollout 结果或 benchmark 汇总做规划。

7. `cfd-multi-stage-workflow`
适用：需要把新数据接口、模型适配、训练、推理、评估等多个阶段串成完整闭环。

具体说明和参考入口见 `skills/onescience-role/cfd/task_map.md`。

## CFD Role 的输出要求

在进入下游前，至少整理出：

- `cfd_task_type`
- `stage_goal`
- `current_role`
- `role_chain`
- `handoff_artifacts`
- `coder_reference_mode=assets_only`
- `coder_reference_targets`
- `default_benchmark_models`
- `model_reuse_policy`
- `forbid_local_model_definitions`
- 是否允许进入代码生成

如果任务涉及新数据集，还必须补充：

- `new_dataset_stage`: `datapipe-only`、`full-adaptation` 或 `full-adaptation + benchmark-comparison`
- 数据形态判断：规则网格、非结构点云、PyG 图、DGL 图、VTK / surface mesh、HDF5 / PDEBench 风格或未知
- README 信息是否足够，以及是否需要先做只读字段 / shape 探测
- datapipe 命名建议和是否为 `case-local` 集成

如果任务涉及模型复用或对比，还必须补充：

- 候选模型
- 每个模型的数据协议
- 每个模型的兼容状态：`direct`、`adapter-required` 或 `not-recommended`
- 是否需要 canonical datapipe 之外的 adapter / view
- 是否明确要求使用 OneScience 已登记模型实现，而不是训练脚本内自定义替代模型

## CFD Benchmark 默认模型

当用户只说“在不同 PDE 模型上训练并对比效果”或“比较多个 CFD / operator 模型”，但没有指定模型列表时，默认候选固定为：

- `Transolver`
- `FNO`
- `U_Net (CFD_Benchmark)`
- `LSM`

说明：

- 这里的 `Transolver` 是默认任务候选名。
- 如果数据是结构网格、规则网格或 `(x, fx)` operator view，实际下发给 coder 的模型卡应是 `Transolver (CFD_Benchmark)`。
- 结构网格不是排除 Transolver 的理由，优先判断是否能走 `onescience.models.cfd_benchmark.Transolver`。

如果某个默认候选与数据协议不兼容，应标记为 `adapter-required` 或 `not-recommended`，不要静默替换成 `DeepONet`、普通 `UNet`、临时 FNO、MLP 或其它更容易手写的模型。

正式训练对比必须复用 OneScience 中已有模型实现。允许新增 datapipe、adapter、view、runner、config、loss、metrics，但不要在训练脚本内现场定义替代模型主体。

## 下探原则

- 需要代码实现时，交给 `onescience-coder`
- CFD 任务交给 coder 时，只下发 `onescience-coder/assets/` 下的模型卡、数据卡和组件契约
- 当 assets 信息不足时，让 coder 根据资产卡片里的源码锚点读取 `onescience/` 源码或 `examples/cfd/` 案例
- 不要把 `onescience-coder/references/workflow.md` 或 `onescience-coder/references/new_dataset_workflow.md` 作为 CFD 任务下发目标
- 当前若只是验证路由是否正确，可停留在“任务桶识别 + 交接摘要”层级

## 本层应读取的资料

默认先读取：

- `skills/onescience-role/cfd/boundary_contract.md`

再按任务桶细分需要读取：

- `skills/onescience-role/cfd/task_map.md`

必要时回退：

- `skills/onescience-role/references/role_matrix.md`

## 一个标准例子

如果请求是“我有一个新的翼型数据集，README 位于某路径，我想在不同 PDE 模型上训练并对比效果”，则本层应：

1. 归类为 `cfd_task_type=cfd-model-benchmark-comparison`
2. 同时标记 `new_dataset_stage=full-adaptation + benchmark-comparison`
3. 指定 coder 先读取 `assets/datapipes/datapipe_index.md`、`assets/models/model_index.md` 和 `assets/contracts/component_index.md`
4. 默认候选模型先考虑 `Transolver`、`FNO`、`U_Net (CFD_Benchmark)`、`LSM`
5. 若 README 未声明字段名、shape 或 split，先要求 coder 生成只读探测方案，再生成训练代码
6. 明确交接 `model_reuse_policy=use_onescience_models_only` 与 `forbid_local_model_definitions=true`
