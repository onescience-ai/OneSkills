# launch

按任务选择脚本入口，由 coder 生成带完整参数的命令，再交给 runtime 执行。例如：

```sh
python script/bio_single_cell_tools/qc_analysis.py --input input.h5ad --output-dir qc_out --sample-id sample_001
```

# input_schema

必须显式传入输入文件、输出目录和关键字段，不从环境变量推断路径。常见字段包括 `input_h5ad`、`input_10x_h5`、`metadata_csv`、`batch_key`、`label_key`、`layer`、`model_type`、`min_genes`、`max_mito_pct`、`n_top_genes`、`output_dir`。

# runtime_interfaces

- CLI 脚本：`script/bio_single_cell_tools/*.py`
- 可导入 helper：`model_utils.py`、`qc_core.py`、`qc_plotting.py`
- 适用任务标签：`single-cell-toolkit`、`single-cell-toolkit-down`、`single-cell-rna-analysis`
- 执行边界：由 coder 生成显式命令后交给 runtime；本卡不直接运行脚本。

# main_functions

- validate AnnData
- prepare data
- run QC
- train model
- cluster and embed
- differential expression
- transfer labels
- integrate datasets

# execution_resources

小型 QC 可在 CPU 执行；scVI 系列训练和大规模整合建议使用 GPU。运行前需要确认 scanpy、anndata、scvi-tools 与绘图库环境。

# operation_limits

该卡不负责下载公共数据、不负责临床诊断结论、不保证 scVI 模型适合所有实验设计。缺少 batch/label/organism 元数据时，只能生成待确认的执行计划。
