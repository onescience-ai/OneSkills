# 藏红花素（Crocin）生物合成通路基因推理工作流

## 适用范围

**触发条件**：
- 需要推断藏红花（Crocus sativus）活性成分合成通路的关键基因
- 已有藏红花基因组/转录组数据，需要功能注释和通路解析
- 需要理解藏红花素（crocin）、藏红花酸（crocetin）等类胡萝卜素衍生物的生物合成机制
- 需要鉴定 CCD、UGT/GLT 基因家族成员及其催化功能

**适用场景**：
- 藏红花素生物合成通路解析（zeaxanthin → crocetin → crocin）
- 类胡萝卜素裂解双加氧酶（CCD）基因家族鉴定与功能验证
- 糖基转移酶（UGT/GLT）基因家族鉴定与底物特异性分析
- 柱头特异性表达的转录调控网络构建
- 基因家族扩张事件（WGT）与功能分化溯源

**不适用场景**：
- 非藏红花物种的类胡萝卜素代谢（如栀子花 Gardenia 的 crocin 合成走独立进化路径 [1]）
- 无组学数据支持的纯文献综述
- 藏红花素药理活性研究（本卡片聚焦合成通路基因层面）

## 输入

| 输入项 | 格式/来源 | 说明 |
|--------|----------|------|
| 参考基因组 | FASTA + GFF3 | C. sativus 染色体级基因组（4769.31 Mb, 8 条假染色体, 60,656 个蛋白编码基因）[1] |
| 转录组数据 | FASTQ (RNA-seq) | 柱头、花瓣、雄蕊、叶、根、花梗、全花等 7 个组织 [1] |
| 代谢组数据 | UPLC-MS/MS | 类胡萝卜素和脱辅基类胡萝卜素靶向代谢组 [1] |
| 同源参考 | A. thaliana CCD/UGT 基因 | 用于 BLASTP 同源搜索（E-value cutoff 1e-10）[1] |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| 关键基因清单 | 表格 | CsCCD2-1/2, CsGLT2, CsUGT73D1, CsADH11367 等，含功能注释 |
| 通路示意图 | 多级箭头链 | zeaxanthin → CsCCD2 → crocetin → CsGLT2/UGT → crocin |
| 调控 TF 清单 | 表格 | MADS, C2H2, ERF, bZIP, MYB, HB, bHLH, WRKY |
| 共表达模块 | WGCNA 模块表 | brown/blue/green 三个脱辅基类胡萝卜素特异模块 |
| 关键氨基酸位点 | 列表 | CsCCD2-1 催化活性位点：I143, L146, R161, E181, T259, I260, S292, T326, M352, L353, S364 |

## 流程节点

### Step 1：基因组数据准备与注释

- **操作**：获取 C. sativus 染色体级参考基因组，确认组装质量
- **参数**：
  - 组装大小：4769.31 Mb [1]
  - Contig N50：361,768 bp [1]
  - 假染色体数：8 [1]
  - BUSCO 完整度：97.5%（基因组）/ 92.2%（注释）[1]
  - 蛋白编码基因数：60,656 [1]
  - 重复序列密度：65.57% [1]
- **工具**：OrthoFinder (v2.5.4), RAxML (v8.1.13), BUSCO
- **质量门禁**：BUSCO 完整度 ≥ 90%，Contig N50 ≥ 100 kb

### Step 2：WGT 事件溯源与基因家族扩张分析

- **操作**：鉴定物种特异性全基因组三倍化（WGT）事件，追踪 CCD 基因家族扩张
- **参数**：
  - WGT 轮次：2 轮物种特异性 WGT [1]
  - 关键发现：近期 WGT 事件驱动 CsCCD2 从 CsCCD1 进化而来 [1]
  - 外群：V. vinifera（葡萄）[1]
  - 分歧时间校准：O. sativa vs Zea mays 42-52 MYA [1]
