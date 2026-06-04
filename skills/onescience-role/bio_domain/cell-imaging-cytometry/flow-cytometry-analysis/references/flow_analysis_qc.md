# 流式分析 QC

## 预处理顺序

1. 读取 FCS 元数据和 channel-marker 映射。
2. 处理 acquisition anomalies：flow rate spike、time drift、margin events。
3. 应用 compensation 或 spectral unmixing。
4. 转换 fluorescence marker：logicle、biexponential 或 arcsinh。
5. Dead cell、debris 和 doublet 过滤。
6. 门控或聚类后做 condition-level 统计。

## 控制样本

- Unstained：背景和 autofluorescence。
- Single-stain：补偿矩阵。
- FMO：多色门控阈值。
- Isotype：非特异背景参考，不等价于 FMO。
- Beads：CyTOF 或仪器漂移归一化。

## 统计比较

Population frequency 常需要按样本聚合后比较，不要把单个 event 当独立生物重复。差异丰度应记录 design matrix、batch、donor、condition 和多重检验校正。
