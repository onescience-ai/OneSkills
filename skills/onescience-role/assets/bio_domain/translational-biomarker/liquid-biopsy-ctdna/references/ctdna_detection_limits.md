# ctDNA 检测边界

## 低 VAF

- >1 percent VAF 通常更稳定，但仍需 depth、strand、UMI 和背景错误检查。
- 0.5-1 percent VAF 需要深度和错误抑制支持。
- 0.1-0.5 percent VAF 接近很多 assay 的噪声区，必须依赖验证过的 UMI/error model。
- <0.1 percent VAF 不应默认解释为可靠阳性。

## CHIP 与 Germline

DNMT3A、TET2、ASXL1、PPM1D、JAK2、SF3B1、SRSF2、TP53 等基因中的变异可能来自 clonal hematopoiesis。优先使用 matched WBC 或纵向/组织证据过滤。

## Fragmentomics 与甲基化

Fragment size、end motif、nucleosome footprint 和甲基化 signal 常受 pre-analytical 变量影响，需要记录采血管、处理时间、建库方法和批次。
