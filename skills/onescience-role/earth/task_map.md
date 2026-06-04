# Earth Task Map

本文件用于整理 `earth` 领域当前已经具备的样例资产，并把常见任务归入稳定的任务桶，供 `onescience-role` 做领域决策时使用。

## 使用原则

1. 本文件只做任务识别、任务拆解和参考入口归类，不直接承担代码实现。
2. 这里的 `reference examples` 用于告诉 `role` 后续应把任务交给哪类 `coder` 参考，而不是要求 `role` 直接展开代码细节。
3. 若用户只是要求规划路线或尚未授权实现，可以停留在“识别任务桶 + 指向后续 skill / reference”的层级，不进入代码生成。

## 当前已梳理的核心 Earth Example

这些目录可视为当前 `earth` 领域最稳定的主参考：

- `fengwu`
- `fourcastnet`
- `fuxi`
- `graphcast`
- `pangu_weather`
- `xihe`

这些目录可视为补充或专项参考：

- `TJ-Data`
- `corrdiff`
- `era5_dataset_prepare`
- `graphcast_jax`
- `nowcastnet`
- `oceancast`

## 任务桶

### 1. 已有 Earth 数据流复用与适配

适用信号：

- “接入已有 Earth 数据”
- “复用现有数据读取流程”
- “沿用某个 example 的数据接口”

角色层关注点：

- 当前是直接复用，还是只做轻量接口适配
- 数据对象属于哪一类 Earth 数据
- 是否已经存在可沿用的训练或推理流程

阶段目标：

- 明确当前复用哪条已有 Earth 数据流，以及最小适配边界

建议交接物：

- 当前数据对象与来源
- 目标任务使用的数据变量、时间范围、空间范围
- 计划复用的 example 或 datapipe 类型
- 需要保持兼容的训练或推理入口

下游去向：

- 默认交给 `onescience-coder`

运行约束：

- 无固定运行约束；若后续涉及服务器运行，只保留与数据路径相关的必要事实

后续 coder 参考入口：

- `onescience-coder/assets/datapipes/`
- `onescience-coder/references/new_dataset_workflow.md`
- `examples/earth/*/conf/config.yaml`
- `examples/earth/*/train.py`

### 2. 新数据接口构建

适用信号：

- “新增一套 Earth 数据接口”
- “把新数据做成 datapipe / dataset”
- “先完成读取，再接训练或推理”

角色层关注点：

- 当前是 `datapipe-only`，还是后续还要接训练 / 推理
- 数据组织方式、变量口径、样本切分是否已明确
- 是否需要先形成最小读取与配置样例

阶段目标：

- 先形成一套最小可交接的数据读取与接口约定

建议交接物：

- 数据目录结构或样本组织方式
- 输入变量、输出变量、标签口径
- 划分方式：训练 / 验证 / 推理
- 当前是 `datapipe-only` 还是后续还要接训练 / 推理
- 参考入口：`TJ-Data` 或其它相近 example

下游去向：

- 默认交给 `onescience-coder`

运行约束：

- 无固定运行约束；若数据生成或预处理依赖远程环境，只保留执行前置条件，不在本层展开

主参考：

- `examples/earth/TJ-Data/data_read.py`
- `examples/earth/TJ-Data/conf/config.yaml`
- `examples/earth/TJ-Data/tmp_data_generation.py`

后续 coder 参考入口：

- `onescience-coder/references/new_dataset_workflow.md`
- `onescience-coder/assets/datapipes/`
- 与目标最接近的 `examples/earth/*/train.py`

### 3. Earth 模型构建与结构改造

适用信号：

- “复用现有 Earth 模型做改造”
- “替换或新增关键模块”
- “构建新的 Earth 预测模型”

角色层关注点：

- 当前是复用已有模型，还是从现有资产组合出新结构
- 需求重点在模型主干、输入输出协议，还是组件替换
- 是否必须和某个已有流程保持兼容

阶段目标：

- 明确模型改造范围，以及必须保持兼容的输入输出协议

建议交接物：

