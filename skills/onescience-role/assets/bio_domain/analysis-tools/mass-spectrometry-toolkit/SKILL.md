---
name: bio-mass-spectrometry-toolkit
description: 质谱分析工具 skill。用于 PyOpenMS、OpenMS、matchms、mzML/mzXML、feature detection、RT alignment、spectral similarity、peptide/protein identification、metabolite annotation 和 MS 数据结构处理。
---

# 质谱工具箱

## 工具选择

- 原始/开放格式读取：mzML、mzXML、mzTab、idXML、featureXML。
- signal processing：smoothing、centroiding、baseline、normalization。
- feature detection：LC-MS feature picking、RT alignment、consensus map。
- peptide/protein ID：search result 读取、FDR、protein inference。
- metabolomics：spectral similarity、library matching、annotation confidence。

## 交接物

```yaml
tool_family: mass-spectrometry
input_format:
ms_level:
analysis_goal:
search_or_library_database:
feature_or_identification_strategy:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要混淆 MS1 feature detection 和 MS2 identification。
- 不要在没有 FDR 或 annotation level 时输出确定鉴定。
- 不要忽略 retention time alignment 和 batch QC。
