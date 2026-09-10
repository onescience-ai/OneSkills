# 吗啡类生物碱在酵母中的重构与发酵生产工作流

## 适用范围

**触发条件**：
- 需要在酿酒酵母 (*Saccharomyces cerevisiae*) 中重建吗啡烷生物碱（可待因/吗啡/蒂巴因）或其分支中间体 (S)-reticuline
- 需要评估微生物合成路线 vs 植物提取路线的可行性
- 需要理解为何酵母比大肠杆菌更适合承载植物 P450 酶
- 需要规划底盘代谢工程改造（酪氨酸/莽草酸/Ehrlich 通路）来提升滴度

**适用场景**：
- 酵母中 (S)-reticuline / (S)-norcoclaurine 的 gram 级滴度生产
- 从 (S)-reticuline 经蒂巴因到可待因/吗啡的酶级联重构
- norlaudanosoline（去甲鸟药碱）替代 (S)-norcoclaurine 路线的选择性优化
- 大肠杆菌路线对比与 stepwise（多菌株串联）工艺设计

**不适用场景**：
- 纯基因通路解析（请召回 bio-opium-poppy-morphinan-biosynthesis-pathway 卡片）
- 非微生物的体内/体外纯酶 biotransformation（如 thebaine→codeine 单酶转化，见 [5] 可作参考）
- 药理活性评价（本卡片聚焦工程与滴度）

## 输入

| 输入项 | 格式/来源 | 说明 |
|--------|----------|------|
| 前体/底物 | (R,S)-norlaudanosoline、(S)-reticuline、salutaridine、thebaine、codeine | 喂养实验底物 [3] |
| 罂粟通路基因 | STORR、SALSYN、SALR、SALAT、T6ODM、CODM、COR、NISO | 需异源表达 [1][3][5] |
| 宿主菌株 | S. cerevisiae（如 BY4741 衍生） | 底盘 [1][2] |
| 还原伙伴 | CPR（如 AtATR2） | 支持 P450 [1] |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 重构流程 | 步骤链 | 底盘改造 → 前体通路 → 异源酶级联 → 发酵 |
| 滴度参数表 | 表格 | (S)-reticuline 4.6 g/L 等关键值 |
| 宿主改造点清单 | 列表 | 酪氨酸/莽草酸/Ehrlich/氧化还原酶删除 |
| 瓶颈与副产物分析 | 表 | codeine→morphine 0.5%、neopine 副产物 |
| 与大肠杆菌对比 | 表 | 300 倍蒂巴因提升等 |

## 流程节点

### Step 1：底盘与公共前体通路改造

- **操作**：改造酵母以生产植物非天然代谢物多巴胺与 4-HPAA
- **数值**：通过 >20 次菌株工程改造 shikimate、Ehrlich、L-酪氨酸通路，使 (S)-去甲鸟药碱达 77 mg/L（较早期 11,000 倍提升），补料分批下 1.6 g/L [1]
- **关键删除**：删除 aldehyde dehydrogenase ALD4、多个氧化还原酶（gre2Δ、hfd1Δ 等）以减少 tyrosol/4-HPAC 竞争与 off-target THIQ [1]
- **关键拷贝**：整合 8 拷贝 NdNCSΔN20；改用 CjNCSΔN35 使产量 +50% [1]
- **工具**：标准酵母分子克隆、基因编辑
- **质量门禁**：确认产物为 (S)-对映体（手性分析）[1]

### Step 2：异源 P450 表达（酵母 vs 大肠杆菌关键差异）

- **操作**：表达植物 P450（NMCH/CYP80B1、SALSYN、STORR 模块），并配 CPR 还原伙伴
- **要点**：酵母具膜结合细胞器，能正确折叠并锚定植物 P450，故成为重构首选宿主；大肠杆菌需 N-端截短、表达受限，且缺乏膜结构 [1][4]
- **数值**：CYP76AD5 酪氨酸羟化酶双倍表达使 (S)-去甲乌药碱翻倍至 245 mg/L [1]
- **质量门禁**：确认 P450 有功能产物生成而非仅蛋白表达

### Step 3：到 (S)-reticuline 的支路与高滴度平台

- **操作**：把公共前体通路延伸到分支枢纽 (S)-reticuline
- **数值**：整合 Ps6OMT/PsCNMT/Ps4′OMT 等，(S)-reticuline 微孔板 340 mg/L；多整合 1 拷贝 4′OMT2 使滴度 +45% 至 492 mg/L [1]
- **里程碑**：菌株 LP507 在补料分批矿物培养基中达 **(S)-reticuline 4.6 g/L**、norcoclaurine 0.6 g/L——相对早期工作 57,000 倍提升 [1][2]
- **质量门禁**：报告滴度需注明培养方式（摇瓶/微孔板/补料分批）

