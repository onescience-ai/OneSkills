---
name: bio-proteomics-metabolomics
description: 蛋白质组、代谢组、脂质组和质谱数据 workflow skill。用于 mzML/mzXML、DDA/DIA、peptide identification、protein inference、differential abundance、PTM、XCMS、MS-DIAL、feature alignment、metabolite annotation 等任务。
---

# 蛋白质组与代谢组流程

## 使用边界

用于 LC-MS/MS、DIA、DDA、targeted metabolomics、untargeted metabolomics、lipidomics。若用户要蛋白结构预测，进入 `onescience-models`。

## 推荐流程

1. 明确 raw/vendor 格式、是否已转换 mzML、DDA/DIA/targeted 类型。
2. 蛋白质组：search database、enzyme、FDR、peptide/protein inference、quantification、batch normalization。
3. 代谢组：feature detection、RT alignment、blank correction、adduct/isotope、compound annotation。
4. 差异分析：统计设计、batch correction、multiple testing、effect size。
5. 输出：feature/peptide/protein/metabolite table、QC plots、volcano/heatmap、annotation confidence。

## QC 检查点

- TIC/BPC、feature count、missingness、retention time drift。
- PSM/peptide/protein FDR。
- blank/sample carryover、QC pool stability。

## 交接物

```yaml
bio_task_family: proteomics-metabolomics
ms_data_type:
input_object:
search_or_annotation_database:
quantification_strategy:
normalization_strategy:
qc_checkpoints:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把低置信 metabolite annotation 当作确定结构。
- 不要忽略 FDR、blank 和 batch。
- 不要把蛋白组差异丰度与 RNA-seq 差异表达混为同一统计模型。
