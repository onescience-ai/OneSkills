# launch

该卡以模板启用为主：

```sh
cp script/bio_workflow_templates/rnaseq_contrast.yaml ./rnaseq_contrast.yaml
```

# input_schema

必须提供流程类型、输入对象、物种或参考、样本表、分组/contrast、QC checkpoint、分析分支和预期输出。路径、参考版本和输出目录由模板字段或 coder 生成的配置显式提供。

# runtime_interfaces

- 模板入口：`rnaseq_metadata.csv`、`rnaseq_contrast.yaml`、`long_read_run_plan.yaml`、`cohort_sample_map.tsv`、`post_transcriptional_plan.yaml`、`screen_analysis_plan.yaml`
- 适用任务标签：`rnaseq-differential-expression`、`long-read-sequencing-analysis`、`variant-calling-interpretation`、`functional-genomics-screens`、`post-transcriptional-regulation`、`single-cell-rna-analysis`、`spatial-multiomics-analysis`、`epigenomics-regulation`、`microbiome-metagenomics`、`proteomics-metabolomics`、`multiomics-systems-biology`、`immune-repertoire-neoantigen`、`genome-assembly-annotation`、`protein-design-structure-validation`
- execution_kind：template_only

# main_functions

- emit RNA-seq pipeline templates
- emit long-read run plan
- emit variant cohort sample map
- emit post-transcriptional plan
- emit functional screen plan
- emit generic pipeline skeleton

# execution_resources

模板生成无需计算资源。实际流程执行需要按工具链评估 CPU/GPU、内存、存储和调度系统。

# operation_limits

该卡不直接运行 STAR、Salmon、GATK、minimap2、MAGeCK、Ribo-seq、CLIP、Kraken、QIIME2、MaxQuant、Cell Ranger、RFdiffusion 或 ProteinMPNN；只生成结构化配置和执行交接。