- 目标模型类型或参考模型
- 当前要改的是主干、头部、嵌入、融合还是整体结构
- 输入输出变量组织
- 必须兼容的训练、推理或数据接口
- 预期最小改动边界

下游去向：

- 默认交给 `onescience-coder`

运行约束：

- 无固定运行约束；若后续要进远程训练，只保留模型入口与资源规模提示

后续 coder 参考入口：

- `onescience-coder/assets/models/`
- `onescience-coder/assets/contracts/`
- `examples/earth/fengwu/`
- `examples/earth/fourcastnet/`
- `examples/earth/fuxi/`
- `examples/earth/graphcast/`
- `examples/earth/pangu_weather/`
- `examples/earth/xihe/`

### 4. Earth 训练流程构建

适用信号：

- “构建训练流程”
- “补训练入口 / runner / config”
- “把模型和数据串成训练闭环”

角色层关注点：

- 当前是已有模型接现有训练流程，还是数据与模型一起落成训练闭环
- 训练入口、配置文件、样本组织是否已明确
- 是否只需要最小训练链路，还是要兼顾后续运行链路
- 若后续要上服务器运行，是否需要给 `runtime` 保留提交与诊断约束

阶段目标：

- 形成最小可运行的训练链路定义，而不是直接展开远程提交细节

建议交接物：

- 目标训练入口
- 计划复用的配置结构
- 样本 batch 组织与输入输出协议
- 单阶段训练还是多阶段训练
- 若后续进入运行层，需要保留的资源规模或提交约束

下游去向：

- 代码链路交给 `onescience-coder`
- 仅当后续明确要求服务器运行时，再把运行约束保留给 `onescience-runtime`

运行约束：

- 可保留训练入口、资源规模、日志位置等约束
- 不在本层展开 `SLURM` 提交脚本实现

后续 coder 参考入口：

- `examples/earth/fengwu/train.py`
- `examples/earth/fourcastnet/train.py`
- `examples/earth/fuxi/train_base.py`
- `examples/earth/fuxi/train_short.py`
- `examples/earth/fuxi/train_medium.py`
- `examples/earth/fuxi/train_long.py`
- `examples/earth/graphcast/train.py`
- `examples/earth/pangu_weather/train.py`
- `examples/earth/pangu_weather/train_mvp.py`
- `examples/earth/pangu_weather/train_pangu_reconstructed.py`
- `examples/earth/xihe/train.py`

### 5. Earth 推理流程构建

适用信号：

- “补推理入口”
- “做预测 / rollout / 结果导出”
- “在已有模型或已有权重上跑 inference”

角色层关注点：

- 当前是普通推理，还是需要参考外部基线
- 是否只需要本地推理入口，还是后续要接运行链路
- 输出产物属于预测结果、评估结果还是其它分析产物
- 若后续要上服务器运行，是否需要给 `runtime` 保留提交与诊断约束

阶段目标：

- 明确推理入口、输入输出产物和是否需要与现有流程保持一致

建议交接物：

- 目标推理入口
- 输入数据形式与输出产物形式
- 是单步推理、长时 rollout，还是结果导出
- 是否需要复用已有权重、配置或结果脚本
- 若后续进入运行层，需要保留的资源规模或提交约束

下游去向：

- 代码链路交给 `onescience-coder`
- 仅当后续明确要求服务器运行时，再把运行约束保留给 `onescience-runtime`

运行约束：

- 可保留推理入口、日志位置、资源规模等约束
- 不在本层展开 `SLURM` 提交脚本实现

后续 coder 参考入口：

- `examples/earth/fengwu/inference.py`
- `examples/earth/fourcastnet/inference.py`
- `examples/earth/fuxi/inference.py`
- `examples/earth/graphcast/inference.py`
- `examples/earth/pangu_weather/inference.py`
- `examples/earth/xihe/inference.py`

### 6. 外部参考推理对照

适用信号：

- “参考外部权重做推理”
- “做外部结果对照”
- “保留对照推理链路”

角色层关注点：

