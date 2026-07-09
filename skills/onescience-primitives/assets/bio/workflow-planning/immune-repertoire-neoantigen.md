# 免疫组库与新抗原工作流

- workflow_id: `immune-repertoire-neoantigen`

## 适用范围

用于 TCR/BCR repertoire、VDJ、clonotype、MIXCR、scirpy、single-cell VDJ、neoantigen prediction、HLA/MHC binding、epitope ranking、immunogenicity scoring 和 tumor variant 到 neoantigen 的证据规划。

## 输入

- 必需：VDJ FASTQ、AIRR table、clonotype table、single-cell VDJ object、VCF + HLA 或 peptide list 中的至少一种；sample metadata。
- neoantigen 分支：可信 tumor variant、HLA type、expression evidence、peptide length、annotation。
- 可选：paired scRNA object、known epitope database、tumor purity、clonality 信息。

## 输出

- clonotype table、diversity metrics、expansion plots。
- paired chain summary。
- candidate peptide table。
- MHC binding/ranking table。
- QC report 和证据摘要。

## 流程节点

1. 判定 repertoire-only、scVDJ integration、tumor variant to peptide 或 peptide ranking 分支。
2. 组装或校验 clonotype、productive chain、chain pairing、cell/sample mapping。
3. 计算 clonal expansion、diversity、sharing、V/J usage 和 phenotype association。
4. neoantigen 分支从可信变异生成 peptide，结合 HLA type 做 binding/ranking。
5. 结合 expression、clonality、variant confidence、peptide processing 和 known epitope 证据排序。
6. 输出技术证据，不给临床用药建议。

## 边界与分流

- tumor variant 必须由 `variant-calling-interpretation` 或可信上游提供。
- scVDJ 关联 scRNA 前，scRNA 对象应先经过 `single-cell-rna-analysis`。
- binding score 不等于免疫原性或临床有效性。

## 模型与工具选择边界

- VDJ/clonotype 使用 repertoire 工具链。
- MHC binding 和 epitope ranking 使用 peptide-HLA 专用工具。
- variant confidence、expression 和 clonality 是候选排序证据，不是临床结论。

## 质量检查

- productive chain rate。
- scVDJ doublet/multiplet 风险。
- HLA typing confidence。
- tumor variant confidence 和 VAF。
- expression evidence 和 peptide length/allele compatibility。

## 回退策略

- 缺 HLA type：只输出 repertoire 或 peptide inventory，请求 HLA 后再做 binding。
- 缺可信 variant：不做 neoantigen ranking，要求上游变异证据。
- 缺 paired scRNA：只做 repertoire 层分析，不做表达支持排序。

## 资源召回建议

- HLA/MHC/epitope/database 查询：`bio_knowledge_query_app`。
- 候选排序表：`bio_table_qc_biomarker_app`。
- 报告：`bio_qc_report_app`。
