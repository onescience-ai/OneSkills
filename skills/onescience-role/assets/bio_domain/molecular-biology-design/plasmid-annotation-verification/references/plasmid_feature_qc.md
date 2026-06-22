# 质粒 Feature QC

## 常见元件

- Replication origin：pUC/ColE1、p15A、SV40、oriP 等，需与宿主系统匹配。
- Selectable marker：ampicillin、kanamycin、puromycin、hygromycin 等，需与宿主和培养条件匹配。
- Expression cassette：promoter、enhancer、RBS/Kozak、CDS、tag/linker、terminator/polyA。
- Cloning elements：MCS、restriction sites、attB/attP、loxP/FRT、barcode、sgRNA scaffold。

## 核对重点

- CDS 是否 in-frame，fusion tag 是否保持 linker 和 stop codon 逻辑。
- Promoter 与 ORF 方向是否一致。
- Circular feature 是否跨 origin，需要拆分或明确 wraparound。
- 提交共享前需输出 GenBank、feature table、质粒全长、抗性和宿主系统。
