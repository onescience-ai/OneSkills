# Earth Role Boundary Contract

本文件用于约束 `onescience-role` 在 Earth 领域任务中的职责边界，并定义它向 `onescience-coder` 下探时应整理的交接内容。

这里默认上游入口已经完成了顶层任务识别，并把当前请求下探到了 `onescience-role`。本文件不重复解释上游入口如何工作，只约束 Earth 领域的 `role` 层该做什么、不该做什么。

## Role 层的定位

当任务已经进入 Earth 领域的 `role` 层时，这一层只负责两件事：

1. 把当前请求归入合适的 Earth 任务桶。
2. 把领域决策整理成可交给 `onescience-coder` 的交接摘要。

## Role 层回答的问题

- 当前 Earth 任务属于哪一类
- 这个任务现阶段优先拆哪一步
- 需要哪些交接物才能继续下探
- 后续应让 `coder` 先参考哪一类实现资料
- 当前是否只是规划阶段，还是允许进入实现准备

## Role 层不回答的问题

- 不重新判断顶层工作流入口
- 不重新做领域识别
- 不直接决定具体修改哪几行源码
- 不直接产出 datapipe / model / train / inference 代码
- 不展开到函数、张量 shape、参数默认值等实现细节

## Role 层的输入假设

进入本层时，默认已经具备最小上游摘要。即使字段名不完全一致，也至少应能从上下文中识别出：

- 用户当前要完成的目标
- 当前任务已经被识别为 `earth`
- 这是偏数据、模型、训练、推理还是全流程的请求
- 当前阶段是否只做规划，不进入代码生成

如果这些最小信息仍不足以进行 Earth 任务拆解，`role` 层应只补最小必要判断，不要退回去重复做完整入口分析。

## Role 层的核心产物

`onescience-role` 在 Earth 领域至少应产出这些内容，再交给 `onescience-coder`：

- `earth_task_type`
- `current_role`
- `role_chain`
- `stage_goal`
- `handoff_artifacts`
- `coder_reference_targets`
- 是否允许进入代码生成

## `earth_task_type` 的职责边界

下面这些判断属于 Earth `role` 层：

- 这是“已有 Earth 数据接入”还是“新数据接口构建”
- 这是“模型结构改造”还是“训练流程构建”
- 这是“普通推理”还是“官方权重推理对照”
- 这是单阶段任务，还是需要拆成多阶段串联

下面这些判断不属于 Earth `role` 层，而属于 `coder`：

- 应先读哪一个 `train.py`
- 应先读哪一个 `inference.py`
- 应先读哪一个 `config.yaml`
- 应优先看 `assets/models/`、`assets/contracts/` 还是 `assets/datapipes/`

## Role 层应参考的本地资料

优先读取：

- `skills/onescience-role/earth/task_map.md`

必要时回退通用角色补充：

- `skills/onescience-role/references/role_matrix.md`

## 给 Coder 的交接要求

当 Earth `role` 层把任务继续下探到 `onescience-coder` 时，交接内容至少要表达清楚：

1. 当前任务属于哪个 Earth 任务桶
2. 当前阶段的唯一主目标是什么
3. 需要优先保持不变的边界是什么
4. 应先查看哪一类 example 或 asset
5. 当前是否禁止直接进入代码生成

## 规划阶段

当当前阶段只做路线规划、任务拆解或尚未授权实现时，Earth `role` 层应遵守：

1. 正常完成 Earth 任务桶识别。
2. 正常给出后续应参考的资料类型。
3. 明确标记“当前只做规划，不进入代码生成”。

此时即使继续下探到 `coder`，也只要求 `coder` 返回“将读取哪些参考”和“最小实现路径”，不要求产出代码。

## 一条标准下探方式

以“新数据接口构建，参考 `TJ-Data`”为例，Earth `role` 层应完成的是：

1. 把任务归类为 `earth_task_type=new-data-interface-construction`
2. 判断当前阶段主目标是先形成数据读取与接口约定
3. 交接给 `coder`：
   - 先看 `examples/earth/TJ-Data/`
   - 再看 `onescience-coder/references/new_dataset_workflow.md`
   - 再选最接近的 Earth example 训练入口
4. 若当前是规划阶段，明确禁止继续生成实现代码
