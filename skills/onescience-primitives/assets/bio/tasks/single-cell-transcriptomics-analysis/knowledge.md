# 单细胞转录组分析 (single-cell-transcriptomics-analysis)

## 任务目标
对单细胞 RNA-seq 数据执行完整分析流程：质控过滤、归一化、高变基因选择、降维（PCA/UMAP/t-SNE）、Leiden 聚类、marker 基因识别、细胞类型注释，以及可选的批次整合与 pseudobulk 差异表达。数据结构基于 AnnData（.h5ad），工具链以 Scanpy 1.12.x 为核心，支持 10X/CSV/loom/MTX 等多格式输入及 R 对象（Seurat/SCE .rds）转换。

## 适用范围 / 不适用场景
适用：scRNA-seq 探索性分析（.h5ad、10X、CSV 格式）；QC 过滤与双细胞检测（Scrublet）；UMAP/t-SNE/PCA 可视化；聚类与 marker 识别；细胞类型注释；轨迹推断/pseudotime；pseudobulk 聚合衔接 PyDESeq2；R-native 对象转换。
不适用：深度学习概率模型（应使用 scvi-tools）；空间转录组（应使用 squidpy）；bulk RNA-seq 差异表达；大规模群体查询（应使用 cellxgene-census）。

## 实体槽（Entity Slots）
- organism: 物种，决定线粒体基因前缀（human: MT-, mouse: mt-）
- input_format: 输入格式（h5ad / 10x_mtx / 10x_h5 / csv / loom / rds）
- batch_key: 批次整合键名（如 sample），无需整合则为空
- batch_method: 整合方法（harmony / bbknn / combat）
- n_top_genes: 高变基因数量（典型 2000-3000）
- n_pcs: PCA 主成分数（由 variance ratio plot 决定，典型 30-50）
- resolution: Leiden 聚类分辨率（0.4-1.2，越高聚类越细）
- qc_thresholds: QC 阈值组（min_genes 200-500, min_cells 3-10, pct_counts_mt 5-20%）

## 输入输出契约
输入：
- .h5ad 文件（AnnData 格式，cells×genes 矩阵 + obs/var 元数据）
- 或 10X 目录/h5 文件（通过 `sc.read_10x_mtx` / `sc.read_10x_h5` 加载）
- 或 R-native .rds（须先通过 Rscript 转换为 .h5ad）
- 可选：细胞类型映射 JSON（cluster→cell_type）

