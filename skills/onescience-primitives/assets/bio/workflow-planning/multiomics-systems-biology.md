# 多组学与系统生物学工作流

- workflow_id: `multiomics-systems-biology`

## 适用范围

用于 transcriptome、proteome、metabolome、epigenome、single-cell 或 spatial 结果的整合，以及 GO/KEGG/Reactome/GSEA、MOFA、DIABLO、network、CellChat、COBRApy、SBML 和 flux balance 分析规划。

## 输入

- 必需：各模态 QC 后的矩阵或结果表；sample/cell metadata；ID mapping 规则；研究目标。
- 可选：gene set/pathway database、PPI/network database、SBML/metabolic model、condition labels、phenotype/outcome。

## 输出

- harmonized feature tables。
- integrated latent factors 或 network modules。
- pathway/enrichment/GSEA 结果。
- cell communication、regulatory network 或 metabolic model change set。
- figures 和解释报告。

## 流程节点

1. 检查每个模态是否已完成自身 QC 和 primary analysis。
2. 对齐 sample/cell ID、gene/protein/metabolite ID 和 metadata。
3. 根据目标选择 factor model、supervised integration、network/pathway、cell communication 或 metabolic model 分支。
4. 执行 integration、enrichment、network 或 flux analysis。
5. 做 robustness、permutation、held-out modality 或 independent evidence 检查。
6. 输出整合结果，并区分 association、prediction、mechanism 和 causality。

## 边界与分流

- RNA-seq、proteomics、single-cell、epigenomics 等 primary analysis 必须先在各自工作流完成。
- 整合不能修复失败的单模态 QC。
- 相关性、共同变化或网络边不等于因果。

## 模型与工具选择边界

- 无监督 matched multiomics：MOFA 类 factor model。
- 表型预测：DIABLO 或 supervised integration。
- 通路解释：GO/KEGG/Reactome/GSEA。
- 单细胞通信：CellChat 类方法。
- 代谢模型：COBRApy/SBML/FBA，必须记录 objective 和 constraints。

## 质量检查

- ID mapping rate 和丢失比例。
- sample/cell alignment。
- per-modality QC 状态。
- missingness 和 batch effect。
- gene set/pathway/network 数据库版本。
- metabolic model objective 和约束来源。

## 回退策略

- 模态未配对：使用 aggregate pathway/network comparison，不做 paired latent factor。
- ID mapping 损失大：先输出映射问题和可分析子集。
- 缺背景基因集：不解释 enrichment p value。

## 资源召回建议

- feature matrix 和 biomarker 表：`bio_table_qc_biomarker_app`。
- pathway/network/database：`bio_knowledge_query_app`。
- 各模态按需召回对应工作流资源。
