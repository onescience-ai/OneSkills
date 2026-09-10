# 罂粟吗啡类生物碱合成通路基因解析工作流

## 适用范围

**触发条件**：
- 需要理解罂粟（*Papaver somniferum*）中吗啡/可待因/蒂巴因等吗啡烷类生物碱的生物合成机制
- 已有罂粟或其他苄基异喹啉生物碱（BIA）物种基因组/转录组数据，需做功能注释与通路定位
- 需要解析 BIA 基因在基因组中的成簇组织与拷贝数变异
- 需要把某一步"基因-酶-产物"对应关系用于代谢工程或微生物重构

**适用场景**：
- 吗啡烷通路完整骨架解析（L-酪氨酸 → (S)-reticuline → 蒂巴因 → 可待因 → 吗啡）
- STORR 双功能融合蛋白的演化与催化角色分析
- BIA 通路基因簇、串联复制、拷贝数变异的基因组学分析
- 微生物（酵母/大肠杆菌）中重构吗啡烷通路前的前期基因梳理

**不适用场景**：
- 纯药理活性研究（本卡片聚焦合成通路基因-酶-产物层面）
- 非 BIA 谱系（如藏红花类胡萝卜素通路）——请召回 bio-saffron-crocin-biosynthesis-gene-reasoning 卡片
- 无任何序列或文献证据支持的纯猜测推理

## 输入

| 输入项 | 格式/来源 | 说明 |
|--------|----------|------|
| 基因组序列 | FASTA + GFF3 | 罂粟 CHM/HN1 等染色体级组装 [5] |
| 转录组 | RNA-seq FASTQ | 乳管/蒴果组织，BIA 基因高表达 [4][5] |
| 通路基因参考 | 已功能表征的 BIA 基因集 | 如 Guo 组装注释的 STORR、T6ODM、CODM 等 [4] |
| 同源物种 | 其他 Papaver/Ranunculales 基因组 | 用于演化定位 [3][5] |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 通路示意链 | 多级箭头链 | 底物→酶→产物完整路径（见"通路示意"） |
| 关键酶-基因表 | 表格 | 每步酶名、所属基因/家族、催化反应、证据 |
| 基因簇与 CNV 分析 | 表/图 | 成簇比例、串联复制拷贝数 |
| 演化时间线 | 列表 | STORR 融合、T6ODM/CODM 分化等事件 |
| 重构所需基因清单 | 表格 | 微生物重构需引入的酶与宿主改造点 |

## 流程节点

### Step 1：通路骨架确认（公共核心）

- **操作**：确认从 L-酪氨酸到 (S)-reticuline 的公共 BIA 核心通路
- **要点**：多巴胺 + 4-羟基苯乙醛（4-HPAA）经 norcoclaurine synthase (NCS) 缩合成 (S)-去甲乌药碱 [1]；(S)-reticuline 是所有下游子通路（血根碱、小檗碱、noscapine、吗啡烷）的公共分支枢纽 [1][3]
- **基因**：NCS → 6OMT → CNMT → CYP80B1(NMCH, P450) → 4′OMT
- **质量门禁**：能列出 4OMT/6OMT/CNMT 各自的甲基化位点与底物立体选择性

### Step 2：吗啡烷特异通路（(R) 立体中心 + 蒂巴因）

- **操作**：梳理从 (S)-reticuline 到蒂巴因的特异步骤
- **关键开关**：STORR——双功能 P450-氧化还原酶融合蛋白，催化 (S)→(R)-reticuline 异构化 [3]
- **通路**：(R)-reticuline →(SALSYN/CYP719B1)→ salutaridine →(SALR)→ salutaridinol →(SALAT)→ salutaridinol-7-O-乙酸酯 →(自发重排,碱性)→ **thebaine（蒂巴因，首个吗啡烷产物）** [3]
- **质量门禁**：确认蒂巴因前各步酶与罂粟基因组基因一一对应；明确 SALSYN 对 (R) 型的对映选择性

### Step 3：晚步骤（蒂巴因 → 可待因 → 吗啡）

