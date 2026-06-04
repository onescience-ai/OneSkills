---
name: bio-public-data-ingestion
description: 公共生信数据接入 skill。用于 GEO/SRA/ENA/ArrayExpress、PubMed 附件、公共 FASTQ、count matrix、h5ad、VCF、PDB/mmCIF、mzML 等数据的 accession 解析、下载计划、样本元数据抽取和可复现数据清单生成。
---

# 公共数据接入

## 使用边界

用于数据发现和接入计划。涉及联网下载时，由执行层按权限处理；本 skill 负责 accession、文件类型和元数据交接。

## 推荐流程

1. 识别 accession 类型：GSE/GSM/SRR/PRJNA/ERP/DRR、PDB ID、BioProject、BioSample。
2. 获取 study metadata：样本、条件、平台、文库类型、物种、run accession。
3. 判断可下载对象：FASTQ、BAM、count matrix、supplementary files、processed object。
4. 生成 data manifest：sample ID、condition、batch、file URL/accession、checksum、target path。
5. 指定下游 workflow 和参考版本。

## 交接物

```yaml
bio_task_family: public-data-ingestion
accessions:
data_type:
organism_or_taxon:
sample_metadata:
download_manifest:
processed_files_available:
downstream_workflow:
execution_entry:
```

## 禁止事项

- 不要在未读样本元数据时把所有 SRR 当作同一实验条件。
- 不要下载前不规划磁盘空间和文件清单。
- 不要忽略受控访问或许可限制。
