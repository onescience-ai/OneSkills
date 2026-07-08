# description
`uma_head` 的规划决策用于把 UMA backbone 的共享嵌入分配给具体任务输出。核心选择包括 energy-only、energy-force-stress、direct force、gradient force、多数据集 wrapper 和输出 key 包装方式，并确保与 loss、normalizer、metric 和 dataset 字段一致。

# when_to_use
- 需要为 UMA 模型添加或修改 energy、forces、stress 输出。
- 需要决定直接力还是能量导数力。
- 需要为多数据集训练配置 dataset-specific head 或 MoE head。
- 需要排查 loss 找不到输出 key、force 梯度断裂或 stress shape 错误。
- 不用于构建近邻图或修改 eSCNMD block。

# inputs
- 任务列表：每个 task 的 `property`、loss、normalizer 和 metric。
- backbone 配置：`regress_forces`、`regress_stress`、`direct_forces`、`sphere_channels`。
- 数据字段：`batch`、`natoms`、`pos`、`cell`、`dataset`。
- 输出约定：是否 `wrap_property`，是否带 prefix 或 dataset 前缀。
- 资源约束：是否能承受 gradient-based forces/stress。
- 多数据集策略：共享 head、single head wrapper 或 MoE wrapper。

# outputs
- head 选择：`MLP_EFS_Head`、`MLP_Energy_Head`、`Linear_Force_Head`、`MLP_Stress_Head` 等。
- 输出 key 设计：property key、dataset 前缀和包装结构。
- force/stress 策略：direct 或 autograd。
- 对齐清单：head 输出、loss 输入、normalizer、metric、dataset name。
- 验证计划：单 batch forward、loss key 检查、梯度检查。

# procedure
1. 列出目标任务和每个任务需要的输出字段。
2. 若要求能量守恒力，选择 gradient-based EFS 路线并确认 `pos.requires_grad`。
3. 若优先推理速度，可评估 direct force head，但需接受非严格能量导数一致性。
4. 对 stress 任务，确认 cell、displacement、输出 shape 和 loss 约定。
5. 多数据集训练时，选择 wrapper 并确认 `dataset_names` 覆盖 batch。
6. 明确 `wrap_property` 和 prefix，更新 loss/metric 读取路径。
7. 运行单 batch，检查输出 dict key、shape、梯度和空 dataset mask。

# constraints
- head 输出 key 必须与 task property 完全一致。
- direct force 与 gradient force 策略必须和 backbone 配置一致。
- stress 分支不能缺少 cell/displacement。
- dataset wrapper 不应吞掉未覆盖数据集。
- 模型并行归约路径要与 head 输出维度匹配。

# next_phase_recommendation
- 为每个 UMA 任务生成 head-output 到 loss-input 的映射表。
- 对多数据集任务，增加 dataset mask 覆盖率检查。
- 对 direct force 任务，增加能量-力一致性评估。
- 对 stress 任务，固定 stress shape 与单位校验。

# fallback
- loss 找不到 key：打印 head 输出 dict，检查 prefix、dataset 前缀和 `wrap_property`。
- force 为 None：改用 direct force 或恢复 `pos.requires_grad` 与 EFS head。
- stress shape 错误：先关闭 stress head，确认 energy/forces 后再接回。
- dataset wrapper 报错：检查 `dataset_names` 和 batch 内 dataset 字符串。
- 模型并行异常：先在单进程模式验证 head，再恢复并行归约。
