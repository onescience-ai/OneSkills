# 非编码变异功能影响判读 (genomic-variant-impact-interpretation)

## 任务目标
给定 chr:pos:ref>alt 格式变异，预测并判读其对基因表达、染色质可及性、组蛋白标记与转录因子结合的
调控影响（含启动子/增强子/剪接扰动），并用群体频率与基因约束交叉核验致病性线索，产出 report.md。

## 适用范围 / 不适用场景
适用：非编码变异调控效应、组织特异性效应发现、生物术语到 UBERON/CL 本体解析。
不适用：临床级诊断结论；体细胞突变追踪（COSMIC）；个体患者基因组解读；原始测序读段获取（ENA）。

## 实体槽（Entity Slots）
- variant_format：chr-pos-ref-alt（如 chr2:1234:A>C）。
- tissue_scope：pan-tissue-discovery（广谱发现扫描）/ disease-relevant-keywords（疾病组织扩展检索）。
- modality：rna-seq / dnase / chip / tf。

## 输入输出契约
输入：变异字符串 + 可选疾病组织关键词。输出：tidy 分数表（biosample_name / gene_name / output_type /
quantile_score / raw_score）、Ref/Alt 与剪接可视化图、report.md（含 top hits 表与自批评环节）。

## 方法路线（可替换）
score_variant 广谱发现扫描（仅 differential scorers，排除 ACTIVE/CAGE/PROCAP；窗口 SEQ_LENGTH=2^20）
→ tidy_scores(match_gene_strand=True) → |quantile_score|>0.995 显著性过滤、按 |raw_score| 降序 →
疾病关键词扩展检索 → 群体层用 gnomAD FAF 与 pLI/LOEUF 做先验交叉核验。基因/转录本查询只用本地 GTF
（lookup_gene_info.py），禁止外部 API。

## 操作序列（Operations）
1. 解析变异与用户意图；2. 解析组织/模态本体；3. score_variant 打分；4. 显著性过滤与排序；
5. 疾病组织扩展；6. Ref/Alt 与剪接可视化（zoom 须含侧翼外显子与长 junction 锚定外显子）；
7. 先读解释指南再判读；8. 写 report.md 并自批评核验链接与论断。

## 验证契约（Validations）
- 显著性阈值 |quantile_score|>0.995；top hits 表必须入报告。
- 负结果伪影核查：区分数学伪影与 proxy 效应（参考 GATA4/TGFB3 负例、RNU4ATAC 模型局限例）。
- API 形状陷阱：score_variant 不接受 ontology_terms（predict_variant 才接受），返回的 AnnData 需手动
  按 adata.var 过滤；列名是 gene_name/output_type 而非 gene_symbol/modality；GTF feather 列名首字母大写。

## 资源引用（Resources）
- tools/gnomad-variant-frequency-access：等位基因频率、FAF、基因约束（pLI/LOEUF）。

## 前后置任务（Task Graph）
无强制前后置；多变异请求按变异拆分并行分析后合成单报告。

## 缺口与降级（Fallback / Gap）
无 ALPHAGENOME_API_KEY → halt 走凭据协议申请；基因 >500kb 使 whole_gene 视图失效 → 改 --view detail
或手动区域窗；本地 GTF 缺失 → 修环境/路径而非切换外部 API；群体稀有度问题 → 改道 gnomAD FAF 判据。
