# 系统发育树推断 (phylogenetic-tree-inference)

## 任务目标
从核酸或蛋白质 FASTA 序列出发，经多序列比对（MAFFT）、可选比对修剪（TrimAl）、最大似然树推断（IQ-TREE 2 或 FastTree），产出带分支支持值的 Newick 树文件，并使用 ETE3 进行 rooting、统计分析与可视化渲染。适用于进化关系推断、病毒系统动力学、蛋白家族分析、分子钟定年等场景。

## 适用范围 / 不适用场景
适用：基因/蛋白/基因组序列的进化关系重建；病毒爆发传播追踪与分化时间估计；蛋白家族系统发育；水平基因转移检测（对比物种树与基因树）；祖先序列重建；16S rRNA 或核心基因组微生物系统发育。
不适用：仅做序列比对而无需建树（MAFFT 单独即可）；群体遗传学/GWAS（无建树需求）；结构变异检测；需要贝叶斯推断（MrBayes/BEAST）的严格后验概率场景（本技能覆盖 ML 路线）。

## 实体槽（Entity Slots）
- sequence_type: 序列类型（nt=核酸 / aa=蛋白质），决定模型与 FastTree 参数
- input_fasta: 未比对 FASTA 文件路径
- n_sequences: 序列数量，决定工具选择（<200 精确比对, >1000 快速方法, >5000 用 FastTree）
- mafft_method: MAFFT 比对策略（auto / linsi / einsi / fftnsi / fftns / retree2）
- substitution_model: 替代模型（TEST 自动选择 / GTR+G4 / HKY+G4 / LG+G4 / WAG+G4）
- bootstrap: 超快自举重复数（推荐 ≥1000）
- rooting_method: 定根方式（outgroup 指定 / midpoint rooting）
- use_fasttree: 是否用 FastTree 替代 IQ-TREE（大数据集加速）

## 输入输出契约
输入：
- 未比对 FASTA 文件（核酸 .fasta/.fna 或蛋白 .faa）
- 可选：outgroup 物种名列表（用于定根）
- 可选：dates.txt（分子钟分析时的采样日期）

输出：
- 比对后 FASTA：`*_aligned.fasta`（MAFFT 产出）
- 修剪后 FASTA（可选）：TrimAl 产出
- Newick 树文件：`*.treefile`（IQ-TREE）或 `*.tree`（FastTree）
- 定根后 Newick：`*_rooted.nwk`（ETE3 midpoint/outgroup 定根后写出）
- IQ-TREE 报告：`*.iqtree`（含最佳模型、似然值、分支支持）
- 可视化图像：`*_tree.png`（ETE3 渲染，矩形或圆形布局）
- 树统计摘要：n_leaves、n_internal_nodes、total_branch_length、max/mean_leaf_distance

## 方法路线（可替换）
路线 A（标准 ML，≤5000 序列）：MAFFT 比对 → TrimAl 修剪 → IQ-TREE 2（`-m TEST -B 1000 -T AUTO`）自动模型选择 + 超快自举 → ETE3 定根与可视化。
路线 B（快速近似 ML，>5000 序列）：MAFFT（fftns/auto）→ FastTree（核酸: `-nt -gtr`；蛋白: `-lg`）→ ETE3 定根。速度快 10-100× 但精度略低。
路线 C（分子钟/定年）：在 IQ-TREE 基础上追加 `--date dates.txt --clock-test --date-CI 95` 进行时间校准树推断。
比对策略选择：< 200 序列用 linsi/einsi（精确）；200-1000 用 fftnsi；> 1000 用 fftns/auto；> 10000 用 `--retree 1`。

