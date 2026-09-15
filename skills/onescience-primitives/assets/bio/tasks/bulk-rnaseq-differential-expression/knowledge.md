# Bulk RNA-seq 差异表达分析 (bulk-rnaseq-differential-expression)

## 任务目标
从原始 FASTQ 测序数据出发，经质控、修剪、比对/定量，生成基因级 counts 矩阵，使用 PyDESeq2 完成差异表达分析（Wald 检验 + BH FDR 校正），输出显著差异基因列表（padj < 0.05）并衔接下游通路富集与可视化。全流程强调可重复性（版本锁定、固定种子）、质量门控（QC 前后检查）与统计严谨性（充分重复、正确设计公式）。

## 适用范围 / 不适用场景
适用：Bulk RNA-seq（样本=生物个体/组织），有 FASTQ 或已定量输出，需要完整差异表达工作流；实验设计审查（重复数、批次、链方向）。
不适用：单细胞/单核 RNA-seq（应使用 scanpy 流程）；仅需富集分析而无 DE 步骤；蛋白质组学或非转录组数据。

## 实体槽（Entity Slots）
- organism: 物种（如 human/mouse），决定参考基因组与注释版本
- reference_genome: 参考基因组（如 GRCh38），需锁定版本
- design_formula: 设计公式（如 `~batch + condition`），调整变量置前
- contrast: 对比定义 `[variable, test_level, reference_level]`
- aligner: 比对/定量工具选择（STAR / Salmon / featureCounts）
- pipeline_path: 上游路径选择（nf-core/rnaseq 或 standalone tools）
- replicates_per_group: 每组生物学重复数（≥3 为最低要求）
- strandedness: 链方向（unstranded/forward/reverse），Salmon 可用 `-l A` 自动推断

## 输入输出契约
输入：
- 原始 FASTQ 文件（paired-end 或 single-end）+ samplesheet.csv（样本元数据）
- 或已定量的 Salmon quant.sf / STAR ReadsPerGene.out.tab / featureCounts 输出
- tx2gene 映射表（Salmon 路径需要）

输出：
- counts.csv：基因×样本整数矩阵（PyDESeq2 要求整数）
- metadata.csv：样本元数据（行=样本，含 condition/batch 列）
- DE 结果表：含 baseMean、log2FoldChange、stat、pvalue、padj 列
- 显著基因子集：padj < 0.05，可选 |log2FC| > 1 双重过滤
- 可视化：volcano plot、MA plot、PCA、dispersion 分布、p-value 直方图

## 方法路线（可替换）
路线 A（推荐）：nf-core/rnaseq (Nextflow) — 一条命令完成 FastQC→trim→STAR/Salmon→tximport→MultiQC，内部已做 gene counts 合并，输出 `salmon.merged.gene_counts_length_scaled.tsv` 可直接用于 DE。
路线 B：Standalone tools — FastQC + fastp/Trim Galore 修剪 → STAR `--quantMode GeneCounts` 或 Salmon quasi-mapping（decoy-aware index, `--gcBias --seqBias`）→ `build_counts_matrix.py` 聚合。
DE 引擎：PyDESeq2 0.5.x（Python），DeseqDataSet 拟合 + DeseqStats Wald 检验；可选 apeGLM LFC shrinkage 用于排序/可视化。

## 操作序列（Operations）
1. 实验设计验证：确认 ≥3 生物学重复/组，识别批次混杂，构建 samplesheet 并用 `validate_samplesheet.py` 校验
2. 原始 reads QC：FastQC 逐文件 + MultiQC 聚合；检查 per-base quality、adapter content、duplication
3. 修剪：fastp（`--thread 4`）或 Trim Galore 去除接头/低质量尾部；修剪后重跑 FastQC 确认
4. 比对/定量：STAR genome align + GeneCounts，或 Salmon quant（`-l A` 自动链推断，`--gcBias --seqBias`）
5. 构建 counts 矩阵：`build_counts_matrix.py --from salmon --quant-dir quant/ --tx2gene tx2gene.tsv`；Salmon 估计值用 `counts_from_abundance="length_scaled_tpm"` 聚合后四舍五入为整数
6. PyDESeq2 差异表达：加载 counts_df（samples×genes，需 `.T` 转置）+ metadata → 过滤低计数基因（sum ≥ 10）→ 设定 Categorical 参考水平 → `DeseqDataSet(design="~batch + condition", refit_cooks=True)` → `dds.deseq2()` → `DeseqStats(contrast=[...])` → `ds.summary()`
7. 结果解读：`ds.results_df` 提取 padj < 0.05 显著基因；可选 `ds.lfc_shrink(coeff="condition[T.treated]")` 用于排序
8. QC 后检：检查 size_factors 是否接近 1、dispersion 分布、p-value 直方图（应近似平坦 + 0 附近峰）、PCA/样本距离热图

## 验证契约（Validations）
- Counts 矩阵必须为整数（PyDESeq2 硬性要求），Salmon 估计值已四舍五入
- 绝不可将 TPM/FPKM/归一化值输入 DESeq2
- samplesheet 索引与 counts 列名必须完全匹配（取 intersection 若不一致）
- 数据方向：counts_df 需为 samples×genes（行=样本），若 genes > samples 则需 `.T`
- 设计矩阵满秩检查：`pd.crosstab(condition, batch)` 排除混杂
- padj（BH 校正）用于显著性判定，非 raw p-value
- 所有样本必须使用相同工具、版本、参考基因组和参数定量
- Pipeline 版本锁定：`nextflow run -r 3.26.0`，工具 conda 版本 pin

## 资源引用（Resources）
- nf-core/rnaseq: https://nf-co.re/rnaseq
- STAR: https://github.com/alexdobin/STAR
- Salmon: https://salmon.readthedocs.io
- fastp: https://github.com/OpenGene/fastp
- MultiQC: https://multiqc.info
- pytximport: https://pytximport.complextissue.com
- PyDESeq2: https://pydeseq2.readthedocs.io (Muzellec et al. 2023, DOI: 10.1093/bioinformatics/btad547)
- DESeq2 方法学: Love et al. 2014, DOI: 10.1186/s13059-014-0550-8
- tximport: Soneson et al. 2015, DOI: 10.12688/f1000research.7563.2

## 前后置任务（Task Graph）
- 前置：无强制前后置（原始数据来源多样，实验设计审查建议在定量前完成）
- 后置：DE 结果表可衔接 pathway-enrichment（ORA 用 padj+|LFC| 阈值命中列表，GSEA 用 stat 全排名）；可视化衔接 scientific-visualization

## 缺口与降级（Fallback / Gap）
- 重复数不足（< 3）：统计功效极低、dispersion 估计不稳定，应增加重复而非加深测序
- 批次与条件完全混杂：效果不可恢复，降级为仅报告 `~condition` 设计但须在方法中声明局限
- 链方向选错：Salmon `-l A` 自动推断为默认安全选择；若 STAR/featureCounts 选错列则 counts 约减半，验证 assigned-reads fraction
- Salmon 非整数 counts：bridge 脚本四舍五入可接受（length_scaled_tpm 模式），替代方案为 DESeq2+tximport offset 路线
- 基因 ID 不匹配（Ensembl→Symbol）：在富集前必须映射，否则"nothing is significant"
- 无 Nextflow/容器环境：退回 Path B standalone tools，conda 安装并 pin 版本
- PyDESeq2 不可用或版本不兼容：降级至 R DESeq2，输入格式一致
