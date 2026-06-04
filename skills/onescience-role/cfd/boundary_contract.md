# CFD Role Boundary Contract

本文件用于约束 `onescience-role` 在 CFD 领域任务中的职责边界，并定义它向 `onescience-coder` 下探时应整理的交接内容。

这里默认上游入口已经完成了顶层任务识别，并把当前请求下探到了 `onescience-role`。本文件不重复解释上游入口如何工作，只约束 CFD 领域的 `role` 层该做什么、不该做什么。

## Role 层的定位

当任务已经进入 CFD 领域的 `role` 层时，这一层只负责三件事：

1. 把当前请求归入合适的 CFD 任务桶。
2. 把数据接口、模型协议、训练流程和评估目标之间的兼容性决策整理成摘要。
3. 把后续实现所需的 `onescience-coder/assets/` 目标交给 coder。

## Role 层回答的问题

- 当前 CFD 任务属于哪一类
- 这个任务现阶段优先拆哪一步
- 是已有 datapipe 适配，还是新数据接口构建
- 是单模型适配，还是多模型 benchmark 对比
- 数据协议与目标模型是否可能直接兼容
- 若不能直接兼容，最小桥接应放在 datapipe、adapter、config 还是调用层
- 后续应让 coder 先参考哪些 `assets` 卡片
- 当前是否只做路由验证，还是允许进入实现准备

## Role 层不回答的问题

- 不重新判断顶层工作流入口
- 不重新做领域识别
- 不直接决定具体修改哪几行源码
- 不直接产出 datapipe / model / train / inference 代码
- 不展开到函数内部、张量重排、参数默认值等实现细节
- 不把 CFD 任务下发到 `onescience-coder/references/` 中的通用流程文档

## Role 层的输入假设

进入本层时，默认已经具备最小上游摘要。即使字段名不完全一致，也至少应能从上下文中识别出：

- 用户当前要完成的目标
- 当前任务已经被识别为 `cfd`
- 这是偏数据、模型、训练、推理、评估还是全流程的请求
- 当前阶段是否只验证路由，不进入代码生成

如果这些最小信息仍不足以进行 CFD 任务拆解，`role` 层应只补最小必要判断，不要退回去重复做完整入口分析。

## Role 层的核心产物

`onescience-role` 在 CFD 领域至少应产出这些内容，再交给 `onescience-coder`：

- `cfd_task_type`
- `current_role`
- `role_chain`
- `stage_goal`
- `handoff_artifacts`
- `coder_reference_mode=assets_only`
- `coder_reference_targets`
- `default_benchmark_models`
- `model_reuse_policy`
- 是否允许进入代码生成

## `cfd_task_type` 的职责边界

下面这些判断属于 CFD `role` 层：

- 这是“已有 CFD 数据接入”还是“新数据接口构建”
- 这是“单模型适配”还是“多模型 benchmark 对比”
- 这是“规则网格算子任务”还是“非结构点云 / 图网络任务”
- 这是“普通训练评估”还是“rollout 稳定性评估”
- 这是单阶段任务，还是需要拆成多阶段串联

下面这些判断不属于 CFD `role` 层，而属于 `coder`：

- 应具体读取哪一个源码函数实现
- 应具体修改哪个 `train.py`、`inference.py` 或 `config.yaml`
- 应如何实现 `Dataset.__getitem__`
- 应如何实现 collate、adapter、loss、metrics 或 rollout 循环

## CFD 下发 Coder 的资产模式

CFD 任务默认使用 `assets_only` 模式。

允许下发：

- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- `skills/onescience-coder/assets/models/model_index.md`
- `skills/onescience-coder/assets/contracts/component_index.md`
- `skills/onescience-coder/assets/datapipes/*.md`
- `skills/onescience-coder/assets/models/*.md`
- `skills/onescience-coder/assets/contracts/*.md`

禁止作为 CFD 任务的默认下发目标：

- `skills/onescience-coder/references/workflow.md`
- `skills/onescience-coder/references/new_dataset_workflow.md`
- 其它 `skills/onescience-coder/references/*.md` 通用流程文档

如果资产卡片信息不足，role 应要求 coder 沿资产卡片中的源码锚点继续读 `onescience/` 源码或 `examples/cfd/` 案例，而不是回到 coder references。

## CFD 模型来源消歧

CFD role 层下发 benchmark / 多模型对比任务时，必须先消解同名模型和来源差异：

