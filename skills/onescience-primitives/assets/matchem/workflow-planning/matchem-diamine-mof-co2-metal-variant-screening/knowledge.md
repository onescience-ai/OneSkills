# 二胺接枝 MOF（M₂(dobpdc)）金属变体筛选与工况匹配

## 适用范围

**触发条件**：
- 需要在 M₂(dobpdc)（M = Mg/Mn/Fe/Co/Ni/Zn）或不同二胺之间做候选排序；
- 需要按目标工况（DAC / 燃煤烟气 / 天然气烟气 / 沼气 / 室内空气）匹配阶梯压力（P_step）与分压；
- 需要容量、工作容量、选择性、再生能耗等候选变量对比。

**适用场景**：
- 金属变体与二胺的初步筛选与优先级排序；
- P_step 与工况 CO₂ 分压的匹配原则应用；
- 为具体材料确定容量-分压窗口与再生条件。

**不适用场景**：
- 仅需机制/术语解释（改用 `matchem-diamine-mof-co2-cooperative-insertion`）；
- 需要稳定性/杂质/验证分工（改用 `matchem-diamine-mof-co2-stability-validation-contract`）；
- 非二胺接枝 MOF 体系。

## 输入

- 候选集合：金属 M、二胺名称/结构、接枝密度；
- 目标工况：CO₂ 分压或浓度、温度、压力、湿度、竞争组分（N₂/CH₄/O₂）；
- 可选：已有等温线/等压线、工作容量、再生能耗、选择性数据。

预处理：先把工况换算为 CO₂ 分压（bar），再与 P_step 比较；容量须在**目标分压**下取值，而非仅总容量。

## 输出

- 候选金属变体-工况匹配表；
- 筛选排序与理由（含 P_step 匹配、容量、再生能耗、Ni 例外）；
- 关键参数表与不确定度/证据分级；
- 待确认项（缺数据标 `PARTIAL`）。

## 流程节点

### Step 1：建立候选与工况矩阵
- **操作**：列出 M 变体 × 二胺 × 工况（分压/温度/湿度）。
- **参数**：M = Mg, Mn, Fe, Co, Ni, Zn（同构系列） [1]。
- **质量门禁**：工况分压必须显式给出；缺失则标 `BLOCKED`。

### Step 2：P_step 与工况分压匹配
- **操作**：按“吸附质浓度决定最优 P_step”的原则匹配。
- **参数**：煤烟气约 0.15 bar；天然气烟气约 0.05 bar [1]；DAC/室内约 400–2000 ppm（约 0.4–2 mbar） [3]；沼气/填埋气 40–60% CO₂ [2]。
- **判据**：Mg、Mn 更适合低分压（烟气）；Fe、Co、Zn 更适合较高 CO₂ 浓度混合物 [1]。
- **质量门禁**：不得用总容量替代目标分压下的容量 [3]。

### Step 3：容量与工作容量评估
- **操作**：取目标分压/温度下的容量；按温度/压力摆幅计算工作容量。
- **参数**：容量与工作容量行见本表 P6–P8、P10、P13–P17；机制与稳定性/能耗参数按表内指针引用配套卡片。
- **质量门禁**：单位统一（mmol/g 或 wt%）；注明温度与分压。

### Step 4：再生能耗与选择性校核
- **操作**：用等量吸附热（Qst）/差示焓与 TSA 工作容量估算再生能耗；用 IAST 计算选择性。
- **参数**：Qst 范围、再生能耗与循环数据单一源见 `matchem-diamine-mof-co2-stability-validation-contract`（L4–L8）；选择性由 IAST 从单组分等温线计算（CO₂ 400–4000 ppm） [3]。
- **质量门禁**：Qst 过高会抬高脱附能耗；阈值与案例值见稳定性卡 L5/L6 [3]。

### Step 5：输出排序与适用域
- **操作**：综合 P_step 匹配、容量、能耗、稳定性给出排序；标注证据分级与适用域。
- **质量门禁**：推荐必须可回溯到原始数据；不确定度明确。

## 关键参数

