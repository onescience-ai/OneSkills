---
name: bio-liquid-biopsy-ctdna
description: 液体活检 cfDNA 和 ctDNA 分析 skill。用于 cfDNA preprocessing、UMI consensus、低 VAF 突变检测、tumor fraction、fragmentomics、甲基化检测、纵向 MRD 监测和报告交接。
---

# 液体活检 cfDNA/ctDNA 分析

## 使用边界

用于 plasma cfDNA/ctDNA 的检测、定量和纵向监测。若是普通 tumor/normal WES 变异分析，优先读取 `../../workflows/variant-calling-interpretation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/liquid_biopsy_panel.yaml`：panel、UMI、深度、目标突变、纵向采样和输出模板。
- `references/ctdna_detection_limits.md`：低 VAF、CHIP、UMI、tumor fraction、fragmentomics 和 MRD 边界。
- `onescience-coder/assets/bio_table_qc_tools/ctdna_vaf_panel.py`：从目标位点 read count 表计算 VAF 和低深度/低 alt count flag。

## 推荐流程

1. 明确 assay：targeted panel、WES、sWGS、cfMeDIP/bisulfite、fragmentomics。
2. 预处理：adapter trimming、短片段优化比对、UMI consensus、duplicate/error suppression。
3. 变异或负荷：low-VAF caller、targeted mutation tracking、ichorCNA/tumor fraction、methylation/fragment features。
4. 过滤：depth、alt count、strand/UMI family、panel of normals、CHIP gene、germline contamination。
5. 纵向分析：baseline、nadir、molecular response、relapse signal、采样间隔和置信区间。
6. 输出：mutation/VAF table、tumor fraction、QC、trend plot、临床审核边界。

## 交接物

```yaml
bio_task_family: translational-biomarker
translational_task: liquid-biopsy-ctdna
assay:
sample_series:
panel_or_targets:
umi_strategy:
qc_thresholds:
variant_or_burden_method:
chip_and_germline_filter:
longitudinal_interpretation:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要把 <0.1 percent VAF 的信号当成可靠阳性，除非给出经过验证的 UMI/error model。
- 不要忽略 CHIP、白细胞对照和 germline 过滤。
- 不要把研究型 MRD 趋势写成临床诊疗建议。
