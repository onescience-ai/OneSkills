# description
MatRIS 的规划核心是把材料结构预测任务拆成结构读取、图构造、任务头选择、预训练权重选择和下游应用验证。它适合在 agent 工作流中承担能量、力、应力、磁矩预测，以及 ASE calculator、结构弛豫、分子动力学的模型原语角色。

# when_to_use
- 需要对晶体、合金、无机材料或分子材料预测能量、力、应力或磁矩。
- 需要使用预训练材料势函数快速评估结构。
- 下游任务是结构优化、MD、材料筛选或近似势能面评估。
- 输入可转换为 `pymatgen.Structure` 或 `ase.Atoms`，并能构造半径图。
- 希望同时利用二体边特征和三体角特征表达局部结构。

不优先使用：

- 任务不涉及原子结构或局部相互作用。
- 只需要电子密度、能带、态密度等非势函数直接输出。
- 结构包含模型不支持或未覆盖的元素范围。
- 必须使用未开放下载/加载的 `matris_10m_omat`，且没有本地 checkpoint。

# inputs
- 结构来源：CIF、POSCAR、pymatgen `Structure`、ASE `Atoms` 或批量结构列表。
- 任务组合：`e`、`ef`、`efs`、`efsm` 或 `em`。
- 模型来源：从头实例化、`matris_10m_oam`、`matris_10m_mp` 或本地 checkpoint。
- 图参数：`pairwise_cutoff`、`three_body_cutoff`、是否需要修改默认 cutoff。
- 物理输出约定：能量是每原子还是总能，应力单位是否需要转换。
- 运行资源：CPU/GPU、单结构大小、批量结构数量、是否包含应力。
- 下游路径：直接 forward、ASE calculator、结构优化或 MD。

# outputs
- 模型调用方式：`MatRIS.forward`、`MatRIS.load`、`MatRISCalculator` 或 `StructOptimizer`。
- 输入转换计划：文件到 `Structure/Atoms`，再到 `RadiusGraph` 或 calculator 自动转换。
- 任务配置：`task` 字符串、`is_training`、`is_conservation` 与输出字段预期。
- 权重策略：本地 checkpoint 路径、缓存路径、模型名和设备选择。
- 验证结果：输出字段、shape、单位、能量换算方式和异常结构处理记录。
- 下游建议：是否进入 relax、MD、筛选或重新训练/微调阶段。

# procedure
1. 判断任务需要哪些物理量：只要能量用 `e`，优化/MD 用 `ef` 或 `efs`，磁性相关任务用 `efsm`。
2. 读取结构并确认元素、周期性、cell 和原子间距合理。
3. 选择权重：
   - 通用预训练优先 `matris_10m_oam`。
   - MPTrj 相关分布可尝试 `matris_10m_mp`。
   - 离线环境优先设置 `ONESCIENCE_MODELS_DIR`。
4. 决定入口：
   - 需要单次模型推理：`MatRIS.load` + `model.graph_converter` + `model([graph], task=...)`。
   - 需要 ASE 工作流：`MatRISCalculator`。
   - 需要结构优化：`StructOptimizer`。
5. 先用小结构 smoke test，检查 `e/f/s/m` 字段和 shape。
6. 对目标结构运行正式推理；若 `task` 包含 `s`，额外确认 stress 单位和体积归一化。
7. 对 relax 或 MD 任务，记录能量、最大力、应力、磁矩和是否出现异常近邻。
8. 若结果不稳定，回查结构质量、cutoff、元素覆盖和 checkpoint 来源。

# constraints
- 结构必须能形成有效半径图；空邻居或异常近邻会破坏计算。
- `task` 必须只由模型识别的 `e/f/s/m` 组合构成。
- 当前预训练加载入口只保证 `matris_10m_oam` 和 `matris_10m_mp`。
- `is_intensive=True` 输出每原子能量，使用总能时必须乘以原子数或通过 calculator。
- stress 在内部和 ASE 输出之间存在单位转换，不能混用。
- 大结构或高 cutoff 会显著增加边数和三体角数量，是主要资源瓶颈。

# next_phase_recommendation
- 为目标材料体系建立一个固定 smoke test：单结构 forward、ASE calculator、relax 10 step。
- 如果用于筛选，统一输出总能、每原子能、最大力、应力范数和磁矩统计。
- 如果用于结构优化，先用 `ef` 或 `efs` 对少量代表结构验证收敛和物理合理性。
- 如果用于 MD，先短程 NVE/NVT 检查能量漂移和异常力，再扩大步数。
- 如需领域微调，补充训练数据字段、loss 权重、参考能和元素覆盖策略。

# fallback
- 预训练下载失败：设置 `ONESCIENCE_MODELS_DIR` 并放置 `MatRIS_10M_OAM.pth.tar` 或 `MatRIS_10M_MP.pth.tar`。
- 模型名不支持：改用 `matris_10m_oam` 或 `matris_10m_mp`，或手动用 `from_dict` 加载本地兼容 checkpoint。
- 图构造失败：检查结构 cell、PBC、原子重叠和 cutoff；必要时先用 ASE/pymatgen 清洗结构。
- 显存不足：降低结构批量、减少 cutoff、避免 `efsm` 中不必要的 stress/magmom，或改用 CPU/分批运行。
- 输出能量与预期差异大：确认 `is_intensive`、参考能、单位和 calculator 总能换算。
- relax/MD 不稳定：缩小步长、降低温度、先做结构预优化，并排查异常近邻与元素覆盖问题。