- **工具**：OrthoFinder, MCMCtree, CAFÉ (v3.1), KEGG/GO 富集
- **质量门禁**：低拷贝基因系统发育树 bootstrap ≥ 70%

### Step 3：组织特异性表达分析

- **操作**：比较 7 个组织的基因表达谱，鉴定柱头特异性高表达基因
- **参数**：
  - 组织：根、花梗、叶、全花、雄蕊、花瓣、柱头 [1]
  - 表达阈值：FPKM ≥ 1（排除 9430 个不表达基因，占 15.5%）[1]
  - 聚类方法：k-means，48 个聚类 [1]
  - 柱头特异聚类：3, 5, 13, 15, 17, 20, 34, 43 [1]
  - 候选 TF 筛选：FPKM > 10，共 85 个 [1]
- **工具**：RNA-seq 比对（基因组参考），k-means 聚类（R packages）
- **质量门禁**：柱头特异聚类中萜类/类胡萝卜素合成基因显著富集

### Step 4：代谢通路关键酶基因鉴定

- **操作**：鉴定 crocin 合成通路的核心结构基因
- **关键基因与功能**：

| 基因 | 酶/功能 | 催化反应 | 证据 |
|------|---------|---------|------|
| CsCCD2-1/2 | 类胡萝卜素裂解双加氧酶 2 | zeaxanthin → crocetin（7,8/7′,8′ 位裂解）| [1] |
| CsCCD1 | 类胡萝卜素裂解双加氧酶 1 | 底物偏好不同，不催化 zeaxanthin 裂解 | [1] |
| CsCCD4 | 类胡萝卜素裂解双加氧酶 4 | 功能分化，与 CCD2 不同 | [1] |
| CsGLT2 | 藏红花酸糖基转移酶 2 | crocetin → crocin（葡萄糖基化）| [2] |
| CsUGT73D1 | UDP-葡萄糖依赖糖基转移酶 | crocetin 糖基化（blue 模块）| [2] |
| CsADH11367 | 醛脱氢酶 | crocetinal → crocetin | [2] |
| CsADH3F1 | 醛脱氢酶家族 3 成员 F1 | 辅助氧化步骤 | [2] |

- **关键发现**：ABA 合成通路在柱头中被抑制（NCED3 沉默，ZEP/NSY FPKM < 5），代谢流导向 crocin 合成 [1]
- **工具**：BLASTP (v2.11.0, E-value 1e-10), HMMER, InterProScan
- **质量门禁**：每个基因家族成员 ≥ 3，结构域完整性 ≥ 80%

### Step 5：CsCCD2 催化活性关键氨基酸鉴定

- **操作**：通过结构预测和分子对接鉴定 CsCCD2-1 的催化关键残基
- **参数**：
  - 候选残基（距底物 zeaxanthin 5 Å 内）：I143, L146, R161, E181, T259, I260, S292, T326, M352, L353, S364 [1]
  - 正选择位点：S292, T326 [1]
  - 分子动力学：RMSF 分析确认残基刚性（低 RMSF = 保守底物识别/结合口袋稳定）[1]
  - 定点突变验证：丙氨酸替换，6 次重复 [1]
- **工具**：AlphaFold2（结构预测），分子对接，分子动力学模拟，CloneExpress II 定点突变
- **质量门禁**：突变体与野生型催化活性差异 P < 0.05（*）或 P < 0.01（**）

### Step 6：WGCNA 共表达网络与 hub TF 识别

- **操作**：构建柱头转录组共表达网络，识别脱辅基类胡萝卜素特异模块和 hub TF
- **参数**：
  - 数据来源：NCBI SRA（19 个 accession，含不同生态型和发育阶段）[2]
  - 组装：Trinity de novo (k-mer=32)，Bowtie 2 比对 [2]
  - 定量：Salmon (v1.9.0)，TPM + Log2 转换 [2]
  - 批次校正：ComBat (SVA v3.44.0)，Mean-only adjustment [2]
  - 模块数：11 个，其中 3 个为脱辅基类胡萝卜素特异模块 [2]
