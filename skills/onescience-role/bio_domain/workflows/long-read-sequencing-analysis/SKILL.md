---
name: bio-long-read-sequencing-analysis
description: 长读长测序分析 workflow skill。用于 Nanopore 或 PacBio 的 basecalling、read QC、long-read alignment、SV calling、Iso-Seq、direct RNA、nanopore methylation、phasing、assembly polishing 和长读长交付。
---

# 长读长测序分析流程

## 使用边界

用于 ONT/PacBio 长读长数据从原始信号或 reads 到变异、转录本、甲基化、组装或单倍型结果的链路。若任务是从头组装和注释大基因组，读取 `../genome-assembly-annotation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_workflow_templates/long_read_run_plan.yaml`：平台、basecalling、QC、比对、SV/Iso-Seq/methylation/phasing 和输出模板。
- `references/long_read_decision_guide.md`：ONT/PacBio 数据类型、工具选择、QC 指标和常见失败点。

## 推荐流程

1. 明确平台和数据：ONT POD5/FAST5/FASTQ、PacBio HiFi/subreads、direct RNA、Iso-Seq、adaptive sampling。
2. 预处理/QC：read length N50、Q-score、yield、adapter/chimeric read、contamination、barcode demultiplex。
3. 比对：minimap2 或平台特异流程，记录 preset、reference build、supplementary alignment。
4. 分析分支：
   - SV/CNV：read depth、split read、assembly support、benchmark truth set。
   - Iso-Seq/direct RNA：full-length read、transcript collapse、SQANTI-style QC、novel isoform。
   - methylation：modified base calling、modkit-style pileup、coverage threshold。
   - phasing：haplotag、phase block N50、trio/HiFi/ONT support。
5. 输出：BAM/CRAM、VCF/BED、transcript GTF/FASTA、methylation bedMethyl、QC report。

## 交接物

```yaml
bio_task_family: workflows
assay_or_pipeline: long-read-sequencing-analysis
platform:
input_data:
reference_build:
basecalling_or_read_source:
qc_checkpoints:
analysis_branch:
core_tools:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要混用 ONT raw signal、ONT FASTQ、PacBio HiFi 的 QC 指标。
- 不要在没有 read length、coverage 和 Q-score 的情况下判断 SV/isoform 可靠性。
- Nanopore methylation 必须写明 modified-base model、coverage 阈值和 motif/strand 处理。
