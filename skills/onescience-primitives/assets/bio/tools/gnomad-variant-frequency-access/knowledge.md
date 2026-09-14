# gnomAD 群体变异频率与基因约束访问 (gnomad-variant-frequency-access)

## 定位与适用任务
判定变异稀有度与等位基因频率、获取基因 loss-of-function 不耐受约束（pLI、LOEUF）、
区域或基因内变异扫描、结构变异查询。为变异影响判读任务提供种群层交叉核验证据。
不适用：个体患者基因组、体细胞突变（COSMIC）、原始测序读段（ENA）。

## 访问方式与鉴权
gnomAD API 经封装脚本：get_variant_frequency.py（--variant_id chrom-pos-ref-alt 或 --rsid；
--dataset exome/genome/total）、get_gene_constraint.py（--gene 符号）、search_variants.py
（--chrom/--start/--end 或 --gene + --consequence pLoF|missense）；无需 key；脚本自动限流。

## 核心操作模式
- 频率查询返回全局与祖先群特异 AF、纯合计数、Grpmax Filtering AF（faf95/faf99）。
- 约束查询响应含 pli；LOEUF 以 oe_lof_upper 字段表示。
- 区域扫描按染色体坐标窗；基因扫描可限定后果类型。

## 输出契约与关键字段
JSON 落盘（--output 必填）。FAF 语义：最大可信祖先群 AF 的下界（95%/99% CI 单侧），
稀有度判定优先用 FAF 而非原始 AF。

## 限流与合规
遵循 gnomAD policies 与数据 API 条款；禁止绕开封装直打 API。

## 常见坑与降级
用原始 AF 判稀有度会高估常见变异在单一祖先群中的稀缺性 → 用 FAF；LOEUF 字段名是 oe_lof_upper
而非 loeuf；癌症体细胞问题 → 改道 COSMIC 类资源。

## 来源与许可
封装自 google-deepmind/science-skills（Apache-2.0，commit 28b84826）之 gnomad_database 技能；
上游条款见 gnomad.broadinstitute.org/policies。
