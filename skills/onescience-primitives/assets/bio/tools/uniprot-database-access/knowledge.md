# UniProt 蛋白知识库访问 (uniprot-database-access)

## 定位与适用任务
蛋白功能注释、序列获取、分类与蛋白组关系、大规模元数据拉取、跨 100+ 外部库 ID 映射、历史/已删除条目
回查（UniSave）。为同源分析等任务提供命中回注与身份解析。不适用：序列比对、折叠预测、相似性搜索
（走专门任务卡）。

## 访问方式与鉴权
- get/search/stream/count → `rest.uniprot.org/{dataset}/`；map → `rest.uniprot.org/idmapping/`；
  sparql → `sparql.uniprot.org/sparql`；get --dataset unisave → `rest.uniprot.org/unisave/`。无需 API key。

## 核心操作模式
- 先 count 估量，再 search/stream：bulk 优先 stream（≤10,000,000 条，不支持 --limit）或 sparql。
- search 用于探索（--limit 5 验证查询意图；>500 条自动分页；分页下 TXT 格式 --limit 按行计不可靠）。
- 全序列精确匹配用 SPARQL（REST /search 不支持序列串直查）；计数类问题用 count 或 SPARQL。
- map 做跨库 ID 转换；非显式请求时先试 search 再退 map（外部 ID 可能在 UniParc 可搜但映射失败）。

## 输出契约与关键字段
JSON/FASTA/TSV。UniProtKB accession（如 P04637）携带功能元数据；UniParc ID（UPI…）仅序列，
需经 ID Mapping 回连 accession。stream 支持 --format tsv --fields 选取列。

## 限流与合规
遵循 UniProt 许可与 API 条款；首次含 UniProt 数据的回复必须声明使用并提示用户审阅许可条款。

## 常见坑与降级
- `name:` 非合法查询项 → 用 `protein_name:`；列表用大写 OR 而非逗号；空格即 AND。
- 非模式生物基因查不到 → 转蛋白名、UniParc、或先解析人/鼠 ortholog 命名。
- 宽泛文本搜索有引文噪声（命中维护蛋白等假阳）→ 用字段过滤如 `cc_function:`、`protein_name:`；
  短词加引号防子串误配（如 lanM 误配 Lancefieldella）。
- ID 映射目标库写 UniProtKB 而非 UniProtKB_AC-ID；复杂查询失败改 SPARQL 而非放弃。
- 不得手工编辑/截断蛋白序列；ID 含义必须先查自然语言描述再用于检索。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 uniprot_database 技能；
上游条款见 uniprot.org/help/license 与 api_queries。