### Step 4：到蒂巴因/可待因/吗啡的酶级联重构

- **操作**：从 (R)-reticuline/salutaridine/codeine 底物重构下游吗啡烷
- **瓶颈**：SALSYN/SAR/SAT + 自发重排（pH 8–9）可产蒂巴因；但 CODM 末端 step 极弱——codeine→morphine 转化仅 ~0.5%，COR 还会把 codeine 反向氧化成 codeinone [3]
- **要点**：酵母无法补足 (S)→(R)-reticuline 异构化（需 STORR），故从 (R,S)-去甲鸟药碱出发只积累 (S)-网状番荔枝碱 [3]
- **质量门禁**：区分"去甲鸟药碱途径"(S) 端与需 (R) 型的吗啡烷支路

### Step 5：norlaudanosoline 新路线与选择性提升（2026）

- **操作**：绕开 (S)-去甲乌药碱需 P450 羟化的步骤，改走 (S)-norlaudanosoline 路线
- **机制**：以人多巴胺单胺氧化酶 A (MAO) 把多巴胺氧化成 3,4-dHPAA，再与多巴胺缩合为 norlaudanosoline，省去 CYP80B1 羟化 [2]
- **数值**：TEF2 启动子驱动 MAOΔTM 时 (S)-reticuline 达 3–4 g/L；(S)-reticuline 占全部 THIQ 的比例从 42–49% 提升至 ~80%（选择性）[2]
- **工具**：MAO 异构体（HsMAO-A、MlMAO）、启动子强度平衡
- **质量门禁**：监测 off-target 4′-unsubstituted THIQ（4′-dHN）与 hydroxytyrosol 累积

### Step 6：半合成/路线对比与产业评估

- **操作**：比较 de novo 全合成与"产中间体+酶转化"半合成路线
- **对照**：大肠杆菌四菌株串联 stepwise 从甘油产 thebaine 6.21 mg/L、hydrocodone 1.15 mg/L，较同期酵母蒂巴因系统约 300 倍 [4]
- **体外转化参考**：酵母区室化表达 T6ODM+COR 使 thebaine→codeine 产率 ~1.8%；大肠杆菌 whole-cell 加 NISO 后 codeine:neopine 20:80 → 74:26，产率 64%、体积产率 ~0.1 g/(L·h)（~160 倍提升）[5]
- **产业基准**：微生物阿片商业化目标 ~5 g/L [1][2]
- **质量门禁**：结论区分 full 全合成滴度 vs 单步 biotransformation 产率

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 宿主 | S. cerevisiae (BY4741 衍生) | [1][2] | 高滴度平台 |
| (S)-reticuline 滴度 | 4.6 g/L（补料分批） | [1] | 57,000 倍提升 |
| (S)-norcoclaurine 滴度 | 77 mg/L→1.6 g/L | [1] | 微孔板→补料分批 |
| CjNCSΔN35 增益 | +50% | [1] | 与 NdNCSΔN20 比较 |
| 额外 4′OMT2 拷贝 | +45%（492 mg/L） | [1] | 减少中间体积累 |
| codeine→morphine | ~0.5% | [3] | CODM 末端瓶颈 |
| 2026 新路线滴度 | 3–4 g/L | [2] | norlaudanosoline 路线 |
| THIQ 选择性 | 42%→80% | [2] | LP507 vs 新菌株 |
| 大肠杆菌蒂巴因 | 6.21 mg/L | [4] | 较酵母 ~300 倍 |
| thebaine→codeine(酵母) | ~1.8% | [5] | 区室化 |
| thebaine→codeine(大肠全细胞) | 64%, 74:26 | [5] | 加 NISO |
| 产业目标 | 5 g/L | [1][2] | 阿片商业化基准 |

## 通路/工艺示意

