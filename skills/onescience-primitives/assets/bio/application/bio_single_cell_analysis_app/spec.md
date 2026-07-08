# architecture_overview

该应用卡聚合单细胞分析中可复用的轻量执行脚本，覆盖 AnnData 校验、QC、过滤、scVI/scANVI/totalVI/PeakVI/MultiVI/veloVI 训练、邻居图/UMAP/聚类、差异表达、标签迁移和批次整合。工具/API 级任务可直接选择脚本入口；端到端分析链路需先明确阶段、输入对象和交付物，再交给 coder 生成命令或配置。

# parameter_scale

非模型原语，不固定参数规模。资源规模主要由输入 AnnData/10x h5 的细胞数、基因数、批次数、模态数和 scvi-tools 模型配置决定。

# architecture_structure

- `validate_adata.py`：检查 AnnData 结构、obs/var 字段和矩阵可用性。
- `prepare_data.py`、`model_utils.py`：完成过滤、批次字段、标签字段和模型输入准备。
- `qc_analysis.py`、`qc_core.py`、`qc_plotting.py`：计算 QC 指标、MAD outlier、过滤结果和图形产物。
- `train_model.py`：训练 scVI 系列模型。
- `cluster_embed.py`：构建邻居图、UMAP/t-SNE 与聚类。
- `differential_expression.py`：按 group/contrast 输出 marker 或差异表达表。
- `transfer_labels.py`：执行 reference-to-query 标签迁移。
- `integrate_datasets.py`：整合多个 AnnData 或批次。

# input_schema

输入通常为 `.h5ad` 或 10x h5/矩阵目录，并需要明确 `sample_metadata`、`batch_key`、`label_key`、`layer`、`organism`、QC 阈值和输出目录。端到端分析必须记录样本来源、测序平台、过滤逻辑、批次变量和期望交付物。

# output_schema

输出包括过滤后的 `.h5ad`、QC 表、QC 图、训练后的 latent 表示、聚类标签、UMAP 坐标、差异表达结果、标签迁移结果、整合后的对象和报告素材。

# shape_transformations

AnnData 主矩阵: cells x features
  -> QC/filter: cells' x features'
  -> highly variable genes: cells' x hvgs
  -> model latent: cells' x latent_dim
  -> neighbors/embedding: cells' x 2 或 cells' x n_components
  -> downstream tables: cell/group/feature 级二维表

# key_dependencies

- AnnData/Scanpy 数据对象约定
- scvi-tools 模型训练与推理接口
- pandas/numpy 表格处理
- matplotlib/seaborn 或 scanpy plotting 图形输出

# common_modification_points

- 物种相关的线粒体/核糖体基因规则。
- QC 阈值、MAD outlier 倍数和 doublet/dead-cell 处理。
- `batch_key`、`label_key`、`layer`、`counts_layer` 的字段映射。
- 模型类型、latent 维度、训练轮数和 GPU/CPU 策略。
- marker 输出列、contrast 和细胞类型注释规则。

# implementation_risks

- 不可把不同物种或不同基因命名体系的 QC 规则直接混用。
- 不可在没有 batch/label 字段确认时直接训练或迁移标签。
- 不可把规划建议当成已执行结果。
- 大规模数据需要 runtime 评估内存/GPU，application 卡只提供入口和约束。

# code_references

- primitive 脚本目录：`assets/bio_single_cell_analysis_app/script/bio_single_cell_tools/`
- 语义来源标签：`analysis-tools/single-cell-toolkit`
- 语义来源标签：`single-cell-toolkit-down`
- 语义来源标签：`single-cell-rna-analysis`
