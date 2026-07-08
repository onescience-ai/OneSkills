# launch

按任务选择对应轻量工具。例如 PAM 扫描：

```sh
python script/bio_molecular_tools/pam_scan.py --fasta targets.fa --pam NGG --output pam_sites.tsv
```

限制性酶切报告：

```sh
python script/bio_molecular_tools/restriction_digest_report.py --fasta plasmid.fa --enzymes EcoRI,BamHI --topology circular --output digest.tsv
```

# input_schema

优先使用 `script/bio_molecular_templates/*.yaml` 或 `.tsv` 填写请求。关键字段包括目标序列、物种/参考、assay 类型、primer/probe 约束、编辑类型、Cas 系统、PAM、off-target 策略、donor/编辑窗口、酶集合、序列拓扑、插入片段、质粒 feature、验证策略、RNA 条件和输出格式。

# runtime_interfaces

- CLI 工具：`pam_scan.py`、`sequence_design_checks.py`、`restriction_digest_report.py`、`dotbracket_stats.py`
- 模板入口：`crispr_design_request.yaml`、`primer_request.yaml`、`restriction_map_request.yaml`、`rna_structure_request.yaml`、`plasmid_feature_table.tsv`、`plasmid_verification_plan.yaml`
- 适用任务标签：`primer-probe-design`、`crispr-guide-editing`、`restriction-cloning-mapping`、`plasmid-annotation-verification`、`rna-structure-design`

# main_functions

- scan PAM
- check sequence design metrics
- report restriction digest
- summarize dot-bracket structure
- emit CRISPR editing handoff
- emit plasmid verification plan
- emit RNA structure tool handoff
- emit molecular design templates

# execution_resources

CPU 即可。输入规模较大时需要按序列拆分或流式处理。

# operation_limits

该卡只提供本地候选生成、格式化和轻量检查；完整 off-target、热力学折叠、RNA-RNA interaction、pseudoknot/modification/protein-binding 结构解释、引物特异性 BLAST、donor 设计验证或湿实验验证需要外部工具或后续执行计划。
