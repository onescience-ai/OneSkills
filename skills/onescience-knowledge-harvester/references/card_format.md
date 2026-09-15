# 知识卡片格式规范

本文档定义 `onescience-knowledge-harvester` 技能生成的知识卡片格式。

## 目录结构

```
skills/onescience-primitives/assets/<domain>/workflow-planning/<card-name>/
  metadata.json    # 基础信息（必需）
  knowledge.md     # 完整正文（必需）
```

- `<domain>`：bio | matchem | climate | cfd | general
- `<card-name>`：kebab-case，长度 ≤ 80 字符；通用类卡格式 `<domain>-<问题类>-<方案/交付物>`（不得含实例专名），实例级卡格式 `<domain>-<topic>-<method>`（可含实体名），见下方"命名规则"

## metadata.json 规范

### 固定字段（9 个，与 onescience-primitives 对齐）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| name | string | 卡片名称，与目录名一致 | "bio-saffron-gene-derivative-reasoning" |
| type | string | 固定为 "workflow-planning" | "workflow-planning" |
| domain | string | 领域 | "bio" |
| version | string | 版本号 | "1.0.0" |
| visibility | string | 可见性 | "public" |
| created_at | string | 创建时间（ISO 8601） | "2026-09-09T19:00:00Z" |
| updated_at | string | 更新时间（ISO 8601） | "2026-09-09T19:00:00Z" |
| description | string | 信息密集的描述 | 见下方"description 撰写规则" |
| tags | array | 多维度标签 | 见下方"tags 撰写规则" |

### harvested 扩展字段

| 字段 | 类型 | 说明 |
|------|------|------|
| harvested | boolean | 固定为 true，标识自动采集来源 |
| harvest_source | string | 固定为 "onescience-knowledge-harvester" |
| harvest_query | string | 原始知识缺口描述 |
| aliases | array | 可选，实例别名（纯字符串），仅供召回，不参与身份面表达 |
| evidence_papers | array | 证据论文列表 |
| evidence_docs | array | 可选，开源权威文档证据列表（见下） |
| evidence_user | array | 可选，用户自有数据证据列表（见下） |
| merged_batches | array | 可选，每次 modify/merge 追加一条批次标识 |
| conflicts | array | 可选，补充证据与论文证据的待裁决冲突描述 |

### evidence_papers 格式

```json
{
  "title": "论文标题",
  "doi": "10.xxxx/xxxxx",
  "year": 2024,
  "venue": "期刊名",
  "authors": ["作者1", "作者2"],
  "oa_url": "开放获取链接（可选）"
}
```

### evidence_docs 格式（开源权威文档）

```json
{
  "title": "文档标题",
  "url": "https://...",
  "publisher": "发布机构（官方/标准组织/公共机构/大学/官方 GitHub 组织）",
  "version": "版本号或发布日期（缺失视为低置信）",
  "accessed_at": "2026-09-10"
}
```

### evidence_user 格式（用户自有数据）

```json
{
  "provider": "user",
  "provided_at": "2026-09-10",
  "location": "会话附件或用户指定路径/描述",
  "attestation": "用户在会话中显式确认入库（true/false）"
}
```

### version 与 merge 约定

- new：version 从 1.0.0 起。
- modify / merge：version 升 minor（1.0.0 → 1.1.0），updated_at 更新，merged_batches 追加一条批次标识（建议格式 `harvest-<ISO日期>`）。
- 冲突不覆盖：补充证据与论文证据冲突时写入 conflicts，正文新旧值并存标注，待人工裁决。

### description 撰写规则

description 是 onescience-primitives 语义匹配的核心字段，必须信息密集：

1. **首句**：说明卡片核心能力（做什么）
2. **第二句**：说明适用场景（何时用）
3. **第三句**：说明关键参数/方法（怎么做）
4. **第四句**：说明输出产物（得到什么）

**示例**：
```
藏红花基因衍生推理工作流：从基因组数据推断藏红花（Crocus sativus）活性成分合成通路的关键基因。适用于需要理解藏红花素（crocin）、藏红花酸（crocetin）等类胡萝卜素衍生物生物合成机制的研究场景。核心方法包括：转录组测序（RNA-seq）差异表达分析、基因家族鉴定（CYP450/UGT）、共表达网络构建。输出为基因-酶-产物对应关系表和通路示意图。
```

