# description

将单细胞分析请求转为可执行的 AnnData/scVI 应用流程，并明确阶段拆解、脚本/模板入口和运行边界。

# when_to_use

用于 10x/h5ad/scRNA-seq/CITE-seq/Multiome 中需要 QC、过滤、聚类、marker、整合、标签迁移或 scVI 系列模型训练的任务。

# inputs

- 输入对象路径和格式。
- 样本表、批次字段、标签字段、物种和参考。
- 分析目标：QC、聚类、注释、差异表达、整合或模型训练。
- 资源限制：CPU/GPU、内存、输出目录。

# outputs

- 脚本执行命令或 coder handoff。
- 过滤后的对象、表格、图形、模型结果和报告素材。
- 对缺失字段、批次风险和解释边界的说明。

# procedure

1. 先判断是 toolkit 任务还是端到端分析链路。
2. 选择本 application 卡和 `script/bio_single_cell_tools/`。
3. 根据任务选择最小脚本集合，不把 QC、训练、注释全部默认串起来。
4. coder 生成显式参数命令和输出目录规划。
5. runtime 执行并收集日志，后续由 data-analyzer 或报告卡整理结果。

# constraints

- 应用卡不得直接代表已运行脚本。
- 不得省略 batch/label/layer 等字段确认。
- 不得把自动注释直接写成最终生物学结论。
- 不得从环境变量或硬编码路径推断输入输出。

# next_phase_recommendation

需要正式执行时交给 `onescience-runtime`；需要图形报告时交给 `onescience-data-analyzer` 或 `bio_qc_report_app`。

# fallback

若缺少可运行环境，输出 AnnData 字段检查清单和命令草案；若缺少关键元数据，只生成模板化 handoff，不执行训练或差异分析。
