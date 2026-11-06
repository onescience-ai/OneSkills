## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/finetune/DeepSTARR-enhancer-activity`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/DeepSTARR-enhancer-activity`。



已绑定的资源入口：

- `Carbon/finetune/DeepSTARR-enhancer-activity/train.parquet`
- `Carbon/finetune/DeepSTARR-enhancer-activity/valid.parquet`
- `Carbon/finetune/DeepSTARR-enhancer-activity/test.parquet`

## data_schema

`id:string,sequence:string`；活性列 `Dev_log2_enrichment,Hk_log2_enrichment` 及对应 `_scaled`、`_quantile_normalized` 列（double）；`label:list<double>`。首条训练样本中 label 顺序与 `[Dev_log2_enrichment_scaled,Hk_log2_enrichment_scaled]` 一致，正式消费前还须核查整个目标映射。

## task_usage

用于 DNA 编码器加双输出回归头，分别评估两个目标；相关系数或误差指标与目标空间一并报告。

## integration_paths

固定目标列/label 顺序 → tokenizer 与长度检查 → 双目标回归 adapter；输出保留 id 和 split。

## preparation_requirements

验证序列字符/长度分布、目标有限值、label 长度及与选定活性列的对应；核查 split 重复和目标变换来源。

## consumption_interfaces

sequence、两个指定顺序的连续 targets、id、split；需要反变换时同时交付匹配的目标变换参数。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

不要将 label 列转为类别 ID，也不要只凭向量长度猜测两个目标顺序。预处理、截断和 reverse complement augmentation 应记录，不能跨 split 重采样。