- **操作**：梳理三次脱甲基/还原晚步骤及副产物
- **关键酶**：thebaine 6-O-demethylase (T6ODM) 与 codeine O-demethylase (CODM)——均为 2-酮戊二酸依赖双加氧酶 [6]；codeinone reductase (COR)；neopinone isomerase (NISO)
- **要点**：NISO 酶促催化 neopinone→codeinone（非自发）；COR 对 neopinone 还原生成副产物 neopine，CODM 也可脱 codeine→morphine 之外产生 neomorphine [2][6]
- **质量门禁**：能画出吗啡的"经可待因"主路线与"或ipavine/neomorphine"副路线及其各自分支酶

### Step 4：基因组组织与演化分析

- **操作**：分析 BIA 基因在罂粟基因组中的成簇与拷贝数
- **数值**：Hi-C 组装中 109 个 BIA 基因及旁系（58 核心 + 51 旁系，12 疑似假基因）中 70% 位于 ≤100 kb 簇内 [4]；吗啡通路（CODM/COR/T6ODM 等）多以串联重复成阵 [4]；罂粟谱系约 7.8 MYA 经历 WGD [4]
- **演化**：STORR 融合为 opium poppy 谱系特异，其 P450 模块 CYP82Y2 在与 E. californica 分岔后分化 [3]；CODM/T6ODM 复制分化驱动吗啡生产获得 [3]
- **工具**：基因树、WGD 分析、共线/成簇检测
- **质量门禁**：能区分 morphine/noscapine/thebaine 子通路成簇程度差异（morphine 通路基因基本不成簇 [4]）

### Step 5：整理微生物重构基因清单

- **操作**：把植物基因映射为重构所需异源表达清单
- **要点**：P450（SALSYN、CYP80B1、STORR 模块）需宿主膜结构与 CPR 还原伙伴支持 [1]；COR/NISO/T6ODM/CODM 为脱甲基/还原核心 [2][6]
- **质量门禁**：标注每酶的宿主适配难点（膜表达、对映选择性、副产物）

## 通路示意

