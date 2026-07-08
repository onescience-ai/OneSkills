# description

把端到端生信分析请求转为标准流程模板和执行前交接。

# when_to_use

用于 bulk RNA-seq、单细胞、空间组学、变异检测、表观调控、长读长、微生物组、蛋白质组/代谢组、多组学、免疫信息、基因组组装注释、功能基因组筛选、转录后调控和蛋白设计结构验证等需要结构化配置的任务。若用户需要完整科研流程拆解、节点依赖和资源组合，应交给 research-workflow。

# inputs

- pipeline_family、input_object、organism_or_taxon。
- reference_build_or_database、sample_metadata。
- workflow_stages、qc_checkpoints、expected_outputs。
- platform、contrast、caller_strategy、analysis_branch、screen_type、modalities、model_chain。

# outputs

- CSV/TSV/YAML 模板。
- 流程阶段和 QC checkpoint。
- coder/runtime 执行交接。

# procedure

1. 判断任务是否需要端到端科研编排；若需要，先交给 research-workflow 形成节点计划。
2. 根据 pipeline_family 选择专用模板或通用骨架字段。
3. 补全样本表、参考版本、平台、分组/contrast、QC checkpoint 和预期输出。
4. coder 补全模板并生成后续脚本或配置。
5. runtime 只在已有可执行脚本/命令时介入。

# constraints

- 不得把模板当成已运行结果。
- 不得跨流程混用输入语义和 QC 指标。
- 不得省略 reference build、contrast、平台和样本 metadata。
- 不得用该应用卡替代 research-workflow 的多节点科研编排。

# next_phase_recommendation

模板补全后，若需要执行，交给相应工具应用、模型卡或 runtime；若需要报告，交给 QC report app。

# fallback

若任务类型不清，输出候选流程类型和待确认字段；若输入缺少样本表或参考版本，只生成骨架模板。
