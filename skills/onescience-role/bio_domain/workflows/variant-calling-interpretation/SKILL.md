---
name: bio-variant-calling-interpretation
description: 变异检测与解释 workflow skill。用于 germline/somatic SNP/indel、CNV、SV、long-read variant、VCF 过滤注释、ClinVar/gnomAD/COSMIC 查询、GATK/BCFtools/DeepVariant/Mutect2/CNVkit 等任务。
---

# 变异检测与解释流程

## 使用边界

用于 DNA/RNA 测序变异任务。先区分 germline、somatic、cohort joint calling、target panel、WES/WGS、long-read。

## 可复用资源

- `onescience-coder/assets/bio_workflow_templates/cohort_sample_map.tsv`：GVCF joint calling 或 cohort annotation 的样本映射模板。

当用户要组织 cohort calling 或批量注释时，先用该模板明确 sample、path 和 status。

## 推荐流程

1. 明确样本类型、测序平台、参考版本、目标区域、tumor/normal 配对。
2. 预处理：BAM sort/index、mark duplicates、BQSR 或平台特异校正。
3. calling：
   - germline：HaplotypeCaller/DeepVariant，cohort 用 GVCF/joint genotyping。
   - somatic：Mutect2/Strelka 类路线，考虑 panel of normals、contamination。
   - CNV/SV：CNVkit/GATK CNV/minimap2/Sniffles/Clair3 等按平台选择。
4. filtering：VQSR 或 hard filters；记录过滤表达式。
5. annotation：SnpEff/VEP/ANNOVAR、ClinVar、gnomAD、COSMIC、dbSNP 等。
6. 输出：VCF/BCF、过滤报告、注释表、关键变异摘要。

## QC 检查点

- coverage、mapping rate、duplicate rate、insert size、contamination。
- Ti/Tv、het/hom ratio、known/novel ratio。
- somatic VAF 分布、tumor purity、strand bias。

## 交接物

```yaml
bio_task_family: variant-calling
sample_context:
sequencing_platform:
reference_build:
target_regions:
caller_strategy:
filter_strategy:
annotation_sources:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要混用不同 reference build 的 BAM、VCF、BED 和 annotation。
- 不要把 germline caller 用于 somatic 结论。
- 不要给出临床诊断结论；只整理技术证据和需人工复核项。