- `CFD_Benchmark` 目录里存在若干与主库其它目录同名但不同实现的模型，尤其是 `Transolver` 和 `MeshGraphNet`，不要混用。
- 新数据集接入，特别是 benchmark / 多模型对比案例，默认模型实现来源优先使用 `onescience.models.cfd_benchmark`。
- `pdenneval` 只能作为 PDEBench 数据接口或 PDENNEval 专属示例路线参考，不要把默认 benchmark 模型导入到 `onescience.models.pdenneval.*` 下。
- 结构网格或 `(x, fx)` operator view 并不排斥 Transolver；这种场景应使用 `Transolver (CFD_Benchmark)`，不要因为不是 PyG `Data` 就把 Transolver 标记为不兼容。

默认 benchmark 模型来源表：

| 默认模型 | 正确模型来源 | 推荐实例化方式 | 不要使用 |
| --- | --- | --- | --- |
| `FNO` | `onescience.models.cfd_benchmark.FNO` | `FNO.Model(args, device)` | `model_factory.get_model`、`onescience.models.pdenneval.fno.FNO*d`，除非明确复现原仓库 runner 或 PDENNEval/FNO 示例 |
| `U_Net (CFD_Benchmark)` | `onescience.models.cfd_benchmark.U_Net` | `U_Net.Model(args, device)` | `model_factory.get_model`、`onescience.models.pdenneval.unet.UNet*d`，除非明确复现原仓库 runner 或 PDENNEval/UNet 示例 |
| `LSM` | `onescience.models.cfd_benchmark.LSM` | `LSM.Model(args, device)` | `model_factory.get_model`、`onescience.models.pdenneval.lsm`、`LSM1d`、`LSM2d`、`LSM3d` |
| `Transolver (CFD_Benchmark)` | `onescience.models.cfd_benchmark.Transolver` | `Transolver.Model(args, device)` | `model_factory.get_model`、直接吃 PyG `Data` 的 `Transolver2D/3D`，除非当前 adapter 明确走 PyG 点级协议 |

补充说明：

- `pdenneval` 目录下确实有 FNO / UNet / UNO / PINO / DeepONet 等 PDENNEval 专属模型，但它不是默认 CFD benchmark 模型来源。
- `LSM` 不存在 `pdenneval` 版本，也不存在 `LSM2d` 类；正式对比时必须读取 `lsm.md` 并使用 `cfd_benchmark/LSM.py`。
- 数据接口可以参考 `pdenneval.md`，但模型导入必须以命中的模型卡为准。
- 新数据集 benchmark 训练脚本默认不要调用 `onescience.models.cfd_benchmark.model_factory.get_model`；除非用户明确要求复刻 `examples/cfd/CFD_Benchmark` 原 runner，否则应直接导入目标模型模块。
- 模型参数默认写入 YAML 配置文件，训练脚本读取 YAML 后转为 `args` 对象，再传给 `Model(args, device)`，不要把模型超参数散落硬编码在训练脚本里。

## CFD Benchmark 默认模型约束

当用户要求“在不同 PDE / CFD / operator 模型上训练并对比效果”，且没有明确指定模型列表时，默认候选必须是：

- `Transolver`
- `FNO`
- `U_Net (CFD_Benchmark)`
- `LSM`

默认候选中的 `Transolver` 必须按数据协议分流：

- PyG 点级协议：读取 `Transolver`
- 结构网格、规则网格、`(x, fx)` operator view 或 `CFD_Benchmark` 风格 batch：读取 `Transolver (CFD_Benchmark)`
- 不要因为当前数据是结构网格就把 Transolver 标记为 `not-recommended`

默认候选只是候选，不代表一定都能生成可运行训练代码。role 层必须要求 coder 先给出每个模型的兼容状态：

- `direct`
- `adapter-required`
- `not-recommended`

如果某个默认候选和数据协议不兼容，应标记为 `adapter-required` 或 `not-recommended`，不要静默替换成 `DeepONet`、普通 `UNet`、MLP、临时 FNO 或其它自写模型。

只有在用户明确指定、上游交接摘要明确追加，或默认候选全部不适合且已经说明原因时，才允许把 `DeepONet`、`U_FNO`、`U_NO`、`PointNet`、`MeshGraphNet` 等模型作为追加候选。

## OneScience 模型复用约束

CFD role 下发给 coder 时，必须把模型复用写成硬边界：