- **模块-通路对应**：

| 模块 | 富集通路 | 关键基因 |
|------|---------|---------|
| brown | Apocarotenoid, Carotenoid biosynthesis, MEP Pathway, Phenylpropanoid, ABC transporters | CCD2, ADH11367, GLT2 |
| blue | MVA Pathway, Saponin biosynthesis, monoterpene, Apocarotenoid | UGT73D1, UGT12 |
| green | Flavonoid biosynthesis, Apocarotenoid | — |

- **hub TF 识别**：
  - brown 模块：MADS, C2H2, ERF [2]
  - blue 模块：MYB, bZIP [2]
  - green 模块：HB [2]
  - 启动子 cis-element 分析（MEME）：HB, MYB, WRKY, MADS 为最常见 TFBS [2]
- **PLS 回归验证**：C2H2/MADS 与 GLT2/CCD2 强相关；ERF 与 ADH11367 强相关 [2]
- **工具**：WGCNA, Cytoscape (v3.7.1), MEME, PlantTFDB (v5.0), PLS 回归
- **质量门禁**：模块-性状相关性 r ≥ 0.8，hub TF 在 RT-qPCR 中与靶基因表达趋势一致

### Step 7：RT-qPCR 验证与生态型比较

- **操作**：在高/低代谢物含量生态型中验证 hub TF 与靶基因的表达相关性
- **参数**：
  - 验证基因：CCD2, ADH11367, GLT2, MADS, C2H2, ERF, ADH3F1, HB（brown 模块）；UGT73D1, UGT12, MYB, bZIP（blue/green 模块）[2]
  - 发育阶段：RED, -2 DAY, 0 DAY（柱头）[2]
  - 重复：3 次生物学重复 [2]
- **工具**：RT-qPCR，HPLC（crocin/picrocrocin 含量测定）
- **质量门禁**：高含量生态型中 CCD2/GLT2 表达显著高于低含量生态型

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 基因组大小 | 4769.31 Mb | [1] | C. sativus 染色体级组装 |
| 蛋白编码基因数 | 60,656 | [1] | 注释基因总数 |
| 假染色体数 | 8 | [1] | 三倍体（3n=24） |
| WGT 事件 | 2 轮物种特异性 | [1] | 驱动 CCD 家族扩张 |
| CsCCD2 裂解位点 | 7,8/7′,8′ | [1] | zeaxanthin → crocetin |
| 关键氨基酸数 | 11 个 | [1] | CsCCD2-1 催化活性位点 |
| 正选择位点 | S292, T326 | [1] | 与催化活性相关 |
| 共表达模块数 | 11（3 个脱辅基类胡萝卜素特异）| [2] | WGCNA 分析 |
| hub TF 数 | 6 类（MADS, C2H2, ERF, bZIP, MYB, HB）| [2] | 调控 crocin 合成 |
| 柱头特异 TF 候选 | 85 个（FPKM > 10）| [1] | 共表达网络节点 |
| NCED3 基因数 | 6 个（柱头全部沉默）| [1] | ABA 通路被抑制 |
| ZEP/NSY 表达 | FPKM < 5（柱头）| [1] | 代谢流导向 crocin |

## 通路示意

```
类胡萝卜素合成通路（质体）：
  IPP/DMAPP → GGPP → phytoene → lycopene → β-carotene → zeaxanthin
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │                   │
                                              [ABA 通路]          [Crocin 通路]
                                              ZEP → NSY →        CsCCD2 (7,8/7′,8′ 裂解)
                                              NCED3 → ABA              │
                                              (柱头沉默)          crocetin dialdehyde
                                                                        │
                                                                  CsADH (氧化)
                                                                        │
                                                                    crocetin
                                                                        │
                                                              CsGLT2 / CsUGT73D1
                                                              (葡萄糖基化，1-5 个 glucose)
                                                                        │
                                                                    CROCIN
                                                              (藏红花素，柱头红色)

调控层：
  MADS ──┐
  C2H2 ──┼──→ CCD2, GLT2（brown 模块）
  ERF  ──┘
  MYB  ──┐
  bZIP ──┼──→ UGT73D1, UGT12（blue 模块）
  HB   ──┘
```

