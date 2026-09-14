# 二胺接枝 MOF 协同 CO₂ 捕集：已知局限与验证契约

## 适用范围

**触发条件**：
- 需要评估二胺接枝 MOF 在湿度、SO₂/NOx 杂质、循环、再生能耗方面的风险；
- 需要规划 DFT / GCMC / breakthrough / 循环实验的分工与质量门禁；
- 需要对性能结论做适用范围与不确定度审查。

**适用场景**：
- 材料性能验证方案设计；
- 已知局限清单与失效风险审查；
- 计算与实验的验证契约定义。

**不适用场景**：
- 仅需术语/机制（改用 `matchem-diamine-mof-co2-cooperative-insertion`）；
- 仅需变体筛选/工况匹配（改用 `matchem-diamine-mof-co2-metal-variant-screening`）。

## 输入

- 材料与工况：金属/二胺、CO₂ 分压、温度、湿度、杂质（SO₂/NOx/O₂）、循环模式；
- 已有数据：等温线/等压线、Qst、breakthrough、循环、XRD/NMR/IR；
- 计算资源：VASP/Quantum ESPRESSO、GCMC 工具、结构文件。

## 输出

- 局限清单（湿度、杂质、循环、能耗）与风险等级；
- 验证分工表（DFT/GCMC/breakthrough/循环各自的适用范围与门禁）；
- 质量门禁与失败处理；
- 证据分级与未覆盖项（标 `PARTIAL`/`UNVERIFIED`）。

## 流程节点

### Step 1：湿度影响评估
- **操作**：评估水竞争吸附与结构稳定性。
- **参数**：NICS-24 在 2000 ppm CO₂ 下，干态容量 0.64 mmol/g → 50% RH 降至 0.1 mmol/g；水吸附容量 2.25 mmol/g [3]；NICS-24 于 60 °C 水中浸泡 3 天结构完整，10 次 breakthrough 循环稳定 [3]。
- **机制**：干态羧基甲酸盐需 2 个胺/CO₂；湿态可经碳酸氢盐仅需 1 个胺/CO₂，某些体系湿度反而提升容量 [3]。
- **质量门禁**：未测湿度影响时明确标注；不得把干态容量当作湿态性能。

### Step 2：杂质中毒评估（SO₂/NOx）
- **操作**：评估酸性杂质对胺位点的不可逆中毒风险。
- **证据状态**：本次全文级证据（[1][2][3]）未直接给出 M₂(dobpdc) 的 SO₂/NOx 定量数据；仅有摘要级旁证（胺基固体吸附剂 SO₂ 影响 [5]；胺功能化 MOF 降解抑制 [6]）。
- **质量门禁**：SO₂/NOx 结论标 `PARTIAL`（证据有限），不得给出定量结论；需专门实验或文献补充。

### Step 3：循环稳定性评估
- **操作**：评估多次吸附/脱附循环的容量保持与结构/胺负载完整性。
- **参数**：pip2–Mg₂(dobpdc) 经 4 次 breakthrough 循环容量不变，500 次 TGA 循环容量稳定（~16.9 g/100 g），循环后 PXRD 高结晶、胺负载 ~100% [2]；NICS-24 经 20 次 TSA 循环、10 次 breakthrough 循环稳定 [3]。
- **质量门禁**：循环结论须给出循环次数、条件与容量保持率；缺失则标 `PARTIAL`。

### Step 4：再生能耗评估
- **操作**：用 Qst/差示焓 + 工作容量估算 TSA/湿度/压力 swing 能耗。
- **参数**：最优 Qst 约 30–60 kJ/mol [3]；pip2–Mg₂(dobpdc) 再生能耗约 1.58 MJ/kg CO₂（MEA 约 4.5 MJ/kg CO₂） [2]；水胺溶液再生能耗高、氧化/热稳定性差 [2]。
- **质量门禁**：Qst 过高（NICS-24 约 68 kJ/mol）须标注脱附能耗风险 [3]。

### Step 5：验证分工与门禁
- **操作**：按目的分配 DFT / GCMC / breakthrough / 循环实验（见下表与关键参数）。
- **质量门禁**：每项验证须记录参数、版本、对照与失败样本。

## 验证分工契约

| 方法 | 适用范围 | 关键参数/设置 | 输出 | 证据 |
|------|----------|----------------|------|------|
| 周期性 DFT | 插入能、结合能、金属–胺键长、NMR 化学位移 | VASP 5.3.3，PBE/M06L，PAW 550 eV，力 <0.02 eV/Å，Γ 点，Mn/Fe/Co/Ni 加 Hubbard U [1]；或 QE RPBE+D3，GBRV 赝势，60/600 Ry，1×1×3 k，力 <1e-4 Ry/Bohr [2] | 能量、键长、化学位移 | [1][2] |
| AIMD | 有限温结构/构象 | NPT，Parrinello–Rahman + Langevin，0.5 fs，PAW 400 eV，vdW-DF2，1×1×3 k，22×21×7 Å 超胞 [1] | 平衡结构 | [1] |
| XAS 模拟 | 电子结构/吸附物种 | PBE，超软赝势，25/200 Ry，QE PWSCF，XCH，2×2×2 k [1] | NEXAFS 谱 | [1] |
| GCMC / 晶格模型 | 等温线与阈值压力 | 晶格模型（chain/pair），相互作用能取自 DFT，压力 shift 由最高/最低温阶跃拟合 [1] | 阶跃等温线、P_step | [1] |
| IAST | 混合物选择性（CO₂/N₂、CO₂/O₂） | 由单组分等温线计算；CO₂ 400–4000 ppm [3] | 选择性 | [3] |
| 气体吸附等温线 | 容量/Qst | Micromeritics 3Flex；平衡判据：11 个连续区间压力变化 <0.01%（15 s/区间）；Clausius–Clapeyron 求 Δhads [2] | 等温线、Δhads/Δsads | [2] |
| Breakthrough | 动态多组分分离性能 | 自制装置；60% CO₂/N₂、5 sccm、GC 检测 [2]；或 2000 ppm CO₂ + 20% O₂、干/湿对比 [3] | 穿透容量、工作容量 | [2][3] |
| 循环实验 | 耐久性 | TGA：吸附 15 min/脱附 1 min，500 次 [2]；TSA 20 次 [3] | 容量保持率 | [2][3] |
| 谱学/衍射 | 吸附物种与结构 | DRIFTS（1644/1325 cm⁻¹ 羧基甲酸盐）、ssNMR（¹³C/¹⁵N）、PXRD、DSC、TGA [2][3] | 物种鉴定、结构 | [2][3] |

