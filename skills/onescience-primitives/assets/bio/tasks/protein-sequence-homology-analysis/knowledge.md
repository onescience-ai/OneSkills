# 蛋白序列同源分析与多序列比对 (protein-sequence-homology-analysis)

## 任务目标
给定一条蛋白序列（或含 ≥2 条序列的 FASTA 文件），推断其同源蛋白、保守域与关键残基保守性，
产出 top 命中表（Q-Cov / E-value / Seq Identity）与保守性结论，支撑功能注释与下游结构分析。

## 适用范围 / 不适用场景
适用：单序列同源搜索（默认 MMseqs2，通常 <2 分钟）；多序列保守性/关键残基分析（Clustal Omega，
≤4000 条序列、≤4MB）。不适用：基于结构相似性的同源推断（改走 Foldseek 结构搜索）；非蛋白序列
（DNA/RNA）；仅有一条序列却请求 MSA（应先做同源搜索扩充序列集）。

## 实体槽（Entity Slots）
- query_type：homologue-search（找同源）/ conservation-analysis（保守性判读）。
- search_engine：mmseqs2（快，默认）/ blast（慢，兜底或用户指定）。
- taxon_scope：BLAST 库白名单取值，如 uniprotkb、uniprotkb_swissprot（人工 curated）、
  uniprotkb_bacteria、uniprotkb_human、uniref50、pdb 等共 24 个；白名单外请求必须 halt 并出示清单。

## 输入输出契约
输入：原始氨基酸序列字符串或 FASTA 文件（每条 header 以 `>` 开头）。
输出：`.md` 人读汇总表 + `.json` 原始结果（仅供后续工具消费）；MSA 另存比对文件。
判读只读 `.md`，禁止自行解析 JSON/a3m 原始输出；禁止虚构命中。

## 方法路线（可替换）
- 同源搜索主路：MMseqs2（ColabFold API）；退出码 2（RATELIMIT/API 错误）或用户点名 BLAST/特定库时
  改道 EBI BLAST（最长约 15 分钟，需 USER_EMAIL 头）。
- 保守性分析：EBI Clustal Omega 全局比对；成对指标从 MSA 中提取。

## 操作序列（Operations）
1. 识别查询（序列串或文件路径）；2. 按 query_type/search_engine 选路；3. 运行搜索或比对并重定向落盘；
4. 读取 `.md` 汇总；5. 判读指标；6. 命中仅有 UniProt accession 无描述时，取 top 3–5 回连
   tools/uniprot-database-access 补名称与功能后再汇总；7. 报告必须声明所用引擎与序列库。

## 验证契约（Validations）
- E-value 显著性：越低越显著（如 1e-50 为极强统计显著）。
- Q-Cov：高百分比表示命中覆盖查询序列大部分。
- 同一性指标分母四选一，按生物学语境匹配：较短序列长度（域/片段是否完整保留）、
  全比对列数（全长比较、最保守）、去末端 gap 列数（片段对全长）、完全保守列占比（家族进化签名）。
- 已知功能残基需投影到比对列做局部保守性核验，不得仅凭全局指标下结论。

## 资源引用（Resources）
- tools/uniprot-database-access：命中功能注释回查、查询序列获取。

## 前后置任务（Task Graph）
后继：predicted-protein-structure-fetch-analysis（同源与功能线索确认后进入结构置信判读）。

## 缺口与降级（Fallback / Gap）
MMseqs2 限流/报错 → 自动降级 BLAST 并告知用户；BLAST 库不在白名单 → halt 出示清单；
仅单条序列请求 MSA → 改道同源搜索先扩充序列集；搜索零命中 → 如实报告，不得虚构。
