# description

把实验协议、液体处理、ELN/库存登记和图像定量布局请求转为可审核的结构化模板。

# when_to_use

用于 Opentrons/Flex/OT-2 或通用液体处理、PCR/qPCR setup、serial dilution、plate replication、ELN 协议登记、样本/构件/库存注册、Western blot、gel electrophoresis、dot blot 或 plate image 定量布局。

# inputs

- 实验步骤、样本、试剂、平台和耗材。
- 体积、浓度、孔位、controls 和 replicates。
- deck map、labware、dead volume、simulation plan、ELN/库存字段或图像 lane/spot/ROI 字段。
- 安全、simulation 和人工审核要求。

# outputs

- 填写后的 YAML/CSV 模板。
- 设备或 ELN handoff。
- 图像定量布局、归一化字段和重复聚合计划。
- 缺失字段和审核点。

# procedure

1. 根据任务标签判定 liquid handling、protocol registry/ELN 或 assay image quantification。
2. 选择对应模板文件。
3. coder 按字段补全，不生成未确认的可上机脚本。
4. 需要设备执行、ELN 写入或图像分析时再交给专门运行层或平台适配器。

# constraints

- 不得跳过 simulation 和人工审核。
- 不得硬编码设备路径或凭据。
- 不得在缺少关键实验参数时输出最终协议。

# next_phase_recommendation

如果用户需要真实设备运行、ELN 写入或图像分析，应先生成模拟/校验计划和人工审核清单，再由设备或平台适配层处理。

# fallback

参数不足时输出模板和待补字段清单。
