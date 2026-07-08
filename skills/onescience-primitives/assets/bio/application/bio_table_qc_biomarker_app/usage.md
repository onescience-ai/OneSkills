# launch

matrix/metadata 一致性检查：

```sh
python script/bio_table_qc_tools/matrix_metadata_check.py --matrix counts.csv --metadata metadata.csv --sample-id sample_id --output qc.json
```

ctDNA VAF 计算：

```sh
python script/bio_table_qc_tools/ctdna_vaf_panel.py --input read_counts.csv --output vaf_panel.csv
```

# input_schema

必须显式传入 data object、file format、path/accession、reference build、matrix、metadata、sample ID 列、endpoint、split、read count 表、panel 模板或 schema。临床/转化任务必须说明 cohort、assay、endpoint、evidence source 和人工审核边界。

# runtime_interfaces

- CLI 工具：`matrix_metadata_check.py`、`feature_table_leakage_check.py`、`ctdna_vaf_panel.py`
- 模板入口：`feature_matrix_manifest.yaml`、`generic_samplesheet.csv`、`biomarker_model_card.yaml`、`liquid_biopsy_panel.yaml`、`causal_genomics_plan.yaml`、`pharmacogenomics_handoff.yaml`、`variant_prioritization_schema.tsv`
- 适用任务标签：`alignment-bam-processing`、`expression-matrix-feature-tables`、`public-data-ingestion`、`read-qc-trimming`、`samplesheet-metadata-design`、`sequence-io-manipulation`、`variant-interval-files`、`biomarker-machine-learning`、`liquid-biopsy-ctdna`、`causal-genomics`、`pharmacogenomics-risk`、`clinical-variant-oncology`

# main_functions

- check matrix metadata consistency
- check feature leakage
- calculate ctDNA VAF
- emit data foundation manifest and QC checklist
- emit biomarker and clinical handoff templates

# execution_resources

CPU 表格任务。大矩阵需要分块或内存评估。

# operation_limits

该卡不训练正式机器学习模型，不做临床诊断，不替代人工变异审核，也不直接执行下载、剪切、比对、坐标转换或文件改写。模型训练或报告解释需交给后续分析流程。