输出：
- processed.h5ad：含 QC 过滤后矩阵、归一化层（counts layer + raw）、HVG 标记、PCA/UMAP 嵌入、Leiden 聚类标签、marker 基因结果
- markers/*.csv：每 cluster 的 rank_genes_groups 结果表
- figures/：UMAP、dotplot、violin、heatmap 等可视化图像
- pseudobulk 矩阵（可选）：按 sample×cell_type 聚合的 counts，衔接 PyDESeq2

## 方法路线（可替换）
路线 A（一键流水线）：`scripts/run_pipeline.py raw.h5ad -o processed.h5ad` — 自动完成 load→QC→normalize→HVG→PCA→(batch)→UMAP→Leiden→markers，支持 `--config params.json` 复现参数。
路线 B（逐步链式）：qc_analysis.py → preprocess.py → reduce_dimensions.py → batch_correct.py → cluster.py → find_markers.py → annotate.py，每步产出 .h5ad 可检查中间结果。
路线 C（编程式）：直接使用 Scanpy API（sc.pp.filter_cells, sc.pp.normalize_total, sc.pp.log1p, sc.pp.highly_variable_genes, sc.pp.pca, sc.pp.neighbors, sc.tl.umap, sc.tl.leiden, sc.tl.rank_genes_groups）。
聚类：Leiden（`sc.tl.leiden`）为默认，louvain 已在 scanpy 1.12 中弃用。

## 操作序列（Operations）
1. 数据加载与检查：`sc.read_h5ad` / `sc.read_10x_mtx`；用 `inspect_data.py` 查看 shape、layers、已计算内容
2. QC 过滤：计算 `pct_counts_mt`（线粒体比例）；`sc.pp.filter_cells(min_genes=200)`；`sc.pp.filter_genes(min_cells=3)`；根据 QC 小提琴图选定阈值（非默认盲用）；可选 Scrublet 双细胞检测
3. 保存原始计数：`adata.raw = adata`（在基因过滤前执行）
4. 归一化：`sc.pp.normalize_total(target_sum=1e4)` → `sc.pp.log1p`
5. 高变基因选择：`sc.pp.highly_variable_genes(n_top_genes=2000)` → 子集 `adata[:, adata.var.highly_variable]`
6. 降维：`sc.pp.pca(n_comps=50)` → 检查 variance ratio 确定 n_pcs → `sc.pp.neighbors(n_neighbors=15, n_pcs=40)` → `sc.tl.umap()`
7. 批次整合（多样本时）：harmony / bbknn / combat（`sc.external.pp.harmony_integrate` 或 `sc.pp.combat(key='batch')`）
8. 聚类：`sc.tl.leiden(resolution=0.5)`；尝试多分辨率（0.3/0.5/0.8/1.0）选最优
9. Marker 识别：`sc.tl.rank_genes_groups(groupby='leiden', use_raw=True)`；导出每 cluster CSV
10. 细胞类型注释：基于 marker 基因手动/半自动映射 cluster→cell_type（`annotate.py --mapping celltypes.json`）
11. 保存结果：`adata.write_h5ad('processed.h5ad')`；中间步骤建议保存 checkpoint

## 验证契约（Validations）
- QC 阈值必须基于数据集实际分布选定，检查 QC 前后小提琴图（n_genes_by_counts, total_counts, pct_counts_mt）
- `adata.raw` 必须在 HVG 过滤前保存，后续 `use_raw=True` 绘图依赖此层
- PCA variance ratio plot 确认所选 n_pcs 覆盖足够方差（拐点之后）
- Leiden 聚类结果需生物学验证：marker 基因应匹配预期细胞类型
- 不可将 `rank_genes_groups` p-value 视为条件间严格 DE（应用 pseudobulk + PyDESeq2）
- R 对象不可在 Python 中直接解析 .rds，必须先转换
- scanpy 1.12 中 `sc.tl.louvain` 已弃用，`save=` 参数已弃用（用 `sc.settings.autosave=True`）
- 大数据集使用 backed mode（`ad.read_h5ad(backed='r')`）避免 OOM

## 资源引用（Resources）
- Scanpy 文档: https://scanpy.scverse.org/en/stable/
- AnnData 文档: https://anndata.readthedocs.io/
- scverse 生态: https://scverse.org/
- R 互操作 (zellkonverter): https://www.bioconductor.org/packages/release/bioc/html/zellkonverter.html
- SeuratDisk: https://mojaveazure.github.io/seurat-disk/
- 最佳实践: Luecken & Theis (2019) "Current best practices in single-cell RNA-seq"
- rapids-singlecell (GPU): https://rapids-singlecell.readthedocs.io/

## 前后置任务（Task Graph）
- 前置：无强制前后置（数据来源多样：10X 下机、公共数据集、R 对象转换）
- 后置：pseudobulk 聚合后可衔接 PyDESeq2 做条件间差异表达；marker 基因列表可衔接 pathway-enrichment 做功能富集

## 缺口与降级（Fallback / Gap）
- 无 Python 3.12+ 环境：scanpy 1.12 不支持 ≤3.11，须升级或退回旧版 scanpy（功能受限）
- Leiden 依赖缺失：需安装 `scanpy[leiden]` extra（含 python-igraph + leidenalg），否则 louvain 为降级选择但已弃用
- 大数据集 OOM：使用 backed mode + Dask 数组（实验性）或 rapids-singlecell (GPU)
- R 对象转换失败：确认 R 环境安装了 Seurat/SingleCellExperiment + zellkonverter/SeuratDisk，检查 counts/metadata 是否完整保留
- 批次整合效果差：尝试不同方法（harmony→bbknn→combat），或增加 n_pcs；极端情况降级为不整合、分样本独立分析
- Scrublet 不适用（无 10X 特征的物种/平台）：降级为基于 QC 指标的人工双细胞过滤（高 n_genes + 高 total_counts）
- pseudobulk 后样本数不足（< 3/组）：统计功效不够，降级为报告描述性结果或使用非参数检验