```
酵母底盘（BY4741）
  酪氨酸/莽草酸/Ehrlich 通路改造
  （删除 ALD4/gre2/HFD1；↑CYP76AD5、8×NCS）
       ▼
多巴胺 + 4-HPAA ──NCS──▶ (S)-norcoclaurine     (A 路线，需 P450 羟化)  [1]
多巴胺 ──MAO──▶ 3,4-dHPAA ─▶ (S)-norlaudanosoline (B 路线，无 P450)     [2]
       ▼ 6OMT/CNMT/4′OMT（多拷贝 4′OMT2）
   (S)-reticuline  ── 4.6 g/L（LP507）/ 3-4 g/L 高纯（2026）[1][2]
       │ STORR 需引入（酵母内建 (S)→(R) 困难）[3]
   salutaridine ─▶ 蒂巴因 thebaine（酵母内浓度低）
       ─T6ODM/NISO/COR/CODM─▶ 可待因 → 吗啡（末端 CODM 0.5% 瓶颈）[3]
```

## 边界与分流

- **立体化学硬约束**：罂粟 MTs 从 (R,S)-去甲鸟药碱只产 (S)-网状番荔枝碱；吗啡烷下游需 (R) 型，需 STORR——酵母重构最大障碍之一 [3]
- **宿主取舍**：要膜 P450 → 酵母；要无 P450 纯化度高滴度中间体/快速出产物 → 大肠杆菌（蒂巴因高 300 倍）[1][4]
- **P450 表达差异**：大肠杆菌需 N 端截短且表达难；酵母能承载完整植物 P450 [1][4]
- **副产物**：COR 底物混杂产 neopine，植物靠 NISO 抑制；酵母内需空间/时间分离策略（参考区室化 1.8%）[3][5]
- **路线分流**：要 (S)-reticuline → 走 (S)-norcoclaurine 或 norlaudanosoline 均可；要吗啡烷末端 → 需 (R) 型与 STORR，工艺更复杂

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|---------|
| 产物对映体 | 100% (S) 型（上游） | 手性柱 LC 复核 |
| THIQ 纯度 | (S)-reticuline 占 >70% | 检查 off-target 醛来源 |
| 滴度可复现 | 与文献同数量级 | 核查培养方式与菌株 |
| 末端转化 | 报告是否到吗啡/仅中间体 | 明确区分路径深度 |

## 回退策略

- **P450 表达失败**：改用不同物种同源酶、N 端改造、宿主密码子优化 [1][4]
- **(S)→(R) 异构化瓶颈**：绕过——从 (R)-网状番荔枝碱/salutaridine 直接喂养，或半合成 route（微生物产 thebaine + 酶转化）[3][5]
- **末端 CODM 弱**：接受到 codeine/蒂巴因为止，用体外 biotransformation 补末端 [3][5]
- **选择性差**：改用 norlaudanosoline 路线（省 P450 羟化 + 减少 off-target THIQ）[2]

## 资源召回建议

**何时应召回本卡片**：
- 用户询问吗啡/可待因/蒂巴因能否或如何在酵母中生产
- 用户做酵母代谢工程改造 BIA 滴度
- 用户对比酵母与大肠杆菌产阿片路线
- 用户需要 (S)-reticuline 高滴度平台作下游底物

**配套资源**：
- onescience-primitives bio 域卡片 bio-opium-poppy-morphinan-biosynthesis-pathway（上游基因通路）
- onescience-primitives bio 域发酵/fed-batch/菌株工程分析卡片
- onescience-live-literature 技能：实时检索最新酵母 BIA/阿片滴度突破

## 证据来源

[1] Pyne ME, Kevvai K, Grewal PS, et al. "A yeast platform for high-level synthesis of tetrahydroisoquinoline alkaloids." Nature Communications, 2020, 11:3337. DOI: 10.1038/s41467-020-17172-x. (full-text)

[2] Narcross L, Pyne ME, Kevvai K, et al. "Benzylisoquinoline Alkaloid Production in Yeast via Norlaudanosoline Improves Titer, Selectivity, and Yield." ACS Synthetic Biology, 2026. DOI: 10.1021/acssynbio.5c00897. (full-text)

[3] Fossati E, Narcross L, Ekins A, et al. "Synthesis of Morphinan Alkaloids in Saccharomyces cerevisiae." PLoS ONE, 2015, 10(5):e0124459. DOI: 10.1371/journal.pone.0124459. (full-text)

[4] Nakagawa A, Matsumura E, Koyanagi T, et al. "Total biosynthesis of opiates by stepwise fermentation using engineered Escherichia coli." Nature Communications, 2016, 7:10390. DOI: 10.1038/ncomms10390. (full-text)

[5] Li X, Krysiak-Baltyn K, Richards L, et al. "High-Efficiency Biocatalytic Conversion of Thebaine to Codeine." ACS Omega, 2020, 5:9330-9340. DOI: 10.1021/acsomega.0c00282. (full-text)