**通用类卡的 description 附加规则**（卡片身份 = 通用问题类时）：

1. 首句必须以需求级通用主语开头："面向目标X，选择或设计满足Y要求的Z……"，不得以具体实例场景开头。
2. 实例分子/材料专名不得饱和填充 description：至多在"校准数值来自 X 体系，其他体系需重新锚定证据"这类从句中出现一次。
3. 实例召回词一律进 tags/aliases，不进身份面（name/description 主语）。
4. 禁用脚手架词："具体场景""上层需求""本卡解决""槽位""迁移矩阵""复用协议""抽象层级""升维"。

### tags 撰写规则

tags 用于快速过滤，必须覆盖多个维度：

1. **物种/体系**：如 "saffron", "Crocus sativus"
2. **方法/技术**：如 "RNA-seq", "gene family", "co-expression"
3. **目标分子**：如 "crocin", "crocetin", "carotenoid"
4. **领域关键词**：如 "biosynthesis", "metabolic pathway", "gene derivative"
5. **应用场景**：如 "pathway engineering", "molecular breeding"

**示例**：
```json
["saffron", "Crocus sativus", "crocin", "crocetin", "carotenoid", "biosynthesis", "RNA-seq", "gene family", "CYP450", "UGT", "co-expression", "metabolic pathway", "gene derivative"]
```

## knowledge.md 规范

### 推荐章节（至少包含 5 个）

| 章节 | 说明 | 必需 |
|------|------|------|
| 适用范围 | 触发条件、适用场景、不适用场景 | 推荐 |
| 输入 | 输入数据格式、来源、预处理要求 | 推荐 |
| 输出 | 输出产物、格式、验证标准 | 推荐 |
| 流程节点 | 步骤链，每步含操作、参数、工具、质量门禁 | 推荐 |
| 关键参数 | 参数表（参数/值/来源/说明） | 推荐 |
| 边界与分流 | 异常处理、降级策略、分支条件 | 可选 |
| 质量检查 | 验证点、阈值、失败处理 | 可选 |
| 回退策略 | 失败时的替代方案 | 可选 |
| 资源召回建议 | 何时应召回本卡片、配套资源 | 可选 |
| 补充证据 | 开源文档 [Dn] / 用户自有 [Un] 引用列表 | 可选（有补充通道证据时写） |
| 批次补充 | merge 产生的追加节，标题为 `## 批次补充 <日期>（<来源>）` | 可选（merge 时产生） |
| 证据来源 | 论文引用列表（连续编号） | 必需 |

### 章节撰写规则

#### 适用范围

```markdown
## 适用范围

**触发条件**：
- 需要推断藏红花活性成分合成通路的关键基因
- 已有藏红花转录组/基因组数据，需要功能注释

**适用场景**：
- 藏红花素（crocin）生物合成通路解析
- 藏红花酸（crocetin）衍生物生成机制研究
- 类胡萝卜素裂解双加氧酶（CCD）基因家族鉴定

**不适用场景**：
- 非藏红花物种的基因衍生推理
- 无组学数据支持的纯文献综述
```

#### 流程节点

```markdown
## 流程节点

### Step 1：数据准备
- **操作**：下载藏红花参考基因组/转录组数据
- **参数**：物种=Crocus sativus, 数据库=NCBI SRA, 数据类型=RNA-seq
- **工具**：SRA Toolkit, fastq-dump
- **质量门禁**：reads 数 ≥ 10M, Q30 ≥ 80%

### Step 2：差异表达分析
- **操作**：比较不同组织/发育阶段的基因表达
- **参数**：软件=DESeq2, padj < 0.05, |log2FC| > 1
- **工具**：DESeq2, edgeR
- **质量门禁**：PCA 分离度 R² ≥ 0.7

### Step 3：基因家族鉴定
- **操作**：鉴定 CYP450、UGT、CCD 等家族成员
- **参数**：HMM 阈值 e-value < 1e-5, 结构域完整性 ≥ 80%
- **工具**：HMMER, InterProScan
- **质量门禁**：家族成员数 ≥ 3

### Step 4：共表达网络构建
- **操作**：构建基因共表达网络，识别模块
- **参数**：软件=WGCNA, soft threshold power=6, min module size=30
- **工具**：WGCNA
- **质量门禁**：模块数 ≥ 3, 关键模块与目标性状相关性 r ≥ 0.8
```

