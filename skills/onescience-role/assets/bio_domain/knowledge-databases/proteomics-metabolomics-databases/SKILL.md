---
name: bio-proteomics-metabolomics-databases
description: 蛋白质组和代谢组数据库 skill。用于 PRIDE、PeptideAtlas、MassIVE、ProteomeXchange、HMDB、Metabolomics Workbench、RefMet、GNPS、mzML/raw 文件、肽段证据和代谢物谱库查询交接。
---

# 蛋白质组与代谢组数据库

## 使用边界

用于查找、下载或交叉链接蛋白质组/代谢组公共数据和谱库证据。若任务是实际处理 mzML 或做差异丰度，读取 `../../workflows/proteomics-metabolomics/SKILL.md` 或 `../../analysis-tools/mass-spectrometry-toolkit/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_knowledge_templates/omics_database_query.yaml`：研究、物种、组织、仪器、文件类型、代谢物/肽段字段模板。
- `references/proteomics_metabolomics_sources.md`：常用数据库、可返回字段和下载边界。

## 推荐流程

1. 明确查询目标：dataset、raw files、mzML、peptide PSM、protein evidence、metabolite、spectral match。
2. 标准化 ID：UniProt、peptide sequence、USI、InChIKey、HMDB ID、RefMet name、study accession。
3. 设过滤：organism、tissue、disease、instrument、assay type、quant method、sample count。
4. 输出：dataset accession、file URLs、metadata fields、license/access、版本日期和下游处理入口。

## 交接物

```yaml
database_family: proteomics-metabolomics
query_object:
identifier_type:
databases:
filters:
return_fields:
download_plan:
downstream_skill:
execution_entry:
```

## 禁止事项

- 不要把谱库匹配等同于已确认代谢物身份；必须说明 identification level。
- 不要下载大规模 RAW 文件前跳过文件大小、许可和存储计划。
- 不要混用 peptide evidence、protein inference 和 quantification evidence。
