---
name: bio-pathogen-genomic-surveillance
description: 病原基因组监测与暴发分析 skill。用于病原 SNP/lineage、样本元数据、聚类、系统树、时间尺度传播分析、耐药或毒力标记、监测报告和公共卫生交接。
---

# 病原基因组监测

## 使用边界

用于细菌、病毒、真菌或寄生虫基因组监测、暴发聚类、lineage/variant assignment 和时间序列传播分析。若任务只是微生物组群落组成，读取 `../../workflows/microbiome-metagenomics/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_population_templates/pathogen_surveillance_metadata.csv`：样本、采集时间、地点、宿主、lineage、测序和质控模板。
- `references/pathogen_surveillance_workflow.md`：监测分析、元数据、聚类和报告边界。

## 推荐流程

1. 明确病原体和数据：assembly、reads、consensus FASTA、VCF、lineage scheme。
2. QC：coverage、Ns、contamination、mixed infection、reference bias、sample duplicates。
3. 变异/lineage：SNP calling、mask problematic regions、lineage/clade assignment、AMR/virulence marker。
4. 聚类与系统树：SNP distance、ML tree、time-resolved tree、metadata annotation。
5. 解释：结合采样时间地点和流行病学证据，不直接声称传播方向。
6. 输出：监测表、cluster list、tree、QC flags、报告摘要。

## 交接物

```yaml
bio_task_family: population-phylo-evolution
evolution_task: pathogen-genomic-surveillance
pathogen:
input_data:
metadata:
qc_filters:
lineage_or_variant_scheme:
cluster_definition:
phylogenetic_analysis:
public_health_boundary:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要只凭系统树拓扑断言直接传播。
- 不要忽略采样时间、地点、测序批次和低覆盖样本。
- 不要混用不同 lineage scheme 或参考版本。
