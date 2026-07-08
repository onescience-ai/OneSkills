# description
`mace_block` 的规划决策重点是为 MACE 势函数选择和约束主干积木：在给定数据、checkpoint、物理输出和资源条件下，确定 interaction 类型、irreps 宽度、角动量、correlation、readout、scale/shift 与多头策略，使模型既能表达目标材料相互作用，又能保持训练和微调可加载、可稳定运行。

# when_to_use
- 需要搭建或改造 MACE/ScaleShiftMACE 主干。
- 需要新增逐原子能量、偶极或多头 readout。
- 需要分析 foundation model fine-tuning 的结构兼容性。
- 需要定位 MACE 训练中的 irreps、head、product basis 或 readout shape 错误。
- 不用于数据字段解析、邻居搜索或 loss 权重选择的首要决策。

# inputs
- 模型目标：energy-only、energy-force、energy-force-stress、dipole 或多任务。
- 数据约束：元素表、最大原子数、邻居密度、head/dataset 划分。
- 结构约束：`num_channels`、`max_L`、`correlation`、`num_interactions`、`hidden_irreps`。
- checkpoint 约束：是否加载 foundation model，旧权重的 irreps、head 和 correlation。
- 资源约束：显存、batch size、训练时限。
- 风险信号：shape mismatch、tensor product 报错、loss 不稳定、多头输出缺失。

# outputs
- block 组合方案：节点嵌入、interaction、product basis、readout、scale/shift 是否启用。
- 参数建议：`hidden_irreps`、`correlation`、`avg_num_neighbors`、`radial_MLP`、`heads`。
- 兼容性判断：是否可加载旧 checkpoint，哪些权重需要重建或迁移。
- 验证计划：单 batch forward、输出字段检查、能量/力 smoke test。
- 风险清单：irreps 不匹配、head 缺失、元素表错位、LAMMPS 分支破坏。

# procedure
1. 判断任务输出是否需要普通能量 readout、非线性 readout、偶极 readout 或多头 readout。
2. 若使用 foundation checkpoint，先固定旧模型的 `hidden_irreps`、`max_L`、`correlation`、`heads` 和元素表。
3. 根据数据规模和资源选择通道数与 interaction 层数；先从 demo 稳定配置出发。
4. 若需要提升 many-body 表达，再调整 `correlation`，并同步检查 product basis 权重形状。
5. 配置 `avg_num_neighbors`，优先使用数据统计而不是手写猜测。
6. 做单 batch forward，检查每层 `node_feats`、readout 输出和 head mask。
7. 接入 loss 后再判断是否需要改 block，而不是只根据单步 loss 改结构。

# constraints
- 不在 block 层临时修正数据字段或单位问题。
- 不随意改变 foundation checkpoint 的 `correlation`、irreps 和 head 数量。
- `node_attrs` 必须来自同一元素表。
- LAMMPS/MLIAP 兼容分支必须保留 ghost atom 语义。
- 新增 property 应通过模型输出和 loss 正式接入，不绕过 readout 聚合路径。

# next_phase_recommendation
- 为目标任务建立一份 block 结构卡，记录 irreps、correlation、readout、heads 与 checkpoint 来源。
- 若计划 fine-tuning，先做权重加载报告和单 batch 输出对齐。
- 若计划新增 head，下一阶段同步更新 loss、metric 和数据字段契约。
- 若出现训练不稳定，优先检查数据统计、cutoff 和 loss 权重，再决定是否扩大 block。

# fallback
- irreps 报错：回退到原 checkpoint 或 demo 配置，逐项恢复 `hidden_irreps`、`max_L`、`correlation`。
- head 输出缺失：检查 `heads`、`head`、`node_heads` 和 readout wrapper。
- 显存不足：降低 `num_channels`、`max_L`、`correlation` 或 batch size。
- fine-tuning 权重不兼容：冻结结构参数，重新初始化新增 readout，必要时从头训练 baseline。
- 多头数据异常：先以单 head `Default` 跑通，再恢复多头配置。
