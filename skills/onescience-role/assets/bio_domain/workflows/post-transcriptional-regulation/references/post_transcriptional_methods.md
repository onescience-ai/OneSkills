# 转录后调控方法参考

## Splicing

使用 junction reads 和 PSI 解释 exon skipping、A5SS/A3SS、MXE、intron retention。需要足够 junction coverage。

## Ribo-seq

关键 QC 是 read length、3-nt periodicity、P-site offset、start/stop codon enrichment 和 rRNA contamination。

## Small RNA

重点检查 adapter trimming、18-30 nt size distribution、miRNA/isomiR annotation 和 multi-mapping。

## CLIP

需要 crosslink-induced signal、input/control、peak calling、motif 和 target annotation。PCR duplicate/UMI 处理很关键。

## RNA modification

MeRIP-seq 依赖 IP/input peak；direct RNA modification 依赖模型版本、coverage 和 modification probability 阈值。