## 操作序列（Operations）
1. 安装环境：`conda install -c bioconda mafft iqtree fasttree trimal`；`uv pip install ete3 PyQt5`
2. 多序列比对：`run_mafft(input_fasta, output_fasta, method="auto", n_threads=4)`；验证比对序列数与输入一致
3. 比对修剪（推荐）：`trimal -automated1 -in aligned.fasta -out trimmed.fasta -fasta`；去除高 gap 列提升树精度
4. 模型选择与建树（IQ-TREE）：`iqtree2 -s aligned.fasta --prefix phylo -m TEST -B 1000 -T 4 --redo`；检查 .log 中 "Best-fit model" 行确认所选模型
5. 或快速建树（FastTree）：`FastTree -nt -gtr aligned.fasta > output.tree`（核酸）/ `FastTree -lg aligned.fasta`（蛋白）
6. 加载树并定根：`t = Tree(tree_file)` → `t.set_outgroup(t.get_midpoint_outgroup())`（无 outgroup 时用 midpoint）
7. 树统计分析：计算 n_leaves、total_branch_length、max/mean_leaf_distance；查找 MRCA（`t.get_common_ancestor(*leaf_names)`）
8. 可视化渲染：ETE3 TreeStyle（mode="r" 矩形 / "c" 圆形），设置 show_branch_support=True，可选 color_groups 着色；`t.render(output_file, tree_style=ts, w=800, units="px")`
9. 剪枝（可选）：`t.prune(keep_leaves, preserve_branch_length=True)` 保留目标类群
10. 保存定根树：`t.write(format=1, outfile="*_rooted.nwk")`

## 验证契约（Validations）
- 比对质量优先：poor alignment → unreliable tree；建建树前手动检查比对（特别关注 gap-rich 区域）
- MAFFT 输出序列数必须等于输入序列数（检查 `>` 行数）
- IQ-TREE `-m TEST` 自动模型选择为默认推荐，除非有明确理由指定固定模型
- 自举支持值 ≥ 70% 视为分支可信（超快自举 `-B 1000`）
- 必须定根：未定根树可能误导进化方向解读；有明确 outgroup 用 outgroup，否则 midpoint
- 病毒/细菌序列建树前检查重组（RDP4, GARD），重组区域须排除或分区分析
- 不可混用不同替代模型跨数据集比较树拓扑
- TrimAl 失败时降级使用未修剪比对（脚本已内置 fallback copy）
- ETE3 图像渲染需 PyQt5；纯解析/统计无需 Qt 依赖

## 资源引用（Resources）
- MAFFT: https://mafft.cbrc.jp/alignment/software/
- IQ-TREE 2: http://www.iqtree.org/
- FastTree: http://www.microbesonline.org/fasttree/
- ETE3: http://etetoolkit.org/
- TrimAl: https://vicfero.github.io/trimal/
- FigTree (GUI): https://tree.bio.ed.ac.uk/software/figtree/
- iTOL (Web 可视化): https://itol.embl.de/
- MUSCLE (替代比对器): https://www.drive5.com/muscle/

## 前后置任务（Task Graph）
无强制前后置。输入为独立 FASTA 序列文件，输出 Newick 树可衔接下游可视化（iTOL/FigTree）或比较基因组学分析。

## 缺口与降级（Fallback / Gap）
- IQ-TREE 对 >5000 序列过慢：降级至 FastTree（速度快 10-100×，精度略低但可接受用于大规模筛查）
- MAFFT linsi/einsi 对 >200 序列过慢：降级至 fftnsi（中等）或 fftns/auto（快速）
- TrimAl 未安装或修剪失败：脚本内置 fallback — 直接复制未修剪比对继续建树
- 无明确 outgroup：使用 midpoint rooting（`t.get_midpoint_outgroup()`）作为替代
- PyQt5 不可用（无 GUI 环境）：ETE3 树解析和统计正常工作，仅图像渲染失败；降级为导出 Newick 用 iTOL 在线可视化
- 需要贝叶斯后验概率而非 ML 自举：超出本技能范围，需 MrBayes/BEAST（本技能不覆盖）
- 序列含重组区域：建树前须用 RDP4/GARD 检测并排除重组区段，否则树拓扑不可靠