| 编号 | 参数 | 值 | 来源 | 说明 |
|------|------|-----|------|------|
| P1 | 金属系列 | Mg, Mn, Fe, Co, Ni, Zn（同构） | [1] | M₂(dobpdc) |
| P2 | 等温线测量温度 | 25 / 40 / 50 / 75 °C | [1] | 阶梯随温度向高压移动 |
| P3 | 阶梯位置顺序（同温） | 单一源：见 `matchem-diamine-mof-co2-cooperative-insertion` P3 | [1] | 机制参数，本轮去重，本卡仅引用 |
| P4 | Hill 系数（25 °C） | 单一源：见 `matchem-diamine-mof-co2-cooperative-insertion` P2 | [1] | 机制参数，本轮去重，本卡仅引用 |
| P5 | Ni 例外 | 单一源：见 `matchem-diamine-mof-co2-cooperative-insertion` P4 | [1] | 机制参数，本轮去重，本卡仅引用 |
| P6 | 工作容量（Mg） | >13 wt%（100→150 °C 摆幅） | [1] | mmen-Mg₂(dobpdc) |
| P7 | 工作容量（Mn） | >10 wt%（70→120 °C 摆幅） | [1] | mmen-Mn₂(dobpdc) |
| P8 | 工况分压 | 煤烟气 ~0.15 bar；天然气烟气 ~0.05 bar | [1] | 匹配依据 |
| P9 | 模拟煤烟气 | 单一源：见 `matchem-diamine-mof-co2-stability-validation-contract` L10 | [1] | 动态穿透条件，本轮去重，本卡仅引用 |
| P10 | pip2–Mg₂(dobpdc) 容量 | 1.4 CO₂/二胺；25 °C 总容量 4.9 mmol/g；300 mbar 下 4.4 mmol/g；30 °C 1 bar 下 5.1 mmol/g | [2] | 混合化学/物理吸附 |
| P11 | pip2–Mg₂(dobpdc) 工作容量 | 单一源：见 `matchem-diamine-mof-co2-stability-validation-contract` L7 | [2] | 循环稳定性，本轮去重，本卡仅引用 |
| P12 | pip2–Mg₂(dobpdc) 再生能耗 | 单一源：见 `matchem-diamine-mof-co2-stability-validation-contract` L4 | [2] | 再生能耗，本轮去重，本卡仅引用 |
| P13 | mmen-Mg₂(dobpdc) DAC 容量 | 3.0 mmol/g（DAC 条件） | [3]（引文 24） | 用于 DAC |
| P14 | MOF-74(Mg) 容量 | 6.3 mmol/g（27.5 wt%），1 bar，25 °C | [3] | 对比材料 |
| P15 | NbOFFIVE-1 容量 | 2.2 mmol/g（400 ppm） | [3] | 对比材料 |
| P16 | NICS-24 容量 | 2.4 mmol/g（0.15 bar）；0.7 mmol/g（2 mbar） | [3] | 低浓度 CO₂ |
| P17 | CALF-20 容量 | 4.1 mmol/g（1 bar）；2.9 mmol/g（0.15 bar） | [3] | 对比材料 |
| P18 | 最优 Qst 范围 | 单一源：见 `matchem-diamine-mof-co2-stability-validation-contract` L5 | [3] | 能耗参数，本轮去重，本卡仅引用 |
| P19 | NICS-24 Qst | 单一源：见 `matchem-diamine-mof-co2-stability-validation-contract` L6 | [3] | 能耗参数，本轮去重，本卡仅引用 |
| P20 | 室内阈值浓度 | 约 2000 ppm（约 2 mbar） | [3] | IAC 工况 |

## 边界与分流

- **Ni 变体**：不适用于需要阶跃窗口的分离（Langmuir 型无阶跃，单一源：机制卡 P4） [1]。
- **低分压（DAC/IAC）**：需强结合位点；胺功能化可提升低分压容量，但过高 Qst 增加再生能耗 [3]。
- **高 CO₂ 浓度（沼气/填埋气 40–60%）**：可考虑 pip2 类大容量材料 [2]。
- **单组分容量 ≠ 混合物性能**：必须考虑分压、选择性、动力学 [3]。
- **数据缺失**：某变体缺目标分压数据时，标 `PARTIAL`，不得外推为确定值。

## 质量检查

- 容量必绑定温度与 CO₂ 分压；
- 工作容量须给出温度/压力摆幅；
- 选择性须由 IAST 或竞争吸附给出，不得由单组分等温线直接推断；
- 每个推荐绑定证据编号与分级；
- 论文数值仅作对账，不得作为本任务材料结果。

## 回退策略

- 无目标分压数据：退化为“P_step 匹配定性排序 + 待测清单”，标 `PARTIAL`。
- 无再生能耗数据：用 Qst + 工作容量定性比较，标 `PARTIAL`。
- 湿度影响显著：转 `matchem-diamine-mof-co2-stability-validation-contract`。

## 资源召回建议

- 当任务需要候选金属变体/二胺筛选、工况匹配或容量排序时召回本卡片；
- 配套：`matchem-diamine-mof-co2-cooperative-insertion`（机制）、`matchem-diamine-mof-co2-stability-validation-contract`（验证）。
- 参数单一源约定：机制参数（阶梯顺序/Hill 系数/Ni 例外）单一源在机制卡；稳定性与能耗参数（Qst/再生能耗/循环/模拟烟气）单一源在稳定性卡；本卡仅持有容量与工况参数，排序任务须同时召回配套卡片。

## 证据来源

[1] "Cooperative insertion of CO2 in diamine-appended metal-organic frameworks", McDonald TM, Mason JA, et al., Nature, 2015, DOI: 10.1038/nature14327
[2] "High-Capacity, Cooperative CO2 Capture in a Diamine-Appended Metal-Organic Framework through a Combined Chemisorptive and Physisorptive Mechanism", Zhang Z, Tieu H, et al., J. Am. Chem. Soc., 2024, DOI: 10.1021/jacs.3c13381
[3] "Amine-Functionalized Triazolate-Based Metal-Organic Frameworks for Enhanced Diluted CO2 Capture Performance", Angew. Chem. Int. Ed., 2025, DOI: 10.1002/anie.202424747
[4] "Data-driven design of metal-organic frameworks for wet flue gas CO2 capture", Nature, 2019, DOI: 10.1038/s41586-019-1798-7（abstract-only，未提取全文；仅作湿烟气背景）

> 证据分级：[1][2][3] 为全文级；[4] 为摘要级。P13 系 [3] 转引（引文 24），未直接核验原文献。
