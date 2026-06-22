---
name: bio-immune-repertoire-neoantigen
description: 免疫信息学 workflow skill。用于 TCR/BCR repertoire、VDJ、clonotype、MIXCR、scirpy、neoantigen prediction、MHC binding、epitope、immunogenicity scoring、tumor variant 到 neoantigen 等任务。
---

# 免疫组库与新抗原流程

## 使用边界

用于 TCR/BCR 组库、抗原表位、新抗原预测和免疫原性评分。若涉及临床用药建议，只输出技术证据，不给医疗建议。

## 推荐流程

1. 明确输入：VDJ FASTQ、AIRR table、single-cell VDJ、VCF + HLA、peptide list。
2. 组库分析：alignment/assembly、clonotype、CDR3、V/J usage、diversity、public clone。
3. 单细胞整合：TCR/BCR 与 scRNA cell type 关联。
4. 新抗原：somatic variant -> peptide generation -> HLA typing -> MHC binding -> expression/filter。
5. 输出：clonotype table、diversity plots、candidate peptide table、QC report。

## 交接物

```yaml
bio_task_family: immune-repertoire-neoantigen
input_object:
hla_or_receptor_info:
sample_context:
analysis_goal:
primary_tools:
qc_checkpoints:
candidate_filtering:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 binding score 直接等同于临床有效性。
- 不要忽略 HLA typing、肿瘤表达和 variant confidence。
- 不要混淆 bulk VDJ 和 single-cell VDJ 的 clonotype 口径。
