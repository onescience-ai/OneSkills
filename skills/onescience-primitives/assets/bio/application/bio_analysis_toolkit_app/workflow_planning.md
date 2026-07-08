# description

把通用生信工具请求转为工具选择、接口契约、质量检查和后续执行交接。

# when_to_use

用于用户请求集中在某个工具包、脚本接口、文件格式处理、统计方法选择、可视化设计或轻量 API/CLI 交接时。若请求已经是 RNA-seq、单细胞、变异检测、蛋白设计等多阶段科研目标，应交给 research-workflow 做端到端编排；若请求明确是单细胞 AnnData/scVI 执行，应优先召回 `bio_single_cell_analysis_app`。

# inputs

- tool_family、packages、input_format、operation。
- data_size、reference_or_database、rate_limit_or_external_tool。
- statistical_design、visualization_type、quality_checks。
- expected_outputs、execution_boundary。

# outputs

- 工具选择模板。
- 脚本/API/CLI 接口契约。
- 输入输出字段、质量检查和解释边界。
- coder/runtime 交接建议。

# procedure

1. 判断任务是否为工具级请求，若是端到端科研目标则转交 research-workflow。
2. 选择最小工具族和包/API/CLI。
3. 补全输入格式、数据规模、版本、外部数据库和质量检查。
4. 输出 `bio_tool_handoff.yaml` 或等价结构化交接。
5. 需要实际代码时交给 coder，需要运行时交给 runtime。

# constraints

- 不得把工具选择模板当成已执行结果。
- 不得忽略输入格式、版本、索引、reference build、rate limit 和外部数据库。
- 不得把统计相关性、分子相似性、docking score 或谱库匹配写成确认性结论。

# next_phase_recommendation

若需要实现脚本，交给 coder；若需要执行脚本，交给 runtime；若需要报告和图表汇总，交给 `bio_qc_report_app` 或 data-analyzer。

# fallback

若工具族不确定，输出候选工具族和待确认字段；若环境不可用，只输出接口契约和可替代工具建议。
