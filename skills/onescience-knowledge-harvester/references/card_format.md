# 知识卡片格式规范

本文档定义 `onescience-knowledge-harvester` 技能生成的知识卡片格式。

## 目录结构

```
skills/onescience-primitives/assets/<domain>/workflow-planning/<card-name>/
  metadata.json    # 基础信息（必需）
  knowledge.md     # 完整正文（必需）
```

- `<domain>`：bio | matchem | climate | cfd | general
- `<card-name>`：kebab-case，格式 `<domain>-<topic>-<method>`，长度 ≤ 80 字符

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
| evidence_papers | array | 证据论文列表 |

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

## 质量门禁

生成的卡片必须通过以下检查：

1. **文件完整性**：metadata.json 和 knowledge.md 都存在且非空
2. **JSON 有效性**：metadata.json 可被标准 JSON 解析
3. **字段完整性**：metadata.json 含全部 9 个固定字段 + harvested 标记
4. **description 质量**：description ≥ 100 字符，含核心能力、适用场景、关键方法
5. **tags 覆盖**：tags ≥ 5 个，覆盖物种/方法/目标/领域/应用维度
6. **knowledge.md 章节**：含推荐章节中的至少 5 个
7. **证据标注**：关键参数表中的"来源"列引用了证据编号
8. **证据来源**：knowledge.md 末尾含"证据来源"章节，列出 ≥ 1 篇论文

## 命名规则

### 卡片目录名

- 格式：`<domain>-<topic>-<method>`
- 示例：
  - `bio-saffron-gene-derivative-reasoning`
  - `matchem-mxene-electronic-structure-calculation`
  - `climate-weather-forecast-model-evaluation`
  - `cfd-turbulence-simulation-mesh-generation`

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
