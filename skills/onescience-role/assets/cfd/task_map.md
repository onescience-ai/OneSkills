# CFD Task Map

本文件用于整理 `cfd` 领域当前已经具备的样例资产，并把常见任务归入稳定的任务桶，供 `onescience-role` 做领域决策时使用。

## 使用原则

1. 本文件只做任务识别、任务拆解和资产入口归类，不直接承担代码实现。
2. CFD 任务下发 coder 时默认使用 `assets_only` 模式。
3. 这里的 `coder asset targets` 用于告诉 `role` 后续应把任务交给 coder 参考哪些资产卡片，而不是要求 `role` 直接展开代码细节。
4. 若用户只是要求验证路由是否正确，可以停留在“识别任务桶 + 指向后续 assets”的层级，不进入代码生成。

## 当前核心 CFD Example

这些目录可视为当前 `cfd` 领域最常见的主参考：

- `examples/cfd/Transolver-Airfoil-Design`
- `examples/cfd/Transolver-Car-Design`
- `examples/cfd/Vortex_shedding_mgn`
- `examples/cfd/DeepCFD`
- `examples/cfd/CFD_Benchmark`
- `examples/cfd/CFDBench`
- `examples/cfd/PDENNEval`
- `examples/cfd/Lagrangian_MGN`

这些目录可视为补充或专项参考：

- `examples/cfd/BENO`
- `examples/cfd/EagleMeshTransformer`
- `examples/cfd/GP_for_TO`
- `examples/cfd/PINNsformer`

## 当前核心 CFD Assets

数据接口资产优先入口：

- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- `skills/onescience-coder/assets/datapipes/airfrans.md`
- `skills/onescience-coder/assets/datapipes/shapenetcar.md`
- `skills/onescience-coder/assets/datapipes/deepcfd.md`
- `skills/onescience-coder/assets/datapipes/cfdbench.md`
- `skills/onescience-coder/assets/datapipes/pdenneval.md`
- `skills/onescience-coder/assets/datapipes/deepmind_cylinderflow.md`
- `skills/onescience-coder/assets/datapipes/deepmind_lagrangian.md`
- `skills/onescience-coder/assets/datapipes/eagle.md`
- `skills/onescience-coder/assets/datapipes/beno.md`
- `skills/onescience-coder/assets/datapipes/drivaerml_figconvunet.md`

模型资产优先入口：

- `skills/onescience-coder/assets/models/model_index.md`
- `skills/onescience-coder/assets/models/cfd_benchmark_args.md`
- `skills/onescience-coder/assets/models/transolver.md`
- `skills/onescience-coder/assets/models/transolver_benchmark.md`
- `skills/onescience-coder/assets/models/fno.md`
- `skills/onescience-coder/assets/models/u_net_operator.md`
- `skills/onescience-coder/assets/models/lsm.md`
- `skills/onescience-coder/assets/models/meshgraphnet.md`
- `skills/onescience-coder/assets/models/meshgraphnet_benchmark.md`
- `skills/onescience-coder/assets/models/u_fno.md`
- `skills/onescience-coder/assets/models/u_no.md`
- `skills/onescience-coder/assets/models/f_fno.md`
- `skills/onescience-coder/assets/models/deeponet.md`
- `skills/onescience-coder/assets/models/graphsage.md`
- `skills/onescience-coder/assets/models/graph_unet.md`
- `skills/onescience-coder/assets/models/pointnet.md`
- `skills/onescience-coder/assets/models/regdgcnn.md`

CFD_Benchmark args 入口：

- 生成或改写 `onescience.models.cfd_benchmark` 相关训练配置、YAML、benchmark runner 前，必须把 `skills/onescience-coder/assets/models/cfd_benchmark_args.md` 作为优先资产。
- 该资产集中覆盖当前 `./onescience/src/onescience/models/cfd_benchmark` 下全部模型的 `args.xxx` 字段，避免只读单个模型卡时漏掉 `shapelist`、`fun_dim`、`out_dim`、`slice_num`、`modes` 等参数。
- 这是配置生成契约，不要求 coder 在训练脚本里加入强制运行时校验；优先把完整参数写入 YAML，再传给 `Model(args, device)`。

CFD_Benchmark 里当前已覆盖的模型：

- `DeepONet`
- `Factformer`
- `FNO`
- `F_FNO`
- `Galerkin_Transformer`
- `GFNO`
- `GNOT`
- `GraphSAGE`
- `Graph_UNet`
- `LSM`
- `MeshGraphNet (CFD_Benchmark)`
- `MWT`
- `ONO`
- `PointNet`
- `RegDGCNN`
- `Swin_Transformer`
- `Transformer`
- `Transolver (CFD_Benchmark)`
- `U_FNO`
- `U_Net (CFD_Benchmark)`
- `U_NO`

