---
name: bio-post-transcriptional-regulation
description: 转录后调控 workflow skill。用于 alternative splicing、differential splicing、Ribo-seq、small RNA/miRNA、CLIP-seq/RBP binding、m6A/epitranscriptomics、RNA modification calling 和 RNA 调控可视化交接。
---

# 转录后调控分析流程

## 使用边界

用于 RNA 加工、翻译、RNA binding、RNA modification 和剪接相关分析。若是普通 bulk RNA-seq 差异表达，读取 `../rnaseq-differential-expression/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_workflow_templates/post_transcriptional_plan.yaml`：assay、样本、参考、关键 QC、分析分支和输出模板。
- `references/post_transcriptional_methods.md`：splicing、Ribo-seq、small RNA、CLIP、m6A 的方法边界。

## 推荐流程

1. 明确 assay：rMATS/MAJIQ splicing、Ribo-seq、small RNA-seq、CLIP/eCLIP/iCLIP、MeRIP-seq、direct RNA modification。
2. 预处理：adapter trimming、read length、rRNA/tRNA contamination、alignment strategy、dedup/UMI。
3. 分析分支：
   - Splicing：junction reads、PSI、event type、sashimi plot。
   - Ribo-seq：P-site offset、3-nt periodicity、ORF calling、translation efficiency。
   - small RNA：size distribution、miRNA annotation、isomiR、differential abundance。
   - CLIP：crosslink site、peak calling、motif、target annotation。
   - m6A/RNA modification：IP/input、peak calling、metagene、stoichiometry 或 reactivity。
4. 输出：event/peak/modification table、QC figures、track files、可视化和解释边界。

## 交接物

```yaml
bio_task_family: workflows
assay_or_pipeline: post-transcriptional-regulation
assay:
input_reads_or_matrix:
reference_annotation:
sample_metadata:
qc_checkpoints:
analysis_branch:
expected_outputs:
downstream_links:
execution_entry:
```

## 禁止事项

- 不要把差异表达直接解释为差异剪接或翻译效率变化。
- CLIP/MeRIP 必须区分 input/control 和 biological replicate。
- Ribo-seq 必须检查周期性和 P-site offset 后再解释 ORF/翻译。
