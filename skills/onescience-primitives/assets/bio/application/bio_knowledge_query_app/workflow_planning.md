# description

把数据库检索需求转成可执行层消费的 query handoff。

# when_to_use

用于文献/序列、通路/PPI、蛋白质组/代谢组、调控注释、单细胞图谱、结构/化合物、变异/临床证据等公共知识库查询设计。

# inputs

- database_family、query_terms、identifier_type。
- species_or_taxon、release_or_date、genome_build。
- accession、background_set、cell_type_schema、structure_or_compound_filters、variant_representation、transcript。
- return_fields、evidence_fields、output_format。

# outputs

- 结构化查询模板。
- 字段映射和证据整理要求。
- 执行层联网或本地数据库 handoff。

# procedure

1. 根据数据库家族和任务标签选择查询模板或通用字段起点。
2. 补全查询模板。
3. coder 补全结构化字段。
4. 需要实际查询时交给具备网络或数据库权限的执行层。

# constraints

- 不得声称模板生成已经完成检索。
- 不得省略 release/date 和 genome build。
- 不得混用 identifier 类型和证据等级。
- 不得把数据库命中、PPI 边、预测结构、docking pose 或临床注释直接当成最终生物学或临床结论。
- 不得忽略物种、版本、坐标系统、transcript、cell ontology、assay 条件或访问权限。

# next_phase_recommendation

实际检索后可交给 data-analyzer 或 report app 汇总证据。

# fallback

若数据库或 identifier 不确定，输出候选数据库和待确认字段。
