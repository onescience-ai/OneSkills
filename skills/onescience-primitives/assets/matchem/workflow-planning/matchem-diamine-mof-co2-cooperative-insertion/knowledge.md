# 二胺接枝 MOF 协同 CO₂ 捕集：术语与协同插入机制

## 适用范围

**触发条件**：
- 查询中出现二胺接枝/接枝 MOF、M₂(dobpdc)、mmen、协同 CO₂ 捕集、阶跃等温线、氨基甲酸铵链、Hill 系数等术语；
- 需要解释“CO₂ 如何插入金属–胺键并形成铵基甲酸盐链”的分子级机制；
- 需要为 M₂(dobpdc) 系列的机制/术语建立一致口径。

**适用场景**：
- 术语同义词消歧与缩写展开（见关键参数表 T1–T8）；
- 协同插入机制推理与阶跃等温线物理解释；
- 作为金属变体筛选、工况匹配、验证契约类卡片的机制底座。

**不适用场景**：
- 非二胺接枝类吸附剂（如纯物理吸附 MOF、分子筛、活性炭）的机制解释；
- 仅需要容量/选择性数值的筛选任务（应改用 `matchem-diamine-mof-co2-metal-variant-screening`）；
- 需要实验/计算验证分工的任务（应改用 `matchem-diamine-mof-co2-stability-validation-contract`）。

## 输入

- 材料标识：拓扑（dobpdc）、金属中心 M、二胺名称与接枝方式；
- 现象或数据：等温线/等压线形状、阶梯位置、温度或压力窗口、谱学特征（IR/NMR/XRD）；
- 可选：文献检索关键词（术语同义词列表见下）。

预处理：先做术语归一化（同义词 → 标准名），再进入机制推理；避免把“阶跃”与门控/孔开机制混淆。

## 输出

- 术语映射表（标准名 / 缩写 / 全名 / 同义表述）；
- 机制流程（CO₂ 插入 → 铵基甲酸盐链 → 协同传播 → 阶跃）；
- 关键参数（阈值压力、Hill 系数、阶梯位置顺序、Ni 例外）；
- 机制判据清单（用于区分协同插入 vs 门控/相变）。

## 流程节点

### Step 1：术语归一化
- **操作**：把查询中的同义词映射到标准名。
- **参数**：见“关键参数”表 T1–T8。
- **质量门禁**：每个缩写都有明确全名来源；无来源的缩写标记 `UNVERIFIED`。

### Step 2：确认“可重排的金属–胺配位键”前提
- **操作**：判断二胺是否通过配位键（而非共价键）接枝到开放金属位。
- **依据**：只有通过配位键系连于固相的胺才能发生所报道的重排机制 [1]。
- **质量门禁**：若为共价接枝，机制不适用，转出本卡片。

### Step 3：协同插入机制推理
- **操作**：在高于金属依赖阈值压力时，CO₂ 插入金属–胺键；一个胺的配位使相邻胺去稳定化，引发沿晶格方向传播；胺重排为有序铵基甲酸盐链 [1]。
- **参数**：阈值压力随温度显著移动；阶梯位置顺序 Mg < Mn < Fe < Zn < Co（同温） [1]。
- **质量门禁**：机制解释须同时解释“阶跃”与“金属依赖阈值”，否则标记证据不足。

### Step 4：阶跃型等温线物理解释
- **操作**：把阶跃归因于协同固–固相变（而非孔开/门开/吸附层相变）。
- **判据**：吸附前后单胞体积变化很小（mmen-Mn₂(dobpdc) 吸附 CO₂ 后单胞体积下降 <1%）；吸附相在 CO₂ 临界温度以上仍稳定；吸附/脱附起始点温度压力接近、滞后小 [1]。
- **质量门禁**：若数据仅显示单组分 Langmuir 型等温线，不得声称协同阶跃。

### Step 5：Hill 系数判读
- **操作**：用 Hill 系数（Hill 方程 [2]）量化协同性。
- **参数**：25 °C 阶跃的 Hill 系数：Mg 10.6、Mn 5.6、Fe 7.5、Co 11.5、Zn 6.0 [1]。
- **质量门禁**：Hill 系数须绑定到具体温度与拟合区间；缺温度标注时标 `PARTIAL`。

## 关键参数

