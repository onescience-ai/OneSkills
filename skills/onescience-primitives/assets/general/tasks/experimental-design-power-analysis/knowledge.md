# 实验设计与统计功效分析 (experimental-design-power-analysis)

## 任务目标
在数据采集前完成两项决策：（1）选择实验设计类型并生成随机化/DOE 布局；（2）确定达到目标功效所需的样本量或最小可检测效应（MDE）。输出可复现、可审计的设计文档与功效陈述，使后续分析具有因果解释力且不被审稿人质疑。

## 适用范围 / 不适用场景
适用：比较性实验规划、多因素筛选/优化（因子设计、响应面）、随机化分组（简单/区组/分层/整群）、交叉/重复测量/裂区设计、序贯/自适应试验、样本量论证（基金申请/IRB/预注册）、功效曲线制作。
不适用：数据已采集后的统计推断（应转 statistical-analysis）；单纯的数据探索与可视化（应转 EDA）；观测性研究中的因果推断建模（需额外 DAG/IV 框架）。

## 实体槽（Entity Slots）
- design_type：实验设计类型（completely-randomized / block / crossover / factorial / fractional-factorial / response-surface / cluster / latin-square / split-plot / sequential）
- factors：处理因素及其水平数/范围（连续型用 (low, high) 元组）
- nuisance_factors：需区组化或分层控制的干扰变量（batch / day / site / plate / operator）
- effect_size：功效计算所用的效应量（Cohen's d / f / r / η² / h / w / OR）
- alpha：显著性水平，默认 0.05 双侧
- power_target：目标功效，常用 0.80（探索）或 0.90（验证性/临床）
- unit_of_randomization：随机化单元（个体/窝/诊所/板位）——决定真正独立重复的层级
- seed：随机种子，保证布局可复现

## 输入输出契约
输入：研究问题描述、处理条件列表与水平范围、已知干扰因素、预期效应量（或 SESOI 依据）、α/功效目标、分配比例（如 2:1）、脱落率估计。
输出：
1. 设计类型声明与理由（决策树路径）；
2. 随机化分配表或 DOE 矩阵（CSV，含 seed 可再生）；
3. 功效分析结果——所需 n、MDE、或功效曲线图（PNG）；
4. 功效陈述文本（含效应量来源、α、功效、脱落调整、Monte Carlo CI 等完整输入）；
5. 灵敏度分析表（效应量区间 vs. 所需 n）。

## 方法路线（可替换）
A. 闭式功效计算：statsmodels / pingouin 提供的解析公式，适用 t 检验、ANOVA、比例、相关、卡方、线性回归。快速、精确。
B. 模拟功效（Monte Carlo）：自行编写数据生成过程 → 用计划分析模型拟合 → 重复 ≥1000 次（稳定估计需 5000-10000 次）。适用 logistic/Poisson 回归、混合模型、整群随机、生存分析、交互作用等无公式设计。
C. DOE 矩阵生成：pyDOE3 封装脚本（two_level_factorial / fractional_factorial / plackett_burman / central_composite / box_behnken / latin_hypercube），输入因素范围输出实际单位布局。
D. 随机化分配：simple / block / stratified_block / cluster 四种函数，seeded，可导出 allocation_schedule.csv。

## 操作序列（Operations）
1. 明确研究问题、随机化单元、响应变量及其层级。
2. 列举干扰因素，决定区组化/分层/随机化跨越策略。
3. 通过决策树选定设计类型；若为多因素筛选选 fractional factorial（分辨率 ≥ IV 以分离主效应与二阶交互），若需检测曲率选 CCD/Box-Behnken。
4. 确定效应量：优先 SESOI → 缩减的先验/试点估计 → Cohen 惯例（末选且须明示）。
5. 设定 α（默认 0.05 双侧）与目标功效（0.80/0.90）；声明分配比例。
6. 调用 power.py 闭式计算或 simulate_power.py 模拟计算，得到 n；对无公式设计直接走模拟。
7. 运行灵敏度分析：在合理效应量区间重算 n，输出功效曲线。
8. 调整脱落（n_enroll = ceil(n_analyzed / (1 − dropout_rate))）、整群设计效应（DEFF = 1 + (m−1)·ICC）、多重比较（α/m 或模拟 FWER/FDR 过程）。
9. 生成随机化/DOE 布局，随机化运行顺序，导出 CSV 并记录 seed。
10. 撰写功效陈述与设计文档（含所有输入、软件版本、seed），必要时预注册。

## 验证契约（Validations）
- 分配表各组计数平衡检查（arm_balance）；区组随机化须保证全程均衡。
- DOE 矩阵运行顺序已随机化（不与时间/漂移混淆）。
- 功效分析输出 Monte Carlo CI（模拟法），CI 宽度 < 0.05 为稳定。
- 效应量来源有据可查（SESOI / 文献 / 试点，非臆造）。
- 禁止事后功效（post-hoc observed power）——若被要求，改报灵敏度分析或效应量 CI。
- 设计文档包含 seed + 脚本版本 + 输入参数，可复现。

## 资源引用（Resources）
- scripts/randomization.py：simple_randomization, block_randomization, stratified_block_randomization, cluster_randomization, assign_factorial_runs, arm_balance。
- scripts/doe_designs.py：full_factorial, two_level_factorial, fractional_factorial, plackett_burman, central_composite, box_behnken, latin_hypercube。
- scripts/power.py：sample_size, power, mde, power_curve（统一闭式接口，覆盖 t_ind/t_paired/anova/two_proportions/one_proportion/correlation/chi2/linear_regression）。
- scripts/simulate_power.py：simulate_power(), find_sample_size()，含 logistic/cluster/LMM 示例。
- references/randomization_and_blocking.md、factorial_and_doe.md、design_types.md、sequential_and_adaptive.md。
- references/closed_form_recipes.md、simulation_based_power.md、effect_sizes.md。
- 依赖：Python ≥3.10, numpy ≥1.26, pandas ≥2.0, pyDOE3, statsmodels ≥0.14.6, scipy ≥1.11, pingouin ≥0.6, matplotlib。可选 lifelines（生存模拟）。

## 前后置任务（Task Graph）
无强制前后置；作为通用方法层任务被各域复用。典型上游：研究问题定义 / 文献调研确定效应量依据。典型下游：数据采集完成后转入统计分析任务（假设检验、模型拟合、报告）。

## 缺口与降级（Fallback / Gap）
- 效应量无可靠来源：使用 SESOI 作为最低可接受效应，明示为保守假设，并输出宽范围灵敏度分析。
- 无闭式公式（混合模型/生存/交互）：降级为 Monte Carlo 模拟功效；模拟次数 ≥5000 以稳定 80% 附近估计。
- pyDOE3 不可用：手动用 numpy 生成全因子/随机化排列，但需自行验证正交性与分辨率。
- 整群设计 ICC 未知：从文献取保守上界（如 0.05），或进行 ICC 灵敏度分析展示 DEFF 对 n 的影响。
- 低分辨率部分析因设计别名严重：升级分辨率（Resolution V）或改为全因子；若运行成本不允许，声明仅主效应可解释、交互作用与别名结构不可分。
- 脱落率不确定：按 20% 默认调整并标注为假设；建议在最终报告中更新。