组件契约资产优先入口：

- `skills/onescience-coder/assets/contracts/component_index.md`
- `skills/onescience-coder/assets/contracts/onefourier.md`
- `skills/onescience-coder/assets/contracts/onemlp.md`
- `skills/onescience-coder/assets/contracts/onehead.md`
- `skills/onescience-coder/assets/contracts/oneencoder.md`
- `skills/onescience-coder/assets/contracts/onedecoder.md`
- `skills/onescience-coder/assets/contracts/oneattention.md`
- `skills/onescience-coder/assets/contracts/onetransformer.md`
- `skills/onescience-coder/assets/contracts/oneedge.md`
- `skills/onescience-coder/assets/contracts/onenode.md`
- `skills/onescience-coder/assets/contracts/oneprocessor.md`
- `skills/onescience-coder/assets/contracts/onepooling.md`
- `skills/onescience-coder/assets/contracts/oneequivariant.md`

## 任务桶

### 1. 已有 CFD 数据流复用与适配

适用信号：

- “使用 DeepCFD / AirfRANS / CFDBench / PDEBench 数据接口”
- “复用现有 CFD datapipe”
- “沿用某个 CFD example 的数据读取流程”

角色层关注点：

- 当前是直接复用，还是只做轻量接口适配
- 样本返回协议是 `dict`、`(x, fx)`、PyG `Data`、DGL `Graph` 还是其它结构
- 目标模型是否能直接消费该 batch 协议
- 是否需要 adapter / collate / reshape / interpolation

后续 coder asset targets：

- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- 对应 datapipe 卡片
- `skills/onescience-coder/assets/models/model_index.md`
- 目标模型卡片

### 2. 新 CFD 数据接口构建

适用信号：

- “我有一个新的 CFD 数据集”
- “README 位于某路径”
- “一批 VTK / mesh / HDF5 / npy / pickle / Tecplot / CSV 流场文件”
- “先帮我完成数据集接口”

角色层关注点：

- 当前是 `datapipe-only`、`full-adaptation` 还是 `full-adaptation + benchmark-comparison`
- 数据形态是规则网格、非结构点云、PyG 图、DGL 图、VTK / surface mesh、HDF5 / PDEBench 风格还是未知
- README 是否明确写出字段名、shape、split、单位、输入变量和目标变量
- 若 README 不完整，是否需要先做只读探测
- 新 datapipe 是 `case-local` 还是主库集成
- 是否需要 canonical datapipe 之外的模型 view / adapter

数据探测要求：

- README 未声明字段名时，不要猜测 `p`、`cp`、`pressure`、`velocity` 等字段
- README 未声明 shape 时，不要猜测网格维度、节点数或 target 通道数
- 对 VTK / mesh 文件，先探测 point data、cell data、字段名、节点数、单元数、异常文件和缺失字段
- 对 HDF5 / npy / pickle 文件，先探测 key、array shape、dtype、样本数量和 split
- 探测脚本必须只读，不得改写原始数据

鲁棒性要求：

- 对损坏文件、格式不支持文件或字段缺失文件，datapipe 应支持跳过或显式报错
- target schema 应固定，不能让不同样本返回不同 target 维度
- 对缺失字段必须显式选择跳过、填充或降级目标变量
- 需要输出 bad file / missing field 摘要

后续 coder asset targets：

- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- 与数据形态最接近的 datapipe 卡片
- `skills/onescience-coder/assets/models/model_index.md`
- 如涉及模型，读取目标模型卡片
- `skills/onescience-coder/assets/contracts/component_index.md`

### 3. CFD 模型适配

适用信号：

- “接到 Transolver / FNO / U_Net / LSM / MeshGraphNet”
- “沿用某个现有案例训练流程”
- “数据和原案例不完全一致，但想复用模型架构”

角色层关注点：

- 目标模型的数据协议是什么
- 当前 datapipe 是否直接返回模型需要的字段
- 需要改 datapipe、adapter、config、loss、metrics 还是 inference
- 是否能保持模型主体和训练主循环不变
- 若目标模型和数据形态不匹配，是否应标记为 `not-recommended`

后续 coder asset targets：

- `skills/onescience-coder/assets/models/model_index.md`
- 目标模型卡片
- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- 目标数据或参考数据卡片
- `skills/onescience-coder/assets/contracts/component_index.md`

### 4. CFD 多模型 Benchmark 对比

适用信号：

- “在不同 PDE 模型上训练并对比”
- “比较 UNet 和神经算子”
- “比较 Transolver、FNO、U_Net、LSM”
- “用户没指定模型，但希望做 CFD 代理模型效果对比”

角色层关注点：