## 关键参数

| 编号 | 参数 | 值 | 来源 | 说明 |
|------|------|-----|------|------|
| L1 | 湿态容量下降（NICS-24） | 2000 ppm 干 0.64 → 50% RH 0.1 mmol/g | [3] | 水竞争 |
| L2 | 湿态水吸附（NICS-24） | 2.25 mmol/g | [3] | 竞争吸附 |
| L3 | 水稳定性（NICS-24） | 60 °C 水浸泡 3 天结构完整 | [3] | 结构稳定 |
| L4 | 再生能耗（pip2） | ~1.58 MJ/kg CO₂（MEA ~4.5） | [2] | TSA 25→80 °C |
| L5 | 最优 Qst | 30–60 kJ/mol | [3] | 平衡再生 |
| L6 | NICS-24 Qst | 68 kJ/mol | [3] | 接近 TSA 上限 |
| L7 | 循环（pip2） | 500 次 TGA 稳定，~16.9 g/100 g | [2] | 胺负载 ~100% |
| L8 | 循环（NICS-24） | 20 次 TSA、10 次 breakthrough 稳定 | [3] | — |
| L9 | 热稳定性（NICS-24） | 配体分解 300–400 °C | [3] | TGA |
| L10 | 模拟煤烟气 | 15% CO₂, 4% O₂, 余 N₂, 1.5% 水 | [1] | 动态穿透 |
| L11 | SO₂/NOx | 本次全文级证据未覆盖 | — | `PARTIAL`/`UNVERIFIED` |

## 边界与分流

- **湿态**：未测湿度时不得外推干态容量；胺功能化框架通常亲水，需评估水竞争 [3]。
- **酸性杂质**：SO₂/NOx 定量结论证据不足，需专门实验 [5][6]（摘要级）。
- **强结合材料**：Qst 过高会抬高脱附能耗，需权衡 [3]。
- **单组分 vs 混合物**：breakthrough/IAST 才能反映真实分离；单组分容量不足为凭 [2][3]。
- **计算与实验关系**：计算（DFT/GCMC）给出能学与等温线预测，实验（breakthrough/循环）给出动态与耐久证据；两者不可互替。

## 质量检查

- 每条局限绑定证据与分级；
- 未覆盖项（SO₂/NOx）明确标 `PARTIAL`/`UNVERIFIED`，不得编造；
- 计算参数（泛函、赝势、截断、k 点、力收敛、U 值）完整记录；
- 实验条件（温度、分压、湿度、循环次数、平衡判据）完整记录；
- 结论区分“已证实/探索性/无法回答”。

## 回退策略

- 无 SO₂/NOx 数据：标 `PARTIAL`，列为待补实验/文献项。
- 无 breakthrough 装置：用 IAST + 单组分等温线做初步选择性，标 `PARTIAL`。
- 无循环数据：以短期稳定性替代并明确标注。
- 无 DFT 资源：仅交付验证契约与参数模板，不产出本材料能学结论。

## 资源召回建议

- 当任务涉及稳定性/杂质/循环/再生能耗或验证方案设计时召回本卡片；
- 配套：`matchem-diamine-mof-co2-cooperative-insertion`（机制）、`matchem-diamine-mof-co2-metal-variant-screening`（筛选）。

## 证据来源

[1] "Cooperative insertion of CO2 in diamine-appended metal-organic frameworks", McDonald TM, Mason JA, et al., Nature, 2015, DOI: 10.1038/nature14327
[2] "High-Capacity, Cooperative CO2 Capture in a Diamine-Appended Metal-Organic Framework through a Combined Chemisorptive and Physisorptive Mechanism", Zhang Z, Tieu H, et al., J. Am. Chem. Soc., 2024, DOI: 10.1021/jacs.3c13381
[3] "Amine-Functionalized Triazolate-Based Metal-Organic Frameworks for Enhanced Diluted CO2 Capture Performance", Angew. Chem. Int. Ed., 2025, DOI: 10.1002/anie.202424747
[4] "Water Enables Efficient CO2 Capture from Natural Gas Flue Emissions in an Oxidation-Resistant Diamine-Appended Metal-Organic Framework", J. Am. Chem. Soc., 2019, DOI: 10.1021/jacs.9b05567（abstract-only）
[5] "Effect of SO2 on the CO2 Capture Performance of Self-Supported Branched Poly(ethyleneimine) Scaffold", Energy & Fuels, 2023, DOI: 10.1021/acs.energyfuels.2c03846（abstract-only）
[6] "Inhibitory Effects on the Degradation Behavior of Amine-Functionalized MOF-Based Adsorbents for CO2", Ind. Eng. Chem. Res., 2026, DOI: 10.1021/acs.iecr.6c01030（abstract-only）

> 证据分级：[1][2][3] 为全文级；[4][5][6] 为摘要级。SO₂/NOx 定量结论证据有限，已明确标注。