#### 关键参数

```markdown
## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 物种 | Crocus sativus | [1] | 藏红花学名 |
| 目标分子 | crocin, crocetin | [1][2] | 主要活性成分 |
| 关键酶 | CCD2, UGT74AD1 | [2][3] | 藏红花素合成关键酶 |
| 基因家族 | CYP450, UGT, CCD | [3] | 候选基因家族 |
| 表达阈值 | padj < 0.05, |log2FC| > 1 | [4] | 差异表达标准 |
| 共表达阈值 | r ≥ 0.8 | [4] | 模块-性状相关性 |
```

#### 证据来源

```markdown
## 证据来源

[1] "Crocus sativus transcriptome assembly and analysis", Author et al., Plant Journal, 2023, DOI: 10.xxxx/xxxxx
[2] "Molecular cloning and characterization of CCD2 in saffron", Author et al., Phytochemistry, 2022, DOI: 10.xxxx/xxxxx
[3] "Genome-wide identification of UGT genes in Crocus", Author et al., BMC Genomics, 2024, DOI: 10.xxxx/xxxxx
[4] "WGCNA analysis of saffron stigma development", Author et al., Frontiers in Plant Science, 2023, DOI: 10.xxxx/xxxxx
```

#### 补充证据（可选）

```markdown
## 补充证据

[D1] "DESeq2 Official Manual", Bioconductor 官方站, version 3.18, URL: https://...（accessed 2026-09-10，交叉验证）
[U1] 用户提供的实验滴度记录, 2026-09-10（用户自有, 未经公开源验证）
```

**证据编号约定**：论文 `[1]..[n]`、开源文档 `[D1]..[Dn]`、用户自有 `[U1]..[Un]`，三套编号独立不混排；关键参数表"来源"列须带编号与层级（如 `[D1]`、`[U1, 经[2]佐证]`）。

## 通用类卡正文规范（硬门禁）

卡片身份为通用问题类时，knowledge.md 必须满足（与 SKILL.md Step 4 规范一致）：

1. "适用范围"以自然散文开场陈述问题类，不以实例场景开场。
2. 脚手架禁词零出现（词表见 description 附加规则第 4 条）。
3. 具体体系只出现在四个自然位置：流程例句（"以 X 体系为例"）、校准数值表引语、术语表举例引语、metadata aliases/tags。
4. 通用论断主句通用，证据用引用编号挂靠句尾；不得把实例塞进前提清单括号。
5. "关键参数"分两表：通用判据（方法层，逐条带证据编号）与校准数值（体系专属，引语写明其他体系需重新锚定）。
6. "边界与分流"写明每条关键前提不成立时的改道方案族。

## 质量门禁

生成的卡片必须通过以下检查：

1. **文件完整性**：metadata.json 和 knowledge.md 都存在且非空
2. **JSON 有效性**：metadata.json 可被标准 JSON 解析
3. **字段完整性**：metadata.json 含全部 9 个固定字段 + harvested 标记
4. **description 质量**：description ≥ 100 字符，含核心能力、适用场景、关键方法
5. **tags 覆盖**：tags ≥ 5 个，覆盖物种/方法/目标/领域/应用维度
6. **knowledge.md 章节**：含推荐章节中的至少 5 个
7. **证据标注**：关键参数表中的"来源"列引用了证据编号（论文 [n]、文档 [Dn]、用户 [Un]）
8. **证据来源**：knowledge.md 末尾含"证据来源"章节，列出 ≥ 1 篇论文；确无论文证据时仅当 evidence_user 非空且用户在会话中显式确认才允许入库，并须在 description 与 observation.quality_notes 标注"论文证据缺失"
9. **单调性校验（modify/merge）**：旧标题集合 ⊆ 新标题集合、新字符数 ≥ 旧字符数、旧 tags ⊆ 新 tags、旧 evidence 条目只增不删
10. **补充证据溯源**：evidence_docs 每条含 url/publisher/accessed_at；evidence_user 每条含 provided_at/location；权威黑名单来源不得出现
11. **脚手架禁词零命中**（通用类卡）：对 knowledge.md 与 metadata.json 执行禁词检查，命中即不合格
12. **变体召回自测**（通用类卡）：≥2 条"同需求换体系"变体查询仍能命中本卡；不命中则回重写身份面，而非追加实例词