- 用户是否指定模型
- 若用户未指定模型，默认候选固定为 `Transolver`、`FNO`、`U_Net (CFD_Benchmark)`、`LSM`
- 默认候选里的 `Transolver` 要按协议分流：PyG 点级数据看 `Transolver`，结构网格 / 规则网格 / `(x, fx)` operator view 看 `Transolver (CFD_Benchmark)`
- 默认候选只是起点，最终是否生成训练代码必须由数据协议兼容性决定
- 第一轮应输出模型兼容性表：`direct`、`adapter-required`、`not-recommended`
- 多模型对比优先生成 canonical datapipe，再为不同模型生成 adapter / view
- 不要为了让所有模型都能跑而隐式丢弃目标变量、坐标、边界条件或时间信息
- 不要把默认候选静默替换成 `DeepONet`、普通 `UNet`、临时 FNO、MLP 或其它容易手写的模型
- 如果默认候选不适配，应标记跳过或需要 adapter，不要用自写模型补位

模型实现来源约束：

- `Transolver` 必须来自 OneScience 的 Transolver 模型卡和源码锚点；如果是结构网格或 `(x, fx)` benchmark 协议，必须使用 `Transolver (CFD_Benchmark)` / `cfd_benchmark/Transolver.py`
- `FNO` 必须来自 OneScience 的 `cfd_benchmark/FNO.py`
- `U_Net (CFD_Benchmark)` 必须来自 OneScience 的 `cfd_benchmark/U_Net.py`
- `LSM` 必须来自 OneScience 的 `cfd_benchmark/LSM.py`
- 训练脚本只能新增 adapter / view / runner，不得在脚本内定义替代模型主体
- 新数据集接入，特别是 benchmark 类案例，都要优先去 `cfd_benchmark` 中找默认模型；`pdenneval` 只作为 PDEBench 数据接口或 PDENNEval 专属示例路线，不能推断出 `pdenneval.lsm` 或 `LSM2d`

默认模型选择提示：

- 非结构翼型、表面点云或网格采样：先看 `Transolver`，再判断 `FNO / LSM` 是否可通过 `(x, fx)` view 接入
- 规则网格稳态流场：先看 `Transolver (CFD_Benchmark)`、`FNO`、`U_Net (CFD_Benchmark)`、`LSM`
- PyG 图：先看 `Transolver`、`GraphSAGE`、`Graph_UNet`
- DGL 图或显式 mesh message passing：先看 `MeshGraphNet`
- HDF5 / PDEBench 风格：数据接口先看 `pdenneval.md`，默认 benchmark 模型仍先看 `FNO`、`U_Net (CFD_Benchmark)`、`LSM` 的 `cfd_benchmark` 模型卡；只有明确复现 PDENNEval 示例时才看 `PINO / DeepONet / pdenneval FNO / pdenneval UNet` 相关资产

新 CFD 数据集默认 benchmark 候选：

| 数据形态 | 默认候选 | 追加候选 | 适配提示 |
| --- | --- | --- | --- |
| 非结构翼型 / 点云 / 表面采样 | `Transolver`, `FNO`, `LSM` | `PointNet`, `RegDGCNN` | `FNO / LSM` 通常需要 `(x, fx)` view；规则网格模型需要插值或跳过 |
| 规则网格流场 | `Transolver (CFD_Benchmark)`, `FNO`, `U_Net (CFD_Benchmark)`, `LSM` | `U_FNO`, `U_NO`, `F_FNO`, `MWT` | `Transolver (CFD_Benchmark)` 可走 structured 分支；同时保证 `shapelist / fun_dim / out_dim` 与 datapipe 一致 |
| PyG 图 | `Transolver` | `GraphSAGE`, `Graph_UNet` | 先确认 `Data.pos / Data.x / Data.y / edge_index` 是否齐全 |
| DGL 图 | `MeshGraphNet` | `BiStrideMeshGraphNet` | 先确认 node/edge features、graph 和 rollout 协议 |
| HDF5 / PDEBench 风格 | `Transolver (CFD_Benchmark)`, `FNO`, `U_Net (CFD_Benchmark)`, `LSM` | `DeepONet`, `PINO`, `UNO` | 数据可参考 `pdenneval.md`，但默认 benchmark 模型仍优先走 `cfd_benchmark` 并通过 adapter 对齐 `(x, fx)` |

后续 coder asset targets：

- `skills/onescience-coder/assets/models/model_index.md`
- `skills/onescience-coder/assets/models/cfd_benchmark_args.md`
- `skills/onescience-coder/assets/models/transolver.md`
- `skills/onescience-coder/assets/models/transolver_benchmark.md`
- `skills/onescience-coder/assets/models/fno.md`
- `skills/onescience-coder/assets/models/u_net_operator.md`
- `skills/onescience-coder/assets/models/lsm.md`
- 按兼容性追加其它模型卡
- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- `skills/onescience-coder/assets/contracts/component_index.md`

