---
name: bio-genome-assembly-annotation
description: 基因组组装、注释和比较基因组 workflow skill。用于 short-read/long-read/HiFi assembly、polishing、scaffolding、BUSCO、contamination、Prokka、eukaryotic gene prediction、repeat/ncRNA/functional annotation、ortholog、synteny、selection 等任务。
---

# 基因组组装与注释流程

## 使用边界

用于从 reads 到 assembly、annotation 和 comparative genomics。若是单个序列格式转换，进入 `data-foundation/sequence-io-manipulation`。

## 推荐流程

1. 明确物种、基因组大小、倍性、测序平台、coverage、是否有 Hi-C/linked reads。
2. assembly：SPAdes/MEGAHIT/Flye/hifiasm 等按数据类型选择。
3. polishing/scaffolding：短读纠错、long-read polishing、Hi-C scaffolding。
4. QC：N50、BUSCO、QUAST、k-mer、contamination、coverage。
5. annotation：prokaryotic/eukaryotic gene prediction、repeat、ncRNA、functional annotation。
6. comparative：ortholog、synteny、phylogeny、selection、HGT。
7. 输出：FASTA、GFF/GTF、protein/CDS FASTA、QC report、annotation summary。

## 交接物

```yaml
bio_task_family: genome-assembly-annotation
organism_or_taxon:
sequencing_platform:
estimated_genome_size:
coverage:
assembly_strategy:
annotation_strategy:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要用单一 N50 判断 assembly 质量。
- 不要忽略污染、倍性和重复序列。
- 不要把原核注释流程直接套到真核基因组。
