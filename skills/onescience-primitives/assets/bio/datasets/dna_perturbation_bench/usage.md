## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/perturbation-bench`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/perturbation-bench`。



已绑定的资源入口：

- `Carbon/eval/perturbation-bench/syn_human`
- `Carbon/eval/perturbation-bench/syn_mouse`
- `Carbon/eval/perturbation-bench/motif_human`
- `Carbon/eval/perturbation-bench/promoter_revcomp`
- `Carbon/eval/perturbation-bench/tata`
- `Carbon/eval/perturbation-bench/synonymous_codons`
- `Carbon/eval/smoke/perturbation`

## data_schema

每个分支都有 `original_sequence,sequence`，其余字段不统一。syn_human/syn_mouse 含 benchmark_id、参考版本/注释、位点、CDS 与 patch 边界、n_codons_changed、fraction_codons_changed 等；motif_human 含 motif/patch_len_bp；promoter_revcomp 含 TSS/promoter 布局；tata/synonymous_codons 仅有 `chr,start,end,strand,length` 及序列对，没有 benchmark_id。

## task_usage

用于冻结 DNA 模型对原序列/指定扰动的似然偏好或分数差评测；按具体操作分组报告，并固定分数方向与长度归一化政策。

## integration_paths

选定分支和操作定义 → 序列对一致性检查 → 配对模型打分 → 按操作/物种/位点分层；保留完整操作元数据。

## preparation_requirements

验证长度、序列差异是否在声明 patch、strand 与 genome_assembly，检查重复 benchmark_id/位点、原/扰动未误换及模型分数长度偏差。

## consumption_interfaces

original_sequence 与 sequence 成对输入，附分支和可用的 benchmark_id/位点/物种/操作元数据；输出配对分数及固定方向的偏好结果。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

保留原/扰动方向、链方向、参考组装和 CDS/patch 的坐标约定。不能把六分支 schema 强行补成一套已存在的字段，也不能仅按列名判断所有分支功能含义相同。