交接摘要必须包含：

- `default_benchmark_models=[Transolver, FNO, U_Net (CFD_Benchmark), LSM]`
- `transolver_variant=Transolver` 或 `Transolver (CFD_Benchmark)`，由 batch 协议决定
- `model_reuse_policy=use_onescience_models_only`
- `model_instantiation_policy=direct_module_import`
- `model_config_source=yaml`
- `forbid_local_model_definitions=true`
- 每个默认模型的 `direct / adapter-required / not-recommended` 状态

### 5. CFD 图网络 Rollout 稳定性

适用信号：

- “Vortex_shedding_mgn”
- “MeshGraphNets / GNS”
- “噪声扰动训练”
- “多步 rollout 评估”
- “提升长时间预测稳定性”

角色层关注点：

- 当前任务是训练增强、rollout 评估，还是两者都要
- 数据是否包含时间序列、边、节点特征、边特征、mask、边界节点和状态更新变量
- 噪声应加在动态节点状态、速度 / 压力字段，还是其它可学习状态上
- rollout 评估应按单步误差、多步累计误差、最终步误差或轨迹稳定性汇总
- 训练增强不应破坏已有 datapipe 的真实标签协议

后续 coder asset targets：

- `skills/onescience-coder/assets/models/meshgraphnet.md`
- `skills/onescience-coder/assets/models/meshgraphnet_benchmark.md`
- `skills/onescience-coder/assets/datapipes/deepmind_cylinderflow.md`
- `skills/onescience-coder/assets/datapipes/deepmind_lagrangian.md`
- `skills/onescience-coder/assets/datapipes/eagle.md`
- `skills/onescience-coder/assets/contracts/oneedge.md`
- `skills/onescience-coder/assets/contracts/onenode.md`
- `skills/onescience-coder/assets/contracts/oneprocessor.md`

### 6. CFD 推理与评估流程

适用信号：

- “补推理代码”
- “做预测 / rollout / 可视化 / 结果导出”
- “比较不同模型效果”
- “生成评估脚本或汇总指标”

角色层关注点：

- 当前是单步推理、多步 rollout，还是 steady-state field regression
- 评估指标是点级误差、场误差、积分量误差、相对误差、时间累计误差还是可视化输出
- 输出产物是预测文件、图像、指标 JSON / CSV 还是 benchmark 汇总
- 推理入口是否需要复用训练时的 adapter / view

后续 coder asset targets：

- `skills/onescience-coder/assets/models/model_index.md`
- 目标模型卡片
- `skills/onescience-coder/assets/datapipes/datapipe_index.md`
- 目标数据卡片

### 7. CFD 多阶段流程串联

适用信号：

- “完成一整套适配”
- “包括数据接口、训练代码、配置文件、推理代码、评估”
- “从新数据集到多个模型训练对比串起来”

角色层关注点：

- 当前是否应拆成数据探测、datapipe、模型 adapter、训练、推理、评估多个阶段
- 哪些阶段可以直接生成，哪些阶段必须先等探测结果
- 是否应先只完成 case-local 实现，再考虑主库集成
- 需要哪些阶段性交接物，避免 coder 一次性在信息不足时硬写完整闭环

后续 coder asset targets：

- 先按前 6 个任务桶拆分，再分别交给对应 assets

## CFD 任务到后续路线

- `已有 CFD 数据流复用与适配` -> `onescience-role` 规划后交给 `onescience-coder`，使用 `assets_only`
- `新 CFD 数据接口构建` -> `onescience-role` 规划后交给 `onescience-coder`，使用 `assets_only`
- `CFD 模型适配` -> `onescience-role` 规划后交给 `onescience-coder`，使用 `assets_only`
- `CFD 多模型 Benchmark 对比` -> `onescience-role` 先做兼容性分层，再交给 `onescience-coder`
- `CFD 图网络 Rollout 稳定性` -> `onescience-role` 规划训练增强和评估目标，再交给 `onescience-coder`
- `CFD 推理与评估流程` -> `onescience-role` 规划产物与指标，再交给 `onescience-coder`
- `CFD 多阶段流程串联` -> `onescience-role` 先拆阶段，再按阶段交给 `onescience-coder`

## 路由验证建议

当当前阶段只验证技能路线是否正确时，优先设计以下类型的请求，不要求 `coder` 继续产出代码：

- “我有一个新的翼型数据集，先只判断应该走哪条技能链”
- “我有一批 VTK 流场文件，先别写代码，只告诉我你会读取哪些 assets”
- “我想比较 Transolver、FNO、U_Net、LSM，先只判断数据和模型协议怎么对齐”
- “我想在 Vortex_shedding_mgn 加噪声训练和 rollout 评估，先看你如何路由”
