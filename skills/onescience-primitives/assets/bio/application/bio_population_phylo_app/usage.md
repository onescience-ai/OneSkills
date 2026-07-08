# launch

GWAS summary QC 示例：

```sh
python script/bio_population_tools/gwas_summary_qc.py --input gwas.tsv --output gwas_qc.json
```

Newick QC 示例：

```sh
python script/bio_population_tools/newick_qc.py --input tree.nwk --output newick_qc.json
```

# input_schema

输入路径和输出路径必须由命令行参数提供。GWAS 任务需要列名、样本/群体 manifest、表型和协变量；系统发育任务需要树或比对来源、taxon 名称、rooting 和支持度解释。

# runtime_interfaces

- CLI 工具：`newick_qc.py`、`gwas_summary_qc.py`
- 模板入口：`comparative_genomics_plan.yaml`、`gwas_qc_manifest.csv`、`imputation_prs_manifest.yaml`、`pathogen_surveillance_metadata.csv`、`phylo_analysis_plan.yaml`
- 适用任务标签：`phylogenetics-tree-analysis`、`population-genetics-gwas`、`comparative-genomics-evolution`、`phasing-imputation-prs`、`pathogen-genomic-surveillance`

# main_functions

- validate Newick
- validate GWAS summary stats
- emit phylogenetic analysis plan
- emit population genetics manifest
- emit pathogen surveillance metadata

# execution_resources

轻量检查为 CPU 任务。正式 GWAS、树推断、填补或贝叶斯系统发育需要后续分析流程和 runtime 资源评估。

# operation_limits

该卡不执行正式关联分析、树推断、填补或传播链重建；仅做格式/QC/计划交接。
