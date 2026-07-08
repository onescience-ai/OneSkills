# launch

该卡以模板启用为主：

```sh
cp script/bio_analysis_toolkit_templates/bio_tool_handoff.yaml ./bio_tool_handoff.yaml
```

# input_schema

必须填写 `tool_family`、`packages`、`input_format`、`operation`、`data_size`、`quality_checks`、`expected_outputs` 和 `execution_boundary`。涉及 NCBI/UniProt/BLAST 等外部服务时必须记录 email、API key 或速率限制要求；涉及 R/Bioconductor 时必须记录对象类型、design formula 和版本；涉及质谱时必须记录 MS level、数据库和 FDR/annotation level。

# runtime_interfaces

- 模板入口：`bio_tool_handoff.yaml`
- 适用任务标签：`python-bio-toolkit`、`r-bioconductor-toolkit`、`cheminformatics-toolkit`、`mass-spectrometry-toolkit`、`statistics-visualization`
- 关联任务标签：`single-cell-toolkit-down`
- execution_kind：template_only

# main_functions

- emit tool selection handoff
- define package/API interface
- define input/output contract
- define quality checks
- define visualization and interpretation limits

# execution_resources

模板生成无需计算资源。实际执行依赖对应 Python/R/CLI 环境、数据库、网络权限、索引文件、内存和存储；大文件处理需优先使用流式、索引或分块策略。

# operation_limits

该卡不直接执行 R、Python、RDKit、OpenMS、BLAST 或数据库查询，不替代完整科研流程编排，不保证外部数据库或软件环境可用。
