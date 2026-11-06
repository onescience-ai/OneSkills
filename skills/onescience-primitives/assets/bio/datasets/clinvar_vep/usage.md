## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/clinvar-vep`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/clinvar-vep`。



已绑定的资源入口：

- `Carbon/eval/clinvar-vep/coding/clinvar_coding.parquet`
- `Carbon/eval/clinvar-vep/non_coding/clinvar_non_coding.parquet`
- `Carbon/eval/smoke/clinvar_coding.parquet`
- `Carbon/eval/smoke/clinvar_non_coding.parquet`

## data_schema

coding 包含 `chrom,pos,ref,alt,label`、`type,refseq_id`，以及 CADD、phyloP、phastCons、GPN-MSA、NT、NT-v2、HyenaDNA、Evo2、GENERator 等来源模型分数。non_coding 包含坐标/等位基因、`gene_symbol,clinical_significance_terms,pathogenicity_group,qc_star_rating,qc_review_level,qc_is_reviewed,qc_is_high_confidence_review,variant_type,consequence_terms,region_group,region_subtype,coding_status,label`。两者均没有 `ref_seq,var_seq` 列。

## task_usage

可直接做已有模型分数的受控复核；若运行新的 DNA 模型，先获取匹配参考并生成窗口，保留原始变异 ID 和坐标。

## integration_paths

位点/label 表 → 参考版本核查与 ref 校验 → 生成成对序列 → 新模型 VEP；历史 score 列独立保留用于比较。

## preparation_requirements

检查 label、重复位点、review 过滤、coding_status、缺失 score；固定窗口长度、坐标变换、参考版本及评测方向。

## consumption_interfaces

现有分数复核消费 variant key + label + 指定 score；新模型消费显式生成的 ref/alt 序列，不能从不存在的窗口列直接加载。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

不能把含模型分数的表当成原始序列训练集。重建窗口前必须确认参考基因组版本、pos 的坐标约定及 ref 一致性，不能仅因旁边有 hg38 文件就默认所有位点兼容。clinical 标签不等同于实验功能强度。
