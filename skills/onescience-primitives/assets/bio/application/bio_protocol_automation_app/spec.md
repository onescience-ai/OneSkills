# architecture_overview

该应用卡以模板为主，承载液体处理机器人协议、协议/ELN 登记和 blot/gel/plate 图像定量布局。应用层在生成可上机协议前必须确认体积、浓度、耗材、移液范围、死体积、deck/labware、controls、replicates、simulation 和人工审核步骤；若任务是仪器数据标准化或 QC 报告，应转入 clinical-lab-quality 类应用。

# parameter_scale

非模型原语。规模由 plate 数、well 数、样本数、reagent 数、transfer step 数、deck/labware 数、协议步骤数、图像 lane/spot/ROI 数和重复数决定。

# architecture_structure

- `liquid_handler_protocol.yaml`：记录 Opentrons OT-2/Flex 或通用液体处理平台、deck map、labware、source/destination、体积、浓度、dead volume、mixing、controls、serial dilution、PCR/qPCR setup、plate replication 和 simulation 约束。
- `protocol_record.yaml`：记录协议来源、结构化步骤、样本/构件/库存登记字段、材料试剂、版本控制、ELN 字段、追溯信息和审核状态。
- `blot_quantification_layout.csv`：记录 Western blot、gel electrophoresis、dot blot 或 plate image 的 lane/band/spot/ROI、样本、曝光、技术重复/生物重复、背景扣除、saturation flag、housekeeping/loading control 归一化和图表交接字段。

# input_schema

输入包括 `experiment_task`、`sample_or_construct_inputs`、`protocol_source_or_steps`、`instrument_or_platform`、`layout_or_plate_map`、`controls_and_replicates`、`safety_or_review_points` 和 `expected_outputs`。液体处理任务还必须显式给出 robot_platform、deck map、labware、reagents、transfer_steps、体积、浓度、移液范围、死体积和 simulation plan；图像定量任务必须给出 lane/spot/ROI、exposure、背景扣除、loading control、saturation flag、技术重复/生物重复结构、重复聚合和输出图表要求；ELN 登记任务必须给出材料、样本、构件、库存、版本和追溯字段。

# output_schema

输出为 YAML/CSV 模板、机器人协议 handoff、ELN/库存登记字段、结构化协议记录、图像定量布局表、归一化字段和审核清单。若缺少关键实验参数，只输出待补字段清单，不输出可上机协议。

# shape_transformations

protocol steps
  -> structured YAML record
  -> instrument handoff

sample/layout table
  -> plate or lane map
  -> quantification/review table

# key_dependencies

- 明确体积、浓度、耗材、孔位和实验步骤。
- 平台名称、deck map、labware 规格、移液范围和 dead volume。
- ELN/库存系统字段、材料试剂、版本控制和追溯约定。
- 图像 lane/spot/ROI、背景扣除、loading control 和重复聚合规则。

# common_modification_points

- 机器人平台、deck map 和 labware 名称。
- plate map、deck map 和移液策略。
- controls、replicates 和 normalization 字段。
- ELN/库存字段、材料试剂、版本控制和审核状态。
- band/lane/spot/ROI 定量、背景扣除和图表交接字段。

# implementation_risks

- 不可在缺少体积、浓度、耗材和移液范围时生成可上机协议。
- 不可把自动化协议当成已经通过湿实验验证的 SOP。
- 不可把 ELN/库存系统凭据写入模板或卡片。
- 不可把图像定量布局表当作已经完成的 band/spot 定量结果。
- 不可定量饱和条带并当作可靠线性信号；不可把技术重复当作生物重复。

# code_references

- primitive 模板目录：`assets/bio_protocol_automation_app/script/bio_protocol_templates/`
- 语义来源标签：`experimental-protocol-automation`
- 语义来源标签：`liquid-handling-protocols`
- 语义来源标签：`protocol-registry-eln`
- 语义来源标签：`assay-image-quantification`
