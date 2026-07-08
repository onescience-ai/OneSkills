# description

把成像、流式和空间表型请求转成模板化计划、轻量 QC 或 mask 定量入口。

# when_to_use

用于 FCS 派生表、marker panel、IMC、显微图像分割、WSI tile、图像数据 manifest 和 mask measurement。

# inputs

- assay_or_image_type、input_format、channel_or_marker_panel。
- preprocessing、segmentation_or_gating_strategy。
- QC checkpoints、review artifacts 和 quantitative outputs。

# outputs

- 计划模板或 manifest。
- mask/cytometry QC 输出。
- 人工审核和下游分析 handoff。

# procedure

1. 根据任务标签判定 flow、IMC、bioimage、WSI 或 image management。
2. 选择对应模板和工具脚本。
3. coder 生成模板或命令。
4. runtime 执行轻量脚本；复杂分割/门控交给后续专业分析流程。

# constraints

- 不得把图像当普通二维表处理。
- 不得省略像素尺度、通道、tile、z/time 或 mask 对齐说明。
- 应用卡只提供模板和轻量脚本入口，不直接代表已执行分析。

# next_phase_recommendation

需要图形汇总时交给 data-analyzer；需要模型分割或 WSI 大规模处理时交给 runtime 规划资源。

# fallback

若缺少原始图像或 mask，仅生成 manifest 和分割计划；若 marker panel 不完整，仅输出待补字段清单。