| 编号 | 术语/参数 | 值/全名 | 来源 | 说明 |
|------|-----------|---------|------|------|
| T1 | diamine-appended MOF | 二胺接枝（接枝/附加）金属有机框架 | [1] | 与 diamine-grafted MOF 同义 |
| T2 | M₂(dobpdc) | 金属–dobpdc 框架 | [1][3] | M = Mg, Mn, Fe, Co, Ni, Zn |
| T3 | dobpdc⁴⁻ | 4,4′-dioxidobiphenyl-3,3′-dicarboxylate（4,4′-二氧基联苯-3,3′-二羧酸根） | [1][3] | 配体全名 |
| T4 | mmen | N,N′-dimethylethylenediamine（N,N′-二甲基乙二胺） | [1] | 常见二胺 |
| T5 | ammonium carbamate chain | 氨基甲酸铵链（铵基甲酸盐链） | [1] | 机制产物 |
| T6 | cooperative CO₂ adsorption / cooperative insertion | 协同 CO₂ 吸附 / 协同插入 | [1] | 机制名 |
| T7 | step-shaped isotherm / S-shaped isotherm | 阶跃型（S 型）等温线 | [1] | 现象 |
| T8 | Hill coefficient | Hill 系数 | [1][2] | 协同性度量；Hill 方程见 [2] |
| P1 | 阈值压力（threshold pressure） | 金属依赖；随温度升高向高压移动 | [1] | 阶跃发生压力 |
| P2 | Hill 系数（25 °C） | Mg 10.6 / Mn 5.6 / Fe 7.5 / Co 11.5 / Zn 6.0 | [1] | 协同性 |
| P3 | 阶梯位置顺序（同温） | Mg < Mn < Fe < Zn < Co | [1] | 与八面体金属配合物稳定性序列一致 |
| P4 | Ni 例外 | Ni 化合物呈 Langmuir 型、无阶跃 | [1] | 归因于 Ni–mmen 键过强 |
| P5 | 体积变化判据 | mmen-Mn₂(dobpdc) 吸附后单胞体积下降 <1% | [1] | 排除门控机制 |
| T9 | en | ethylenediamine（乙二胺） | [1]（参考文献层面） | **仅参考文献出现，本次证据未展开其在本体系的协同行为，标 PARTIAL** |
| T10 | dmpn | 未在本次全文证据中确认 | — | `UNVERIFIED`，不得展开 |

## 边界与分流

- **共价接枝**：机制不适用（需可重排配位键） [1]。
- **无开放金属位/无均匀位点**：难以复制该机制；论文指出能模拟该行为的 MOF 非常有限，胺功能化介孔二氧化硅难以精确满足要求 [1]。
- **Ni 变体**：无阶跃，不纳入协同阶跃推理 [1]。
- **双阶跃**：部分大位阻 1°,2°-二胺可出现双阶跃（如 pip2–Mg₂(dobpdc) 阶跃位于约 55 与 40 °C） [3]。
- **物理吸附叠加**：pip2–Mg₂(dobpdc) 第二个阶跃同时包含化学吸附与物理吸附 [3]。

## 质量检查

- 术语：缩写均绑定全名与来源；无来源标 `UNVERIFIED`。
- 机制：同时解释阶跃与金属依赖阈值。
- 判据：用体积变化/滞后/临界温度等判据排除门控与吸附层相变 [1]。
- 数值：Hill 系数与阶梯顺序绑定温度；缺条件标 `PARTIAL`。
- 一致性：不得把论文数值当作本任务材料上的结果。

## 回退策略

- 若无法获得谱学/衍射证据：仅交付“术语映射 + 机制假设 + 待验证清单”，机制结论标 `PARTIAL`。
- 若材料为共价接枝或非 dobpdc 体系：转出本卡片，改用通用 CO₂ 吸附机制知识。
- 若仅有单组分 Langmuir 等温线：不得声称协同阶跃，改走物理吸附分析。

## 资源召回建议

- 当任务涉及二胺接枝 MOF 的术语消歧、机制解释、阶跃等温线判读时召回本卡片；
- 配套召回：`matchem-diamine-mof-co2-metal-variant-screening`（变体与工况）、`matchem-diamine-mof-co2-stability-validation-contract`（验证与局限）。

## 证据来源

[1] "Cooperative insertion of CO2 in diamine-appended metal-organic frameworks", McDonald TM, Mason JA, Kong X, et al., Nature, 2015, DOI: 10.1038/nature14327（开放获取全文：escholarship.org qt2vs0h0wg；正文事实行号见登记文档）
[2] Hill 方程参考（Weiss JN, FASEB J, 1997），由 [1] 引用（Hill coefficient²³）
[3] "High-Capacity, Cooperative CO2 Capture in a Diamine-Appended Metal-Organic Framework through a Combined Chemisorptive and Physisorptive Mechanism", Zhang Z, Tieu H, et al., J. Am. Chem. Soc., 2024, DOI: 10.1021/jacs.3c13381
[4] "Hysteresis curves reveal the microscopic origin of cooperative CO2 adsorption in diamine-appended metal-organic frameworks", J. Chem. Phys., 2021, DOI: 10.1063/5.0054794（abstract-only，未提取全文）

> 证据分级：[1][3] 为本次全文级证据；[4] 为摘要级；[2] 为 [1] 转引的方法学参考。跨文献推断已标注。
