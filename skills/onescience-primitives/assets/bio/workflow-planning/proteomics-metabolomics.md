# 蛋白质组与代谢组工作流

- workflow_id: `proteomics-metabolomics`

## 适用范围

用于 mzML、mzXML、MGF、DDA、DIA、peptide identification、protein inference、label-free/TMT quantification、PTM、metabolomics、lipidomics、XCMS、MS-DIAL、feature alignment、differential abundance 和 metabolite annotation。

## 输入

- 必需：raw MS files 或 feature table；sample metadata；contrast；acquisition mode；assay type。
- 蛋白组分支：search database、enzyme、modification、FDR 策略。
- 代谢组分支：blank/QC pool、internal standards、annotation database、polarity/mode。
- 可选：batch、run order、spectral library、PTM site list。

## 输出

- peptide/protein/metabolite feature table。
- identification/annotation confidence。
- normalized abundance matrix。
- differential abundance table。
- PTM 或 metabolite annotation 表。
- QC plots、volcano/heatmap、报告。

## 流程节点

1. 判定 assay：proteomics、metabolomics、lipidomics、targeted、untargeted、DDA、DIA、TMT 或 PTM。
2. 规划 spectra 转换、peak detection、feature extraction、alignment、blank/QC handling。
3. 蛋白组执行 peptide identification、protein inference 和 FDR 控制。
4. 代谢组执行 feature annotation、adduct/isotope grouping 和 confidence 标注。
5. 做 normalization、missingness、batch/QC drift 和 differential abundance 分析。
6. 输出 feature、统计、置信度和图。

## 边界与分流

- 跨 RNA/protein/metabolite 整合转到 `multiomics-systems-biology`。
- 不把蛋白组/代谢组差异丰度当作 RNA-seq 差异表达。
- 低置信 metabolite annotation 不能当作确定结构。

## 模型与工具选择边界

- 蛋白组使用 peptide search、protein inference、FDR 控制工具链。
- DIA 和 DDA 分支分开规划。
- metabolomics/lipidomics 使用 feature detection、alignment、annotation confidence 分支。
- TMT/label-free/targeted 使用不同归一化和统计策略。

## 质量检查

- blank/carryover 和 QC pool stability。
- peptide/protein FDR。
- missingness pattern 和 batch/run-order effect。
- internal standard 或 QC drift 记录。
- annotation confidence 和数据库版本。

## 回退策略

- 只有 feature table：从 feature QC 和差异丰度开始，标记 identification 复现限制。
- 缺 blank/QC pool：标记污染和漂移风险。
- 数据库版本不明：限制 annotation 解释。

## 资源召回建议

- 工具交接：`bio_analysis_toolkit_app`。
- 数据库查询：`bio_knowledge_query_app`。
- 报告：`bio_qc_report_app`。
