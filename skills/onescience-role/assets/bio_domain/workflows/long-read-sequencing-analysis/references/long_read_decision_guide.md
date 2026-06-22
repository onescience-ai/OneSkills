# 长读长分析决策参考

## ONT

ONT 数据可能从 POD5/FAST5 basecall，也可能已经是 FASTQ/BAM。需要记录 basecaller、model、duplex/simplex、modified base model 和 barcode kit。

## PacBio

PacBio HiFi 通常以高准确度 CCS reads 为核心；subreads 和 HiFi reads 的 QC 与错误模型不同。

## 常见分支

- SV：需要覆盖度、read length、split read 支持和过滤 false positives。
- Iso-Seq：需要 full-length non-chimeric read、transcript collapse 和注释比较。
- Methylation：需要 modified-base model、coverage、motif 和 strand 处理。
- Phasing：需要 phase block、haplotag 和 family/trio/reference 支持。