```
L-酪氨酸 ──▶ 多巴胺 + 4-HPAA
   │ NCS（缩合）                         [公共核心]
   ▼
(S)-去甲乌药碱 ─6OMT─▶ (S)-coclaurine ─CNMT─▶ (S)-N-甲基coclaurine
   ─CYP80B1(NMCH)+CPR─▶ 3′-OH-衍生物 ─4′OMT─▶ (S)-reticuline  [1][3]
   （分支枢纽：→血根碱 / →小檗碱 / →noscapine）
   │ STORR（P450-氧化还原酶融合，(S)→(R) 异构化）[3]
   ▼
(R)-reticuline ─SALSYN(CYP719B1)─▶ salutaridine ─SALR─▶ salutaridinol
   ─SALAT─▶ salutaridinol-7-O-乙酸酯 ─自发重排(碱性)─▶ 蒂巴因 thebaine [3]
   ─T6ODM─▶ neopinone ─NISO─▶ codeinone ─COR─▶ 可待因 codeine
   ─CODM─▶ 吗啡 morphine                 [6][2]
   （副产物：COR+neopinone→neopine；CODM+neopine→neomorphine）[2]
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 物种 | Papaver somniferum | [5] | 吗啡等药用来源 |
| 基因组估计 | ~3.37 Gb（17-mer） | [5] | CHM 农家种 |
| 蛋白编码基因 | 79,668 | [5] | CHM 组装预测 |
| WGD 时间 | ~7.8 MYA | [4] | 罂粟谱系 |
| 核心通路酶（前缀） | 6OMT, CNMT, NMCH/CYP80B1, 4′OMT | [1][3] | 到 (S)-reticuline |
| 吗啡烷开关酶 | STORR（融合蛋白） | [3] | (S)→(R) 异构化 |
| 蒂巴因合成酶 | SALSYN, SALR, SALAT（+自发重排） | [3] | 到首个吗啡烷 |
| 晚步骤酶 | T6ODM, NISO, COR, CODM | [6][2] | 到可待因/吗啡 |
| 脱甲基酶机制 | 2-酮戊二酸依赖双加氧酶 | [6] | T6ODM/CODM |
| BIA 基因成簇比例 | 70% ≤100 kb；89% ≤10 Mb | [4] | 109 个基因+旁系 |
| 吗啡通路成簇 | 基本不成簇（0/4 成簇） | [4] | 与 noscapine/thebaine 相反 |

## 边界与分流

- **物种边界**：吗啡烷通路（尤其 (R)-reticuline 与蒂巴因以下步骤）基本为罂粟/部分 Papaver 谱系所有；无吗啡生产物种共享 (S)-reticuline 公共核心但不含吗啡烷特异酶 [3]
- **立体选择性**：SALSYN 严格对 (R)-reticuline 起作用；(S) 型不进入吗啡烷分支 [2]
- **宿主差异**：E. coli 缺乏膜结合细胞器，P450（SALSYN/STORR 等）功能表达受限，酵母因具内质网更合适 [1]
- **晚步骤副产物**：COR 的底物混杂是 neopine 副产物根源，植物靠 NISO 与代谢通道抑制 [2]

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|---------|
| 通路步骤完整性 | 核心+吗啡烷+晚步骤三段齐全 | 补抓缺失步骤文献 |
| 酶-基因对应 | 每步至少 1 条直接证据 | 回到全文抓取核实 |
| 立体/机制断言 | 同一文献直接支持 | 拆分并标跨文献推断 |
| 成簇数值 | 引用的 kb/% 与原文一致 | 复核 pool/全文数值 |

## 回退策略

- **全文抓取失败**：降级为摘要级证据并在来源标注 (abstract-only)，如本文 Planta 综述 [7]
- **某步酶基因未克隆**：如实标注"存在酶活性但基因未分离"，不编造序列
- **物种间推演**：只对同一谱系可推演，跨大谱系需标"(跨文献推断)"

## 资源召回建议

**何时应召回本卡片**：
- 用户询问吗啡/可待因/蒂巴因的生物合成基因通路
- 用户需要在酵母中重构吗啡烷通路（配合 bio-morphinan-alkaloid-yeast-reconstitution 卡片）
- 用户解析罂粟基因组中 BIA 基因簇与演化

**配套资源**：
- onescience-primitives bio 域卡片 bio-morphinan-alkaloid-yeast-reconstitution（本通路在酵母中的工程重构、滴度与瓶颈）
- onescience-primitives bio 域 RNA-seq / WGCNA / 基因家族分析卡片
- onescience-live-literature 技能：实时检索最新吗啡烷酶/基因簇文献

## 证据来源

[1] Pyne ME, Kevvai K, Grewal PS, et al. "A yeast platform for high-level synthesis of tetrahydroisoquinoline alkaloids." Nature Communications, 2020, 11:3337. DOI: 10.1038/s41467-020-17172-x. (full-text)

[2] Fossati E, Narcross L, Ekins A, et al. "Synthesis of Morphinan Alkaloids in Saccharomyces cerevisiae." PLoS ONE, 2015, 10(5):e0124459. DOI: 10.1371/journal.pone.0124459. (full-text)

[3] Li Y, Winzer T, He Z, et al. "Over 100 Million Years of Enzyme Evolution Underpinning the Production of Morphine in the Papaveraceae Family of Flowering Plants." Plant Communications, 2020, 1:100029. DOI: 10.1016/j.xplc.2020.100029. (full-text)

[4] Li Q, Ramasamy S, Singh P, et al. "Gene clustering and copy number variation in alkaloid metabolic pathways of opium poppy." Nature Communications, 2020, 11:1190. DOI: 10.1038/s41467-020-15040-2. (full-text)

[5] Li P, Wang B, Ye J, et al. "Genome and transcriptome of Papaver somniferum Chinese landrace CHM indicates that massive genome expansion contributes to high benzylisoquinoline alkaloid biosynthesis." Horticulture Research, 2021, 8:34. DOI: 10.1038/s41438-020-00435-5. (full-text)

[6] Farrow SC, Facchini PJ, et al. "Dioxygenases Catalyze O-Demethylation and O,O-Demethylenation with Widespread Roles in Benzylisoquinoline Alkaloid Metabolism in Opium Poppy." Journal of Biological Chemistry, 2013, 288(40):28997. DOI: 10.1074/jbc.M113.488585. (abstract-only)

[7] Beaudoin GAW, Facchini PJ. "Benzylisoquinoline alkaloid biosynthesis in opium poppy." Planta, 2014, 240:19-32. DOI: 10.1007/s00425-014-2056-8. (abstract-only)
