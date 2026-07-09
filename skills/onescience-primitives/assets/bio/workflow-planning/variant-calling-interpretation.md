# 变异检测与解释工作流

- workflow_id: `variant-calling-interpretation`

## 适用范围

用于 germline/somatic SNP/indel、CNV、SV、long-read variant、VCF/BCF 过滤、注释和证据整理。典型触发包括 GATK、BCFtools、DeepVariant、Mutect2、CNVkit、ClinVar、gnomAD、COSMIC、VCF annotation 和关键变异摘要。

## 输入

- 必需：FASTQ/BAM/CRAM 或已有 VCF/BCF；reference build；样本元数据；目标分支。
- 分支输入：pedigree、tumor-normal pairing、target intervals、panel BED、caller 输出、覆盖统计、肿瘤纯度或 HLA/临床数据库需求。
- 可选：ClinVar、gnomAD、COSMIC、dbNSFP、OncoKB 类证据源。

## 输出

- filtered VCF/BCF。
- 注释表和优先级表。
- 过滤报告、覆盖/QC 报告、关键变异摘要。
- 人工复核项、证据来源和版本记录。

## 流程节点

1. 判定任务分支：germline、somatic、CNV、SV、mitochondrial、targeted panel 或 long-read variant。
2. 校验 reference build、BAM header、coverage、duplicate rate、contamination、sex check、pairing。
3. 选择 caller 和 filtering 策略，记录参数和阈值。
4. 标准化 VCF，进行 left-normalization、split multiallelic 和基本格式检查。
5. 添加 gene consequence、population frequency、clinical/cancer database、functional prediction 等注释。
6. 按 phenotype、gene panel、inheritance、VAF、depth、technical confidence 和数据库证据排序。
7. 输出技术证据和需人工复核项。

## 边界与分流

- 长读长平台预处理、read QC 和 alignment 先走 `long-read-sequencing-analysis`。
- GWAS、PRS、phasing-heavy 或群体遗传任务使用 `bio_population_phylo_app` 相关资源。
- 肿瘤变异到新抗原预测交给 `immune-repertoire-neoantigen`。
- 本工作流不输出临床诊断或治疗建议。

## 模型与工具选择边界

- short-read germline SNP/indel：GATK/DeepVariant/BCFtools 风格分支。
- tumor-normal somatic small variants：Mutect2 风格分支。
- CNV：CNVkit/ichorCNA 类分支。
- SV：Manta/Delly/Sniffles 等按平台选择。
- Evo2/AlphaGenome 只能辅助变异效应或调控建模，不是 caller。

## 质量检查

- BAM、VCF、BED、annotation 使用同一 reference build。
- coverage、mapping quality、duplicate、contamination、sample swap、sex check 可解释。
- allele depth、VAF、QUAL、FILTER、strand bias 等阈值有记录。
- 注释数据库版本和日期有记录。

## 回退策略

- 只有 VCF：跳过 calling，从 VCF QC、标准化、注释和证据整理开始。
- reference build 不明：暂停最终注释和解释，要求确认 build。
- 缺 tumor-normal pairing：按 tumor-only 风险处理，并显式标记假阳性风险。

## 资源召回建议

- 数据标准：`biology_genome_dataset`。
- 变异优先级和 biomarker 表：`bio_table_qc_biomarker_app`。
- 数据库查询：`bio_knowledge_query_app`。
- 报告：`bio_qc_report_app`。