- 已有模型卡覆盖的模型，必须使用 OneScience 中的真实实现
- 训练脚本不得现场定义替代模型主体
- 允许新增 adapter / view / collate / config / runner 来桥接数据协议
- 不允许用自写 `FNO1D`、`SimpleUNet`、临时 `DeepONet` 或 MLP baseline 替代已登记模型
- 如果模型无法适配，应跳过或标记 `not-recommended`，而不是换成一个更容易手写的模型
- `Transolver`、`Transolver (CFD_Benchmark)`、`FNO`、`U_Net (CFD_Benchmark)`、`LSM` 都已经有 OneScience 模型卡和源码锚点，正式训练对比必须导入并实例化这些真实模型。
- 新数据集 benchmark 代码应直接使用 `from onescience.models.cfd_benchmark import FNO, U_Net, LSM, Transolver` 这类模块导入方式，再调用对应模块的 `Model(args, device)`。
- 默认不要使用 `from onescience.models.cfd_benchmark.model_factory import get_model`；这个工厂函数只适合复刻原 `CFD_Benchmark` runner，不适合作为新 case 的默认生成方式。
- 每个模型的参数应保存在 YAML 中，例如 `configs/fno.yaml`、`configs/u_net.yaml`、`configs/lsm.yaml`、`configs/transolver.yaml`，训练脚本读取后生成 `args` 对象。
- 只有用户明确要求“写一个临时 baseline / toy model / 从零实现模型”时，才允许在 case 脚本中定义新模型，并且必须明确标记它不是 OneScience 已登记模型。

## 数据与接口兼容性原则

当任务要求“沿用某个 datapipe、example 或训练流程”，去适配另一套 CFD 数据或模型时，先做兼容性判断，不要默认它们可以直接互通。

交接摘要中至少要检查：

- 样本返回格式是否兼容
- `DataLoader` 的 batch 结构是否兼容
- 训练脚本的 batch 解包方式是否兼容
- 模型期望的输入输出协议是否兼容
- 配置文件里的关键字段是否能直接复用
- loss、metrics、inference 是否与目标变量一致

如果不能直接兼容，必须明确写出：

- 当前不兼容的原因
- 最小可行桥接路径
- 计划在 datapipe、adapter、配置层还是调用层做适配

默认优先最小改动路径：

- 先保持现有模型主体不变
- 先保持现有训练主循环不变
- 优先在 datapipe、adapter、配置或调用层完成桥接

## 新数据集安全规则

当用户提供的是尚未登记的新 CFD 数据集时，role 层必须要求 coder 先判断 README 是否足够支撑实现。

如果 README 没有明确字段名、shape、split、单位或目标变量：

- 不要默认假设字段名，例如不要把压力系数 `cp` 假设成 `p`
- 先要求生成只读探测脚本或探测方案
- 探测目标至少包括文件列表、样本数、字段名、数组 shape、缺失字段、异常文件和 split 规则
- 探测脚本不得改写、移动或删除原始数据

如果数据格式可能存在损坏文件或不一致字段，例如 VTK / mesh surface 数据：

- datapipe 设计中应保留跳过损坏文件的鲁棒逻辑
- 建议保留 `strict` / `skip_bad_files` / `required_fields` 这类配置
- target schema 应在初始化或探测阶段确定，不要让不同样本返回不同 target 维度
- 对缺失字段的文件，应在跳过、填充默认值或降级目标变量之间显式选择，不要隐式改变目标维度
- 输出 bad file / missing field 摘要，便于用户后续清洗数据

## 新 datapipe 命名规则

生成新 datapipe 时，默认遵守：

- 文件名：`<DatasetName>.py`
- 数据集类：`<DatasetName>Dataset`
- 数据管道类：`<DatasetName>Datapipe`

如果用户没有明确要求改主库，默认把新 datapipe 与相关训练文件生成到目标 case 目录，而不是直接修改 `onescience/src/`。

## 给 Coder 的交接要求

当 CFD `role` 层把任务继续下探到 `onescience-coder` 时，交接内容至少要表达清楚：

1. 当前任务属于哪个 CFD 任务桶
2. 当前阶段的唯一主目标是什么
3. 当前是否允许进入代码生成
4. 当前是否为 `assets_only` 模式
5. 应先查看哪些 `assets` 卡片
6. 需要优先保持不变的边界是什么
7. 是否需要先做字段 / shape / 文件健康度探测
8. 如果是多模型任务，每个模型的兼容状态是什么
9. 如果是 CFD benchmark 任务，默认模型是否仍为 `Transolver / FNO / U_Net (CFD_Benchmark) / LSM`
10. 是否明确禁止在训练脚本内现场定义替代模型主体

## 路由验证模式

当当前阶段只验证索引路线是否正确时，CFD `role` 层应遵守：

1. 正常完成 CFD 任务桶识别。
2. 正常给出后续应参考的 `assets` 资料。
3. 明确标记“当前只验证路线，不进入代码生成”。

此时即使继续下探到 `coder`，也只要求 `coder` 返回“将读取哪些资产卡片”和“最小实现路径”，不要求产出代码。
