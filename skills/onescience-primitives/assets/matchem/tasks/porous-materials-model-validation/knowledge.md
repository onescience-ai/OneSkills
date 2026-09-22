# 多孔材料模型验证任务

## 适用范围

当多孔材料性质预测模型（基础模型/ML 势/吸附模型等）完成训练后，需要使用独立验证数据（实验或高保真计算结果）评估模型预测准确性时，本卡提供验证方法选择、验证数据获取、验证指标计算和结果报告的标准化流程。

## 输入

- 待验证的模型预测结果（吸附等温线、结合能、扩散系数等）
- 独立验证数据（实验测量值或高保真计算值，与模型训练数据分离）
- 验证目标（定量精度、定性排序、物理合理性）

## 输出

- 验证报告（含预测值 vs 真实值对比、统计指标、残差分析）
- 验证数据来源记录（数据库/文献/实验条件）
- 模型可靠性评估结论（PASS/CONDITIONAL/REJECT）

## 流程节点

1. 验证数据获取 → 预测-验证对照 → 统计指标计算 → 残差分析 → 结论判定
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 验证方法 | 适用性质 | 数据来源 | 精度要求 | 来源 |
|---------|---------|---------|---------|------|
| GCMC 模拟验证 | 吸附容量、吸附等温线、选择性 | RASPA / LAMMPS | 与实验偏差 <15-20% | [1][2][3] |
| DFT 验证 | 结合能、电子结构、带隙 | VASP / Gaussian | 与实验偏差 <0.1-0.2 eV | [3][4] |
| 实验验证 | 吸附容量、选择性、稳定性 | 文献数据 / 自测 | N/A（基准） | [2][5] |
| IAST 验证 | 多组分吸附选择性 | 基于单组分等温线 | 与 GCMC 偏差 <10% | [2] |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GCMC 典型模拟步数 | 10^5 - 10^6 MC 步 | [1][3] | 平衡步数 + 采样步数 |
| CO2 吸附容量验证 MAE | <0.5 mmol/g（MOF 体系） | [1] | Tao et al. 2022 基准 |
| H2S 吸附筛选偏差 | <10%（zeolite 体系） | [3] | Song et al. 2021 基准 |
| 吸附选择性排序一致性 | >90%（Top-K 候选重合率） | [2] | Bingel et al. 2024 基准 |

## 边界与分流

- 若无实验数据可用，使用高保真计算（GCMC/DFT）作为代理验证基准
- 若验证数据与模型训练数据来源相同，标记为非独立验证并降低置信度
- 若验证结果异常（MAE >50%），需排查数据质量问题而非直接判定模型失败

## 质量检查

- 验证数据必须与模型训练数据完全分离（无交叉污染）
- 每个验证样本需标注来源（实验/计算）和不确定度
- 验证报告必须包含残差分布图和物理合理性检查

## 回退策略

- 若独立验证数据不可获取，使用 k-fold 交叉验证作为最低验证标准（需标注为非独立）
- 若 GCMC 模拟资源受限，使用简化力场或文献校准值

## 资源召回建议

- 当模型训练完成后需要独立验证时召回本卡
- 配套资源：多孔材料数据获取卡、基础模型架构卡

## 证据来源

[1] Tao YR, et al. "Grand canonical Monte Carlo (GCMC) study on adsorption performance of metal organic frameworks (MOFs) for carbon capture." Sustainable Materials and Technologies, 2022, DOI: 10.1016/j.susmat.2021.e00383
[2] Bingel LW, et al. "IAST and GCMC predictions and experimental measurements of gas mixture adsorption on three metal-organic frameworks." Adsorption, 2024, DOI: 10.1007/s10450-024-00540-0
[3] Song L, et al. "Screening of zeolites for H2S adsorption in mixed gases: GCMC and DFT simulations." Microporous and Mesoporous Materials, 2021, DOI: 10.1016/j.micromeso.2021.111495
[4] Cheng J, et al. "Hydrogen adsorption performance of UiO-66 functionalized by -OH, -NH2 and -NO2 groups: GCMC simulation and experimental investigation." Materials Today Communications, 2025, DOI: 10.1016/j.mtcomm.2025.112123
[5] Hiraide S, et al. "GCMC kernel for analyzing the pore size distribution of porous carbons." Adsorption, 2023, DOI: 10.1007/s10450-023-00418-7

## 补充证据（批次：2026-09-21）

[6] Schnieders MJ, et al. "Fast process-level screening of metal-organic frameworks for adsorption-based gas separation." Digital Discovery, 2025, DOI: 10.1039/d6me00066e（全文级证据：GCMC模拟参数详解、cDFT vs GCMC过程级验证流程、CoRE MOF 2025数据库筛选）

[7] GCMC for NU-2100 authors. "Analyzing the gas storage capacities of NU-2100 MOF via GCMC simulations: a materials informatics approach." Adsorption, 2025, DOI: 10.1007/s10450-025-00641-4

[8] GCMC-MD shale gas authors. "GCMC-MD prediction of adsorption and diffusion behavior of shale gas in nanopores." Fuel, 2024, DOI: 10.1016/j.fuel.2024.133052

### 补充关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GCMC 初始化周期 | 20000 | [6] | RASPA 2.0 软件默认推荐的2倍 |
| GCMC 生产周期 | 100000 | [6] | 确保系统达到平衡 |
| Lennard-Jones 截断距离 | 14 Å | [6] | TraPPE-UA力场参数化距离 |
| 孔径计算工具 | Zeo++ | [6] | 100个Monte Carlo样本/单元 |
| 过程级验证 Pearson r | >0.98 (能量/容量), >0.92 (回收率), >0.82 (纯度) | [6] | cDFT vs GCMC 过程KPI相关系数 |
| Top-10% 识别率 | >92% (能量/容量), 60-70% (纯度/回收率) | [6] | cDFT正确识别最佳MOF的比例 |
| 力场 | UFF (吸附质) + TraPPE-UA (吸附分子) | [6] | 标准分子模拟力场组合 |