- 当前是否明确指定模型或对照来源
- 是仅做外部推理链路，还是要与 OneScience 流程对齐
- 是否需要保留对照脚本或下载脚本

阶段目标：

- 明确外部参考链路与 OneScience 本地链路之间的对照关系

建议交接物：

- 指定模型或外部参考来源
- 当前是只做外部推理，还是要做结果对照
- 需要保留的下载、推理或比较脚本
- 与本地推理入口之间的对应关系

下游去向：

- 默认交给 `onescience-coder`

运行约束：

- 若外部参考推理后续要进远程运行，只保留必要入口和资源事实

主参考：

- `examples/earth/pangu_weather/official_compare/infer.py`
- `examples/earth/pangu_weather/official_compare/compare.py`
- `examples/earth/pangu_weather/official_compare/model_weight_download.sh`
- `examples/earth/graphcast_jax/inference.py`

后续 coder 参考入口：

- 对应模型的 `inference.py`
- 对应模型的官方对照目录

### 7. Earth 多阶段流程串联

适用信号：

- “把多个阶段串成完整流程”
- “从数据到训练 / 推理串起来”
- “做一个 Earth 领域完整闭环”

角色层关注点：

- 当前是从已有 example 演化，还是从新数据接口起步
- 是否应先拆成多个阶段，再逐步下探
- 需要哪些阶段性交接物，避免 coder 一次性承担整个闭环

阶段目标：

- 先把完整 Earth 流程拆成可依次下探的多个阶段

建议交接物：

- 当前完整目标
- 阶段拆分顺序：数据、模型、训练、推理、对照或运行
- 每个阶段的唯一主目标
- 阶段之间必须传递的交接物
- 哪些阶段只做规划，哪些阶段允许进入实现

下游去向：

- 先由 `onescience-role` 完成分阶段规划
- 再按阶段分别交给 `onescience-coder`

运行约束：

- 若后续涉及服务器运行，只在对应阶段保留运行约束，不把整条链路一次性下发给运行层

后续 coder 参考入口：

- 先按前 6 个任务桶拆分，再分别交给对应参考

## 运行交接提示

当 Earth 任务后续需要在服务器端通过 `SLURM` 提交时，`role` 层只负责保留运行约束，不负责展开提交脚本实现。

此时应把以下信息交给后续运行相关层：

- 对应的训练或推理入口
- 资源规格是否有固定约束
- 是否已有可参考的 `SLURM` 提交样式
- 是否需要保留日志输出位置和分布式启动方式

当前 Earth 领域的案例提交脚本可参考：

- `examples/earth/pangu_weather/work_slurm.sh`

这里的作用只是告诉后续 `onescience-runtime` 存在一个可参考的提交样式，不把它作为 `coder` 的主参考路线。

## Earth 任务到后续路线

- `已有 Earth 数据流复用与适配` -> `onescience-role` 规划后交给 `onescience-coder`
- `新数据接口构建` -> `onescience-role` 规划后交给 `onescience-coder`
- `Earth 模型构建与结构改造` -> `onescience-role` 规划后交给 `onescience-coder`
- `Earth 训练流程构建` -> `onescience-role` 规划后交给 `onescience-coder`
- `Earth 推理流程构建` -> `onescience-role` 规划后交给 `onescience-coder`
- `外部参考推理对照` -> `onescience-role` 规划后交给 `onescience-coder`
- `Earth 多阶段流程串联` -> `onescience-role` 先拆阶段，再按阶段交给 `onescience-coder`

## 规划阶段建议

当当前阶段只规划技能路线时，优先按以下类型理解请求，不要求 `coder` 继续产出代码：

- “我想复用一套 Earth 数据流程，但先只判断应该走哪条技能链”
- “我想新建一个 Earth 数据接口，参考 TJ-Data，先别写代码，只告诉我你会调用哪些技能”
- “我想基于现有 Earth 模型构建训练流程，先不要生成代码，只看你如何路由”
- “我想做外部权重推理对照，先只判断应该读取哪些参考”
