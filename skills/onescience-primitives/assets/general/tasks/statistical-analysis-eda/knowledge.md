# 统计分析与探索性数据分析 (statistical-analysis-eda)

## 任务目标
对已采集的研究数据执行完整的分析流程：先通过有界 EDA 了解数据结构、缺失模式与分布特征，再选定假设检验/回归/贝叶斯模型，验证前提假设，计算效应量，最终以 APA 格式输出可辩护的统计报告。目标是一个审稿人无法击穿的完整分析链。

## 适用范围 / 不适用场景
适用：组间比较（t 检验/ANOVA/非参数）、相关与回归（线性/logistic/Poisson）、贝叶斯建模（PyMC）、分类数据分析（卡方/Fisher）、前提假设诊断、效应量与置信区间报告、APA 格式撰写、有界 CSV/TSV/JSON/NPY/HDF5/FASTA/TIFF 等格式的数据画像与缺失审计。
不适用：数据采集前的实验设计与功效分析（应转 experimental-design-power-analysis）；需要网络调用或超出授权根目录的文件访问；自动删除异常值/插补/覆写原始数据；从 EDA 结果做因果/临床/机制性断言；未被自动化层支持的专有格式（PDB/SAM/BAM/VCF/DICOM 等需领域工具）。

## 实体槽（Entity Slots）
- test_type：检验类型（t_ind / t_paired / anova / kruskal / chi2 / fisher / pearson / spearman / ols / logistic / bayesian_ttest）
- outcome_variable：因变量列名
- predictor_variables：自变量/分组变量列名
- group_variable：分组列（若适用）
- data_format：输入数据格式（csv / tsv / json / npy / npz / h5 / fasta / fastq / tiff）
- assumption_checks_required：需执行的前提检验集合（normality / homogeneity / linearity / outliers / independence）
- effect_size_measure：效应量指标（cohen_d / eta_p2 / r / R2 / cramers_v / hedges_g / rank_biserial）
- alpha：显著性水平，默认 0.05
- root_dir：EDA 授权数据根目录（安全边界）

## 输入输出契约
输入：已采集的数据文件（CSV/TSV/JSON 等）、数据字典（变量含义/单位/允许范围）、研究设计描述（独立/配对、组数、是否重复测量）、预设假设与计划检验。
输出：
1. EDA 报告（JSON/Markdown）：schema、分布统计、缺失模式、异常值标记、组间泄漏审计结果；
2. 前提假设检查结果（Shapiro-Wilk / Levene / Q-Q 图 / VIF / 残差图）及通过/违反判定；
3. 检验结果：统计量、df、精确 p 值、效应量及 95% CI；
4. 后事后检验（Tukey HSD / Holm / BH-FDR）结果（若 ANOVA 显著）；
5. APA 格式完整报告段落（含描述统计、检验统计、效应量、假设检查结果、所有计划分析含非显著发现）；
6. 可复现脚本与随机种子。

## 方法路线（可替换）
A. 频率学派路线（pingouin + statsmodels + scipy）：标准检验首选，自动返回效应量；pg.ttest(correction='auto') 自动 Welch 校正；pg.anova + pg.pairwise_tukey 完成方差分析与后事后；statsmodels OLS + check_regression_diagnostics 完成回归全套诊断。
B. 贝叶斯路线（PyMC + ArviZ）：小样本/序贯数据/需量化零假设支持/有先验信息时使用；pm.sample(2000, tune=1000)；ArviZ 1.x 默认 89% CI，报告用 ci_prob=0.95；单侧贝叶斯需 PyMC 直接计算后验概率（pingouin 已移除单侧 BF）。
C. 非参数路线：正态性中度/严重违反或 n 小且无法变换时，Mann-Whitney U / Wilcoxon / Kruskal-Wallis / Friedman；报告 rank-biserial 相关（pg.mwu 返回 RBC）。
D. EDA 有界自动化路线：capability_manifest.py 确定格式层级 → eda_analyzer.py / tabular_profile.py / missingness_leakage_audit.py / distribution_sensitivity.py 逐步执行，所有输出为 JSON/Markdown，不修改原始数据。

