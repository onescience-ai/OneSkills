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
2. 选择对应模板和最小 Python 工具脚本，并确定用户输入、输出路径和脚本参数。
3. 从用户明确提供的项目目录创建或复用 `<project_dir>/app/`；复制选中的 `.py` 入口及其本地 Python 依赖闭包并保持相对结构，目标同名文件已存在时先比较内容，未经确认不得覆盖。
4. 静态分析复制后脚本的 import，把标准库、本地模块和第三方包分开，形成所需包及版本约束清单。
5. 在当前 Python 环境检查第三方包是否已安装、已安装版本是否满足约束，并以只读依赖解析检查安装或升级是否会破坏现有包约束。
6. 若依赖均已存在且兼容，跳过安装；若有已安装但版本冲突的依赖，报告包名、当前版本、要求版本和受影响包，等待用户选择环境隔离、调整版本或停止。
7. 若依赖缺失且解析无冲突，向用户说明待安装包、版本和目标环境并询问是否安装；得到明确同意后才可安装。若缺失依赖的安装会产生冲突，报告冲突和可选方案，由用户选择，禁止自动安装。
8. 依赖门禁通过后，coder 生成指向 `<project_dir>/app/` 内复制脚本的参数化命令；runtime 使用用户已确认的输入直接执行并收集日志。复杂分割/门控交给后续专业分析流程。

# constraints

- 不得把图像当普通二维表处理。
- 不得省略像素尺度、通道、tile、z/time 或 mask 对齐说明。
- 应用卡只提供模板和轻量脚本入口，不直接代表已执行分析。

# next_phase_recommendation

需要图形汇总时交给 data-analyzer；需要模型分割或 WSI 大规模处理时交给 runtime 规划资源。

# fallback

若缺少原始图像或 mask，仅生成 manifest 和分割计划；若 marker panel 不完整，仅输出待补字段清单。