## 命名规则

### 卡片目录名

- **通用类卡**：`<domain>-<问题类>-<方案/交付物>`，不得含实例分子/材料/模型专名（如 co2、saffron、mxene）
  - 示例：`matchem-gas-capture-material-design-validation`
- **实例级卡**：`<domain>-<topic>-<method>`，可含实体名
  - 示例：`bio-saffron-gene-derivative-reasoning`、`matchem-mxene-electronic-structure-calculation`、`climate-weather-forecast-model-evaluation`、`cfd-turbulence-simulation-mesh-generation`

### 命名约束

- 使用 kebab-case（小写字母 + 连字符）
- 长度 ≤ 80 字符
- 不含特殊字符（除连字符外）
- 语义清晰，可从名称推断卡片内容

## 与 onescience-primitives 的集成

### 发现机制

onescience-primitives 通过以下机制发现卡片：

1. **Glob 枚举**：`assets/<domain>/**/metadata.json` 递归搜索
2. **语义匹配**：Read metadata.json 的 description/tags 与查询对比
3. **内容组织**：按 content_request 读取 knowledge.md

### harvested 标记的作用

- 与人工撰写的原语卡区分
- 标识卡片来源为自动采集
- 便于后续质量审计和清理

### 召回流程

当用户查询与 harvested 卡片相关时：

1. onescience-primitives 的 Glob 枚举找到 metadata.json
2. 语义匹配 description/tags 确认相关性
3. Read knowledge.md 获取完整正文
4. 返回 resource_retrieval_result 给调用方

## 示例卡片

### metadata.json

```json
{
  "name": "bio-saffron-gene-derivative-reasoning",
  "type": "workflow-planning",
  "domain": "bio",
  "version": "1.0.0",
  "visibility": "public",
  "created_at": "2026-09-09T19:00:00Z",
  "updated_at": "2026-09-09T19:00:00Z",
  "description": "藏红花基因衍生推理工作流：从转录组数据推断藏红花（Crocus sativus）活性成分合成通路的关键基因。适用于需要理解藏红花素（crocin）、藏红花酸（crocetin）等类胡萝卜素衍生物生物合成机制的研究场景。核心方法包括：差异表达分析（DESeq2）、基因家族鉴定（CYP450/UGT/CCD）、共表达网络构建（WGCNA）。输出为基因-酶-产物对应关系表和通路示意图。",
  "tags": ["saffron", "Crocus sativus", "crocin", "crocetin", "carotenoid", "biosynthesis", "RNA-seq", "DESeq2", "WGCNA", "CYP450", "UGT", "CCD", "gene family", "co-expression", "metabolic pathway"],
  "harvested": true,
  "harvest_source": "onescience-knowledge-harvester",
  "harvest_query": "缺少藏红花基因衍生推理的知识",
  "evidence_papers": [
    {
      "title": "Crocus sativus transcriptome assembly and analysis",
      "doi": "10.xxxx/xxxxx",
      "year": 2023,
      "venue": "Plant Journal"
    },
    {
      "title": "Molecular cloning and characterization of CCD2 in saffron",
      "doi": "10.xxxx/xxxxx",
      "year": 2022,
      "venue": "Phytochemistry"
    }
  ]
}
```

### knowledge.md

见上方各章节示例。

> 上方 metadata 示例为 new 入库的最小集；可选字段（evidence_docs / evidence_user / merged_batches / conflicts）按本文档规范按需写入。