## 边界与分流

- **物种边界**：本通路仅适用于 Crocus sativus；Gardenia jasminoides（栀子）的 crocin 合成走独立进化路径，CCD 和 UGT 基因不同源 [1]
- **组织边界**：crocin 仅在柱头和全花中高积累；叶中主要积累 β-carotene、zeaxanthin、antheraxanthin，不积累 crocin [1]
- **ABA 竞争**：柱头中 ABA 合成被抑制（NCED3 沉默，ZEP/NSY 低表达），确保代谢流导向 crocin；若 ABA 通路激活，crocin 产量下降 [1]
- **CCD 亚家族分流**：CsCCD1 不催化 zeaxanthin 裂解（底物偏好不同）；CsCCD4 功能分化；只有 CsCCD2 是 crocin 合成关键酶 [1]

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|---------|
| 基因组 BUSCO 完整度 | ≥ 90% | 重新组装或换用更高质量参考 |
| 柱头特异聚类富集 | 萜类/类胡萝卜素基因显著富集 | 检查组织取样纯度 |
| CCD 家族成员数 | ≥ 3 | 降低 BLAST E-value 阈值或换用 HMM 搜索 |
| WGCNA 模块-性状相关性 | r ≥ 0.8 | 调整 soft threshold power 或增加样本量 |
| RT-qPCR 验证一致性 | hub TF 与靶基因表达趋势一致 | 增加生物学重复或换用其他生态型 |
| 定点突变活性差异 | P < 0.05 | 增加重复次数或检查突变构建 |

## 回退策略

- **无参考基因组**：退回 de novo 转录组组装（Trinity），用同源物种（如 Iris、Gladiolus）基因组辅助注释
- **CCD2 同源搜索无结果**：降低 E-value 至 1e-5，或用 HMMER + Pfam CCD 结构域（PF01753）搜索
- **WGCNA 模块不显著**：减少样本批次效应（ComBat），或改用 Spearman 相关性网络
- **RT-qPCR 验证失败**：换用其他发育阶段样本，或改用 RNA-seq 差异表达验证

## 资源召回建议

**何时应召回本卡片**：
- 用户询问藏红花素/藏红花酸生物合成机制
- 用户需要鉴定 Crocus sativus 的 CCD/UGT 基因家族
- 用户构建藏红花代谢通路模型或基因调控网络
- 用户进行藏红花分子育种或通路工程

**配套资源**：
- onescience-primitives 中 bio 域的 RNA-seq 差异表达分析卡片
- onescience-primitives 中 bio 域的 WGCNA 共表达网络卡片
- onescience-live-literature 技能：实时检索最新藏红花基因组/转录组文献

## 证据来源

[1] Xu Z, Chen S, Wang Y, Tian Y, Wang X, Xin T, Li Z, Hua X, Tan S, Sun W, Pu X, Yao H, Gao R, Song J. "Crocus genome reveals the evolutionary origin of crocin biosynthesis." Acta Pharmaceutica Sinica B, 2024, 14(4):1878-1891. DOI: 10.1016/j.apsb.2023.12.013. PMCID: PMC10985130.

[2] Eshaghi M, Rashidi-Monfared S. "Co-regulatory network analysis of the main secondary metabolite (SM) biosynthesis in Crocus sativus L." Scientific Reports, 2024, 14:15839. DOI: 10.1038/s41598-024-65870-z. PMCID: PMC11233700.