## 操作序列（Operations）
1. 确认数据文件在授权 root 内；运行 capability_manifest.py inspect 判断格式层级。
2. 执行有界 EDA：tabular_profile.py 获取 schema 与分布画像；missingness_leakage_audit.py 审计缺失与分组泄漏；distribution_sensitivity.py 检查异常值与变换灵敏度。
3. 在检验前明确假设、结局变量、预测变量、设计类型；承诺计划检验（避免 p-hacking）。
4. 描述性统计：每组 n / M / SD / median / IQR / 缺失数；绘制原始数据分布图。
5. 选定检验（快速参考表或 test_selection_guide.md）；执行 assumption_checks.py 对应函数。
6. 前提违反处理：轻度 + n>30 → 仍用参数检验（稳健）；中度 → 非参数替代；方差不齐 → Welch's t / Welch's ANOVA；异方差回归 → HC3 稳健标准误。
7. 运行检验并计算效应量 + 95% CI（pg.compute_esci）；p 值报告精确值（p = .034 非 p < .05），仅 p < .001 可用不等式。
8. 若 ANOVA 显著 → Tukey HSD 后事后；多重比较族 → Holm 或 BH-FDR 校正并声明方法。
9. 贝叶斯分支（若选）：设定先验（按数据 SD 缩放）→ 采样 → 检查 R-hat < 1.01 / ESS > 1000 → 报告后验差值 + 95% CrI + 方向概率。
10. 撰写 APA 报告段落：描述统计 + 检验统计 + 效应量 CI + 假设检查 + 所有计划分析（含非显著结果）。
11. 生成 report_scaffold.py 输出或手动填充报告模板；保留可运行脚本与种子。

## 验证契约（Validations）
- 前提假设检查已执行并报告（Shapiro-Wilk / Levene / VIF / 残差图），违反时有明确处理声明。
- 效应量必须伴随每个检验报告；CI 使用 pg.compute_esci（非 compute_effsize_from_t，后者不返回 CI）。
- 区分验证性与探索性分析：计划外发现标记为 exploratory。
- 不追逐显著性（不更换检验/亚组/异常值方案直到 p < .05）。
- 非显著 ≠ 无效应：小 n 时补充灵敏度分析或贝叶斯/等价检验。
- EDA 输出中标记"未检测"仅指有界扫描范围内；IQR 栅栏/MAD 为灵敏度摘要而非删除规则。
- 缺失数据处理声明（listwise deletion 仅 MCAR 安全；否则用多重插补并报告）。
- 可复现性：random seed、库版本、完整命令记录。

## 资源引用（Resources）
- scripts/assumption_checks.py：comprehensive_assumption_check, check_normality, check_normality_per_group, check_homogeneity_of_variance, check_regression_diagnostics, check_linearity, detect_outliers。
- scripts/eda_analyzer.py / tabular_profile.py / missingness_leakage_audit.py / distribution_sensitivity.py / sequence_inspector.py / image_inspector.py / report_scaffold.py / capability_manifest.py。
- references/test_selection_guide.md、assumptions_and_diagnostics.md、effect_sizes_and_power.md、bayesian_statistics.md、reporting_standards.md。
- references/general_scientific_formats.md 等六个格式参考。
- 依赖：Python ≥3.10（EDA 可选 ≥3.12）, pingouin ≥0.6, scipy ≥1.11, statsmodels ≥0.14.6, pandas, matplotlib, seaborn；贝叶斯：pymc ≥5.0, arviz ≥1.0；EDA 可选：numpy 2.5.1, h5py 3.16.0, biopython 1.87, pillow 12.3.0, tifffile 2026.7.14, polars 1.43.0。

## 前后置任务（Task Graph）
无强制前后置；作为通用方法层任务被各域复用。典型上游：实验设计完成、数据采集结束、文件落入授权目录。典型下游：结果可视化/报告撰写/论文投稿。EDA 子流程为统计推断的前置（先了解数据再做检验）。

## 缺口与降级（Fallback / Gap）
- 数据格式不在自动化矩阵中（PDB/SAM/VCF/DICOM 等）：不运行 eda_analyzer.py；阅读对应 reference 文件，使用领域专用工具或转换派生副本为 CSV/NPY 后再处理。
- pingouin 单侧贝叶斯 BF 已移除：降级为 PyMC 直接计算方向后验概率，或使用 JASP/R BayesFactor。
- statsmodels + SciPy 版本冲突（_lazywhere 错误）：确保 statsmodels ≥0.14.6 + scipy ≥1.11。
- 正态性检验大样本过敏（n ≥ 100 Shapiro-Wilk 拒绝但分布近似正态）：以 Q-Q 图目视为主判据，辅以偏度/峰度，文档中声明判据选择。
- 缺失机制不明/非 MCAR：不做 listwise deletion；降级为多重插补（MICE）并在报告中声明方法、插补次数、收敛诊断。
- ArviZ 版本差异：1.x 移除 plot_posterior，改用 plot_dist；CI 默认 89% 需显式传 ci_prob=0.95。
